"""
Model training service.
"""
from typing import List, Dict, Any
from .risk_model import RiskPredictionModel
from ..core.logging import setup_logger

logger = setup_logger(__name__)


class ModelTrainer:
    """Service for training risk prediction models."""
    
    def __init__(self, model_type: str = "random_forest"):
        self.model = RiskPredictionModel(model_type=model_type)
    
    def train_from_incidents(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train model from incident data."""
        logger.info(f"Training model with {len(incidents)} incidents")
        metrics = self.model.train(incidents)
        return metrics
    
    def retrain(self, incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Retrain model with new data."""
        return self.train_from_incidents(incidents)

