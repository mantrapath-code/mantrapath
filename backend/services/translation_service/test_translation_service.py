#!/usr/bin/env python3
"""
Comprehensive test script for the Translation Service
Tests all endpoints and functionality
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timedelta
import jwt
from typing import Dict, Any

SECRET_KEY = "ursiW6MiNevaTHstfT04gvFbBZnwIbfscqBv4jEKRjDtp74x35NVy7Ol9VY3RJxz6eAHWb8KyqfWitkJBC7w"  # Combined JWT key from .env
ALGORITHM = "HS256"

BASE_URL = "http://localhost:8010"

def create_test_token(user_id: str = "test_user", email: str = "test@example.com") -> str:
    """Create a test JWT token for authentication"""
    data = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "type": "access"
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

class TranslationServiceTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.session = None
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test the health check endpoint"""
        print("🔍 Testing health check...")
        try:
            async with self.session.get(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health check passed: {data}")
                    self.test_results.append(("Health Check", "PASS", data))
                else:
                    error_data = await response.text()
                    print(f"⚠️ Health check returned {response.status}: {error_data}")
                    self.test_results.append(("Health Check", "FAIL", f"Status: {response.status}"))
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.test_results.append(("Health Check", "ERROR", str(e)))
    
    async def test_basic_translation(self):
        """Test basic translation functionality using test endpoint"""
        print("🔍 Testing basic translation...")
        
        try:
            # Test request payload
            payload = {
                "text": "Hello, welcome to our meditation app",
                "source_language": "en",
                "target_language": "es",
                "engine": "local",
                "domain": "meditation",
                "cultural_adaptation": True,
                "use_custom_glossary": True,
                "use_cache": True
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/test/translate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Translation successful: '{payload['text']}' -> '{data.get('translated_text', 'No translation')}'")
                        print(f"   Source: {data.get('source_language', 'Unknown')}")
                        print(f"   Target: {data.get('target_language', 'Unknown')}")
                        print(f"   Engine: {data.get('engine_used', 'Unknown')}")
                        print(f"   Processing time: {data.get('processing_time_ms', 0)}ms")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Translation failed with {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Translation test failed with exception: {e}")
            return False
    
    async def test_translation_authenticated(self):
        """Test basic translation with authentication"""
        print("🔍 Testing authenticated translation...")
        
        # Create test token
        token = create_test_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            async with self.session.post(
                f"{BASE_URL}/translate",
                json={
                    "text": "Hello, how are you?",
                    "source_language": "en",
                    "target_language": "es",
                    "engine": "local"
                },
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Authenticated translation successful: {data.get('translated_text', 'N/A')}")
                    self.test_results.append(("Authenticated Translation", "PASS", data))
                else:
                    error_text = await response.text()
                    print(f"❌ Authenticated translation failed with {response.status}: {error_text}")
                    self.test_results.append(("Authenticated Translation", "FAIL", f"Status: {response.status}"))
        except Exception as e:
            print(f"❌ Authenticated translation error: {e}")
            self.test_results.append(("Authenticated Translation", "ERROR", str(e)))

    async def test_language_detection(self):
        """Test language detection endpoint"""
        print("🔍 Testing language detection...")
        
        test_request = {
            "text": "Namaste, let's begin our meditation journey"
        }
        
        try:
            async with self.session.post(
                f"{BASE_URL}/detect-language",
                json=test_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Language detection successful: {data}")
                    self.test_results.append(("Language Detection", "PASS", data))
                elif response.status == 401:
                    print("⚠️ Language detection requires authentication")
                    self.test_results.append(("Language Detection", "AUTH_REQUIRED", "Authentication needed"))
                else:
                    error_data = await response.text()
                    print(f"❌ Language detection failed with {response.status}: {error_data}")
                    self.test_results.append(("Language Detection", "FAIL", f"Status: {response.status}"))
                    
        except Exception as e:
            print(f"❌ Language detection test failed: {e}")
            self.test_results.append(("Language Detection", "ERROR", str(e)))
    
    async def test_supported_languages(self):
        """Test supported languages endpoint"""
        print("🔍 Testing supported languages...")
        
        try:
            async with self.session.get(f"{BASE_URL}/languages") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Supported languages retrieved: {len(data.get('languages', []))} languages")
                    self.test_results.append(("Supported Languages", "PASS", f"{len(data.get('languages', []))} languages"))
                else:
                    error_data = await response.text()
                    print(f"❌ Supported languages failed with {response.status}: {error_data}")
                    self.test_results.append(("Supported Languages", "FAIL", f"Status: {response.status}"))
                    
        except Exception as e:
            print(f"❌ Supported languages test failed: {e}")
            self.test_results.append(("Supported Languages", "ERROR", str(e)))
    
    async def test_openapi_docs(self):
        """Test OpenAPI documentation endpoint"""
        print("🔍 Testing OpenAPI documentation...")
        
        try:
            async with self.session.get(f"{BASE_URL}/openapi.json") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ OpenAPI docs available: {data.get('info', {}).get('title', 'Unknown')}")
                    self.test_results.append(("OpenAPI Docs", "PASS", "Documentation available"))
                else:
                    error_data = await response.text()
                    print(f"❌ OpenAPI docs failed with {response.status}: {error_data}")
                    self.test_results.append(("OpenAPI Docs", "FAIL", f"Status: {response.status}"))
                    
        except Exception as e:
            print(f"❌ OpenAPI docs test failed: {e}")
            self.test_results.append(("OpenAPI Docs", "ERROR", str(e)))
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Translation Service Tests...\n")
        
        await self.test_health_check()
        await self.test_supported_languages()
        await self.test_openapi_docs()
        await self.test_language_detection()
        await self.test_basic_translation()
        await self.test_translation_authenticated()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        for test_name, status, details in self.test_results:
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌", 
                "ERROR": "💥",
                "AUTH_REQUIRED": "🔐"
            }.get(status, "❓")
            
            print(f"{status_emoji} {test_name}: {status}")
            if status in ["FAIL", "ERROR"] and details:
                print(f"   Details: {details}")
        
        # Calculate stats
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r[1] == "PASS"])
        auth_required = len([r for r in self.test_results if r[1] == "AUTH_REQUIRED"])
        failed = len([r for r in self.test_results if r[1] in ["FAIL", "ERROR"]])
        
        print(f"\n📈 STATISTICS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed}")
        print(f"   Auth Required: {auth_required}")
        print(f"   Failed: {failed}")
        
        success_rate = ((passed + auth_required) / total_tests * 100) if total_tests > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 Translation service is functioning well!")
        elif success_rate >= 60:
            print("\n⚠️ Translation service has some issues but is mostly functional")
        else:
            print("\n🚨 Translation service has significant issues")

async def main():
    """Main test function"""
    async with TranslationServiceTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
