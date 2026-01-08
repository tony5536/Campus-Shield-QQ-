"""
FastAPI routes for LLM integration endpoints.

Provides multi-turn chat, summarization, report generation,
anomaly explanation, and historical incident retrieval.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse

from ...services.advanced_llm_service import get_llm_service, LLMConfig
from ...services.langchain_service import is_langchain_available
from ...core.logging import setup_logger

# Configure logging
logger = setup_logger()

# Create router
router = APIRouter(
    prefix="/api/llm",
    tags=["LLM & AI Insights"],
    responses={500: {"description": "Internal Server Error"}, 503: {"description": "Service Unavailable"}},
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_llm_service_or_raise():
    """
    Get LLM service or raise 503 if unavailable.
    
    Returns:
        LLM service instance
        
    Raises:
        HTTPException: 503 if service is unavailable
    """
    try:
        # Check LangChain availability first
        if not is_langchain_available():
            raise HTTPException(status_code=503, detail="LLM service unavailable: LangChain not configured")
        
        service = get_llm_service()
        return service
    except (ImportError, ModuleNotFoundError) as e:
        logger.error(f"LLM service import error: {e}")
        raise HTTPException(status_code=503, detail="LLM service unavailable: required modules not available")
    except Exception as e:
        # Check if it's a service initialization error
        error_str = str(e).lower()
        if "unavailable" in error_str or "not available" in error_str or "not configured" in error_str:
            raise HTTPException(status_code=503, detail=f"LLM service unavailable: {str(e)}")
        # Otherwise, it's a real error
        raise


# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE
# ============================================================================

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")


class ChatRequest(BaseModel):
    """Multi-turn chat request."""
    user_input: str = Field(..., description="User query/message")
    conversation_id: str = Field("default", description="Conversation identifier for context")
    use_context: bool = Field(True, description="Retrieve historical incidents for context")


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    chat_history: List[ChatMessage] = Field(..., description="Updated chat history")


class SummarizeRequest(BaseModel):
    """Incident summarization request."""
    incident_ids: Optional[List[int]] = Field(None, description="Specific incident IDs to summarize")
    period: str = Field("day", description="Time period: 'day', 'week', 'month'")
    focus_area: Optional[str] = Field(None, description="Focus area for summarization")


class SummarizeResponse(BaseModel):
    """Summarization response."""
    summary: str = Field(..., description="Summary text")
    incident_count: int = Field(..., description="Number of incidents summarized")
    generated_at: str = Field(..., description="Generation timestamp")


class ReportRequest(BaseModel):
    """Report generation request."""
    report_type: str = Field("daily", description="Report type: 'daily' or 'weekly'")
    start_date: Optional[str] = Field(None, description="Report start date")
    end_date: Optional[str] = Field(None, description="Report end date")
    include_recommendations: bool = Field(True, description="Include recommendations")


class ReportResponse(BaseModel):
    """Report response."""
    report: str = Field(..., description="Generated report")
    report_type: str = Field(..., description="Report type")
    generated_at: str = Field(..., description="Generation timestamp")


class AnomalyExplanationRequest(BaseModel):
    """Anomaly explanation request."""
    anomaly_score: float = Field(..., ge=0.0, le=1.0, description="Anomaly score (0-1)")
    anomaly_type: str = Field(..., description="Type of anomaly detected")
    affected_area: str = Field(..., description="Location/area affected")
    threshold: float = Field(0.7, ge=0.0, le=1.0, description="Anomaly threshold")
    comparisons: Optional[List[Dict[str, Any]]] = Field(None, description="Metric comparisons")


class AnomalyExplanationResponse(BaseModel):
    """Anomaly explanation response."""
    explanation: str = Field(..., description="Detailed explanation")
    risk_level: str = Field(..., description="Risk level: 'Low', 'Medium', 'High', 'Critical'")
    recommendations: List[str] = Field(..., description="Recommended actions")


class HistoricalIncidentsRequest(BaseModel):
    """Historical incident retrieval request."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    min_severity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum severity filter")
    location: Optional[str] = Field(None, description="Location filter")


class HistoricalIncidentsResponse(BaseModel):
    """Historical incidents response."""
    incidents: List[Dict[str, Any]] = Field(..., description="Retrieved incidents")
    query: str = Field(..., description="Original query")
    count: int = Field(..., description="Number of results returned")


class LLMConfigRequest(BaseModel):
    """LLM configuration request."""
    model: Optional[str] = Field(None, description="LLM model name")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=4000, description="Max response tokens")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Nucleus sampling parameter")


class LLMConfigResponse(BaseModel):
    """LLM configuration response."""
    model: str = Field(..., description="Active model")
    temperature: float = Field(..., description="Temperature setting")
    max_tokens: int = Field(..., description="Max tokens setting")
    top_p: float = Field(..., description="Top-p setting")


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", response_model=Dict[str, str])
async def llm_health():
    """
    Health check for LLM service.
    
    Returns:
        Health status
    """
    try:
        service = get_llm_service_or_raise()
        return {
            "status": "healthy",
            "service": "LLM Module",
            "model": service.config.model,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LLM health check failed: {e}")
        raise HTTPException(status_code=503, detail="LLM service unavailable")


# ============================================================================
# MULTI-TURN CHAT
# ============================================================================

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Multi-turn chat endpoint.
    
    Maintains conversation context and retrieves relevant historical incidents.
    
    Args:
        request: ChatRequest with user input and conversation ID
    
    Returns:
        ChatResponse with assistant response and updated history
    """
    try:
        service = get_llm_service_or_raise()
        
        response = service.chat.chat(
            user_input=request.user_input,
            conversation_id=request.conversation_id,
        )
        
        # Convert history to ChatMessage format
        chat_history = [
            ChatMessage(
                role=msg['role'],
                content=msg['content'],
                timestamp=msg.get('timestamp'),
            )
            for msg in service.chat.get_history()
        ]
        
        return ChatResponse(
            response=response,
            conversation_id=request.conversation_id,
            chat_history=chat_history,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str) -> Dict[str, Any]:
    """
    Retrieve chat history for a conversation.
    
    Args:
        conversation_id: Conversation identifier
    
    Returns:
        Chat history and metadata
    """
    try:
        service = get_llm_service_or_raise()
        history = service.chat.get_history()
        
        return {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "role": msg['role'],
                    "content": msg['content'],
                    "timestamp": msg.get('timestamp'),
                }
                for msg in history
            ],
            "message_count": len(history),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving history")


@router.delete("/chat/history/{conversation_id}")
async def clear_chat_history(conversation_id: str) -> Dict[str, str]:
    """
    Clear chat history for a conversation.
    
    Args:
        conversation_id: Conversation identifier
    
    Returns:
        Confirmation message
    """
    try:
        service = get_llm_service_or_raise()
        service.chat.clear_history()
        service.chain_manager.clear_memory(f"chat_{conversation_id}")
        
        return {
            "status": "success",
            "message": f"Chat history cleared for conversation: {conversation_id}",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail="Error clearing history")


# ============================================================================
# INCIDENT SUMMARIZATION
# ============================================================================

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_incidents(request: SummarizeRequest):
    """
    Summarize incidents.
    
    Generates concise summaries of incident data with key insights.
    
    Args:
        request: SummarizeRequest with incident data
    
    Returns:
        SummarizeResponse with summary text
    """
    try:
        from datetime import datetime, timedelta
        from ...models.incident import Incident
        from ...core.security import get_db
        
        service = get_llm_service_or_raise()
        
        # Fetch real incidents from database
        db = next(get_db())
        try:
            # Get incidents based on request parameters
            query = db.query(Incident)
            
            # Filter by period if specified
            if request.period == "day":
                start_date = datetime.utcnow() - timedelta(days=1)
            elif request.period == "week":
                start_date = datetime.utcnow() - timedelta(days=7)
            elif request.period == "month":
                start_date = datetime.utcnow() - timedelta(days=30)
            else:
                start_date = None
            
            if start_date:
                query = query.filter(Incident.timestamp >= start_date)
            
            # Filter by specific incident IDs if provided
            if request.incident_ids:
                query = query.filter(Incident.id.in_(request.incident_ids))
            
            incidents = query.order_by(Incident.timestamp.desc()).limit(100).all()
            
            # Convert to dict format for summarizer
            incidents_data = [
                {
                    'id': inc.id,
                    'incident_type': inc.incident_type,
                    'location': inc.location or 'Unknown',
                    'zone': inc.zone or 'Unknown',
                    'severity': inc.severity,
                    'description': inc.description or '',
                    'timestamp': inc.timestamp.isoformat() if inc.timestamp else datetime.utcnow().isoformat(),
                }
                for inc in incidents
            ]
            
            if not incidents_data:
                return SummarizeResponse(
                    summary="No incidents found for the specified criteria.",
                    incident_count=0,
                    generated_at=datetime.utcnow().isoformat(),
                )
            
            summary = service.summarizer.summarize_incidents(
                incidents=incidents_data,
                focus=request.focus_area,
            )
            
            return SummarizeResponse(
                summary=summary,
                incident_count=len(incidents_data),
                generated_at=datetime.utcnow().isoformat(),
            )
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing incidents: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization error: {str(e)}")


# ============================================================================
# REPORT GENERATION
# ============================================================================

@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate security report.
    
    Creates daily or weekly reports with statistics and recommendations.
    
    Args:
        request: ReportRequest with report parameters
    
    Returns:
        ReportResponse with generated report
    """
    try:
        from datetime import datetime, timedelta
        from ...models.incident import Incident
        from ...core.security import get_db
        
        service = get_llm_service_or_raise()
        
        # Fetch real incidents from database
        db = next(get_db())
        try:
            # Determine date range based on report type
            if request.report_type == "daily":
                if request.start_date:
                    start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
                else:
                    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
            else:  # weekly
                if request.start_date:
                    start_date = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
                else:
                    start_date = datetime.utcnow() - timedelta(days=7)
                end_date = start_date + timedelta(days=7)
            
            # Query incidents in date range
            incidents = db.query(Incident).filter(
                Incident.timestamp >= start_date,
                Incident.timestamp < end_date
            ).order_by(Incident.timestamp.desc()).all()
            
            # Convert to dict format for reporter
            incidents_data = [
                {
                    'id': inc.id,
                    'incident_type': inc.incident_type,
                    'location': inc.location or 'Unknown',
                    'zone': inc.zone or 'Unknown',
                    'severity': inc.severity,
                    'description': inc.description or '',
                    'timestamp': inc.timestamp.isoformat() if inc.timestamp else datetime.utcnow().isoformat(),
                    'status': inc.status.value if hasattr(inc.status, 'value') else str(inc.status),
                }
                for inc in incidents
            ]
            
            if request.report_type == "daily":
                report = service.reporter.generate_daily_report(
                    incidents=incidents_data,
                    report_date=start_date.isoformat(),
                )
            else:
                report = service.reporter.generate_weekly_report(
                    incidents=incidents_data,
                    week_start=start_date.isoformat(),
                )
            
            return ReportResponse(
                report=report,
                report_type=request.report_type,
                generated_at=datetime.utcnow().isoformat(),
            )
        finally:
            db.close()
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")


# ============================================================================
# ANOMALY EXPLANATION
# ============================================================================

@router.post("/explain-anomaly", response_model=AnomalyExplanationResponse)
async def explain_anomaly(request: AnomalyExplanationRequest):
    """
    Explain detected anomaly.
    
    Provides detailed analysis of anomalies with risk assessment and recommendations.
    
    Args:
        request: AnomalyExplanationRequest with anomaly details
    
    Returns:
        AnomalyExplanationResponse with explanation
    """
    try:
        service = get_llm_service_or_raise()
        
        explanation = service.explainer.explain_anomaly(
            anomaly_score=request.anomaly_score,
            anomaly_type=request.anomaly_type,
            affected_area=request.affected_area,
            threshold=request.threshold,
            comparisons=request.comparisons,
        )
        
        # Determine risk level based on anomaly score
        if request.anomaly_score > 0.9:
            risk_level = "Critical"
        elif request.anomaly_score > 0.7:
            risk_level = "High"
        elif request.anomaly_score > 0.5:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        recommendations = [
            "Review incident logs and access patterns",
            "Correlate with other security events",
            "Consider activating enhanced monitoring",
            "Document findings for analysis",
        ]
        
        return AnomalyExplanationResponse(
            explanation=explanation,
            risk_level=risk_level,
            recommendations=recommendations,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining anomaly: {e}")
        raise HTTPException(status_code=500, detail=f"Anomaly explanation error: {str(e)}")


# ============================================================================
# HISTORICAL INCIDENT RETRIEVAL
# ============================================================================

@router.post("/historical-incidents", response_model=HistoricalIncidentsResponse)
async def retrieve_historical_incidents(request: HistoricalIncidentsRequest):
    """
    Retrieve historical incidents from vector database.
    
    Performs semantic similarity search on past incidents.
    
    Args:
        request: HistoricalIncidentsRequest with search parameters
    
    Returns:
        HistoricalIncidentsResponse with matched incidents
    """
    try:
        from ..services.vector_store_service import get_vector_store
        
        vector_store = get_vector_store()
        
        # Build filters
        filters = {}
        if request.min_severity is not None:
            filters['min_severity'] = request.min_severity
        if request.location is not None:
            filters['location'] = request.location
        
        # Retrieve similar incidents
        incidents = vector_store.retrieve_similar_incidents(
            query=request.query,
            top_k=request.top_k,
            filters=filters if filters else None,
        )
        
        return HistoricalIncidentsResponse(
            incidents=incidents,
            query=request.query,
            count=len(incidents),
        )
    
    except Exception as e:
        logger.error(f"Error retrieving historical incidents: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")


# ============================================================================
# LLM CONFIGURATION
# ============================================================================

@router.get("/config", response_model=LLMConfigResponse)
async def get_config():
    """
    Get current LLM configuration.
    
    Returns:
        Current configuration settings
    """
    try:
        service = get_llm_service_or_raise()
        config = service.get_config()
        
        return LLMConfigResponse(
            model=config['model'],
            temperature=config['temperature'],
            max_tokens=config['max_tokens'],
            top_p=config['top_p'],
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving configuration")


@router.put("/config", response_model=LLMConfigResponse)
async def update_config(request: LLMConfigRequest):
    """
    Update LLM configuration.
    
    Allows dynamic adjustment of model parameters.
    
    Args:
        request: LLMConfigRequest with new settings
    
    Returns:
        Updated configuration
    """
    try:
        service = get_llm_service_or_raise()
        current = service.get_config()
        
        # Update only provided fields
        new_config = LLMConfig(
            model=request.model or current['model'],
            temperature=request.temperature if request.temperature is not None else current['temperature'],
            max_tokens=request.max_tokens or current['max_tokens'],
            top_p=request.top_p if request.top_p is not None else current['top_p'],
        )
        
        service.update_config(new_config)
        
        return LLMConfigResponse(
            model=new_config.model,
            temperature=new_config.temperature,
            max_tokens=new_config.max_tokens,
            top_p=new_config.top_p,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail="Error updating configuration")


@router.get("/models", response_model=Dict[str, List[str]])
async def get_available_models():
    """
    Get available LLM models.
    
    Returns:
        List of supported models
    """
    return {
        "available_models": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ],
        "description": "Intermediate to advanced LLM models suitable for campus security analysis",
    }
