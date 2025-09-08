#!/usr/bin/env python3
"""
Quick test script for translation service error handling
Tests the specific failing cases mentioned by the user
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8010"

def test_health():
    """Test if service is available"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Service is healthy")
            return True
        else:
            print(f"❌ Service returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        return False

def test_error_cases():
    """Test the specific error handling cases that are failing"""
    
    tests = [
        {
            "name": "Error Handling - Empty Text",
            "data": {"text": "", "target_language": "hi"},
            "expected_behavior": "Should handle empty text gracefully"
        },
        {
            "name": "Error Handling - Unsupported Target Language", 
            "data": {"text": "Hello world", "target_language": "xyz"},
            "expected_behavior": "Should handle unsupported language gracefully"
        },
        {
            "name": "Error Handling - Missing Text Field",
            "data": {"target_language": "hi"},
            "expected_behavior": "Should return validation error for missing text"
        },
        {
            "name": "Error Handling - Missing Target Language",
            "data": {"text": "Hello world"},
            "expected_behavior": "Should auto-detect and use default or return error"
        }
    ]
    
    print("\n🧪 ERROR HANDLING TESTS")
    print("=" * 50)
    
    for i, test in enumerate(tests, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Data: {test['data']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/translate",
                json=test['data'],
                timeout=10
            )
            
            print(f"  Status Code: {response.status_code}")
            
            try:
                result = response.json()
                print(f"  Response: {result}")
                
                # Analyze the response
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS - Service handled gracefully")
                elif response.status_code == 422:
                    print(f"  ✅ SUCCESS - Proper validation error")
                elif response.status_code == 400:
                    print(f"  ✅ SUCCESS - Proper client error")
                else:
                    print(f"  ❌ UNEXPECTED - Status {response.status_code}")
                    
            except json.JSONDecodeError:
                print(f"  Response text: {response.text}")
                print(f"  ❌ FAILED - Invalid JSON response")
                
        except requests.exceptions.Timeout:
            print(f"  ❌ FAILED - Request timeout")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ FAILED - Connection error")
        except Exception as e:
            print(f"  ❌ FAILED - Unknown error: {e}")
        
        print()

def test_language_detection_errors():
    """Test language detection error cases"""
    
    tests = [
        {
            "name": "Language Detection - Empty Text",
            "data": {"text": ""},
            "expected_behavior": "Should handle empty text gracefully"
        },
        {
            "name": "Language Detection - Very Short Text",
            "data": {"text": "a"},
            "expected_behavior": "Should handle short text gracefully"
        },
        {
            "name": "Language Detection - Numbers Only",
            "data": {"text": "12345"},
            "expected_behavior": "Should handle numbers gracefully"
        }
    ]
    
    print("\n🧪 LANGUAGE DETECTION ERROR TESTS")
    print("=" * 50)
    
    for i, test in enumerate(tests, 1):
        print(f"Test {i}: {test['name']}")
        print(f"  Data: {test['data']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/detect-language",
                json=test['data'],
                timeout=10
            )
            
            print(f"  Status Code: {response.status_code}")
            
            try:
                result = response.json()
                print(f"  Response: {result}")
                
                if response.status_code == 200:
                    print(f"  ✅ SUCCESS - Service handled gracefully")
                elif response.status_code == 422:
                    print(f"  ✅ SUCCESS - Proper validation error")
                else:
                    print(f"  ❌ UNEXPECTED - Status {response.status_code}")
                    
            except json.JSONDecodeError:
                print(f"  Response text: {response.text}")
                print(f"  ❌ FAILED - Invalid JSON response")
                
        except Exception as e:
            print(f"  ❌ FAILED - Error: {e}")
        
        print()

def main():
    print("🔧 TRANSLATION SERVICE ERROR HANDLING TESTS")
    print("=" * 60)
    
    # Check if service is available
    if not test_health():
        print("❌ Service is not available. Please start the translation service first.")
        sys.exit(1)
    
    # Test error cases
    test_error_cases()
    test_language_detection_errors()
    
    print("\n✅ Error handling tests completed!")

if __name__ == "__main__":
    main()
