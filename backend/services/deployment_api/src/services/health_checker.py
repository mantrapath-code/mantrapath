"""
Health Checker Service for monitoring backend services
"""

import asyncio
import httpx
from typing import Dict, Any, List
from datetime import datetime, timezone


class HealthCheckerService:
    """Service for checking health of all backend services"""
    
    def __init__(self):
        self.services = {
            "api_gateway": {
                "url": "http://localhost:8000/health",
                "name": "API Gateway",
                "port": 8000,
                "critical": True
            },
            "voice_service": {
                "url": "http://localhost:8011/health",
                "name": "Voice Service",
                "port": 8011,
                "critical": True
            },
            "models_service": {
                "url": "http://localhost:8085/health",
                "name": "Models Service",
                "port": 8085,
                "critical": True
            },
            "community_service": {
                "url": "http://localhost:8012/health",
                "name": "Community Service",
                "port": 8012,
                "critical": False
            },
            "ml_service": {
                "url": "http://localhost:8013/health",
                "name": "ML Service",
                "port": 8013,
                "critical": False
            }
        }
        self.health_cache = {}
        self.cache_ttl = 30  # 30 seconds
    
    async def initialize(self):
        """Initialize the service"""
        pass
    
    async def cleanup(self):
        """Cleanup resources"""
        pass
    
    async def get_overall_health(self) -> Dict[str, Any]:
        """Get overall health status of all services"""
        try:
            health_results = await self._check_all_services()
            
            # Calculate overall status
            total_services = len(health_results)
            healthy_services = sum(1 for h in health_results.values() if h["status"] == "healthy")
            critical_healthy = sum(1 for h in health_results.values() 
                                if h["status"] == "healthy" and h["critical"])
            critical_total = sum(1 for h in health_results.values() if h["critical"])
            
            overall_status = "healthy"
            if critical_healthy < critical_total:
                overall_status = "critical"
            elif healthy_services < total_services:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "summary": {
                    "total_services": total_services,
                    "healthy_services": healthy_services,
                    "unhealthy_services": total_services - healthy_services,
                    "critical_services_healthy": critical_healthy,
                    "critical_services_total": critical_total
                },
                "services": health_results,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to get overall health: {str(e)}"}
    
    async def get_all_services_health(self) -> Dict[str, Any]:
        """Get health status of all individual services"""
        try:
            health_results = await self._check_all_services()
            return {
                "services": health_results,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to get services health: {str(e)}"}
    
    async def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health status of a specific service"""
        try:
            if service_name not in self.services:
                return {
                    "error": f"Service '{service_name}' not found",
                    "available_services": list(self.services.keys())
                }
            
            health_result = await self._check_service(service_name)
            return health_result
        except Exception as e:
            return {"error": f"Failed to get {service_name} health: {str(e)}"}
    
    async def _check_all_services(self) -> Dict[str, Any]:
        """Check health of all services concurrently"""
        try:
            tasks = []
            for service_name in self.services.keys():
                tasks.append(self._check_service(service_name))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            health_results = {}
            for i, (service_name, result) in enumerate(zip(self.services.keys(), results)):
                if isinstance(result, Exception):
                    health_results[service_name] = {
                        "status": "error",
                        "error": str(result),
                        "critical": self.services[service_name]["critical"]
                    }
                else:
                    health_results[service_name] = result
            
            return health_results
        except Exception as e:
            return {"error": f"Failed to check all services: {str(e)}"}
    
    async def _check_service(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        try:
            service = self.services[service_name]
            
            # Check cache first
            current_time = datetime.now(timezone.utc).timestamp()
            if (service_name in self.health_cache and 
                current_time - self.health_cache[service_name]["timestamp"] < self.cache_ttl):
                return self.health_cache[service_name]["data"]
            
            # Perform health check
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    response = await client.get(service["url"])
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        status = "healthy"
                    else:
                        health_data = {"status_code": response.status_code}
                        status = "unhealthy"
                        
                except httpx.RequestError as e:
                    health_data = {"error": str(e)}
                    status = "unreachable"
                except Exception as e:
                    health_data = {"error": str(e)}
                    status = "error"
            
            result = {
                "name": service["name"],
                "url": service["url"],
                "port": service["port"],
                "status": status,
                "critical": service["critical"],
                "data": health_data,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
            
            # Cache the result
            self.health_cache[service_name] = {
                "data": result,
                "timestamp": current_time
            }
            
            return result
            
        except Exception as e:
            return {
                "name": service_name,
                "status": "error",
                "error": str(e),
                "critical": self.services.get(service_name, {}).get("critical", False),
                "last_check": datetime.now(timezone.utc).isoformat()
            }
    
    async def get_critical_services_status(self) -> Dict[str, Any]:
        """Get status of critical services only"""
        try:
            critical_services = {k: v for k, v in self.services.items() if v["critical"]}
            
            health_results = {}
            for service_name in critical_services.keys():
                health_results[service_name] = await self._check_service(service_name)
            
            # Determine critical status
            critical_healthy = sum(1 for h in health_results.values() if h["status"] == "healthy")
            critical_total = len(critical_services)
            
            critical_status = "healthy" if critical_healthy == critical_total else "critical"
            
            return {
                "status": critical_status,
                "critical_services": health_results,
                "summary": {
                    "total_critical": critical_total,
                    "healthy_critical": critical_healthy,
                    "unhealthy_critical": critical_total - critical_healthy
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to get critical services status: {str(e)}"}
    
    async def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific service"""
        try:
            if service_name not in self.services:
                return {"error": f"Service '{service_name}' not found"}
            
            # This would typically query actual metrics from the service
            # For now, return mock metrics
            mock_metrics = {
                "response_time": {
                    "current": "45ms",
                    "average": "52ms",
                    "p95": "120ms",
                    "p99": "200ms"
                },
                "throughput": {
                    "requests_per_second": 150,
                    "total_requests": 1250000
                },
                "errors": {
                    "error_rate": "0.5%",
                    "total_errors": 6250
                },
                "resources": {
                    "cpu_usage": "45%",
                    "memory_usage": "2.1 GB",
                    "disk_usage": "15%"
                }
            }
            
            return {
                "service": service_name,
                "metrics": mock_metrics,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to get metrics for {service_name}: {str(e)}"}

