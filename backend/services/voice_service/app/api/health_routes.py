"""
Health Check Routes
Comprehensive health monitoring and diagnostics
"""
import logging
import time
from typing import Dict, Any
from fastapi import APIRouter
from datetime import datetime

from ..core.models_client import ModelsServiceClient
from ..core.session_manager import SessionManager
from ..core.audio_cache_manager import AudioCacheManager
from ..core.voice_enhancer import VoiceEnhancer
from ..core.language_detector import LanguageDetector
from ..models.responses import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Initialize components for health checks
models_client = ModelsServiceClient()
session_manager = SessionManager()
audio_cache = AudioCacheManager()
voice_enhancer = VoiceEnhancer()
language_detector = LanguageDetector()

@router.get("/", response_model=HealthResponse)
async def comprehensive_health_check():
    """Comprehensive health check of all components"""
    try:
        start_time = time.time()
        
        # Check all components
        models_health = await models_client.health_check(use_cache=False)
        session_health = session_manager.health_check()
        cache_health = audio_cache.health_check()
        enhancer_health = voice_enhancer.health_check()
        detector_health = language_detector.health_check()
        
        # Determine overall status
        component_statuses: Dict[str, bool] = {
            "models_service": models_health.get("status") == "healthy",
            "session_manager": session_health.get("status") == "healthy",
            "audio_cache": cache_health.get("status") in ["healthy", "degraded"],
            "voice_enhancer": enhancer_health.get("status") == "healthy",
            "language_detector": detector_health.get("status") == "healthy"
        }
        
        overall_status = "healthy"
        if not component_statuses["models_service"]:
            overall_status = "unhealthy"  # Models service is critical
        elif not all(component_statuses.values()):
            overall_status = "degraded"
        
        # Gather dependency information
        dependencies = {
            "redis": session_health.get("redis_connection", "unknown"),
            "models_service": models_health.get("connection", "unknown"),
            "numpy": enhancer_health.get("dependencies", {}).get("numpy", "unknown"),
            "librosa": enhancer_health.get("dependencies", {}).get("librosa", "unknown"),
            "scipy": enhancer_health.get("dependencies", {}).get("scipy", "unknown")
        }
        
        processing_time = time.time() - start_time
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            version="2.0.0",
            components={
                "models_service": models_health,
                "session_manager": session_health,
                "audio_cache": cache_health,
                "voice_enhancer": enhancer_health,
                "language_detector": detector_health,
                "component_statuses": component_statuses,
                "health_check_time": processing_time
            },
            dependencies=dependencies
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="error",
            timestamp=datetime.now(),
            version="2.0.0",
            components={"error": str(e)},
            dependencies={}
        )

@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Simple liveness check for container orchestration"""
    return {
        "status": "alive",
        "service": "voice_service",
        "timestamp": time.time()
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for container orchestration"""
    try:
        # Quick check of critical components
        models_health = await models_client.health_check(use_cache=True)
        
        if models_health.get("status") == "healthy":
            return {
                "status": "ready",
                "service": "voice_service",
                "timestamp": time.time()
            }
        else:
            return {
                "status": "not_ready",
                "service": "voice_service",
                "reason": "models_service_unavailable",
                "timestamp": time.time()
            }
            
    except Exception as e:
        return {
            "status": "not_ready",
            "service": "voice_service",
            "reason": str(e),
            "timestamp": time.time()
        }

@router.get("/components")
async def component_health() -> Dict[str, Any]:
    """Individual component health status"""
    try:
        components: Dict[str, Any] = {}
        
        # Models Service
        try:
            models_health = await models_client.health_check(use_cache=False)
            components["models_service"] = models_health
        except Exception as e:
            components["models_service"] = {"status": "error", "error": str(e)}
        
        # Session Manager
        try:
            session_health = session_manager.health_check()
            components["session_manager"] = session_health
        except Exception as e:
            components["session_manager"] = {"status": "error", "error": str(e)}
        
        # Audio Cache
        try:
            cache_health = audio_cache.health_check()
            components["audio_cache"] = cache_health
        except Exception as e:
            components["audio_cache"] = {"status": "error", "error": str(e)}
        
        # Voice Enhancer
        try:
            enhancer_health = voice_enhancer.health_check()
            components["voice_enhancer"] = enhancer_health
        except Exception as e:
            components["voice_enhancer"] = {"status": "error", "error": str(e)}
        
        # Language Detector
        try:
            detector_health = language_detector.health_check()
            components["language_detector"] = detector_health
        except Exception as e:
            components["language_detector"] = {"status": "error", "error": str(e)}
        
        return {
            "timestamp": datetime.now().isoformat(),
            "components": components
        }
        
    except Exception as e:
        logger.error(f"Component health check failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "components": {}
        }

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get service metrics and statistics"""
    try:
        # Session metrics
        session_stats = session_manager.get_session_stats()
        
        # Cache metrics
        cache_stats = audio_cache.get_cache_stats()
        
        # Models service metrics
        models_health = await models_client.health_check(use_cache=True)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "sessions": session_stats,
                "cache": cache_stats,
                "models_service": {
                    "status": models_health.get("status"),
                    "response_time": models_health.get("response_time_ms", 0)
                }
            },
            "uptime": time.time(),  # Simplified uptime
            "version": "2.0.0"
        }
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "metrics": {}
        }

@router.get("/dependencies")
async def check_dependencies() -> Dict[str, Any]:
    """Check external dependencies"""
    try:
        dependencies: Dict[str, Any] = {}
        
        # Models Service
        models_health = await models_client.health_check(use_cache=False)
        dependencies["models_service"] = {
            "status": models_health.get("status"),
            "connection": models_health.get("connection"),
            "required": True
        }
        
        # Redis (via session manager)
        session_health = session_manager.health_check()
        dependencies["redis"] = {
            "status": "available" if session_health.get("redis_connection") == "active" else "unavailable",
            "connection": session_health.get("redis_connection"),
            "required": False,
            "fallback": "in-memory storage"
        }
        
        # Python packages
        enhancer_deps = voice_enhancer.health_check().get("dependencies", {})
        dependencies["python_packages"] = {
            "numpy": {"status": enhancer_deps.get("numpy"), "required": True},
            "librosa": {"status": enhancer_deps.get("librosa"), "required": False},
            "scipy": {"status": enhancer_deps.get("scipy"), "required": False}
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "dependencies": dependencies
        }
        
    except Exception as e:
        logger.error(f"Dependency check failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "dependencies": {}
        }
