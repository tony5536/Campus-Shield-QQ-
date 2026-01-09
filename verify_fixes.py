import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_ai_assist():
    print("\n[TEST] Testing AI Assist Alias (POST /api/ai/assist)...")
    url = f"{BASE_URL}/api/ai/assist"
    payload = {"query": "Suspicious person in the parking lot"}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "confidence" in data:
                 print(f"✅ SUCCESS: /api/ai/assist working. Response: {data.keys()}")
            else:
                 print(f"❌ FAILURE: Invalid JSON structure: {data.keys()}")
        else:
            print(f"❌ FAILURE: Status Check Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_incidents_redirect():
    print("\n[TEST] Testing Incidents Redirect (GET /api/v1/incidents)...")
    url = f"{BASE_URL}/api/v1/incidents" # No trailing slash
    try:
        response = requests.get(url, allow_redirects=False, timeout=5)
        if response.status_code == 200:
            print(f"✅ SUCCESS: /api/v1/incidents (no slash) returned 200 OK.")
        elif response.status_code == 307:
             print(f"❌ FAILURE: Received 307 Redirect.")
        else:
             print(f"❌ FAILURE: Status {response.status_code}.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_cameras():
    print("\n[TEST] Testing Cameras API (GET /api/cameras)...")
    url = f"{BASE_URL}/api/cameras"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ SUCCESS: /api/cameras returned list with {len(data)} items.")
                print(f"   Sample: {data[0]}")
            else:
                 print(f"❌ FAILURE: Returned empty list or invalid type.")
        else:
            print(f"❌ FAILURE: Status {response.status_code}.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_dashboard_metrics():
    print("\n[TEST] Testing Dashboard Metrics (GET /api/v1/dashboard/metrics)...")
    url = f"{BASE_URL}/api/v1/dashboard/metrics"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            avg_time = data.get("avg_response_time")
            print(f"   avg_response_time: {avg_time}")
            if "m" in str(avg_time) or "—" in str(avg_time):
                 print(f"✅ SUCCESS: Dashboard metrics format looks correct.")
            else:
                 print(f"⚠️ WARNING: Unexpected format for avg_response_time.")
        else:
             print(f"❌ FAILURE: Status {response.status_code}.")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        
if __name__ == "__main__":
    print("Waiting for backend to ensure readiness...")
    time.sleep(2)
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("Backend is UP.")
    except:
        print("Backend seems DOWN, attempting tests anyway...")
    
    test_ai_assist()
    test_incidents_redirect()
    test_cameras()
    test_dashboard_metrics()
