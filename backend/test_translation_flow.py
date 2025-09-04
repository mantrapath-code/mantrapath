#!/usr/bin/env python3
"""
Test Script: Verify Translation Service Integration with Phi-3
Tests the complete flow: Chatbot -> Translation Service -> Models Service (Phi-3)
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# Service URLs
TRANSLATION_SERVICE_URL = "http://localhost:8010"
MODELS_SERVICE_URL = "http://localhost:8085"
CHATBOT_SERVICE_URL = "http://localhost:8006"

class TranslationFlowTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_models_service_health(self) -> bool:
        """Test if Models Service is running and healthy"""
        try:
            response = await self.client.get(f"{MODELS_SERVICE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Models Service is healthy: {data}")
                return True
            else:
                print(f"❌ Models Service health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Models Service not accessible: {e}")
            return False
    
    async def test_models_service_phi3_translation(self) -> bool:
        """Test direct Phi-3 translation via Models Service"""
        try:
            test_text = "Hello, how are you today?"
            payload = {
                "text": test_text,
                "source_language": "en",
                "target_language": "hi"
            }
            
            response = await self.client.post(
                f"{MODELS_SERVICE_URL}/api/v1/translation/translate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Direct Phi-3 translation works:")
                print(f"   Original: {test_text}")
                print(f"   Translated: {data.get('translated_text')}")
                print(f"   Engine: {data.get('engine')}")
                print(f"   Confidence: {data.get('confidence_score')}")
                return True
            else:
                print(f"❌ Direct Phi-3 translation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Direct Phi-3 translation error: {e}")
            return False
    
    async def test_translation_service_health(self) -> bool:
        """Test if Translation Service is running"""
        try:
            response = await self.client.get(f"{TRANSLATION_SERVICE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Translation Service is healthy: {data}")
                return True
            else:
                print(f"❌ Translation Service health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Translation Service not accessible: {e}")
            return False
    
    async def test_enhanced_translation_service(self) -> bool:
        """Test enhanced translation service with Phi-3 integration"""
        try:
            test_cases = [
                {
                    "text": "I am feeling very happy today!",
                    "source_language": "en",
                    "target_language": "hi",
                    "description": "English to Hindi (should use Phi-3)"
                },
                {
                    "text": "आज मौसम बहुत अच्छा है",
                    "source_language": "hi",
                    "target_language": "en",
                    "description": "Hindi to English (should use Bhashini + Phi-3)"
                },
                {
                    "text": "This is a complex sentence with multiple clauses that requires context-aware translation for better accuracy.",
                    "source_language": "en",
                    "target_language": "ta",
                    "description": "Complex English to Tamil (should use Phi-3 for context)"
                }
            ]
            
            all_passed = True
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n🧪 Test Case {i}: {test_case['description']}")
                
                payload = {
                    "text": test_case["text"],
                    "source_language": test_case["source_language"],
                    "target_language": test_case["target_language"]
                }
                
                start_time = time.time()
                response = await self.client.post(
                    f"{TRANSLATION_SERVICE_URL}/translate",
                    json=payload
                )
                elapsed_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Success ({elapsed_time:.2f}s)")
                    print(f"   Original: {test_case['text']}")
                    print(f"   Translated: {data.get('translated_text')}")
                    print(f"   Engine: {data.get('engine')}")
                    print(f"   Confidence: {data.get('confidence_score')}")
                    print(f"   Processing Time: {data.get('processing_time_ms')}ms")
                else:
                    print(f"   ❌ Failed ({response.status_code}): {response.text}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Enhanced translation service test error: {e}")
            return False
    
    async def test_chatbot_translation_integration(self) -> bool:
        """Test chatbot integration with translation service"""
        try:
            # Test multilingual chat message
            payload = {
                "message": "नमस्ते! मैं आज खुश हूँ। क्या आप मेरी मदद कर सकते हैं?",
                "language": "hi",
                "session_id": "test-session-123"
            }
            
            response = await self.client.post(
                f"{CHATBOT_SERVICE_URL}/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chatbot multilingual response works:")
                print(f"   User Message: {payload['message']}")
                print(f"   Bot Response: {data.get('response')}")
                print(f"   Translation Used: {data.get('translation_used', False)}")
                return True
            else:
                print(f"❌ Chatbot translation integration failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Chatbot translation integration error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting Translation Flow Integration Tests...")
        print("=" * 60)
        
        results = {}
        
        # Test 1: Models Service Health
        print("\n1️⃣ Testing Models Service Health...")
        results["models_service_health"] = await self.test_models_service_health()
        
        # Test 2: Direct Phi-3 Translation
        print("\n2️⃣ Testing Direct Phi-3 Translation...")
        results["phi3_direct"] = await self.test_models_service_phi3_translation()
        
        # Test 3: Translation Service Health
        print("\n3️⃣ Testing Translation Service Health...")
        results["translation_service_health"] = await self.test_translation_service_health()
        
        # Test 4: Enhanced Translation Service
        print("\n4️⃣ Testing Enhanced Translation Service...")
        results["enhanced_translation"] = await self.test_enhanced_translation_service()
        
        # Test 5: Chatbot Integration
        print("\n5️⃣ Testing Chatbot Translation Integration...")
        results["chatbot_integration"] = await self.test_chatbot_translation_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY:")
        print("=" * 60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Translation flow is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the issues above.")
        
        await self.client.aclose()

async def main():
    """Main test function"""
    tester = TranslationFlowTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
