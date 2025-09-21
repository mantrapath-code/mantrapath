"""
Health Check Module - Monitors gateway and service health
"""
from typing import Dict
from datetime import datetime
from src.core.models import ServiceInstance, ServiceStatus
from src.registry.service_registry import ServiceRegistry
from src.middleware.circuit_breaker import CircuitBreaker

class HealthChecker:
    """Provides health check endpoints and monitoring"""
    
    def __init__(self, registry: ServiceRegistry, circuit_breaker: CircuitBreaker):
        self.registry = registry
        self.circuit_breaker = circuit_breaker
    
    async def gateway_health(self) -> Dict[str, any]:
        """Get overall gateway health status"""
        start_time = datetime.now()
        
        # Get all services and their health
        all_services = self.registry.get_all_services()
        total_services = sum(len(instances) for instances in all_services.values())
        healthy_services = sum(
            len([i for i in instances if i.status == ServiceStatus.HEALTHY])
            for instances in all_services.values()
        )
        
        # Calculate health percentage
        health_percentage = (healthy_services / total_services * 100) if total_services > 0 else 100
        
        # Determine overall status
        if health_percentage >= 80:
            status = "healthy"
        elif health_percentage >= 50:
            status = "degraded"
        else:
            status = "unhealthy"
        
        response_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "uptime": self._get_uptime(),
            "services": {
                "total": total_services,
                "healthy": healthy_services,
                "health_percentage": round(health_percentage, 2)
            },
            "response_time": round(response_time * 1000, 2)  # in milliseconds
        }
    
    async def detailed_health(self) -> Dict[str, any]:
        """Get detailed health information including all services"""
        gateway_health = await self.gateway_health()
        
        # Get detailed service information
        all_services = self.registry.get_all_services()
        service_details = {}
        
        for service_name, instances in all_services.items():
            circuit_state = self.circuit_breaker.get_circuit_state(service_name)
            
            service_details[service_name] = {
                "instances": [
                    {
                        "id": instance.id,
                        "url": instance.url,
                        "status": instance.status.value,
                        "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None,
                        "failure_count": instance.failure_count,
                        "weight": instance.weight
                    }
                    for instance in instances
                ],
                "circuit_breaker": {
                    "state": circuit_state.state,
                    "failure_count": circuit_state.failure_count,
                    "last_failure": circuit_state.last_failure_time.isoformat() if circuit_state.last_failure_time else None
                }
            }
        
        return {
            **gateway_health,
            "services_detail": service_details
        }
    
    async def service_health(self, service_name: str) -> Dict[str, any]:
        """Get health information for a specific service"""
        services = self.registry.get_all_services()
        
        if service_name not in services:
            return {
                "error": "Service not found",
                "service_name": service_name,
                "timestamp": datetime.now().isoformat()
            }
        
        instances = services[service_name]
        healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]
        circuit_state = self.circuit_breaker.get_circuit_state(service_name)
        
        return {
            "service_name": service_name,
            "status": "healthy" if healthy_instances else "unhealthy",
            "instances": {
                "total": len(instances),
                "healthy": len(healthy_instances),
                "unhealthy": len(instances) - len(healthy_instances)
            },
            "circuit_breaker": {
                "state": circuit_state.state,
                "failure_count": circuit_state.failure_count
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_uptime(self) -> str:
        """Get gateway uptime (placeholder implementation)"""
        # In a real implementation, this would track actual uptime
        return "0d 0h 0m 0s"
    
    async def readiness_check(self) -> Dict[str, any]:
        """Check if gateway is ready to accept traffic"""
        # Check if essential services are available
        essential_services = ["auth"]  # Add other essential services
        
        all_services = self.registry.get_all_services()
        ready = True
        
        for service_name in essential_services:
            if service_name not in all_services:
                ready = False
                break
            
            healthy_instances = [
                i for i in all_services[service_name]
                if i.status == ServiceStatus.HEALTHY
            ]
            
            if not healthy_instances:
                ready = False
                break
        
        return {
            "ready": ready,
            "timestamp": datetime.now().isoformat(),
            "essential_services": essential_services
        }
    
    async def liveness_check(self) -> Dict[str, any]:
        """Check if gateway is alive (basic health check)"""
        return {
            "alive": True,
            "timestamp": datetime.now().isoformat(),
            "pid": "unknown"  # In real implementation, use os.getpid()
        }
