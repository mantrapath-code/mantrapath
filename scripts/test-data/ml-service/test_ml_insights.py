#!/usr/bin/env python3
"""
ML Service Test Data Validator and Tester
Tests ML insights endpoints and validates the data we've been working on
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import json
from auth_helper import get_authenticated_session

class MLServiceTester:
    def __init__(self, auth_helper):
        self.auth = auth_helper
        
    def test_ml_endpoints(self):
        """Test all ML service endpoints"""
        print("🔬 Testing ML Service Endpoints...")
        
        endpoints = [
            ("/ml/personalized-insights/me", "GET", "Personalized Insights"),
            ("/ml/analyze-patterns/me", "POST", "Pattern Analysis"),
            ("/ml/correlation-analysis/me", "GET", "Correlation Analysis"),
            ("/ml/health", "GET", "Health Check")
        ]
        
        results = {}
        
        for endpoint, method, name in endpoints:
            try:
                print(f"\n📊 Testing {name}...")
                
                response = self.auth.make_request(method, endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    results[name] = {
                        "status": "✅ SUCCESS",
                        "data_keys": list(data.keys()) if isinstance(data, dict) else "Non-dict response",
                        "response_size": len(str(data))
                    }
                    print(f"✅ {name}: SUCCESS")
                    
                    # Print key insights for pattern analysis
                    if "patterns" in endpoint:
                        self.analyze_pattern_response(data)
                    elif "insights" in endpoint:
                        self.analyze_insights_response(data)
                    elif "correlation" in endpoint:
                        self.analyze_correlation_response(data)
                        
                else:
                    results[name] = {
                        "status": f"❌ FAILED ({response.status_code})",
                        "error": response.text[:200]
                    }
                    print(f"❌ {name}: FAILED ({response.status_code})")
                    
            except Exception as e:
                results[name] = {
                    "status": f"❌ ERROR",
                    "error": str(e)[:200]
                }
                print(f"❌ {name}: ERROR - {e}")
        
        return results
    
    def analyze_pattern_response(self, data):
        """Analyze pattern analysis response"""
        print("  📈 Pattern Analysis Details:")
        
        if "statistics" in data:
            stats = data["statistics"]
            print(f"    • Best day: {stats.get('best_day', 'Not found')}")
            print(f"    • Energy peak: {stats.get('energy_peak', 'Not found')}")
            print(f"    • Mood streak: {stats.get('mood_streak', 'Not found')} days")
            print(f"    • Weekly average: {stats.get('weekly_average_mood', 'Not found')}")
        
        if "patterns" in data:
            patterns = data["patterns"]
            print(f"    • Pattern count: {len(patterns) if isinstance(patterns, list) else 'N/A'}")
        
        if "insights" in data:
            insights = data["insights"]
            print(f"    • Insights count: {len(insights) if isinstance(insights, list) else 'N/A'}")
    
    def analyze_insights_response(self, data):
        """Analyze personalized insights response"""
        print("  🎯 Personalized Insights Details:")
        
        if "insights" in data:
            insights = data["insights"]
            print(f"    • Total insights: {len(insights) if isinstance(insights, list) else 'N/A'}")
        
        if "recommendations" in data:
            recommendations = data["recommendations"]
            print(f"    • Recommendations: {len(recommendations) if isinstance(recommendations, list) else 'N/A'}")
        
        if "confidence_score" in data:
            print(f"    • Confidence: {data['confidence_score']}")
    
    def analyze_correlation_response(self, data):
        """Analyze correlation analysis response"""
        print("  🔗 Correlation Analysis Details:")
        
        if "correlations" in data:
            correlations = data["correlations"]
            print(f"    • Correlation count: {len(correlations) if isinstance(correlations, list) else 'N/A'}")
        
        if "mood_statistics" in data:
            stats = data["mood_statistics"]
            print(f"    • Mood stats available: {bool(stats)}")
    
    def test_frontend_integration(self):
        """Test the frontend unified insight service integration"""
        print("\n🔗 Testing Frontend Integration...")
        
        # Test the frontend API endpoints that call ML service
        frontend_endpoints = [
            ("http://localhost:5173", "Frontend Server"),
            ("http://localhost:8000/api/v1/ml/personalized-insights/me", "API Gateway ML Route"),
            ("http://localhost:8008/ml/personalized-insights/me", "Direct ML Service")
        ]
        
        for url, name in frontend_endpoints:
            try:
                if "localhost:5173" in url:
                    print(f"✅ {name}: Should be running (check browser)")
                else:
                    response = self.auth.make_request("GET", url.replace("http://localhost:8000", ""))
                    if response.status_code == 200:
                        print(f"✅ {name}: Accessible")
                    else:
                        print(f"❌ {name}: Failed ({response.status_code})")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
    
    def generate_insights_test_report(self):
        """Generate a comprehensive test report for insights"""
        print("\n📋 Generating ML Insights Test Report...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "user_id": self.auth.get_user_id(),
            "tests": {},
            "summary": {}
        }
        
        # Test all endpoints
        endpoint_results = self.test_ml_endpoints()
        report["tests"]["endpoints"] = endpoint_results
        
        # Test integration
        self.test_frontend_integration()
        
        # Summary
        successful_tests = sum(1 for result in endpoint_results.values() if "SUCCESS" in result["status"])
        total_tests = len(endpoint_results)
        
        report["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%",
            "status": "PASS" if successful_tests == total_tests else "PARTIAL" if successful_tests > 0 else "FAIL"
        }
        
        # Save report
        report_file = f"/Users/sachin/Documents/GitHub/mantrapath/scripts/test-data/ml_insights_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved: {report_file}")
        print(f"🎯 Overall Status: {report['summary']['status']}")
        print(f"📊 Success Rate: {report['summary']['success_rate']}")
        
        return report
    
    def validate_insights_data_flow(self):
        """Validate that insights show real data instead of fallbacks"""
        print("\n🔍 Validating Insights Data Flow...")
        
        try:
            # Test pattern analysis for statistics
            response = self.auth.make_request("POST", "/ml/analyze-patterns/me")
            
            if response.status_code == 200:
                data = response.json()
                
                print("🔬 Checking for real vs fallback data...")
                
                # Check statistics section
                if "statistics" in data:
                    stats = data["statistics"]
                    
                    # These should NOT be empty/default values if we have real data
                    best_day = stats.get("best_day", "")
                    energy_peak = stats.get("energy_peak", 0)
                    mood_streak = stats.get("mood_streak", 0)
                    
                    print(f"  📅 Best day: '{best_day}' {'✅ Has data' if best_day else '⚠️ Empty'}")
                    print(f"  ⚡ Energy peak: {energy_peak} {'✅ Has data' if energy_peak > 0 else '⚠️ Zero/Empty'}")
                    print(f"  🔥 Mood streak: {mood_streak} days {'✅ Has data' if mood_streak > 0 else '⚠️ Zero'}")
                    
                    if best_day and energy_peak > 0:
                        print("✅ REAL DATA: Statistics contain actual calculated values")
                    else:
                        print("⚠️ LIMITED DATA: Some statistics are empty (may need more mood entries)")
                else:
                    print("❌ NO STATISTICS: Statistics section missing from response")
            else:
                print(f"❌ ENDPOINT FAILED: {response.status_code}")
                
        except Exception as e:
            print(f"❌ VALIDATION ERROR: {e}")

def main():
    """Main function to run ML service testing"""
    print("🚀 Starting ML Service Test Data Validation...")
    
    try:
        # Get authenticated session
        auth = get_authenticated_session("primary")
        tester = MLServiceTester(auth)
        
        # Choose testing option
        print("\n" + "="*50)
        print("Choose ML service testing option:")
        print("1. Test all ML endpoints")
        print("2. Validate insights data flow")
        print("3. Generate comprehensive test report")
        print("4. Test frontend integration")
        print("5. Full validation suite (all tests)")
        print("="*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            tester.test_ml_endpoints()
        elif choice == "2":
            tester.validate_insights_data_flow()
        elif choice == "3":
            tester.generate_insights_test_report()
        elif choice == "4":
            tester.test_frontend_integration()
        elif choice == "5":
            print("🎯 Running full validation suite...")
            tester.test_ml_endpoints()
            tester.validate_insights_data_flow()
            tester.test_frontend_integration()
            tester.generate_insights_test_report()
        else:
            print("❌ Invalid choice")
            return
        
        print("\n🎉 ML service testing completed!")
        print("\n💡 Next steps:")
        print("   • Check the insights section in your browser at http://localhost:5173")
        print("   • Look for 'Best day', 'Energy peak', and 'Mood streak' values")
        print("   • If values are still empty, run mood data generation first")
        
    except Exception as e:
        print(f"❌ Error in ML service testing: {e}")

if __name__ == "__main__":
    main()
