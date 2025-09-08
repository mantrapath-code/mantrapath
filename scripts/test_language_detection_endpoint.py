#!/usr/bin/env python3
"""
Test script for the new /detect-language endpoint
Tests the standalone language detection functionality
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Any

BASE_URL = "http://localhost:8010"

class LanguageDetectionTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    async def test_health(self):
        """Check if the service is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Service is healthy: {data['status']} (v{data['version']})")
                        return True
                    else:
                        print(f"❌ Service health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Cannot connect to service: {e}")
            return False

    async def test_language_detection_endpoint(self):
        """Test the /detect-language endpoint with various texts"""
        print("\n🔍 Testing Language Detection Endpoint...")
        
        test_cases = [
            # Hindi
            {"text": "नमस्ते आप कैसे हैं? मैं आज बहुत खुश हूं।", "expected": "hi", "name": "Hindi"},
            {"text": "मैं भारत से हूं और हिंदी बोलता हूं।", "expected": "hi", "name": "Hindi 2"},
            
            # English
            {"text": "Hello, how are you today? I am feeling great!", "expected": "en", "name": "English"},
            {"text": "The weather is beautiful today in New York.", "expected": "en", "name": "English 2"},
            
            # Bengali
            {"text": "আপনি কেমন আছেন? আমি আজ খুব ভালো আছি।", "expected": "bn", "name": "Bengali"},
            {"text": "আমি বাংলাদেশ থেকে এসেছি।", "expected": "bn", "name": "Bengali 2"},
            
            # Tamil
            {"text": "நீங்கள் எப்படி இருக்கிறீர்கள்? நான் நன்றாக இருக்கிறேன்.", "expected": "ta", "name": "Tamil"},
            
            # Telugu
            {"text": "మీరు ఎలా ఉన్నారు? నేను బాగున్నాను.", "expected": "te", "name": "Telugu"},
            
            # Spanish
            {"text": "Hola, ¿cómo estás? Espero que tengas un buen día.", "expected": "es", "name": "Spanish"},
            
            # French
            {"text": "Bonjour, comment allez-vous? J'espère que vous passez une bonne journée.", "expected": "fr", "name": "French"},
            
            # German
            {"text": "Hallo, wie geht es Ihnen? Ich hoffe, Sie haben einen schönen Tag.", "expected": "de", "name": "German"},
            
            # Japanese
            {"text": "こんにちは、お元気ですか？今日は良い天気ですね。", "expected": "ja", "name": "Japanese"},
            
            # Chinese
            {"text": "你好，你好吗？今天天气很好。", "expected": "zh", "name": "Chinese"},
            
            # Mixed content
            {"text": "Hello नमस्ते", "expected": "mixed", "name": "Mixed Hindi-English"},
        ]
        
        results = []
        correct_predictions = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/detect-language",
                        json={"text": test_case["text"]},
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        response_time = (time.time() - start_time) * 1000  # ms
                        
                        if response.status == 200:
                            result = await response.json()
                            detected = result.get("detected_language", "unknown")
                            confidence = result.get("confidence", 0.0)
                            
                            # Check if prediction is correct (allowing some flexibility)
                            is_correct = (detected == test_case["expected"] or 
                                        (test_case["expected"] == "mixed" and detected in ["hi", "en"]))
                            
                            if is_correct:
                                correct_predictions += 1
                                status_icon = "✅"
                            else:
                                status_icon = "❌"
                            
                            print(f"  {status_icon} Test {i:2d}/{total_tests}: {test_case['name']}")
                            print(f"     Text: '{test_case['text'][:50]}...'")
                            print(f"     Expected: {test_case['expected']}, Detected: {detected}")
                            print(f"     Confidence: {confidence:.2f}, Response time: {response_time:.1f}ms")
                            
                            results.append({
                                "test_name": test_case["name"],
                                "text": test_case["text"],
                                "expected": test_case["expected"],
                                "detected": detected,
                                "confidence": confidence,
                                "response_time_ms": response_time,
                                "correct": is_correct,
                                "status": "success"
                            })
                        else:
                            print(f"  ❌ Test {i:2d}/{total_tests}: {test_case['name']} - HTTP {response.status}")
                            error_text = await response.text()
                            print(f"     Error: {error_text}")
                            
                            results.append({
                                "test_name": test_case["name"],
                                "text": test_case["text"],
                                "expected": test_case["expected"],
                                "detected": "error",
                                "confidence": 0.0,
                                "response_time_ms": response_time,
                                "correct": False,
                                "status": "http_error",
                                "error": f"HTTP {response.status}: {error_text}"
                            })
                            
            except Exception as e:
                print(f"  ❌ Test {i:2d}/{total_tests}: {test_case['name']} - Exception: {e}")
                results.append({
                    "test_name": test_case["name"],
                    "text": test_case["text"],
                    "expected": test_case["expected"],
                    "detected": "error",
                    "confidence": 0.0,
                    "response_time_ms": 0,
                    "correct": False,
                    "status": "exception",
                    "error": str(e)
                })
            
            # Small delay between requests
            await asyncio.sleep(0.1)
        
        # Calculate statistics
        accuracy = (correct_predictions / total_tests) * 100 if total_tests > 0 else 0
        avg_response_time = sum(r["response_time_ms"] for r in results if r["status"] == "success") / max(1, len([r for r in results if r["status"] == "success"]))
        avg_confidence = sum(r["confidence"] for r in results if r["status"] == "success") / max(1, len([r for r in results if r["status"] == "success"]))
        
        # Print summary
        print(f"\n📊 Language Detection Test Summary:")
        print(f"   Total tests: {total_tests}")
        print(f"   Correct predictions: {correct_predictions}")
        print(f"   Accuracy: {accuracy:.1f}%")
        print(f"   Average response time: {avg_response_time:.1f}ms")
        print(f"   Average confidence: {avg_confidence:.2f}")
        
        return {
            "accuracy": accuracy,
            "total_tests": total_tests,
            "correct_predictions": correct_predictions,
            "avg_response_time": avg_response_time,
            "avg_confidence": avg_confidence,
            "results": results
        }

    async def test_edge_cases(self):
        """Test edge cases for language detection"""
        print("\n🧪 Testing Edge Cases...")
        
        edge_cases = [
            {"text": "", "name": "Empty string"},
            {"text": " ", "name": "Whitespace only"},
            {"text": "123", "name": "Numbers only"},
            {"text": "!@#$%^&*()", "name": "Special characters only"},
            {"text": "a", "name": "Single character"},
            {"text": "The", "name": "Single English word"},
            {"text": "हाँ", "name": "Single Hindi word"},
            {"text": "hi there नमस्ते", "name": "Code-mixed text"},
            {"text": "x" * 1000, "name": "Very long text (1000 chars)"},
        ]
        
        edge_results = []
        
        for i, test_case in enumerate(edge_cases, 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/detect-language",
                        json={"text": test_case["text"]},
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            detected = result.get("detected_language", "unknown")
                            confidence = result.get("confidence", 0.0)
                            
                            print(f"  ✅ Edge case {i}: {test_case['name']}")
                            print(f"     Detected: {detected}, Confidence: {confidence:.2f}")
                            
                            edge_results.append({
                                "name": test_case["name"],
                                "text": test_case["text"][:50] + "..." if len(test_case["text"]) > 50 else test_case["text"],
                                "detected": detected,
                                "confidence": confidence,
                                "status": "success"
                            })
                        else:
                            error_text = await response.text()
                            print(f"  ❌ Edge case {i}: {test_case['name']} - HTTP {response.status}")
                            print(f"     Error: {error_text}")
                            
                            edge_results.append({
                                "name": test_case["name"],
                                "text": test_case["text"][:50] + "..." if len(test_case["text"]) > 50 else test_case["text"],
                                "detected": "error",
                                "confidence": 0.0,
                                "status": "error",
                                "error": f"HTTP {response.status}: {error_text}"
                            })
                            
            except Exception as e:
                print(f"  ❌ Edge case {i}: {test_case['name']} - Exception: {e}")
                edge_results.append({
                    "name": test_case["name"],
                    "text": test_case["text"][:50] + "..." if len(test_case["text"]) > 50 else test_case["text"],
                    "detected": "error",
                    "confidence": 0.0,
                    "status": "exception",
                    "error": str(e)
                })
            
            await asyncio.sleep(0.1)
        
        return edge_results

    async def performance_test(self):
        """Test performance with concurrent requests"""
        print("\n🚀 Testing Performance (Concurrent Requests)...")
        
        test_text = "नमस्ते आप कैसे हैं? मैं आज बहुत खुश हूं।"
        num_requests = 20
        
        async def single_request(session, request_id):
            start_time = time.time()
            try:
                async with session.post(
                    f"{self.base_url}/detect-language",
                    json={"text": test_text},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "request_id": request_id,
                            "response_time": response_time,
                            "detected": result.get("detected_language"),
                            "confidence": result.get("confidence"),
                            "success": True
                        }
                    else:
                        return {
                            "request_id": request_id,
                            "response_time": response_time,
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "response_time": (time.time() - start_time) * 1000,
                    "success": False,
                    "error": str(e)
                }
        
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            tasks = [single_request(session, i) for i in range(num_requests)]
            results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        if successful_requests:
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            min_response_time = min(r["response_time"] for r in successful_requests)
            max_response_time = max(r["response_time"] for r in successful_requests)
            requests_per_second = num_requests / total_time
            
            print(f"  ✅ Completed {len(successful_requests)}/{num_requests} requests successfully")
            print(f"     Total time: {total_time:.2f}s")
            print(f"     Requests/second: {requests_per_second:.1f}")
            print(f"     Avg response time: {avg_response_time:.1f}ms")
            print(f"     Min response time: {min_response_time:.1f}ms")
            print(f"     Max response time: {max_response_time:.1f}ms")
            
            if failed_requests:
                print(f"     Failed requests: {len(failed_requests)}")
                for failure in failed_requests[:3]:  # Show first 3 failures
                    print(f"       - Request {failure['request_id']}: {failure.get('error', 'Unknown error')}")
        else:
            print(f"  ❌ All {num_requests} requests failed")
        
        return {
            "total_requests": num_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "total_time": total_time,
            "requests_per_second": requests_per_second if successful_requests else 0,
            "avg_response_time": avg_response_time if successful_requests else 0,
            "results": results
        }

    async def run_all_tests(self):
        """Run all language detection tests"""
        print("🧪 LANGUAGE DETECTION ENDPOINT TESTS")
        print("=" * 50)
        
        # Health check first
        if not await self.test_health():
            print("❌ Service is not healthy. Exiting tests.")
            return
        
        # Run main tests
        main_results = await self.test_language_detection_endpoint()
        edge_results = await self.test_edge_cases()
        perf_results = await self.performance_test()
        
        # Final summary
        print("\n" + "=" * 50)
        print("📋 FINAL SUMMARY")
        print("=" * 50)
        print(f"Language Detection Accuracy: {main_results['accuracy']:.1f}%")
        print(f"Average Response Time: {main_results['avg_response_time']:.1f}ms")
        print(f"Average Confidence: {main_results['avg_confidence']:.2f}")
        print(f"Performance: {perf_results['requests_per_second']:.1f} req/sec")
        print(f"Edge Cases Handled: {len([r for r in edge_results if r['status'] == 'success'])}/{len(edge_results)}")
        
        # Overall assessment
        if main_results['accuracy'] >= 80 and perf_results['requests_per_second'] >= 10:
            print("\n✅ Language detection endpoint is working excellently!")
        elif main_results['accuracy'] >= 60 and perf_results['requests_per_second'] >= 5:
            print("\n✅ Language detection endpoint is working well!")
        else:
            print("\n⚠️ Language detection endpoint needs improvement.")

async def main():
    tester = LanguageDetectionTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
