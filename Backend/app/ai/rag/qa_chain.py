"""
Question-Answering chain for RAG system.
Combines retrieval with LLM generation.
"""
from typing import Dict, Any, Optional, List
from ..llm.base import BaseLLM
from ..llm.prompts import RAG_QA_SYSTEM, RAG_QA_PROMPT
from .retriever import RAGRetriever
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class RAGQAChain:
    """RAG-based question-answering chain."""
    
    def __init__(
        self,
        llm: BaseLLM,
        retriever: Optional[RAGRetriever] = None,
        min_confidence: float = 0.3
    ):
        self.llm = llm
        self.retriever = retriever or RAGRetriever()
        self.min_confidence = min_confidence
    
    async def ask(
        self,
        question: str,
        context_filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.
        
        Args:
            question: User question
            context_filters: Optional metadata filters
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer, sources, confidence, and citations
        """
        # Retrieve relevant context
        retrieval_result = self.retriever.retrieve_with_context(
            query=question,
            context_filters=context_filters,
            top_k=top_k
        )
        
        context = retrieval_result["context"]
        sources = retrieval_result["sources"]
        confidence = retrieval_result["confidence"]
        
        # Check confidence threshold
        if confidence < self.min_confidence:
            return {
                "answer": "Insufficient data to provide a reliable answer. Please provide more context or check back later.",
                "sources": [],
                "confidence": confidence,
                "citations": []
            }
        
        # Generate answer using LLM
        prompt = RAG_QA_PROMPT.format(
            context=context,
            question=question
        )
        
        try:
            answer = await self.llm.generate(
                prompt=prompt,
                system_prompt=RAG_QA_SYSTEM,
                temperature=0.3,
                max_tokens=1000
            )
        except Exception as e:
            logger.error(f"Error generating RAG answer: {e}")
            return {
                "answer": "Error generating answer. Please try again.",
                "sources": sources,
                "confidence": confidence,
                "citations": []
            }
        
        # Extract citations from answer
        citations = self._extract_citations(answer, sources)
        
        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "citations": citations
        }
    
    def _extract_citations(self, answer: str, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract citations from answer text."""
        citations = []
        for i, source in enumerate(sources, 1):
            if f"[Source {i}]" in answer or f"source {i}" in answer.lower():
                citations.append({
                    "index": i,
                    "source": source.get("source", "Unknown"),
                    "metadata": source.get("metadata", {})
                })
        return citations

