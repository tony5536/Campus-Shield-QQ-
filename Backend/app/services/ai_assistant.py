"""
Hardened AI Assistant service with timeout, fallback, and strict response format.
Isolated from route layer - can be tested independently.
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AIAssistantService:
    """
    Production-ready AI assistant with:
    - Timeout protection
    - Fallback responses
    - Strict JSON response format
    - Error recovery
    """
    
    def __init__(self, openai_client, model: str = "gpt-4o-mini", timeout: int = 30):
        self.client = openai_client
        self.model = model
        self.timeout = timeout
        logger.info(f"AIAssistantService initialized with model={model}, timeout={timeout}s")
    
    async def chat(
        self,
        query: str,
        history: Optional[list[dict]] = None,
        temperature: float = 0.7
    ) -> dict:
        """
        Chat endpoint with conversation history support.
        
        Returns strictly formatted response:
        {
            "reply": str,
            "confidence": float (0-1),
            "sources": optional list
        }
        """
        if not query or not isinstance(query, str):
            logger.warning(f"Invalid query received: {query}")
            return self._fallback_response("Please provide a valid query.", confidence=0.0)
        
        try:
            # Build messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": self._system_prompt()
                }
            ]
            
            # Add conversation history if provided
            if history and isinstance(history, list):
                for msg in history[-10:]:  # Keep last 10 messages
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        messages.append({
                            "role": msg["role"],
                            "content": str(msg["content"])[:2000]  # Truncate long messages
                        })
            
            # Add current query
            messages.append({
                "role": "user",
                "content": str(query)[:2000]
            })
            
            logger.debug(f"Sending {len(messages)} messages to LLM")
            
            # Call OpenAI with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=1024
                ),
                timeout=self.timeout
            )
            
            reply = response.choices[0].message.content
            
            logger.info(f"LLM response received: {len(reply)} chars")
            
            return {
                "reply": reply,
                "confidence": 0.95,  # High confidence for direct LLM response
                "sources": []
            }
        
        except asyncio.TimeoutError:
            logger.error(f"LLM timeout after {self.timeout}s")
            return self._fallback_response(
                "The AI assistant is taking too long to respond. Please try again.",
                confidence=0.0
            )
        
        except Exception as e:
            logger.error(f"LLM error: {type(e).__name__}: {str(e)}")
            return self._fallback_response(
                f"AI assistant encountered an error. Please try again.",
                confidence=0.0
            )
    
    async def analyze_incident(self, incident_data: dict) -> dict:
        """Analyze a specific incident"""
        if not incident_data:
            return self._fallback_response("No incident data provided.")
        
        prompt = f"""
        Analyze this incident and provide a brief risk assessment:
        
        Type: {incident_data.get('incident_type', 'Unknown')}
        Location: {incident_data.get('location', 'Unknown')}
        Description: {incident_data.get('description', 'No description')}
        Severity: {incident_data.get('severity', 'Unknown')}
        
        Provide a 2-3 sentence analysis and risk level (LOW/MEDIUM/HIGH).
        """
        
        return await self.chat(prompt, temperature=0.5)
    
    def _system_prompt(self) -> str:
        """System prompt for campus security context"""
        return """You are an expert AI assistant for campus security operations at CampusShield AI.
        
Your role is to:
- Help security staff understand incidents and threats
- Provide clear, actionable analysis
- Maintain professionalism and accuracy
- Be concise (aim for 2-5 sentences per response)

Always respond in JSON-compatible format. Be direct and avoid ambiguity."""
    
    def _fallback_response(self, message: str, confidence: float = 0.0) -> dict:
        """Fallback response when LLM unavailable"""
        return {
            "reply": message,
            "confidence": confidence,
            "sources": []
        }


# Singleton instance
_instance: Optional[AIAssistantService] = None


def get_ai_assistant(
    openai_client=None,
    model: str = "gpt-4o-mini",
    timeout: int = 30
) -> AIAssistantService:
    """Get or create singleton AI assistant instance"""
    global _instance
    
    if _instance is None:
        if openai_client is None:
            from openai import AsyncOpenAI
            openai_client = AsyncOpenAI()
        
        _instance = AIAssistantService(openai_client, model=model, timeout=timeout)
    
    return _instance
