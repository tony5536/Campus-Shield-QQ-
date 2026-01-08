"""
Security Analyst Agent - Analyzes incidents and provides intelligence.
"""
from typing import Dict, Any, List, Optional
import json
from ..llm.base import BaseLLM
from ..llm.prompts import SYSTEM_PROMPT_ANALYST, INCIDENT_ANALYSIS_PROMPT
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class AnalystAgent:
    """Security Analyst Agent for incident analysis."""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def analyze_incident(
        self,
        incident_data: Dict[str, Any],
        historical_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze an incident and generate intelligence.
        
        Returns:
            {
                "severity": "Low|Medium|High|Critical",
                "risk_score": 0.0-1.0,
                "root_cause": "explanation",
                "similar_cases": count,
                "recommended_actions": ["action1", "action2"],
                "confidence": 0.0-1.0
            }
        """
        # Format historical context
        hist_str = "No similar historical incidents found."
        if historical_context:
            hist_str = "\n".join([
                f"- {inc.get('incident_type', 'Unknown')} at {inc.get('location', 'Unknown')} "
                f"(severity: {inc.get('severity', 'Unknown')})"
                for inc in historical_context[:5]
            ])
        
        prompt = INCIDENT_ANALYSIS_PROMPT.format(
            incident_data=json.dumps(incident_data, indent=2, default=str),
            historical_context=hist_str
        )
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT_ANALYST,
                temperature=0.3,
                max_tokens=800
            )
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(response)
            except json.JSONDecodeError:
                # Fallback: extract structured data manually
                analysis = self._parse_unstructured_response(response, incident_data)
            
            # Validate and normalize
            severity = analysis.get("severity", "Medium").capitalize()
            if severity not in ["Low", "Medium", "High", "Critical"]:
                severity = "Medium"
            
            risk_score = float(analysis.get("risk_score", 0.5))
            risk_score = max(0.0, min(1.0, risk_score))
            
            return {
                "severity": severity,
                "risk_score": risk_score,
                "root_cause": analysis.get("root_cause", "Analysis pending"),
                "similar_cases": analysis.get("similar_cases", len(historical_context or [])),
                "recommended_actions": analysis.get("recommended_actions", []),
                "confidence": float(analysis.get("confidence", 0.7))
            }
            
        except Exception as e:
            logger.error(f"Error in analyst agent: {e}")
            # Return safe fallback
            return {
                "severity": "Medium",
                "risk_score": 0.5,
                "root_cause": "Analysis temporarily unavailable",
                "similar_cases": len(historical_context or []),
                "recommended_actions": ["Review incident manually", "Follow standard protocols"],
                "confidence": 0.3
            }
    
    def _parse_unstructured_response(self, response: str, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse unstructured LLM response into structured format."""
        # Simple heuristic parsing
        severity_map = {"low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"}
        severity = "Medium"
        for key, value in severity_map.items():
            if key in response.lower():
                severity = value
                break
        
        return {
            "severity": severity,
            "risk_score": 0.5,
            "root_cause": response[:200] if len(response) > 200 else response,
            "similar_cases": 0,
            "recommended_actions": ["Review incident details", "Follow security protocols"],
            "confidence": 0.6
        }

