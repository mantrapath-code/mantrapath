"""
API Gateway for MantraPath
Routes requests to appropriate microservices
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import json
from typing import Dict, Any
import os
from contextlib import asynccontextmanager

# Service URLs mapping
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "profile": os.getenv("PROFILE_SERVICE_URL", "http://profile-service:8002"), 
    "mood": os.getenv("MOOD_SERVICE_URL", "http://mood-service:8003"),
    "chatbot": os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8004"),
    "content": os.getenv("CONTENT_SERVICE_URL", "http://content-service:8005"),
    "community": os.getenv("COMMUNITY_SERVICE_URL", "http://community-service:8006"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8007"),
    "media": os.getenv("MEDIA_SERVICE_URL", "http://media-service:8009"),
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 API Gateway starting up...")
    yield
    # Shutdown  
    print("🛑 API Gateway shutting down...")

app = FastAPI(
    title="MantraPath API Gateway",
    description="Central API gateway for MantraPath microservices",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route mapping based on path patterns
ROUTE_MAPPING = {
    "/login": "auth",
    "/register": "auth", 
    "/logout": "auth",
    "/me": "auth",
    "/refresh-token": "auth",
    "/api/profiles": "profile",
    "/api/preferences": "profile",
    "/api/v1/mood": "mood",
    "/api/v1/journal": "mood",
    "/api/v1/habits": "mood", 
    "/api/v1/insights": "mood",
    "/api/v1/analytics": "mood",
    "/api/chatbot": "chatbot",
    "/content": "content",
    "/affirmations": "content",
    "/bookmark": "content",
    "/challenge": "content",
    "/forums": "community",
    "/users": "community",
    "/notify": "notification",
    "/api/v1/media": "media",
}

def get_service_for_path(path: str) -> str:
    """Determine which service to route to based on path"""
    for route_prefix, service in ROUTE_MAPPING.items():
        if path.startswith(route_prefix):
            return service
    return "auth"  # Default fallback

async def forward_request(
    request: Request,
    service_name: str,
    path: str
) -> JSONResponse:
    """Forward request to appropriate microservice"""
    
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
    
    service_url = SERVICES[service_name]
    target_url = f"{service_url}{path}"
    
    # Prepare headers (exclude host)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Get request body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body,
            )
            
        # Return response
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"detail": response.text},
            headers=dict(response.headers)
        )
        
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {"status": "healthy", "gateway": "running", "services": SERVICES}

@app.get("/metrics")
async def metrics():
    """System metrics"""
    return {
        "services_count": len(SERVICES),
        "active_services": list(SERVICES.keys()),
        "gateway_status": "operational"
    }

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def gateway_route(request: Request, path: str):
    """Universal route handler"""
    
    # Handle preflight OPTIONS requests
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    # Determine target service
    service_name = get_service_for_path(f"/{path}")
    
    # Forward request
    return await forward_request(request, service_name, f"/{path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)