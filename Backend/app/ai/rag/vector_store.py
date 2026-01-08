"""
Vector store abstraction for RAG system.
Supports FAISS (local) and cloud providers (Pinecone, Weaviate).
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np
from ...core.config import settings
from ...core.logging import setup_logger

logger = setup_logger(__name__)


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
    """FAISS-based local vector store."""
    
    def __init__(self, embedding_model: str = None, dimension: int = 384):
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("faiss-cpu and sentence-transformers required for FAISS vector store")
        
        self.embedding_model_name = embedding_model or settings.embedding_model
        self.embedder = SentenceTransformer(self.embedding_model_name)
        self.dimension = dimension
        self.index = None
        self.documents = []
        self.metadatas = []
        self._build_index()
    
    def _build_index(self):
        """Initialize FAISS index."""
        import faiss
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
        
        embeddings = self._embed(texts)
        self.index.add(embeddings)
        
        if ids is None:
            ids = [f"doc_{len(self.documents) + i}" for i in range(len(texts))]
        
        self.documents.extend(texts)
        self.metadatas.extend(metadatas or [{}] * len(texts))
        
        return ids
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents."""
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


def get_vector_store(store_type: str = None) -> VectorStore:
    """Factory function to get vector store instance."""
    store_type = store_type or settings.vector_store_type
    
    if store_type == "faiss":
        return FAISSVectorStore()
    elif store_type == "pinecone":
        # TODO: Implement Pinecone
        raise NotImplementedError("Pinecone not yet implemented")
    elif store_type == "weaviate":
        # TODO: Implement Weaviate
        raise NotImplementedError("Weaviate not yet implemented")
    else:
        raise ValueError(f"Unknown vector store type: {store_type}")

