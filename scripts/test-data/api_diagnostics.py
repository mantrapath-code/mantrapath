#!/usr/bin/env python3
"""
API Diagnostics Script
Tests the actual API responses to identify data structure issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth_helper import get_authenticated_session
import json

def test_api_responses():
    """Test all API endpoints and examine their response structures"""
    print("🔬 Diagnosing API Response Structures...")
    
    try:
        # Get authenticated session
        auth = get_authenticated_session("primary")
        
        # Test endpoints that are failing
        endpoints_to_test = [
            ("/api/v1/mood/", "GET", "Mood Entries"),
            ("/api/v1/journal/", "GET", "Journal Entries"),
            ("/forums/threads", "GET", "Community Posts"),
            ("/ml/personalized-insights/me", "GET", "ML Insights"),
            ("/ml/analyze-patterns/me", "POST", "ML Pattern Analysis")
        ]
        
        for endpoint, method, name in endpoints_to_test:
            print(f"\n📊 Testing {name} ({method} {endpoint})...")
            
            try:
                response = auth.make_request(method, endpoint)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   Response type: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"   Keys: {list(data.keys())}")
                            if len(data) > 0:
                                # Show first key's value type
                                first_key = list(data.keys())[0]
                                print(f"   First value type: {type(data[first_key])}")
                        elif isinstance(data, list):
                            print(f"   List length: {len(data)}")
                            if len(data) > 0:
                                print(f"   First item type: {type(data[0])}")
                                if isinstance(data[0], dict):
                                    print(f"   First item keys: {list(data[0].keys())}")
                        
                        # Show first 200 chars of response
                        response_str = json.dumps(data)[:200]
                        print(f"   Sample: {response_str}...")
                        
                    except json.JSONDecodeError as e:
                        print(f"   ❌ JSON decode error: {e}")
                        print(f"   Raw response: {response.text[:200]}")
                else:
                    print(f"   ❌ Error response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"   ❌ Request error: {e}")
        
        print("\n🎯 Summary of Issues Found:")
        print("   - Check if APIs are returning lists instead of expected dict structures")
        print("   - Verify frontend code handles the actual response format")
        
    except Exception as e:
        print(f"❌ Overall error: {e}")

if __name__ == "__main__":
    test_api_responses()
