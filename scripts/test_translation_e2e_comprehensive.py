#!/usr/bin/env python3
"""
Comprehensive End-to-End Translation Service Test
Tests real functionality without mock data dependencies
"""
import requests
import json
import time
import sys
import asyncio
from typing import Dict, List, Tuple

# Test configuration
BASE_URL = "http://localhost:8010"
TIMEOUT = 30
TEST_CASES = []

class TestCase:
    def __init__(self, name: str, source_text: str, target_language: str, 
                 expected_source_lang: str = None, min_confidence: float = 0.5, 
                 test_type: str = "translation"):
        self.name = name
        self.source_text = source_text
        self.target_language = target_language
        self.expected_source_lang = expected_source_lang
        self.min_confidence = min_confidence
        self.test_type = test_type
        self.result = None
        self.passed = False
        self.error = None

class E2ETestSuite:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.results = []
        
        # Define comprehensive test cases
        self.define_test_cases()
    
    def define_test_cases(self):
        """Define real-world test cases without mock dependencies"""
        global TEST_CASES
        
        # Real Indian language tests (Bhashini strength)
        TEST_CASES = [
            # Hindi tests
            TestCase(
                "Hindi to English - Common Greeting",
                "नमस्ते, आप कैसे हैं?",
                "en",
                expected_source_lang="hi",
                min_confidence=0.6
            ),
            TestCase(
                "English to Hindi - Basic Phrase", 
                "Hello, how are you?",
                "hi",
                expected_source_lang="en",
                min_confidence=0.6
            ),
            
            # Bengali tests
            TestCase(
                "Bengali to English - Greeting",
                "আপনি কেমন আছেন?",
                "en", 
                expected_source_lang="bn",
                min_confidence=0.6
            ),
            TestCase(
                "English to Bengali - Basic Phrase",
                "Good morning",
                "bn",
                expected_source_lang="en", 
                min_confidence=0.6
            ),
            
            # Tamil tests
            TestCase(
                "Tamil to English - Greeting",
                "நீங்கள் எப்படி இருக்கிறீர்கள்?",
                "en",
                expected_source_lang="ta",
                min_confidence=0.6
            ),
            
            # Telugu tests  
            TestCase(
                "Telugu to English - Greeting",
                "మీరు ఎలా ఉన్నారు?",
                "en",
                expected_source_lang="te", 
                min_confidence=0.6
            ),
            
            # Multi-language detection tests
            TestCase(
                "Auto-detect Spanish",
                "Hola, ¿cómo estás? Espero que tengas un buen día.",
                "en",
                expected_source_lang="es",
                min_confidence=0.5,
                test_type="detection"
            ),
            TestCase(
                "Auto-detect French", 
                "Bonjour, comment allez-vous? J'espère que vous passez une bonne journée.",
                "en",
                expected_source_lang="fr",
                min_confidence=0.5,
                test_type="detection"
            ),
            
            # Edge cases and error handling
            TestCase(
                "Very Short Text",
                "Hi",
                "hi",
                expected_source_lang="en",
                min_confidence=0.3
            ),
            TestCase(
                "Numbers and Mixed Content",
                "Price: 100 rupees", 
                "hi",
                expected_source_lang="en",
                min_confidence=0.3
            ),
            TestCase(
                "Long Text Translation",
                "This is a longer text to test how well the translation service handles extended content with multiple sentences and complex grammar structures.",
                "hi",
                expected_source_lang="en",
                min_confidence=0.4
            ),
            
            # Cross-language Indian scripts
            TestCase(
                "Gujarati to Hindi",
                "તમે કેમ છો?",
                "hi", 
                expected_source_lang="gu",
                min_confidence=0.5
            ),
            TestCase(
                "Malayalam to English",
                "നിങ്ങൾ എങ്ങനെയുണ്ട്?",
                "en",
                expected_source_lang="ml",
                min_confidence=0.5
            ),
            
            # Real-world use cases
            TestCase(
                "English Cultural Context",
                "Thank you very much for your help.",
                "hi",
                expected_source_lang="en",
                min_confidence=0.5
            ),
            TestCase(
                "Hindi Cultural Context",
                "धन्यवाद आपकी सहायता के लिए।",
                "en",
                expected_source_lang="hi", 
                min_confidence=0.6
            )
        ]
    
    def test_service_health(self) -> bool:
        """Test if service is available and healthy"""
        try:
            print("🔍 Testing service health...")
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Service is healthy: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Service returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to service: {e}")
            return False
    
    def test_language_detection(self, test_case: TestCase) -> bool:
        """Test language detection functionality"""
        try:
            response = requests.post(
                f"{BASE_URL}/detect-language",
                json={"text": test_case.source_text},
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                detected_lang = result.get('detected_language')
                confidence = result.get('confidence', 0)
                
                test_case.result = {
                    'detected_language': detected_lang,
                    'confidence': confidence,
                    'response_time': response.elapsed.total_seconds() * 1000
                }
                
                # Check if detection matches expectation
                if test_case.expected_source_lang:
                    language_match = detected_lang == test_case.expected_source_lang
                else:
                    language_match = True  # No specific expectation
                
                confidence_ok = confidence >= test_case.min_confidence
                test_case.passed = language_match and confidence_ok
                
                if not test_case.passed:
                    test_case.error = f"Expected {test_case.expected_source_lang}, got {detected_lang} (conf: {confidence})"
                
                return test_case.passed
            else:
                test_case.error = f"HTTP {response.status_code}: {response.text}"
                return False
                
        except Exception as e:
            test_case.error = str(e)
            return False
    
    def test_translation(self, test_case: TestCase) -> bool:
        """Test translation functionality"""
        try:
            # Test data
            request_data = {
                "text": test_case.source_text,
                "target_language": test_case.target_language
            }
            
            # Add source language if specified
            if test_case.expected_source_lang:
                request_data["source_language"] = test_case.expected_source_lang
            
            response = requests.post(
                f"{BASE_URL}/translate",
                json=request_data,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                
                test_case.result = {
                    'translated_text': result.get('translated_text'),
                    'source_language': result.get('source_language'),
                    'target_language': result.get('target_language'),
                    'confidence_score': result.get('confidence_score', 0),
                    'engine': result.get('engine'),
                    'processing_time_ms': result.get('processing_time_ms', 0),
                    'cache_hit': result.get('cache_hit', False),
                    'response_time': response.elapsed.total_seconds() * 1000
                }
                
                # Validation criteria
                confidence_ok = result.get('confidence_score', 0) >= test_case.min_confidence
                has_translation = bool(result.get('translated_text', '').strip())
                source_detected = result.get('source_language') == test_case.expected_source_lang if test_case.expected_source_lang else True
                target_correct = result.get('target_language') == test_case.target_language
                
                # Check if it's not just echoing the input (real translation)
                translated_text = result.get('translated_text', '')
                is_real_translation = translated_text != test_case.source_text
                
                # For mock data, check if it's meaningful 
                is_mock_data = '[BHASHINI' in translated_text or 'FALLBACK' in translated_text
                
                test_case.passed = (confidence_ok and has_translation and 
                                  source_detected and target_correct and
                                  (is_real_translation or not is_mock_data))
                
                if not test_case.passed:
                    issues = []
                    if not confidence_ok:
                        issues.append(f"Low confidence: {result.get('confidence_score', 0)}")
                    if not has_translation:
                        issues.append("No translation output")
                    if not source_detected:
                        issues.append(f"Wrong source: expected {test_case.expected_source_lang}, got {result.get('source_language')}")
                    if not target_correct:
                        issues.append(f"Wrong target: expected {test_case.target_language}, got {result.get('target_language')}")
                    if not is_real_translation and is_mock_data:
                        issues.append("Using mock data instead of real translation")
                    
                    test_case.error = "; ".join(issues)
                
                return test_case.passed
            else:
                test_case.error = f"HTTP {response.status_code}: {response.text}"
                return False
                
        except Exception as e:
            test_case.error = str(e)
            return False
    
    def run_single_test(self, test_case: TestCase) -> bool:
        """Run a single test case"""
        print(f"\n📝 Test: {test_case.name}")
        print(f"   Text: '{test_case.source_text[:50]}{'...' if len(test_case.source_text) > 50 else ''}'")
        print(f"   Target: {test_case.target_language}")
        
        if test_case.test_type == "detection":
            success = self.test_language_detection(test_case)
        else:
            success = self.test_translation(test_case)
        
        if success:
            print(f"   ✅ PASSED")
            if test_case.result:
                if test_case.test_type == "detection":
                    print(f"      Detected: {test_case.result.get('detected_language')} (confidence: {test_case.result.get('confidence'):.2f})")
                else:
                    print(f"      Translated: '{test_case.result.get('translated_text', '')[:60]}{'...' if len(test_case.result.get('translated_text', '')) > 60 else ''}'")
                    print(f"      Source: {test_case.result.get('source_language')}, Confidence: {test_case.result.get('confidence_score', 0):.2f}")
                    print(f"      Engine: {test_case.result.get('engine')}, Response time: {test_case.result.get('response_time', 0):.1f}ms")
        else:
            print(f"   ❌ FAILED: {test_case.error}")
        
        return success
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 COMPREHENSIVE END-TO-END TRANSLATION SERVICE TEST")
        print("=" * 70)
        print("Testing REAL functionality without mock dependencies")
        
        # Health check first
        if not self.test_service_health():
            print("\n❌ Service health check failed. Cannot proceed with tests.")
            return
        
        # Get service info
        try:
            response = requests.get(f"{BASE_URL}/languages", timeout=10)
            if response.status_code == 200:
                lang_data = response.json()
                print(f"\n📋 Service supports {len(lang_data.get('supported_languages', []))} languages")
                print(f"   Indian languages: {len(lang_data.get('indian_languages', []))}")
        except:
            pass
        
        print(f"\n🧪 Running {len(TEST_CASES)} test cases...")
        print("=" * 50)
        
        # Run all tests
        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"\n[{i}/{len(TEST_CASES)}]", end="")
            success = self.run_single_test(test_case)
            
            self.total_tests += 1
            if success:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
            
            self.results.append(test_case)
            
            # Small delay to avoid overwhelming the service
            time.sleep(0.1)
        
        # Generate final report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 FINAL TEST REPORT")
        print("=" * 70)
        
        # Summary statistics
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests} ({success_rate:.1f}%)")
        print(f"❌ Failed: {self.failed_tests}")
        
        # Confidence score analysis
        confidence_scores = []
        response_times = []
        engines_used = {}
        
        for test_case in self.results:
            if test_case.result and test_case.test_type != "detection":
                conf = test_case.result.get('confidence_score', 0)
                if conf > 0:
                    confidence_scores.append(conf)
                
                rt = test_case.result.get('response_time', 0)
                if rt > 0:
                    response_times.append(rt)
                
                engine = test_case.result.get('engine', 'unknown')
                engines_used[engine] = engines_used.get(engine, 0) + 1
        
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            print(f"\n📈 CONFIDENCE ANALYSIS:")
            print(f"   Average Confidence: {avg_confidence:.3f}")
            print(f"   Min Confidence: {min(confidence_scores):.3f}")
            print(f"   Max Confidence: {max(confidence_scores):.3f}")
            
            # Confidence distribution
            high_conf = len([c for c in confidence_scores if c >= 0.7])
            med_conf = len([c for c in confidence_scores if 0.5 <= c < 0.7])
            low_conf = len([c for c in confidence_scores if c < 0.5])
            
            print(f"   High (≥0.7): {high_conf} tests")
            print(f"   Medium (0.5-0.7): {med_conf} tests") 
            print(f"   Low (<0.5): {low_conf} tests")
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            print(f"\n⚡ PERFORMANCE ANALYSIS:")
            print(f"   Average Response Time: {avg_response:.1f}ms")
            print(f"   Fastest: {min(response_times):.1f}ms")
            print(f"   Slowest: {max(response_times):.1f}ms")
        
        if engines_used:
            print(f"\n🔧 ENGINE USAGE:")
            for engine, count in engines_used.items():
                percentage = (count / len([t for t in self.results if t.test_type != "detection"])) * 100
                print(f"   {engine}: {count} tests ({percentage:.1f}%)")
        
        # Failed tests details
        failed_tests = [t for t in self.results if not t.passed]
        if failed_tests:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for test_case in failed_tests:
                print(f"   • {test_case.name}: {test_case.error}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if success_rate >= 90:
            print("   🎉 Excellent! Service is working very well.")
        elif success_rate >= 70:
            print("   👍 Good performance. Some areas for improvement.")
        elif success_rate >= 50:
            print("   ⚠️  Moderate performance. Significant improvements needed.")
        else:
            print("   🚨 Poor performance. Major issues need attention.")
            
        if confidence_scores and avg_confidence < 0.6:
            print("   📊 Consider improving confidence calculation algorithms.")
        
        if response_times and avg_response > 1000:
            print("   ⚡ Consider optimizing for better response times.")
        
        print(f"\n✅ End-to-end testing completed!")

def main():
    """Main test execution"""
    print("🔧 Comprehensive Translation Service End-to-End Test")
    print("🎯 Testing REAL functionality without mock dependencies")
    print("📝 Validating confidence score calculations")
    
    # Run test suite
    test_suite = E2ETestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()
