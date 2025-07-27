"""
FastAPI API Gateway for MantraPath
Handles routing, authentication, rate limiting, and cross-service communication
"""

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import httpx
import redis.asyncio as redis
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from contextlib import asynccontextmanager
import os
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs from environment
SERVICE_URLS = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth_service:8001"),
    "profile": os.getenv("PROFILE_SERVICE_URL", "http://profile_service:8002"),
    "mood": os.getenv("MOOD_SERVICE_URL", "http://mood_service:8003"),
    "chatbot": os.getenv("CHATBOT_SERVICE_URL", "http://chatbot_service:8004"),
    "content": os.getenv("CONTENT_SERVICE_URL", "http://content_service:8005"),
    "community": os.getenv("COMMUNITY_SERVICE_URL", "http://community_service:8006"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification_service:8007"),
    "media": os.getenv("MEDIA_SERVICE_URL", "http://media_service:8009"),
    "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://analytics_service:8010"),
}

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit"""
        current = await self.redis.get(key)
        if current is None:
            await self.redis.setex(key, window, 1)
            return True
        
        if int(current) >= limit:
            return False
        
        await self.redis.incr(key)
        return True

async def get_redis():
    """Get Redis connection"""
    return redis.from_url(REDIS_URL, decode_responses=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    app.state.redis = await get_redis()
    app.state.rate_limiter = RateLimiter(app.state.redis)
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("API Gateway started successfully")
    
    yield
    
    # Shutdown
    await app.state.redis.close()
    await app.state.http_client.aclose()
    logger.info("API Gateway shutdown complete")

app = FastAPI(
    title="MantraPath API Gateway",
    description="Central API gateway for MantraPath microservices",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://mantrapath.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

def get_service_url(path: str) -> tuple[str, str]:
    """Determine which service to route to based on path"""
    if path.startswith("/api/auth/") or path.startswith("/auth/"):
        return SERVICE_URLS["auth"], path.replace("/api/auth", "").replace("/auth", "")
    elif path.startswith("/api/profiles/") or path.startswith("/profiles/"):
        return SERVICE_URLS["profile"], path
    elif path.startswith("/api/v1/mood/") or path.startswith("/api/v1/journal/") or \
         path.startswith("/api/v1/habits/") or path.startswith("/api/v1/insights/") or \
         path.startswith("/api/v1/analytics/"):
        return SERVICE_URLS["mood"], path
    elif path.startswith("/api/chatbot/"):
        return SERVICE_URLS["chatbot"], path
    elif path.startswith("/content/") or path.startswith("/affirmations/") or \
         path.startswith("/bookmark/") or path.startswith("/challenge/"):
        return SERVICE_URLS["content"], path
    elif path.startswith("/forums/") or path.startswith("/users/"):
        return SERVICE_URLS["community"], path
    elif path.startswith("/notify/"):
        return SERVICE_URLS["notification"], path
    elif path.startswith("/api/v1/media/"):
        return SERVICE_URLS["media"], path
    elif path.startswith("/api/analytics/"):
        return SERVICE_URLS["analytics"], path
    else:
        raise HTTPException(status_code=404, detail="Service not found")

async def verify_token(request: Request) -> Optional[Dict[str, Any]]:
    """Verify JWT token with auth service"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    
    # Check cache first
    cached_user = await app.state.redis.get(f"token:{token}")
    if cached_user:
        return json.loads(cached_user)
    
    # Verify with auth service
    try:
        async with app.state.http_client as client:
            response = await client.post(
                f"{SERVICE_URLS['auth']}/validate",
                json={"token": token}
            )
            if response.status_code == 200:
                user_data = response.json()
                # Cache for 5 minutes
                await app.state.redis.setex(f"token:{token}", 300, json.dumps(user_data))
                return user_data
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
    
    return None

async def check_rate_limit(request: Request, user_id: Optional[str] = None):
    """Check rate limits for requests"""
    client_ip = request.client.host
    
    # Different limits for authenticated vs anonymous users
    if user_id:
        limit_key = f"rate_limit:user:{user_id}"
        limit = 1000  # 1000 requests per hour for authenticated users
    else:
        limit_key = f"rate_limit:ip:{client_ip}"
        limit = 100   # 100 requests per hour for anonymous users
    
    if not await app.state.rate_limiter.is_allowed(limit_key, limit, 3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": list(SERVICE_URLS.keys())
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    # This would typically integrate with Prometheus
    return {
        "active_connections": 0,
        "requests_per_minute": 0,
        "error_rate": 0.0,
        "avg_response_time": 0.0
    }

async def proxy_request(request: Request, target_url: str, target_path: str):
    """Proxy request to target service"""
    try:
        # Prepare headers
        headers = dict(request.headers)
        # Remove hop-by-hop headers
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # Read request body
        body = await request.body()
        
        # Make request to target service
        url = urljoin(target_url, target_path.lstrip('/'))
        
        async with app.state.http_client as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # Prepare response headers
            response_headers = dict(response.headers)
            # Remove hop-by-hop headers
            for header in ["content-length", "transfer-encoding", "connection"]:
                response_headers.pop(header, None)
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                status_code=response.status_code,
                headers=response_headers
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_to_service(request: Request, path: str):
    """Route all requests to appropriate microservices"""
    
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return JSONResponse(content={}, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        })
    
    # Rate limiting
    user_data = await verify_token(request)
    user_id = user_data.get("user_id") if user_data else None
    await check_rate_limit(request, user_id)
    
    # Get target service
    try:
        target_url, target_path = get_service_url(f"/{path}")
    except HTTPException:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    # Check if endpoint requires authentication
    protected_paths = [
        "/api/profiles/", "/api/v1/mood/", "/api/v1/journal/", "/api/v1/habits/",
        "/api/v1/insights/", "/api/v1/analytics/", "/api/chatbot/", "/forums/",
        "/notify/", "/api/v1/media/", "/bookmark/", "/challenge/"
    ]
    
    requires_auth = any(f"/{path}".startswith(protected) for protected in protected_paths)
    
    if requires_auth and not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Add user context to request headers if authenticated
    if user_data:
        # Forward user info to downstream services
        if hasattr(request, 'headers'):
            headers = dict(request.headers)
        else:
            headers = {}
        headers["X-User-ID"] = user_data.get("user_id", "")
        headers["X-User-Role"] = user_data.get("role", "user")
        headers["X-User-Email"] = user_data.get("email", "")
        
        # Create new request with updated headers
        request._headers = headers
    
    return await proxy_request(request, target_url, target_path)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)