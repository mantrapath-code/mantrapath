"""
MantraPath API Gateway V3 Enhanced - Main Application
Voice-enabled, AI-powered, culturally-aware service orchestration platform
"""

import uuid
import logging
import time
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# V3 Enhanced Imports
from src.core.config import gateway_config, service_config
from src.core.models import ProxyRequest, HTTPMethod
from src.registry import ServiceRegistry
from src.routing import RequestRouter, LoadBalancerFactory, RequestProxy
from src.middleware import RateLimiter, get_client_identifier, CircuitBreaker
from src.health import HealthChecker

# V3 Enhanced Components
from src.middleware.voice_routing import VoiceRoutingMiddleware
from src.middleware.ai_context import AIContextMiddleware
from src.middleware.cultural_context import CulturalContextMiddleware
from src.middleware.performance import PerformanceMiddleware

from src.services.voice_router import VoiceCommandRouter
from src.services.context_manager import AIContextManager
from src.services.cultural_manager import CulturalContextManager
from src.services.websocket_manager import WebSocketManager

from src.models.voice_models import VoiceCommand, VoiceResponse
from src.models.context_models import AIContext, CulturalContext
from src.models.response_models import EnhancedResponse

from src.utils.language_detector import LanguageDetector
from src.utils.cache_manager import CacheManager
from src.utils.performance_monitor import PerformanceMonitor

# Configure structured logging
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global V3 Enhanced Components
service_registry = ServiceRegistry()
request_router = RequestRouter()
load_balancer = LoadBalancerFactory.create_load_balancer(gateway_config.load_balancing_strategy)
request_proxy = RequestProxy()
rate_limiter = RateLimiter()
circuit_breaker = CircuitBreaker()
health_checker = HealthChecker(service_registry, circuit_breaker)

# V3 Enhanced Services
voice_router = VoiceCommandRouter()
ai_context_manager = AIContextManager()
cultural_manager = CulturalContextManager()
websocket_manager = WebSocketManager()
language_detector = LanguageDetector()
cache_manager = CacheManager()
performance_monitor = PerformanceMonitor()

# Security
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for V3 Enhanced Gateway"""
    # Startup
    logger.info("🚀 Starting MantraPath API Gateway V3 Enhanced...")
    
    # Initialize core services
    await service_registry.start()
    await cache_manager.initialize()
    await performance_monitor.start()
    
    # Initialize V3 enhanced services
    await voice_router.initialize()
    await ai_context_manager.initialize()
    await cultural_manager.initialize()
    await websocket_manager.initialize()
    
    logger.info("✅ API Gateway V3 Enhanced started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API Gateway V3 Enhanced...")
    await websocket_manager.shutdown()
    await performance_monitor.stop()
    await cache_manager.close()
    await service_registry.stop()
    logger.info("✅ API Gateway V3 Enhanced shutdown complete")


# Create FastAPI application with V3 enhancements
app = FastAPI(
    title="MantraPath API Gateway V3 Enhanced",
    description="Voice-enabled, AI-powered, culturally-aware service orchestration platform",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/api/v3/docs",
    redoc_url="/api/v3/redoc",
    openapi_url="/api/v3/openapi.json"
)

# Add V3 Enhanced Middleware Stack
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Voice-Intent", "X-Cultural-Context", "X-AI-Context"]
)

# V3 Enhanced Custom Middleware
app.add_middleware(PerformanceMiddleware, performance_monitor=performance_monitor)
app.add_middleware(CulturalContextMiddleware, cultural_manager=cultural_manager)
app.add_middleware(AIContextMiddleware, ai_context_manager=ai_context_manager)
app.add_middleware(VoiceRoutingMiddleware, voice_router=voice_router)


# V3 Enhanced Health Endpoints
@app.get("/api/v3/health/enhanced")
async def enhanced_health_check():
    """Enhanced health check with V3 features"""
    try:
        return {
            "status": "healthy",
            "version": "3.0.0-enhanced",
            "timestamp": time.time(),
            "features": {
                "voice_routing": await voice_router.health_check(),
                "ai_context": await ai_context_manager.health_check(),
                "cultural_intelligence": await cultural_manager.health_check(),
                "websocket": await websocket_manager.health_check(),
                "performance": await performance_monitor.health_check()
            },
            "services": await health_checker.gateway_health()
        }
    except Exception as e:
        logger.error("Enhanced health check failed", error=str(e))
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "version": "3.0.0-enhanced",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


@app.get("/health")
async def basic_health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": time.time()
    }


@app.get("/health/live")
async def liveness_check():
    """Liveness check endpoint for Docker health checks"""
    return {
        "status": "alive",
        "service": "api-gateway",
        "timestamp": time.time()
    }


@app.get("/health/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return await health_checker.readiness_check()


@app.get("/api/v3/health/voice")
async def voice_system_health():
    """Voice system specific health check"""
    return await voice_router.detailed_health_check()


@app.get("/api/v3/health/ai-context")
async def ai_context_health():
    """AI context system health check"""
    return await ai_context_manager.detailed_health_check()


@app.get("/api/v3/health/cultural")
async def cultural_system_health():
    """Cultural intelligence system health check"""
    return await cultural_manager.detailed_health_check()


# V3 Enhanced Voice Command Endpoints
@app.post("/api/v3/voice/command", response_model=VoiceResponse)
async def process_voice_command(
    voice_command: VoiceCommand,
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Process voice command with V3 enhanced routing"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        "Processing voice command",
        request_id=request_id,
        intent=voice_command.intent,
        language=voice_command.language,
        cultural_context=voice_command.cultural_context
    )
    
    try:
        # Authenticate request if credentials provided
        user_context = None
        if credentials:
            user_context = await authenticate_user(credentials)
        
        # Detect language if not provided
        if not voice_command.language:
            voice_command.language = await language_detector.detect(voice_command.text)
        
        # Route voice command
        routing_result = await voice_router.route_command(voice_command, user_context)
        
        # Inject AI context
        ai_context = await ai_context_manager.get_context(user_context, voice_command)
        
        # Apply cultural adaptations
        cultural_context = await cultural_manager.adapt_context(
            voice_command.cultural_context,
            voice_command.language,
            user_context
        )
        
        # Execute the routed request
        enhanced_request = ProxyRequest(
            method=routing_result.method,
            path=routing_result.target_endpoint,
            headers={
                **routing_result.headers,
                "X-Request-ID": request_id,
                "X-Voice-Intent": voice_command.intent,
                "X-AI-Context": ai_context.to_header() if ai_context else "",
                "X-Cultural-Context": cultural_context.to_header() if cultural_context else "",
                "X-Language": voice_command.language
            },
            body=routing_result.body,
            query_params=routing_result.query_params
        )
        
        # Proxy request to target service
        service_response = await request_proxy.proxy_request(
            enhanced_request,
            routing_result.target_service
        )
        
        # Enhance response with cultural adaptation
        enhanced_response = await cultural_manager.adapt_response(
            service_response,
            cultural_context,
            voice_command.language
        )
        
        processing_time = (time.time() - start_time) * 1000
        
        # Record metrics
        await performance_monitor.record_voice_command(
            intent=voice_command.intent,
            language=voice_command.language,
            processing_time=processing_time,
            success=True
        )
        
        return VoiceResponse(
            request_id=request_id,
            status="success",
            response=enhanced_response,
            processing_time_ms=round(processing_time, 2),
            routing_info=routing_result,
            ai_context=ai_context,
            cultural_context=cultural_context
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        # Record error metrics
        await performance_monitor.record_voice_command(
            intent=voice_command.intent if hasattr(voice_command, 'intent') else "unknown",
            language=voice_command.language if hasattr(voice_command, 'language') else "unknown",
            processing_time=processing_time,
            success=False,
            error=str(e)
        )
        
        logger.exception(
            "Voice command processing failed",
            request_id=request_id,
            error=str(e),
            processing_time=processing_time
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "error": "Voice command processing failed",
                "message": str(e)
            }
        )


# V3 Enhanced WebSocket Endpoint for Real-time Voice Streaming
@app.websocket("/api/v3/voice/stream")
async def voice_streaming_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time voice streaming"""
    connection_id = str(uuid.uuid4())
    await websocket.accept()
    
    logger.info("Voice streaming connection established", connection_id=connection_id)
    
    try:
        # Register connection with WebSocket manager
        await websocket_manager.register_connection(connection_id, websocket)
        
        # Handle voice streaming
        async for message in websocket.iter_text():
            await websocket_manager.handle_voice_stream(connection_id, message)
            
    except WebSocketDisconnect:
        logger.info("Voice streaming connection closed", connection_id=connection_id)
    except Exception as e:
        logger.exception("Voice streaming error", connection_id=connection_id, error=str(e))
    finally:
        await websocket_manager.unregister_connection(connection_id)


# V3 Enhanced Metrics Endpoints
@app.get("/api/v3/metrics/performance")
async def performance_metrics():
    """Get performance metrics for V3 enhanced features"""
    return await performance_monitor.get_metrics()


@app.get("/api/v3/metrics/voice")
async def voice_metrics():
    """Get voice command processing metrics"""
    return await performance_monitor.get_voice_metrics()


@app.get("/api/v3/metrics/cultural")
async def cultural_metrics():
    """Get cultural adaptation metrics"""
    return await performance_monitor.get_cultural_metrics()


# Enhanced Service Proxy with V3 Features
@app.api_route(
    "/api/v3/service/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
)
async def enhanced_service_proxy(
    service_name: str,
    path: str,
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Enhanced service proxy with V3 features"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        "Enhanced service proxy request",
        request_id=request_id,
        service=service_name,
        path=path,
        method=request.method
    )
    
    try:
        # Rate limiting
        client_id = get_client_identifier(dict(request.headers))
        if not rate_limiter.is_allowed(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Authentication if credentials provided
        user_context = None
        if credentials:
            user_context = await authenticate_user(credentials)
        
        # Get AI context
        ai_context = await ai_context_manager.get_context(user_context)
        
        # Get cultural context from request headers or user profile
        cultural_context = await cultural_manager.get_context_from_request(request, user_context)
        
        # Create enhanced proxy request
        body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
        
        enhanced_request = ProxyRequest(
            method=HTTPMethod(request.method),
            path=f"/{path}",
            headers={
                **dict(request.headers),
                "X-Request-ID": request_id,
                "X-AI-Context": ai_context.to_header() if ai_context else "",
                "X-Cultural-Context": cultural_context.to_header() if cultural_context else ""
            },
            body=body,
            query_params=dict(request.query_params)
        )
        
        # Circuit breaker check
        if not circuit_breaker.is_call_allowed(service_name):
            raise HTTPException(status_code=503, detail=f"Service {service_name} is currently unavailable")
        
        # Proxy request
        try:
            response = await request_proxy.proxy_request(enhanced_request, service_name)
            circuit_breaker.record_success(service_name)
            
            # Apply cultural adaptation to response
            enhanced_response = await cultural_manager.adapt_response(
                response,
                cultural_context
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            # Record metrics
            await performance_monitor.record_service_request(
                service=service_name,
                path=path,
                method=request.method,
                processing_time=processing_time,
                success=True
            )
            
            return enhanced_response
            
        except Exception as e:
            circuit_breaker.record_failure(service_name)
            raise e
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        # Record error metrics
        await performance_monitor.record_service_request(
            service=service_name,
            path=path,
            method=request.method,
            processing_time=processing_time,
            success=False,
            error=str(e)
        )
        
        logger.exception(
            "Enhanced service proxy failed",
            request_id=request_id,
            service=service_name,
            path=path,
            error=str(e)
        )
        
        if isinstance(e, HTTPException):
            raise e
        else:
            raise HTTPException(status_code=500, detail=str(e))


async def authenticate_user(credentials: HTTPAuthorizationCredentials) -> Optional[Dict[str, Any]]:
    """Authenticate user and return user context"""
    try:
        # Import auth utilities
        import sys
        sys.path.append('/app/shared')
        from shared.auth import verify_token
        
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "user"),
            "preferences": {},
            "cultural_profile": {}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Generic request router for all non-V3 endpoints
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def route_request(
    path: str, 
    request: Request, 
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """Route requests using the RequestRouter"""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    logger.info(
        "Routing request",
        request_id=request_id,
        path=f"/{path}",
        method=request.method
    )
    
    try:
        # Skip V3 API routes that are handled elsewhere
        if path.startswith("api/v3"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Find route using RequestRouter
        route = request_router.find_route(f"/{path}", request.method)
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Rate limiting
        client_id = get_client_identifier(dict(request.headers))
        if not rate_limiter.is_allowed(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Authentication if required by route
        user_context = None
        if route.auth_required:
            if not credentials:
                raise HTTPException(status_code=401, detail="Authentication required")
            user_context = await authenticate_user(credentials)
        elif credentials:
            # Optional auth - try to authenticate if provided
            try:
                user_context = await authenticate_user(credentials)
            except:
                pass  # Continue without auth if optional
        
        # Get AI context
        ai_context = await ai_context_manager.get_context(user_context) if user_context else None
        
        # Get cultural context from request headers or user profile
        cultural_context = await cultural_manager.get_context_from_request(request, user_context)
        
        # Create proxy request
        body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
        
        # Handle prefix stripping if configured
        target_path = f"/{path}"
        if route.strip_prefix and route.path_pattern:
            # Extract the prefix from the pattern (e.g., "^/voice/.*" -> "/voice", "^/auth/.*" -> "/auth")
            import re
            pattern_match = re.match(r'\^/([^/]+)', route.path_pattern)
            if pattern_match:
                prefix = f"/{pattern_match.group(1)}"
                if target_path.startswith(prefix):
                    target_path = target_path[len(prefix):]
                    if not target_path.startswith('/'):
                        target_path = f"/{target_path}"
        
        proxy_request = ProxyRequest(
            method=HTTPMethod(request.method),
            path=target_path,
            headers={
                **dict(request.headers),
                "X-Request-ID": request_id,
                "X-AI-Context": ai_context.to_header() if ai_context else "",
                "X-Cultural-Context": cultural_context.to_header() if cultural_context else ""
            },
            body=body,
            query_params=dict(request.query_params)
        )
        
        # Circuit breaker check
        service_name = route.service_name
        if not circuit_breaker.is_call_allowed(service_name):
            raise HTTPException(status_code=503, detail=f"Service {service_name} is currently unavailable")
        
        # Get healthy service instances
        healthy_instances = service_registry.get_healthy_services(service_name)
        if not healthy_instances:
            raise HTTPException(status_code=503, detail=f"No healthy instances of service {service_name}")
        
        # Use load balancer to select an instance
        target_service = load_balancer.select_instance(healthy_instances)
        if not target_service:
            raise HTTPException(status_code=503, detail=f"Failed to select service instance for {service_name}")
        
        # Proxy request to target service
        try:
            response = await request_proxy.proxy_request(proxy_request, target_service)
            circuit_breaker.record_success(service_name)
            
            # Apply cultural adaptation to response
            enhanced_response = await cultural_manager.adapt_response(
                response,
                cultural_context
            ) if cultural_context else response
            
            processing_time = (time.time() - start_time) * 1000
            
            # Record metrics
            await performance_monitor.record_service_request(
                service=service_name,
                path=f"/{path}",
                method=request.method,
                processing_time=processing_time,
                success=True
            )
            
            return enhanced_response
            
        except Exception as e:
            circuit_breaker.record_failure(service_name)
            raise e
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        # Record error metrics
        await performance_monitor.record_service_request(
            service=route.service_name if 'route' in locals() else "unknown",
            path=f"/{path}",
            method=request.method,
            processing_time=processing_time,
            success=False,
            error=str(e)
        )
        
        logger.exception(
            "Request routing failed",
            request_id=request_id,
            path=f"/{path}",
            error=str(e)
        )
        
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_v3_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )
