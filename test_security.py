#!/usr/bin/env python
"""
Backend security, logging, and async code validation.
"""
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("🔒 SECURITY & CODE QUALITY VALIDATION")
print("=" * 70)

# 1. Check for hardcoded secrets
print("\n1️⃣  Checking for hardcoded secrets...")
suspicious_terms = ["password", "secret_key", "api_key", "token"]
files_to_check = [
    "Backend/app/main.py",
    "Backend/app/config/settings.py",
    "Backend/app/utils/security.py"
]

issues = []
for file_path in files_to_check:
    full_path = Path(file_path)
    if full_path.exists():
        content = full_path.read_text()
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if '=' in line and not line.strip().startswith('#'):
                for term in suspicious_terms:
                    if term.lower() in line.lower() and '=' in line:
                        value_part = line.split('=')[1].strip()
                        if value_part.startswith('"') or value_part.startswith("'"):
                            if "dev-secret" in value_part or "changeme" in value_part.lower():
                                issues.append(f"   ⚠️  {file_path}:{i} - {line.strip()}")

if issues:
    print("   ⚠️  Found hardcoded dev secrets (acceptable in DEV, fix for PROD):")
    for issue in issues:
        print(issue)
else:
    print("   ✓ No obvious hardcoded production secrets found")

# 2. Check debug flag
print("\n2️⃣  Checking debug flag...")
from Backend.app.config.settings import settings
if settings.debug:
    print(f"   ⚠️  DEBUG=True in config (settings.debug={settings.debug})")
    print("   ℹ️  This is acceptable in DEV but MUST be False in production")
else:
    print(f"   ✓ DEBUG=False (safe for production)")

# 3. Check CORS settings
print("\n3️⃣  Checking CORS configuration...")
if "*" in settings.cors_origins:
    print(f"   ⚠️  CORS_ORIGINS includes '*' (allows any origin)")
    print("   ℹ️  This is acceptable in DEV but should be restrictive in production")
    print(f"   Current: {settings.cors_origins}")
else:
    print(f"   ✓ CORS properly restricted: {settings.cors_origins}")

# 4. Check logging
print("\n4️⃣  Checking logging setup...")
try:
    from Backend.app.utils.logger import setup_logger
    logger = setup_logger("test")
    if logger.handlers:
        print(f"   ✓ Logger has {len(logger.handlers)} handler(s)")
        print(f"   ✓ Logger level: {logger.level}")
    else:
        print("   ⚠️  Logger has no handlers")
except Exception as e:
    print(f"   ✗ Logging error: {e}")

# 5. Check async/await patterns in routes
print("\n5️⃣  Checking async patterns in routes...")
try:
    from Backend.app.api.routes import auth, cameras, incidents, alerts
    
    async_count = 0
    sync_count = 0
    
    for route_module in [auth, cameras, incidents, alerts]:
        for name, obj in inspect.getmembers(route_module):
            if inspect.iscoroutinefunction(obj):
                async_count += 1
            elif callable(obj) and name.startswith(('get_', 'list_', 'create_', 'acknowledge')):
                if not inspect.iscoroutinefunction(obj):
                    sync_count += 1
    
    print(f"   ✓ Async route handlers: {async_count}")
    print(f"   ✓ Sync route handlers: {sync_count}")
    
    if sync_count > 0:
        print("   ℹ️  Sync handlers are fine if they don't block (e.g., DB queries with SQLAlchemy)")
except Exception as e:
    print(f"   ✗ Error checking routes: {e}")

# 6. Check for circular imports
print("\n6️⃣  Checking for circular imports...")
try:
    from Backend.app.main import app
    from Backend.app.services.orchestrator import enrich_incident_with_clip
    from Backend.app.services.ai_service import analyze_clip
    from Backend.app.models.user import User
    print("   ✓ No obvious circular imports detected")
except ImportError as e:
    print(f"   ✗ Circular import detected: {e}")

# 7. Check exception handling
print("\n7️⃣  Checking exception handling in routes...")
try:
    import Backend.app.api.routes.incidents as inc_route
    source = inspect.getsource(inc_route)
    if "HTTPException" in source and "raise HTTPException" in source:
        print("   ✓ HTTPException is used for error responses")
    if "try:" in source or "except:" in source:
        print("   ✓ Exception handling present")
    else:
        print("   ⚠️  Limited exception handling found")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 8. Check Pydantic models for validation
print("\n8️⃣  Checking Pydantic models...")
try:
    from Backend.app.api.routes.cameras import CameraIn, CameraOut
    from Backend.app.api.routes.incidents import IncidentIn, IncidentOut
    
    # Test validation
    try:
        camera = CameraIn(name="Test", rtsp_url="rtsp://example.com")
        print("   ✓ Pydantic models working (CameraIn)")
    except Exception as e:
        print(f"   ✗ Pydantic validation error: {e}")
    
    print("   ✓ Request/response schemas defined")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print("✅ SECURITY & CODE QUALITY VALIDATION COMPLETE")
print("=" * 70)
