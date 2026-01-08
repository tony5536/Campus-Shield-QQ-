"""
Risk predictor service combining ML models with AI explanations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .risk_model import RiskPredictionModel
from ..ai.agents.forecasting_agent import ForecastingAgent
from ..ai.llm.base import BaseLLM
from ..core.logging import setup_logger

logger = setup_logger(__name__)


class RiskPredictor:
    """Combines ML predictions with AI explanations."""
    
    def __init__(self, ml_model: RiskPredictionModel, forecasting_agent: ForecastingAgent):
        self.ml_model = ml_model
        self.forecasting_agent = forecasting_agent
    
    async def predict_zone_risk(
        self,
        zone: str,
        historical_data: List[Dict[str, Any]],
        time_horizon: str = "24h"
    ) -> Dict[str, Any]:
        """
        Predict risk for a zone with AI explanation.
        
        Returns:
            {
                "zone": zone,
                "risk_score": 0.0-1.0,
                "probability": "74%",
                "explanation": "AI-generated explanation",
                "time_window": time_horizon,
                "confidence": 0.0-1.0
            }
        """
        # ML prediction
        ml_risk = self.ml_model.predict_zone_risk(zone, time_horizon, historical_data)
        
        # AI explanation
        forecast_result = await self.forecasting_agent.forecast_risk(
            historical_data=historical_data,
            zones=[zone],
            time_range=time_horizon
        )
        
        explanation = forecast_result.get("explanation", f"Risk prediction for {zone}")
        
        return {
            "zone": zone,
            "risk_score": ml_risk,
            "probability": f"{int(ml_risk * 100)}%",
            "explanation": explanation,
            "time_window": time_horizon,
            "confidence": forecast_result.get("confidence", 0.7)
        }
    
    async def predict_multi_zone(
        self,
        zones: List[str],
        historical_data: List[Dict[str, Any]],
        time_horizon: str = "7d"
    ) -> Dict[str, Any]:
        """Predict risk for multiple zones."""
        predictions = {}
        
        for zone in zones:
            predictions[zone] = await self.predict_zone_risk(zone, historical_data, time_horizon)
        
        # Identify hotspots
        hotspots = [zone for zone, pred in predictions.items() if pred["risk_score"] > 0.6]
        
        return {
            "zone_predictions": predictions,
            "hotspots": hotspots,
            "time_horizon": time_horizon,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def predict_incident_risk(
        self,
        incident: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> float:
        """Predict risk score for a specific incident."""
        return self.ml_model.predict(incident, historical_data)

