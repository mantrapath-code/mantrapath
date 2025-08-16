#!/usr/bin/env python3
"""
MantraPath Quick Health Monitor
Simple script to monitor service health and key functionality
"""

import requests
from datetime import datetime
import sys

def health_check():
    """Quick health check of all MantraPath services"""
    services = {
        "API Gateway": "http://localhost:8000/health",
        "Auth Service": "http://localhost:8001/health", 
        "Profile Service": "http://localhost:8002/health",
        "Mood Service": "http://localhost:8003/health",
        "Chatbot Service": "http://localhost:8004/health",
        "Translation Service": "http://localhost:8005/health",
        "Content Service": "http://localhost:8006/health",
        "Community Service": "http://localhost:8007/health",
        "Notification Service": "http://localhost:8008/health",
        "ML Service": "http://localhost:8009/health",
        "Media Service": "http://localhost:8010/health",
        "Voice Service": "http://localhost:8011/health",
        "Action Orchestrator": "http://localhost:8012/health",
        "Phi3 Agent": "http://localhost:8013/health",
    }
    
    print(f"🔍 MantraPath Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    healthy = 0
    total = len(services)
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print(f"✅ {service:20} | Healthy")
                healthy += 1
            else:
                print(f"❌ {service:20} | Status: {response.status_code}")
        except Exception:
            print(f"❌ {service:20} | Error: Connection failed")
    
    print("=" * 60)
    health_percentage = (healthy / total) * 100
    print(f"📊 Overall Health: {healthy}/{total} services ({health_percentage:.1f}%)")
    
    if health_percentage >= 90:
        print("🟢 System Status: EXCELLENT")
    elif health_percentage >= 75:
        print("🟡 System Status: GOOD")
    elif health_percentage >= 50:
        print("🟠 System Status: DEGRADED")
    else:
        print("🔴 System Status: CRITICAL")
    
    return health_percentage

def quick_login_test():
    """Test login functionality"""
    print("\n🔐 Testing Authentication...")
    
    try:
        response = requests.post(
            "http://localhost:8001/login",
            json={
                "email_or_username": "ssharma8132@gmail.com",
                "password": "Dev@#123"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Authentication: Working")
            return True
        else:
            print("❌ Authentication: Failed")
            return False
    except Exception:
        print("❌ Authentication: Error")
        return False

def test_voice_service():
    """Test voice service TTS functionality"""
    print("\n🎤 Testing Voice Service...")
    
    try:
        response = requests.post(
            "http://localhost:8011/tts",
            json={
                "text": "Hello, this is a test",
                "language": "en",
                "voice": "default"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Voice Service (TTS): Working")
            return True
        else:
            print("❌ Voice Service (TTS): Failed")
            return False
    except Exception:
        print("❌ Voice Service: Connection Error")
        return False

def test_translation_service():
    """Test translation service functionality"""
    print("\n🌐 Testing Translation Service...")
    
    try:
        # Test language detection
        response = requests.post(
            "http://localhost:8005/detect-language",
            json={"text": "Hello world"},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Translation Service (Language Detection): Working")
            
            # Test translation
            response = requests.post(
                "http://localhost:8005/translate",
                json={
                    "text": "Hello world",
                    "target_language": "es",
                    "source_language": "en"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ Translation Service (Translation): Working")
                return True
            else:
                print("❌ Translation Service (Translation): Failed")
                return False
        else:
            print("❌ Translation Service (Language Detection): Failed")
            return False
    except Exception:
        print("❌ Translation Service: Connection Error")
        return False

def test_chatbot_integration():
    """Test chatbot service integration"""
    print("\n🤖 Testing Chatbot Integration...")
    
    try:
        response = requests.post(
            "http://localhost:8004/chat",
            json={
                "message": "Hello, how are you?",
                "session_id": None
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Chatbot Service: Working")
            return True
        else:
            print("❌ Chatbot Service: Failed")
            return False
    except Exception:
        print("❌ Chatbot Service: Connection Error")
        return False

def test_mood_analysis():
    """Test mood analysis functionality"""
    print("\n😊 Testing Mood Analysis...")
    
    try:
        # Test sentiment analysis via ML service
        response = requests.post(
            "http://localhost:8009/sentiment-analysis",
            json={"text": "I'm feeling great today!"},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Mood Analysis (Sentiment): Working")
            return True
        else:
            print("❌ Mood Analysis (Sentiment): Failed")
            return False
    except Exception:
        print("❌ Mood Analysis: Connection Error")
        return False

def test_api_gateway_routing():
    """Test API Gateway routing functionality"""
    print("\n🌐 Testing API Gateway Routing...")
    
    try:
        # Test voice service routing through gateway
        response = requests.post(
            "http://localhost:8000/api/v1/voice/tts",
            json={
                "text": "Gateway test",
                "language": "en"
            },
            timeout=5
        )
        
        if response.status_code in [200, 401, 403]:  # Any response means routing works
            print("✅ API Gateway (Voice Routing): Working")
            
            # Test translation service routing
            response = requests.post(
                "http://localhost:8000/api/v1/translate/detect-language",
                json={"text": "Hello"},
                timeout=5
            )
            
            if response.status_code in [200, 401, 403]:
                print("✅ API Gateway (Translation Routing): Working")
                return True
            else:
                print("❌ API Gateway (Translation Routing): Failed")
                return False
        else:
            print("❌ API Gateway (Voice Routing): Failed")
            return False
    except Exception:
        print("❌ API Gateway Routing: Connection Error")
        return False

if __name__ == "__main__":
    health_percentage = health_check()
    auth_working = quick_login_test()
    voice_working = test_voice_service()
    translation_working = test_translation_service()
    chatbot_working = test_chatbot_integration()
    mood_working = test_mood_analysis()
    gateway_working = test_api_gateway_routing()
    
    print(f"\n📋 Comprehensive Health Summary:")
    print(f"   Services Health: {health_percentage:.1f}%")
    print(f"   Authentication: {'✅ Working' if auth_working else '❌ Failed'}")
    print(f"   Voice Service: {'✅ Working' if voice_working else '❌ Failed'}")
    print(f"   Translation: {'✅ Working' if translation_working else '❌ Failed'}")
    print(f"   Chatbot: {'✅ Working' if chatbot_working else '❌ Failed'}")
    print(f"   Mood Analysis: {'✅ Working' if mood_working else '❌ Failed'}")
    print(f"   API Gateway: {'✅ Working' if gateway_working else '❌ Failed'}")
    
    # Calculate overall system health
    feature_tests = [auth_working, voice_working, translation_working, chatbot_working, mood_working, gateway_working]
    features_working = sum(feature_tests)
    total_features = len(feature_tests)
    feature_percentage = (features_working / total_features) * 100
    
    print(f"\n🎯 Feature Tests: {features_working}/{total_features} working ({feature_percentage:.1f}%)")
    
    # Overall system status
    overall_health = (health_percentage + feature_percentage) / 2
    
    if overall_health >= 90:
        print("🟢 Overall System Status: EXCELLENT")
        exit_code = 0
    elif overall_health >= 75:
        print("🟡 Overall System Status: GOOD")
        exit_code = 0
    elif overall_health >= 50:
        print("🟠 Overall System Status: DEGRADED")
        exit_code = 1
    else:
        print("🔴 Overall System Status: CRITICAL")
        exit_code = 1
    
    print(f"📊 Overall Health Score: {overall_health:.1f}%")
    
    # Recommendations based on failed services
    if not auth_working:
        print("\n⚠️  Authentication issues detected. Check auth service logs.")
    if not voice_working:
        print("\n⚠️  Voice service issues. Check TTS/STT functionality.")
    if not translation_working:
        print("\n⚠️  Translation service issues. Check language detection and translation.")
    if not chatbot_working:
        print("\n⚠️  Chatbot service issues. Check AI model integration.")
    if not mood_working:
        print("\n⚠️  Mood analysis issues. Check ML service sentiment analysis.")
    if not gateway_working:
        print("\n⚠️  API Gateway routing issues. Check service discovery and routing.")
    
    if health_percentage < 80:
        print("\n⚠️  Multiple services down. Check docker containers and logs.")
        print("   To restart services: ./start.sh")
    
    print(f"\n🔧 Quick Start Commands:")
    print(f"   Start all services: ./start.sh")
    print(f"   Backend only: ./start.sh backend")
    print(f"   Check logs: docker-compose logs -f")
    print(f"   Restart single service: docker-compose restart <service_name>")
    
    sys.exit(exit_code)
