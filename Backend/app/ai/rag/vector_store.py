"""
Vector store abstraction for RAG system.
Supports FAISS (local) and cloud providers (Pinecone, Weaviate).
With lazy loading and graceful degradation if dependencies are missing.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from ...core.config import settings
from ...core.logging import setup_logger

logger = setup_logger(__name__)

# Check for optional dependencies
FAISS_AVAILABLE = False
SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    logger.warning("faiss-cpu not installed. FAISS vector store will be unavailable.")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("sentence-transformers not installed. Embeddings will be unavailable.")


class VectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def delete(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        pass


class FAISSVectorStore(VectorStore):
    """FAISS-based local vector store with lazy initialization."""
    
    def __init__(self, embedding_model: str = None, dimension: int = 384):
        if not FAISS_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE:
            missing = []
            if not FAISS_AVAILABLE:
                missing.append("faiss-cpu")
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                missing.append("sentence-transformers")
            raise ImportError(
                f"FAISS vector store requires: {', '.join(missing)}. "
                "Install with: pip install {' '.join(missing)}"
            )
        
        self.embedding_model_name = embedding_model or settings.embedding_model
        self._embedder = None  # Lazy-loaded
        self.dimension = dimension
        self.index = None
        self.documents = []
        self.metadatas = []
        self._initialized = False
        
        logger.info(f"Initializing FAISS vector store with model: {self.embedding_model_name}")
        self._lazy_init()
    
    def _lazy_init(self):
        """Lazy-load embedder and build index on first use."""
        if self._initialized:
            return
        
        try:
            if self._embedder is None:
                self._embedder = SentenceTransformer(self.embedding_model_name)
            self._build_index()
            self._initialized = True
            logger.info("FAISS vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS vector store: {e}")
            raise
    
    @property
    def embedder(self):
        """Get embedder with lazy initialization."""
        if self._embedder is None:
            self._lazy_init()
        return self._embedder
    
    def _build_index(self):
        """Initialize FAISS index."""
        if not FAISS_AVAILABLE:
            raise RuntimeError("FAISS not available")
        self.index = faiss.IndexFlatL2(self.dimension)
    
    def _embed(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts."""
        embeddings = self.embedder.encode(texts, show_progress_bar=False)
        return embeddings.astype('float32')
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to FAISS index."""
        if not texts:
            return []
        
        if not self._initialized:
            self._lazy_init()
        
        embeddings = self._embed(texts)
        self.index.add(embeddings)
        
        if ids is None:
            ids = [f"doc_{len(self.documents) + i}" for i in range(len(texts))]
        
        self.documents.extend(texts)
        self.metadatas.extend(metadatas or [{}] * len(texts))
        
        logger.info(f"Added {len(texts)} documents to FAISS vector store")
        return ids
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self._initialized:
            self._lazy_init()
        
        if self.index.ntotal == 0:
            return []
        
        query_embedding = self._embed([query])
        distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                result = {
                    "text": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "score": float(distances[0][i])
                }
                # Apply filter if provided
                if filter:
                    if all(result["metadata"].get(k) == v for k, v in filter.items()):
                        results.append(result)
                else:
                    results.append(result)
        
        return results
    
    def delete(self, ids: List[str]) -> bool:
        """Delete documents (FAISS limitation: requires rebuild)."""
        # FAISS doesn't support efficient deletion, would need to rebuild
        logger.warning("FAISS doesn't support efficient deletion. Consider rebuilding index.")
        return False


class NoOpVectorStore(VectorStore):
    """No-op vector store for when RAG is disabled."""
    
    def __init__(self):
        logger.warning("Using no-op vector store. RAG features will be disabled.")
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        logger.warning("add_documents called on no-op vector store")
        return []
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        logger.warning("similarity_search called on no-op vector store")
        return []
    
    def delete(self, ids: List[str]) -> bool:
        return False


# Global vector store instance (lazy-loaded)
_vector_store_instance: Optional[VectorStore] = None
_vector_store_error: Optional[str] = None


def get_vector_store(store_type: str = None) -> VectorStore:
    """Factory function to get vector store instance with graceful degradation."""
    global _vector_store_instance, _vector_store_error
    
    # Return cached instance if available
    if _vector_store_instance is not None:
        return _vector_store_instance
    
    # Check if we already tried and failed
    if _vector_store_error is not None:
        logger.warning(f"Vector store unavailable: {_vector_store_error}. Using no-op store.")
        _vector_store_instance = NoOpVectorStore()
        return _vector_store_instance
    
    store_type = store_type or settings.vector_store_type
    
    try:
        if store_type == "faiss":
            if not FAISS_AVAILABLE or not SENTENCE_TRANSFORMERS_AVAILABLE:
                missing = []
                if not FAISS_AVAILABLE:
                    missing.append("faiss-cpu")
                if not SENTENCE_TRANSFORMERS_AVAILABLE:
                    missing.append("sentence-transformers")
                raise ImportError(f"Missing dependencies: {', '.join(missing)}")
            
            _vector_store_instance = FAISSVectorStore()
            logger.info("Vector store initialized: FAISS")
            return _vector_store_instance
        
        elif store_type == "pinecone":
            raise NotImplementedError("Pinecone not yet implemented")
        
        elif store_type == "weaviate":
            raise NotImplementedError("Weaviate not yet implemented")
        
        else:
            raise ValueError(f"Unknown vector store type: {store_type}")
    
    except Exception as e:
        _vector_store_error = str(e)
        logger.error(f"Failed to initialize vector store: {e}")
        logger.warning("Falling back to no-op vector store")
        _vector_store_instance = NoOpVectorStore()
        return _vector_store_instance

