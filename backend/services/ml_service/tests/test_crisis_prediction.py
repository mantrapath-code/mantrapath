"""
🧪 Crisis Prediction System - Comprehensive Test Suite

Live testing suite for Phase 2A crisis prediction and early warning system.
Tests both individual components and full end-to-end scenarios.

Test Categories:
- Unit Tests: Individual ML model components
- Integration Tests: API endpoints and service interactions  
- Load Tests: System performance under stress
- Safety Tests: Crisis detection accuracy and response times
- End-to-End Tests: Complete user journey scenarios
"""

import pytest
import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import aiohttp
import time
from unittest.mock import Mock, patch

# Test configuration
TEST_CONFIG = {
    "ml_service_url": "http://localhost:8008",
    "test_timeout": 30,
    "load_test_users": 500,  # Increased for more realistic production load testing
    "crisis_threshold_accuracy": 0.85,
    "response_time_threshold": 5.0,  # seconds
    "uptime_requirement": 99.0,  # percent
}

class CrisisPredictionTester:
    """Comprehensive testing class for crisis prediction system"""
    
    def __init__(self, base_url: str = TEST_CONFIG["ml_service_url"]):
        self.base_url = base_url
        self.test_results = []
        self.session = None
    
    async def setup_session(self):
        """Initialize HTTP session for testing"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=TEST_CONFIG["test_timeout"])
            )
    
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", data: Dict = None, headers: Dict = None):
        """Make HTTP request with error handling and timing"""
        await self.setup_session()
        
        url = f"{self.base_url}{endpoint}"
        
        # Add authentication header (mock for testing)
        if not headers:
            headers = {}
        headers["Authorization"] = "Bearer test-token"
        headers["Content-Type"] = "application/json"
        
        start_time = time.time()
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=headers) as response:
                    response_time = time.time() - start_time
                    content = await response.json() if response.content_type == 'application/json' else await response.text()
                    return {
                        "status": response.status,
                        "data": content,
                        "response_time": response_time,
                        "success": response.status == 200
                    }
            elif method == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    response_time = time.time() - start_time
                    content = await response.json() if response.content_type == 'application/json' else await response.text()
                    return {
                        "status": response.status,
                        "data": content,
                        "response_time": response_time,
                        "success": response.status == 200
                    }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "response_time": time.time() - start_time,
                "success": False
            }

# 🔧 Unit Tests for Individual Components

class TestCrisisPredictionModels:
    """Test individual ML model components"""
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "user_id": "test-user-123",
            "mood_entries": [
                {
                    "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                    "mood_score": max(1, 5 - i * 0.5),  # Declining mood pattern
                    "energy_level": max(1, 5 - i * 0.3),
                    "stress_level": min(10, 3 + i * 0.4),
                    "notes": f"Day {i} mood entry"
                }
                for i in range(14)  # 2 weeks of data
            ],
            "journal_entries": [
                {
                    "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                    "content": f"Feeling overwhelmed today. Day {i} has been particularly challenging.",
                    "sentiment": "negative" if i < 7 else "neutral"
                }
                for i in range(7)  # 1 week of journal entries
            ],
            "activity_data": {
                "sleep_hours_avg": max(4, 8 - len([i for i in range(14) if i < 7]) * 0.3),
                "exercise_minutes_avg": max(0, 30 - len([i for i in range(14) if i < 5]) * 5),
                "social_interactions": max(0, 10 - len([i for i in range(14) if i < 10]))
            },
            "demographic_info": {
                "age": 28,
                "timezone": "America/New_York"
            }
        }
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test ML service health endpoint"""
        tester = CrisisPredictionTester()
        try:
            result = await tester.make_request("/health")
            
            assert result["success"], f"Health check failed: {result['data']}"
            assert result["response_time"] < 2.0, f"Health check too slow: {result['response_time']}s"
            
            # Verify crisis prediction components are loaded
            data = result["data"]
            assert data.get("models_loaded", {}).get("crisis_predictor") is not None
            assert data.get("phase_2a_active") is True
            
            print(f"✅ Health check passed in {result['response_time']:.2f}s")
            
        finally:
            await tester.cleanup_session()
    
    @pytest.mark.asyncio
    async def test_crisis_prediction_endpoint(self, sample_user_data):
        """Test crisis risk prediction endpoint"""
        tester = CrisisPredictionTester()
        try:
            # Test crisis prediction
            result = await tester.make_request(
                "/crisis/predict-risk",
                method="POST",
                data={
                    "user_id": sample_user_data["user_id"],
                    "mood_entries": sample_user_data["mood_entries"],
                    "journal_entries": sample_user_data["journal_entries"],
                    "activity_data": sample_user_data["activity_data"],
                    "demographic_info": sample_user_data["demographic_info"],
                    "include_interventions": True
                }
            )
            
            assert result["success"], f"Crisis prediction failed: {result['data']}"
            assert result["response_time"] < TEST_CONFIG["response_time_threshold"], \
                f"Crisis prediction too slow: {result['response_time']}s"
            
            # Verify response structure
            crisis_data = result["data"]["crisis_assessment"]
            required_fields = [
                "crisis_probability", "risk_level", "confidence",
                "key_risk_factors", "recommended_interventions", "urgency_level"
            ]
            
            for field in required_fields:
                assert field in crisis_data, f"Missing required field: {field}"
            
            # Verify data types and ranges
            assert 0 <= crisis_data["crisis_probability"] <= 1, "Crisis probability out of range"
            assert crisis_data["risk_level"] in ["MINIMAL", "LOW", "MEDIUM", "HIGH"], "Invalid risk level"
            assert crisis_data["urgency_level"] in ["ROUTINE", "MODERATE", "URGENT", "IMMEDIATE"], "Invalid urgency level"
            
            print(f"✅ Crisis prediction test passed - Risk: {crisis_data['risk_level']}, "
                  f"Probability: {crisis_data['crisis_probability']:.3f}")
            
        finally:
            await tester.cleanup_session()
    
    @pytest.mark.asyncio
    async def test_user_monitoring_endpoint(self, sample_user_data):
        """Test real-time user monitoring endpoint"""
        tester = CrisisPredictionTester()
        try:
            result = await tester.make_request(
                "/crisis/monitor-user",
                method="POST",
                data={
                    "user_id": sample_user_data["user_id"],
                    "user_data": sample_user_data,
                    "force_check": True
                }
            )
            
            assert result["success"], f"User monitoring failed: {result['data']}"
            assert result["response_time"] < 3.0, f"User monitoring too slow: {result['response_time']}s"
            
            # Verify monitoring result structure
            monitoring_data = result["data"]["monitoring_result"]
            assert "risk_assessment" in monitoring_data or "alert_triggered" in monitoring_data
            
            print(f"✅ User monitoring test passed in {result['response_time']:.2f}s")
            
        finally:
            await tester.cleanup_session()
    
    @pytest.mark.asyncio
    async def test_dashboard_metrics_endpoint(self):
        """Test dashboard metrics endpoint"""
        tester = CrisisPredictionTester()
        try:
            result = await tester.make_request("/dashboard/metrics")
            
            assert result["success"], f"Dashboard metrics failed: {result['data']}"
            assert result["response_time"] < 2.0, f"Dashboard metrics too slow: {result['response_time']}s"
            
            # Verify metrics structure
            metrics = result["data"]["dashboard_metrics"]
            system_status = result["data"]["system_status"]
            
            required_metrics = [
                "total_predictions", "high_risk_alerts", "intervention_success_rate", "avg_response_time"
            ]
            
            for metric in required_metrics:
                assert metric in metrics, f"Missing metric: {metric}"
                assert isinstance(metrics[metric], (int, float)), f"Invalid metric type: {metric}"
            
            print(f"✅ Dashboard metrics test passed - {metrics['total_predictions']} predictions today")
            
        finally:
            await tester.cleanup_session()

# 🏋️ Load Testing Suite

class TestCrisisPredictionLoad:
    """Load testing for crisis prediction system"""
    
    @pytest.mark.asyncio
    async def test_graduated_load_testing(self):
        """Test system with graduated load increases"""
        tester = CrisisPredictionTester()
        
        # Graduated load test phases
        load_phases = [
            {"users": 50, "name": "Light Load"},
            {"users": 150, "name": "Medium Load"},
            {"users": 300, "name": "Heavy Load"},
            {"users": 500, "name": "Peak Load"}
        ]
        
        phase_results = []
        
        for phase in load_phases:
            print(f"\n🏋️ Testing {phase['name']} ({phase['users']} users)...")
            
            # Create test data for this phase
            test_users = []
            for i in range(phase["users"]):
                test_users.append({
                    "user_id": f"load-test-user-{i}",
                    "mood_entries": [
                        {
                            "timestamp": (datetime.utcnow() - timedelta(hours=j)).isoformat(),
                            "mood_score": np.random.uniform(1, 5),
                            "energy_level": np.random.uniform(1, 10),
                            "stress_level": np.random.uniform(1, 10)
                        }
                        for j in range(12)  # 12 hours of data for faster processing
                    ],
                    "include_interventions": False
                })
            
            try:
                # Execute concurrent requests for this phase
                tasks = []
                for user_data in test_users:
                    task = tester.make_request(
                        "/crisis/predict-risk",
                        method="POST",
                        data=user_data
                    )
                    tasks.append(task)
                
                start_time = time.time()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                total_time = time.time() - start_time
                
                # Analyze phase results
                successful_requests = [r for r in results if not isinstance(r, Exception) and r["success"]]
                failed_requests = len(results) - len(successful_requests)
                success_rate = len(successful_requests) / len(results) * 100
                avg_response_time = np.mean([r["response_time"] for r in successful_requests]) if successful_requests else float('inf')
                throughput = len(results) / total_time
                
                phase_result = {
                    "phase": phase["name"],
                    "users": phase["users"],
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "throughput": throughput,
                    "failed_requests": failed_requests
                }
                phase_results.append(phase_result)
                
                print(f"   Success Rate: {success_rate:.1f}%")
                print(f"   Avg Response Time: {avg_response_time:.2f}s")
                print(f"   Throughput: {throughput:.1f} req/s")
                print(f"   Failed Requests: {failed_requests}")
                
                # Check if system is degrading
                if success_rate < 90.0:
                    print(f"   ⚠️ System degradation detected at {phase['users']} users")
                    break
                elif avg_response_time > TEST_CONFIG["response_time_threshold"] * 2:
                    print(f"   ⚠️ Response time degradation at {phase['users']} users")
                    break
                else:
                    print(f"   ✅ {phase['name']} passed")
                    
            except Exception as e:
                print(f"   ❌ {phase['name']} failed: {str(e)}")
                break
        
        # Summary of graduated load test
        print(f"\n📊 Graduated Load Test Summary:")
        for result in phase_results:
            print(f"   {result['phase']}: {result['success_rate']:.1f}% success, "
                  f"{result['avg_response_time']:.2f}s avg, {result['throughput']:.1f} req/s")
        
        # Determine maximum sustainable load
        max_sustainable = max([r["users"] for r in phase_results if r["success_rate"] >= 95.0], default=0)
        print(f"\n🎯 Maximum Sustainable Load: {max_sustainable} concurrent users")
        
        assert len(phase_results) > 0, "No load test phases completed successfully"
        assert max_sustainable >= 150, f"System cannot handle minimum required load of 150 users (max: {max_sustainable})"
        
        print(f"✅ Graduated load test completed!")
    
    @pytest.mark.asyncio
    async def test_concurrent_predictions(self):
        """Test system under concurrent load (legacy test)"""
        tester = CrisisPredictionTester()
        
        # Create sample data for multiple users
        test_users = []
        for i in range(TEST_CONFIG["load_test_users"]):
            test_users.append({
                "user_id": f"load-test-user-{i}",
                "mood_entries": [
                    {
                        "timestamp": (datetime.utcnow() - timedelta(hours=j)).isoformat(),
                        "mood_score": np.random.uniform(1, 5),
                        "energy_level": np.random.uniform(1, 10),
                        "stress_level": np.random.uniform(1, 10)
                    }
                    for j in range(24)  # 24 hours of data
                ],
                "include_interventions": False  # Faster processing
            })
        
        try:
            # Create concurrent requests
            tasks = []
            for user_data in test_users:
                task = tester.make_request(
                    "/crisis/predict-risk",
                    method="POST",
                    data=user_data
                )
                tasks.append(task)
            
            # Execute all requests concurrently
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # Analyze results
            successful_requests = [r for r in results if not isinstance(r, Exception) and r["success"]]
            failed_requests = len(results) - len(successful_requests)
            
            success_rate = len(successful_requests) / len(results) * 100
            avg_response_time = np.mean([r["response_time"] for r in successful_requests]) if successful_requests else float('inf')
            
            print(f"🏋️ Load Test Results:")
            print(f"   Total Users: {len(test_users)}")
            print(f"   Success Rate: {success_rate:.1f}%")
            print(f"   Failed Requests: {failed_requests}")
            print(f"   Average Response Time: {avg_response_time:.2f}s")
            print(f"   Total Test Time: {total_time:.2f}s")
            print(f"   Throughput: {len(results)/total_time:.1f} requests/second")
            
            # Assertions for load test
            assert success_rate >= 95.0, f"Success rate too low: {success_rate}%"
            assert avg_response_time < TEST_CONFIG["response_time_threshold"], \
                f"Average response time too high: {avg_response_time}s"
            
            print(f"✅ Load test passed!")
            
        finally:
            await tester.cleanup_session()

# 🛡️ Safety and Accuracy Tests

class TestCrisisSafetyAccuracy:
    """Test crisis detection accuracy and safety protocols"""
    
    @pytest.mark.asyncio
    async def test_high_risk_detection_accuracy(self):
        """Test accuracy of high-risk crisis detection"""
        tester = CrisisPredictionTester()
        
        # Create test cases with known high-risk patterns
        high_risk_cases = [
            {
                "name": "Severe Mood Decline",
                "data": {
                    "user_id": "high-risk-test-1",
                    "mood_entries": [
                        {
                            "timestamp": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                            "mood_score": max(1, 5 - i * 0.8),  # Rapid decline
                            "energy_level": max(1, 5 - i * 0.7),
                            "stress_level": min(10, 3 + i * 1.2)
                        }
                        for i in range(7)
                    ],
                    "journal_entries": [
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "content": "I feel hopeless. Nothing seems to matter anymore. I don't see a way forward.",
                            "sentiment": "very_negative"
                        }
                    ]
                },
                "expected_risk": "HIGH"
            },
            {
                "name": "Sleep and Social Isolation",
                "data": {
                    "user_id": "high-risk-test-2",
                    "activity_data": {
                        "sleep_hours_avg": 3,  # Severe sleep deprivation
                        "social_interactions": 0,  # Complete isolation
                        "exercise_minutes_avg": 0
                    },
                    "mood_entries": [
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "mood_score": 1,
                            "energy_level": 1,
                            "stress_level": 10
                        }
                    ]
                },
                "expected_risk": "HIGH"
            }
        ]
        
        correct_predictions = 0
        
        try:
            for case in high_risk_cases:
                result = await tester.make_request(
                    "/crisis/predict-risk",
                    method="POST",
                    data=case["data"]
                )
                
                if result["success"]:
                    crisis_data = result["data"]["crisis_assessment"]
                    predicted_risk = crisis_data["risk_level"]
                    
                    print(f"🛡️ Safety Test - {case['name']}: "
                          f"Predicted {predicted_risk} (Expected {case['expected_risk']})")
                    
                    if predicted_risk == case["expected_risk"]:
                        correct_predictions += 1
                    
                    # Verify intervention recommendations for high risk
                    if predicted_risk in ["HIGH", "CRITICAL"]:
                        assert len(crisis_data["recommended_interventions"]) > 0, \
                            "High risk cases must have intervention recommendations"
                        assert crisis_data["urgency_level"] in ["URGENT", "IMMEDIATE"], \
                            "High risk cases must have urgent urgency level"
        
            accuracy = correct_predictions / len(high_risk_cases) * 100
            
            print(f"🛡️ Safety Test Results: {accuracy:.1f}% accuracy ({correct_predictions}/{len(high_risk_cases)})")
            
            assert accuracy >= TEST_CONFIG["crisis_threshold_accuracy"] * 100, \
                f"Crisis detection accuracy too low: {accuracy}%"
            
            print("✅ Safety and accuracy tests passed!")
            
        finally:
            await tester.cleanup_session()

# 🔄 End-to-End Integration Tests

class TestEndToEndCrisisFlow:
    """Test complete crisis prediction workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_crisis_workflow(self):
        """Test full crisis detection and response workflow"""
        tester = CrisisPredictionTester()
        
        try:
            test_user_id = "e2e-test-user"
            
            # Step 1: Predict crisis risk
            print("🔄 Step 1: Crisis Risk Prediction")
            risk_result = await tester.make_request(
                "/crisis/predict-risk",
                method="POST",
                data={
                    "user_id": test_user_id,
                    "mood_entries": [
                        {
                            "timestamp": datetime.utcnow().isoformat(),
                            "mood_score": 2,
                            "energy_level": 2,
                            "stress_level": 8
                        }
                    ],
                    "include_interventions": True
                }
            )
            
            assert risk_result["success"], "Crisis prediction failed"
            crisis_data = risk_result["data"]["crisis_assessment"]
            print(f"   ✅ Risk Level: {crisis_data['risk_level']}")
            
            # Step 2: Monitor user
            print("🔄 Step 2: User Monitoring")
            monitor_result = await tester.make_request(
                "/crisis/monitor-user",
                method="POST",
                data={
                    "user_id": test_user_id,
                    "user_data": {"current_mood": "low"},
                    "force_check": True
                }
            )
            
            assert monitor_result["success"], "User monitoring failed"
            print("   ✅ User monitoring active")
            
            # Step 3: Check alert status
            print("🔄 Step 3: Alert Status Check")
            status_result = await tester.make_request(f"/crisis/alert-status/{test_user_id}")
            
            assert status_result["success"], "Alert status check failed"
            print("   ✅ Alert status retrieved")
            
            # Step 4: Get dashboard metrics
            print("🔄 Step 4: Dashboard Metrics")
            dashboard_result = await tester.make_request("/dashboard/metrics")
            
            assert dashboard_result["success"], "Dashboard metrics failed"
            print("   ✅ Dashboard metrics available")
            
            # Step 5: System health check
            print("🔄 Step 5: System Health")
            health_result = await tester.make_request("/dashboard/health")
            
            assert health_result["success"], "System health check failed"
            system_status = health_result["data"]["system_status"]
            print(f"   ✅ System Status: {system_status['dashboard_status']}")
            
            print("🎉 End-to-end crisis workflow test passed!")
            
        finally:
            await tester.cleanup_session()

# 📊 Test Execution and Reporting

async def run_all_tests():
    """Execute all crisis prediction tests and generate report"""
    print("🧪 Starting Crisis Prediction System Test Suite")
    print("=" * 60)
    
    test_results = {
        "start_time": datetime.utcnow(),
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "errors": []
    }
    
    test_classes = [
        TestCrisisPredictionModels,
        TestCrisisPredictionLoad,
        TestCrisisSafetyAccuracy,
        TestEndToEndCrisisFlow
    ]
    
    for test_class in test_classes:
        print(f"\n🧪 Running {test_class.__name__}")
        print("-" * 40)
        
        # Run tests in the class
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            test_results["tests_run"] += 1
            try:
                print(f"   Running {test_method}...")
                if asyncio.iscoroutinefunction(getattr(test_instance, test_method)):
                    await getattr(test_instance, test_method)()
                else:
                    getattr(test_instance, test_method)()
                test_results["tests_passed"] += 1
                print(f"   ✅ {test_method} passed")
            except Exception as e:
                test_results["tests_failed"] += 1
                test_results["errors"].append(f"{test_class.__name__}.{test_method}: {str(e)}")
                print(f"   ❌ {test_method} failed: {str(e)}")
    
    # Generate test report
    test_results["end_time"] = datetime.utcnow()
    test_results["duration"] = (test_results["end_time"] - test_results["start_time"]).total_seconds()
    
    print("\n" + "=" * 60)
    print("🧪 CRISIS PREDICTION TEST REPORT")
    print("=" * 60)
    print(f"Tests Run:     {test_results['tests_run']}")
    print(f"Tests Passed:  {test_results['tests_passed']}")
    print(f"Tests Failed:  {test_results['tests_failed']}")
    print(f"Success Rate:  {(test_results['tests_passed']/test_results['tests_run']*100):.1f}%")
    print(f"Duration:      {test_results['duration']:.2f}s")
    
    if test_results["errors"]:
        print(f"\n❌ FAILED TESTS:")
        for error in test_results["errors"]:
            print(f"   - {error}")
    
    if test_results["tests_failed"] == 0:
        print("\n🎉 ALL TESTS PASSED! Crisis prediction system is ready for production.")
    else:
        print(f"\n⚠️  {test_results['tests_failed']} tests failed. Review and fix before production deployment.")
    
    return test_results

# Command line execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Crisis Prediction System Test Suite')
    parser.add_argument('--url', default=TEST_CONFIG["ml_service_url"], 
                       help='ML Service base URL')
    parser.add_argument('--load-users', type=int, default=TEST_CONFIG["load_test_users"],
                       help='Number of users for load testing')
    parser.add_argument('--timeout', type=int, default=TEST_CONFIG["test_timeout"],
                       help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    TEST_CONFIG["ml_service_url"] = args.url
    TEST_CONFIG["load_test_users"] = args.load_users
    TEST_CONFIG["test_timeout"] = args.timeout
    
    # Run all tests
    asyncio.run(run_all_tests())
