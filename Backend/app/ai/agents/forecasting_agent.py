"""
Forecasting Agent - Predicts future risks and explains predictions.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..llm.base import BaseLLM
from ..llm.prompts import SYSTEM_PROMPT_FORECASTING, RISK_FORECAST_PROMPT
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class ForecastingAgent:
    """Risk forecasting agent."""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def forecast_risk(
        self,
        historical_data: List[Dict[str, Any]],
        zones: Optional[List[str]] = None,
        time_range: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Forecast future risks based on historical data.
        
        Returns:
            {
                "zone_predictions": {"zone1": 0.75, "zone2": 0.60},
                "time_patterns": {"8-10 PM": "High risk"},
                "hotspots": ["zone1", "zone2"],
                "explanation": "Natural language explanation",
                "confidence": 0.0-1.0
            }
        """
        # Aggregate historical data
        zones = zones or self._extract_zones(historical_data)
        time_range = time_range or "Next 7 days"
        
        # Format historical data summary
        hist_summary = self._summarize_historical_data(historical_data)
        
        prompt = RISK_FORECAST_PROMPT.format(
            historical_data=hist_summary,
            zones=", ".join(zones) if zones else "All zones",
            time_range=time_range
        )
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT_FORECASTING,
                temperature=0.4,
                max_tokens=1000
            )
            
            # Extract structured predictions
            zone_predictions = self._extract_zone_predictions(response, zones)
            time_patterns = self._extract_time_patterns(response)
            hotspots = self._extract_hotspots(response, zone_predictions)
            
            return {
                "zone_predictions": zone_predictions,
                "time_patterns": time_patterns,
                "hotspots": hotspots,
                "explanation": response,
                "confidence": 0.7  # Could be calculated from model confidence
            }
        except Exception as e:
            logger.error(f"Error in forecasting agent: {e}")
            return {
                "zone_predictions": {},
                "time_patterns": {},
                "hotspots": [],
                "explanation": "Forecasting temporarily unavailable",
                "confidence": 0.3
            }
    
    def _extract_zones(self, data: List[Dict[str, Any]]) -> List[str]:
        """Extract unique zones from historical data."""
        zones = set()
        for item in data:
            if "location" in item:
                zones.add(item["location"])
            if "zone" in item:
                zones.add(item["zone"])
        return list(zones)
    
    def _summarize_historical_data(self, data: List[Dict[str, Any]]) -> str:
        """Summarize historical incident data."""
        if not data:
            return "No historical data available."
        
        summary = f"Total incidents: {len(data)}\n"
        
        # Group by type
        by_type = {}
        for item in data:
            inc_type = item.get("incident_type", "Unknown")
            by_type[inc_type] = by_type.get(inc_type, 0) + 1
        
        summary += "By type:\n"
        for inc_type, count in by_type.items():
            summary += f"- {inc_type}: {count}\n"
        
        # Group by location
        by_location = {}
        for item in data:
            location = item.get("location", "Unknown")
            by_location[location] = by_location.get(location, 0) + 1
        
        summary += "\nBy location:\n"
        for location, count in list(by_location.items())[:10]:
            summary += f"- {location}: {count}\n"
        
        return summary
    
    def _extract_zone_predictions(self, text: str, zones: List[str]) -> Dict[str, float]:
        """Extract zone risk predictions from text."""
        predictions = {}
        for zone in zones:
            # Look for zone mentions with probability
            if zone.lower() in text.lower():
                # Try to extract probability
                import re
                pattern = rf"{re.escape(zone)}.*?(\d+\.?\d*)%"
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    predictions[zone] = float(match.group(1)) / 100.0
                else:
                    predictions[zone] = 0.5  # Default
        return predictions
    
    def _extract_time_patterns(self, text: str) -> Dict[str, str]:
        """Extract time-based patterns from text."""
        patterns = {}
        # Simple extraction - look for time mentions
        import re
        time_pattern = r"(\d+[-\s]?\d*\s*(?:AM|PM|hours?|o'clock)?)"
        matches = re.findall(time_pattern, text, re.IGNORECASE)
        for match in matches:
            patterns[match] = "High risk"  # Simplified
        return patterns
    
    def _extract_hotspots(self, text: str, zone_predictions: Dict[str, float]) -> List[str]:
        """Extract hotspot zones."""
        # Zones with prediction > 0.6
        hotspots = [zone for zone, prob in zone_predictions.items() if prob > 0.6]
        # Also check text for "hotspot" mentions
        for zone in zone_predictions.keys():
            if "hotspot" in text.lower() and zone.lower() in text.lower():
                if zone not in hotspots:
                    hotspots.append(zone)
        return hotspots

