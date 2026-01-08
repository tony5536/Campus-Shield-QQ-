"""
Production readiness validation script.
Checks all systems for proper configuration before deployment.
"""
import os
import sys
from pathlib import Path

def check_backend_structure():
    """Verify all backend files exist"""
    print("\n" + "=" * 60)
    print("BACKEND STRUCTURE CHECK")
    print("=" * 60)
    
    required_files = [
        "app/schemas/incident.py",
        "app/config/settings.py",
        "app/core/logging.py",
        "app/services/ai_assistant.py",
        "app/api/v1/incidents_hardened.py",
        "app/api/v1/ai_hardened.py",
        "app/main.py",
        "requirements.txt"
    ]
    
    backend_dir = Path("Backend")
    all_exist = True
    
    for file in required_files:
        path = backend_dir / file
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist


def check_frontend_structure():
    """Verify all frontend files exist"""
    print("\n" + "=" * 60)
    print("FRONTEND STRUCTURE CHECK")
    print("=" * 60)
    
    required_files = [
        "src/schemas/incident.js",
        "src/services/api.js",
        "src/pages/IncidentsHardened.jsx",
    ]
    
    dashboard_dir = Path("dashboard")
    all_exist = True
    
    for file in required_files:
        path = dashboard_dir / file
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist


def check_env_configuration():
    """Check .env file for critical variables"""
    print("\n" + "=" * 60)
    print("ENVIRONMENT CONFIGURATION CHECK")
    print("=" * 60)
    
    env_path = Path("Backend/.env")
    
    if not env_path.exists():
        print("✗ .env file not found")
        print("  Create with: cp Backend/.env.example Backend/.env")
        return False
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    critical_vars = [
        ("DATABASE_URL", "Database connection"),
        ("OPENAI_API_KEY", "OpenAI API key"),
        ("LLM_PROVIDER", "LLM provider selection"),
    ]
    
    all_set = True
    for var, description in critical_vars:
        if var in env_content and f"{var}=" in env_content:
            print(f"✓ {var}: {description}")
        else:
            print(f"✗ {var}: {description} - NOT SET")
            all_set = False
    
    return all_set


def check_dependencies():
    """Check if Python dependencies are installed"""
    print("\n" + "=" * 60)
    print("PYTHON DEPENDENCIES CHECK")
    print("=" * 60)
    
    required = [
        "fastapi",
        "pydantic",
        "sqlalchemy",
        "openai",
        "langchain",
    ]
    
    all_installed = True
    for package in required:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print("\nInstall with: pip install -r Backend/requirements.txt")
    
    return all_installed


def check_data_contracts():
    """Verify data contract files"""
    print("\n" + "=" * 60)
    print("DATA CONTRACT CHECK")
    print("=" * 60)
    
    checks = [
        ("Backend/app/schemas/incident.py", [
            "IncidentResponse",
            "IncidentCreate",
            "AssistantResponse",
        ]),
        ("dashboard/src/schemas/incident.js", [
            "validateIncident",
            "normalizeIncident",
            "formatIncidentDisplay",
        ]),
    ]
    
    all_valid = True
    for file, exports in checks:
        path = Path(file)
        if not path.exists():
            print(f"✗ {file} - NOT FOUND")
            all_valid = False
            continue
        
        with open(path, 'r') as f:
            content = f.read()
        
        found = all(export in content for export in exports)
        status = "✓" if found else "✗"
        print(f"{status} {file}")
        
        if not found:
            all_valid = False
            for export in exports:
                if export not in content:
                    print(f"  ✗ Missing: {export}")
    
    return all_valid


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║  CAMPUSSHIELD AI - PRODUCTION READINESS VALIDATION     ║")
    print("╚" + "=" * 58 + "╝")
    
    results = {
        "Backend Structure": check_backend_structure(),
        "Frontend Structure": check_frontend_structure(),
        "Environment Config": check_env_configuration(),
        "Dependencies": check_dependencies(),
        "Data Contracts": check_data_contracts(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - SYSTEM IS PRODUCTION READY")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review PRODUCTION_HARDENING_GUIDE.md")
        print("2. Start backend: python -m uvicorn app.main:app --reload")
        print("3. Start frontend: npm start")
        print("4. Test API endpoints")
        print("5. Deploy to production")
    else:
        print("✗ SOME CHECKS FAILED - REVIEW ABOVE")
        print("=" * 60)
        print("\nFix issues before proceeding to production")
        sys.exit(1)


if __name__ == "__main__":
    main()
