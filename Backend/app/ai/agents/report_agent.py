"""
Report Agent - Generates summaries and insights.
"""
import json
from typing import Dict, Any, List, Optional
from ..llm.base import BaseLLM
from ..llm.prompts import SYSTEM_PROMPT_REPORTER, INCIDENT_REPORT_PROMPT
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class ReportAgent:
    """Report generation agent."""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def generate_report(
        self,
        incident_data: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a professional incident report."""
        analysis_str = json.dumps(analysis, indent=2, default=str) if analysis else "No analysis available"
        
        prompt = INCIDENT_REPORT_PROMPT.format(
            incident_data=json.dumps(incident_data, indent=2, default=str),
            analysis=analysis_str
        )
        
        try:
            report = await self.llm.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT_REPORTER,
                temperature=0.3,
                max_tokens=1500
            )
            return report
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Report generation error: {str(e)}"
    
    async def generate_summary(
        self,
        incidents: List[Dict[str, Any]],
        summary_type: str = "daily"
    ) -> str:
        """Generate summary of multiple incidents."""
        if not incidents:
            return "No incidents to summarize."
        
        prompt = f"""Generate a {summary_type} security summary for the following incidents:

{json.dumps(incidents[:20], indent=2, default=str)}

Include:
1. Overview and statistics
2. Key incidents
3. Patterns and trends
4. Recommendations

Keep it concise and actionable."""
        
        try:
            summary = await self.llm.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT_REPORTER,
                temperature=0.4,
                max_tokens=1000
            )
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Summary generation error: {str(e)}"

