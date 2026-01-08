"""
AI Query & Analysis APIs - Phase 3
RAG-based question answering and AI assistant.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core.security import get_db
from ...ai.llm.openai import OpenAILLM
from ...ai.rag.qa_chain import RAGQAChain
from ...ai.rag.retriever import RAGRetriever
from ...core.config import settings
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize RAG components
llm = OpenAILLM()
retriever = RAGRetriever()
qa_chain = RAGQAChain(llm, retriever)


class AskRequest(BaseModel):
    """Request model for AI ask endpoint."""
    question: str = Field(..., description="Question to ask the AI assistant")
    context_filters: Optional[Dict[str, Any]] = Field(None, description="Optional metadata filters")


class AskResponse(BaseModel):
    """Response model for AI ask endpoint."""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    citations: List[Dict[str, Any]]
    generated_at: datetime


@router.post("/ask", response_model=AskResponse)
async def ask_ai(
    request: AskRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question using RAG (Retrieval-Augmented Generation).
    
    The AI will:
    - Retrieve relevant context from indexed documents
    - Answer based ONLY on retrieved context
    - Cite sources
    - Refuse to answer if confidence is too low
    
    Example:
        "What are the most common incident types in the library?"
        "What security policies apply to after-hours access?"
    """
    try:
        result = await qa_chain.ask(
            question=request.question,
            context_filters=request.context_filters,
            top_k=5
        )
        
        return AskResponse(
            answer=result.get("answer", "Unable to generate answer"),
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0),
            citations=result.get("citations", []),
            generated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error in AI ask endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"AI query error: {str(e)}")

