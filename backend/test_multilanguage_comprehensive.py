#!/usr/bin/env python3
"""
Enhanced test script for multi-language chatbot functionality
"""
import requests
import json

def test_multilanguage_chatbot():
    """Test the multi-language chatbot functionality"""
    
    # Get authentication token
    print("Getting authentication token...")
    auth_payload = {
        "email_or_username": "sa@gmail.com",
        "password": "Dev@#123"
    }
    
    auth_response = requests.post(
        "http://localhost:8000/auth/login",
        json=auth_payload
    )
    
    if auth_response.status_code == 200:
        token_data = auth_response.json()
        body_data = json.loads(token_data["body"])
        access_token = body_data["access_token"]
        print(f"✅ Token acquired successfully")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test cases for different languages
        test_cases = [
            {
                "name": "English Test",
                "payload": {
                    "message": "I am feeling very happy today. How can you help me?",
                    "language": "auto",
                    "preferred_response_language": "en"
                }
            },
            {
                "name": "Hindi Test - Request Hindi Response",
                "payload": {
                    "message": "मैं आज बहुत खुश हूं। आप मेरी कैसे मदद कर सकते हैं?",
                    "language": "auto",
                    "preferred_response_language": "hi"
                }
            },
            {
                "name": "Tamil Test - Request Tamil Response", 
                "payload": {
                    "message": "நான் இன்று மிகவும் மகிழ்ச்சியாக இருக்கிறேன்",
                    "language": "auto",
                    "preferred_response_language": "ta"
                }
            },
            {
                "name": "Bengali Test - Request Bengali Response",
                "payload": {
                    "message": "আমি আজ খুব খুশি।",
                    "language": "auto", 
                    "preferred_response_language": "bn"
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n{'='*50}")
            print(f"🧪 {test_case['name']}")
            print(f"{'='*50}")
            
            try:
                chat_response = requests.post(
                    "http://localhost:8004/chat/intelligent",
                    json=test_case["payload"],
                    headers=headers,
                    timeout=30
                )
                
                if chat_response.status_code == 200:
                    response_data = chat_response.json()
                    print(f"✅ Status: {chat_response.status_code}")
                    print(f"📝 Input Message: {test_case['payload']['message']}")
                    print(f"🔍 Detected Language: {response_data.get('detected_language', 'unknown')}")
                    print(f"🗣️ Response Language: {response_data.get('response_language', 'unknown')}")
                    print(f"🔄 Translation Used: {response_data.get('translation_used', False)}")
                    print(f"💬 Response: {response_data.get('response', 'No response')[:200]}...")
                    
                    if response_data.get('follow_up_suggestions'):
                        print(f"💡 Suggestions: {response_data['follow_up_suggestions']}")
                        
                else:
                    print(f"❌ Error Status: {chat_response.status_code}")
                    print(f"❌ Error Response: {chat_response.text}")
                    
            except Exception as e:
                print(f"❌ Error making request: {e}")
                
        # Test voice endpoint
        print(f"\n{'='*50}")
        print(f"🎤 Voice Service Integration Test")
        print(f"{'='*50}")
        
        # Check if voice service is available
        try:
            voice_health = requests.get("http://localhost:8006/health", timeout=5)
            if voice_health.status_code == 200:
                print("✅ Voice service is healthy and ready for integration")
                
                # Test creating a simple audio file simulation
                print("📝 Voice integration is ready for frontend testing")
                print("🎯 Next steps: Test with actual audio files from frontend")
            else:
                print(f"⚠️ Voice service health check failed: {voice_health.status_code}")
        except Exception as e:
            print(f"⚠️ Voice service not accessible: {e}")
            
    else:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        print(f"❌ Auth Response: {auth_response.text}")

if __name__ == "__main__":
    test_multilanguage_chatbot()
