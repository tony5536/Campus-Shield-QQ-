"""
Retriever for RAG system.
Handles similarity search with metadata filtering.
"""
from typing import List, Dict, Any, Optional
from .vector_store import VectorStore, get_vector_store
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class RAGRetriever:
    """Retrieves relevant documents for RAG."""
    
    def __init__(self, vector_store: Optional[VectorStore] = None, top_k: int = 5):
        self.vector_store = vector_store or get_vector_store()
        self.top_k = top_k
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter: Metadata filter (e.g., {"severity": "High"})
            min_score: Minimum similarity score threshold
            
        Returns:
            List of retrieved documents with text, metadata, and score
        """
        top_k = top_k or self.top_k
        
        results = self.vector_store.similarity_search(
            query=query,
            k=top_k,
            filter=filter
        )
        
        # Filter by minimum score if provided
        if min_score is not None:
            results = [r for r in results if r.get("score", float('inf')) <= min_score]
        
        # Sort by score (lower is better for L2 distance)
        results.sort(key=lambda x: x.get("score", float('inf')))
        
        return results
    
    def retrieve_with_context(
        self,
        query: str,
        context_filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve documents and format as context string.
        
        Returns:
            Dictionary with 'context' (formatted text) and 'sources' (metadata list)
        """
        results = self.retrieve(query, top_k=top_k, filter=context_filters)
        
        if not results:
            return {
                "context": "",
                "sources": [],
                "confidence": 0.0
            }
        
        # Format context
        context_parts = []
        sources = []
        
        for i, result in enumerate(results, 1):
            text = result.get("text", "")
            metadata = result.get("metadata", {})
            score = result.get("score", float('inf'))
            
            context_parts.append(f"[Source {i}]\n{text}\n")
            sources.append({
                "source": metadata.get("source", "Unknown"),
                "metadata": metadata,
                "score": score
            })
        
        context = "\n".join(context_parts)
        
        # Calculate confidence (inverse of average score, normalized)
        avg_score = sum(r.get("score", 0) for r in results) / len(results)
        confidence = max(0.0, min(1.0, 1.0 / (1.0 + avg_score)))
        
        return {
            "context": context,
            "sources": sources,
            "confidence": confidence
        }

