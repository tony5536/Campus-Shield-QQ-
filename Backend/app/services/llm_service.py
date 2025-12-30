"""
LLM Service for CampusShield AI
Provides AI-powered incident explanation, report generation, and admin assistant.
Supports OpenAI (GPT-4o-mini), Groq (LLaMA-3), and Google Gemini.
"""

import os
import json
from typing import Dict, List, Optional, Any
from enum import Enum

import httpx
from ..config.settings import settings
from ..utils.logger import setup_logger

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
        
        Args:
            incident_data: Incident dictionary with fields like type, severity, description, etc.
        
        Returns:
            Human-readable explanation
        """
        system_prompt = """You are an AI assistant for CampusShield AI, a smart campus safety system.
Your role is to explain security incidents in clear, actionable language for security staff.
Be concise, professional, and focus on what action should be taken."""
        
        prompt = f"""Explain the following security incident in clear, professional language for security staff:

Incident Details:
- Type: {incident_data.get('incident_type', 'Unknown')}
- Severity: {incident_data.get('severity', 'Unknown')}
- Status: {incident_data.get('status', 'Unknown')}
- Description: {incident_data.get('description', 'No description provided')}
- Timestamp: {incident_data.get('timestamp', 'Unknown')}
- Camera ID: {incident_data.get('camera_id', 'Not specified')}

Provide:
1. A clear summary of what happened
2. Why this incident matters (risk assessment)
3. Recommended immediate actions
4. Priority level assessment

Keep the response concise (2-3 paragraphs)."""
        
        try:
            response = await self.generate(prompt, system_prompt=system_prompt, max_tokens=500)
            return response
        except Exception as e:
            logger.error(f"Error explaining incident: {e}")
            return f"Unable to generate explanation due to: {str(e)}"
    
    async def generate_report(self, incident_data: Dict[str, Any], include_recommendations: bool = True) -> str:
        """
        Generate a professional incident report.
        
        Args:
            incident_data: Incident dictionary
            include_recommendations: Whether to include AI-generated recommendations
        
        Returns:
            Professional incident report
        """
        system_prompt = """You are an AI assistant generating professional security incident reports.
Your reports should be formal, comprehensive, and suitable for official documentation.
Use professional language and structure."""
        
        prompt = f"""Generate a professional incident report for the following security incident:

Incident Data:
{json.dumps(incident_data, indent=2, default=str)}

Structure the report as follows:
1. Executive Summary
2. Incident Details
   - Type and Classification
   - Timeline
   - Location/Context
   - Severity Assessment
3. Analysis
   - What occurred
   - Contributing factors
   - Impact assessment
{"4. Recommendations" if include_recommendations else ""}
{"   - Immediate actions" if include_recommendations else ""}
{"   - Preventive measures" if include_recommendations else ""}
5. Conclusion

Make it professional and suitable for official records (500-800 words)."""
        
        try:
            response = await self.generate(prompt, system_prompt=system_prompt, max_tokens=1500)
            return response
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
    
    async def analyze_incident(self, query: str) -> Dict[str, Any]:
        """
        Analyze an incident query and return structured analysis with severity assessment.
        This is the core hackathon demo function.
        
        Args:
            query: Natural language description of an incident or query
        
        Returns:
            Dictionary with:
            - summary: Brief summary of the incident
            - severity: "Low", "Medium", or "High"
            - recommended_action: Action recommendation
            - confidence: Confidence percentage as string
        """
        system_prompt = """You are CampusShield AI, an intelligent emergency response assistant for campus safety.
Analyze incidents, determine severity, and recommend immediate actions clearly and concisely.

You must respond ONLY with valid JSON in this exact format:
{
  "summary": "Brief 2-3 sentence summary of the incident",
  "severity": "Low" OR "Medium" OR "High",
  "recommended_action": "Clear, actionable recommendation",
  "confidence": "85%"
}

Severity Guidelines:
- High: Immediate threat to safety, requires urgent response (violence, unauthorized access, active threat)
- Medium: Potential risk, needs monitoring (suspicious activity, crowd gathering, unusual behavior)
- Low: Minor concern, routine monitoring (vehicle in wrong zone, minor disturbance)

Be decisive and confident. Always return valid JSON."""
        
        prompt = f"""Analyze this incident or query: {query}

Provide a structured analysis with severity assessment and recommended action."""
        
        try:
            response_text = await self.generate(
                prompt, 
                system_prompt=system_prompt, 
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=300
            )
            
            # Extract JSON from response (handle cases where LLM adds extra text)
            response_text = response_text.strip()
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback: try to extract JSON object
                import re
                json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Validate and normalize response
            severity = result.get("severity", "Medium").capitalize()
            if severity not in ["Low", "Medium", "High"]:
                severity = "Medium"
            
            return {
                "summary": result.get("summary", "Incident analysis completed."),
                "severity": severity,
                "recommended_action": result.get("recommended_action", "Monitor the situation and maintain standard security protocols."),
                "confidence": result.get("confidence", "75%")
            }
            
        except Exception as e:
            logger.error(f"Error analyzing incident: {e}")
            # Return safe fallback response - NEVER crash during demo
            return {
                "summary": "Unable to complete AI analysis at this time. Please review the incident manually.",
                "severity": "Medium",
                "recommended_action": "Review incident details and follow standard security protocols.",
                "confidence": "N/A"
            }


# Singleton instance
llm_service = LLMService()

