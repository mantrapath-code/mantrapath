#!/usr/bin/env python3
"""
Test script for language preferences API endpoints
Tests GET and PUT operations with user Ramesh (Dev@#123)
"""

import requests
import json
from .config import PROFILE_BASE, AUTH_BASE

# Configuration
BASE_URL = PROFILE_BASE  # Resolved via test config (no hardcoded localhost)
TEST_USER = {
    "email_or_username": "mydreems2good@gmail.com",
    "password": "Dev@#123"
}

def get_auth_token():
    """Get JWT token for test user from auth service (dynamic URL)"""
    auth_url = f"{AUTH_BASE}/login"  # Auth service may expose login at root
    
    try:
        response = requests.post(auth_url, json=TEST_USER)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Auth failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Auth request failed: {e}")
        return None

def test_language_preferences():
    """Test language preferences endpoints"""
    print("🧪 Testing Language Preferences API...")
    
    # Get auth token
    print("1. Getting auth token...")
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without auth token")
        return False
    
    print(f"✅ Got token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test GET endpoint
    print("\n2. Testing GET /api/profile/language-preferences...")
    try:
        response = requests.get(f"{BASE_URL}/api/profile/language-preferences", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GET successful: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ GET failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ GET request failed: {e}")
        return False
    
    # Test PUT endpoint - update preferences
    print("\n3. Testing PUT /api/profile/language-preferences...")
    update_data = {
        "primary_language": "hi",  # Change to Hindi
        "secondary_languages": ["en", "ta", "ur"],  # Add Urdu
        "auto_detect_language": False,
        "cultural_region": "IN"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/profile/language-preferences", 
            headers=headers,
            json=update_data
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PUT successful: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ PUT failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ PUT request failed: {e}")
        return False
    
    # Test GET again to verify changes
    print("\n4. Verifying changes with GET...")
    try:
        response = requests.get(f"{BASE_URL}/api/profile/language-preferences", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Verification successful: {json.dumps(data, indent=2)}")
            
            # Validate expected changes
            expected = {
                "primary_language": "hi",
                "secondary_languages": ["en", "ta", "ur"],
                "auto_detect_language": False,
                "cultural_region": "IN"
            }
            
            success = True
            for key, expected_value in expected.items():
                if data.get(key) != expected_value:
                    print(f"❌ Mismatch in {key}: expected {expected_value}, got {data.get(key)}")
                    success = False
            
            if success:
                print("✅ All fields updated correctly!")
            
            return success
        else:
            print(f"❌ Verification GET failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Verification request failed: {e}")
        return False

def test_validation():
    """Test validation of language preferences"""
    print("\n🧪 Testing validation...")
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test invalid language code
    invalid_data = {
        "primary_language": "xyz",  # Invalid code
        "secondary_languages": ["en", "invalid_lang"],
        "cultural_region": "INVALID"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/profile/language-preferences", 
            headers=headers,
            json=invalid_data
        )
        if response.status_code == 422:  # Validation error expected
            print(f"✅ Validation working: {response.status_code}")
            print(f"   Error details: {response.json()}")
            return True
        else:
            print(f"❌ Expected validation error, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Language Preferences API Test")
    print("=" * 60)
    
    # Test basic functionality
    success1 = test_language_preferences()
    
    # Test validation
    success2 = test_validation()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
