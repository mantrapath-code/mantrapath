#!/usr/bin/env python3
"""
Comprehensive Voice Service Testing Script
Tests all major functionality of the MantraPath Voice Service
"""

import asyncio
import json
import logging
import time
import httpx
from pathlib import Path
import io
from typing import Dict, Any, List
import wave
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceServiceTester:
    """Comprehensive testing for Voice Service functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8007", auth_token: str = None):
        self.base_url = base_url
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log_test_result(self, test_name: str, passed: bool, details: str = "", duration: float = 0):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "duration": f"{duration:.2f}s"
        }
        self.test_results.append(result)
        logger.info(f"{status} - {test_name} ({duration:.2f}s): {details}")
    
    def create_test_audio(self, duration: float = 2.0, sample_rate: int = 44100) -> bytes:
        """Create test audio data (sine wave)"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A note
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Convert to 16-bit PCM
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        return buffer.getvalue()
    
    async def test_health_check(self) -> bool:
        """Test service health endpoint"""
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                details = f"Status: {data.get('status', 'unknown')}"
                self.log_test_result("Health Check", True, details, duration)
                return True
            else:
                self.log_test_result("Health Check", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Health Check", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_capabilities_endpoint(self) -> bool:
        """Test service capabilities endpoint"""
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/capabilities")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', {})
                commands = data.get('supported_commands', {})
                details = f"Features: {len(features)}, Commands: {len(commands)}"
                self.log_test_result("Capabilities Check", True, details, duration)
                return True
            else:
                self.log_test_result("Capabilities Check", False, f"HTTP {response.status_code}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Capabilities Check", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_speech_to_text(self) -> bool:
        """Test Speech-to-Text functionality"""
        if not self.auth_token:
            self.log_test_result("STT Test", False, "No auth token provided", 0)
            return False
            
        start_time = time.time()
        try:
            # Create test audio file
            test_audio = self.create_test_audio(duration=3.0)
            
            files = {
                'file': ('test_audio.wav', io.BytesIO(test_audio), 'audio/wav')
            }
            data = {
                'language': 'en',
                'model': 'base',
                'enable_emotion_analysis': 'true'
            }
            headers = {
                'Authorization': f'Bearer {self.auth_token}'
            }
            
            response = await self.client.post(
                f"{self.base_url}/stt",
                files=files,
                data=data,
                headers=headers
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('text', '')
                confidence = result.get('confidence', 0)
                details = f"Text length: {len(text)}, Confidence: {confidence:.2f}"
                self.log_test_result("STT Test", True, details, duration)
                return True
            else:
                error_detail = response.text
                self.log_test_result("STT Test", False, f"HTTP {response.status_code}: {error_detail}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("STT Test", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_text_to_speech(self) -> bool:
        """Test Text-to-Speech functionality"""
        if not self.auth_token:
            self.log_test_result("TTS Test", False, "No auth token provided", 0)
            return False
            
        start_time = time.time()
        try:
            payload = {
                "text": "Hello, this is a test of the MantraPath Voice Service text-to-speech functionality.",
                "language": "en",
                "voice_name": "neural",
                "audio_format": "wav"
            }
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
            
            response = await self.client.post(
                f"{self.base_url}/tts",
                json=payload,
                headers=headers
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                audio_size = len(response.content)
                details = f"Generated audio size: {audio_size} bytes"
                self.log_test_result("TTS Test", True, details, duration)
                return True
            else:
                error_detail = response.text
                self.log_test_result("TTS Test", False, f"HTTP {response.status_code}: {error_detail}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("TTS Test", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_voice_command_processing(self) -> bool:
        """Test Voice Command processing"""
        if not self.auth_token:
            self.log_test_result("Voice Command Test", False, "No auth token provided", 0)
            return False
            
        start_time = time.time()
        try:
            payload = {
                "command": "start meditation session",
                "language": "en",
                "context": {
                    "current_page": "dashboard",
                    "user_state": "active"
                }
            }
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
            
            response = await self.client.post(
                f"{self.base_url}/voice-command",
                json=payload,
                headers=headers
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                intent = result.get('intent', '')
                confidence = result.get('confidence', 0)
                details = f"Intent: {intent}, Confidence: {confidence:.2f}"
                self.log_test_result("Voice Command Test", True, details, duration)
                return True
            else:
                error_detail = response.text
                self.log_test_result("Voice Command Test", False, f"HTTP {response.status_code}: {error_detail}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Voice Command Test", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_emotion_analysis(self) -> bool:
        """Test Emotion Analysis functionality"""
        if not self.auth_token:
            self.log_test_result("Emotion Analysis Test", False, "No auth token provided", 0)
            return False
            
        start_time = time.time()
        try:
            # Create test audio with emotional content simulation
            test_audio = self.create_test_audio(duration=4.0)
            
            files = {
                'file': ('emotional_test.wav', io.BytesIO(test_audio), 'audio/wav')
            }
            headers = {
                'Authorization': f'Bearer {self.auth_token}'
            }
            
            response = await self.client.post(
                f"{self.base_url}/emotion-analysis",
                files=files,
                headers=headers
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                emotions = result.get('emotions', {})
                primary_emotion = result.get('primary_emotion', '')
                details = f"Primary: {primary_emotion}, Detected emotions: {len(emotions)}"
                self.log_test_result("Emotion Analysis Test", True, details, duration)
                return True
            else:
                error_detail = response.text
                self.log_test_result("Emotion Analysis Test", False, f"HTTP {response.status_code}: {error_detail}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Emotion Analysis Test", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_language_support(self) -> bool:
        """Test multilingual language support"""
        start_time = time.time()
        try:
            # Test different languages
            test_languages = ['en', 'hi', 'es', 'fr', 'ar']
            supported_count = 0
            
            for lang in test_languages:
                # Test TTS for each language (if auth available)
                if self.auth_token:
                    payload = {
                        "text": "Hello world",
                        "language": lang,
                        "audio_format": "wav"
                    }
                    headers = {
                        'Authorization': f'Bearer {self.auth_token}',
                        'Content-Type': 'application/json'
                    }
                    
                    response = await self.client.post(
                        f"{self.base_url}/tts",
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        supported_count += 1
            
            duration = time.time() - start_time
            details = f"Supported languages: {supported_count}/{len(test_languages)}"
            self.log_test_result("Language Support Test", supported_count > 0, details, duration)
            return supported_count > 0
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Language Support Test", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_voice_profile_management(self) -> bool:
        """Test Voice Profile management"""
        if not self.auth_token:
            self.log_test_result("Voice Profile Test", False, "No auth token provided", 0)
            return False
            
        start_time = time.time()
        try:
            # Get user profiles
            headers = {
                'Authorization': f'Bearer {self.auth_token}'
            }
            
            response = await self.client.get(
                f"{self.base_url}/profiles",
                headers=headers
            )
            duration = time.time() - start_time
            
            if response.status_code == 200:
                profiles = response.json()
                profile_count = len(profiles) if isinstance(profiles, list) else 0
                details = f"User profiles found: {profile_count}"
                self.log_test_result("Voice Profile Test", True, details, duration)
                return True
            else:
                error_detail = response.text
                self.log_test_result("Voice Profile Test", False, f"HTTP {response.status_code}: {error_detail}", duration)
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("Voice Profile Test", False, f"Exception: {str(e)}", duration)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        logger.info("🚀 Starting Voice Service Test Suite")
        logger.info(f"Testing service at: {self.base_url}")
        
        start_time = time.time()
        
        # Core service tests (no auth required)
        await self.test_health_check()
        await self.test_capabilities_endpoint()
        
        # Authenticated feature tests
        if self.auth_token:
            logger.info("🔐 Running authenticated tests...")
            await self.test_speech_to_text()
            await self.test_text_to_speech()
            await self.test_voice_command_processing()
            await self.test_emotion_analysis()
            await self.test_language_support()
            await self.test_voice_profile_management()
        else:
            logger.warning("⚠️ No auth token provided - skipping authenticated tests")
        
        total_duration = time.time() - start_time
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{success_rate:.1f}%",
            "total_duration": f"{total_duration:.2f}s",
            "test_results": self.test_results
        }
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 VOICE SERVICE TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        logger.info(f"⏱️  Total Duration: {total_duration:.2f}s")
        logger.info(f"{'='*60}")
        
        return summary

async def main():
    """Main testing function"""
    # Configuration
    BASE_URL = "http://localhost:8007"
    AUTH_TOKEN = None  # Set to valid JWT token for full testing
    
    # Check if service is running
    logger.info("🔍 Checking if Voice Service is running...")
    
    async with VoiceServiceTester(BASE_URL, AUTH_TOKEN) as tester:
        try:
            # Quick connectivity test
            response = await tester.client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                logger.info("✅ Voice Service is running and accessible")
                
                # Run full test suite
                results = await tester.run_all_tests()
                
                # Save results to file
                results_file = Path("voice_service_test_results.json")
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2)
                logger.info(f"📄 Test results saved to: {results_file}")
                
                return results
            else:
                logger.error(f"❌ Voice Service not responding properly: HTTP {response.status_code}")
                return None
                
        except httpx.ConnectError:
            logger.error(f"❌ Cannot connect to Voice Service at {BASE_URL}")
            logger.info("💡 Ensure the Voice Service is running:")
            logger.info("   cd backend/services/voice_service")
            logger.info("   python main.py")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return None

if __name__ == "__main__":
    asyncio.run(main())
