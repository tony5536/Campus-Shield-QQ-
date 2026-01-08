"""
Compatibility layer for old ai/llm_utils.py module.
Provides modern LangChain imports only - no deprecated fallbacks.
"""
import os
from typing import Optional

# Use modern LangChain imports only
try:
    from langchain_openai import ChatOpenAI
    from langchain.chains import LLMChain
    from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
    from langchain.prompts import PromptTemplate, ChatPromptTemplate
    from langchain.callbacks import StreamingStdOutCallbackHandler
    LANGCHAIN_MODERN_AVAILABLE = True
except ImportError:
    ChatOpenAI = None
    LLMChain = None
    ConversationBufferMemory = None
    ConversationSummaryMemory = None
    PromptTemplate = None
    ChatPromptTemplate = None
    StreamingStdOutCallbackHandler = None
    LANGCHAIN_MODERN_AVAILABLE = False

__all__ = [
    "ChatOpenAI",
    "LLMChain",
    "ConversationBufferMemory",
    "ConversationSummaryMemory",
    "PromptTemplate",
    "ChatPromptTemplate",
    "StreamingStdOutCallbackHandler",
    "LANGCHAIN_MODERN_AVAILABLE",
]

