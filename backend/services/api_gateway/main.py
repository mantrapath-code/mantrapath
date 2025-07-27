"""
API Gateway for MantraPath - Central routing and authentication
"""

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
import time
import asyncio
from typing import Dict, Any, Optional
import redis
import json
from datetime import datetime

app = FastAPI(
    title="MantraPath API Gateway",
    description="Central gateway for MantraPath microservices",
    version="1.0.0"
)

# Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

# Redis client for caching and rate limiting
redis_client = redis.from_url(REDIS_URL)

# Service URLs mapping
SERVICES = {
    "auth": "http://localhost:8001",
    "profile": "http://localhost:8002", 
    "mood": "http://localhost:8003",
    "chatbot": "http://localhost:8004",
    "content": "http://localhost:8005",
    "community": "http://localhost:8006",
    "notification": "http://localhost:8007",
    "media": "http://localhost:8009"
}

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

# Rate limiting
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, key: str, limit: int = 100, window: int = 60) -> bool:
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, window)
        return current <= limit

rate_limiter = RateLimiter(redis_client)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Global rate limiting"""
    client_ip = request.client.host
    endpoint = request.url.path
    
    # Different limits for different endpoints
    if endpoint.startswith("/auth/"):
        limit = 30  # Stricter for auth endpoints
    else:
        limit = 100
    
    rate_key = f"rate_limit:{client_ip}:{endpoint}"
    
    if not rate_limiter.is_allowed(rate_key, limit, 60):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "retry_after": 60}
        )
    
    response = await call_next(request)
    return response

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Request/Response logging"""
    start_time = time.time()
    
    # Log request
    request_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    response_log = {
        **request_log,
        "status_code": response.status_code,
        "process_time": process_time
    }
    
    # Store in Redis for monitoring (with expiration)
    log_key = f"request_log:{int(time.time())}"
    redis_client.setex(log_key, 3600, json.dumps(response_log))
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Authentication utilities
async def verify_token_with_auth_service(token: str) -> Optional[Dict[str, Any]]:
    """Verify token with auth service"""
    try:
        # Check cache first
        cached_user = redis_client.get(f"user_cache:{token[:20]}")
        if cached_user:
            return json.loads(cached_user)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/validate",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                # Cache for 5 minutes
                redis_client.setex(
                    f"user_cache:{token[:20]}", 
                    300, 
                    json.dumps(user_data)
                )
                return user_data
    except Exception as e:
        print(f"Token verification failed: {e}")
    
    return None

def get_service_url(path: str) -> str:
    """Determine which service should handle the request"""
    # Auth service routes
    if path.startswith("/auth/") or path.startswith("/api/auth/"):
        return SERVICES["auth"]
    
    # Profile service routes
    if path.startswith("/api/profiles/") or path.startswith("/api/preferences/"):
        return SERVICES["profile"]
    
    # Mood service routes
    if any(path.startswith(prefix) for prefix in [
        "/api/v1/mood/", "/api/v1/journal/", "/api/v1/habits/", 
        "/api/v1/insights/", "/api/v1/analytics/"
    ]):
        return SERVICES["mood"]
    
    # Chatbot service routes
    if path.startswith("/api/chatbot/"):
        return SERVICES["chatbot"]
    
    # Content service routes
    if any(path.startswith(prefix) for prefix in [
        "/content/", "/affirmations/", "/bookmark/", "/challenge/"
    ]):
        return SERVICES["content"]
    
    # Community service routes
    if path.startswith("/forums/") or path.startswith("/users/"):
        return SERVICES["community"]
    
    # Notification service routes
    if path.startswith("/notify/"):
        return SERVICES["notification"]
    
    # Media service routes
    if path.startswith("/api/v1/media/"):
        return SERVICES["media"]
    
    # Default to auth service for unknown routes
    return SERVICES["auth"]

async def proxy_request(request: Request, service_url: str) -> JSONResponse:
    """Proxy request to appropriate microservice"""
    try:
        # Prepare headers
        headers = dict(request.headers)
        # Remove host header to avoid conflicts
        headers.pop("host", None)
        
        # Get request body if present
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
        
        # Make request to microservice
        timeout = httpx.Timeout(30.0)  # 30 second timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(
                method=request.method,
                url=f"{service_url}{request.url.path}",
                headers=headers,
                params=request.query_params,
                content=body
            )
            
            # Return response
            return JSONResponse(
                status_code=response.status_code,
                content=response.json() if response.content else None,
                headers=dict(response.headers)
            )
    
    except httpx.TimeoutException:
        return JSONResponse(
            status_code=504,
            content={"error": "Service timeout", "service": service_url}
        )
    except httpx.ConnectError:
        return JSONResponse(
            status_code=503,
            content={"error": "Service unavailable", "service": service_url}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "Gateway error", "detail": str(e)}
        )

# Health check endpoints
@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "service": "api_gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health/services")
async def services_health():
    """Check health of all services"""
    health_status = {}
    
    async def check_service(name: str, url: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                health_status[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": url,
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            health_status[name] = {
                "status": "unhealthy",
                "url": url,
                "error": str(e)
            }
    
    # Check all services concurrently
    tasks = [check_service(name, url) for name, url in SERVICES.items()]
    await asyncio.gather(*tasks)
    
    overall_status = "healthy" if all(
        service["status"] == "healthy" for service in health_status.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "services": health_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Get gateway metrics"""
    # Get recent request logs
    log_keys = redis_client.keys("request_log:*")
    recent_logs = []
    
    for key in log_keys[-100:]:  # Last 100 requests
        log_data = redis_client.get(key)
        if log_data:
            recent_logs.append(json.loads(log_data))
    
    # Calculate metrics
    total_requests = len(recent_logs)
    avg_response_time = sum(log.get("process_time", 0) for log in recent_logs) / max(total_requests, 1)
    
    status_codes = {}
    for log in recent_logs:
        code = log.get("status_code", 0)
        status_codes[code] = status_codes.get(code, 0) + 1
    
    return {
        "total_requests": total_requests,
        "avg_response_time": avg_response_time,
        "status_codes": status_codes,
        "timestamp": datetime.utcnow().isoformat()
    }

# Main routing handler
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_request(request: Request, path: str):
    """Route requests to appropriate microservice"""
    
    # Handle OPTIONS requests for CORS
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    # Get target service
    service_url = get_service_url(f"/{path}")
    
    # Proxy the request
    return await proxy_request(request, service_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)