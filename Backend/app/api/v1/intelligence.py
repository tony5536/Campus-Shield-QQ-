"""
Incident Intelligence Engine API - Phase 2
Automatically analyzes incidents and generates intelligence.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core.security import get_db
from ...models.incident import Incident
from ...ai.llm.openai import OpenAILLM
from ...ai.agents.analyst_agent import AnalystAgent
from ...ai.agents.orchestrator import AgentOrchestrator
from ...core.config import settings
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize LLM and agents
llm = OpenAILLM()
orchestrator = AgentOrchestrator(llm)


class IntelligenceResponse(BaseModel):
    """Response model for intelligence analysis."""
    incident_id: int
    severity: str
    risk_score: float
    root_cause: str
    similar_cases: int
    recommended_actions: List[str]
    confidence: float
    generated_at: datetime


@router.post("/analyze", response_model=IntelligenceResponse)
async def analyze_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """
    Analyze an incident and generate intelligence.
    
    Returns:
        Comprehensive intelligence analysis including:
        - Severity classification
        - Risk score
        - Root cause inference
        - Pattern matching
        - Recommended actions
        - Confidence score
    """
    # Fetch incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Convert to dict
    incident_data = {
        "id": incident.id,
        "incident_type": incident.incident_type,
        "severity": incident.severity,
        "status": incident.status,
        "description": incident.description,
        "location": incident.location,
        "timestamp": incident.timestamp.isoformat() if incident.timestamp else None,
        "camera_id": incident.camera_id,
    }
    
    # Get historical context (similar incidents)
    historical = db.query(Incident).filter(
        Incident.id != incident_id,
        Incident.incident_type == incident.incident_type
    ).order_by(Incident.timestamp.desc()).limit(10).all()
    
    historical_data = [
        {
            "id": h.id,
            "incident_type": h.incident_type,
            "severity": h.severity,
            "location": h.location,
            "timestamp": h.timestamp.isoformat() if h.timestamp else None,
        }
        for h in historical
    ]
    
    # Analyze using orchestrator
    try:
        analysis = await orchestrator.analyze_incident_comprehensive(
            incident_data,
            historical_data
        )
        
        return IntelligenceResponse(
            incident_id=incident.id,
            severity=analysis.get("severity", "Medium"),
            risk_score=analysis.get("risk_score", 0.5),
            root_cause=analysis.get("root_cause", "Analysis pending"),
            similar_cases=analysis.get("similar_cases", 0),
            recommended_actions=analysis.get("recommended_actions", []),
            confidence=analysis.get("confidence", 0.7),
            generated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error analyzing incident {incident_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

