#!/usr/bin/env python3
"""
Test script for chatbot service
"""
import requests
import json

# Test the chatbot service directly (without auth for testing)
def test_chatbot_direct():
    print("🧪 Testing chatbot service directly...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8004/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test status endpoint
    try:
        response = requests.get("http://localhost:8004/api/chatbot/status")
        print(f"✅ Status check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def test_chatbot_via_gateway():
    print("\n🌐 Testing chatbot service via API gateway...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/api/chatbot/health")
        print(f"✅ Gateway health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Gateway health check failed: {e}")
    
    # Test status endpoint
    try:
        response = requests.get("http://localhost:8000/api/chatbot/status")
        print(f"✅ Gateway status check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Gateway status check failed: {e}")

if __name__ == "__main__":
    test_chatbot_direct()
    test_chatbot_via_gateway()
    print("\n🎉 Chatbot service tests completed!")