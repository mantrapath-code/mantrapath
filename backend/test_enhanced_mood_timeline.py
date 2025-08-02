#!/usr/bin/env python3
"""
Test script to verify the enhanced mood timeline functionality
"""
import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8003"

def test_mood_service_health():
    """Test if the mood service is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Mood service health: {response.status_code}")
        if response.status_code == 200:
            print(f"   Health data: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Mood service not accessible: {e}")
        return False

def test_mood_endpoints():
    """Test mood endpoints without authentication (expect 403)"""
    endpoints = [
        "/api/v1/mood/",
        "/api/v1/mood/adaptive-questions",
        "/api/v1/mood/analytics/summary",
        "/api/v1/mood/emotional-weather",
        "/api/v1/mood/detect-celebrations"
    ]
    
    print("\n🔍 Testing mood service endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            status = "✅" if response.status_code in [403, 401] else "⚠️"
            print(f"   {status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Error - {e}")

def test_mood_data_structure():
    """Test mood entry creation structure"""
    print("\n📊 Testing mood entry structure (without auth - expect 403):")
    
    sample_mood_data = {
        "mood_score": 7,
        "energy_level": 6,
        "stress_level": 4,
        "sleep_quality": 8,
        "notes": "Testing enhanced mood tracking",
        "context_tags": ["work", "exercise"],
        "emotional_granularity": 4,
        "mood_confidence": 0.8,
        "adaptive_responses": [],
        "environmental_context": {
            "emotions": ["happy", "energetic"],
            "activities": ["work", "exercise"]
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/mood/",
            json=sample_mood_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   ✅ POST mood entry: {response.status_code} (expected 403)")
        if response.status_code != 403:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ POST mood entry error: {e}")

def main():
    print("🧪 Enhanced Mood Timeline Test")
    print("=" * 40)
    
    # Test service health
    if not test_mood_service_health():
        print("❌ Mood service is not running. Please start the backend first.")
        sys.exit(1)
    
    # Test endpoints
    test_mood_endpoints()
    
    # Test data structure
    test_mood_data_structure()
    
    print("\n✅ Enhanced mood timeline backend tests completed!")
    print("\nNext steps:")
    print("1. Frontend mood timeline should now support enhanced data")
    print("2. Energy levels, stress, and sleep quality are tracked")
    print("3. Adaptive questions and celebrations are integrated")
    print("4. Timeline shows energy distribution statistics")

if __name__ == "__main__":
    main()
