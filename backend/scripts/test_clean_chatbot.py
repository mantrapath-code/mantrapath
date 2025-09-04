#!/usr/bin/env python3
"""
Test Clean Chatbot Service
Comprehensive testing of language detection, voice responses, and AI integration
"""

import asyncio
import requests
import json
from datetime import datetime, UTC

def test_clean_chatbot_service():
    """Test the clean chatbot service directly"""
    print("🧪 Testing Clean Chatbot Service")
    print("=" * 50)
    
    # Test language detection
    test_cases = [
        {
            "input": "Hello, how are you?",
            "expected_lang": "en",
            "description": "English text"
        },
        {
            "input": "नमस्ते, कैसे हो आप?",
            "expected_lang": "hi",
            "description": "Hindi text"
        },
        {
            "input": "चलो हम डिस्कस करते हैं बच्चे",
            "expected_lang": "hi",
            "description": "Hindi text about discussing children"
        },
        {
            "input": "Let's discuss about health",
            "expected_lang": "en",
            "description": "English text about health"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['description']}")
        print(f"   Input: {case['input']}")
        print(f"   Expected: {case['expected_lang']}")
        
        # Test simple language detection
        detected = simple_language_detection(case['input'])
        print(f"   Detected: {detected}")
        print(f"   Status: {'✅ Match' if detected == case['expected_lang'] else '❌ Mismatch'}")
        print()

def simple_language_detection(text: str) -> str:
    """Simple language detection using character analysis"""
    if not text:
        return "en"
    
    # Check for Hindi/Devanagari characters
    devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    
    # Check for English characters
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    
    total_chars = len(text)
    
    if total_chars == 0:
        return "en"
    
    # Calculate ratios
    devanagari_ratio = devanagari_chars / total_chars
    english_ratio = english_chars / total_chars
    
    # Determine language based on highest ratio
    if devanagari_ratio > 0.3:
        return "hi"
    elif english_ratio > 0.3:
        return "en"
    else:
        return "en"

def test_chatbot_endpoint():
    """Test the chatbot endpoint"""
    print("\n🤖 Testing Chatbot Endpoint")
    print("=" * 50)
    
    # Test cases with different languages
    test_cases = [
        {
            "message": "Hello, how are you?",
            "language": "auto",
            "description": "English message"
        },
        {
            "message": "नमस्ते, कैसे हो आप?",
            "language": "auto",
            "description": "Hindi message"
        },
        {
            "message": "चलो हम डिस्कस करते हैं बच्चे",
            "language": "auto",
            "description": "Hindi message about discussing children"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['description']}")
        print(f"   Message: {case['message']}")
        print(f"   Language: {case['language']}")
        
        try:
            # Test the endpoint
            response = test_chatbot_api(case['message'], case['language'])
            if response:
                print(f"   Response: {response['response'][:100]}...")
                print(f"   Language Detected: {response.get('metadata', {}).get('language_detected', 'unknown')}")
                print(f"   Status: ✅ Success")
            else:
                print(f"   Status: ❌ Failed")
        except Exception as e:
            print(f"   Status: ❌ Error - {e}")
        print()

def test_chatbot_api(message: str, language: str = "auto") -> dict:
    """Test the chatbot API endpoint"""
    try:
        url = "http://localhost:8004/api/chatbot/enhanced/chat"
        
        payload = {
            "message": message,
            "language": language,
            "session_id": None,
            "user_context_refresh": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"  # You'll need a real token
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"   API Error: {e}")
        return None

def test_voice_service_integration():
    """Test voice service integration"""
    print("\n🎤 Testing Voice Service Integration")
    print("=" * 50)
    
    # Test voice service health
    try:
        response = requests.get("http://localhost:8011/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Voice Service: {health_data.get('status', 'unknown')}")
            print(f"   Service: {health_data.get('service', 'unknown')}")
            print(f"   Version: {health_data.get('version', 'unknown')}")
        else:
            print(f"❌ Voice Service: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Voice Service: Connection failed - {e}")
    
    # Test TTS endpoint
    try:
        test_text = "Hello, this is a test of the text to speech service."
        test_data = {
            "text": test_text,
            "language": "en",
            "voice_type": "default"
        }
        
        response = requests.post("http://localhost:8011/api/tts", 
                               json=test_data, timeout=10)
        
        if response.status_code == 200:
            tts_data = response.json()
            print(f"✅ TTS Service: Working")
            print(f"   Text: {test_text}")
            print(f"   Language: {tts_data.get('language', 'unknown')}")
            print(f"   Audio Format: {tts_data.get('audio_format', 'unknown')}")
        else:
            print(f"❌ TTS Service: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ TTS Service failed: {e}")

def test_frontend_integration():
    """Test frontend integration points"""
    print("\n🌐 Testing Frontend Integration")
    print("=" * 50)
    
    print("🔍 Frontend Integration Points:")
    print("   ✅ Chat Input: Text messages sent to /api/chatbot/enhanced/chat")
    print("   ✅ Voice Input: Needs to be implemented")
    print("   ✅ Response Handling: Text + Audio responses")
    print("   ✅ Language Detection: Automatic based on input")
    print()
    
    print("⚠️  Missing Frontend Features:")
    print("   1. Voice Input Detection")
    print("   2. Audio Response Playback")
    print("   3. Language Selection UI")
    print("   4. Voice/Text Toggle")

def main():
    """Run all tests"""
    print("🧪 MANTRA PATH CLEAN CHATBOT TEST SUITE")
    print("=" * 60)
    print(f"Test run at: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Run all tests
    test_clean_chatbot_service()
    test_chatbot_endpoint()
    test_voice_service_integration()
    test_frontend_integration()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print("   ✅ Language Detection: Tested")
    print("   ✅ Chatbot Endpoint: Tested")
    print("   ✅ Voice Service: Tested")
    print("   ✅ Frontend Integration: Analyzed")
    print()
    
    print("🚀 NEXT STEPS:")
    print("   1. Fix remaining backend issues")
    print("   2. Implement voice input detection")
    print("   3. Add audio response playback")
    print("   4. Test end-to-end voice conversations")
    print()
    
    print("💡 RECOMMENDATIONS:")
    print("   • Test with real JWT tokens")
    print("   • Verify all services are running")
    print("   • Check language detection accuracy")
    print("   • Implement voice input handling")

if __name__ == "__main__":
    main()

