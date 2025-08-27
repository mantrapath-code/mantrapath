#!/usr/bin/env python3
"""
Comprehensive Test Runner for Epic V3-BK-001: Action Orchestrator Implementation
Validates all acceptance criteria and scenarios for voice-driven cross-service workflows
"""
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import pytest


class EpicV3BK001TestRunner:
    """Test runner for Epic V3-BK-001 validation"""
    
    def __init__(self):
        self.results = {
            "epic": "V3-BK-001",
            "title": "Action Orchestrator Core Service",
            "timestamp": datetime.now().isoformat(),
            "acceptance_criteria": {
                "voice_intent_processing": {"status": "pending", "tests": []},
                "cross_service_coordination": {"status": "pending", "tests": []},
                "cultural_context_handling": {"status": "pending", "tests": []},
                "rollback_error_handling": {"status": "pending", "tests": []}
            },
            "test_categories": {
                "unit_tests": {"status": "pending", "coverage": 0},
                "integration_tests": {"status": "pending", "coverage": 0},
                "performance_tests": {"status": "pending", "results": {}},
                "security_tests": {"status": "pending", "vulnerabilities": []},
                "cultural_tests": {"status": "pending", "languages": []}
            },
            "overall_status": "pending",
            "coverage_target": 90,
            "coverage_achieved": 0
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite for Epic V3-BK-001"""
        print("🚀 Starting Epic V3-BK-001 Test Suite")
        print("=" * 60)
        
        try:
            # 1. Run unit tests with coverage
            self._run_unit_tests()
            
            # 2. Run integration tests
            self._run_integration_tests()
            
            # 3. Run performance tests
            self._run_performance_tests()
            
            # 4. Run security tests
            self._run_security_tests()
            
            # 5. Run cultural context tests
            self._run_cultural_tests()
            
            # 6. Validate acceptance criteria
            self._validate_acceptance_criteria()
            
            # 7. Generate final report
            self._generate_final_report()
            
        except Exception as e:
            print(f"❌ Test suite execution failed: {e}")
            self.results["overall_status"] = "failed"
            self.results["error"] = str(e)
        
        return self.results
    
    def _run_unit_tests(self):
        """Run unit tests with coverage reporting"""
        print("\n📋 Running Unit Tests...")
        
        try:
            # Run unit tests with coverage
            cmd = [
                "python", "-m", "pytest",
                "tests/test_epic_v3_bk_001_comprehensive.py",
                "-v",
                "--cov=src",
                "--cov-report=json",
                "--cov-report=term-missing",
                "--json-report",
                "--json-report-file=test_results_unit.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse coverage results
            if os.path.exists("coverage.json"):
                with open("coverage.json", "r") as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                    self.results["test_categories"]["unit_tests"]["coverage"] = total_coverage
                    self.results["coverage_achieved"] = max(self.results["coverage_achieved"], total_coverage)
            
            # Parse test results
            if os.path.exists("test_results_unit.json"):
                with open("test_results_unit.json", "r") as f:
                    test_data = json.load(f)
                    
                    # Check acceptance criteria tests
                    self._analyze_acceptance_criteria_tests(test_data)
            
            if result.returncode == 0:
                self.results["test_categories"]["unit_tests"]["status"] = "passed"
                print("✅ Unit tests passed")
            else:
                self.results["test_categories"]["unit_tests"]["status"] = "failed"
                print(f"❌ Unit tests failed: {result.stderr}")
                
        except Exception as e:
            self.results["test_categories"]["unit_tests"]["status"] = "error"
            print(f"❌ Unit test execution error: {e}")
    
    def _run_integration_tests(self):
        """Run integration tests"""
        print("\n🔗 Running Integration Tests...")
        
        try:
            cmd = [
                "python", "-m", "pytest",
                "tests/test_api_integration_epic_v3_bk_001.py",
                "-v",
                "--json-report",
                "--json-report-file=test_results_integration.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.results["test_categories"]["integration_tests"]["status"] = "passed"
                print("✅ Integration tests passed")
            else:
                self.results["test_categories"]["integration_tests"]["status"] = "failed"
                print(f"❌ Integration tests failed: {result.stderr}")
                
        except Exception as e:
            self.results["test_categories"]["integration_tests"]["status"] = "error"
            print(f"❌ Integration test execution error: {e}")
    
    def _run_performance_tests(self):
        """Run performance tests"""
        print("\n⚡ Running Performance Tests...")
        
        try:
            cmd = [
                "python", "-m", "pytest",
                "tests/test_api_integration_epic_v3_bk_001.py::TestActionOrchestratorPerformance",
                "-v", "-m", "slow",
                "--json-report",
                "--json-report-file=test_results_performance.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.results["test_categories"]["performance_tests"]["status"] = "passed"
                print("✅ Performance tests passed")
            else:
                self.results["test_categories"]["performance_tests"]["status"] = "failed"
                print(f"❌ Performance tests failed: {result.stderr}")
                
        except Exception as e:
            self.results["test_categories"]["performance_tests"]["status"] = "error"
            print(f"❌ Performance test execution error: {e}")
    
    def _run_security_tests(self):
        """Run security tests"""
        print("\n🔒 Running Security Tests...")
        
        try:
            cmd = [
                "python", "-m", "pytest",
                "tests/test_api_integration_epic_v3_bk_001.py::TestActionOrchestratorSecurity",
                "-v",
                "--json-report",
                "--json-report-file=test_results_security.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.results["test_categories"]["security_tests"]["status"] = "passed"
                print("✅ Security tests passed")
            else:
                self.results["test_categories"]["security_tests"]["status"] = "failed"
                print(f"❌ Security tests failed: {result.stderr}")
                
        except Exception as e:
            self.results["test_categories"]["security_tests"]["status"] = "error"
            print(f"❌ Security test execution error: {e}")
    
    def _run_cultural_tests(self):
        """Run cultural context tests"""
        print("\n🌍 Running Cultural Context Tests...")
        
        try:
            cmd = [
                "python", "-m", "pytest",
                "tests/test_api_integration_epic_v3_bk_001.py::TestActionOrchestratorCulturalScenarios",
                "-v",
                "--json-report",
                "--json-report-file=test_results_cultural.json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.results["test_categories"]["cultural_tests"]["status"] = "passed"
                self.results["test_categories"]["cultural_tests"]["languages"] = ["hi", "ja", "ar", "en"]
                print("✅ Cultural context tests passed")
            else:
                self.results["test_categories"]["cultural_tests"]["status"] = "failed"
                print(f"❌ Cultural context tests failed: {result.stderr}")
                
        except Exception as e:
            self.results["test_categories"]["cultural_tests"]["status"] = "error"
            print(f"❌ Cultural test execution error: {e}")
    
    def _analyze_acceptance_criteria_tests(self, test_data: Dict[str, Any]):
        """Analyze test results against acceptance criteria"""
        tests = test_data.get("tests", [])
        
        # Map test names to acceptance criteria
        criteria_mapping = {
            "voice_intent_processing": [
                "test_voice_intent_processing_hindi",
                "test_voice_intent_processing_english",
                "test_low_confidence_intent_handling"
            ],
            "cross_service_coordination": [
                "test_multi_service_coordination_sequential",
                "test_multi_service_coordination_parallel",
                "test_concurrent_workflow_execution"
            ],
            "cultural_context_handling": [
                "test_cultural_context_integration_hindi",
                "test_cultural_context_timezone_handling"
            ],
            "rollback_error_handling": [
                "test_workflow_rollback_on_failure",
                "test_error_handling_service_timeout",
                "test_error_handling_invalid_input",
                "test_complex_workflow_partial_rollback"
            ]
        }
        
        for criteria, test_names in criteria_mapping.items():
            criteria_tests = []
            all_passed = True
            
            for test in tests:
                test_name = test.get("nodeid", "").split("::")[-1]
                if any(name in test_name for name in test_names):
                    test_result = {
                        "name": test_name,
                        "status": "passed" if test.get("outcome") == "passed" else "failed",
                        "duration": test.get("duration", 0)
                    }
                    criteria_tests.append(test_result)
                    
                    if test.get("outcome") != "passed":
                        all_passed = False
            
            self.results["acceptance_criteria"][criteria]["tests"] = criteria_tests
            self.results["acceptance_criteria"][criteria]["status"] = "passed" if all_passed else "failed"
    
    def _validate_acceptance_criteria(self):
        """Validate all acceptance criteria are met"""
        print("\n✅ Validating Acceptance Criteria...")
        
        criteria_status = []
        
        for criteria, data in self.results["acceptance_criteria"].items():
            status = data["status"]
            criteria_status.append(status == "passed")
            
            if status == "passed":
                print(f"✅ {criteria.replace('_', ' ').title()}: PASSED")
            else:
                print(f"❌ {criteria.replace('_', ' ').title()}: FAILED")
        
        # Overall acceptance criteria validation
        all_criteria_passed = all(criteria_status)
        coverage_met = self.results["coverage_achieved"] >= self.results["coverage_target"]
        
        if all_criteria_passed and coverage_met:
            self.results["overall_status"] = "passed"
            print("\n🎉 All acceptance criteria met!")
        else:
            self.results["overall_status"] = "failed"
            print("\n❌ Some acceptance criteria not met")
    
    def _generate_final_report(self):
        """Generate final test report"""
        print("\n📊 Generating Final Report...")
        
        report_file = f"epic_v3_bk_001_test_report_{int(time.time())}.json"
        
        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 EPIC V3-BK-001 TEST SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {self.results['overall_status'].upper()}")
        print(f"Coverage Achieved: {self.results['coverage_achieved']:.1f}%")
        print(f"Coverage Target: {self.results['coverage_target']}%")
        
        print("\nAcceptance Criteria:")
        for criteria, data in self.results["acceptance_criteria"].items():
            status_icon = "✅" if data["status"] == "passed" else "❌"
            print(f"  {status_icon} {criteria.replace('_', ' ').title()}")
        
        print(f"\nDetailed report saved to: {report_file}")
        print("=" * 60)


def main():
    """Main entry point for test runner"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Epic V3-BK-001 Test Runner")
        print("Validates Action Orchestrator Core Service implementation")
        print("\nUsage: python run_epic_tests.py")
        print("\nTest Categories:")
        print("  - Unit Tests (with coverage)")
        print("  - Integration Tests")
        print("  - Performance Tests")
        print("  - Security Tests")
        print("  - Cultural Context Tests")
        return
    
    runner = EpicV3BK001TestRunner()
    results = runner.run_all_tests()
    
    # Exit with appropriate code
    if results["overall_status"] == "passed":
        print("\n🎉 Epic V3-BK-001 validation successful!")
        sys.exit(0)
    else:
        print("\n❌ Epic V3-BK-001 validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
