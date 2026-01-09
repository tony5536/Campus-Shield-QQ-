import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_cameras():
    print("\n--- Testing Cameras Endpoint ---")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/cameras")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            cameras = response.json()
            print(f"Cameras Found: {len(cameras)}")
            for cam in cameras:
                print(f"  - {cam.get('id')}: {cam.get('name')} ({cam.get('status')})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_ai_analyze():
    print("\n--- Testing AI Analyze Endpoint ---")
    payload = {"query": "Unauthorized person detection in lobby"}
    try:
        # Testing the legacy endpoint used by frontend (now via v1 alias)
        response = requests.post(f"{BASE_URL}/api/v1/ai/analyze", json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", json.dumps(response.json(), indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_cameras()
    test_ai_analyze()
