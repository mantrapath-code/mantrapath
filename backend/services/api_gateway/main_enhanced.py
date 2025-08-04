"""
Enhanced API Gateway - Robust, scalable gateway with request tracking and unified service integration
"""
from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import os
import json
import time
import uuid
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from contextlib import asynccontextmanager

# Import shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.auth import verify_token, get_current_user

try:
    from shared.redis_client import get_redis_client
except ImportError:
    def get_redis_client():
        return None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Service registry with health check endpoints
SERVICE_REGISTRY = {
    "auth": {
        "url": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
        "health_endpoint": "/health",
        "routes": ["/auth/", "/register", "/login", "/logout", "/refresh-token", "/me", "/users/"],
        "version": "v1"
    },
    "profile": {
        "url": os.getenv("PROFILE_SERVICE_URL", "http://localhost:8002"),
        "health_endpoint": "/health",
        "routes": ["/api/profiles/", "/api/preferences/"],
        "version": "v1"
    },
    "mood": {
        "url": os.getenv("MOOD_SERVICE_URL", "http://localhost:8003"),
        "health_endpoint": "/health",
        "routes": ["/api/v1/mood/", "/api/v1/journal/", "/api/v1/habits/", "/api/v1/insights/", "/api/v1/analytics/"],
        "version": "v1"
    },
    "chatbot": {
        "url": os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004"),
        "health_endpoint": "/health",
        "routes": ["/api/chatbot/", "/api/v1/chat/"],
        "version": "v1"
    },
    "content": {
        "url": os.getenv("CONTENT_SERVICE_URL", "http://localhost:8005"),
        "health_endpoint": "/health",
        "routes": ["/content/", "/affirmations", "/bookmark/", "/challenge/", "/api/v1/content/"],
        "version": "v1"
    },
    "community": {
        "url": os.getenv("COMMUNITY_SERVICE_URL", "http://localhost:8006"),
        "health_endpoint": "/health",
        "routes": ["/forums/", "/api/v1/community/", "/api/v1/social/"],
        "version": "v1"
    },
    "notification": {
        "url": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8007"),
        "health_endpoint": "/health",
        "routes": ["/notify/", "/api/v1/notifications/"],
        "version": "v1",
        "websocket": True
    },
    "ml": {
        "url": os.getenv("ML_SERVICE_URL", "http://localhost:8008"),
        "health_endpoint": "/health",
        "routes": ["/api/v1/ml/", "/ml/", "/crisis/", "/dashboard/"],
        "version": "v1"
    },
    "media": {
        "url": os.getenv("MEDIA_SERVICE_URL", "http://localhost:8009"),
        "health_endpoint": "/health",
        "routes": ["/api/v1/media/", "/api/v1/upload/"],
        "version": "v1"
    }
}

# Request tracking and analytics
request_metrics = defaultdict(lambda: defaultdict(float))
service_health = {}
active_websockets = {}

# Rate limiting
rate_limit_storage = defaultdict(lambda: defaultdict(list))

class APIGateway:
    def __init__(self):
        self.app = FastAPI(
            title="MantraPath API Gateway",
            description="Enhanced gateway for all MantraPath microservices with request tracking",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        self.setup_middleware()
        self.setup_routes()
        
    def setup_middleware(self):
        """Setup CORS and custom middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.middleware("http")
        async def request_tracking_middleware(request: Request, call_next):
            """Track all requests for analytics and monitoring"""
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            # Add request ID to headers
            request.state.request_id = request_id
            
            # Log request
            logger.info(f"Request {request_id}: {request.method} {request.url}")
            
            try:
                response = await call_next(request)
                
                # Calculate response time
                process_time = time.time() - start_time
                
                # Track metrics
                endpoint = str(request.url.path)
                request_metrics[endpoint]["total"] += 1
                request_metrics[endpoint]["response_time"] += process_time
                
                if response.status_code >= 400:
                    request_metrics[endpoint]["errors"] += 1
                
                # Add tracking headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = str(process_time)
                
                logger.info(f"Request {request_id}: {response.status_code} - {process_time:.3f}s")
                
                return response
                
            except Exception as e:
                process_time = time.time() - start_time
                logger.error(f"Request {request_id}: Error - {str(e)} - {process_time:.3f}s")
                raise
    
    def setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/health")
        async def gateway_health():
            """Gateway health check with service status"""
            return {
                "status": "healthy",
                "service": "api-gateway",
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "services": service_health
            }
        
        @self.app.get("/services")
        async def list_services():
            """List all registered services with their status"""
            return {
                "services": SERVICE_REGISTRY,
                "health": service_health,
                "total_services": len(SERVICE_REGISTRY)
            }
        
        @self.app.get("/metrics")
        async def get_metrics(credentials: HTTPAuthorizationCredentials = Depends(security)):
            """Get request metrics (requires authentication)"""
            if not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Verify token
            payload = verify_token(credentials.credentials)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            # Calculate average response times
            metrics = {}
            for endpoint, data in request_metrics.items():
                total_requests = data["total"]
                if total_requests > 0:
                    metrics[endpoint] = {
                        "total_requests": total_requests,
                        "error_count": data["errors"],
                        "error_rate": data["errors"] / total_requests * 100,
                        "avg_response_time": data["response_time"] / total_requests,
                        "last_updated": datetime.utcnow().isoformat()
                    }
            
            return {
                "metrics": metrics,
                "active_websockets": len(active_websockets),
                "service_health": service_health
            }
        
        @self.app.delete("/user/{user_id}/data")
        async def delete_user_data(
            user_id: str,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Delete all user data across all services"""
            if not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Verify token and user authorization
            payload = verify_token(credentials.credentials)
            if not payload or payload.get("sub") != user_id:
                raise HTTPException(status_code=403, detail="Unauthorized to delete this user's data")
            
            # Add background task to delete data from all services
            background_tasks.add_task(delete_user_data_from_services, user_id)
            
            return {
                "message": "User data deletion initiated",
                "user_id": user_id,
                "status": "processing"
            }
        
        @self.app.get("/user/{user_id}/data/export")
        async def export_user_data(
            user_id: str,
            credentials: HTTPAuthorizationCredentials = Depends(security)
        ):
            """Export all user data from all services"""
            if not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            # Verify token and user authorization
            payload = verify_token(credentials.credentials)
            if not payload or payload.get("sub") != user_id:
                raise HTTPException(status_code=403, detail="Unauthorized to export this user's data")
            
            # Collect data from all services
            user_data = await collect_user_data_from_services(user_id)
            
            return {
                "user_id": user_id,
                "export_timestamp": datetime.utcnow().isoformat(),
                "data": user_data
            }
        
        @self.app.websocket("/ws/{user_id}")
        async def websocket_endpoint(websocket: WebSocket, user_id: str):
            """WebSocket endpoint for real-time features"""
            await websocket.accept()
            active_websockets[user_id] = websocket
            
            try:
                # Send welcome message
                await websocket.send_json({
                    "type": "connection",
                    "data": {"message": "Connected to MantraPath Gateway", "user_id": user_id},
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Keep connection alive
                while True:
                    try:
                        data = await websocket.receive_json()
                        
                        # Handle different message types
                        if data.get("type") == "heartbeat":
                            await websocket.send_json({
                                "type": "heartbeat_ack",
                                "timestamp": datetime.utcnow().isoformat()
                            })
                        else:
                            # Forward to appropriate service if needed
                            logger.info(f"WebSocket message from {user_id}: {data}")
                            
                    except WebSocketDisconnect:
                        break
                    except Exception as e:
                        logger.error(f"WebSocket error for user {user_id}: {e}")
                        break
                        
            finally:
                active_websockets.pop(user_id, None)
                logger.info(f"WebSocket disconnected for user {user_id}")
        
        # Universal request handler
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
        async def route_request(request: Request, path: str):
            """Enhanced request routing with rate limiting and service discovery"""
            
            # Handle preflight CORS requests
            if request.method == "OPTIONS":
                return JSONResponse(content={}, headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                })
            
            # Apply rate limiting
            client_ip = request.client.host if request.client else "unknown"
            if await is_rate_limited(client_ip, path):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Find service and route
            service_name, service_config = get_service_for_path(f"/{path}")
            
            if not service_name or not service_config:
                raise HTTPException(status_code=404, detail="Service not found for this path")
            
            # Check service health
            if not await is_service_healthy(service_name, service_config):
                raise HTTPException(status_code=503, detail=f"Service {service_name} is unavailable")
            
            # Proxy the request
            return await proxy_request_enhanced(request, service_config, f"/{path}")

async def is_rate_limited(client_ip: str, path: str, limit: int = 100, window: int = 60) -> bool:
    """Check if client is rate limited"""
    now = time.time()
    window_start = now - window
    
    # Clean old requests
    rate_limit_storage[client_ip][path] = [
        req_time for req_time in rate_limit_storage[client_ip][path] 
        if req_time > window_start
    ]
    
    # Check limit
    if len(rate_limit_storage[client_ip][path]) >= limit:
        return True
    
    # Add current request
    rate_limit_storage[client_ip][path].append(now)
    return False

def get_service_for_path(path: str) -> tuple[Optional[str], Optional[Dict]]:
    """Find the appropriate service for a given path"""
    for service_name, config in SERVICE_REGISTRY.items():
        for route_pattern in config["routes"]:
            if path.startswith(route_pattern):
                return service_name, config
    
    # Default to auth service for unmatched routes
    return "auth", SERVICE_REGISTRY["auth"]

async def is_service_healthy(service_name: str, service_config: Dict) -> bool:
    """Check if a service is healthy"""
    try:
        health_url = f"{service_config['url']}{service_config['health_endpoint']}"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(health_url)
            is_healthy = response.status_code == 200
            
            # Update service health cache
            service_health[service_name] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "last_check": datetime.utcnow().isoformat(),
                "url": service_config["url"]
            }
            
            return is_healthy
            
    except Exception as e:
        logger.error(f"Health check failed for {service_name}: {e}")
        service_health[service_name] = {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat(),
            "url": service_config["url"]
        }
        return False

async def proxy_request_enhanced(request: Request, service_config: Dict, path: str):
    """Enhanced request proxying with better error handling"""
    
    url = f"{service_config['url']}{path}"
    
    # Prepare headers
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Add request tracking headers
    headers["X-Gateway-Request-ID"] = request.state.request_id
    headers["X-Gateway-Timestamp"] = datetime.utcnow().isoformat()
    
    # Handle query parameters
    query_params = str(request.query_params)
    if query_params:
        url += f"?{query_params}"
    
    # Get request body
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body,
            )
            
            # Add gateway headers to response
            response_headers = dict(response.headers)
            response_headers["X-Gateway-Service"] = service_config["url"]
            response_headers["X-Gateway-Version"] = service_config["version"]
            
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code,
                headers=response_headers
            )
            
    except httpx.TimeoutException:
        logger.error(f"Timeout when proxying to {url}")
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.RequestError as e:
        logger.error(f"Request error when proxying to {url}: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error when proxying to {url}: {e}")
        raise HTTPException(status_code=500, detail="Internal gateway error")

async def delete_user_data_from_services(user_id: str):
    """Delete user data from all services"""
    logger.info(f"Starting user data deletion for user {user_id}")
    
    deletion_results = {}
    
    for service_name, config in SERVICE_REGISTRY.items():
        try:
            # Call delete endpoint on each service
            delete_url = f"{config['url']}/api/v1/user/{user_id}/delete"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(delete_url)
                
                deletion_results[service_name] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_code": response.status_code,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to delete data from {service_name}: {e}")
            deletion_results[service_name] = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    logger.info(f"User data deletion completed for user {user_id}: {deletion_results}")
    
    # Store deletion audit log
    try:
        redis_client = get_redis_client()
        if redis_client:
            audit_log = {
                "user_id": user_id,
                "action": "data_deletion",
                "results": deletion_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            redis_client.setex(f"audit:deletion:{user_id}", 86400 * 30, json.dumps(audit_log))  # Keep for 30 days
    except Exception as e:
        logger.error(f"Failed to store deletion audit log: {e}")

async def collect_user_data_from_services(user_id: str) -> Dict:
    """Collect user data from all services for export"""
    logger.info(f"Starting user data export for user {user_id}")
    
    user_data = {}
    
    for service_name, config in SERVICE_REGISTRY.items():
        try:
            # Call export endpoint on each service
            export_url = f"{config['url']}/api/v1/user/{user_id}/export"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(export_url)
                
                if response.status_code == 200:
                    user_data[service_name] = response.json()
                else:
                    user_data[service_name] = {
                        "error": f"Export failed with status {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Failed to export data from {service_name}: {e}")
            user_data[service_name] = {
                "error": str(e)
            }
    
    logger.info(f"User data export completed for user {user_id}")
    return user_data

async def health_check_background_task():
    """Background task to periodically check service health"""
    while True:
        logger.info("Running periodic health checks...")
        
        for service_name, config in SERVICE_REGISTRY.items():
            await is_service_healthy(service_name, config)
        
        await asyncio.sleep(30)  # Check every 30 seconds

# Create the gateway instance
gateway = APIGateway()
app = gateway.app

# Start background tasks
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(health_check_background_task())
    logger.info("API Gateway started with enhanced features")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
