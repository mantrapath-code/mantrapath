#!/usr/bin/env python3
"""
MantraPath Translation Service - Enhanced Testing Script
========================================================

Comprehensive testing script for translation service with language auto-detection
and translation capabilities. Tests multiple scenarios and languages.

Usage:
    python test_translation_service.py                    # Basic health check
    python test_translation_service.py --full             # Full test suite
    python test_translation_service.py --auto-detect      # Focus on auto-detection
    python test_translation_service.py --translations     # Focus on translations
    python test_translation_service.py --monitor          # Continuous monitoring
    python test_translation_service.py --performance      # Performance testing
    python test_translation_service.py --verbose          # Detailed output

Features:
- Auto language detection testing
- Multi-language translation testing
- Performance benchmarking
- Error handling validation
- Continuous monitoring mode
- Indian languages focus testing
"""

import asyncio
import aiohttp
import time
import json
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    success: bool
    duration: float
    details: Dict
    error: Optional[str] = None

@dataclass
class TranslationTestCase:
    """Translation test case"""
    name: str
    text: str
    expected_source_lang: Optional[str]
    target_lang: str
    expected_translation_contains: Optional[List[str]] = None
    should_auto_detect: bool = True

class TranslationServiceTester:
    """Comprehensive tester for translation service"""
    
    def __init__(self, base_url: str = "http://localhost:8010"):
        self.base_url = base_url
        self.session = None
        self.test_results: List[TestResult] = []
        
        # Test cases for various scenarios
        self.test_cases = [
            # English to other languages
            TranslationTestCase(
                name="English to Hindi",
                text="Hello, how are you today?",
                expected_source_lang="en",
                target_lang="hi",
                expected_translation_contains=["नमस्ते", "कैसे", "आज"]
            ),
            TranslationTestCase(
                name="English to Spanish",
                text="Good morning, I hope you have a wonderful day!",
                expected_source_lang="en",
                target_lang="es",
                expected_translation_contains=["Buenos", "mañana", "día"]
            ),
            TranslationTestCase(
                name="English to French",
                text="Thank you for your help with this project.",
                expected_source_lang="en",
                target_lang="fr",
                expected_translation_contains=["Merci", "aide", "projet"]
            ),
            
            # Indian languages to English
            TranslationTestCase(
                name="Hindi to English",
                text="नमस्ते, आप कैसे हैं? आज मौसम बहुत अच्छा है।",
                expected_source_lang="hi",
                target_lang="en",
                expected_translation_contains=["hello", "how", "weather", "good"]
            ),
            TranslationTestCase(
                name="Tamil to English", 
                text="வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? இன்று நல்ல நாள்.",
                expected_source_lang="ta",
                target_lang="en",
                expected_translation_contains=["hello", "how", "good", "day"]
            ),
            TranslationTestCase(
                name="Bengali to English",
                text="নমস্কার, আপনি কেমন আছেন? আজকের দিনটি খুব সুন্দর।",
                expected_source_lang="bn",
                target_lang="en",
                expected_translation_contains=["hello", "how", "beautiful", "day"]
            ),
            
            # Cross-language (non-English)
            TranslationTestCase(
                name="Spanish to Hindi",
                text="Hola, ¿cómo estás? Espero que tengas un buen día.",
                expected_source_lang="es",
                target_lang="hi",
                expected_translation_contains=["नमस्ते", "कैसे", "दिन"]
            ),
            
            # Short text detection
            TranslationTestCase(
                name="Short English text",
                text="Hello",
                expected_source_lang="en",
                target_lang="hi"
            ),
            TranslationTestCase(
                name="Short Hindi text",
                text="नमस्ते",
                expected_source_lang="hi", 
                target_lang="en"
            ),
            
            # Mixed content
            TranslationTestCase(
                name="Mixed English-Hindi",
                text="Hello दोस्त, how are you आज?",
                expected_source_lang=None,  # Could be either
                target_lang="es"
            ),
            
            # Technical/Domain specific
            TranslationTestCase(
                name="Technical English",
                text="The API endpoint returned a 404 error with JSON response data.",
                expected_source_lang="en",
                target_lang="hi"
            ),
            
            # Emotional/Mental health context
            TranslationTestCase(
                name="Mental health context",
                text="I'm feeling anxious today and need some support and guidance.",
                expected_source_lang="en",
                target_lang="hi",
                expected_translation_contains=["चिंतित", "सहायता", "मार्गदर्शन"]
            ),
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def health_check(self) -> TestResult:
        """Basic health check"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return TestResult(
                        test_name="Health Check",
                        success=True,
                        duration=duration,
                        details={
                            "status": data.get("status"),
                            "service": data.get("service"),
                            "version": data.get("version"),
                            "response_time_ms": round(duration * 1000, 2)
                        }
                    )
                else:
                    return TestResult(
                        test_name="Health Check",
                        success=False,
                        duration=duration,
                        details={"status_code": response.status},
                        error=f"HTTP {response.status}"
                    )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Health Check",
                success=False,
                duration=duration,
                details={},
                error=str(e)
            )

    async def test_supported_languages(self) -> TestResult:
        """Test supported languages endpoint"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{self.base_url}/languages") as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    supported_langs = data.get("supported_languages", [])
                    indian_langs = data.get("indian_languages", [])
                    
                    return TestResult(
                        test_name="Supported Languages",
                        success=True,
                        duration=duration,
                        details={
                            "total_supported": len(supported_langs),
                            "indian_languages": len(indian_langs),
                            "has_english": "en" in supported_langs,
                            "has_hindi": "hi" in supported_langs,
                            "sample_supported": supported_langs[:10] if supported_langs else [],
                            "response_time_ms": round(duration * 1000, 2)
                        }
                    )
                else:
                    return TestResult(
                        test_name="Supported Languages",
                        success=False,
                        duration=duration,
                        details={"status_code": response.status},
                        error=f"HTTP {response.status}"
                    )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name="Supported Languages",
                success=False,
                duration=duration,
                details={},
                error=str(e)
            )

    async def test_auto_detection_and_translation(self, test_case: TranslationTestCase) -> TestResult:
        """Test auto-detection and translation for a specific case"""
        start_time = time.time()
        
        try:
            payload = {
                "text": test_case.text,
                "source_language": "auto",  # Auto-detect
                "target_language": test_case.target_lang
            }
            
            async with self.session.post(
                f"{self.base_url}/translate",
                json=payload
            ) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Validate response structure
                    required_fields = ["translated_text", "source_language", "target_language", "confidence_score", "engine"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        return TestResult(
                            test_name=test_case.name,
                            success=False,
                            duration=duration,
                            details=data,
                            error=f"Missing required fields: {missing_fields}"
                        )
                    
                    # Check if source language detection is reasonable
                    detected_lang = data["source_language"]
                    lang_detection_ok = True
                    lang_detection_note = ""
                    
                    if test_case.expected_source_lang:
                        if detected_lang != test_case.expected_source_lang:
                            lang_detection_ok = False
                            lang_detection_note = f"Expected {test_case.expected_source_lang}, got {detected_lang}"
                    
                    # Check if translation contains expected terms (if specified)
                    translation_quality_ok = True
                    translation_note = ""
                    
                    if test_case.expected_translation_contains:
                        translated_text = data["translated_text"].lower()
                        found_terms = [term for term in test_case.expected_translation_contains 
                                     if term.lower() in translated_text]
                        
                        if not found_terms:
                            translation_quality_ok = False
                            translation_note = f"Translation doesn't contain expected terms: {test_case.expected_translation_contains}"
                    
                    success = (response.status == 200 and 
                             not missing_fields and 
                             data["translated_text"] and 
                             data["confidence_score"] > 0)
                    
                    return TestResult(
                        test_name=test_case.name,
                        success=success,
                        duration=duration,
                        details={
                            "original_text": test_case.text,
                            "translated_text": data["translated_text"],
                            "detected_source": detected_lang,
                            "expected_source": test_case.expected_source_lang,
                            "target_language": data["target_language"],
                            "confidence_score": data["confidence_score"],
                            "engine": data["engine"],
                            "processing_time_ms": data.get("processing_time_ms", 0),
                            "cache_hit": data.get("cache_hit", False),
                            "language_detection_accurate": lang_detection_ok,
                            "language_detection_note": lang_detection_note,
                            "translation_quality_ok": translation_quality_ok,
                            "translation_note": translation_note,
                            "response_time_ms": round(duration * 1000, 2)
                        }
                    )
                else:
                    response_text = await response.text()
                    return TestResult(
                        test_name=test_case.name,
                        success=False,
                        duration=duration,
                        details={
                            "status_code": response.status,
                            "response_text": response_text
                        },
                        error=f"HTTP {response.status}"
                    )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_case.name,
                success=False,
                duration=duration,
                details={"original_text": test_case.text},
                error=str(e)
            )

    async def test_error_handling(self) -> List[TestResult]:
        """Test error handling scenarios"""
        error_tests = [
            {
                "name": "Empty Text",
                "payload": {"text": "", "target_language": "hi"},
                "expected_to_fail": True
            },
            {
                "name": "Very Long Text",
                "payload": {
                    "text": "A" * 10000,  # Very long text
                    "target_language": "hi"
                },
                "expected_to_fail": False  # Should handle gracefully
            },
            {
                "name": "Unsupported Target Language",
                "payload": {
                    "text": "Hello world",
                    "target_language": "xyz"  # Invalid language
                },
                "expected_to_fail": True
            },
            {
                "name": "Special Characters Only",
                "payload": {
                    "text": "!@#$%^&*()",
                    "target_language": "hi"
                },
                "expected_to_fail": False  # Should handle gracefully
            },
            {
                "name": "Numbers Only",
                "payload": {
                    "text": "12345 67890",
                    "target_language": "hi"
                },
                "expected_to_fail": False  # Should handle gracefully
            }
        ]
        
        results = []
        
        for test in error_tests:
            start_time = time.time()
            
            try:
                async with self.session.post(
                    f"{self.base_url}/translate",
                    json=test["payload"]
                ) as response:
                    duration = time.time() - start_time
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()
                    
                    # Determine if test passed based on expectation
                    if test["expected_to_fail"]:
                        success = response.status != 200
                    else:
                        success = response.status == 200
                    
                    results.append(TestResult(
                        test_name=f"Error Handling - {test['name']}",
                        success=success,
                        duration=duration,
                        details={
                            "payload": test["payload"],
                            "status_code": response.status,
                            "response": response_data,
                            "expected_to_fail": test["expected_to_fail"],
                            "response_time_ms": round(duration * 1000, 2)
                        }
                    ))
            except Exception as e:
                duration = time.time() - start_time
                # For expected failures, exceptions might be ok
                success = test["expected_to_fail"]
                
                results.append(TestResult(
                    test_name=f"Error Handling - {test['name']}",
                    success=success,
                    duration=duration,
                    details={"payload": test["payload"]},
                    error=str(e)
                ))
        
        return results

    async def performance_test(self, num_requests: int = 10) -> TestResult:
        """Run performance tests with multiple concurrent requests"""
        start_time = time.time()
        
        test_text = "Hello, this is a performance test for the translation service."
        tasks = []
        
        for i in range(num_requests):
            task = self.session.post(
                f"{self.base_url}/translate",
                json={
                    "text": f"{test_text} Request {i+1}",
                    "source_language": "auto",
                    "target_language": "hi"
                }
            )
            tasks.append(task)
        
        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            total_duration = time.time() - start_time
            
            success_count = 0
            error_count = 0
            response_times = []
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    error_count += 1
                else:
                    if response.status == 200:
                        success_count += 1
                    else:
                        error_count += 1
                    
                    # For individual response time, we'd need to track separately
                    # For now, we'll use average
                    response_times.append(total_duration / num_requests)
            
            avg_response_time = statistics.mean(response_times) if response_times else 0
            
            return TestResult(
                test_name=f"Performance Test ({num_requests} requests)",
                success=success_count > 0,
                duration=total_duration,
                details={
                    "total_requests": num_requests,
                    "successful_requests": success_count,
                    "failed_requests": error_count,
                    "success_rate": success_count / num_requests * 100,
                    "total_duration_seconds": round(total_duration, 2),
                    "average_response_time_seconds": round(avg_response_time, 3),
                    "requests_per_second": round(num_requests / total_duration, 2)
                }
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=f"Performance Test ({num_requests} requests)",
                success=False,
                duration=duration,
                details={"total_requests": num_requests},
                error=str(e)
            )

    def print_test_result(self, result: TestResult, verbose: bool = False):
        """Print a single test result"""
        status = "✅ PASS" if result.success else "❌ FAIL"
        duration_ms = round(result.duration * 1000, 2)
        
        print(f"{status} {result.test_name} ({duration_ms}ms)")
        
        if result.error:
            print(f"   Error: {result.error}")
        
        if verbose or not result.success:
            print(f"   Details: {json.dumps(result.details, indent=2, ensure_ascii=False)}")
        
        print()

    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r.duration for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        print("="*60)
        print("TRANSLATION SERVICE TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "N/A")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Average Test Duration: {avg_duration:.3f}s")
        print("="*60)
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result.success:
                    print(f"  - {result.test_name}: {result.error or 'Unknown error'}")

    async def run_basic_tests(self, verbose: bool = False):
        """Run basic test suite"""
        print("🚀 Running Basic Translation Service Tests...\n")
        
        # Health check
        result = await self.health_check()
        self.test_results.append(result)
        self.print_test_result(result, verbose)
        
        # Supported languages
        result = await self.test_supported_languages()
        self.test_results.append(result)
        self.print_test_result(result, verbose)
        
        # Quick translation test
        quick_test = TranslationTestCase(
            name="Quick English to Hindi",
            text="Hello world",
            expected_source_lang="en",
            target_lang="hi"
        )
        
        result = await self.test_auto_detection_and_translation(quick_test)
        self.test_results.append(result)
        self.print_test_result(result, verbose)

    async def run_auto_detection_tests(self, verbose: bool = False):
        """Run focused auto-detection tests"""
        print("🔍 Running Auto-Detection Focused Tests...\n")
        
        # Select test cases that focus on language detection
        detection_cases = [tc for tc in self.test_cases 
                          if tc.expected_source_lang and tc.should_auto_detect]
        
        for test_case in detection_cases:
            result = await self.test_auto_detection_and_translation(test_case)
            self.test_results.append(result)
            self.print_test_result(result, verbose)

    async def run_translation_tests(self, verbose: bool = False):
        """Run focused translation tests"""
        print("🌐 Running Translation Focused Tests...\n")
        
        for test_case in self.test_cases:
            result = await self.test_auto_detection_and_translation(test_case)
            self.test_results.append(result)
            self.print_test_result(result, verbose)

    async def run_full_test_suite(self, verbose: bool = False):
        """Run complete test suite"""
        print("🔬 Running Complete Translation Service Test Suite...\n")
        
        # Basic tests
        await self.run_basic_tests(verbose)
        
        # All translation tests
        print("\n" + "="*50)
        print("TRANSLATION AND AUTO-DETECTION TESTS")
        print("="*50)
        
        for test_case in self.test_cases:
            result = await self.test_auto_detection_and_translation(test_case)
            self.test_results.append(result)
            self.print_test_result(result, verbose)
        
        # Error handling tests
        print("\n" + "="*50)
        print("ERROR HANDLING TESTS") 
        print("="*50)
        
        error_results = await self.test_error_handling()
        self.test_results.extend(error_results)
        for result in error_results:
            self.print_test_result(result, verbose)

    async def run_performance_tests(self, verbose: bool = False):
        """Run performance tests"""
        print("⚡ Running Performance Tests...\n")
        
        # Sequential performance test
        result = await self.performance_test(5)
        self.test_results.append(result)
        self.print_test_result(result, verbose)
        
        # Concurrent performance test
        result = await self.performance_test(10)
        self.test_results.append(result)
        self.print_test_result(result, verbose)

    async def monitor_service(self, interval: int = 30):
        """Continuous monitoring mode"""
        print(f"🔄 Starting continuous monitoring (checking every {interval}s)...")
        print("Press Ctrl+C to stop\n")
        
        iteration = 0
        try:
            while True:
                iteration += 1
                print(f"--- Monitoring Check #{iteration} at {datetime.now().strftime('%H:%M:%S')} ---")
                
                # Reset results for this iteration
                self.test_results = []
                
                # Quick health and basic function check
                await self.run_basic_tests(verbose=False)
                
                # Print mini summary
                passed = sum(1 for r in self.test_results if r.success)
                total = len(self.test_results)
                
                if passed == total:
                    print(f"✅ All {total} checks passed")
                else:
                    print(f"⚠️  {total-passed}/{total} checks failed")
                
                print(f"Next check in {interval}s...\n")
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Translation Service Tester")
    parser.add_argument("--full", action="store_true", help="Run full test suite")
    parser.add_argument("--auto-detect", action="store_true", help="Focus on auto-detection tests")
    parser.add_argument("--translations", action="store_true", help="Focus on translation tests")
    parser.add_argument("--monitor", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--url", default="http://localhost:8010", help="Service URL")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    print("🧘‍♀️ MantraPath Translation Service Tester")
    print("=" * 50)
    print(f"Service URL: {args.url}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")
    
    async with TranslationServiceTester(args.url) as tester:
        try:
            if args.monitor:
                await tester.monitor_service(args.interval)
            elif args.full:
                await tester.run_full_test_suite(args.verbose)
            elif args.auto_detect:
                await tester.run_auto_detection_tests(args.verbose)
            elif args.translations:
                await tester.run_translation_tests(args.verbose)
            elif args.performance:
                await tester.run_performance_tests(args.verbose)
            else:
                # Default: basic tests
                await tester.run_basic_tests(args.verbose)
            
            if not args.monitor:
                tester.print_summary()
                
        except KeyboardInterrupt:
            print("\n🛑 Testing interrupted by user")
        except Exception as e:
            print(f"\n❌ Testing failed with error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
