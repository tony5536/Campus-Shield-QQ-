"""
Multi-Agent Orchestrator - Coordinates multiple AI agents.
"""
from typing import Dict, Any, List, Optional
from ..llm.base import BaseLLM
from .analyst_agent import AnalystAgent
from .policy_agent import PolicyAgent
from .forecasting_agent import ForecastingAgent
from .report_agent import ReportAgent
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class AgentOrchestrator:
    """Orchestrates multiple AI agents for comprehensive analysis."""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.analyst = AnalystAgent(llm)
        self.policy = PolicyAgent(llm)
        self.forecasting = ForecastingAgent(llm)
        self.report = ReportAgent(llm)
    
    async def analyze_incident_comprehensive(
        self,
        incident_data: Dict[str, Any],
        historical_context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive incident analysis using multiple agents.
        
        Returns unified analysis combining:
        - Analyst insights
        - Policy compliance
        - Recommendations
        """
        # Run agents in parallel (conceptually)
        analyst_result = await self.analyst.analyze_incident(incident_data, historical_context)
        policy_result = await self.policy.check_compliance(incident_data)
        
        # Combine results
        return {
            "incident_id": incident_data.get("id"),
            "severity": analyst_result.get("severity", "Medium"),
            "risk_score": analyst_result.get("risk_score", 0.5),
            "root_cause": analyst_result.get("root_cause", "Analysis pending"),
            "similar_cases": analyst_result.get("similar_cases", 0),
            "recommended_actions": analyst_result.get("recommended_actions", []),
            "policy_compliant": policy_result.get("compliant", True),
            "policy_violations": policy_result.get("violations", []),
            "policy_recommendations": policy_result.get("recommendations", []),
            "confidence": analyst_result.get("confidence", 0.7)
        }
    
    async def generate_intelligence_report(
        self,
        incident_data: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate comprehensive intelligence report using report agent."""
        if analysis is None:
            analysis = await self.analyst.analyze_incident(incident_data)
        
        return await self.report.generate_report(incident_data, analysis)
    
    async def forecast_and_explain(
        self,
        historical_data: List[Dict[str, Any]],
        zones: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Forecast risks and provide AI explanation."""
        return await self.forecasting.forecast_risk(historical_data, zones)

