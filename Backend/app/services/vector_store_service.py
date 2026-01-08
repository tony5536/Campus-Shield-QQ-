"""
Vector Store Service wrapper for FastAPI integration.

Provides singleton pattern for vector store initialization and management.
"""

from typing import Optional
from ai.vector_store import VectorStore, VectorStoreFactory, get_vector_store as get_vector_store_util

__all__ = ['get_vector_store', 'reset_vector_store']


def get_vector_store(
    store_type: str = "faiss",
    **kwargs
) -> VectorStore:
    """Get vector store instance."""
    return get_vector_store_util(store_type=store_type, **kwargs)


def reset_vector_store():
    """Reset vector store instance."""
    from ai.vector_store import reset_vector_store as reset_store
    reset_store()
