import sys
import os
# Add root to python path
sys.path.insert(0, "C:/Dev/CampusShield-AI")

try:
    from Backend.app.main import app
    
    print("Registered Routes:")
    for route in app.routes:
        if hasattr(route, "path"):
            methods = ", ".join(route.methods) if hasattr(route, "methods") else "None"
            print(f"{methods} {route.path}")
            
    print("\nChecking Modules:")
    try:
        from Backend.app.api.routes import ai
        print(f"Backend.app.api.routes.ai imported: {ai}")
    except Exception as e:
        print(f"Error importing Backend.app.api.routes.ai: {e}")

except Exception as e:
    print(f"Failed to load app: {e}")
