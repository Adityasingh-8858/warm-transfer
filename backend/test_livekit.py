#!/usr/bin/env python3
"""
Simple test script to validate LiveKit token generation
"""

import requests
import json
import sys

def test_token_endpoint():
    """Test the token generation endpoint"""
    try:
        # Test health endpoint first
        print("Testing health endpoint...")
        health_response = requests.get("http://localhost:8000/health")
        print(f"Health Status: {health_response.status_code}")
        print(f"Health Response: {health_response.json()}")
        print()
        
        # Test token generation
        print("Testing token generation...")
        token_response = requests.get(
            "http://localhost:8000/get-token",
            params={
                "room_name": "test-room",
                "identity": "test-user"
            }
        )
        
        print(f"Token Status: {token_response.status_code}")
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            print(f"Token Response: {json.dumps(token_data, indent=2)}")
            
            # Basic validation
            if "accessToken" in token_data:
                token = token_data["accessToken"]
                print(f"Token length: {len(token)} characters")
                print("✅ Token generation successful!")
                return True
            else:
                print("❌ Access token not found in response")
                return False
        else:
            print(f"❌ Token generation failed: {token_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server at http://localhost:8000")
        print("Make sure the backend server is running!")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_rooms_endpoint():
    """Test the rooms listing endpoint"""
    try:
        print("\nTesting rooms endpoint...")
        rooms_response = requests.get("http://localhost:8000/rooms")
        print(f"Rooms Status: {rooms_response.status_code}")
        
        if rooms_response.status_code == 200:
            rooms_data = rooms_response.json()
            print(f"Rooms Response: {json.dumps(rooms_data, indent=2)}")
            print("✅ Rooms listing successful!")
            return True
        else:
            print(f"❌ Rooms listing failed: {rooms_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing rooms endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 LiveKit Integration Test")
    print("=" * 40)
    
    success = True
    
    # Test token generation
    if not test_token_endpoint():
        success = False
    
    # Test rooms endpoint
    if not test_rooms_endpoint():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 All tests passed! LiveKit integration is working properly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    sys.exit(0 if success else 1)