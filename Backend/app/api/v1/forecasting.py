"""
Risk Forecasting API - Phase 5
Predicts future campus risks with AI explanations.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...core.security import get_db
from ...models.incident import Incident
from ...ai.llm.openai import OpenAILLM
from ...ai.agents.forecasting_agent import ForecastingAgent
from ...ml.predictor import RiskPredictor
from ...ml.risk_model import RiskPredictionModel
from ...core.logging import setup_logger

logger = setup_logger(__name__)
router = APIRouter()

# Initialize components
llm = OpenAILLM()
forecasting_agent = ForecastingAgent(llm)
ml_model = RiskPredictionModel()
risk_predictor = RiskPredictor(ml_model, forecasting_agent)


class ForecastRequest(BaseModel):
    """Request model for risk forecast."""
    zones: Optional[List[str]] = None
    time_horizon: str = "7d"  # 24h, 7d, 30d


class ForecastResponse(BaseModel):
    """Response model for risk forecast."""
    zone_predictions: Dict[str, Dict[str, Any]]
    hotspots: List[str]
    time_horizon: str
    generated_at: datetime


@router.get("/risk", response_model=ForecastResponse)
async def forecast_risk(
    zones: Optional[str] = None,  # Comma-separated zones
    time_horizon: str = "7d",
    db: Session = Depends(get_db)
):
    """
    Predict future campus risks with AI explanations.
    
    Returns zone-wise risk predictions with natural language explanations.
    
    Example output:
        "There is a 74% probability of incidents near Hostel-B between 8–10 PM on Fridays."
    """
    try:
        # Get historical incidents
        historical_incidents = db.query(Incident).order_by(
            Incident.timestamp.desc()
        ).limit(100).all()
        
        historical_data = [
            {
                "id": inc.id,
                "incident_type": inc.incident_type,
                "severity": inc.severity,
                "location": inc.location,
                "timestamp": inc.timestamp.isoformat() if inc.timestamp else None,
            }
            for inc in historical_incidents
        ]
        
        # Parse zones
        zone_list = zones.split(",") if zones else None
        if not zone_list:
            # Extract unique zones from historical data
            zone_list = list(set([inc.get("location") for inc in historical_data if inc.get("location")]))
        
        # Predict
        result = await risk_predictor.predict_multi_zone(
            zones=zone_list,
            historical_data=historical_data,
            time_horizon=time_horizon
        )
        
        return ForecastResponse(
            zone_predictions=result.get("zone_predictions", {}),
            hotspots=result.get("hotspots", []),
            time_horizon=time_horizon,
            generated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error in risk forecasting: {e}")
        raise HTTPException(status_code=500, detail=f"Forecasting error: {str(e)}")

