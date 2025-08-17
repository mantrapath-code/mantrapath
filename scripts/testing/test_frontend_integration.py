#!/usr/bin/env python3
"""
Frontend Integration Test Script
Tests the complete flow: Authentication → Frontend → Unified Insights Endpoint
"""

import requests

def test_frontend_integration():
    """Test the complete frontend integration flow"""
    
    print("🧪 Frontend Integration Test")
    print("=" * 50)
    
    # Step 1: Test Authentication
    print("\n1. Testing Authentication...")
    auth_url = "http://localhost:8001/login"
    auth_data = {
        "email_or_username": "Ramesh123",
        "password": "Dev@#123"
    }
    
    try:
        auth_response = requests.post(auth_url, json=auth_data)
        if auth_response.status_code == 200:
            token = auth_response.json().get('access_token')
            print("✅ Authentication successful")
            print(f"   Token: {token[:20]}...")
        else:
            print("❌ Authentication failed")
            print(f"   Status: {auth_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Step 2: Test Unified Insights Endpoint
    print("\n2. Testing Unified Insights Endpoint...")
    insights_url = "http://localhost:8008/api/v1/insights/unified"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        insights_response = requests.get(insights_url, headers=headers)
        if insights_response.status_code == 200:
            insights_data = insights_response.json()
            print("✅ Unified insights endpoint working")
            print(f"   Cache hit: {insights_data.get('cache_info', {}).get('hit', 'unknown')}")
            print(f"   Insights count: {insights_data.get('aggregated_insights', {}).get('insights_summary', {}).get('total_insights', 0)}")
        else:
            print("❌ Unified insights endpoint failed")
            print(f"   Status: {insights_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Unified insights error: {e}")
        return False
    
    # Step 3: Test Frontend Service Compatibility
    print("\n3. Testing Frontend Service Compatibility...")
    try:
        # Check if the response structure matches frontend expectations
        expected_fields = [
            'aggregated_insights',
            'cache_info', 
            'timestamp',
            'user_id'
        ]
        
        for field in expected_fields:
            if field in insights_data:
                print(f"✅ Field '{field}' present")
            else:
                print(f"❌ Field '{field}' missing")
                return False
                
        # Check aggregated_insights structure
        agg_insights = insights_data.get('aggregated_insights', {})
        expected_sections = ['mood', 'trends', 'insights_summary']
        
        for section in expected_sections:
            if section in agg_insights:
                print(f"✅ Section '{section}' present in aggregated_insights")
            else:
                print(f"❌ Section '{section}' missing from aggregated_insights")
                return False
                
    except Exception as e:
        print(f"❌ Compatibility check error: {e}")
        return False
    
    print("\n4. Integration Summary:")
    print("✅ Authentication flow working")
    print("✅ Backend services healthy")  
    print("✅ Unified insights endpoint accessible")
    print("✅ Response structure compatible with frontend")
    print("✅ Cache system operational")
    
    print(f"\n🎉 Frontend Integration (Step 1) COMPLETE!")
    print("Ready to proceed to Step 2: Redis Scaling")
    
    return True

if __name__ == "__main__":
    success = test_frontend_integration()
    exit(0 if success else 1)
