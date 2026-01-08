"""
Risk prediction model using ML algorithms.
"""
from typing import List, Dict, Any, Optional
import pickle
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from .feature_engineering import FeatureEngineer
from ..core.config import settings
from ..core.logging import setup_logger

logger = setup_logger(__name__)


class RiskPredictionModel:
    """ML model for risk prediction."""
    
    def __init__(self, model_type: str = "random_forest"):
        self.model_type = model_type
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.model_path = Path(settings.ml_model_path) / "risk_model.pkl"
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _create_model(self):
        """Create model instance."""
        if self.model_type == "random_forest":
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == "gradient_boosting":
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, incidents: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Train the risk prediction model.
        
        Returns:
            Dictionary with training metrics
        """
        if not incidents or len(incidents) < 10:
            logger.warning("Insufficient data for training. Need at least 10 incidents.")
            return {"status": "insufficient_data"}
        
        # Prepare data
        df = self.feature_engineer.prepare_training_data(incidents)
        
        if len(df) < 10:
            logger.warning("Insufficient data after feature engineering.")
            return {"status": "insufficient_data"}
        
        # Split features and target
        X = df.drop('target', axis=1)
        y = df['target']
        
        # Split train/test
        if len(X) > 20:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        else:
            X_train, X_test, y_train, y_test = X, X, y, y
        
        # Create and train model
        self._create_model()
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Save model
        self.save()
        
        metrics = {
            "status": "trained",
            "train_mse": float(train_mse),
            "test_mse": float(test_mse),
            "train_r2": float(train_r2),
            "test_r2": float(test_r2),
            "n_samples": len(X)
        }
        
        logger.info(f"Model trained: {metrics}")
        return metrics
    
    def predict(self, incident: Dict[str, Any], historical_data: List[Dict[str, Any]] = None) -> float:
        """
        Predict risk score for an incident.
        
        Returns:
            Risk score (0.0 to 1.0)
        """
        if self.model is None:
            self.load()
        
        if self.model is None:
            # Fallback: use simple heuristic
            return float(incident.get('severity', 0.5))
        
        # Extract features
        features = self.feature_engineer.extract_features(incident, historical_data)
        
        # Convert to array
        feature_array = np.array([[features.get(col, 0.0) for col in self.feature_engineer.feature_columns]])
        
        # Predict
        prediction = self.model.predict(feature_array)[0]
        
        # Normalize to 0-1
        prediction = max(0.0, min(1.0, prediction))
        
        return float(prediction)
    
    def predict_zone_risk(self, zone: str, time_window: str = "24h", historical_data: List[Dict[str, Any]] = None) -> float:
        """Predict risk for a specific zone."""
        if not historical_data:
            return 0.5  # Default
        
        # Filter incidents by zone
        zone_incidents = [inc for inc in historical_data if inc.get('location') == zone]
        
        if not zone_incidents:
            return 0.3  # Low risk if no incidents
        
        # Calculate risk based on recent incidents
        recent_count = len(zone_incidents)
        avg_severity = np.mean([float(inc.get('severity', 0.5)) for inc in zone_incidents])
        
        # Simple risk calculation
        risk = min(1.0, (recent_count / 10.0) * 0.5 + avg_severity * 0.5)
        
        return float(risk)
    
    def save(self):
        """Save model to disk."""
        if self.model is not None:
            with open(self.model_path, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'model_type': self.model_type,
                    'feature_columns': self.feature_engineer.feature_columns
                }, f)
            logger.info(f"Model saved to {self.model_path}")
    
    def load(self):
        """Load model from disk."""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.model_type = data.get('model_type', 'random_forest')
                    if 'feature_columns' in data:
                        self.feature_engineer.feature_columns = data['feature_columns']
                logger.info(f"Model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                self.model = None
        else:
            logger.warning(f"Model file not found: {self.model_path}")

