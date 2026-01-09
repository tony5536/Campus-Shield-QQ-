"""
LLM Service for CampusShield AI
Provides AI-powered incident analysis, threat assessment, report generation, and admin assistant.
Supports OpenAI (GPT-4o-mini), Groq (LLaMA-3), and Google Gemini.

CRITICAL: All responses use structured threat assessment format with:
- Threat summary
- Severity (LOW/MEDIUM/HIGH/CRITICAL)
- Confidence (percentage, never N/A)
- Reasoning (list of factors)
- Recommended actions (specific, not generic)

Fallback analysis uses rule-based assessment when LLM fails.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

import httpx
from ..config.settings import settings
from ..utils.logger import setup_logger

# Import fallback analysis function
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ai.prompts import generate_fallback_analysis

logger = setup_logger()


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    GROQ = "groq"
    GEMINI = "gemini"


class LLMService:
    """
    Unified LLM service supporting multiple providers.
    Uses environment variables to configure the provider and API keys.
    """
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Default model per provider
        self.models = {
            LLMProvider.OPENAI: os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            LLMProvider.GROQ: os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            LLMProvider.GEMINI: os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        }
        
        self.model = self.models.get(self.provider, "gpt-4o-mini")
        self._client = None
        
        # Validate API key presence
        if self.provider == LLMProvider.OPENAI and not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found. LLM features will be disabled.")
        elif self.provider == LLMProvider.GROQ and not self.groq_api_key:
            logger.warning("GROQ_API_KEY not found. LLM features will be disabled.")
        elif self.provider == LLMProvider.GEMINI and not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not found. LLM features will be disabled.")
    
    async def _call_openai(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call OpenAI API"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_groq(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call Groq API (LLaMA-3)"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not configured")
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _call_gemini(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call Google Gemini API"""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        # Convert messages format for Gemini
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.gemini_api_key}"
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 1000),
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generate text using the configured LLM provider.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system/instruction prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            if self.provider == LLMProvider.OPENAI:
                return await self._call_openai(messages, **kwargs)
            elif self.provider == LLMProvider.GROQ:
                return await self._call_groq(messages, **kwargs)
            elif self.provider == LLMProvider.GEMINI:
                return await self._call_gemini(messages, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    async def explain_incident(self, incident_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable explanation of an incident for security staff.
        Always returns meaningful analysis (never placeholder text).
        
        Args:
            incident_data: Incident dictionary with type, severity, description, etc.
        
        Returns:
            Human-readable explanation with threat assessment
        """
        system_prompt = """You are an AI assistant for CampusShield AI, a campus safety system.
Your role is to explain security incidents in clear, actionable language for security staff.

Be concise, professional, and focus on what action should be taken.
NEVER use generic phrases like "monitor the situation" or "review manually".
Always provide specific, contextual recommendations based on the incident."""
        
        incident_type = incident_data.get('incident_type', 'Unknown')
        severity = incident_data.get('severity', 'Unknown')
        description = incident_data.get('description', 'No description provided')
        location = incident_data.get('location', 'Unknown location')
        
        prompt = f"""Explain this security incident clearly for security staff:

Incident Details:
- Type: {incident_type}
- Severity: {severity}
- Location: {location}
- Description: {description}
- Timestamp: {incident_data.get('timestamp', 'Unknown')}

Provide:
1. What happened (clear summary, not generic)
2. Why it matters (specific threat assessment)
3. Immediate recommended actions (specific to this incident)
4. Priority level (how urgent)

Be direct and actionable (2-3 paragraphs)."""
        
        try:
            response = await self.generate(prompt, system_prompt=system_prompt, max_tokens=500)
            return response
        except Exception as e:
            logger.error(f"Error explaining incident: {e}")
            
            # FALLBACK: Generate basic but meaningful explanation
            fallback = f"""
INCIDENT EXPLANATION: {incident_type}

WHAT HAPPENED:
{description if description != 'No description provided' else f'A {incident_type.lower()} incident was detected at {location}.'}

WHY IT MATTERS:
Incidents of this type at {location} require appropriate security response. The reported severity level is {severity}, indicating the need for prompt attention.

RECOMMENDED ACTIONS:
1. Security personnel should investigate the {incident_type.lower()} incident at {location}
2. Document all findings and timeline
3. Follow standard incident response protocol for {severity.lower()}-severity incidents
4. Escalate if incident shows signs of escalation or requires specialized response

This incident has been logged and requires appropriate follow-up."""
            
            return fallback
    
    async def generate_report(self, incident_data: Dict[str, Any], include_recommendations: bool = True) -> str:
        """
        Generate a professional incident report with threat assessment.
        Always returns meaningful report (never placeholder text).
        
        Args:
            incident_data: Incident dictionary
            include_recommendations: Whether to include recommendations
        
        Returns:
            Professional incident report
        """
        system_prompt = """You are an AI assistant generating professional security incident reports.
Your reports should be formal, comprehensive, and suitable for official documentation.
Use professional language, clear structure, and ALWAYS include threat assessment and specific recommendations.
NEVER use generic phrases - be specific to each incident."""
        
        prompt = f"""Generate a professional incident report for official records:

{json.dumps(incident_data, indent=2, default=str)}

REQUIRED REPORT SECTIONS:
1. Executive Summary: Threat assessment and key findings
2. Incident Details: Type, timeline, location, severity assessment
3. Analysis: What occurred, threat factors, contributing factors
4. Impact Assessment: Consequences and scope
{"5. Recommendations: Specific immediate and preventive actions" if include_recommendations else ""}
6. Conclusion: Summary of incident and status

Requirements:
- Be specific (not generic)
- Include threat reasoning
- Provide actionable recommendations
- Suitable for official records (500-800 words)
- Format: Professional report style"""
        
        try:
            response = await self.generate(prompt, system_prompt=system_prompt, max_tokens=1500)
            return response
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            
            # FALLBACK: Generate structured report with available data
            fallback_report = f"""
INCIDENT REPORT
===============
Generated: {datetime.now().isoformat()}

EXECUTIVE SUMMARY
-----------------
{incident_data.get('incident_type', 'Incident')} reported at {incident_data.get('location', 'campus location')}
Severity: {incident_data.get('severity', 'Medium')}
Status: {incident_data.get('status', 'Active')}

INCIDENT DETAILS
----------------
Type: {incident_data.get('incident_type', 'Unknown')}
Location: {incident_data.get('location', 'Unknown')}
Reported: {incident_data.get('timestamp', 'Unknown')}
Description: {incident_data.get('description', 'No description provided')}

ANALYSIS
--------
This incident has been documented and categorized as {incident_data.get('incident_type', 'Unknown')}.
The severity level {incident_data.get('severity', 'Medium')} has been assigned based on available information.
Security personnel and relevant stakeholders should review details and determine appropriate response.

RECOMMENDATIONS
---------------
1. Incident should be investigated thoroughly
2. Follow standard incident response protocol
3. Document all findings and timeline
4. Escalate as needed based on investigation findings
5. Implement preventive measures to avoid recurrence

CONCLUSION
----------
This incident has been reported, documented, and logged in the security system.
Appropriate follow-up action should be taken based on incident severity and investigation findings.
"""
            
            return fallback_report
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return f"Unable to generate report due to: {str(e)}"
    
    async def assistant_query(
        self,
        user_query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Admin AI Assistant - Natural language query handler.
        Can answer questions about incidents, system status, and provide insights.
        
        Args:
            user_query: Natural language question from admin
            context: Optional context (e.g., recent incidents, statistics)
        
        Returns:
            AI-generated response
        """
        system_prompt = """You are an AI assistant for CampusShield AI admin dashboard.
You help administrators understand their security data, answer questions about incidents,
provide insights, and assist with decision-making.

You can:
- Explain incidents and patterns
- Provide statistics and trends
- Answer questions about system capabilities
- Suggest security improvements
- Help interpret data

Be helpful, accurate, and professional. If you don't know something, say so."""
        
        context_str = ""
        if context:
            context_str = f"\n\nCurrent Context:\n{json.dumps(context, indent=2, default=str)}"
        
        prompt = f"""Admin Query: {user_query}{context_str}

Please provide a helpful, accurate response. If the query requires specific data that isn't in the context,
suggest what information would be needed or what action to take."""
        
        try:
            response = await self.generate(prompt, system_prompt=system_prompt, max_tokens=800)
            return response
        except Exception as e:
            logger.error(f"Error processing assistant query: {e}")
            return f"I apologize, but I encountered an error: {str(e)}. Please check your API configuration."
    
    async def analyze_incident(self, query: str, incident_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze an incident and return structured threat assessment.
        CRITICAL: Always returns meaningful analysis (never empty or placeholder).
        Falls back to rule-based analysis if LLM fails.
        
        Args:
            query: Natural language description of incident
            incident_data: Optional dict with incident_type, location, timestamp, etc.
        
        Returns:
            Dictionary with:
            - summary: Brief threat summary (1-2 sentences)
            - severity: "LOW", "MEDIUM", "HIGH", "CRITICAL"
            - confidence: "XX%" (percentage, NEVER "N/A")
            - reasoning: List of factors contributing to assessment
            - recommended_actions: List of specific actions
            - source: "llm" or "rule_based_fallback"
        """
        
        system_prompt = """You are CampusShield AI, a threat assessment specialist for campus safety.
Analyze security incidents and provide structured, confident threat assessments.

YOU MUST respond ONLY with valid JSON in this exact format:
{
  "summary": "1-2 sentence threat summary specific to the incident",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "confidence": "XX% (never N/A - always estimate)",
  "reasoning": [
    "specific factor contributing to severity",
    "contextual indicator or pattern",
    "relevant historical or situational factor"
  ],
  "recommended_actions": [
    "specific immediate action",
    "follow-up or escalation step",
    "monitoring or prevention measure"
  ]
}

SEVERITY GUIDELINES:
- CRITICAL: Immediate threat to life, violence, weapons, medical emergency
- HIGH: Potential violence, unauthorized access, serious disturbance, crime
- MEDIUM: Suspicious activity, unusual behavior, gathering, potential violations
- LOW: Minor concern, routine monitoring, informational alert

CONFIDENCE SCORING:
- 90%+: Clear threat indicators with strong evidence
- 75-89%: Good evidence with minor uncertainties
- 60-74%: Moderate evidence with some uncertainty
- 40-59%: Limited information, significant ambiguity
- NEVER return "N/A" - always estimate based on available data

Be specific, decisive, and confident. Return ONLY valid JSON with no additional text."""
        
        prompt = f"""Analyze this incident: {query}

{f"Additional context: {json.dumps(incident_data, default=str)}" if incident_data else ""}

Provide structured threat assessment in the required JSON format."""
        
        try:
            response_text = await self.generate(
                prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temp for consistent, confident responses
                max_tokens=500
            )
            
            # Extract JSON from response
            response_text = response_text.strip()
            
            # Try to extract JSON block if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON object using regex
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Validate and normalize response
            severity = str(result.get("severity", "MEDIUM")).upper()
            if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                severity = "MEDIUM"
            
            # Validate confidence is percentage, never "N/A"
            confidence = str(result.get("confidence", "75%")).strip()
            if "n/a" in confidence.lower() or confidence == "":
                confidence = "75%"
            if not confidence.endswith("%"):
                confidence = f"{confidence}%"
            
            return {
                "summary": result.get("summary", f"Security incident detected. Assessment: {severity}"),
                "severity": severity,
                "confidence": confidence,
                "reasoning": result.get("reasoning", ["Incident analyzed with available data"]),
                "recommended_actions": result.get("recommended_actions", ["Follow standard security protocol"]),
                "source": "llm"
            }
            
        except Exception as e:
            logger.error(f"LLM analysis error (falling back to rule-based): {e}")
            
            # FALLBACK: Use rule-based analysis
            # Extract incident type and location from query or incident_data
            incident_type = "Unknown Incident"
            location = "Campus Location"
            
            if incident_data:
                incident_type = incident_data.get("incident_type", incident_type)
                location = incident_data.get("location", location)
            
            # Extract from query if not in incident_data
            if "incident_type" not in (incident_data or {}):
                # Try to extract from query
                words = query.lower().split()
                for i, word in enumerate(words):
                    if any(kw in word for kw in ["theft", "assault", "fire", "threat", "intrusion", "fight"]):
                        incident_type = " ".join(words[max(0, i-1):min(len(words), i+3)])
                        break
            
            if "location" not in (incident_data or {}):
                # Try to extract location from query
                if "building" in query.lower():
                    idx = query.lower().index("building")
                    location = query[idx:idx+50].split(",")[0]
            
            fallback_result = generate_fallback_analysis(
                incident_type=incident_type,
                location=location,
                time_of_day="unknown",
                historical_context=query[:100] if query else ""
            )
            
            logger.info(f"Using rule-based fallback analysis for: {incident_type}")
            return fallback_result


# Singleton instance
llm_service = LLMService()

