"""LLM module for CampusShield AI."""
from .base import BaseLLM, LLMProvider
from .openai import OpenAILLM
from .local import LocalLLM

__all__ = ["BaseLLM", "LLMProvider", "OpenAILLM", "LocalLLM"]

