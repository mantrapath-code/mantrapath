#!/usr/bin/env python3
"""
Test script to verify PHI4 integration with the chatbot service
"""
import requests

# Test the chatbot endpoint
def test_chatbot():
    url = "http://localhost:8004/api/chatbot/test"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing PHI4 chatbot endpoint...")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success!")
            print(f"Status: {result['status']}")
            print(f"PHI4 Working: {result['phi4_working']}")
            print(f"Source: {result['source']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Message: {result['message']}")
            print(f"\nResponse sample: {result['response'][:100]}...")
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("\n⚠️ Request timed out")
        return False
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return False

def test_health():
    url = "http://localhost:8004/health"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("\n📊 Health Status:")
            print(f"Status: {result['status']}")
            print(f"PHI4 Available: {result['phi4_available']}")
            print(f"OpenAI Available: {result['openai_available']}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Testing MantraPath Chatbot with PHI4 Integration")
    print("=" * 50)
    
    # Test health first
    if test_health():
        print("\n" + "=" * 50)
        # Test chatbot
        test_chatbot()
    else:
        print("❌ Health check failed, skipping chatbot test")
