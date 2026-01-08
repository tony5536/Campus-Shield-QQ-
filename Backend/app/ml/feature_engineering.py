"""
Feature engineering for risk prediction models.
"""
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


class FeatureEngineer:
    """Engineers features from incident data for ML models."""
    
    def __init__(self):
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'incident_type_encoded', 'location_encoded', 'severity',
            'time_since_last_incident', 'incident_count_last_24h',
            'incident_count_last_7d', 'avg_severity_last_7d'
        ]
    
    def extract_features(self, incident: Dict[str, Any], historical_data: List[Dict[str, Any]] = None) -> Dict[str, float]:
        """Extract features from a single incident."""
        features = {}
        
        # Parse timestamp
        timestamp = incident.get('timestamp')
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            dt = datetime.now()
        
        # Time features
        features['hour'] = dt.hour
        features['day_of_week'] = dt.weekday()  # 0=Monday, 6=Sunday
        features['month'] = dt.month
        features['is_weekend'] = 1.0 if dt.weekday() >= 5 else 0.0
        
        # Incident type encoding (simple hash)
        inc_type = incident.get('incident_type', 'Unknown')
        features['incident_type_encoded'] = hash(inc_type) % 100 / 100.0
        
        # Location encoding
        location = incident.get('location', 'Unknown')
        features['location_encoded'] = hash(location) % 100 / 100.0
        
        # Severity
        features['severity'] = float(incident.get('severity', 0.5))
        
        # Historical features
        if historical_data:
            features.update(self._extract_historical_features(incident, historical_data))
        else:
            features['time_since_last_incident'] = 24.0  # Default
            features['incident_count_last_24h'] = 0.0
            features['incident_count_last_7d'] = 0.0
            features['avg_severity_last_7d'] = 0.5
        
        return features
    
    def _extract_historical_features(self, current_incident: Dict[str, Any], historical: List[Dict[str, Any]]) -> Dict[str, float]:
        """Extract features based on historical patterns."""
        current_time = current_incident.get('timestamp')
        if isinstance(current_time, str):
            current_dt = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
        elif isinstance(current_time, datetime):
            current_dt = current_time
        else:
            current_dt = datetime.now()
        
        location = current_incident.get('location', '')
        
        # Filter historical incidents
        hist_24h = []
        hist_7d = []
        last_incident_time = None
        
        for inc in historical:
            inc_time = inc.get('timestamp')
            if isinstance(inc_time, str):
                inc_dt = datetime.fromisoformat(inc_time.replace('Z', '+00:00'))
            elif isinstance(inc_time, datetime):
                inc_dt = inc_time
            else:
                continue
            
            time_diff = (current_dt - inc_dt).total_seconds() / 3600  # hours
            
            if time_diff <= 24:
                hist_24h.append(inc)
            if time_diff <= 168:  # 7 days
                hist_7d.append(inc)
            
            if last_incident_time is None or inc_dt > last_incident_time:
                last_incident_time = inc_dt
        
        # Calculate features
        time_since_last = (current_dt - last_incident_time).total_seconds() / 3600 if last_incident_time else 24.0
        
        # Filter by location
        hist_24h_location = [inc for inc in hist_24h if inc.get('location') == location]
        hist_7d_location = [inc for inc in hist_7d if inc.get('location') == location]
        
        avg_severity_7d = np.mean([float(inc.get('severity', 0.5)) for inc in hist_7d_location]) if hist_7d_location else 0.5
        
        return {
            'time_since_last_incident': min(time_since_last, 168.0),  # Cap at 7 days
            'incident_count_last_24h': float(len(hist_24h_location)),
            'incident_count_last_7d': float(len(hist_7d_location)),
            'avg_severity_last_7d': avg_severity_7d
        }
    
    def prepare_training_data(self, incidents: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare training data from incidents."""
        features_list = []
        targets = []
        
        for i, incident in enumerate(incidents):
            # Use previous incidents as historical context
            historical = incidents[:i] if i > 0 else []
            features = self.extract_features(incident, historical)
            features_list.append(features)
            
            # Target: risk score (could be severity or derived metric)
            target = float(incident.get('severity', 0.5))
            targets.append(target)
        
        df = pd.DataFrame(features_list)
        df['target'] = targets
        return df

