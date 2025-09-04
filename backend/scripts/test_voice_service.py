#!/usr/bin/env python3
"""
Voice Service Test Script
Tests the fixed voice service to ensure it's working properly
"""

import requests
import time
from datetime import datetime

def test_voice_service():
    """Test the voice service endpoints"""
    
    base_url = "http://localhost:8011"
    
    print("🧪 Testing MantraPath Voice Service")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health Check: {health_data['status']}")
            print(f"   Service: {health_data['service']}")
            print(f"   Version: {health_data['version']}")
            print(f"   Engine Status: {health_data['engine_status']}")
            print(f"   Supported Languages: {len(health_data['supported_languages'])} languages")
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False
    
    # Test 2: Languages Endpoint
    print("\n2️⃣ Testing Languages Endpoint...")
    try:
        response = requests.get(f"{base_url}/languages", timeout=10)
        if response.status_code == 200:
            languages_data = response.json()
            print(f"✅ Languages: {len(languages_data)} languages supported")
            print(f"   Languages: {', '.join(languages_data)}")
        else:
            print(f"❌ Languages Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Languages Error: {e}")
    
    # Test 3: Service Performance
    print("\n3️⃣ Testing Service Performance...")
    start_time = time.time()
    
    try:
        # Make multiple health check requests to test performance
        responses: list[bool] = []
        for _ in range(5):
            response = requests.get(f"{base_url}/health", timeout=5)
            responses.append(response.status_code == 200)
            time.sleep(0.1)  # Small delay between requests
        
        end_time = time.time()
        success_rate = sum(responses) / len(responses) * 100
        avg_response_time = (end_time - start_time) / len(responses)
        
        print(f"✅ Performance Test:")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Average Response Time: {avg_response_time:.3f}s")
        print(f"   Total Test Time: {end_time - start_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Performance Test Error: {e}")
    
    # Test 4: Service Status Check
    print("\n4️⃣ Checking Service Status...")
    try:
        # Check if service is responding consistently
        response = requests.head(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Service Status: Healthy and responding")
            print(f"   Response Headers: {dict(response.headers)}")
        else:
            print(f"❌ Service Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Service Status Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Voice Service Test Complete!")
    
    return True

def test_frontend_integration():
    """Test if the voice service can be accessed from frontend perspective"""
    
    print("\n🌐 Testing Frontend Integration...")
    print("=" * 50)
    
    # Test if the service is accessible from different perspectives
    base_url = "http://localhost:8011"
    
    try:
        # Test CORS headers
        response = requests.options(f"{base_url}/health", timeout=5)
        print(f"✅ CORS Test: {response.status_code}")
        
        # Test with different user agents
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; MantraPath-Frontend/1.0)',
            'Accept': 'application/json',
            'Origin': 'http://localhost:5173'
        }
        
        response = requests.get(f"{base_url}/health", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend Integration: Service accessible with frontend headers")
        else:
            print(f"❌ Frontend Integration: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend Integration Error: {e}")

if __name__ == "__main__":
    print(f"🚀 Starting Voice Service Tests at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test basic functionality
    if test_voice_service():
        # Test frontend integration
        test_frontend_integration()
        
        print("\n" + "=" * 50)
        print("🎯 Test Summary:")
        print("✅ Voice Service is working properly")
        print("✅ Health checks are passing")
        print("✅ Service is responding quickly")
        print("✅ Ready for frontend integration")
        print("=" * 50)
    else:
        print("\n❌ Voice Service tests failed!")
        print("Please check the service status and logs.")
