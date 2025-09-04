#!/usr/bin/env python3
"""
Test script for Models Service capabilities
"""

import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8085"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_status():
    """Test status endpoint"""
    print("🔍 Testing Status Endpoint...")
    response = requests.get(f"{BASE_URL}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_stt_languages():
    """Test STT languages"""
    print("🔍 Testing STT Languages...")
    response = requests.get(f"{BASE_URL}/api/v1/stt/languages")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_tts_languages():
    """Test TTS languages"""
    print("🔍 Testing TTS Languages...")
    response = requests.get(f"{BASE_URL}/api/v1/tts/languages")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_tts_synthesis():
    """Test TTS synthesis"""
    print("🔍 Testing TTS Synthesis...")
    
    # English test
    payload = {
        "text": "Hello, I am MantraPath voice service",
        "language": "en",
        "model_preference": "espeak_en"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/tts/synthesize",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"English TTS - Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content Type: {response.headers.get('content-type')}")
        print(f"Response Length: {len(response.content)} bytes")
    print()
    
    # Hindi test
    payload_hi = {
        "text": "नमस्ते, मैं मंत्रपथ हूं",
        "language": "hi",
        "model_preference": "espeak_hi"
    }
    
    response_hi = requests.post(
        f"{BASE_URL}/api/v1/tts/synthesize",
        json=payload_hi,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Hindi TTS - Status: {response_hi.status_code}")
    try:
        print(f"Response: {json.dumps(response_hi.json(), indent=2)}")
    except:
        print(f"Response Headers: {dict(response_hi.headers)}")
        print(f"Response Content Type: {response_hi.headers.get('content-type')}")
        print(f"Response Length: {len(response_hi.content)} bytes")
    print()

def test_sentiment_analysis():
    """Test sentiment analysis"""
    print("🔍 Testing Sentiment Analysis...")
    
    payload = {
        "text": "I am very happy with this service!",
        "language": "en"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/nlp/sentiment",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text[:200]}...")
    print()

def test_translation():
    """Test translation"""
    print("🔍 Testing Translation...")
    
    payload = {
        "text": "Hello, how are you?",
        "source_lang": "en",
        "target_lang": "hi"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/nlp/translate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text[:200]}...")
    print()

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 MODELS SERVICE CAPABILITY TESTING")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_status()
        test_stt_languages()
        test_tts_languages()
        test_tts_synthesis()
        test_sentiment_analysis()
        test_translation()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Models Service. Make sure it's running on port 8085")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
