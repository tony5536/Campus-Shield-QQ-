"""
LLM Factory Service - Centralized LLM initialization and management.
Provides unified interface for LLM operations with graceful degradation.
"""
from typing import Optional, Dict, Any
from ..core.config import settings
from ..core.logging import setup_logger
from .langchain_service import get_langchain_service, is_langchain_available

logger = setup_logger(__name__)


class LLMFactory:
    """
    Factory for creating and managing LLM instances.
    Supports multiple providers with graceful fallback.
    """
    
    def __init__(self):
        self.langchain_service = get_langchain_service()
        self._llm_instance = None
    
    def get_llm(self, provider: Optional[str] = None):
        """
        Get LLM instance for the specified provider.
        
        Args:
            provider: LLM provider name (defaults to settings.llm_provider)
            
        Returns:
            LLM instance or None if unavailable
        """
        provider = provider or settings.llm_provider
        
        if provider == "openai":
            return self._get_openai_llm()
        elif provider == "groq":
            return self._get_groq_llm()
        elif provider == "gemini":
            return self._get_gemini_llm()
        else:
            logger.warning(f"Unknown LLM provider: {provider}")
            return None
    
    def _get_openai_llm(self):
        """Get OpenAI LLM instance."""
        if is_langchain_available():
            return self.langchain_service.llm
        
        # Fallback to direct OpenAI if LangChain not available
        try:
            from ..ai.llm.openai import OpenAILLM
            return OpenAILLM()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI LLM: {e}")
            return None
    
    def _get_groq_llm(self):
        """Get Groq LLM instance."""
        # Use the existing LLM service for Groq
        try:
            from ..services.llm_service import LLMService
            service = LLMService()
            if service.provider == "groq" and service.groq_api_key:
                return service
        except Exception as e:
            logger.error(f"Failed to initialize Groq LLM: {e}")
        return None
    
    def _get_gemini_llm(self):
        """Get Gemini LLM instance."""
        try:
            from ..services.llm_service import LLMService
            service = LLMService()
            if service.provider == "gemini" and service.gemini_api_key:
                return service
        except Exception as e:
            logger.error(f"Failed to initialize Gemini LLM: {e}")
        return None
    
    def is_available(self, provider: Optional[str] = None) -> bool:
        """Check if LLM is available for the provider."""
        provider = provider or settings.llm_provider
        
        if provider == "openai":
            return is_langchain_available()
        elif provider == "groq":
            return bool(settings.groq_api_key)
        elif provider == "gemini":
            return bool(settings.gemini_api_key)
        return False


# Global factory instance
_llm_factory: Optional[LLMFactory] = None


def get_llm_factory() -> LLMFactory:
    """Get or create LLM factory instance."""
    global _llm_factory
    if _llm_factory is None:
        _llm_factory = LLMFactory()
    return _llm_factory

