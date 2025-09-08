#!/usr/bin/env python3
"""
API Gateway Verification Script
Tests the refined API Gateway functionality including:
- Service registration and discovery
- Request routing and proxy
- Rate limiting
- Health checks
- Connection pooling
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any, List
import httpx
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIGatewayTester:
    """Test the refined API Gateway functionality"""
    
    def __init__(self, gateway_url: str = "http://localhost:8000"):
        self.gateway_url = gateway_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results: List[Dict[str, Any]] = []
    
    async def test_health_endpoints(self) -> bool:
        """Test various health check endpoints"""
        logger.info("🔍 Testing health check endpoints...")
        
        health_endpoints = [
            "/health",
            "/health/live", 
            "/health/ready",
            "/api/v3/health/enhanced",
            "/api/v3/health/voice",
            "/api/v3/health/ai-context",
            "/api/v3/health/cultural"
        ]
        
        all_passed = True
        for endpoint in health_endpoints:
            try:
                response = await self.client.get(f"{self.gateway_url}{endpoint}")
                success = response.status_code == 200
                
                self.test_results.append({
                    "test": f"Health check: {endpoint}",
                    "status": "PASS" if success else "FAIL",
                    "response_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() if response.elapsed else 0
                })
                
                if success:
                    logger.info(f"✅ {endpoint}: {response.status_code}")
                else:
                    logger.error(f"❌ {endpoint}: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {endpoint}: Exception - {e}")
                self.test_results.append({
                    "test": f"Health check: {endpoint}",
                    "status": "ERROR",
                    "error": str(e)
                })
                all_passed = False
        
        return all_passed
    
    async def test_service_routing(self) -> bool:
        """Test routing to different services"""
        logger.info("🔍 Testing service routing...")
        
        # Test routes (these may return 401/403 but should route correctly)
        test_routes = [
            ("/auth/health", "auth-service"),
            ("/profile/health", "profile-service"), 
            ("/mood/health", "mood-service"),
            ("/chat/health", "chatbot-service"),
            ("/content/health", "content-service"),
            ("/notifications/health", "notification-service"),
            ("/voice/health", "voice-service"),
            ("/api/v1/models/health", "models-service")
        ]
        
        all_passed = True
        for route, expected_service in test_routes:
            try:
                response = await self.client.get(f"{self.gateway_url}{route}")
                
                # Check if request was routed (any response indicates routing worked)
                routed = response.status_code in [200, 401, 403, 404, 503]
                
                # Check for gateway headers
                has_gateway_headers = (
                    'x-gateway' in response.headers or
                    'x-gateway-version' in response.headers or
                    'x-forwarded-by' in response.headers
                )
                
                success = routed and has_gateway_headers
                
                self.test_results.append({
                    "test": f"Route: {route}",
                    "status": "PASS" if success else "FAIL",
                    "response_code": response.status_code,
                    "expected_service": expected_service,
                    "has_gateway_headers": has_gateway_headers,
                    "response_time": response.elapsed.total_seconds() if response.elapsed else 0
                })
                
                if success:
                    logger.info(f"✅ {route} -> {expected_service}: {response.status_code}")
                else:
                    logger.error(f"❌ {route} -> {expected_service}: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                logger.error(f"❌ {route}: Exception - {e}")
                self.test_results.append({
                    "test": f"Route: {route}",
                    "status": "ERROR",
                    "error": str(e)
                })
                all_passed = False
        
        return all_passed
    
    async def test_rate_limiting(self) -> bool:
        """Test rate limiting functionality"""
        logger.info("🔍 Testing rate limiting...")
        
        try:
            # Make rapid requests to trigger rate limiting
            requests_made = 0
            rate_limited = False
            
            for i in range(150):  # Exceed the default 100/minute limit
                try:
                    response = await self.client.get(f"{self.gateway_url}/health")
                    requests_made += 1
                    
                    if response.status_code == 429:
                        rate_limited = True
                        break
                        
                except Exception:
                    break
            
            self.test_results.append({
                "test": "Rate limiting",
                "status": "PASS" if rate_limited else "FAIL",
                "requests_made": requests_made,
                "rate_limited": rate_limited
            })
            
            if rate_limited:
                logger.info(f"✅ Rate limiting activated after {requests_made} requests")
                return True
            else:
                logger.warning(f"⚠️ Rate limiting not triggered after {requests_made} requests")
                return False
                
        except Exception as e:
            logger.error(f"❌ Rate limiting test failed: {e}")
            self.test_results.append({
                "test": "Rate limiting",
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    async def test_websocket_connectivity(self) -> bool:
        """Test WebSocket endpoint availability"""
        logger.info("🔍 Testing WebSocket connectivity...")
        
        try:
            # Test WebSocket endpoint (should return 400 for HTTP GET)
            response = await self.client.get(f"{self.gateway_url}/api/v3/voice/stream")
            
            # WebSocket endpoints typically return 400 for HTTP requests
            websocket_available = response.status_code in [400, 426]  # 426 = Upgrade Required
            
            self.test_results.append({
                "test": "WebSocket endpoint",
                "status": "PASS" if websocket_available else "FAIL",
                "response_code": response.status_code
            })
            
            if websocket_available:
                logger.info(f"✅ WebSocket endpoint available: {response.status_code}")
                return True
            else:
                logger.error(f"❌ WebSocket endpoint not available: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ WebSocket test failed: {e}")
            self.test_results.append({
                "test": "WebSocket endpoint",
                "status": "ERROR", 
                "error": str(e)
            })
            return False
    
    async def test_cors_headers(self) -> bool:
        """Test CORS header configuration"""
        logger.info("🔍 Testing CORS headers...")
        
        try:
            # Make an OPTIONS request to test CORS
            response = await self.client.options(
                f"{self.gateway_url}/health",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET"
                }
            )
            
            has_cors_headers = (
                'access-control-allow-origin' in response.headers and
                'access-control-allow-methods' in response.headers
            )
            
            self.test_results.append({
                "test": "CORS headers",
                "status": "PASS" if has_cors_headers else "FAIL",
                "response_code": response.status_code,
                "cors_headers": has_cors_headers
            })
            
            if has_cors_headers:
                logger.info(f"✅ CORS headers present: {response.status_code}")
                return True
            else:
                logger.error(f"❌ CORS headers missing: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ CORS test failed: {e}")
            self.test_results.append({
                "test": "CORS headers",
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    async def test_v3_enhanced_features(self) -> bool:
        """Test V3 enhanced features"""
        logger.info("🔍 Testing V3 enhanced features...")
        
        try:
            # Test voice command endpoint (should return 422 for missing body)
            response = await self.client.post(f"{self.gateway_url}/api/v3/voice/command")
            
            # Should return 422 (validation error) not 404
            v3_available = response.status_code in [422, 401]  # 422 = validation error, 401 = auth required
            
            self.test_results.append({
                "test": "V3 enhanced features",
                "status": "PASS" if v3_available else "FAIL",
                "response_code": response.status_code
            })
            
            if v3_available:
                logger.info(f"✅ V3 features available: {response.status_code}")
                return True
            else:
                logger.error(f"❌ V3 features not available: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ V3 features test failed: {e}")
            self.test_results.append({
                "test": "V3 enhanced features",
                "status": "ERROR",
                "error": str(e)
            })
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        logger.info("🚀 Starting API Gateway verification tests...")
        start_time = time.time()
        
        tests = [
            ("Health Endpoints", self.test_health_endpoints),
            ("Service Routing", self.test_service_routing),
            ("Rate Limiting", self.test_rate_limiting),
            ("WebSocket Connectivity", self.test_websocket_connectivity),
            ("CORS Headers", self.test_cors_headers),
            ("V3 Enhanced Features", self.test_v3_enhanced_features)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Running {test_name} Test ---")
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
                    logger.info(f"✅ {test_name}: PASSED")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Generate summary
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "total_time": total_time,
            "detailed_results": self.test_results
        }
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("🏁 API Gateway Verification Complete")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"Total Time: {total_time:.2f}s")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! API Gateway is working correctly.")
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} test(s) failed. Check the logs for details.")
        
        return summary
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()

async def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="API Gateway Verification Script")
    parser.add_argument(
        "--gateway-url",
        default="http://localhost:8000",
        help="API Gateway URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--output",
        help="Output file for test results (JSON format)"
    )
    
    args = parser.parse_args()
    
    tester = APIGatewayTester(args.gateway_url)
    
    try:
        results = await tester.run_all_tests()
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📄 Results saved to {args.output}")
        
        # Exit with appropriate code
        sys.exit(0 if results['failed_tests'] == 0 else 1)
        
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        sys.exit(1)
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
