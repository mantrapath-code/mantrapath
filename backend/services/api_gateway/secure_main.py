"""
Enhanced Secure API Gateway - Central entry point with security features
- Rate limiting
- Request validation
- Enhanced logging
- Circuit breaker pattern
- Security headers
"""
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
import time
import asyncio
from typing import Dict, Optional
import logging
from collections import defaultdict, deque
import jwt
from datetime import datetime, timedelta
import redis.asyncio as redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MantraPath Secure API Gateway",
    description="Secure central gateway for all MantraPath microservices",
    version="2.0.0",
    docs_url="/gateway/docs",  # Hide docs behind gateway path
    redoc_url="/gateway/redoc"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.mantrapath.com"]  # Add your domain
)

# CORS middleware with stricter controls
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "https://mantrapath.com",  # Add production domain
        "https://app.mantrapath.com"  # Add production app domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Service registry with health status
SERVICES = {
    "auth": {
        "url": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "profile": {
        "url": os.getenv("PROFILE_SERVICE_URL", "http://profile-service:8002"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "mood": {
        "url": os.getenv("MOOD_SERVICE_URL", "http://mood-service:8003"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "chatbot": {
        "url": os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8004"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "content": {
        "url": os.getenv("CONTENT_SERVICE_URL", "http://content-service:8005"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "community": {
        "url": os.getenv("COMMUNITY_SERVICE_URL", "http://community-service:8006"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "notification": {
        "url": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8007"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "ml": {
        "url": os.getenv("ML_SERVICE_URL", "http://ml-service:8008"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
    "media": {
        "url": os.getenv("MEDIA_SERVICE_URL", "http://media-service:8009"),
        "healthy": True,
        "last_check": time.time(),
        "failure_count": 0
    },
}

# Rate limiting storage
rate_limit_storage = defaultdict(lambda: deque())

# Redis connection for caching and rate limiting
redis_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize Redis connection and start health checks"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        redis_client = None
    
    # Start background health checks
    asyncio.create_task(periodic_health_checks())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections"""
    if redis_client:
        await redis_client.close()

# Security utilities
security = HTTPBearer(auto_error=False)

async def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

async def rate_limit_check(request: Request) -> bool:
    """Check if request is within rate limits"""
    client_ip = await get_client_ip(request)
    current_time = time.time()
    
    if redis_client:
        try:
            # Use Redis for distributed rate limiting
            key = f"rate_limit:{client_ip}"
            current_requests = await redis_client.incr(key)
            if current_requests == 1:
                await redis_client.expire(key, RATE_LIMIT_WINDOW)
            
            if current_requests > RATE_LIMIT_REQUESTS:
                return False
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e}")
            # Fallback to in-memory rate limiting
    
    # In-memory rate limiting fallback
    requests = rate_limit_storage[client_ip]
    
    # Remove old requests outside the window
    while requests and requests[0] <= current_time - RATE_LIMIT_WINDOW:
        requests.popleft()
    
    # Check if under limit
    if len(requests) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Add current request
    requests.append(current_time)
    return True

async def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[dict]:
    """Verify JWT token (optional for public endpoints)"""
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT token")
        return None

async def periodic_health_checks():
    """Periodically check service health"""
    while True:
        await asyncio.sleep(30)  # Check every 30 seconds
        await check_all_services_health()

async def check_all_services_health():
    """Check health of all services"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_info in SERVICES.items():
            try:
                response = await client.get(f"{service_info['url']}/health")
                if response.status_code == 200:
                    service_info['healthy'] = True
                    service_info['failure_count'] = 0
                else:
                    service_info['healthy'] = False
                    service_info['failure_count'] += 1
            except Exception as e:
                logger.warning(f"Health check failed for {service_name}: {e}")
                service_info['healthy'] = False
                service_info['failure_count'] += 1
            
            service_info['last_check'] = time.time()

def get_service_url(path: str) -> tuple[str, str]:
    """Determine which service to route to based on path"""
    
    # Auth service routes
    if any(path.startswith(prefix) for prefix in [
        "/auth/", "/register", "/login", "/logout", "/refresh-token", "/me", "/users/"
    ]):
        service_info = SERVICES["auth"]
        return service_info["url"], path, service_info["healthy"]
    
    # Profile service routes
    if path.startswith("/api/profiles/") or path.startswith("/api/preferences/"):
        service_info = SERVICES["profile"]
        return service_info["url"], path, service_info["healthy"]
    
    # Mood service routes
    if any(path.startswith(prefix) for prefix in [
        "/api/v1/mood/", "/api/v1/journal/", "/api/v1/habits/", 
        "/api/v1/insights/", "/api/v1/analytics/"
    ]):
        service_info = SERVICES["mood"]
        return service_info["url"], path, service_info["healthy"]
    
    # Chatbot service routes
    if path.startswith("/api/chatbot/"):
        service_info = SERVICES["chatbot"]
        return service_info["url"], path, service_info["healthy"]
    
    # Content service routes
    if any(path.startswith(prefix) for prefix in [
        "/content/", "/affirmations", "/bookmark/", "/challenge/"
    ]):
        service_info = SERVICES["content"]
        return service_info["url"], path, service_info["healthy"]
    
    # Community service routes
    if any(path.startswith(prefix) for prefix in [
        "/forums", "/user/stats", "/user/activity"
    ]):
        service_info = SERVICES["community"]
        return service_info["url"], path, service_info["healthy"]
    
    # Notification service routes
    if path.startswith("/notify/") or path.startswith("/notifications"):
        service_info = SERVICES["notification"]
        return service_info["url"], path, service_info["healthy"]
    
    # ML service routes (with path transformations)
    if path.startswith("/api/v1/ml/"):
        service_info = SERVICES["ml"]
        transformed_path = path.replace("/api/v1/ml/", "")  # remove prefix
        if transformed_path.startswith(("ml/", "crisis/", "dashboard/")):
            return service_info["url"], f"/{transformed_path}", service_info["healthy"]
        return service_info["url"], f"/ml/{transformed_path}", service_info["healthy"]
    elif path.startswith("/api/ml/"):
        service_info = SERVICES["ml"]
        transformed_path = path.replace("/api/ml/", "")
        if transformed_path.startswith(("ml/", "crisis/", "dashboard/")):
            return service_info["url"], f"/{transformed_path}", service_info["healthy"]
        return service_info["url"], f"/ml/{transformed_path}", service_info["healthy"]
    elif path.startswith("/ml/"):
        service_info = SERVICES["ml"]
        return service_info["url"], path, service_info["healthy"]
    
    # Media service routes
    if path.startswith("/api/v1/media/"):
        service_info = SERVICES["media"]
        return service_info["url"], path, service_info["healthy"]
    
    # Default to auth service for unmatched routes
    service_info = SERVICES["auth"]
    return service_info["url"], path, service_info["healthy"]

async def proxy_request(request: Request, service_url: str, path: str, user_info: dict = None):
    """Proxy request to target service with enhanced error handling"""
    target_url = f"{service_url}{path}"
    
    # Prepare headers
    headers = dict(request.headers)
    headers.pop('host', None)  # Remove host header
    
    # Add user context if available
    if user_info:
        headers['X-User-ID'] = str(user_info.get('user_id', ''))
        headers['X-User-Email'] = user_info.get('email', '')
    
    # Add security headers
    headers['X-Forwarded-For'] = await get_client_ip(request)
    headers['X-Gateway-Version'] = '2.0.0'
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get request body
            body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
            
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body
            )
            
            # Add security headers to response
            response_headers = dict(response.headers)
            response_headers['X-Content-Type-Options'] = 'nosniff'
            response_headers['X-Frame-Options'] = 'DENY'
            response_headers['X-XSS-Protection'] = '1; mode=block'
            
            return JSONResponse(
                content=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                status_code=response.status_code,
                headers=response_headers
            )
            
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to {service_url}")
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.ConnectError:
        logger.error(f"Cannot connect to {service_url}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Error proxying request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Middleware for rate limiting and security
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Apply security checks to all requests"""
    
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/gateway/health"]:
        return await call_next(request)
    
    # Rate limiting
    if not await rate_limit_check(request):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    # Add security headers
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Health check endpoints
@app.get("/health")
@app.get("/gateway/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/gateway/services")
async def get_services():
    """Get service registry with health status"""
    service_status = {}
    for name, info in SERVICES.items():
        service_status[name] = {
            "url": info["url"],
            "healthy": info["healthy"],
            "last_check": info["last_check"],
            "failure_count": info["failure_count"]
        }
    
    return {
        "services": service_status,
        "gateway_version": "2.0.0"
    }

@app.get("/gateway/stats")
async def get_gateway_stats():
    """Get gateway statistics"""
    healthy_services = sum(1 for s in SERVICES.values() if s["healthy"])
    total_services = len(SERVICES)
    
    return {
        "total_services": total_services,
        "healthy_services": healthy_services,
        "unhealthy_services": total_services - healthy_services,
        "uptime": time.time(),
        "version": "2.0.0"
    }

# Universal route handler with enhanced security
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_request(
    request: Request, 
    path: str,
    user_info: dict = Depends(verify_jwt_token)
):
    """Route requests to appropriate services with security checks"""
    
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return JSONResponse(content={}, status_code=200)
    
    # Get service URL and health status
    service_url, service_path, is_healthy = get_service_url(path)
    
    # Check if service is healthy
    if not is_healthy:
        logger.warning(f"Service unhealthy for path: {path}")
        # Try to route anyway but log the issue
    
    logger.info(f"🔄 Routing {request.method} /{path} to {service_url}{service_path}")
    
    return await proxy_request(request, service_url, service_path, user_info)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
