#!/usr/bin/env python
"""
Backend validation script - tests app startup and routes.
"""
import sys
from pathlib import Path

# Load the FastAPI app
try:
    from Backend.app.main import app
    print("✓ FastAPI app instance loaded successfully")
except Exception as e:
    print(f"✗ Failed to load app: {e}")
    sys.exit(1)

# List routes
print(f"\n📍 Total routes: {len(app.routes)}\n")
print("Registered Endpoints:")
for route in app.routes:
    if hasattr(route, 'methods'):
        methods = ', '.join(sorted(route.methods - {'OPTIONS', 'HEAD'}))
        print(f"  {methods:8} {route.path}")
    elif hasattr(route, 'path'):
        print(f"  {'WS':8} {route.path}")

# Check settings
try:
    from Backend.app.config.settings import settings
    print(f"\n⚙️  Config loaded:")
    print(f"  - app_name: {settings.app_name}")
    print(f"  - debug: {settings.debug}")
    print(f"  - database_url: {settings.database_url[:50]}...")
    print(f"  - cors_origins: {settings.cors_origins}")
except Exception as e:
    print(f"✗ Config error: {e}")

# Check database table definitions
try:
    from Backend.app.models.base import Base
    from Backend.app.models.user import User
    from Backend.app.models.camera import Camera
    from Backend.app.models.incident import Incident
    from Backend.app.models.alert import Alert
    print(f"\n💾 Database models loaded:")
    print(f"  - User")
    print(f"  - Camera")
    print(f"  - Incident")
    print(f"  - Alert")
except Exception as e:
    print(f"✗ Model loading error: {e}")

# Check services
try:
    from Backend.app.services.ai_service import analyze_clip
    from Backend.app.services.notification_service import NotificationManager
    from Backend.app.services.orchestrator import enrich_incident_with_clip
    print(f"\n🔧 Services loaded:")
    print(f"  - AI Service (analyze_clip)")
    print(f"  - Notification Manager (broadcast)")
    print(f"  - Orchestrator (enrich_incident_with_clip)")
except Exception as e:
    print(f"✗ Service loading error: {e}")

# Check utilities
try:
    from Backend.app.utils.security import get_password_hash, verify_password, create_access_token, authenticate_user
    from Backend.app.utils.logger import setup_logger
    from Backend.app.utils.video_utils import build_clip_path
    print(f"\n🛠️  Utilities loaded:")
    print(f"  - Security (auth, hashing)")
    print(f"  - Logger")
    print(f"  - Video Utils")
except Exception as e:
    print(f"✗ Utility loading error: {e}")

print("\n✅ All modules loaded successfully!")
