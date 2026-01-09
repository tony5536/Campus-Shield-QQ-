"""
CampusShield AI - Startup Validation & Initialization Script
Ensures all critical components are properly configured before startup.
"""

import os
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent
backend_root = project_root / "Backend"
sys.path.insert(0, str(backend_root))
sys.path.insert(0, str(project_root))

def check_environment():
    """Validate environment configuration."""
    print("\n" + "="*70)
    print("CAMPUSSHIELD AI - STARTUP VALIDATION")
    print("="*70)
    
    print("\n[ENV] Checking environment configuration...")
    
    # Check .env file exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print(f"[ENV] ✗ CRITICAL: .env file not found at {env_file}")
        print("[ENV] Create .env with OPENAI_API_KEY and other settings")
        return False
    
    print(f"[ENV] ✓ .env file found at {env_file}")
    
    # Load and validate .env
    from dotenv import load_dotenv, dotenv_values
    load_dotenv(env_file)
    env_vars = dotenv_values(env_file)
    
    # Check critical variables
    critical_vars = {
        'OPENAI_API_KEY': 'OpenAI API key',
        'ENABLE_LLM': 'LLM enabled flag',
        'ENVIRONMENT': 'Environment type',
    }
    
    missing_vars = []
    for var, desc in critical_vars.items():
        value = os.getenv(var) or env_vars.get(var)
        if not value:
            missing_vars.append(f"{var} ({desc})")
            print(f"[ENV] ✗ Missing: {var} - {desc}")
        else:
            if var == 'OPENAI_API_KEY':
                masked = value[:10] + "..." + value[-4:] if len(value) > 20 else "***"
                print(f"[ENV] ✓ {var} = {masked}")
            else:
                print(f"[ENV] ✓ {var} = {value}")
    
    if missing_vars:
        print(f"\n[ENV] ✗ Missing critical variables: {', '.join(missing_vars)}")
        return False
    
    print("\n[ENV] ✓ All critical environment variables configured")
    return True


def check_backend_dependencies():
    """Validate Python dependencies."""
    print("\n[DEPS] Checking Python dependencies...")
    
    critical_packages = {
        'fastapi': 'FastAPI framework',
        'sqlalchemy': 'SQLAlchemy ORM',
        'pydantic': 'Pydantic validation',
        'langchain': 'LangChain LLM framework',
        'langchain_openai': 'LangChain OpenAI integration',
        'openai': 'OpenAI SDK',
        'dotenv': 'python-dotenv for .env loading',
    }
    
    missing_packages = []
    for package, desc in critical_packages.items():
        try:
            __import__(package)
            print(f"[DEPS] ✓ {package} - {desc}")
        except ImportError:
            missing_packages.append(f"{package} ({desc})")
            print(f"[DEPS] ✗ Missing: {package} - {desc}")
    
    if missing_packages:
        print(f"\n[DEPS] ✗ Missing packages: {', '.join(missing_packages)}")
        print("[DEPS] Install with: pip install -r Backend/requirements.txt")
        return False
    
    print("\n[DEPS] ✓ All critical packages available")
    return True


def check_backend_config():
    """Validate backend configuration."""
    print("\n[CONFIG] Checking backend configuration...")
    
    try:
        from Backend.app.core.config import settings
        
        # Check LLM configuration
        print(f"[CONFIG] ✓ Settings loaded from {settings.__class__.__module__}")
        print(f"[CONFIG]   - Environment: {settings.environment}")
        print(f"[CONFIG]   - LLM Enabled: {settings.enable_llm}")
        print(f"[CONFIG]   - LLM Provider: {settings.llm_provider}")
        print(f"[CONFIG]   - OpenAI Model: {settings.openai_model}")
        print(f"[CONFIG]   - RAG Enabled: {settings.enable_rag}")
        print(f"[CONFIG]   - Database: {settings.database_url}")
        
        # Validate critical settings
        if settings.enable_llm and not settings.openai_api_key:
            print("[CONFIG] ✗ LLM enabled but OPENAI_API_KEY not configured!")
            return False
        
        if settings.enable_llm:
            print(f"[CONFIG] ✓ LLM configured with OpenAI API key")
        else:
            print("[CONFIG] ⚠ LLM disabled (ENABLE_LLM=false)")
        
        print("[CONFIG] ✓ Backend configuration valid")
        return True
        
    except Exception as e:
        print(f"[CONFIG] ✗ Error loading settings: {e}")
        return False


def check_database():
    """Check and initialize database."""
    print("\n[DB] Checking database...")
    
    try:
        from Backend.app.core.security import SessionLocal
        from Backend.app.db.base import init_db
        
        print("[DB] Initializing database schema...")
        init_db()
        print("[DB] ✓ Database tables created/verified")
        
        # Check connectivity
        db = SessionLocal()
        try:
            db.execute("SELECT 1")
            print("[DB] ✓ Database connection successful")
            return True
        finally:
            db.close()
            
    except Exception as e:
        print(f"[DB] ✗ Error with database: {e}")
        return False


def check_services():
    """Check LLM and RAG services."""
    print("\n[SERVICES] Checking AI services...")
    
    try:
        from Backend.app.services.langchain_service import get_langchain_service
        from Backend.app.services.rag_service import get_rag_service
        
        # Check LLM
        llm_service = get_langchain_service()
        if llm_service.is_available:
            print(f"[SERVICES] ✓ LLM Service: AVAILABLE ({llm_service.status.get('model', 'unknown')})")
        else:
            print(f"[SERVICES] ✗ LLM Service: UNAVAILABLE")
            if llm_service.status.get('error'):
                print(f"         Error: {llm_service.status['error']}")
        
        # Check RAG
        rag_service = get_rag_service()
        if rag_service.is_available:
            print(f"[SERVICES] ✓ RAG Service: AVAILABLE ({rag_service.status.get('vector_store_type', 'unknown')})")
        elif rag_service.status['enabled']:
            print(f"[SERVICES] ⚠ RAG Service: ENABLED but NOT AVAILABLE")
            if rag_service.status.get('error'):
                print(f"         Error: {rag_service.status['error']}")
        else:
            print(f"[SERVICES] [INFO] RAG Service: DISABLED (ENABLE_RAG=false)")
        
        return True
        
    except Exception as e:
        print(f"[SERVICES] ✗ Error checking services: {e}")
        return False


def main():
    """Run all startup checks."""
    checks = [
        ("Environment Configuration", check_environment),
        ("Python Dependencies", check_backend_dependencies),
        ("Backend Configuration", check_backend_config),
        ("Database", check_database),
        ("AI Services", check_services),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("STARTUP VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ All startup checks passed! System is ready.")
        print("\nNext steps:")
        print("1. Start backend:  python app.py")
        print("2. Start frontend: cd dashboard && npm start")
        print("3. Open browser:   http://localhost:3000")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix issues above before starting.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
