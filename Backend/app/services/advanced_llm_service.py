"""
Advanced LLM Service for LangChain integration.

Provides multi-turn chat, summarization, reporting, and anomaly explanation
using LangChain orchestration.
"""

import os
import sys
from typing import Optional
from ..core.logging import setup_logger

logger = setup_logger(__name__)

# Import from ai module - fail fast if unavailable
# Add project root to Python path to allow importing ai module
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai.llm_utils import (
    LLMService,
    LLMConfig,
    get_llm_service as get_llm_service_util,
    reset_llm_service as reset_service_util,
)

__all__ = ['get_llm_service', 'reset_llm_service', 'LLMConfig']


def get_llm_service(
    config: Optional[LLMConfig] = None,
) -> LLMService:
    """
    Get advanced LLM service instance.
    
    Args:
        config: Optional LLMConfig for customization
    
    Returns:
        LLMService instance
    """
    return get_llm_service_util(config=config)


def reset_llm_service():
    """Reset LLM service instance."""
    reset_service_util()
