"""
Health Check Template for MantraPath Services
This template can be used to add comprehensive health checks to any service.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
import time
import logging
import asyncio
import httpx
import psutil
import os

logger = logging.getLogger(__name__)

def create_health_router(
    service_name: str,
    version: str = "1.0.0",
    dependencies: Optional[Dict[str, str]] = None,
    custom_checks: Optional[Dict[str, callable]] = None
) -> APIRouter:
    """
    Create a comprehensive health check router for a service.
    
    Args:
        service_name: Name of the service
        version: Service version
        dependencies: Dict of dependency_name -> health_url
        custom_checks: Dict of check_name -> check_function
    
    Returns:
        FastAPI router with health endpoints
    """
    
    router = APIRouter(prefix="/health", tags=["health"])
    dependencies = dependencies or {}
    custom_checks = custom_checks or {}
    
    @router.get("/")
    async def comprehensive_health_check() -> Dict[str, Any]:
        """Comprehensive health check with all components"""
        try:
            start_time = time.time()
            
            # Basic service info
            basic_info = {
                "service": service_name,
                "version": version,
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "uptime": time.time()
            }
            
            # System metrics
            system_metrics = await _get_system_metrics()
            
            # Check dependencies
            dependency_results = await _check_dependencies(dependencies)
            
            # Run custom checks
            custom_results = await _run_custom_checks(custom_checks)
            
            # Determine overall status
            overall_status = "healthy"
            if any(dep.get("status") == "unhealthy" for dep in dependency_results.values()):
                overall_status = "degraded"
            if any(check.get("status") == "error" for check in custom_results.values()):
                overall_status = "error"
            
            processing_time = time.time() - start_time
            
            return {
                **basic_info,
                "status": overall_status,
                "checks": {
                    "dependencies": dependency_results,
                    "custom_checks": custom_results,
                    "system_metrics": system_metrics,
                    "health_check_duration": f"{processing_time:.3f}s"
                }
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": service_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @router.get("/live")
    async def liveness_check() -> Dict[str, Any]:
        """Kubernetes liveness probe - simple check if service is running"""
        return {
            "status": "alive",
            "service": service_name,
            "timestamp": time.time()
        }
    
    @router.get("/ready")
    async def readiness_check() -> Dict[str, Any]:
        """Kubernetes readiness probe - check if service is ready to serve traffic"""
        try:
            # Check critical dependencies
            critical_deps = {k: v for k, v in dependencies.items() if v.get("critical", True)}
            if critical_deps:
                dependency_results = await _check_dependencies(critical_deps)
                unhealthy_deps = [k for k, v in dependency_results.items() if v.get("status") != "healthy"]
                
                if unhealthy_deps:
                    raise HTTPException(
                        status_code=503,
                        detail=f"Critical dependencies unhealthy: {', '.join(unhealthy_deps)}"
                    )
            
            return {
                "status": "ready",
                "service": service_name,
                "timestamp": time.time()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            raise HTTPException(status_code=503, detail=str(e))
    
    @router.get("/dependencies")
    async def check_dependencies_endpoint() -> Dict[str, Any]:
        """Check status of all service dependencies"""
        try:
            dependency_results = await _check_dependencies(dependencies)
            return {
                "service": service_name,
                "dependencies": dependency_results,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            return {
                "service": service_name,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    @router.get("/metrics")
    async def get_service_metrics() -> Dict[str, Any]:
        """Get service performance metrics"""
        try:
            system_metrics = await _get_system_metrics()
            return {
                "service": service_name,
                "version": version,
                "metrics": system_metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return {
                "service": service_name,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def _check_dependencies(deps: Dict[str, str]) -> Dict[str, Any]:
        """Check health of service dependencies"""
        results = {}
        
        async def check_single_dependency(name: str, config: Dict[str, Any]) -> Dict[str, Any]:
            try:
                url = config.get("url") if isinstance(config, dict) else config
                timeout = config.get("timeout", 5.0) if isinstance(config, dict) else 5.0
                
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        return {
                            "status": "healthy",
                            "url": url,
                            "response_time": response.elapsed.total_seconds(),
                            "last_check": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "url": url,
                            "status_code": response.status_code,
                            "last_check": datetime.now(timezone.utc).isoformat()
                        }
                        
            except Exception as e:
                return {
                    "status": "unreachable",
                    "url": url if 'url' in locals() else "unknown",
                    "error": str(e),
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
        
        # Check all dependencies concurrently
        if deps:
            tasks = [check_single_dependency(name, config) for name, config in deps.items()]
            dependency_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, (name, result) in enumerate(zip(deps.keys(), dependency_results)):
                if isinstance(result, Exception):
                    results[name] = {
                        "status": "error",
                        "error": str(result),
                        "last_check": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    results[name] = result
        
        return results
    
    async def _run_custom_checks(checks: Dict[str, callable]) -> Dict[str, Any]:
        """Run custom health checks"""
        results = {}
        
        for check_name, check_func in checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                
                results[check_name] = {
                    "status": "healthy" if result else "unhealthy",
                    "result": result,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Custom check '{check_name}' failed: {e}")
                results[check_name] = {
                    "status": "error",
                    "error": str(e),
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
        
        return results
    
    async def _get_system_metrics() -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # Get process info
            process = psutil.Process()
            
            # CPU and Memory
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # System info
            system_cpu = psutil.cpu_percent(interval=0.1)
            system_memory = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            
            return {
                "process": {
                    "pid": process.pid,
                    "cpu_percent": cpu_percent,
                    "memory_rss": memory_info.rss,
                    "memory_vms": memory_info.vms,
                    "memory_percent": memory_percent,
                    "num_threads": process.num_threads(),
                    "create_time": process.create_time()
                },
                "system": {
                    "cpu_percent": system_cpu,
                    "memory_total": system_memory.total,
                    "memory_available": system_memory.available,
                    "memory_percent": system_memory.percent,
                    "disk_total": disk_usage.total,
                    "disk_used": disk_usage.used,
                    "disk_percent": disk_usage.percent
                },
                "environment": {
                    "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
                    "platform": os.name,
                    "hostname": os.uname().nodename if hasattr(os, 'uname') else 'unknown'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    return router


# Example usage:
"""
from health_template import create_health_router

# Define service dependencies
dependencies = {
    "postgres": {
        "url": "http://postgres:5432/health",
        "critical": True,
        "timeout": 3.0
    },
    "redis": {
        "url": "http://redis:6379/ping",
        "critical": False,
        "timeout": 2.0
    },
    "models_service": {
        "url": "http://models-service:8080/health",
        "critical": True,
        "timeout": 5.0
    }
}

# Define custom health checks
def check_database_connection():
    # Your database connection check logic
    return True

async def check_ml_model_loaded():
    # Your ML model check logic
    return True

custom_checks = {
    "database_connection": check_database_connection,
    "ml_model_loaded": check_ml_model_loaded
}

# Create health router
health_router = create_health_router(
    service_name="my-service",
    version="1.0.0",
    dependencies=dependencies,
    custom_checks=custom_checks
)

# Add to FastAPI app
app.include_router(health_router)
"""





