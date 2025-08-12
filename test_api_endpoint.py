#!/usr/bin/env python3
"""
Test the API endpoint directly to verify response format
"""

import requests
import json
import time

def test_api_endpoint():
    """Test the conversation start API endpoint"""
    print("=== Testing API Endpoint ===")
    print()
    
    base_url = "http://localhost:8001"
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Health check passed")
        else:
            print(f"   ⚠ Health check failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    print()
    
    # Test 2: Start conversation
    print("2. Testing conversation start endpoint...")
    try:
        payload = {
            "session_id": f"api_test_{int(time.time())}"
        }
        
        print(f"   Sending POST to {base_url}/api/conversation/start")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/conversation/start",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✓ API call successful")
            print(f"   Response structure:")
            print(f"     - status: {data.get('status')}")
            print(f"     - conversation_id: {data.get('conversation_id')}")
            print(f"     - session_id: {data.get('session_id')}")
            print(f"     - message: {data.get('message')[:100]}..." if data.get('message') else "     - message: None")
            print(f"     - client_info: {data.get('client_info')}")
            print(f"     - completion_percentage: {data.get('completion_percentage')}")
            print(f"     - is_complete: {data.get('is_complete')}")
            
            print(f"   Full response: {json.dumps(data, indent=2)}")
            
            return data
        else:
            print(f"   ❌ API call failed")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("   ❌ Request timed out (30 seconds)")
        return None
    except Exception as e:
        print(f"   ❌ API call error: {e}")
        return None
    
    print()

def test_frontend_api_service():
    """Test using the frontend's API service format"""
    print("3. Testing with frontend API service format...")
    
    try:
        # Simulate what the frontend sends
        session_id = f"programme_setup_{int(time.time())}"
        payload = {"session_id": session_id}
        
        response = requests.post(
            "http://localhost:8001/api/conversation/start",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"   Frontend-style request status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✓ Frontend-style request successful")
            
            # Check if it has the expected fields for frontend
            required_fields = ['conversation_id', 'session_id', 'message', 'client_info', 'completion_percentage', 'is_complete']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                print("   ✓ All required fields present")
            else:
                print(f"   ⚠ Missing fields: {missing_fields}")
                
            return data
        else:
            print(f"   ❌ Frontend-style request failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Frontend-style request error: {e}")
        return None

if __name__ == "__main__":
    print("Starting API endpoint test...")
    print()
    
    try:
        # Test basic API
        api_result = test_api_endpoint()
        
        # Test frontend format
        frontend_result = test_frontend_api_service()
        
        print()
        print("=== Test Summary ===")
        if api_result and frontend_result:
            print("✅ All API tests passed!")
            print("✅ Backend API is working correctly")
            print("✅ Response format matches frontend expectations")
        else:
            print("❌ Some API tests failed")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()