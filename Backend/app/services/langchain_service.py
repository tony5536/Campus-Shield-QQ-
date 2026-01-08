"""
Centralized LangChain LLM Service for CampusShield AI.
Uses modern LangChain imports and provides graceful degradation.
"""
import os
from typing import Optional, Dict, Any
from ..core.config import settings
from ..core.logging import setup_logger

logger = setup_logger(__name__)

# Try to import LangChain components with modern imports
try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
    # Optional imports for advanced features
    try:
        from langchain.chains import LLMChain
        from langchain.memory import ConversationBufferMemory
        from langchain.prompts import PromptTemplate, ChatPromptTemplate
    except ImportError:
        # These are optional - ChatOpenAI is the main requirement
        LLMChain = None
        ConversationBufferMemory = None
        PromptTemplate = None
        ChatPromptTemplate = None
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger.warning(f"LangChain not available: {e}")
    ChatOpenAI = None
    LLMChain = None
    ConversationBufferMemory = None
    PromptTemplate = None
    ChatPromptTemplate = None


class LangChainService:
    """
    Centralized LangChain service with graceful degradation.
    """
    
    def __init__(self):
        self._llm = None
        self._available = False
        self._initialized = False
        self._init_error = None
        
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain packages not installed. LLM features will be disabled.")
            return
        
        self._initialize()
    
    def _initialize(self):
        """Initialize ChatOpenAI instance."""
        if not LANGCHAIN_AVAILABLE:
            return
        
        try:
            api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                logger.warning("OPENAI_API_KEY not configured. LLM features will be disabled.")
                self._init_error = "OPENAI_API_KEY not found"
                return
            
            self._llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0.7,
                max_tokens=1500,
                api_key=api_key,
                streaming=False,
            )
            
            self._available = True
            self._initialized = True
            logger.info(f"LangChain LLM initialized successfully with model: {settings.openai_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain LLM: {e}")
            self._init_error = str(e)
            self._available = False
    
    @property
    def llm(self) -> Optional[Any]:
        """Get ChatOpenAI instance if available."""
        if not self._available or not self._initialized:
            return None
        return self._llm
    
    @property
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self._available and self._initialized
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "available": self.is_available,
            "langchain_installed": LANGCHAIN_AVAILABLE,
            "initialized": self._initialized,
            "model": settings.openai_model if self.is_available else None,
            "error": self._init_error,
        }
    
    def get_llm(self) -> Optional[Any]:
        """Get LLM instance (alias for llm property)."""
        return self.llm


# Global singleton instance
_langchain_service: Optional[LangChainService] = None


def get_langchain_service() -> LangChainService:
    """Get or create LangChain service instance."""
    global _langchain_service
    if _langchain_service is None:
        _langchain_service = LangChainService()
    return _langchain_service


def is_langchain_available() -> bool:
    """Check if LangChain is available and configured."""
    service = get_langchain_service()
    return service.is_available

