"""
Vector Database Integration for Historical Incident Retrieval.

Supports multiple vector stores (FAISS, Pinecone, Weaviate).
Optimized for incident embeddings and similarity search.
"""

import os
import json
import pickle
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

# Optional vector store libraries
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    # Try modern imports first (LangChain 1.x)
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS as LangChainFAISS
    except ImportError:
        # Fallback to old import paths
        try:
            from langchain.embeddings.openai import OpenAIEmbeddings
            from langchain.vectorstores import FAISS as LangChainFAISS
        except ImportError:
            raise ImportError("Cannot import OpenAIEmbeddings or FAISS. Please ensure langchain-openai and langchain-community are installed.")
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# Configure logging
import logging
logger = logging.getLogger(__name__)


class VectorStore:
    """
    Abstract base class for vector store operations.
    """
    
    def __init__(self, embedding_dim: int = 1536):
        """Initialize vector store with embedding dimension."""
        self.embedding_dim = embedding_dim
        self.metadata = {}
    
    def store_incidents(self, incidents: List[Dict[str, Any]]) -> bool:
        """Store incidents with embeddings."""
        raise NotImplementedError
    
    def retrieve_similar_incidents(
        self, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve similar incidents based on query."""
        raise NotImplementedError
    
    def delete_incident(self, incident_id: str) -> bool:
        """Delete incident from store."""
        raise NotImplementedError
    
    def update_incident(self, incident_id: str, incident: Dict[str, Any]) -> bool:
        """Update incident in store."""
        raise NotImplementedError


class FAISSVectorStore(VectorStore):
    """
    FAISS-based vector store for local incident embeddings.
    Lightweight, fast, and suitable for on-device deployments.
    """
    
    def __init__(
        self,
        embedding_model: str = "text-embedding-3-small",
        storage_path: str = "./data/faiss_index",
        use_langchain: bool = True
    ):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_model: OpenAI embedding model
            storage_path: Path to store FAISS index
            use_langchain: Use LangChain wrapper (recommended)
        """
        super().__init__()
        
        if use_langchain and not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not installed. Install with: pip install langchain")
        
        if not FAISS_AVAILABLE and not use_langchain:
            raise ImportError("FAISS not installed. Install with: pip install faiss-cpu")
        
        self.embedding_model = embedding_model
        self.storage_path = storage_path
        self.use_langchain = use_langchain
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        
        # Initialize or load FAISS index
        self.index = None
        self.langchain_vectorstore = None
        self.incident_docs = []
        self.incident_map = {}  # Maps doc_id to incident metadata
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing index or create new one."""
        if os.path.exists(self.storage_path):
            try:
                self.langchain_vectorstore = LangChainFAISS.load_local(
                    self.storage_path,
                    self.embeddings
                )
                logger.info(f"Loaded FAISS index from {self.storage_path}")
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Creating new index.")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        # Create empty documents for initialization
        dummy_docs = ["Initialize vector store"]
        self.langchain_vectorstore = LangChainFAISS.from_texts(
            dummy_docs,
            self.embeddings
        )
        logger.info("Created new FAISS index")
    
    def _format_incident_for_storage(self, incident: Dict[str, Any]) -> str:
        """Format incident data for embedding."""
        text_parts = [
            f"Type: {incident.get('incident_type', 'Unknown')}",
            f"Location: {incident.get('location', 'Unknown')}",
            f"Severity: {incident.get('severity', 0)}",
            f"Description: {incident.get('description', '')}",
            f"Status: {incident.get('status', 'Unknown')}",
        ]
        return " | ".join(text_parts)
    
    def store_incidents(self, incidents: List[Dict[str, Any]]) -> bool:
        """
        Store incidents in vector store.
        
        Args:
            incidents: List of incident dictionaries
        
        Returns:
            True if successful
        """
        try:
            texts = []
            metadatas = []
            
            for incident in incidents:
                text = self._format_incident_for_storage(incident)
                texts.append(text)
                
                metadata = {
                    'incident_id': str(incident.get('id', '')),
                    'type': incident.get('incident_type', ''),
                    'timestamp': str(incident.get('timestamp', '')),
                    'location': incident.get('location', ''),
                    'severity': float(incident.get('severity', 0)),
                }
                metadatas.append(metadata)
            
            if texts:
                self.langchain_vectorstore.add_texts(texts, metadatas=metadatas)
                self._save_index()
                logger.info(f"Stored {len(incidents)} incidents in FAISS")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error storing incidents: {e}")
            return False
    
    def retrieve_similar_incidents(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar incidents using semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters (severity, location, type)
        
        Returns:
            List of similar incidents with scores
        """
        try:
            # Search with similarity scores
            results = self.langchain_vectorstore.similarity_search_with_score(
                query,
                k=top_k * 2  # Get more results for filtering
            )
            
            incidents = []
            for doc, score in results:
                metadata = doc.metadata
                
                # Apply filters if provided
                if filters:
                    if 'min_severity' in filters:
                        if metadata.get('severity', 0) < filters['min_severity']:
                            continue
                    
                    if 'location' in filters:
                        if filters['location'].lower() not in metadata.get('location', '').lower():
                            continue
                    
                    if 'incident_type' in filters:
                        if filters['incident_type'].lower() not in metadata.get('type', '').lower():
                            continue
                
                incidents.append({
                    'incident_id': metadata.get('incident_id'),
                    'type': metadata.get('type'),
                    'location': metadata.get('location'),
                    'severity': metadata.get('severity'),
                    'timestamp': metadata.get('timestamp'),
                    'similarity_score': float(1 / (1 + score)),  # Convert distance to similarity
                })
            
            # Return top_k after filtering
            return incidents[:top_k]
        
        except Exception as e:
            logger.error(f"Error retrieving incidents: {e}")
            return []
    
    def _save_index(self):
        """Save FAISS index to disk."""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            self.langchain_vectorstore.save_local(self.storage_path)
            logger.info(f"Saved FAISS index to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def delete_incident(self, incident_id: str) -> bool:
        """Delete incident (currently unsupported in LangChain FAISS)."""
        logger.warning("Deletion not directly supported. Consider rebuilding index.")
        return False
    
    def update_incident(self, incident_id: str, incident: Dict[str, Any]) -> bool:
        """Update incident by re-storing."""
        self.delete_incident(incident_id)
        return self.store_incidents([incident])


class SimpleMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store for lightweight deployments.
    Useful for development and testing.
    """
    
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        """Initialize memory vector store."""
        super().__init__()
        self.embedding_model = embedding_model
        self.incidents = {}  # incident_id -> incident data
        
        try:
            self.embeddings = OpenAIEmbeddings(model=embedding_model)
        except Exception as e:
            logger.warning(f"Could not initialize embeddings: {e}")
            self.embeddings = None
    
    def store_incidents(self, incidents: List[Dict[str, Any]]) -> bool:
        """Store incidents in memory."""
        try:
            for incident in incidents:
                incident_id = str(incident.get('id', ''))
                self.incidents[incident_id] = incident
            
            logger.info(f"Stored {len(incidents)} incidents in memory")
            return True
        
        except Exception as e:
            logger.error(f"Error storing incidents: {e}")
            return False
    
    def retrieve_similar_incidents(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar incidents using basic text matching.
        """
        try:
            query_lower = query.lower()
            scored_incidents = []
            
            for incident_id, incident in self.incidents.items():
                score = 0
                
                # Score based on text matches
                for field in ['incident_type', 'location', 'description']:
                    if query_lower in incident.get(field, '').lower():
                        score += 1
                
                if score > 0 or not filters:
                    # Apply filters
                    if filters:
                        if 'min_severity' in filters:
                            if incident.get('severity', 0) < filters['min_severity']:
                                continue
                        
                        if 'location' in filters:
                            if filters['location'].lower() not in incident.get('location', '').lower():
                                continue
                    
                    scored_incidents.append((incident, score))
            
            # Sort by score and return top_k
            scored_incidents.sort(key=lambda x: x[1], reverse=True)
            return [inc for inc, _ in scored_incidents[:top_k]]
        
        except Exception as e:
            logger.error(f"Error retrieving incidents: {e}")
            return []
    
    def delete_incident(self, incident_id: str) -> bool:
        """Delete incident from memory."""
        if incident_id in self.incidents:
            del self.incidents[incident_id]
            return True
        return False
    
    def update_incident(self, incident_id: str, incident: Dict[str, Any]) -> bool:
        """Update incident in memory."""
        self.incidents[incident_id] = incident
        return True


class VectorStoreFactory:
    """Factory for creating appropriate vector store instances."""
    
    @staticmethod
    def create(
        store_type: str = "faiss",
        **kwargs
    ) -> VectorStore:
        """
        Create vector store instance.
        
        Args:
            store_type: Type of store ('faiss', 'memory', 'pinecone')
            **kwargs: Additional arguments for the store
        
        Returns:
            VectorStore instance
        """
        store_type = store_type.lower()
        
        if store_type == "faiss":
            return FAISSVectorStore(**kwargs)
        elif store_type == "memory":
            return SimpleMemoryVectorStore(**kwargs)
        elif store_type == "pinecone":
            logger.warning("Pinecone integration coming soon")
            return SimpleMemoryVectorStore(**kwargs)
        else:
            logger.warning(f"Unknown store type: {store_type}. Using memory store.")
            return SimpleMemoryVectorStore(**kwargs)


# Global vector store instance
_vector_store: Optional[VectorStore] = None


def get_vector_store(
    store_type: str = "faiss",
    **kwargs
) -> VectorStore:
    """
    Get or create global vector store instance.
    
    Args:
        store_type: Type of vector store
        **kwargs: Additional arguments
    
    Returns:
        VectorStore instance
    """
    global _vector_store
    
    if _vector_store is None:
        _vector_store = VectorStoreFactory.create(store_type, **kwargs)
    
    return _vector_store


def reset_vector_store():
    """Reset global vector store instance."""
    global _vector_store
    _vector_store = None
