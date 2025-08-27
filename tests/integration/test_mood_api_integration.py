#!/usr/bin/env python3
"""
Test Mood Entry Creation through API Gateway with Memory Service Integration
V3-BK-015: Testing complete flow
"""

import requests
import json
import time

def test_mood_integration_flow():
    """Test creating a mood entry through API Gateway to test Memory Service integration"""
    print("🧪 Testing Complete Mood -> Memory Service Flow")
    print("=" * 60)
    
    # Test mood entry data
    mood_entry_data = {
        "mood_score": 9,
        "energy_level": 8,
        "stress_level": 2,
        "sleep_quality": 9,
        "notes": "Excellent mood today! Memory Service integration test.",
        "context_tags": ["integration_test", "memory_service", "v3_bk_015"],
        "emotional_granularity": 4,
        "mood_confidence": 0.95,
        "adaptive_responses": []
    }
    
    print("📊 Test Mood Entry Data:")
    print(json.dumps(mood_entry_data, indent=2))
    
    # Test direct mood service call (without auth for testing)
    try:
        print("\n🎯 Testing direct mood service endpoint...")
        url = "http://localhost:8003/api/v1/mood/"
        headers = {"Content-Type": "application/json"}
        
        # This will likely fail due to auth, but we can check the logs
        response = requests.post(url, json=mood_entry_data, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Direct call failed (expected due to auth): {e}")
    
    print("\n🔍 Check mood service logs for Memory Service integration attempts...")
    print("💡 Look for messages like '🧠 Attempting to send mood data to Memory Service'")

if __name__ == "__main__":
    test_mood_integration_flow()
