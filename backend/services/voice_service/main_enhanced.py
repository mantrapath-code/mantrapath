"""
Voice Service Main Application
Clean, modular FastAPI application with comprehensive voice processing capabilities
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import core components
from app.core import (
    ModelsServiceClient,
    ConversationManager, 
    ContextProcessor,
    SessionManager,
    AudioCacheManager,
    LanguageDetector,
    VoiceEnhancer
)

# Import API routes
from app.api.voice_routes import router as voice_router
from app.api.conversation_routes import router as conversation_router
from app.api.session_routes import router as session_router
from app.api.health_routes import router as health_router

# Global components
components = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Voice Service v2.0.0")
    
    # Initialize core components
    try:
        components["models_client"] = ModelsServiceClient()
        components["conversation_manager"] = ConversationManager()
        components["context_processor"] = ContextProcessor()
        components["session_manager"] = SessionManager()
        components["audio_cache"] = AudioCacheManager()
        components["language_detector"] = LanguageDetector()
        components["voice_enhancer"] = VoiceEnhancer()
        
        # Test Models Service connection
        health = await components["models_client"].health_check()
        if health["status"] == "healthy":
            logger.info("✅ Models Service connection established")
        else:
            logger.warning("⚠️ Models Service connection degraded")
        
        # Test other components
        session_health = components["session_manager"].health_check()
        cache_health = components["audio_cache"].health_check()
        
        logger.info(f"✅ Session Manager: {session_health['storage_type']}")
        logger.info(f"✅ Audio Cache: {cache_health['storage_type']}")
        
        logger.info("🎤 Voice Service fully initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        # Continue startup but mark as degraded
    
    yield
    
    # Shutdown
    logger.info("Shutting down Voice Service")
    
    # Cleanup components
    try:
        if "audio_cache" in components:
            cleanup_count = components["audio_cache"].cleanup_expired_cache()
            logger.info(f"Cleaned up {cleanup_count} expired cache entries")
        
        if "session_manager" in components:
            expired_sessions = components["session_manager"].cleanup_expired_sessions()
            logger.info(f"Cleaned up {expired_sessions} expired sessions")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    
    logger.info("Voice Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Voice Service",
    description="MantraPath Voice Processing Service - Clean & Modular Implementation",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API routers
app.include_router(voice_router)
app.include_router(conversation_router)
app.include_router(session_router)
app.include_router(health_router)

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "voice_service",
        "version": "2.0.0",
        "description": "MantraPath Voice Processing Service",
        "status": "active",
        "features": [
            "speech_to_text",
            "text_to_speech",
            "conversation_management",
            "context_processing",
            "audio_enhancement",
            "language_detection",
            "session_management",
            "audio_caching",
            "indian_language_support"
        ],
        "endpoints": {
            "voice": "/api/v1/voice/",
            "conversation": "/api/v1/conversation/",
            "session": "/api/v1/session/",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        # Quick health check of critical components
        models_health = await components.get("models_client", {}).health_check() if "models_client" in components else {"status": "missing"}
        
        overall_status = "healthy"
        if models_health.get("status") != "healthy":
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "service": "voice_service",
            "version": "2.0.0",
            "timestamp": time.time(),
            "models_service": models_health.get("status", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "voice_service",
                "version": "2.0.0", 
                "error": str(e),
                "timestamp": time.time()
            }
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "service": "voice_service",
            "timestamp": time.time()
        }
    )

# Make components available to routes
def get_components():
    """Get initialized components"""
    return components

# Export app for uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("VOICE_SERVICE_PORT", 8011))
    host = os.getenv("VOICE_SERVICE_HOST", "0.0.0.0")
    
    logger.info(f"Starting Voice Service on {host}:{port}")
    uvicorn.run(
        "main_enhanced:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
