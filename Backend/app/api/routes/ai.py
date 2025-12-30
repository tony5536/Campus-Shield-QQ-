"""
AI-powered endpoints for CampusShield AI.
Provides incident explanation, report generation, and admin assistant.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...models.incident import Incident
from ...services.llm_service import llm_service
from ...utils.security import get_db
from ...utils.logger import setup_logger

logger = setup_logger()
router = APIRouter()


# ------------------------------------------------------------------
# Request/Response Models
# ------------------------------------------------------------------

class IncidentExplanationRequest(BaseModel):
    """Request model for incident explanation"""
    incident_id: int


class IncidentExplanationResponse(BaseModel):
    """Response model for incident explanation"""
    incident_id: int
    explanation: str
    generated_at: datetime


class ReportGenerationRequest(BaseModel):
    """Request model for report generation"""
    incident_id: int
    include_recommendations: bool = True


class ReportGenerationResponse(BaseModel):
    """Response model for report generation"""
    incident_id: int
    report: str
    generated_at: datetime


class AssistantQueryRequest(BaseModel):
    """Request model for admin assistant"""
    query: str = Field(..., description="Natural language query from admin")
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional context (incidents, stats, etc.)"
    )


class AIAssistRequest(BaseModel):
    """Request model for AI assist endpoint (hackathon demo)"""
    query: str = Field(..., description="Incident description or query to analyze")


class AssistantQueryResponse(BaseModel):
    """Response model for admin assistant"""
    query: str
    response: str
    generated_at: datetime


# ------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------

@router.post("/explain-incident", response_model=IncidentExplanationResponse)
async def explain_incident(
    request: IncidentExplanationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a human-readable explanation of an incident for security staff.
    
    Example request:
    ```json
    {
        "incident_id": 1
    }
    ```
    
    Example response:
    ```json
    {
        "incident_id": 1,
        "explanation": "This incident involves... [AI-generated explanation]",
        "generated_at": "2025-01-27T10:30:00Z"
    }
    ```
    """
    try:
        # Fetch incident from database
        incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Convert SQLAlchemy model to dict
        incident_data = {
            "id": incident.id,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "status": incident.status,
            "description": incident.description,
            "timestamp": incident.timestamp.isoformat() if incident.timestamp else None,
            "camera_id": incident.camera_id,
        }
        
        # Generate explanation using LLM
        explanation = await llm_service.explain_incident(incident_data)
        
        return IncidentExplanationResponse(
            incident_id=incident.id,
            explanation=explanation,
            generated_at=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining incident {request.incident_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")


@router.post("/generate-report", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Auto-generate a professional incident report.
    
    Example request:
    ```json
    {
        "incident_id": 1,
        "include_recommendations": true
    }
    ```
    
    Example response:
    ```json
    {
        "incident_id": 1,
        "report": "EXECUTIVE SUMMARY\n... [AI-generated report]",
        "generated_at": "2025-01-27T10:30:00Z"
    }
    ```
    """
    try:
        # Fetch incident from database
        incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Convert SQLAlchemy model to dict
        incident_data = {
            "id": incident.id,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "status": incident.status,
            "description": incident.description,
            "timestamp": incident.timestamp.isoformat() if incident.timestamp else None,
            "camera_id": incident.camera_id,
        }
        
        # Generate report using LLM
        report = await llm_service.generate_report(
            incident_data,
            include_recommendations=request.include_recommendations
        )
        
        return ReportGenerationResponse(
            incident_id=incident.id,
            report=report,
            generated_at=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report for incident {request.incident_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.post("/assistant", response_model=AssistantQueryResponse)
async def admin_assistant(request: AssistantQueryRequest):
    """
    Admin AI Assistant - Natural language query handler.
    Answers questions about incidents, provides insights, and assists with queries.
    
    Example request:
    ```json
    {
        "query": "What are the most common incident types this week?",
        "context": {
            "recent_incidents": [...]
        }
    }
    ```
    
    Example response:
    ```json
    {
        "query": "What are the most common incident types this week?",
        "response": "Based on the recent incidents... [AI-generated response]",
        "generated_at": "2025-01-27T10:30:00Z"
    }
    ```
    """
    try:
        # Process query using LLM
        response = await llm_service.assistant_query(
            user_query=request.query,
            context=request.context
        )
        
        return AssistantQueryResponse(
            query=request.query,
            response=response,
            generated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error processing assistant query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/assist")
async def ai_assist(request: AIAssistRequest):
    """
    Hackathon Demo Endpoint: AI-powered incident analysis.
    Analyzes incident queries and returns structured analysis with severity assessment.
    
    Example request:
    ```json
    {
        "query": "Unauthorized person detected in building A after hours"
    }
    ```
    
    Example response:
    ```json
    {
        "summary": "Unauthorized access detected in restricted area after operating hours...",
        "severity": "High",
        "recommended_action": "Immediately dispatch security team to Building A...",
        "confidence": "92%"
    }
    ```
    """
    try:
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Use the new analyze_incident function
        analysis = await llm_service.analyze_incident(request.query.strip())
        
        return {
            "query": request.query,
            "analysis": analysis,
            "generated_at": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI assist endpoint: {e}")
        # Return safe fallback - NEVER crash during demo
        return {
            "query": request.query if request.query else "Unknown",
            "analysis": {
                "summary": "AI analysis temporarily unavailable. Please review manually.",
                "severity": "Medium",
                "recommended_action": "Follow standard security protocols and review incident details.",
                "confidence": "N/A"
            },
            "generated_at": datetime.utcnow(),
            "error": "Analysis service temporarily unavailable"
        }


@router.get("/assistant/stats")
async def get_assistant_stats(db: Session = Depends(get_db)):
    """
    Get statistics for the AI assistant context.
    Returns summary data that can be used as context for assistant queries.
    """
    try:
        # Get recent incidents
        recent_incidents = db.query(Incident).order_by(Incident.timestamp.desc()).limit(10).all()
        
        # Calculate statistics
        total_incidents = db.query(Incident).count()
        active_incidents = db.query(Incident).filter(Incident.status == "open").count()
        
        # Group by type
        incidents_by_type = {}
        for inc in db.query(Incident).all():
            inc_type = inc.incident_type
            incidents_by_type[inc_type] = incidents_by_type.get(inc_type, 0) + 1
        
        # Calculate average severity
        all_incidents = db.query(Incident).all()
        avg_severity = sum(inc.severity for inc in all_incidents) / len(all_incidents) if all_incidents else 0.0
        
        stats = {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "resolved_incidents": total_incidents - active_incidents,
            "incidents_by_type": incidents_by_type,
            "average_severity": round(avg_severity, 2),
            "recent_incidents": [
                {
                    "id": inc.id,
                    "type": inc.incident_type,
                    "severity": inc.severity,
                    "status": inc.status,
                    "timestamp": inc.timestamp.isoformat() if inc.timestamp else None,
                }
                for inc in recent_incidents
            ]
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error fetching assistant stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

