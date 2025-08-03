"""
API Gateway - Routes all requests to appropriate microservices
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import os
from typing import Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MantraPath API Gateway",
    description="Central gateway for all MantraPath microservices",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service registry
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
    "profile": os.getenv("PROFILE_SERVICE_URL", "http://localhost:8002"),
    "mood": os.getenv("MOOD_SERVICE_URL", "http://localhost:8003"),
    "chatbot": os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004"),
    "content": os.getenv("CONTENT_SERVICE_URL", "http://localhost:8005"),
    "community": os.getenv("COMMUNITY_SERVICE_URL", "http://localhost:8006"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8007"),
    "ml": os.getenv("ML_SERVICE_URL", "http://localhost:8008"),
    "media": os.getenv("MEDIA_SERVICE_URL", "http://localhost:8009"),
}

def get_service_url(path: str) -> tuple[str, str]:
    """Determine which service to route to based on path"""
    
    # Auth service routes
    if any(path.startswith(prefix) for prefix in ["/auth/", "/register", "/login", "/logout", "/refresh-token", "/me", "/users/"]):
        return SERVICES["auth"], path
    
    # Profile service routes
    if path.startswith("/api/profiles/") or path.startswith("/api/preferences/"):
        return SERVICES["profile"], path
    
    # Mood service routes
    if any(path.startswith(prefix) for prefix in ["/api/v1/mood/", "/api/v1/journal/", "/api/v1/habits/", "/api/v1/insights/", "/api/v1/analytics/"]):
        return SERVICES["mood"], path
    
    # Chatbot service routes
    if path.startswith("/api/chatbot/"):
        # Keep the full path for the chatbot service
        return SERVICES["chatbot"], path
    
    # Content service routes
    if any(path.startswith(prefix) for prefix in ["/content/", "/affirmations", "/bookmark/", "/challenge/"]):
        return SERVICES["content"], path
    
    # Community service routes
    if any(path.startswith(prefix) for prefix in ["/forums", "/user/stats", "/user/activity"]):
        return SERVICES["community"], path
    
    # Notification service routes
    if path.startswith("/notify/") or path.startswith("/notifications"):
        return SERVICES["notification"], path
    
    # ML service routes
    if path.startswith("/api/ml/"):
        # Strip the /api/ml/ prefix for the ML service
        ml_path = path[8:]  # Remove "/api/ml/" (8 characters)
        return SERVICES["ml"], ml_path
    
    # Media service routes
    if path.startswith("/api/v1/media/"):
        return SERVICES["media"], path
    
    # Default to auth service for unmatched routes
    return SERVICES["auth"], path

async def proxy_request(request: Request, service_url: str, path: str):
    """Proxy request to appropriate microservice"""
    
    # Ensure proper URL construction with slash
    if not path.startswith("/"):
        path = f"/{path}"
    url = f"{service_url}{path}"
    
    # Extract headers
    headers = dict(request.headers)
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    # Get query parameters
    query_params = str(request.query_params)
    if query_params:
        url += f"?{query_params}"
    
    # Get request body for POST/PUT requests
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
            
            # Return response with same status code and headers
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/services")
async def list_services():
    """List all registered services"""
    return {"services": SERVICES}

# Universal request handler
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_request(request: Request, path: str):
    """Route requests to appropriate microservice"""
    
    # Handle preflight CORS requests
    if request.method == "OPTIONS":
        return JSONResponse(content={}, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        })
    
    service_url, service_path = get_service_url(f"/{path}")
    
    logger.info(f"Routing {request.method} /{path} to {service_url}{service_path}")
    
    return await proxy_request(request, service_url, service_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)