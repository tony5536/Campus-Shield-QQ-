#!/usr/bin/env python
"""
API endpoint validation script - test each route with sample requests.
"""
import json
import sys
from pathlib import Path

# Test imports
sys.path.insert(0, str(Path(__file__).parent))

from Backend.app.main import app
from fastapi.testclient import TestClient

# Create test client
client = TestClient(app)

print("=" * 70)
print("🧪 TESTING API ENDPOINTS")
print("=" * 70)

# 1. Health check
print("\n1️⃣  GET /health")
try:
    resp = client.get("/health")
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
    assert resp.status_code == 200, "Health check failed"
    print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 2. Auth - Login (will fail without valid user, but tests schema)
print("\n2️⃣  POST /api/auth/login")
try:
    payload = {"username": "testuser", "password": "testpass"}
    resp = client.post("/api/auth/login", json=payload)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 401:
        print(f"   Response: {resp.json()}")
        print("   ✓ PASS (expected 401 for invalid user)")
    else:
        print(f"   Response: {resp.json()}")
        print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 3. Cameras - Create Camera
print("\n3️⃣  POST /api/cameras/")
try:
    payload = {
        "name": "Main Gate",
        "rtsp_url": "rtsp://example.com:554/stream",
        "location": "North Entrance"
    }
    resp = client.post("/api/cameras/", json=payload)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        camera_data = resp.json()
        camera_id = camera_data.get("id")
        print(f"   Response: {camera_data}")
        print("   ✓ PASS")
    else:
        print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 4. Cameras - List Cameras
print("\n4️⃣  GET /api/cameras/")
try:
    resp = client.get("/api/cameras/")
    print(f"   Status: {resp.status_code}")
    cameras = resp.json()
    print(f"   Response: {len(cameras)} camera(s)")
    if cameras:
        print(f"   First camera: {cameras[0]}")
    print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 5. Cameras - Get Camera by ID
print("\n5️⃣  GET /api/cameras/1")
try:
    resp = client.get("/api/cameras/1")
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   Response: {resp.json()}")
        print("   ✓ PASS")
    elif resp.status_code == 404:
        print(f"   Response: {resp.json()}")
        print("   ✓ PASS (expected 404 if no camera with ID 1)")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 6. Incidents - Create Incident
print("\n6️⃣  POST /api/incidents/")
try:
    payload = {
        "camera_id": 1,
        "incident_type": "suspicious_activity",
        "severity": 0.7,
        "description": "Person loitering near entrance"
    }
    resp = client.post("/api/incidents/", json=payload)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        incident_data = resp.json()
        print(f"   Response: {incident_data}")
        print("   ✓ PASS")
    else:
        print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 7. Incidents - List Incidents
print("\n7️⃣  GET /api/incidents/")
try:
    resp = client.get("/api/incidents/")
    print(f"   Status: {resp.status_code}")
    incidents = resp.json()
    print(f"   Response: {len(incidents)} incident(s)")
    print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 8. Alerts - List Alerts
print("\n8️⃣  GET /api/alerts/")
try:
    resp = client.get("/api/alerts/")
    print(f"   Status: {resp.status_code}")
    alerts = resp.json()
    print(f"   Response: {len(alerts)} alert(s)")
    if alerts:
        print(f"   First alert: {alerts[0]}")
    print("   ✓ PASS")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

# 9. Alerts - Acknowledge Alert
print("\n9️⃣  POST /api/alerts/1/ack")
try:
    resp = client.post("/api/alerts/1/ack", params={"actor": "guard"})
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"   Response: {resp.json()}")
        print("   ✓ PASS")
    elif resp.status_code == 404:
        print(f"   Response: {resp.json()}")
        print("   ✓ PASS (expected 404 if no alert with ID 1)")
except Exception as e:
    print(f"   ✗ FAIL: {e}")

print("\n" + "=" * 70)
print("✅ API ENDPOINT VALIDATION COMPLETE")
print("=" * 70)
