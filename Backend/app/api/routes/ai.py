"""
AI-powered endpoints for CampusShield AI - LEGACY ROUTES.
These are aliases for v1 API endpoints.
CRITICAL: Uses same fallback logic as v1 - NO LLM SERVICE METHOD CALLS
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from ...core.logging import setup_logger

# Import from core logic if possible, or duplicate safely
# Here we avoid circular imports by keeping local logic for now

logger = setup_logger(__name__)
router = APIRouter()

# ------------------------------------------------------------------
# Request/Response Models (Flexible for compatibility)
# ------------------------------------------------------------------

class AIAnalyzeRequest(BaseModel):
    """Flexible AI request - accepts multiple input formats."""
    query: Optional[str] = Field(None, description="User query (preferred)")
    text: Optional[str] = Field(None, description="Alternative to query")
    description: Optional[str] = Field(None, description="Alternative to query")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")

    class Config:
        json_schema_extra = {
            "example": {"query": "Unauthorized person detected in building A after hours"}
        }


class AIAnalyzeResponse(BaseModel):
    """Standard AI response format."""
    severity: str = Field(description="LOW | MEDIUM | HIGH")
    summary: str = Field(description="Analysis summary")
    recommended_action: str = Field(description="Recommended action")
    confidence: float = Field(description="Confidence 0-1")


# ------------------------------------------------------------------
# HELPER: Local Analysis (Fallback, no LLM required)
# ------------------------------------------------------------------

def _analyze_locally(text: str) -> dict:
    """
    Local analysis fallback (no LLM required).
    Provides reasonable responses based on keyword matching.
    """
    text_lower = text.lower()
    
    # Determine severity
    high_severity_keywords = [
        "unauthorized", "critical", "emergency", "intruder", "breach",
        "attack", "armed", "weapon", "fire", "explosion", "threat"
    ]
    medium_severity_keywords = [
        "suspicious", "alert", "warning", "unusual", "concern", "risk",
        "suspicious activity", "possible breach"
    ]
    
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
        summary = (
            f"CRITICAL ALERT: {text[:80]}... - Immediate action required. "
            "This incident has been flagged as HIGH priority and requires immediate "
            "security team response."
        )
        action = (
            "Immediately dispatch security team. Establish perimeter if applicable. "
            "Contact emergency services if needed."
        )
    elif severity == "MEDIUM":
        summary = (
            f"ALERT: {text[:80]}... - This incident has been flagged as MEDIUM priority. "
            "Investigate further and assess situation."
        )
        action = "Send security team to location. Gather additional information. Monitor for escalation."
    else:
        summary = (
            f"NOTICE: {text[:80]}... - This incident has been logged as LOW priority for review."
        )
        action = "Log incident for records. Monitor situation. Escalate if severity increases."
    
    return {
        "severity": severity,
        "summary": summary,
        "recommended_action": action,
        "confidence": confidence
    }


# ------------------------------------------------------------------
# ENDPOINTS - All with graceful fallback
# ------------------------------------------------------------------

@router.post("/analyze", response_model=AIAnalyzeResponse)
async def analyze(request: AIAnalyzeRequest):
    """
    LEGACY ALIAS: POST /api/ai/analyze
    
    Flexible input: accepts query, text, or description field.
    
    Returns:
    {
        "severity": "LOW | MEDIUM | HIGH",
        "summary": "...",
        "recommended_action": "...",
        "confidence": 0.0-1.0
    }
    
    NEVER returns 404 - always graceful fallback.
    """
    try:
        # Accept flexible input
        input_text = request.query or request.text or request.description
        
        if not input_text or not input_text.strip():
            raise HTTPException(status_code=400, detail="query/text/description is required")

        logger.info(f"[Legacy AI] Processing query: {input_text[:50]}...")
        
        # If LLM is available, still use local fallback for now
        # (LLM service methods don't exist yet)
        logger.info("[Legacy AI] Using local analysis")
        analysis = _analyze_locally(input_text)
        
        return AIAnalyzeResponse(**analysis)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Legacy AI] Error in analyze endpoint: {e}", exc_info=True)
        # Graceful fallback - NEVER return 404
        return AIAnalyzeResponse(
            severity="MEDIUM",
            summary="Analysis service encountered an error. Please review incident manually.",
            recommended_action="Follow standard security protocols and review incident details.",
            confidence=0.0
        )


@router.post("/assist")
async def assist(request: AIAnalyzeRequest):
    """
    Legacy Hackathon Demo Endpoint: POST /api/ai/assist
    
    Analyzes incident queries and returns structured analysis.
    Same as /analyze but may return additional fields.
    """
    try:
        input_text = request.query or request.text or request.description
        
        if not input_text or not input_text.strip():
            raise HTTPException(status_code=400, detail="query/text/description is required")

        logger.info(f"[Legacy AI Assist] Processing query: {input_text[:50]}...")
        
        # Use same local analysis
        analysis = _analyze_locally(input_text)
        
        return {
            "analysis": {
                "severity": analysis["severity"],
                "summary": analysis["summary"],
                "recommended_action": analysis["recommended_action"],
                "confidence": analysis["confidence"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Legacy AI Assist] Error: {e}", exc_info=True)
        # Return safe fallback
        return {
            "analysis": {
                "severity": "MEDIUM",
                "summary": "Analysis service encountered an error",
                "recommended_action": "Please review incident manually",
                "confidence": 0.0
            }
        }
