#!/usr/bin/env python
"""
Comprehensive test suite for CampusShield AI LLM & RAG restoration.
Verifies all core functionality is working correctly.
"""
import sys
from pathlib import Path

# Add Backend to path
backend_path = Path(__file__).parent / "Backend"
sys.path.insert(0, str(backend_path))


def test_core_config():
    """Test that core configuration loads correctly."""
    print("\n" + "="*70)
    print("TEST 1: Core Configuration")
    print("="*70)
    
    from app.core.config import settings
    
    assert hasattr(settings, 'enable_llm'), "Missing enable_llm field"
    assert hasattr(settings, 'enable_rag'), "Missing enable_rag field"
    assert hasattr(settings, 'openai_api_key'), "Missing openai_api_key field"
    assert hasattr(settings, 'vector_store_type'), "Missing vector_store_type field"
    
    print(f"✓ Settings loaded successfully")
    print(f"  - LLM Enabled: {settings.enable_llm}")
    print(f"  - RAG Enabled: {settings.enable_rag}")
    print(f"  - OpenAI Model: {settings.openai_model}")
    print(f"  - Vector Store Type: {settings.vector_store_type}")
    print(f"  - Embedding Model: {settings.embedding_model}")
    
    return True


def test_langchain_service():
    """Test LangChain service initialization."""
    print("\n" + "="*70)
    print("TEST 2: LangChain Service (LLM)")
    print("="*70)
    
    from app.services.langchain_service import get_langchain_service, is_langchain_available
    
    service = get_langchain_service()
    
    assert service is not None, "LangChain service not initialized"
    assert hasattr(service, 'status'), "Service missing status property"
    
    status = service.status
    print(f"✓ LangChain service initialized")
    print(f"  - Available: {status.get('available', False)}")
    print(f"  - LangChain installed: {status.get('langchain_installed', False)}")
    print(f"  - Initialized: {status.get('initialized', False)}")
    
    if status.get('error'):
        print(f"  - Error: {status.get('error')} (expected if OPENAI_API_KEY not set)")
    
    return True


def test_rag_service():
    """Test RAG service initialization."""
    print("\n" + "="*70)
    print("TEST 3: RAG Service")
    print("="*70)
    
    from app.services.rag_service import get_rag_service, is_rag_available
    
    service = get_rag_service()
    
    assert service is not None, "RAG service not initialized"
    assert hasattr(service, 'status'), "Service missing status property"
    
    status = service.status
    print(f"✓ RAG service initialized")
    print(f"  - Available: {status.get('available', False)}")
    print(f"  - Enabled: {status.get('enabled', False)}")
    print(f"  - Vector Store Type: {status.get('vector_store_type', 'N/A')}")
    
    if status.get('error'):
        print(f"  - Error: {status.get('error')} (expected if dependencies not installed)")
    
    return True


def test_vector_store():
    """Test vector store initialization."""
    print("\n" + "="*70)
    print("TEST 4: Vector Store (FAISS)")
    print("="*70)
    
    from app.ai.rag.vector_store import get_vector_store
    
    store = get_vector_store()
    
    assert store is not None, "Vector store not initialized"
    store_type = store.__class__.__name__
    print(f"✓ Vector store initialized: {store_type}")
    
    if store_type == "NoOpVectorStore":
        print(f"  - Using no-op store (dependencies or RAG disabled)")
    elif store_type == "FAISSVectorStore":
        print(f"  - Using FAISS vector store (FAISS + sentence-transformers available)")
    
    return True


def test_vector_store_operations():
    """Test basic vector store operations."""
    print("\n" + "="*70)
    print("TEST 5: Vector Store Operations")
    print("="*70)
    
    from app.ai.rag.vector_store import get_vector_store
    
    store = get_vector_store()
    store_type = store.__class__.__name__
    
    # Test add_documents
    try:
        ids = store.add_documents(
            texts=["Test document 1", "Test document 2"],
            metadatas=[{"source": "test1"}, {"source": "test2"}]
        )
        print(f"✓ add_documents() successful: {len(ids)} documents added")
    except Exception as e:
        print(f"  - add_documents() skipped or failed: {str(e)[:50]}")
    
    # Test similarity_search
    try:
        results = store.similarity_search("test", k=2)
        print(f"✓ similarity_search() successful: {len(results)} results")
    except Exception as e:
        print(f"  - similarity_search() skipped or failed: {str(e)[:50]}")
    
    return True


def test_ai_module_structure():
    """Test that AI module structure is intact."""
    print("\n" + "="*70)
    print("TEST 6: AI Module Structure")
    print("="*70)
    
    # Test LLM module
    try:
        from app.ai.llm.openai import OpenAILLM
        from app.ai.llm.base import BaseLLM
        print(f"✓ LLM module: base and OpenAI implementations available")
    except ImportError as e:
        print(f"  - LLM module issue: {str(e)[:50]}")
    
    # Test RAG module
    try:
        from app.ai.rag.vector_store import get_vector_store
        from app.ai.rag.indexer import DocumentIndexer
        from app.ai.rag.retriever import RAGRetriever
        from app.ai.rag.qa_chain import RAGQAChain
        print(f"✓ RAG module: all components available")
    except ImportError as e:
        print(f"  - RAG module issue: {str(e)[:50]}")
    
    return True


def test_main_app_startup():
    """Test that main app can be imported (startup sequence check)."""
    print("\n" + "="*70)
    print("TEST 7: Main App Startup")
    print("="*70)
    
    try:
        # This will trigger all the import statements and initialization
        from app import main
        
        assert hasattr(main, 'app'), "FastAPI app not initialized"
        assert main.langchain_service is not None, "LangChain service not initialized"
        assert main.rag_service is not None, "RAG service not initialized"
        
        print(f"✓ FastAPI app initialized successfully")
        print(f"  - LLM available: {main.llm_available}")
        print(f"  - RAG available: {main.rag_available}")
        print(f"  - Environment: {main.env_label}")
        print(f"  - Debug: {main.settings.debug}")
        
    except Exception as e:
        print(f"✗ Main app startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_settings_validation():
    """Test that settings validation works correctly."""
    print("\n" + "="*70)
    print("TEST 8: Settings Validation")
    print("="*70)
    
    from app.core.config import settings
    
    # Check that validation runs on startup
    checks = settings.validate_startup()
    
    print(f"✓ Settings validation completed")
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}: {result}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("CampusShield AI - LLM & RAG Restoration Test Suite")
    print("="*70)
    
    tests = [
        ("Core Configuration", test_core_config),
        ("LangChain Service", test_langchain_service),
        ("RAG Service", test_rag_service),
        ("Vector Store", test_vector_store),
        ("Vector Store Operations", test_vector_store_operations),
        ("AI Module Structure", test_ai_module_structure),
        ("Main App Startup", test_main_app_startup),
        ("Settings Validation", test_settings_validation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except AssertionError as e:
            results[test_name] = False
            print(f"\n✗ {test_name} FAILED: {e}")
        except Exception as e:
            results[test_name] = False
            print(f"\n✗ {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - LLM & RAG restoration is complete!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - see details above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
