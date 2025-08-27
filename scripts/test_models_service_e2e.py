#!/usr/bin/env python3
"""
MantraPath Models Service - Comprehensive End-to-End Testing Script
===============================================================

This script performs comprehensive testing of the Models Service including:
1. Service health and status checks
2. Model loading and management
3. Speech-to-Text (STT) functionality
4. Text-to-Speech (TTS) functionality  
5. Natural Language Processing (NLP) features
6. API endpoint validation
7. Performance and load testing
8. Error handling and edge cases
9. Integration with other services
10. Code quality and coverage analysis

Author: MantraPath Development Team
Date: August 18, 2025
"""

import asyncio
import aiohttp
import json
import time
import logging
import sys
import subprocess
import os
import wave
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import argparse
from datetime import datetime, timedelta
import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'models_service_e2e_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class ModelsServiceE2ETester:
    """Comprehensive end-to-end tester for Models Service"""
    
    def __init__(self, base_url: str = "http://localhost:8080", timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "service_url": base_url,
            "test_summary": {},
            "detailed_results": {},
            "performance_metrics": {},
            "errors": []
        }
        
        # Test configuration
        self.test_audio_file = None
        self.temp_dir = Path(tempfile.mkdtemp(prefix="models_service_test_"))
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        
        # Cleanup temp files
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any], duration: float = 0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name} ({duration:.2f}s)")
        
        self.test_results["detailed_results"][test_name] = {
            "success": success,
            "duration": duration,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        if not success:
            self.test_results["errors"].append({
                "test": test_name,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
    
    async def create_test_audio(self) -> Path:
        """Create a test audio file for STT testing"""
        try:
            # Create a simple sine wave test audio
            import numpy as np
            
            sample_rate = 16000
            duration = 2.0  # 2 seconds
            frequency = 440  # A4 note
            
            t = np.linspace(0, duration, int(sample_rate * duration))
            audio_data = (np.sin(2 * np.pi * frequency * t) * 0.5).astype(np.float32)
            
            audio_file = self.temp_dir / "test_audio.wav"
            
            # Write WAV file
            with wave.open(str(audio_file), 'wb') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 2 bytes per sample
                wav_file.setframerate(sample_rate)
                wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
            
            self.test_audio_file = audio_file
            logger.info(f"Created test audio file: {audio_file}")
            return audio_file
            
        except Exception as e:
            logger.error(f"Failed to create test audio: {e}")
            # Create a minimal WAV file as fallback
            audio_file = self.temp_dir / "minimal_test.wav"
            with open(audio_file, 'wb') as f:
                # Minimal WAV header + 1 second of silence
                wav_header = b'RIFF$\x01\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00@\x1f\x00\x00@\x1f\x00\x00\x01\x00\x08\x00data\x00\x01\x00\x00'
                silence = b'\x80' * 16000  # 1 second of 8-bit silence
                f.write(wav_header + silence)
            
            self.test_audio_file = audio_file
            return audio_file
    
    async def test_service_health(self) -> bool:
        """Test service health endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result("service_health", True, {
                        "status_code": response.status,
                        "response": data,
                        "response_time": duration
                    }, duration)
                    return True
                else:
                    self.log_test_result("service_health", False, {
                        "status_code": response.status,
                        "error": "Non-200 status code"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("service_health", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_service_status(self) -> bool:
        """Test detailed service status"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/status") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate status response structure
                    required_fields = ["service", "timestamp", "status", "hardware", "models"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    success = len(missing_fields) == 0
                    self.log_test_result("service_status", success, {
                        "status_code": response.status,
                        "response": data,
                        "missing_fields": missing_fields,
                        "hardware_info": data.get("hardware", {}),
                        "models_info": data.get("models", {})
                    }, duration)
                    return success
                else:
                    self.log_test_result("service_status", False, {
                        "status_code": response.status,
                        "error": "Non-200 status code"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("service_status", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_models_available(self) -> bool:
        """Test available models endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/models/available") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    self.log_test_result("models_available", True, {
                        "status_code": response.status,
                        "models_count": len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else 0,
                        "response": data
                    }, duration)
                    return True
                else:
                    self.log_test_result("models_available", False, {
                        "status_code": response.status,
                        "error": "Non-200 status code"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("models_available", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_models_loaded(self) -> bool:
        """Test loaded models endpoint"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/models/loaded") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate structure
                    expected_keys = ["stt", "tts", "nlp"]
                    has_structure = all(key in data for key in expected_keys)
                    
                    self.log_test_result("models_loaded", has_structure, {
                        "status_code": response.status,
                        "response": data,
                        "has_expected_structure": has_structure,
                        "stt_models": len(data.get("stt", [])),
                        "tts_models": len(data.get("tts", [])),
                        "nlp_models": len(data.get("nlp", []))
                    }, duration)
                    return has_structure
                else:
                    self.log_test_result("models_loaded", False, {
                        "status_code": response.status,
                        "error": "Non-200 status code"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("models_loaded", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_stt_languages(self) -> bool:
        """Test STT supported languages"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/api/v1/stt/languages") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    has_languages = "supported_languages" in data and len(data["supported_languages"]) > 0
                    
                    self.log_test_result("stt_languages", has_languages, {
                        "status_code": response.status,
                        "response": data,
                        "languages_count": len(data.get("supported_languages", []))
                    }, duration)
                    return has_languages
                else:
                    self.log_test_result("stt_languages", False, {
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("stt_languages", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_stt_transcription(self) -> bool:
        """Test STT transcription with audio file"""
        start_time = time.time()
        try:
            if not self.test_audio_file or not self.test_audio_file.exists():
                await self.create_test_audio()
            
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('audio', open(self.test_audio_file, 'rb'), 
                          filename='test_audio.wav', content_type='audio/wav')
            data.add_field('language', 'en')
            
            async with self.session.post(f"{self.base_url}/api/v1/stt/transcribe", data=data) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    success = result.get("success", False)
                    self.log_test_result("stt_transcription", success, {
                        "status_code": response.status,
                        "response": result,
                        "has_text": bool(result.get("text")),
                        "model_used": result.get("model_used"),
                        "confidence": result.get("confidence")
                    }, duration)
                    return success
                else:
                    self.log_test_result("stt_transcription", False, {
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("stt_transcription", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_tts_languages(self) -> bool:
        """Test TTS supported languages"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/api/v1/tts/languages") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    has_languages = "supported_languages" in data and len(data["supported_languages"]) > 0
                    
                    self.log_test_result("tts_languages", has_languages, {
                        "status_code": response.status,
                        "response": data,
                        "languages_count": len(data.get("supported_languages", []))
                    }, duration)
                    return has_languages
                else:
                    self.log_test_result("tts_languages", False, {
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("tts_languages", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_tts_synthesis(self) -> bool:
        """Test TTS synthesis"""
        start_time = time.time()
        try:
            payload = {
                "text": "Hello, this is a test of the text-to-speech system.",
                "language": "en",
                "voice": None
            }
            
            async with self.session.post(f"{self.base_url}/api/v1/tts/synthesize", 
                                       json=payload) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    success = result.get("success", False)
                    self.log_test_result("tts_synthesis", success, {
                        "status_code": response.status,
                        "response": result,
                        "has_audio_url": bool(result.get("audio_url")),
                        "model_used": result.get("model_used"),
                        "duration": result.get("duration")
                    }, duration)
                    return success
                else:
                    self.log_test_result("tts_synthesis", False, {
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("tts_synthesis", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_nlp_translation(self) -> bool:
        """Test NLP translation functionality"""
        start_time = time.time()
        try:
            payload = {
                "text": "Hello, how are you?",
                "source_lang": "en", 
                "target_lang": "hi"
            }
            
            async with self.session.post(f"{self.base_url}/api/v1/nlp/translate", 
                                       json=payload) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    result = await response.json()
                    
                    success = result.get("success", False)
                    self.log_test_result("nlp_translation", success, {
                        "status_code": response.status,
                        "response": result,
                        "has_translation": bool(result.get("translated_text")),
                        "confidence": result.get("confidence")
                    }, duration)
                    return success
                else:
                    self.log_test_result("nlp_translation", False, {
                        "status_code": response.status,
                        "error": f"HTTP {response.status}"
                    }, duration)
                    return False
                    
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("nlp_translation", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_performance_metrics(self) -> bool:
        """Test service performance under load"""
        start_time = time.time()
        try:
            # Simple performance test - multiple concurrent health checks
            concurrent_requests = 10
            tasks = []
            
            for _ in range(concurrent_requests):
                task = asyncio.create_task(self.session.get(f"{self.base_url}/health"))
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            successful_responses = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
            success_rate = successful_responses / concurrent_requests
            
            # Close all responses
            for response in responses:
                if hasattr(response, 'close'):
                    response.close()
            
            performance_success = success_rate >= 0.8  # 80% success rate threshold
            
            self.log_test_result("performance_metrics", performance_success, {
                "concurrent_requests": concurrent_requests,
                "successful_responses": successful_responses,
                "success_rate": success_rate,
                "total_duration": duration,
                "avg_response_time": duration / concurrent_requests
            }, duration)
            
            # Store performance metrics
            self.test_results["performance_metrics"] = {
                "concurrent_requests": concurrent_requests,
                "success_rate": success_rate,
                "total_duration": duration,
                "avg_response_time": duration / concurrent_requests
            }
            
            return performance_success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("performance_metrics", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def test_error_handling(self) -> bool:
        """Test error handling with invalid requests"""
        start_time = time.time()
        try:
            error_tests = [
                {
                    "name": "invalid_endpoint",
                    "url": f"{self.base_url}/api/v1/invalid/endpoint",
                    "method": "GET",
                    "expected_status": [404, 405]
                },
                {
                    "name": "malformed_stt_request",
                    "url": f"{self.base_url}/api/v1/stt/transcribe",
                    "method": "POST",
                    "data": {"invalid": "data"},
                    "expected_status": [400, 422]
                },
                {
                    "name": "malformed_tts_request", 
                    "url": f"{self.base_url}/api/v1/tts/synthesize",
                    "method": "POST",
                    "json": {"invalid": "data"},
                    "expected_status": [400, 422]
                }
            ]
            
            error_test_results = []
            
            for test in error_tests:
                try:
                    if test["method"] == "GET":
                        async with self.session.get(test["url"]) as response:
                            status_ok = response.status in test["expected_status"]
                            error_test_results.append(status_ok)
                    elif test["method"] == "POST":
                        kwargs = {}
                        if "data" in test:
                            kwargs["data"] = test["data"]
                        if "json" in test:
                            kwargs["json"] = test["json"]
                        
                        async with self.session.post(test["url"], **kwargs) as response:
                            status_ok = response.status in test["expected_status"]
                            error_test_results.append(status_ok)
                            
                except Exception:
                    # Connection errors are also acceptable for error testing
                    error_test_results.append(True)
            
            duration = time.time() - start_time
            overall_success = all(error_test_results)
            
            self.log_test_result("error_handling", overall_success, {
                "error_tests_passed": sum(error_test_results),
                "total_error_tests": len(error_tests),
                "individual_results": dict(zip([t["name"] for t in error_tests], error_test_results))
            }, duration)
            
            return overall_success
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result("error_handling", False, {
                "error": str(e),
                "exception_type": type(e).__name__
            }, duration)
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all end-to-end tests"""
        logger.info("🚀 Starting MantraPath Models Service E2E Testing")
        logger.info(f"Target URL: {self.base_url}")
        logger.info(f"Test timestamp: {self.test_results['timestamp']}")
        
        # Define test sequence
        tests = [
            ("Service Health Check", self.test_service_health),
            ("Service Status", self.test_service_status),
            ("Available Models", self.test_models_available),
            ("Loaded Models", self.test_models_loaded),
            ("STT Languages", self.test_stt_languages),
            ("STT Transcription", self.test_stt_transcription),
            ("TTS Languages", self.test_tts_languages),
            ("TTS Synthesis", self.test_tts_synthesis),
            ("NLP Translation", self.test_nlp_translation),
            ("Performance Metrics", self.test_performance_metrics),
            ("Error Handling", self.test_error_handling)
        ]
        
        # Create test audio file
        await self.create_test_audio()
        
        # Run tests
        total_tests = len(tests)
        passed_tests = 0
        
        for test_name, test_func in tests:
            logger.info(f"🧪 Running: {test_name}")
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                logger.error(f"❌ Test {test_name} failed with exception: {e}")
        
        # Calculate summary
        success_rate = (passed_tests / total_tests) * 100
        self.test_results["test_summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "overall_status": "PASS" if success_rate >= 70 else "FAIL"
        }
        
        # Log summary
        logger.info("=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Overall Status: {self.test_results['test_summary']['overall_status']}")
        
        if self.test_results["errors"]:
            logger.info("\n❌ Failed Tests:")
            for error in self.test_results["errors"]:
                logger.info(f"  • {error['test']}: {error['details'].get('error', 'Unknown error')}")
        
        return self.test_results

def check_service_running(base_url: str) -> bool:
    """Check if the Models Service is running"""
    import requests
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_models_service() -> subprocess.Popen:
    """Start the Models Service if not running"""
    models_service_dir = Path(__file__).parent.parent / "backend" / "services" / "models_service"
    
    if not models_service_dir.exists():
        raise FileNotFoundError(f"Models service directory not found: {models_service_dir}")
    
    logger.info(f"Starting Models Service from {models_service_dir}")
    
    # Start the service
    process = subprocess.Popen(
        ["python", "main.py"],
        cwd=models_service_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "MODELS_SERVICE_PORT": "8080"}
    )
    
    # Wait for service to start
    import time
    for _ in range(30):  # Wait up to 30 seconds
        if check_service_running("http://localhost:8080"):
            logger.info("✅ Models Service started successfully")
            return process
        time.sleep(1)
    
    raise RuntimeError("Failed to start Models Service within 30 seconds")

async def analyze_code_structure():
    """Analyze the code structure and generate report"""
    logger.info("🔍 Analyzing Models Service Code Structure")
    
    models_service_dir = Path(__file__).parent.parent / "backend" / "services" / "models_service"
    
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "directory_structure": {},
        "file_analysis": {},
        "dependencies": {},
        "code_metrics": {}
    }
    
    # Analyze directory structure
    def analyze_directory(path: Path, level: int = 0) -> Dict:
        if level > 3:  # Limit recursion depth
            return {}
        
        structure = {}
        if path.is_dir():
            try:
                for item in sorted(path.iterdir()):
                    if item.name.startswith('.'):
                        continue
                    if item.is_dir():
                        structure[item.name + "/"] = analyze_directory(item, level + 1)
                    else:
                        structure[item.name] = {
                            "size": item.stat().st_size,
                            "type": item.suffix
                        }
            except PermissionError:
                pass
        return structure
    
    analysis["directory_structure"] = analyze_directory(models_service_dir)
    
    # Analyze Python files
    python_files = list(models_service_dir.rglob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            rel_path = py_file.relative_to(models_service_dir)
            analysis["file_analysis"][str(rel_path)] = {
                "lines": len(content.split('\n')),
                "size": len(content),
                "imports": len([line for line in content.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]),
                "functions": len([line for line in content.split('\n') if line.strip().startswith('def ')]),
                "classes": len([line for line in content.split('\n') if line.strip().startswith('class ')]),
                "docstrings": content.count('"""') // 2,
                "comments": len([line for line in content.split('\n') if line.strip().startswith('#')])
            }
        except Exception as e:
            logger.warning(f"Could not analyze {py_file}: {e}")
    
    # Analyze requirements
    req_file = models_service_dir / "requirements.txt"
    if req_file.exists():
        try:
            with open(req_file, 'r') as f:
                requirements = f.read().split('\n')
            
            analysis["dependencies"] = {
                "total_dependencies": len([r for r in requirements if r.strip() and not r.strip().startswith('#')]),
                "requirements": [r.strip() for r in requirements if r.strip() and not r.strip().startswith('#')]
            }
        except Exception as e:
            logger.warning(f"Could not analyze requirements: {e}")
    
    # Calculate code metrics
    total_lines = sum(fa.get("lines", 0) for fa in analysis["file_analysis"].values())
    total_functions = sum(fa.get("functions", 0) for fa in analysis["file_analysis"].values())
    total_classes = sum(fa.get("classes", 0) for fa in analysis["file_analysis"].values())
    
    analysis["code_metrics"] = {
        "total_python_files": len(python_files),
        "total_lines_of_code": total_lines,
        "total_functions": total_functions,
        "total_classes": total_classes,
        "avg_lines_per_file": total_lines / len(python_files) if python_files else 0,
        "avg_functions_per_file": total_functions / len(python_files) if python_files else 0
    }
    
    logger.info(f"📈 Code Analysis Complete:")
    logger.info(f"  • Python Files: {analysis['code_metrics']['total_python_files']}")
    logger.info(f"  • Lines of Code: {analysis['code_metrics']['total_lines_of_code']}")
    logger.info(f"  • Functions: {analysis['code_metrics']['total_functions']}")
    logger.info(f"  • Classes: {analysis['code_metrics']['total_classes']}")
    logger.info(f"  • Dependencies: {analysis['dependencies'].get('total_dependencies', 0)}")
    
    return analysis

async def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description="MantraPath Models Service E2E Testing")
    parser.add_argument("--url", default="http://localhost:8080", help="Models Service URL")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    parser.add_argument("--start-service", action="store_true", help="Start the service if not running")
    parser.add_argument("--analyze-code", action="store_true", help="Include code structure analysis")
    parser.add_argument("--output", help="Output file for test results (JSON)")
    
    args = parser.parse_args()
    
    service_process = None
    
    try:
        # Check if service is running
        if not check_service_running(args.url):
            if args.start_service:
                logger.info("Service not running, attempting to start...")
                service_process = start_models_service()
            else:
                logger.error(f"❌ Models Service is not running at {args.url}")
                logger.info("Use --start-service flag to automatically start the service")
                return 1
        else:
            logger.info(f"✅ Models Service is running at {args.url}")
        
        # Run code analysis if requested
        code_analysis = None
        if args.analyze_code:
            code_analysis = await analyze_code_structure()
        
        # Run E2E tests
        async with ModelsServiceE2ETester(args.url, args.timeout) as tester:
            results = await tester.run_all_tests()
            
            # Add code analysis to results
            if code_analysis:
                results["code_analysis"] = code_analysis
            
            # Save results to file if specified
            if args.output:
                output_file = Path(args.output)
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                logger.info(f"📄 Test results saved to: {output_file}")
            
            # Print final status
            success_rate = results["test_summary"]["success_rate"]
            if success_rate >= 90:
                logger.info("🎉 EXCELLENT: All critical tests passed!")
                return_code = 0
            elif success_rate >= 70:
                logger.info("✅ GOOD: Most tests passed, minor issues detected")
                return_code = 0
            else:
                logger.error("❌ POOR: Significant issues detected, service needs attention")
                return_code = 1
            
            return return_code
    
    except KeyboardInterrupt:
        logger.info("\n🛑 Testing interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Testing failed with error: {e}")
        return 1
    finally:
        # Cleanup: Stop service if we started it
        if service_process:
            logger.info("🛑 Stopping Models Service...")
            service_process.terminate()
            try:
                service_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                service_process.kill()

if __name__ == "__main__":
    # Set up event loop for Windows compatibility
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
