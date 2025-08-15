"""
MantraPath API Gateway - Main Application
A modular, scalable API Gateway with service discovery, load balancing, and health monitoring.
"""
import uuid
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.config import gateway_config, service_config
from src.core.models import ProxyRequest, HTTPMethod
from src.registry import ServiceRegistry
from src.routing import RequestRouter, LoadBalancerFactory, RequestProxy
from src.middleware import RateLimiter, get_client_identifier, CircuitBreaker
from src.health import HealthChecker
from src.voice.endpoints import voice_api

# Configure logging
logging.basicConfig(
    level=getattr(logging, gateway_config.log_level),
    format=gateway_config.log_format
)
logger = logging.getLogger(__name__)

# Global components
service_registry = ServiceRegistry()
request_router = RequestRouter()
load_balancer = LoadBalancerFactory.create_load_balancer(gateway_config.load_balancing_strategy)
request_proxy = RequestProxy()
rate_limiter = RateLimiter()
circuit_breaker = CircuitBreaker()
health_checker = HealthChecker(service_registry, circuit_breaker)

# Security
security = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting MantraPath API Gateway...")
    await service_registry.start()
    logger.info("API Gateway started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway...")
    await service_registry.stop()
    logger.info("API Gateway shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="MantraPath API Gateway",
    description="Intelligent API Gateway for MantraPath platform",
    version="1.0.0",
    docs_url="/docs" if gateway_config.debug else None,
    redoc_url="/redoc" if gateway_config.debug else None,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=gateway_config.cors_origins,
    allow_credentials=gateway_config.cors_credentials,
    allow_methods=gateway_config.cors_methods,
    allow_headers=gateway_config.cors_headers,
)

# Include voice API routes
app.include_router(voice_api)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return await health_checker.gateway_health()

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service information"""
    return await health_checker.detailed_health()

@app.get("/health/ready")
async def readiness_check():
    """Readiness check for Kubernetes"""
    return await health_checker.readiness_check()

@app.get("/health/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return await health_checker.liveness_check()

@app.get("/health/services/{service_name}")
async def service_health_check(service_name: str):
    """Health check for specific service"""
    return await health_checker.service_health(service_name)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # In a real implementation, this would return Prometheus format metrics
    all_services = service_registry.get_all_services()
    circuit_states = circuit_breaker.get_all_circuits()
    
    metrics_data = {
        "gateway_version": "1.0.0",
        "services_total": sum(len(instances) for instances in all_services.values()),
        "services_healthy": sum(
            len([i for i in instances if i.status.value == "healthy"])
            for instances in all_services.values()
        ),
        "circuit_breakers": {
            name: state.state for name, state in circuit_states.items()
        }
    }
    
    return metrics_data

# Main proxy endpoint
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def proxy_request(
    request: Request,
    path: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Main request proxying endpoint"""
    # Generate request ID for tracing
    request_id = str(uuid.uuid4())
    
    try:
        # Extract user info from JWT (simplified)
        user_id = None
        if credentials:
            # In a real implementation, decode and validate JWT
            user_id = "authenticated_user"  # Placeholder
        
        # Rate limiting
        client_id = get_client_identifier(dict(request.headers), user_id)
        if not rate_limiter.is_allowed(client_id):
            rate_info = rate_limiter.get_rate_limit_info(client_id)
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "limit": rate_info["limit"],
                    "reset_time": rate_info["reset_time"].isoformat()
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(int(rate_info["reset_time"].timestamp())),
                    "Retry-After": "60"
                }
            )
        
        # Find route
        full_path = f"/{path}" if not path.startswith('/') else path
        route = request_router.find_route(full_path, request.method)
        if not route:
            return JSONResponse(
                status_code=404,
                content={"error": "Route not found", "path": full_path}
            )
        
        # Get healthy service instances
        healthy_services = service_registry.get_healthy_services(route.service_name)
        if not healthy_services:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service Unavailable",
                    "service": route.service_name,
                    "message": "No healthy instances available"
                }
            )
        
        # Circuit breaker check
        if not circuit_breaker.is_call_allowed(route.service_name):
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service Unavailable",
                    "service": route.service_name,
                    "message": "Circuit breaker is open"
                }
            )
        
        # Load balance and select service instance
        selected_service = load_balancer.select_instance(healthy_services)
        if not selected_service:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service Unavailable",
                    "service": route.service_name,
                    "message": "No service instance selected"
                }
            )
        
        # Prepare proxy request
        body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
        
        proxy_req = ProxyRequest(
            method=request.method,
            path=f"/{path}",
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            body=body,
            user_id=user_id,
            request_id=request_id
        )
        
        # Proxy the request
        proxy_response = await request_proxy.proxy_request(
            proxy_req,
            selected_service,
            timeout=route.timeout
        )
        
        # Record circuit breaker state
        if proxy_response.status_code >= 500:
            circuit_breaker.record_failure(route.service_name)
        else:
            circuit_breaker.record_success(route.service_name)
        
        # Return response
        return Response(
            content=proxy_response.body,
            status_code=proxy_response.status_code,
            headers=proxy_response.headers,
            media_type=proxy_response.headers.get("content-type")
        )
        
    except Exception as e:
        logger.error(f"Proxy error for request {request_id}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "request_id": request_id,
                "message": "Gateway processing error"
            }
        )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=gateway_config.host,
        port=gateway_config.port,
        reload=gateway_config.debug,
        log_level=gateway_config.log_level.lower()
    )
