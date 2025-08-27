"""
Test script for language preferences API endpoints
Tests GET and PUT operations with user Ramesh (Dev@#123)
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8002"  # Profile service port
TEST_USER = {
    "username": "Ramesh",
    "password": "Dev@#123"
}

def create_test_user() -> Dict[str, Any]:
    """Create a test user and return auth token"""
    # First try to register
    register_data = {
        "email": TEST_USER_EMAIL,
        "username": "testuser",
        "password": TEST_USER_PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    }
    
    # Try registration (might fail if user exists)
    try:
        response = requests.post(f"http://localhost:8001/api/auth/register", json=register_data)
        print(f"Registration: {response.status_code}")
    except:
        print("Registration failed or user exists")
    
    # Login to get token
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"http://localhost:8001/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_language_preferences():
    """Test language preference CRUD operations"""
    print("=== Language Preferences API Test ===")
    
    # Get auth token
    auth_result = create_test_user()
    if not auth_result:
        print("❌ Failed to authenticate")
        return False
    
    headers = {"Authorization": f"Bearer {auth_result['access_token']}"}
    
    # Test 1: Get default language preferences
    print("\n1. Testing GET /api/profile/language-preferences (default)")
    response = requests.get(f"{BASE_URL}/api/profile/language-preferences", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        default_prefs = response.json()
        print(f"Default preferences: {json.dumps(default_prefs, indent=2)}")
        assert default_prefs['primary_language'] == 'en'
        assert default_prefs['secondary_languages'] == []
        assert default_prefs['auto_detect_language'] == True
        print("✅ Default preferences correct")
    else:
        print(f"❌ Failed: {response.text}")
        return False
    
    # Test 2: Update with Indian languages
    print("\n2. Testing PUT /api/profile/language-preferences (Indian languages)")
    update_data = {
        "primary_language": "hi",  # Hindi
        "secondary_languages": ["ta", "te", "mr"],  # Tamil, Telugu, Marathi
        "auto_detect_language": False,
        "cultural_region": "IN"
    }
    
    response = requests.put(f"{BASE_URL}/api/profile/language-preferences", 
                          json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated_prefs = response.json()
        print(f"Updated preferences: {json.dumps(updated_prefs, indent=2)}")
        assert updated_prefs['primary_language'] == 'hi'
        assert set(updated_prefs['secondary_languages']) == {'ta', 'te', 'mr'}
        assert updated_prefs['auto_detect_language'] == False
        assert updated_prefs['cultural_region'] == 'IN'
        print("✅ Update successful")
    else:
        print(f"❌ Failed: {response.text}")
        return False
    
    # Test 3: Test normalization (typos/common names)
    print("\n3. Testing language normalization")
    normalize_data = {
        "primary_language": "hindi",  # Should normalize to 'hi'
        "secondary_languages": ["tamil", "telugu", "marathi"],  # Should normalize
        "cultural_region": "in"  # Should uppercase to 'IN'
    }
    
    response = requests.put(f"{BASE_URL}/api/profile/language-preferences", 
                          json=normalize_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        normalized_prefs = response.json()
        print(f"Normalized preferences: {json.dumps(normalized_prefs, indent=2)}")
        assert normalized_prefs['primary_language'] == 'hi'
        assert set(normalized_prefs['secondary_languages']) == {'ta', 'te', 'mr'}
        assert normalized_prefs['cultural_region'] == 'IN'
        print("✅ Normalization working")
    else:
        print(f"❌ Failed: {response.text}")
        return False
    
    # Test 4: Test validation (invalid language)
    print("\n4. Testing validation (invalid language)")
    invalid_data = {
        "primary_language": "xyz",  # Invalid language
    }
    
    response = requests.put(f"{BASE_URL}/api/profile/language-preferences", 
                          json=invalid_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 422:  # Validation error expected
        print("✅ Validation working - rejected invalid language")
    else:
        print(f"❌ Validation failed - should have rejected: {response.text}")
        return False
    
    # Test 5: Test Arabic + region
    print("\n5. Testing Arabic language with Middle East region")
    arabic_data = {
        "primary_language": "ar",
        "secondary_languages": ["en"],
        "cultural_region": "AE"
    }
    
    response = requests.put(f"{BASE_URL}/api/profile/language-preferences", 
                          json=arabic_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        arabic_prefs = response.json()
        print(f"Arabic preferences: {json.dumps(arabic_prefs, indent=2)}")
        assert arabic_prefs['primary_language'] == 'ar'
        assert arabic_prefs['cultural_region'] == 'AE'
        print("✅ Arabic language support working")
    else:
        print(f"❌ Failed: {response.text}")
        return False
    
    # Test 6: Final verification - GET updated preferences
    print("\n6. Final verification GET")
    response = requests.get(f"{BASE_URL}/api/profile/language-preferences", headers=headers)
    if response.status_code == 200:
        final_prefs = response.json()
        print(f"Final preferences: {json.dumps(final_prefs, indent=2)}")
        print("✅ Round-trip test complete")
    else:
        print(f"❌ Failed: {response.text}")
        return False
    
    print("\n🎉 All language preference tests passed!")
    return True

if __name__ == "__main__":
    test_language_preferences()
