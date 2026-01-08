#!/usr/bin/env python
"""
Integration test script to verify all systems working.
Run this AFTER starting both backend and frontend.
"""
import asyncio
import json
import time
from datetime import datetime
import sys

def print_section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)

async def test_backend_health():
    """Test backend health endpoint"""
    print_section("Testing Backend Health")
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/ai/health")
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def test_incidents_endpoint():
    """Test incidents list endpoint"""
    print_section("Testing Incidents Endpoint")
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/incidents?limit=5")
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total incidents: {data.get('total', 0)}")
            
            incidents = data.get('incidents', [])
            if incidents:
                print(f"\nFirst incident:")
                inc = incidents[0]
                print(f"  ID: {inc.get('incident_id')}")
                print(f"  Type: {inc.get('incident_type')}")
                print(f"  Location: {inc.get('location')}")
                print(f"  Severity: {inc.get('severity')}")
                print(f"  Timestamp: {inc.get('timestamp')}")
            
            return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def test_ai_chat():
    """Test AI chat endpoint"""
    print_section("Testing AI Chat Endpoint")
    
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            payload = {
                "query": "What is the status of recent incidents?",
                "history": []
            }
            response = await client.post(
                "http://localhost:8000/api/v1/ai/chat",
                json=payload
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Response:")
            print(f"  Reply: {data.get('reply', 'NO REPLY')[:100]}...")
            print(f"  Confidence: {data.get('confidence', 0)}")
            print(f"  Sources: {len(data.get('sources', []))} items")
            
            return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def test_create_incident():
    """Test incident creation"""
    print_section("Testing Incident Creation")
    
    try:
        import httpx
        payload = {
            "incident_type": "test_incident",
            "location": "Test Building",
            "severity": "MEDIUM",
            "description": "Integration test incident"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/incidents",
                json=payload
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            
            if response.status_code == 201:
                print(f"Created incident ID: {data.get('incident_id')}")
                print(f"Type: {data.get('incident_type')}")
                print(f"Location: {data.get('location')}")
                print(f"Severity: {data.get('severity')}")
                return True
            else:
                print(f"Error: {data}")
                return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def check_startup_logs():
    """Check if startup logs show all services initialized"""
    print_section("Checking Startup Logs")
    
    try:
        with open("logs/campusshield.log", "r") as f:
            logs = f.read()
        
        checks = [
            ("Database", "database" in logs.lower()),
            ("LLM Provider", "llm" in logs.lower()),
            ("CORS", "cors" in logs.lower()),
            ("Logging", "logging" in logs.lower()),
        ]
        
        for check, passed in checks:
            status = "OK" if passed else "MISSING"
            print(f"  {check}: {status}")
        
        return all(passed for _, passed in checks)
    except FileNotFoundError:
        print("  Log file not found - backend may not have been started")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

async def main():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("  CAMPUSSHIELD AI - INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"Test started: {datetime.now().isoformat()}")
    print("\nMake sure backend is running on port 8000!")
    
    # Give user time to start backend if needed
    input("\nPress ENTER to start tests...")
    
    results = {}
    
    # Test backend health
    try:
        results["Backend Health"] = await test_backend_health()
    except:
        results["Backend Health"] = False
    
    time.sleep(0.5)
    
    # Test incidents endpoint
    try:
        results["Incidents List"] = await test_incidents_endpoint()
    except:
        results["Incidents List"] = False
    
    time.sleep(0.5)
    
    # Test AI chat
    try:
        results["AI Chat"] = await test_ai_chat()
    except:
        results["AI Chat"] = False
    
    time.sleep(0.5)
    
    # Test incident creation
    try:
        results["Create Incident"] = await test_create_incident()
    except:
        results["Create Incident"] = False
    
    # Check logs
    results["Startup Logs"] = check_startup_logs()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("RESULT: ALL TESTS PASSED - SYSTEM IS READY")
        print("=" * 60)
        return 0
    else:
        print("RESULT: SOME TESTS FAILED - REVIEW ABOVE")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        sys.exit(1)
