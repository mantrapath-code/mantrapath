#!/usr/bin/env python3
"""
Test runner for MantraPath chatbot and voice integration tests.
Runs all test suites and generates comprehensive reports.
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List

class TestRunner:
    """Comprehensive test runner for MantraPath services"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {}
        self.start_time = time.time()
    
    def run_test_suite(self, test_file: str, test_name: str) -> Dict[str, Any]:
        """Run a specific test suite and return results"""
        print(f"\n{'='*60}")
        print(f"Running {test_name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Run pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                str(self.test_dir / test_file),
                "-v", "--tb=short", "--no-header"
            ], capture_output=True, text=True, timeout=300)
            
            end_time = time.time()
            duration = end_time - start_time
            
            return {
                "test_name": test_name,
                "test_file": test_file,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except subprocess.TimeoutExpired:
            return {
                "test_name": test_name,
                "test_file": test_file,
                "duration": 300,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test timed out after 5 minutes",
                "success": False,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {
                "test_name": test_name,
                "test_file": test_file,
                "duration": 0,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def check_service_health(self) -> Dict[str, bool]:
        """Check if all required services are running"""
        print("\n🔍 Checking service health...")
        
        services = {
            "chatbot_service": "http://localhost:8004/health",
            "models_service": "http://localhost:8081/health",
            "voice_service": "http://localhost:8011/health"
        }
        
        health_status = {}
        
        for service_name, health_url in services.items():
            try:
                import httpx
                with httpx.Client(timeout=5.0) as client:
                    response = client.get(health_url)
                    is_healthy = response.status_code == 200
                    health_status[service_name] = is_healthy
                    status_icon = "✅" if is_healthy else "❌"
                    print(f"  {status_icon} {service_name}: {health_url}")
            except Exception as e:
                health_status[service_name] = False
                print(f"  ❌ {service_name}: Connection failed - {e}")
        
        return health_status
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        print("🚀 Starting MantraPath Test Suite")
        print(f"Test directory: {self.test_dir}")
        
        # Check service health first
        health_status = self.check_service_health()
        
        if not all(health_status.values()):
            print("\n⚠️  Warning: Some services are not healthy!")
            print("Tests may fail due to service unavailability.")
            print("Make sure all services are running before running tests.")
        
        # Define test suites
        test_suites = [
            ("test_chatbot_qwen.py", "Qwen Model Integration Tests"),
            ("test_voice_integration.py", "Voice Service Integration Tests"),
            ("test_chatbot_voice_flow.py", "End-to-End Voice Chatbot Tests")
        ]
        
        # Run each test suite
        for test_file, test_name in test_suites:
            result = self.run_test_suite(test_file, test_name)
            self.results[test_name] = result
            
            # Print immediate results
            if result["success"]:
                print(f"✅ {test_name} - PASSED ({result['duration']:.2f}s)")
            else:
                print(f"❌ {test_name} - FAILED ({result['duration']:.2f}s)")
                if result["stderr"]:
                    print(f"   Error: {result['stderr'][:200]}...")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.start_time
        
        # Calculate summary statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        # Generate report
        report = f"""
# MantraPath Test Report
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
Total Duration: {total_duration:.2f} seconds

## Summary
- Total Test Suites: {total_tests}
- Passed: {passed_tests} ✅
- Failed: {failed_tests} ❌
- Success Rate: {(passed_tests/total_tests)*100:.1f}%

## Test Results
"""
        
        for test_name, result in self.results.items():
            status = "✅ PASSED" if result["success"] else "❌ FAILED"
            report += f"""
### {test_name}
- Status: {status}
- Duration: {result['duration']:.2f}s
- Timestamp: {result['timestamp']}
"""
            
            if not result["success"] and result["stderr"]:
                report += f"- Error: {result['stderr'][:500]}...\n"
        
        return report
    
    def save_report(self, report: str):
        """Save test report to file"""
        report_file = self.test_dir / "test_report.md"
        with open(report_file, "w") as f:
            f.write(report)
        print(f"\n📄 Test report saved to: {report_file}")
    
    def run(self):
        """Main test runner entry point"""
        try:
            # Run all tests
            results = self.run_all_tests()
            
            # Generate and save report
            report = self.generate_report()
            self.save_report(report)
            
            # Print final summary
            print(f"\n{'='*60}")
            print("🏁 Test Suite Complete")
            print(f"{'='*60}")
            print(report)
            
            # Exit with appropriate code
            all_passed = all(result["success"] for result in self.results.values())
            sys.exit(0 if all_passed else 1)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Test runner failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    runner = TestRunner()
    runner.run()
