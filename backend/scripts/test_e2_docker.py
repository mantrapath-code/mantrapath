#!/usr/bin/env python3
"""
E2 Unified Insights Docker Testing Script

This script tests the unified insights aggregation endpoint
with a real Docker environment and actual user data.
"""

import os
import sys
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Base URLs for services
AUTH_BASE_URL = "http://localhost:8001"
MOOD_BASE_URL = "http://localhost:8002"
ML_BASE_URL = "http://localhost:8008"

class E2TestFramework:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.test_results = []
    
    def log_test(self, test_name: str, status: str, details: Dict[str, Any]):
        """Log test results for later analysis"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        print(f"✅ {test_name}: {status}" if status == "PASSED" else f"❌ {test_name}: {status}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
    
    def authenticate_user(self) -> bool:
        """Authenticate with existing user credentials"""
        try:
            # Login with existing user
            login_data = {
                "email_or_username": "Ramesh123",
                "password": "Dev@#123"
            }
            
            response = self.session.post(
                f"{AUTH_BASE_URL}/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                auth_data = response.json()
                self.access_token = auth_data.get("access_token")
                
                # Get user profile to get user_id
                headers = {"Authorization": f"Bearer {self.access_token}"}
                profile_response = self.session.get(
                    f"{AUTH_BASE_URL}/me",
                    headers=headers,
                    timeout=10
                )
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    self.user_id = profile_data.get("id")
                    
                    self.log_test("Authentication", "PASSED", {
                        "user_id": self.user_id,
                        "token_received": bool(self.access_token)
                    })
                    return True
                else:
                    self.log_test("Authentication", "FAILED", {
                        "error": "Failed to get user profile",
                        "status_code": profile_response.status_code,
                        "response": profile_response.text
                    })
                    return False
            else:
                self.log_test("Authentication", "FAILED", {
                    "error": "Login failed",
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Authentication", "FAILED", {
                "error": str(e),
                "type": type(e).__name__
            })
            return False
    
    def create_test_mood_data(self) -> bool:
        """Create some mood data for testing"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # Create a few mood entries
            mood_entries = [
                {"mood_score": 8, "energy_level": 7, "stress_level": 3, "notes": "Feeling great today!"},
                {"mood_score": 6, "energy_level": 5, "stress_level": 5, "notes": "Average day"},
                {"mood_score": 9, "energy_level": 8, "stress_level": 2, "notes": "Excellent mood!"}
            ]
            
            created_count = 0
            for mood_data in mood_entries:
                response = self.session.post(
                    f"{MOOD_BASE_URL}/api/v1/mood/",
                    json=mood_data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    created_count += 1
                # Sleep briefly between entries
                time.sleep(0.1)
            
            self.log_test("Mood Data Creation", "PASSED", {
                "entries_created": created_count,
                "total_attempted": len(mood_entries)
            })
            return created_count > 0
            
        except Exception as e:
            self.log_test("Mood Data Creation", "FAILED", {
                "error": str(e),
                "type": type(e).__name__
            })
            return False
    
    def test_unified_insights_endpoint(self) -> bool:
        """Test the unified insights aggregation endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            response = self.session.get(
                f"{ML_BASE_URL}/api/v1/insights/unified",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                insights_data = response.json()
                
                # Validate response structure
                required_fields = ["user_id", "timestamp", "aggregated_insights"]
                missing_fields = [field for field in required_fields if field not in insights_data]
                
                if missing_fields:
                    self.log_test("Unified Insights Endpoint", "FAILED", {
                        "error": f"Missing required fields: {missing_fields}",
                        "response": insights_data
                    })
                    return False
                
                # Check if we have mood insights
                aggregated = insights_data.get("aggregated_insights", {})
                mood_insights = aggregated.get("mood", {})
                
                self.log_test("Unified Insights Endpoint", "PASSED", {
                    "response_size": len(json.dumps(insights_data)),
                    "user_id": insights_data.get("user_id"),
                    "mood_stats_present": bool(mood_insights),
                    "mood_total_entries": mood_insights.get("total_entries", 0),
                    "cache_info": insights_data.get("cache_info", {})
                })
                
                # Test cache functionality by making a second request
                return self.test_cache_functionality()
                
            else:
                self.log_test("Unified Insights Endpoint", "FAILED", {
                    "error": "HTTP error",
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Unified Insights Endpoint", "FAILED", {
                "error": str(e),
                "type": type(e).__name__
            })
            return False
    
    def test_cache_functionality(self) -> bool:
        """Test that cache is working by making a second request"""
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # First request (should miss cache)
            start_time = time.time()
            response1 = self.session.get(
                f"{ML_BASE_URL}/api/v1/insights/unified",
                headers=headers,
                timeout=30
            )
            first_duration = time.time() - start_time
            
            # Second request (should hit cache)
            start_time = time.time()
            response2 = self.session.get(
                f"{ML_BASE_URL}/api/v1/insights/unified",
                headers=headers,
                timeout=30
            )
            second_duration = time.time() - start_time
            
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                # Check cache info
                cache1 = data1.get("cache_info", {})
                cache2 = data2.get("cache_info", {})
                
                self.log_test("Cache Functionality", "PASSED", {
                    "first_request_duration": round(first_duration, 3),
                    "second_request_duration": round(second_duration, 3),
                    "first_cache_hit": cache1.get("hit", False),
                    "second_cache_hit": cache2.get("hit", False),
                    "speed_improvement": round((first_duration - second_duration) / first_duration * 100, 2) if first_duration > 0 else 0
                })
                return True
            else:
                self.log_test("Cache Functionality", "FAILED", {
                    "error": "One or both requests failed",
                    "first_status": response1.status_code,
                    "second_status": response2.status_code
                })
                return False
                
        except Exception as e:
            self.log_test("Cache Functionality", "FAILED", {
                "error": str(e),
                "type": type(e).__name__
            })
            return False
    
    def check_service_health(self) -> bool:
        """Check if all required services are healthy"""
        services = [
            ("Auth Service", AUTH_BASE_URL),
            ("Mood Service", MOOD_BASE_URL),
            ("ML Service", ML_BASE_URL)
        ]
        
        healthy_services = 0
        service_details = {}
        
        for service_name, base_url in services:
            try:
                response = self.session.get(f"{base_url}/health", timeout=5)
                if response.status_code == 200:
                    healthy_services += 1
                    service_details[service_name] = "healthy"
                else:
                    service_details[service_name] = f"unhealthy (status: {response.status_code})"
            except Exception as e:
                service_details[service_name] = f"unreachable ({str(e)})"
        
        all_healthy = healthy_services == len(services)
        self.log_test("Service Health", "PASSED" if all_healthy else "FAILED", {
            "healthy_count": healthy_services,
            "total_services": len(services),
            "details": service_details
        })
        
        return all_healthy
    
    def run_e2_tests(self):
        """Run the complete E2 test suite"""
        print("🚀 Starting E2 Unified Insights Testing")
        print("=" * 50)
        
        # Step 1: Check service health
        if not self.check_service_health():
            print("❌ Service health check failed - aborting tests")
            return False
        
        # Step 2: Authenticate
        if not self.authenticate_user():
            print("❌ Authentication failed - aborting tests")
            return False
        
        # Step 3: Create test data
        self.create_test_mood_data()
        
        # Step 4: Test unified insights endpoint
        if not self.test_unified_insights_endpoint():
            print("❌ Unified insights endpoint test failed")
            return False
        
        # Summary
        passed_tests = sum(1 for result in self.test_results if result["status"] == "PASSED")
        total_tests = len(self.test_results)
        
        print("\n" + "=" * 50)
        print(f"🎯 E2 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ All E2 tests passed! Unified insights implementation is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Check the details above.")
            return False

def main():
    """Main test runner"""
    tester = E2TestFramework()
    success = tester.run_e2_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
