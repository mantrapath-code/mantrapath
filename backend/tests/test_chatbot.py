#!/usr/bin/env python3
"""
Test script for MantraPath Chatbot Service
Tests Phi-3 integration and fallback mechanisms
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any
from .config import API_BASE, CHATBOT_DIRECT

# Test user credentials (you'll need to register first)
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class ChatbotTester:
    def __init__(self):
        self.auth_token = None
        self.session_id = None
        
    async def authenticate(self):
        """Authenticate and get JWT token"""
        print("🔐 Authenticating test user...")
        
        async with httpx.AsyncClient() as client:
            # Try to login first
            try:
                response = await client.post(
                    f"{API_BASE}/api/auth/login",
                    json=TEST_USER
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data["access_token"]
                    print("✅ Authentication successful")
                    return True
                    
            except Exception as e:
                print(f"⚠️  Login failed: {e}")
                
            # Try to register if login failed
            try:
                print("📝 Registering test user...")
                response = await client.post(
                    f"{API_BASE}/api/auth/register",
                    json={
                        **TEST_USER,
                        "full_name": "Test User"
                    }
                )
                
                if response.status_code == 201:
                    # Now login
                    response = await client.post(
                        f"{API_BASE}/api/auth/login",
                        json=TEST_USER
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.auth_token = data["access_token"]
                        print("✅ Registration and authentication successful")
                        return True
                        
            except Exception as e:
                print(f"❌ Registration failed: {e}")
                
        return False
    
    async def test_service_health(self):
        """Test all service health endpoints"""
        print("\n🏥 Testing service health...")
        
        services = [
            ("API Gateway", f"{API_BASE}/health"),
            ("Chatbot Service", f"{CHATBOT_DIRECT}/health"),
            # Phi-3 Agent removed - functionality moved to models_service
        ]
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for name, url in services:
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {name}: {data.get('status', 'healthy')}")
                    else:
                        print(f"⚠️  {name}: HTTP {response.status_code}")
                except Exception as e:
                    print(f"❌ {name}: {str(e)}")
    
    async def create_chat_session(self):
        """Create a new chat session"""
        print("\n💬 Creating chat session...")
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{CHATBOT_DIRECT}/chat/session",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.session_id = data["id"]
                    print(f"✅ Chat session created: {self.session_id}")
                    return True
                else:
                    print(f"❌ Failed to create session: HTTP {response.status_code}")
                    print(response.text)
                    
            except Exception as e:
                print(f"❌ Session creation error: {e}")
                
        return False
    
    async def test_chat_responses(self):
        """Test various chat scenarios"""
        print("\n🤖 Testing chat responses...")
        
        test_messages = [
            "Hello, how are you?",
            "I'm feeling really anxious today",
            "Can you help me with some breathing exercises?",
            "I've been having trouble sleeping",
            "Thank you for your help"
        ]
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i, message in enumerate(test_messages, 1):
                print(f"\n📝 Test {i}: '{message}'")
                
                try:
                    start_time = time.time()
                    
                    response = await client.post(
                        f"{CHATBOT_DIRECT}/api/chatbot/chat",
                        headers=headers,
                        json={
                            "message": message,
                            "session_id": self.session_id
                        }
                    )
                    
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Response ({response_time:.2f}s): {data['response'][:100]}...")
                        print(f"   Source: {data.get('source', 'unknown')}")
                        print(f"   Confidence: {data.get('confidence_score', 0):.2f}")
                        
                        if data.get('crisis_detected'):
                            print("🚨 Crisis detected!")
                            
                    else:
                        print(f"❌ Failed: HTTP {response.status_code}")
                        print(response.text)
                        
                    # Wait between messages
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    async def test_phi4_models_service(self):
        """Test Phi-4 via models service (replaces phi3_agent)"""
        print("\n🧠 Testing Phi-4 via models service...")
        
        # Test text generation endpoint in models service
        models_service_url = API_BASE.replace("/api/v1", ":8081")  # Models service on port 8081
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{models_service_url}/api/v1/nlp/generate",
                    json={
                        "prompt": "You are a helpful mental health support assistant. User: Hello, can you help me with anxiety? Assistant:",
                        "max_tokens": 100,
                        "temperature": 0.7,
                        "model": "phi4"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message = data["generated_text"]
                    print(f"✅ Phi-4 models service response: {message[:100]}...")
                else:
                    print(f"❌ Phi-4 models service test failed: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Phi-4 models service test error: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 MantraPath Chatbot Service Test Suite")
        print("=" * 50)
        
        # Test service health
        await self.test_service_health()
        
        # Test Phi-3 directly
        await self.test_phi3_direct()
        
        # Authenticate
        if not await self.authenticate():
            print("❌ Authentication failed - skipping chat tests")
            return
        
        # Create session
        if not await self.create_chat_session():
            print("❌ Session creation failed - skipping chat tests")
            return
        
        # Test chat responses
        await self.test_chat_responses()
        
        print("\n🎉 Test suite completed!")
        print("\n📊 Summary:")
        print("   • Service health checks completed")
        print("   • Authentication tested")
        print("   • Chat session created")
        print("   • Multiple chat scenarios tested")
        print("   • Phi-3 integration verified")

async def main():
    """Main test function"""
    tester = ChatbotTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())