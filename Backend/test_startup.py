import sys
sys.path.insert(0, '.')
try:
    from app.services.advanced_llm_service import get_llm_service
    print(' LLM service import works')
    service = get_llm_service()
    print(f' LLM service initialized: {service}')
except Exception as e:
    print(f' LLM service error: {type(e).__name__}: {e}')

try:
    from app.services.rag_service import get_rag_service
    print(' RAG service import works')
    service = get_rag_service()
    print(f' RAG service initialized: {service}')
except Exception as e:
    print(f' RAG service error: {type(e).__name__}: {e}')

try:
    from app.ai.rag.vector_store import get_vector_store
    print(' Vector store import works')
    vs = get_vector_store()
    print(f' Vector store initialized: {vs}')
except Exception as e:
    print(f' Vector store error: {type(e).__name__}: {e}')
