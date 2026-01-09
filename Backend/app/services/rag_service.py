"""
RAG (Retrieval-Augmented Generation) Service for CampusShield AI.
Lazy-loads vector store and indexer only when needed.
Gracefully degrades if dependencies are missing.
"""

import logging
from typing import Optional, Dict, Any, List

from ..core.config import settings
from ..core.logging import setup_logger

logger = setup_logger(__name__)


class RAGService:
    """
    Centralized RAG service with lazy initialization and graceful degradation.
    """
    
    def __init__(self):
        self._vector_store = None
        self._indexer = None
        self._retriever = None
        self._qa_chain = None
        self._available = False
        self._initialized = False
        self._init_error = None
        
        # Try to initialize if RAG is enabled
        if settings.enable_rag:
            self._initialize()
    
    def _initialize(self):
        """Initialize RAG components (lazy-loaded on first use)."""
        if self._initialized or self._init_error is not None:
            return
        
        try:
            logger.info("Initializing RAG service...")
            
            # Try importing RAG modules
            from ..ai.rag.vector_store import get_vector_store
            from ..ai.rag.indexer import DocumentIndexer
            from ..ai.rag.retriever import RAGRetriever
            
            # Lazy-load vector store
            self._vector_store = get_vector_store(settings.vector_store_type)
            
            # Initialize indexer and retriever
            self._indexer = DocumentIndexer(self._vector_store)
            self._retriever = RAGRetriever(self._vector_store)
            
            self._available = True
            self._initialized = True
            logger.info(f"RAG service initialized successfully with {settings.vector_store_type} vector store")
        
        except ImportError as e:
            logger.warning(f"RAG modules not available: {e}")
            self._init_error = str(e)
            self._available = False
        
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            self._init_error = str(e)
            self._available = False
    
    @property
    def is_available(self) -> bool:
        """Check if RAG is available and initialized."""
        return self._available and self._initialized
    
    @property
    def vector_store(self):
        """Get vector store (initializes RAG if needed)."""
        if not self._initialized:
            self._initialize()
        return self._vector_store
    
    @property
    def indexer(self):
        """Get document indexer (initializes RAG if needed)."""
        if not self._initialized:
            self._initialize()
        return self._indexer
    
    @property
    def retriever(self):
        """Get retriever (initializes RAG if needed)."""
        if not self._initialized:
            self._initialize()
        return self._retriever
    
    def index_text(
        self,
        text: str,
        metadata: Dict[str, Any],
        chunk: bool = True
    ) -> List[str]:
        """Index a text document."""
        if not self.is_available:
            logger.warning("RAG service not available - document indexing skipped")
            return []
        
        try:
            return self.indexer.index_text(text, metadata, chunk)
        except Exception as e:
            logger.error(f"Failed to index document: {e}")
            return []
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents for a query."""
        if not self.is_available:
            logger.warning("RAG service not available - retrieval skipped")
            return []
        
        try:
            return self.retriever.retrieve(query, top_k, filters)
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "available": self.is_available,
            "enabled": settings.enable_rag,
            "initialized": self._initialized,
            "vector_store_type": settings.vector_store_type,
            "error": self._init_error,
        }


# Global RAG service instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def is_rag_available() -> bool:
    """Check if RAG service is available and configured."""
    service = get_rag_service()
    return service.is_available
