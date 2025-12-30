#!/usr/bin/env python3
"""
Dependency Checker Script
Checks if all required dependencies are installed before starting the server.
Run this script to verify your environment is properly set up.
"""
import sys
import importlib
from typing import List, Tuple

# Required packages from requirements.txt
# Format: (package_name_in_requirements, import_name_in_code)
REQUIRED_PACKAGES = [
    ("fastapi", "fastapi"),
    ("uvicorn[standard]", "uvicorn"),
    ("SQLAlchemy", "sqlalchemy"),
    ("pydantic", "pydantic"),
    ("pydantic-settings", "pydantic_settings"),
    ("python-jose[cryptography]", "jose"),
    ("passlib[bcrypt]", "passlib"),
    ("aiofiles", "aiofiles"),
    ("python-multipart", "multipart"),
    ("python-dotenv", "dotenv"),
    ("httpx", "httpx"),
]

def check_package(package_name: str, import_name: str) -> Tuple[bool, str]:
    """
    Check if a package is installed.
    
    Args:
        package_name: The name as it appears in requirements.txt
        import_name: The name used in import statements
    
    Returns:
        Tuple of (is_installed, error_message)
    """
    try:
        # Import the module to verify it's installed
        importlib.import_module(import_name)
        return True, ""
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def check_all_dependencies() -> bool:
    """Check all required dependencies and print results."""
    print("Checking required dependencies...")
    print("-" * 60)
    
    missing_packages = []
    all_good = True
    
    for package_name, import_name in REQUIRED_PACKAGES:
        is_installed, error = check_package(package_name, import_name)
        
        if is_installed:
            print(f"[OK] {package_name:30s} - Installed")
        else:
            print(f"[X] {package_name:30s} - MISSING ({error})")
            missing_packages.append(package_name)
            all_good = False
    
    print("-" * 60)
    
    if all_good:
        print("\n[SUCCESS] All dependencies are installed!")
        return True
    else:
        print(f"\n[ERROR] {len(missing_packages)} package(s) are missing:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r Backend\\requirements.txt")
        print("Or from the project root:")
        print("  pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = check_all_dependencies()
    sys.exit(0 if success else 1)

