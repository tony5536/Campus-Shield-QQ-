"""
AI Query & Analysis APIs - Consolidated Endpoint
Single source of truth for AI interactions.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from ...core.security import get_db
from ...core.config import settings
from ...core.logging import setup_logger
from ...services.langchain_service import get_langchain_service

logger = setup_logger(__name__)
router = APIRouter()

# Initialize LLM service
llm_service = get_langchain_service()


class AIAnalyzeRequest(BaseModel):
    """
    FLEXIBLE AI REQUEST - Accepts multiple input formats.
    """
    query: Optional[str] = Field(None, description="User query (preferred)")
    text: Optional[str] = Field(None, description="Alternative to query")
    description: Optional[str] = Field(None, description="Alternative to query")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Unauthorized person detected in building A after hours"
            }
        }


class AIAnalyzeResponse(BaseModel):
    """
    STANDARD AI RESPONSE FORMAT
    """
    severity: str = Field(description="LOW | MEDIUM | HIGH")
    summary: str = Field(description="Analysis summary")
    recommended_action: str = Field(description="Recommended action")
    confidence: float = Field(description="Confidence 0-1")


@router.post("/analyze", response_model=AIAnalyzeResponse)
async def analyze_ai(request: AIAnalyzeRequest):
    """
    CANONICAL AI ANALYSIS ENDPOINT
    POST /api/v1/ai/analyze
    
    Flexible input: accepts query, text, or description field.
    
    Example:
    {
        "query": "Unauthorized person in building A"
    }
    
    Returns:
    {
        "severity": "HIGH",
        "summary": "...",
        "recommended_action": "...",
        "confidence": 0.92
    }
    """
    try:
        # Accept flexible input
        input_text = request.query or request.text or request.description
        
        if not input_text or not input_text.strip():
            raise HTTPException(status_code=400, detail="query/text/description is required")

        logger.info(f"Processing AI query: {input_text[:50]}...")
        
        # Check if LLM is available
        if not llm_service.is_available:
            logger.warning("LLM service not available, returning fallback response")
            return AIAnalyzeResponse(
                severity="MEDIUM",
                summary="AI Service is temporarily unavailable. Please try again later.",
                recommended_action="Review incident manually following standard protocols.",
                confidence=0.0
            )

        # Call LLM (would need to implement this in langchain_service)
        # For now, return a reasonable response based on keywords
        analysis = _analyze_locally(input_text)
        
        return AIAnalyzeResponse(
            severity=analysis["severity"],
            summary=analysis["summary"],
            recommended_action=analysis["recommended_action"],
            confidence=analysis["confidence"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI analyze endpoint: {e}", exc_info=True)
        # Graceful fallback - never return 404
        return AIAnalyzeResponse(
            severity="MEDIUM",
            summary="Analysis service error occurred",
            recommended_action="Please review incident manually",
            confidence=0.0
        )


def _analyze_locally(text: str) -> dict:
    """
    Local analysis fallback (no LLM required).
    Provides reasonable responses based on keyword matching.
    """
    text_lower = text.lower()
    
    # Determine severity
    high_severity_keywords = ["unauthorized", "critical", "emergency", "intruder", "breach", "attack", "armed", "weapon", "fire", "explosion"]
    medium_severity_keywords = ["suspicious", "alert", "warning", "unusual", "concern", "risk"]
    
    severity = "LOW"
    confidence = 0.6
    
    for keyword in high_severity_keywords:
        if keyword in text_lower:
            severity = "HIGH"
            confidence = 0.85
            break
    
    if severity == "LOW":
        for keyword in medium_severity_keywords:
            if keyword in text_lower:
                severity = "MEDIUM"
                confidence = 0.70
                break
    
    # Generate summary
    if severity == "HIGH":
        summary = f"CRITICAL ALERT: {text[:80]}... - Immediate action required. This incident has been flagged as HIGH priority and requires immediate security team response."
        action = "Immediately dispatch security team. Establish perimeter if applicable. Contact emergency services if needed."
    elif severity == "MEDIUM":
        summary = f"ALERT: {text[:80]}... - This incident has been flagged as MEDIUM priority. Investigate further and assess situation."
        action = "Send security team to location. Gather additional information. Monitor for escalation."
    else:
        summary = f"NOTICE: {text[:80]}... - This incident has been logged as LOW priority for review."
        action = "Log incident for records. Monitor situation. Escalate if severity increases."
    
    return {
        "severity": severity,
        "summary": summary,
        "recommended_action": action,
        "confidence": confidence
    }

