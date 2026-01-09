#!/usr/bin/env python
"""Test script to verify LLM and RAG services load correctly."""
import sys
from pathlib import Path

# Add Backend to path
backend_path = Path(__file__).parent / "Backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test that all critical modules can be imported."""
    print("=" * 60)
    print("Testing CampusShield AI Backend Imports")
    print("=" * 60)
    
    # Test core config
    try:
        from app.core.config import settings
        print("[OK] Core config settings loaded")
        print(f"    LLM Enabled: {settings.enable_llm}")
        print(f"    RAG Enabled: {settings.enable_rag}")
        print(f"    OpenAI API Key configured: {bool(settings.openai_api_key)}")
    except Exception as e:
        print(f"[FAIL] Core config: {e}")
        return False
    
    # Test logging
    try:
        from app.core.logging import setup_logger
        logger = setup_logger(__name__)
        print("[OK] Logging initialized")
    except Exception as e:
        print(f"[FAIL] Logging: {e}")
        return False
    
    # Test LangChain service
    try:
        from app.services.langchain_service import get_langchain_service
        langchain_service = get_langchain_service()
        print(f"[OK] LangChain service initialized")
        status = langchain_service.status
        print(f"    Available: {status.get('available', False)}")
        print(f"    LangChain installed: {status.get('langchain_installed', False)}")
        if status.get('error'):
            print(f"    Error: {status.get('error')}")
    except Exception as e:
        print(f"[FAIL] LangChain service: {e}")
        return False
    
    # Test RAG service
    try:
        from app.services.rag_service import get_rag_service
        rag_service = get_rag_service()
        print(f"[OK] RAG service initialized")
        status = rag_service.status
        print(f"    Available: {status.get('available', False)}")
        print(f"    Enabled: {status.get('enabled', False)}")
        print(f"    Vector store type: {status.get('vector_store_type', 'N/A')}")
        if status.get('error'):
            print(f"    Error: {status.get('error')}")
    except Exception as e:
        print(f"[FAIL] RAG service: {e}")
        return False
    
    # Test vector store
    try:
        from app.ai.rag.vector_store import get_vector_store
        store = get_vector_store()
        print(f"[OK] Vector store loaded: {store.__class__.__name__}")
    except Exception as e:
        print(f"[FAIL] Vector store: {e}")
        return False
    
    print("=" * 60)
    print("All imports successful!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
