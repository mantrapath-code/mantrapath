"""
MantraPath Deployment API Service
Controlled API access for frontend engineers with model training status and service health
"""

import logging
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Import our modules
from .config.settings import get_settings
from .config.permissions import FRONTEND_ENGINEER_PERMISSIONS
from .utils.auth import FrontendEngineerAuth
from .utils.rate_limiting import RateLimiter
from .services.api_documentation import APIDocumentationService
from .services.model_monitor import ModelMonitorService
from .services.health_checker import HealthCheckerService
from .services.usage_tracker import UsageTrackerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
settings = get_settings()
auth_service = FrontendEngineerAuth()
rate_limiter = RateLimiter()
api_docs_service = APIDocumentationService()
model_monitor_service = ModelMonitorService()
health_checker_service = HealthCheckerService()
usage_tracker_service = UsageTrackerService()

# Security
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting MantraPath Deployment API Service...")
    
    # Initialize services
    await api_docs_service.initialize()
    await model_monitor_service.initialize()
    await health_checker_service.initialize()
    await usage_tracker_service.initialize()
    
    logger.info("✅ Deployment API Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Deployment API Service...")
    await api_docs_service.cleanup()
    await model_monitor_service.cleanup()
    await health_checker_service.cleanup()
    await usage_tracker_service.cleanup()
    logger.info("✅ Deployment API Service shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="MantraPath Deployment API",
    description="Controlled API access for frontend engineers with model training status and service health",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Dependency for frontend engineer authentication
async def get_frontend_engineer(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Authenticate frontend engineer and return permissions"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        engineer = await auth_service.authenticate(credentials.credentials)
        return engineer
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


# Dependency for rate limiting
async def check_rate_limit(
    request: Request,
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
) -> None:
    """Check rate limits for the authenticated engineer"""
    if not await rate_limiter.check_limit(engineer["id"], request.url.path):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "MantraPath Deployment API",
        "version": "1.0.0",
        "description": "Controlled API access for frontend engineers",
        "features": [
            "API Documentation",
            "Model Training Status",
            "Service Health Monitoring",
            "API Testing Tools",
            "Usage Metrics"
        ],
        "documentation": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Service health check"""
    try:
        health_status = await health_checker_service.get_overall_health()
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "deployment_api",
            "details": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "service": "deployment_api",
                "error": str(e)
            }
        )


# API Documentation endpoints
@app.get("/api/docs", dependencies=[Depends(check_rate_limit)])
async def get_api_documentation(
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Get complete API documentation for all services"""
    try:
        docs = await api_docs_service.get_all_documentation()
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_api_documentation",
            "success"
        )
        
        return {
            "status": "success",
            "data": docs,
            "timestamp": time.time(),
            "permissions": engineer["permissions"]
        }
    except Exception as e:
        logger.error(f"Failed to get API documentation: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_api_documentation",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API documentation"
        )


@app.get("/api/docs/{service_name}", dependencies=[Depends(check_rate_limit)])
async def get_service_documentation(
    service_name: str,
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Get API documentation for a specific service"""
    try:
        docs = await api_docs_service.get_service_documentation(service_name)
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            f"get_service_documentation_{service_name}",
            "success"
        )
        
        return {
            "status": "success",
            "service": service_name,
            "data": docs,
            "timestamp": time.time(),
            "permissions": engineer["permissions"]
        }
    except Exception as e:
        logger.error(f"Failed to get {service_name} documentation: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            f"get_service_documentation_{service_name}",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve {service_name} documentation"
        )


# Model Training Status endpoints
@app.get("/api/models/status", dependencies=[Depends(check_rate_limit)])
async def get_model_training_status(
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Get overall model training status"""
    try:
        status_data = await model_monitor_service.get_overall_status()
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_model_training_status",
            "success"
        )
        
        return {
            "status": "success",
            "data": status_data,
            "timestamp": time.time(),
            "permissions": engineer["permissions"]
        }
    except Exception as e:
        logger.error(f"Failed to get model training status: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_model_training_status",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve model training status"
        )


@app.get("/api/models/status/{model_type}", dependencies=[Depends(check_rate_limit)])
async def get_model_type_status(
    model_type: str,
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Get training status for a specific model type"""
    try:
        status_data = await model_monitor_service.get_model_type_status(model_type)
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            f"get_model_type_status_{model_type}",
            "success"
        )
        
        return {
            "status": "success",
            "model_type": model_type,
            "data": status_data,
            "timestamp": time.time(),
            "permissions": engineer["permissions"]
        }
    except Exception as e:
        logger.error(f"Failed to get {model_type} status: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            f"get_model_type_status_{model_type}",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve {model_type} status"
        )


# Service Health endpoints
@app.get("/api/health/services", dependencies=[Depends(check_rate_limit)])
async def get_services_health(
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Get health status of all services"""
    try:
        health_data = await health_checker_service.get_all_services_health()
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_services_health",
            "success"
        )
        
        return {
            "status": "success",
            "data": health_data,
            "timestamp": time.time(),
            "permissions": engineer["permissions"]
        }
    except Exception as e:
        logger.error(f"Failed to get services health: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_services_health",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve services health"
        )


@app.get("/api/health/services/{service_name}", dependencies=[Depends(check_rate_limit)])
async def get_service_health(
    service_name: str,
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Get health status of a specific service"""
    try:
        health_data = await health_checker_service.get_service_health(service_name)
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            f"get_service_health_{service_name}",
            "success"
        )
        
        return {
            "status": "success",
            "service": service_name,
            "data": health_data,
            "timestamp": time.time(),
            "permissions": engineer["id"]
        }
    except Exception as e:
        logger.error(f"Failed to get {service_name} health: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            f"get_service_health_{service_name}",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve {service_name} health"
        )


# API Testing endpoints
@app.post("/api/testing/test-endpoint", dependencies=[Depends(check_rate_limit)])
async def test_api_endpoint(
    request: Dict[str, Any],
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Test a specific API endpoint"""
    try:
        # Check if engineer has testing permissions
        if engineer["permissions"].get("api_testing") != "full":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for API testing"
            )
        
        test_result = await api_docs_service.test_endpoint(request)
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "test_api_endpoint",
            "success"
        )
        
        return {
            "status": "success",
            "data": test_result,
            "timestamp": time.time(),
            "permissions": engineer["permissions"]
        }
    except Exception as e:
        logger.error(f"Failed to test API endpoint: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "test_api_endpoint",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test API endpoint"
        )


# Usage Metrics endpoints
@app.get("/api/usage/metrics", dependencies=[Depends(check_rate_limit)])
async def get_usage_metrics(
    engineer: Dict[str, Any] = Depends(get_frontend_engineer)
):
    """Get usage metrics for the authenticated engineer"""
    try:
        metrics = await usage_tracker_service.get_engineer_metrics(engineer["id"])
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_usage_metrics",
            "success"
        )
        
        return {
            "status": "success",
            "data": metrics,
            "timestamp": time.time(),
            "permissions": engineer["permissions"]
        }
    except Exception as e:
        logger.error(f"Failed to get usage metrics: {e}")
        
        # Track usage
        await usage_tracker_service.track_api_call(
            engineer["id"], 
            "get_usage_metrics",
            "error"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve usage metrics"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time(),
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.DEPLOYMENT_API_HOST,
        port=settings.DEPLOYMENT_API_PORT,
        reload=settings.DEBUG
    )

