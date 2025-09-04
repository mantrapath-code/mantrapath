"""
Voice Service Test Runner
Comprehensive test execution for all test scenarios
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path
import subprocess
import time
import json
from typing import Dict, List, Any

class VoiceServiceTestRunner:
    """Test runner for Voice Service comprehensive testing"""
    
    def __init__(self):
        self.test_results = {}
        self.base_dir = Path(__file__).parent
        self.voice_service_dir = self.base_dir.parent
        
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run all unit tests"""
        print("🧪 Running Unit Tests...")
        
        unit_tests = [
            "tests/unit/test_models_client.py",
            "tests/unit/test_language_detector.py",
            "tests/unit/test_conversation_manager.py"
        ]
        
        results = {}
        for test_file in unit_tests:
            test_path = self.voice_service_dir / test_file
            if test_path.exists():
                print(f"  Running {test_file}...")
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    str(test_path), 
                    "-v", "--tb=short", "--json-report", "--json-report-file=/tmp/test_report.json"
                ], capture_output=True, text=True, cwd=self.voice_service_dir)
                
                results[test_file] = {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                results[test_file] = {"error": "File not found"}
        
        return results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests (requires running service)"""
        print("🔗 Running Integration Tests...")
        
        # Check if voice service is running
        service_running = self.check_service_health()
        if not service_running:
            print("⚠️  Voice service not running. Starting service...")
            service_started = self.start_voice_service()
            if not service_started:
                return {"error": "Could not start voice service"}
        
        integration_tests = [
            "tests/integration/test_voice_service_integration.py"
        ]
        
        results = {}
        for test_file in integration_tests:
            test_path = self.voice_service_dir / test_file
            if test_path.exists():
                print(f"  Running {test_file}...")
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    str(test_path), 
                    "-v", "--tb=short"
                ], capture_output=True, text=True, cwd=self.voice_service_dir)
                
                results[test_file] = {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                results[test_file] = {"error": "File not found"}
        
        return results
    
    def run_indian_language_tests(self) -> Dict[str, Any]:
        """Run specific tests for Indian languages"""
        print("🇮🇳 Running Indian Language Tests...")
        
        # Run specific test patterns for Indian languages
        test_patterns = [
            "test_*hindi*",
            "test_*bengali*", 
            "test_*tamil*",
            "test_*indian*",
            "test_*code_switching*",
            "test_*regional*"
        ]
        
        results = {}
        for pattern in test_patterns:
            print(f"  Running tests matching: {pattern}")
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "-k", pattern,
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=self.voice_service_dir)
            
            results[pattern] = {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        
        return results
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance and benchmark tests"""
        print("⚡ Running Performance Tests...")
        
        performance_tests = [
            "test_performance_large_text",
            "test_concurrent_conversations", 
            "test_cache_functionality",
            "test_performance_benchmarks"
        ]
        
        results = {}
        for test_name in performance_tests:
            print(f"  Running {test_name}...")
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "-k", test_name,
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=self.voice_service_dir)
            
            results[test_name] = {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        
        return results
    
    def check_service_health(self) -> bool:
        """Check if voice service is healthy"""
        try:
            import aiohttp
            
            async def health_check():
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8010/health") as response:
                        return response.status == 200
            
            return asyncio.run(health_check())
        except Exception:
            return False
    
    def start_voice_service(self) -> bool:
        """Start the voice service for testing"""
        try:
            print("  Starting voice service...")
            # Start service in background
            subprocess.Popen([
                sys.executable, "main.py"
            ], cwd=self.voice_service_dir)
            
            # Wait for service to start
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if self.check_service_health():
                    print("  ✅ Voice service started successfully")
                    return True
            
            print("  ❌ Failed to start voice service")
            return False
        except Exception as e:
            print(f"  ❌ Error starting service: {e}")
            return False
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        print("📊 Generating Test Report...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0
            },
            "coverage": {},
            "performance_metrics": {},
            "indian_language_support": {},
            "recommendations": []
        }
        
        # Analyze test results
        for suite_name, results in self.test_results.items():
            suite_summary = self.analyze_test_suite(results)
            report["test_suites"][suite_name] = suite_summary
            
            # Update totals
            report["summary"]["total_tests"] += suite_summary.get("total", 0)
            report["summary"]["passed_tests"] += suite_summary.get("passed", 0)
            report["summary"]["failed_tests"] += suite_summary.get("failed", 0)
            report["summary"]["skipped_tests"] += suite_summary.get("skipped", 0)
        
        # Generate recommendations
        report["recommendations"] = self.generate_recommendations(report)
        
        return report
    
    def analyze_test_suite(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze results from a test suite"""
        analysis = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
        
        for test_file, result in results.items():
            if "error" in result:
                analysis["errors"].append(f"{test_file}: {result['error']}")
                continue
                
            # Parse pytest output
            stdout = result.get("stdout", "")
            if "passed" in stdout:
                # Simple parsing - in real implementation, use pytest JSON report
                analysis["passed"] += stdout.count(" PASSED")
                analysis["failed"] += stdout.count(" FAILED")
                analysis["skipped"] += stdout.count(" SKIPPED")
                
            if result.get("exit_code", 0) != 0:
                analysis["errors"].append(f"{test_file}: Exit code {result['exit_code']}")
        
        analysis["total"] = analysis["passed"] + analysis["failed"] + analysis["skipped"]
        return analysis
    
    def generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        summary = report["summary"]
        
        # Test coverage recommendations
        if summary["failed_tests"] > 0:
            recommendations.append(
                f"❌ {summary['failed_tests']} tests failed. Review and fix failing tests."
            )
        
        if summary["total_tests"] < 50:
            recommendations.append(
                "📝 Consider adding more test cases for better coverage."
            )
        
        # Performance recommendations
        performance_issues = []
        for suite_name, suite_data in report["test_suites"].items():
            if "performance" in suite_name.lower() and suite_data.get("failed", 0) > 0:
                performance_issues.append(suite_name)
        
        if performance_issues:
            recommendations.append(
                f"⚡ Performance issues detected in: {', '.join(performance_issues)}"
            )
        
        # Language support recommendations
        if "indian_language" in report["test_suites"]:
            lang_results = report["test_suites"]["indian_language"]
            if lang_results.get("failed", 0) > 0:
                recommendations.append(
                    "🇮🇳 Some Indian language tests failed. Check language detection and TTS models."
                )
        
        if not recommendations:
            recommendations.append("✅ All tests passed! Voice service is ready for production.")
        
        return recommendations
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        print("🚀 Starting Comprehensive Voice Service Testing...")
        print("=" * 60)
        
        # Run all test suites
        self.test_results["unit_tests"] = self.run_unit_tests()
        self.test_results["integration_tests"] = self.run_integration_tests()
        self.test_results["indian_language_tests"] = self.run_indian_language_tests()
        self.test_results["performance_tests"] = self.run_performance_tests()
        
        # Generate report
        report = self.generate_test_report()
        
        # Print summary
        self.print_test_summary(report)
        
        # Save report
        report_file = self.voice_service_dir / "test_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Detailed report saved to: {report_file}")
        
        return report
    
    def print_test_summary(self, report: Dict[str, Any]):
        """Print test summary to console"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Passed: {summary['passed_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"⏭️  Skipped: {summary['skipped_tests']}")
        
        success_rate = (summary['passed_tests'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 RECOMMENDATIONS:")
        for recommendation in report["recommendations"]:
            print(f"  {recommendation}")
        
        print("\n" + "=" * 60)

def main():
    """Main test runner function"""
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        runner = VoiceServiceTestRunner()
        
        if test_type == "unit":
            results = runner.run_unit_tests()
        elif test_type == "integration":
            results = runner.run_integration_tests()
        elif test_type == "indian":
            results = runner.run_indian_language_tests()
        elif test_type == "performance":
            results = runner.run_performance_tests()
        else:
            print("Unknown test type. Use: unit, integration, indian, performance, or no argument for all")
            return
            
        print(json.dumps(results, indent=2))
    else:
        # Run all tests
        runner = VoiceServiceTestRunner()
        runner.run_all_tests()

if __name__ == "__main__":
    main()
