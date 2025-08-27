#!/usr/bin/env python3
"""
Comprehensive Voice Service Test Script
Tests voice synthesis, voice cloning, multi-language support, and integration with translation service.
Uses only free/open-source technologies.
"""

import asyncio
import json
import logging
import sys
import os
import time
import tempfile
import requests
import aiohttp
from typing import Dict, List, Any, Optional
from pathlib import Path
import wave
import hashlib

# Add backend to path for imports
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_path)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('voice_service_test.log')
    ]
)
logger = logging.getLogger(__name__)

class VoiceServiceTester:
    """Comprehensive voice service testing class."""
    
    def __init__(self, base_url: str = "http://localhost:8011"):
        self.base_url = base_url
        self.session = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "voice_synthesis": [],
            "voice_cloning": [],
            "multi_language": [],
            "integration": [],
            "performance": [],
            "error_handling": []
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def check_service_health(self) -> bool:
        """Check if voice service is running and healthy."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    logger.info(f"Voice service health: {health_data}")
                    return True
                else:
                    logger.error(f"Voice service health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Failed to connect to voice service: {e}")
            return False
    
    async def test_basic_tts(self) -> Dict[str, Any]:
        """Test basic text-to-speech functionality."""
        test_name = "Basic TTS"
        start_time = time.time()
        
        try:
            # Test basic TTS request
            tts_data = {
                "text": "Hello, this is a test of the text-to-speech system.",
                "language": "en",
                "voice_id": "default",
                "engine": "coqui_tts"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/voice/tts",
                json=tts_data
            ) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    duration = time.time() - start_time
                    
                    # Validate audio data
                    if len(audio_data) > 1000:  # Basic size check
                        result = {
                            "status": "PASSED",
                            "test": test_name,
                            "duration": duration,
                            "audio_size": len(audio_data),
                            "message": "Basic TTS generation successful"
                        }
                        self.test_results["passed"] += 1
                    else:
                        result = {
                            "status": "FAILED",
                            "test": test_name,
                            "duration": duration,
                            "error": "Audio data too small"
                        }
                        self.test_results["failed"] += 1
                else:
                    error_text = await response.text()
                    result = {
                        "status": "FAILED",
                        "test": test_name,
                        "duration": time.time() - start_time,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    self.test_results["failed"] += 1
                    
        except Exception as e:
            result = {
                "status": "FAILED",
                "test": test_name,
                "duration": time.time() - start_time,
                "error": str(e)
            }
            self.test_results["failed"] += 1
        
        self.test_results["total_tests"] += 1
        self.test_results["voice_synthesis"].append(result)
        logger.info(f"{test_name}: {result['status']} - {result.get('message', result.get('error'))}")
        return result
    
    async def test_multi_language_tts(self) -> List[Dict[str, Any]]:
        """Test TTS with multiple languages."""
        test_cases = [
            {"text": "Hello, how are you today?", "language": "en", "description": "English"},
            {"text": "Hola, ¿cómo estás hoy?", "language": "es", "description": "Spanish"},
            {"text": "Bonjour, comment allez-vous aujourd'hui?", "language": "fr", "description": "French"},
            {"text": "Hallo, wie geht es dir heute?", "language": "de", "description": "German"},
            {"text": "नमस्ते, आज आप कैसे हैं?", "language": "hi", "description": "Hindi"},
            {"text": "你好，你今天怎么样？", "language": "zh", "description": "Chinese"}
        ]
        
        results = []
        
        for case in test_cases:
            start_time = time.time()
            test_name = f"Multi-language TTS - {case['description']}"
            
            try:
                tts_data = {
                    "text": case["text"],
                    "language": case["language"],
                    "voice_id": "default",
                    "engine": "coqui_tts"
                }
                
                async with self.session.post(
                    f"{self.base_url}/api/v1/voice/tts",
                    json=tts_data
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        audio_data = await response.read()
                        
                        if len(audio_data) > 500:  # Basic validation
                            result = {
                                "status": "PASSED",
                                "test": test_name,
                                "language": case["language"],
                                "duration": duration,
                                "audio_size": len(audio_data),
                                "message": f"Successfully generated {case['description']} TTS"
                            }
                            self.test_results["passed"] += 1
                        else:
                            result = {
                                "status": "FAILED",
                                "test": test_name,
                                "language": case["language"],
                                "duration": duration,
                                "error": "Audio data too small"
                            }
                            self.test_results["failed"] += 1
                    else:
                        error_text = await response.text()
                        result = {
                            "status": "FAILED",
                            "test": test_name,
                            "language": case["language"],
                            "duration": duration,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        self.test_results["failed"] += 1
                        
            except Exception as e:
                result = {
                    "status": "FAILED",
                    "test": test_name,
                    "language": case["language"],
                    "duration": time.time() - start_time,
                    "error": str(e)
                }
                self.test_results["failed"] += 1
            
            self.test_results["total_tests"] += 1
            results.append(result)
            logger.info(f"{test_name}: {result['status']} - {result.get('message', result.get('error'))}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        self.test_results["multi_language"].extend(results)
        return results
    
    async def test_voice_cloning(self) -> Dict[str, Any]:
        """Test voice cloning functionality with free/open-source implementation."""
        test_name = "Voice Cloning"
        start_time = time.time()
        
        try:
            # Create a simple test audio sample (sine wave)
            sample_audio = self._create_test_audio_sample()
            
            # Test voice cloning endpoint
            clone_data = {
                "text": "This is a test of voice cloning technology using free and open source tools.",
                "voice_id": "test_clone_voice",
                "language": "en"
            }
            
            # Upload audio sample for cloning
            form_data = aiohttp.FormData()
            form_data.add_field('audio_sample', sample_audio, filename='test_voice.wav', content_type='audio/wav')
            form_data.add_field('text', clone_data['text'])
            form_data.add_field('voice_id', clone_data['voice_id'])
            form_data.add_field('language', clone_data['language'])
            
            async with self.session.post(
                f"{self.base_url}/api/v1/voice/clone",
                data=form_data
            ) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    audio_data = await response.read()
                    
                    if len(audio_data) > 1000:
                        result = {
                            "status": "PASSED",
                            "test": test_name,
                            "duration": duration,
                            "audio_size": len(audio_data),
                            "voice_id": clone_data['voice_id'],
                            "message": "Voice cloning successful with free/open-source tools"
                        }
                        self.test_results["passed"] += 1
                    else:
                        result = {
                            "status": "FAILED",
                            "test": test_name,
                            "duration": duration,
                            "error": "Cloned audio data too small"
                        }
                        self.test_results["failed"] += 1
                else:
                    error_text = await response.text()
                    result = {
                        "status": "FAILED",
                        "test": test_name,
                        "duration": duration,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    self.test_results["failed"] += 1
                    
        except Exception as e:
            result = {
                "status": "FAILED",
                "test": test_name,
                "duration": time.time() - start_time,
                "error": str(e)
            }
            self.test_results["failed"] += 1
        
        self.test_results["total_tests"] += 1
        self.test_results["voice_cloning"].append(result)
        logger.info(f"{test_name}: {result['status']} - {result.get('message', result.get('error'))}")
        return result
    
    def _create_test_audio_sample(self) -> bytes:
        """Create a simple test audio sample for voice cloning."""
        try:
            # Create a simple sine wave audio sample
            import math
            import struct
            
            sample_rate = 22050
            duration = 3.0  # 3 seconds
            frequency = 440  # A4 note
            
            # Generate sine wave samples
            samples = []
            for i in range(int(sample_rate * duration)):
                t = i / sample_rate
                sample = int(32767 * math.sin(2 * math.pi * frequency * t) * 0.5)
                samples.append(sample)
            
            # Create WAV file in memory
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                with wave.open(tmp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
                
                # Read the WAV file as bytes
                with open(tmp_file.name, 'rb') as f:
                    audio_data = f.read()
                
                # Clean up temp file
                os.unlink(tmp_file.name)
                
                return audio_data
                
        except Exception as e:
            logger.error(f"Failed to create test audio sample: {e}")
            # Return minimal WAV header if generation fails
            return b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
    
    async def test_translation_integration(self) -> Dict[str, Any]:
        """Test integration with translation service for multi-language voice responses."""
        test_name = "Translation Integration"
        start_time = time.time()
        
        try:
            # Test text that should be translated and then spoken
            integration_data = {
                "text": "Hello, how are you feeling today?",
                "source_language": "en",
                "target_language": "es",
                "voice_response": True,
                "engine": "coqui_tts"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/voice/translate-and-speak",
                json=integration_data
            ) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    result_data = await response.json()
                    
                    if "audio_data" in result_data and "translated_text" in result_data:
                        result = {
                            "status": "PASSED",
                            "test": test_name,
                            "duration": duration,
                            "translated_text": result_data["translated_text"],
                            "audio_provided": bool(result_data["audio_data"]),
                            "message": "Translation integration successful"
                        }
                        self.test_results["passed"] += 1
                    else:
                        result = {
                            "status": "FAILED",
                            "test": test_name,
                            "duration": duration,
                            "error": "Missing audio_data or translated_text in response"
                        }
                        self.test_results["failed"] += 1
                else:
                    error_text = await response.text()
                    result = {
                        "status": "FAILED",
                        "test": test_name,
                        "duration": duration,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
                    self.test_results["failed"] += 1
                    
        except Exception as e:
            result = {
                "status": "FAILED",
                "test": test_name,
                "duration": time.time() - start_time,
                "error": str(e)
            }
            self.test_results["failed"] += 1
        
        self.test_results["total_tests"] += 1
        self.test_results["integration"].append(result)
        logger.info(f"{test_name}: {result['status']} - {result.get('message', result.get('error'))}")
        return result
    
    async def test_performance_metrics(self) -> Dict[str, Any]:
        """Test voice service performance and response times."""
        test_name = "Performance Metrics"
        start_time = time.time()
        
        try:
            performance_tests = []
            
            # Test multiple concurrent requests
            tasks = []
            for i in range(5):
                task_data = {
                    "text": f"Performance test number {i+1}. This is testing concurrent voice generation.",
                    "language": "en",
                    "voice_id": "default",
                    "engine": "coqui_tts"
                }
                task = self._single_tts_request(task_data, f"concurrent_{i+1}")
                tasks.append(task)
            
            # Execute concurrent requests
            concurrent_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successful_requests = [r for r in concurrent_results if isinstance(r, dict) and r.get("status") == "PASSED"]
            failed_requests = [r for r in concurrent_results if isinstance(r, Exception) or (isinstance(r, dict) and r.get("status") == "FAILED")]
            
            avg_duration = sum(r["duration"] for r in successful_requests) / len(successful_requests) if successful_requests else 0
            total_duration = time.time() - start_time
            
            result = {
                "status": "PASSED" if len(successful_requests) >= 3 else "FAILED",
                "test": test_name,
                "duration": total_duration,
                "concurrent_requests": 5,
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "average_response_time": avg_duration,
                "message": f"Performance test: {len(successful_requests)}/5 requests successful"
            }
            
            if len(successful_requests) >= 3:
                self.test_results["passed"] += 1
            else:
                self.test_results["failed"] += 1
                
        except Exception as e:
            result = {
                "status": "FAILED",
                "test": test_name,
                "duration": time.time() - start_time,
                "error": str(e)
            }
            self.test_results["failed"] += 1
        
        self.test_results["total_tests"] += 1
        self.test_results["performance"].append(result)
        logger.info(f"{test_name}: {result['status']} - {result.get('message', result.get('error'))}")
        return result
    
    async def _single_tts_request(self, tts_data: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Helper method for single TTS request."""
        start_time = time.time()
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/voice/tts",
                json=tts_data
            ) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    audio_data = await response.read()
                    return {
                        "status": "PASSED",
                        "request_id": request_id,
                        "duration": duration,
                        "audio_size": len(audio_data)
                    }
                else:
                    return {
                        "status": "FAILED",
                        "request_id": request_id,
                        "duration": duration,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "status": "FAILED",
                "request_id": request_id,
                "duration": time.time() - start_time,
                "error": str(e)
            }
    
    async def test_error_handling(self) -> List[Dict[str, Any]]:
        """Test error handling with invalid inputs."""
        test_cases = [
            {
                "name": "Empty Text",
                "data": {"text": "", "language": "en", "voice_id": "default"},
                "expected_status": [400, 422]
            },
            {
                "name": "Invalid Language",
                "data": {"text": "Test", "language": "invalid_lang", "voice_id": "default"},
                "expected_status": [400, 422]
            },
            {
                "name": "Missing Required Fields",
                "data": {"language": "en"},
                "expected_status": [400, 422]
            },
            {
                "name": "Extremely Long Text",
                "data": {"text": "A" * 10000, "language": "en", "voice_id": "default"},
                "expected_status": [400, 413, 422]
            }
        ]
        
        results = []
        
        for case in test_cases:
            start_time = time.time()
            test_name = f"Error Handling - {case['name']}"
            
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v1/voice/tts",
                    json=case["data"]
                ) as response:
                    duration = time.time() - start_time
                    
                    if response.status in case["expected_status"]:
                        result = {
                            "status": "PASSED",
                            "test": test_name,
                            "duration": duration,
                            "expected_status": case["expected_status"],
                            "actual_status": response.status,
                            "message": "Error handled correctly"
                        }
                        self.test_results["passed"] += 1
                    else:
                        result = {
                            "status": "FAILED",
                            "test": test_name,
                            "duration": duration,
                            "expected_status": case["expected_status"],
                            "actual_status": response.status,
                            "error": "Unexpected status code"
                        }
                        self.test_results["failed"] += 1
                        
            except Exception as e:
                result = {
                    "status": "FAILED",
                    "test": test_name,
                    "duration": time.time() - start_time,
                    "error": str(e)
                }
                self.test_results["failed"] += 1
            
            self.test_results["total_tests"] += 1
            results.append(result)
            logger.info(f"{test_name}: {result['status']} - {result.get('message', result.get('error'))}")
        
        self.test_results["error_handling"].extend(results)
        return results
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices from the service."""
        try:
            async with self.session.get(f"{self.base_url}/api/v1/voice/voices") as response:
                if response.status == 200:
                    voices_data = await response.json()
                    logger.info(f"Available voices: {len(voices_data.get('voices', []))}")
                    return voices_data
                else:
                    logger.error(f"Failed to get voices: HTTP {response.status}")
                    return {}
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return {}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        success_rate = (self.test_results["passed"] / self.test_results["total_tests"] * 100) if self.test_results["total_tests"] > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": self.test_results["total_tests"],
                "passed": self.test_results["passed"],
                "failed": self.test_results["failed"],
                "success_rate": f"{success_rate:.1f}%"
            },
            "category_results": {
                "voice_synthesis": len([t for t in self.test_results["voice_synthesis"] if t["status"] == "PASSED"]),
                "voice_cloning": len([t for t in self.test_results["voice_cloning"] if t["status"] == "PASSED"]),
                "multi_language": len([t for t in self.test_results["multi_language"] if t["status"] == "PASSED"]),
                "integration": len([t for t in self.test_results["integration"] if t["status"] == "PASSED"]),
                "performance": len([t for t in self.test_results["performance"] if t["status"] == "PASSED"]),
                "error_handling": len([t for t in self.test_results["error_handling"] if t["status"] == "PASSED"])
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if self.test_results["failed"] > 0:
            recommendations.append("Review failed tests and address underlying issues")
        
        voice_cloning_passed = any(t["status"] == "PASSED" for t in self.test_results["voice_cloning"])
        if not voice_cloning_passed:
            recommendations.append("Voice cloning functionality needs implementation or debugging")
        
        multi_lang_passed = sum(1 for t in self.test_results["multi_language"] if t["status"] == "PASSED")
        if multi_lang_passed < 3:
            recommendations.append("Multi-language support needs improvement")
        
        performance_issues = any("duration" in t and t.get("duration", 0) > 10 for category in self.test_results.values() if isinstance(category, list) for t in category)
        if performance_issues:
            recommendations.append("Consider optimizing response times for better performance")
        
        if not recommendations:
            recommendations.append("All tests passing! Voice service is functioning well with free/open-source tools")
        
        return recommendations

async def main():
    """Main test execution function."""
    print("🎙️ Voice Service Comprehensive Testing")
    print("=====================================")
    print("Testing free/open-source voice synthesis and cloning capabilities")
    print()
    
    # Test configuration
    voice_service_url = os.getenv("VOICE_SERVICE_URL", "http://localhost:8011")
    
    async with VoiceServiceTester(voice_service_url) as tester:
        # Check service health
        print("🔍 Checking voice service health...")
        if not await tester.check_service_health():
            print("❌ Voice service is not available. Please start the service first.")
            return
        
        print("✅ Voice service is healthy")
        print()
        
        # Get available voices
        print("🔍 Getting available voices...")
        voices = await tester.get_available_voices()
        if voices:
            print(f"✅ Found {len(voices.get('voices', []))} available voices")
            if voices.get('supports_cloning'):
                print("✅ Voice cloning supported")
        print()
        
        # Run comprehensive tests
        print("🧪 Running comprehensive voice service tests...")
        print()
        
        # Basic TTS test
        print("1. Testing basic text-to-speech...")
        await tester.test_basic_tts()
        
        # Multi-language TTS tests
        print("2. Testing multi-language support...")
        await tester.test_multi_language_tts()
        
        # Voice cloning test
        print("3. Testing voice cloning...")
        await tester.test_voice_cloning()
        
        # Translation integration test
        print("4. Testing translation integration...")
        await tester.test_translation_integration()
        
        # Performance tests
        print("5. Testing performance...")
        await tester.test_performance_metrics()
        
        # Error handling tests
        print("6. Testing error handling...")
        await tester.test_error_handling()
        
        # Generate and display report
        print("\n📊 Generating test report...")
        report = tester.generate_report()
        
        print("\n" + "="*50)
        print("VOICE SERVICE TEST REPORT")
        print("="*50)
        print(f"Total Tests: {report['test_summary']['total_tests']}")
        print(f"Passed: {report['test_summary']['passed']}")
        print(f"Failed: {report['test_summary']['failed']}")
        print(f"Success Rate: {report['test_summary']['success_rate']}")
        print()
        
        print("Category Results:")
        for category, count in report['category_results'].items():
            category_total = len(report['detailed_results'][category])
            if category_total > 0:
                category_rate = (count / category_total) * 100
                print(f"  {category.replace('_', ' ').title()}: {count}/{category_total} ({category_rate:.1f}%)")
        print()
        
        print("Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        print()
        
        # Save detailed report
        report_file = f"voice_service_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {report_file}")
        
        # Summary
        if report['test_summary']['failed'] == 0:
            print("\n🎉 All tests passed! Voice service is working perfectly with free/open-source tools.")
        else:
            print(f"\n⚠️  {report['test_summary']['failed']} test(s) failed. Check the detailed report for issues.")

if __name__ == "__main__":
    asyncio.run(main())
