"""Health check and service info endpoints."""

import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis

from src.core.config import settings
from src.models.schemas import HealthResponse, ServiceInfo
from shared.database import engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancer.
    
    Checks database, redis, and AI model availability.
    """
    try:
        dependencies = {}
        overall_status = "healthy"
        
        # Check database
        try:
            # Use the imported engine directly
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            dependencies["database"] = "healthy"
        except Exception as e:
            dependencies["database"] = f"unhealthy: {str(e)}"
            overall_status = "degraded"
        
        # Check Redis
        try:
            redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            redis_client.ping()
            dependencies["redis"] = "healthy"
        except Exception as e:
            dependencies["redis"] = f"unhealthy: {str(e)}"
            overall_status = "degraded"
        
        # Check AI model (emotion analysis service)
        try:
            from src.services.emotion_analysis import emotion_service
            model_status = emotion_service.get_health_status()
            status = model_status["status"]
            message = model_status["message"]
            
            if status == "healthy":
                dependencies["emotion_model"] = "healthy"
            elif status == "ready":
                dependencies["emotion_model"] = f"ready: {message}"
                # Don't mark as degraded for lazy loading
            elif status == "disabled":
                dependencies["emotion_model"] = f"disabled: {message}"
                # Don't mark as degraded if intentionally disabled
            else:
                dependencies["emotion_model"] = f"degraded: {message}"
                overall_status = "degraded"
        except Exception as e:
            dependencies["emotion_model"] = f"unhealthy: {str(e)}"
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version=settings.version,
            dependencies=dependencies
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/info", response_model=ServiceInfo)
async def get_service_info():
    """
    Get service information and capabilities.
    """
    try:
        endpoints = [
            "/api/v1/mood/entries",
            "/api/v1/mood/analytics/overview",
            "/api/v1/mood/analytics/patterns",
            "/api/v1/mood/analyze",
            "/api/v1/mood/context",
            "/api/v1/health",
            "/api/v1/info"
        ]
        
        features = {
            "emotion_detection": settings.enable_emotion_detection,
            "sentiment_analysis": settings.enable_sentiment_analysis,
            "mood_patterns": settings.enable_mood_patterns,
            "memory_integration": bool(settings.memory_service_url),
            "chatbot_integration": bool(settings.chatbot_service_url),
            "batch_processing": settings.batch_processing_enabled
        }
        
        return ServiceInfo(
            name=settings.service_name,
            version=settings.version,
            description="AI-powered emotion detection and mood tracking service",
            endpoints=endpoints,
            features=features
        )
        
    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service info")


@router.get("/metrics")
async def get_metrics():
    """
    Get basic service metrics.
    """
    try:
        # This could be expanded with proper metrics collection
        metrics = {
            "service": settings.service_name,
            "version": settings.version,
            "uptime": "available_via_health_check",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")