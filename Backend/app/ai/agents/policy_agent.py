"""
Policy Agent - Checks incidents against campus security policies.
"""
from typing import Dict, Any, List, Optional
from ..llm.base import BaseLLM
from ..llm.prompts import SYSTEM_PROMPT_POLICY
from ...core.logging import setup_logger

logger = setup_logger(__name__)


class PolicyAgent:
    """Policy compliance agent."""
    
    def __init__(self, llm: BaseLLM, policies: Optional[List[str]] = None):
        self.llm = llm
        self.policies = policies or self._default_policies()
    
    def _default_policies(self) -> List[str]:
        """Default campus security policies."""
        return [
            "All incidents must be reported within 15 minutes",
            "High severity incidents require immediate security team dispatch",
            "Unauthorized access after hours is a critical violation",
            "All incidents must be documented with location and timestamp",
            "Medical emergencies require immediate medical response",
            "Fire incidents require immediate evacuation procedures"
        ]
    
    async def check_compliance(
        self,
        incident_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check incident against policies.
        
        Returns:
            {
                "compliant": bool,
                "violations": ["violation1", "violation2"],
                "recommendations": ["rec1", "rec2"],
                "policy_references": ["policy1", "policy2"]
            }
        """
        policies_str = "\n".join([f"- {p}" for p in self.policies])
        
        prompt = f"""Analyze the following incident against campus security policies:

Incident:
{incident_data}

Policies:
{policies_str}

Determine:
1. Is this incident compliant with policies? (Yes/No)
2. What policy violations exist (if any)?
3. What corrective actions are recommended?
4. Which specific policies are relevant?

Provide structured analysis."""
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT_POLICY,
                temperature=0.2,
                max_tokens=500
            )
            
            # Parse response
            compliant = "yes" in response.lower() or "compliant" in response.lower()
            violations = self._extract_violations(response)
            recommendations = self._extract_recommendations(response)
            
            return {
                "compliant": compliant,
                "violations": violations,
                "recommendations": recommendations,
                "policy_references": self._extract_policy_refs(response)
            }
        except Exception as e:
            logger.error(f"Error in policy agent: {e}")
            return {
                "compliant": True,
                "violations": [],
                "recommendations": ["Review incident against policy manual"],
                "policy_references": []
            }
    
    def _extract_violations(self, text: str) -> List[str]:
        """Extract policy violations from text."""
        violations = []
        lines = text.split("\n")
        for line in lines:
            if "violation" in line.lower() or "non-compliant" in line.lower():
                violations.append(line.strip())
        return violations[:5]  # Limit to 5
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from text."""
        recommendations = []
        lines = text.split("\n")
        for line in lines:
            if "recommend" in line.lower() or "action" in line.lower():
                recommendations.append(line.strip())
        return recommendations[:5]
    
    def _extract_policy_refs(self, text: str) -> List[str]:
        """Extract policy references from text."""
        refs = []
        for policy in self.policies:
            if policy.lower() in text.lower():
                refs.append(policy)
        return refs

