"""
Health API endpoints
Provides health check and monitoring endpoints for the AI Context Store service
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Global references to services (will be injected)
context_aggregator_service = None
intelligence_engine = None
event_processor = None

def set_services(aggregator, engine, processor):
    """Set service references"""
    global context_aggregator_service, intelligence_engine, event_processor
    context_aggregator_service = aggregator
    intelligence_engine = engine
    event_processor = processor

@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "ai_context_store",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with service status
    """
    try:
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "ai_context_store",
            "version": "1.0.0",
            "components": {}
        }
        
        # Check context aggregator
        if context_aggregator_service:
            try:
                aggregator_metrics = await context_aggregator_service.get_metrics()
                health_status["components"]["context_aggregator"] = {
                    "status": "healthy",
                    "metrics": aggregator_metrics
                }
            except Exception as e:
                health_status["components"]["context_aggregator"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"
        else:
            health_status["components"]["context_aggregator"] = {
                "status": "unavailable"
            }
            health_status["overall_status"] = "degraded"
        
        # Check intelligence engine
        if intelligence_engine:
            try:
                engine_metrics = await intelligence_engine.get_metrics()
                health_status["components"]["intelligence_engine"] = {
                    "status": "healthy",
                    "metrics": engine_metrics
                }
            except Exception as e:
                health_status["components"]["intelligence_engine"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"
        else:
            health_status["components"]["intelligence_engine"] = {
                "status": "unavailable"
            }
            health_status["overall_status"] = "degraded"
        
        # Check event processor
        if event_processor:
            try:
                processor_metrics = await event_processor.get_metrics()
                health_status["components"]["event_processor"] = {
                    "status": "healthy",
                    "metrics": processor_metrics
                }
            except Exception as e:
                health_status["components"]["event_processor"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"
        else:
            health_status["components"]["event_processor"] = {
                "status": "unavailable"
            }
            health_status["overall_status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Error in detailed health check: {e}")
        return {
            "overall_status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@router.get("/health/metrics")
async def get_all_metrics():
    """
    Get comprehensive metrics from all services
    """
    try:
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "ai_context_store"
        }
        
        if context_aggregator_service:
            metrics["context_aggregator"] = await context_aggregator_service.get_metrics()
        
        if intelligence_engine:
            metrics["intelligence_engine"] = await intelligence_engine.get_metrics()
        
        if event_processor:
            metrics["event_processor"] = await event_processor.get_metrics()
        
        return metrics
        
    except Exception as e:
        logger.error(f"❌ Error getting all metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@router.get("/readiness")
async def readiness_check():
    """
    Readiness check - indicates if the service is ready to handle requests
    """
    try:
        ready = True
        issues = []
        
        # Check if core services are available and running
        if not context_aggregator_service:
            ready = False
            issues.append("Context aggregator service not available")
        
        if not intelligence_engine:
            ready = False
            issues.append("Intelligence engine not available")
        
        if not event_processor:
            ready = False
            issues.append("Event processor not available")
        
        # Check if event processor is running
        if event_processor:
            processor_metrics = await event_processor.get_metrics()
            if not processor_metrics.get("is_running", False):
                ready = False
                issues.append("Event processor not running")
        
        # Check if intelligence engine is running
        if intelligence_engine:
            engine_metrics = await intelligence_engine.get_metrics()
            if not engine_metrics.get("is_running", False):
                ready = False
                issues.append("Intelligence engine not running")
        
        return {
            "ready": ready,
            "status": "ready" if ready else "not_ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"❌ Error in readiness check: {e}")
        return {
            "ready": False,
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issues": [str(e)]
        }

@router.get("/liveness")
async def liveness_check():
    """
    Liveness check - indicates if the service is alive
    """
    return {
        "alive": True,
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime": "running"  # Could track actual uptime if needed
    }

@router.get("/dependencies")
async def dependencies_check():
    """
    Check external dependencies
    """
    try:
        dependencies = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dependencies": {}
        }
        
        # Check Redis connection
        if context_aggregator_service:
            aggregator_metrics = await context_aggregator_service.get_metrics()
            dependencies["dependencies"]["redis"] = {
                "status": "healthy" if aggregator_metrics.get("redis_connected", False) else "unavailable",
                "connected": aggregator_metrics.get("redis_connected", False)
            }
        
        # Check Event Bus
        if event_processor:
            processor_metrics = await event_processor.get_metrics()
            dependencies["dependencies"]["event_bus"] = {
                "status": "healthy" if processor_metrics.get("is_running", False) else "unhealthy",
                "subscriptions_active": processor_metrics.get("is_running", False)
            }
        
        return dependencies
        
    except Exception as e:
        logger.error(f"❌ Error checking dependencies: {e}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dependencies": {},
            "error": str(e)
        }
