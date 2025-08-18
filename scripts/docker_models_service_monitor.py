#!/usr/bin/env python3
"""
MantraPath Models Service - Docker Integration & Monitoring Script
================================================================

This script provides comprehensive testing and monitoring for the Models Service
running in Docker containers, with specific focus on Docker environment integration.

Features:
1. Docker container health monitoring
2. Service endpoint testing with Docker port mapping
3. Model functionality validation
4. Performance monitoring
5. Container resource usage analysis
6. Log analysis and error detection
7. Automatic issue detection and reporting

Usage:
    python docker_models_service_monitor.py                      # Basic monitoring
    python docker_models_service_monitor.py --full-test          # Complete testing
    python docker_models_service_monitor.py --monitor            # Continuous monitoring
    python docker_models_service_monitor.py --analyze-logs       # Log analysis
    python docker_models_service_monitor.py --resource-usage     # Resource monitoring
"""

import asyncio
import aiohttp
import docker
import json
import time
import logging
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import argparse
from datetime import datetime, timedelta
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'models_service_docker_monitor_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class DockerModelsServiceMonitor:
    """Comprehensive Docker-based Models Service Monitor"""
    
    def __init__(self):
        self.docker_client = None
        self.container_name = "backend-models-service-1"
        self.service_port = None
        self.service_url = None
        self.container_info = {}
        self.monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "container_status": {},
            "service_health": {},
            "endpoint_tests": {},
            "resource_usage": {},
            "log_analysis": {},
            "issues_detected": [],
            "recommendations": []
        }
    
    def initialize_docker_client(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            logger.info("✅ Docker client initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Docker client: {e}")
            return False
    
    def find_models_service_container(self) -> bool:
        """Find the models service container"""
        try:
            containers = self.docker_client.containers.list()
            
            for container in containers:
                if self.container_name in container.name or "models-service" in container.name:
                    self.container_info = {
                        "id": container.id,
                        "name": container.name,
                        "status": container.status,
                        "image": container.image.tags[0] if container.image.tags else "unknown",
                        "created": container.attrs['Created'],
                        "ports": container.ports
                    }
                    
                    # Extract service port
                    if '8080/tcp' in container.ports and container.ports['8080/tcp']:
                        self.service_port = container.ports['8080/tcp'][0]['HostPort']
                        self.service_url = f"http://localhost:{self.service_port}"
                    
                    self.container_name = container.name
                    logger.info(f"✅ Found models service container: {self.container_name}")
                    logger.info(f"   Port mapping: {self.service_port}")
                    logger.info(f"   Service URL: {self.service_url}")
                    return True
            
            logger.error("❌ Models service container not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error finding container: {e}")
            return False
    
    def get_container_stats(self) -> Dict:
        """Get container resource usage statistics"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            stats = container.stats(stream=False)
            
            # Calculate CPU percentage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_count = len(stats['cpu_stats']['cpu_usage']['percpu_usage'])
            cpu_percent = (cpu_delta / system_cpu_delta) * cpu_count * 100.0 if system_cpu_delta > 0 else 0.0
            
            # Calculate memory usage
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            
            # Network I/O
            networks = stats.get('networks', {})
            total_rx_bytes = sum(net['rx_bytes'] for net in networks.values())
            total_tx_bytes = sum(net['tx_bytes'] for net in networks.values())
            
            return {
                "cpu_percent": round(cpu_percent, 2),
                "memory_usage_mb": round(memory_usage / (1024 * 1024), 2),
                "memory_limit_mb": round(memory_limit / (1024 * 1024), 2),
                "memory_percent": round(memory_percent, 2),
                "network_rx_mb": round(total_rx_bytes / (1024 * 1024), 2),
                "network_tx_mb": round(total_tx_bytes / (1024 * 1024), 2),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting container stats: {e}")
            return {}
    
    def analyze_container_logs(self, lines: int = 100) -> Dict:
        """Analyze container logs for issues"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            logs = container.logs(tail=lines).decode('utf-8')
            
            analysis = {
                "total_lines": len(logs.split('\n')),
                "errors": [],
                "warnings": [],
                "info_messages": [],
                "performance_metrics": {},
                "recent_activity": []
            }
            
            # Parse logs
            for line in logs.split('\n'):
                if not line.strip():
                    continue
                
                # Detect log levels
                if 'ERROR' in line.upper() or 'Exception' in line:
                    analysis["errors"].append(line.strip())
                elif 'WARNING' in line.upper() or 'WARN' in line.upper():
                    analysis["warnings"].append(line.strip())
                elif 'INFO' in line:
                    analysis["info_messages"].append(line.strip())
                
                # Detect HTTP requests
                if ' - "' in line and 'HTTP/1.1' in line:
                    analysis["recent_activity"].append(line.strip())
            
            # Analyze patterns
            http_requests = len(analysis["recent_activity"])
            error_count = len(analysis["errors"])
            warning_count = len(analysis["warnings"])
            
            analysis["summary"] = {
                "http_requests": http_requests,
                "error_count": error_count,
                "warning_count": warning_count,
                "health_status": "healthy" if error_count == 0 else "issues_detected"
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {}
    
    async def test_service_endpoints(self) -> Dict:
        """Test all service endpoints"""
        if not self.service_url:
            return {"error": "Service URL not available"}
        
        logger.info("🧪 Testing service endpoints...")
        
        test_results = {
            "health": await self._test_health_endpoint(),
            "status": await self._test_status_endpoint(),
            "models_available": await self._test_models_available(),
            "models_loaded": await self._test_models_loaded(),
            "stt_languages": await self._test_stt_languages(),
            "tts_languages": await self._test_tts_languages(),
            "tts_synthesis": await self._test_tts_synthesis(),
            "nlp_translation": await self._test_nlp_translation()
        }
        
        # Calculate success rate
        successful_tests = sum(1 for result in test_results.values() if result.get("success", False))
        total_tests = len(test_results)
        success_rate = (successful_tests / total_tests) * 100
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "overall_status": "pass" if success_rate >= 70 else "fail"
        }
        
        return test_results
    
    async def _test_health_endpoint(self) -> Dict:
        """Test health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                async with session.get(f"{self.service_url}/health") as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "status_code": response.status,
                            "response_time": duration,
                            "data": data
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": response.status,
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _test_status_endpoint(self) -> Dict:
        """Test status endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "status_code": response.status,
                            "data": data
                        }
                    else:
                        return {
                            "success": False,
                            "status_code": response.status
                        }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_models_available(self) -> Dict:
        """Test models available endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/models/available") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "status_code": response.status,
                            "models_count": len(data) if isinstance(data, (list, dict)) else 0
                        }
                    else:
                        return {"success": False, "status_code": response.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_models_loaded(self) -> Dict:
        """Test models loaded endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/models/loaded") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "status_code": response.status,
                            "loaded_models": data
                        }
                    else:
                        return {"success": False, "status_code": response.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_stt_languages(self) -> Dict:
        """Test STT languages endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/api/v1/stt/languages") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "status_code": response.status,
                            "languages_count": len(data.get("supported_languages", {}))
                        }
                    else:
                        return {"success": False, "status_code": response.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_tts_languages(self) -> Dict:
        """Test TTS languages endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.service_url}/api/v1/tts/languages") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "status_code": response.status,
                            "languages_count": len(data.get("supported_languages", {}))
                        }
                    else:
                        return {"success": False, "status_code": response.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_tts_synthesis(self) -> Dict:
        """Test TTS synthesis endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"text": "Hello test", "language": "en"}
                async with session.post(f"{self.service_url}/api/v1/tts/synthesize", 
                                      json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": data.get("success", False),
                            "status_code": response.status,
                            "model_used": data.get("model_used"),
                            "error": data.get("error")
                        }
                    else:
                        return {"success": False, "status_code": response.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_nlp_translation(self) -> Dict:
        """Test NLP translation endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "text": "Hello",
                    "source_lang": "en",
                    "target_lang": "hi"
                }
                async with session.post(f"{self.service_url}/api/v1/nlp/translate",
                                      json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": data.get("success", False),
                            "status_code": response.status,
                            "has_translation": bool(data.get("translated_text"))
                        }
                    else:
                        return {"success": False, "status_code": response.status}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def detect_issues(self) -> List[Dict]:
        """Detect issues based on monitoring data"""
        issues = []
        
        # Container health issues
        if self.container_info.get("status") != "running":
            issues.append({
                "type": "container_health",
                "severity": "high",
                "message": f"Container not running: {self.container_info.get('status')}"
            })
        
        # Resource usage issues
        resource_stats = self.monitoring_results.get("resource_usage", {})
        if resource_stats.get("cpu_percent", 0) > 90:
            issues.append({
                "type": "resource_usage",
                "severity": "medium",
                "message": f"High CPU usage: {resource_stats.get('cpu_percent')}%"
            })
        
        if resource_stats.get("memory_percent", 0) > 90:
            issues.append({
                "type": "resource_usage",
                "severity": "medium",
                "message": f"High memory usage: {resource_stats.get('memory_percent')}%"
            })
        
        # Service health issues
        endpoint_tests = self.monitoring_results.get("endpoint_tests", {})
        success_rate = endpoint_tests.get("summary", {}).get("success_rate", 0)
        
        if success_rate < 50:
            issues.append({
                "type": "service_health",
                "severity": "high",
                "message": f"Low endpoint success rate: {success_rate}%"
            })
        elif success_rate < 80:
            issues.append({
                "type": "service_health", 
                "severity": "medium",
                "message": f"Moderate endpoint issues: {success_rate}% success rate"
            })
        
        # Log analysis issues
        log_analysis = self.monitoring_results.get("log_analysis", {})
        error_count = log_analysis.get("summary", {}).get("error_count", 0)
        
        if error_count > 5:
            issues.append({
                "type": "error_logs",
                "severity": "medium",
                "message": f"Multiple errors detected in logs: {error_count} errors"
            })
        
        return issues
    
    def generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate recommendations based on detected issues"""
        recommendations = []
        
        for issue in issues:
            if issue["type"] == "container_health":
                recommendations.append("Restart the container: docker restart " + self.container_name)
            elif issue["type"] == "resource_usage":
                if "CPU" in issue["message"]:
                    recommendations.append("Monitor CPU usage and consider scaling or optimization")
                if "memory" in issue["message"]:
                    recommendations.append("Increase container memory limits or optimize memory usage")
            elif issue["type"] == "service_health":
                recommendations.append("Check service logs and endpoint implementations")
                recommendations.append("Verify model loading and configuration")
            elif issue["type"] == "error_logs":
                recommendations.append("Review error logs for specific issues")
                recommendations.append("Check model dependencies and system requirements")
        
        if not issues:
            recommendations.append("Service is running well - continue monitoring")
        
        return recommendations
    
    async def run_comprehensive_monitoring(self) -> Dict:
        """Run comprehensive monitoring and analysis"""
        logger.info("🔍 Starting comprehensive Docker Models Service monitoring...")
        
        # Initialize Docker client
        if not self.initialize_docker_client():
            return {"error": "Failed to initialize Docker client"}
        
        # Find container
        if not self.find_models_service_container():
            return {"error": "Models service container not found"}
        
        # Update monitoring results
        self.monitoring_results["container_status"] = self.container_info
        self.monitoring_results["resource_usage"] = self.get_container_stats()
        self.monitoring_results["log_analysis"] = self.analyze_container_logs()
        self.monitoring_results["endpoint_tests"] = await self.test_service_endpoints()
        
        # Detect issues and generate recommendations
        issues = self.detect_issues()
        recommendations = self.generate_recommendations(issues)
        
        self.monitoring_results["issues_detected"] = issues
        self.monitoring_results["recommendations"] = recommendations
        
        return self.monitoring_results
    
    def print_monitoring_report(self, results: Dict):
        """Print comprehensive monitoring report"""
        print("\n" + "=" * 80)
        print("🐳 DOCKER MODELS SERVICE MONITORING REPORT")
        print("=" * 80)
        
        # Container Status
        container_status = results.get("container_status", {})
        print(f"\n📦 CONTAINER STATUS:")
        print(f"   Name: {container_status.get('name', 'Unknown')}")
        print(f"   Status: {container_status.get('status', 'Unknown')}")
        print(f"   Image: {container_status.get('image', 'Unknown')}")
        print(f"   Port Mapping: {container_status.get('ports', {})}")
        
        # Resource Usage
        resource_usage = results.get("resource_usage", {})
        if resource_usage:
            print(f"\n⚡ RESOURCE USAGE:")
            print(f"   CPU: {resource_usage.get('cpu_percent', 0)}%")
            print(f"   Memory: {resource_usage.get('memory_usage_mb', 0):.1f}MB / {resource_usage.get('memory_limit_mb', 0):.1f}MB ({resource_usage.get('memory_percent', 0):.1f}%)")
            print(f"   Network RX: {resource_usage.get('network_rx_mb', 0):.2f}MB")
            print(f"   Network TX: {resource_usage.get('network_tx_mb', 0):.2f}MB")
        
        # Endpoint Tests
        endpoint_tests = results.get("endpoint_tests", {})
        if "summary" in endpoint_tests:
            summary = endpoint_tests["summary"]
            print(f"\n🧪 ENDPOINT TESTS:")
            print(f"   Success Rate: {summary.get('success_rate', 0):.1f}%")
            print(f"   Passed: {summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)}")
            print(f"   Overall Status: {summary.get('overall_status', 'unknown').upper()}")
        
        # Log Analysis
        log_analysis = results.get("log_analysis", {})
        if "summary" in log_analysis:
            log_summary = log_analysis["summary"]
            print(f"\n📋 LOG ANALYSIS:")
            print(f"   HTTP Requests: {log_summary.get('http_requests', 0)}")
            print(f"   Errors: {log_summary.get('error_count', 0)}")
            print(f"   Warnings: {log_summary.get('warning_count', 0)}")
            print(f"   Health Status: {log_summary.get('health_status', 'unknown').upper()}")
        
        # Issues
        issues = results.get("issues_detected", [])
        print(f"\n🚨 ISSUES DETECTED: {len(issues)}")
        for issue in issues:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            icon = severity_icon.get(issue.get("severity"), "⚪")
            print(f"   {icon} [{issue.get('type')}] {issue.get('message')}")
        
        # Recommendations
        recommendations = results.get("recommendations", [])
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        print("\n" + "=" * 80)

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Docker Models Service Monitor")
    parser.add_argument("--full-test", action="store_true", help="Run full comprehensive test")
    parser.add_argument("--monitor", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--analyze-logs", action="store_true", help="Focus on log analysis")
    parser.add_argument("--resource-usage", action="store_true", help="Focus on resource monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    monitor = DockerModelsServiceMonitor()
    
    try:
        if args.monitor:
            logger.info(f"🔄 Starting continuous monitoring (interval: {args.interval}s)")
            while True:
                results = await monitor.run_comprehensive_monitoring()
                monitor.print_monitoring_report(results)
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(results, f, indent=2, default=str)
                
                await asyncio.sleep(args.interval)
        else:
            # Single run
            results = await monitor.run_comprehensive_monitoring()
            monitor.print_monitoring_report(results)
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                logger.info(f"📄 Results saved to: {args.output}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Monitoring stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Monitoring failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
