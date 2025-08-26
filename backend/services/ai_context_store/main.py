"""
AI Context Store Service
Aggregates and stores user context from all services for intelligent cross-service communication.

Features:
- Real-time event aggregation from all 7 services
- Contextual user profile building
- Cross-service intelligence and recommendations
- Event-driven context updates
- Historical context analysis
- Redis caching for performance
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
import os
import logging
import uuid
import json
import asyncio
import sys

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(os.path.dirname(current_dir))

sys.path.insert(0, backend_root)
sys.path.insert(0, current_dir)
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, SessionLocal
from shared.auth import get_current_user
from shared.models import User
from shared.redis_client import redis_client
from shared.events.enhanced_bus import get_enhanced_event_bus

# Import AI Context Store components (available at startup)
import importlib.util
import importlib

# Function to dynamically import modules
def import_module_from_path(module_name, file_path):
    """Import a module from a specific file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import context models directly
context_models_path = os.path.join(current_dir, 'models', 'context_models.py')
context_models = import_module_from_path('context_models', context_models_path)

# Extract classes from context_models
UserContext = context_models.UserContext
ContextEntry = context_models.ContextEntry
ContextAggregator = context_models.ContextAggregator
MoodContext = context_models.MoodContext
CommunityContext = context_models.CommunityContext
VoiceContext = context_models.VoiceContext
TranslationContext = context_models.TranslationContext
ContentContext = context_models.ContentContext
NotificationContext = context_models.NotificationContext

# Import services directly
context_aggregator_path = os.path.join(current_dir, 'services', 'context_aggregator.py')
context_aggregator = import_module_from_path('context_aggregator', context_aggregator_path)
ContextAggregatorService = context_aggregator.ContextAggregatorService

intelligence_engine_path = os.path.join(current_dir, 'services', 'intelligence_engine.py')
intelligence_engine = import_module_from_path('intelligence_engine', intelligence_engine_path)
IntelligenceEngine = intelligence_engine.IntelligenceEngine

event_processor_path = os.path.join(current_dir, 'services', 'event_processor.py')
event_processor = import_module_from_path('event_processor', event_processor_path)
EventProcessor = event_processor.EventProcessor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
context_aggregator_service: Optional[Any] = None
intelligence_engine: Optional[Any] = None
event_processor: Optional[Any] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global context_aggregator_service, intelligence_engine, event_processor
    
    logger.info("🚀 Starting AI Context Store Service...")
    
    # Initialize event_bus variable
    event_bus = None
    
    try:
        # Initialize event bus
        event_bus = get_enhanced_event_bus()
        await event_bus.initialize()
        logger.info("✅ Event bus initialized")
        
        # Initialize core services
        context_aggregator_service = ContextAggregatorService()
        await context_aggregator_service.initialize()
        
        intelligence_engine = IntelligenceEngine()
        event_processor = EventProcessor(context_aggregator_service, intelligence_engine)
        
        # Inject services into API modules
        from api import context_api, intelligence_api, health_api
        context_api.set_services(context_aggregator_service, intelligence_engine)
        intelligence_api.set_services(context_aggregator_service, intelligence_engine)
        health_api.set_services(context_aggregator_service, intelligence_engine, event_processor)
        
        # Include API routes
        from api.context_api import router as context_router
        from api.intelligence_api import router as intelligence_router
        from api.health_api import router as health_router
        
        app.include_router(context_router, prefix="/api/v1/context", tags=["Context"])
        app.include_router(intelligence_router, prefix="/api/v1/intelligence", tags=["Intelligence"])
        app.include_router(health_router, tags=["Health"])  # No prefix, routes defined in router
        
        # Start event subscriptions
        await event_processor.start_subscriptions()
        logger.info("✅ Event subscriptions started")
        
        # Start background tasks
        asyncio.create_task(context_aggregator_service.start_periodic_aggregation())
        asyncio.create_task(intelligence_engine.start_intelligence_processing())
        
        logger.info("🎯 AI Context Store Service fully operational!")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start AI Context Store Service: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🔄 Shutting down AI Context Store Service...")
        if event_processor:
            await event_processor.stop_subscriptions()
        if context_aggregator_service:
            await context_aggregator_service.stop()
        if intelligence_engine:
            await intelligence_engine.stop()
        
        # Cleanup event bus
        if event_bus:
            await event_bus.close()
        logger.info("✅ AI Context Store Service shut down complete")

app = FastAPI(
    title="MantraPath AI Context Store",
    description="Intelligent context aggregation and cross-service intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes - will be imported dynamically in lifespan

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MantraPath AI Context Store",
        "version": "1.0.0",
        "status": "operational",
        "description": "Intelligent context aggregation and cross-service intelligence",
        "endpoints": {
            "context": "/api/v1/context",
            "intelligence": "/api/v1/intelligence",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global context_aggregator_service, intelligence_engine, event_processor
    
    try:
        status = "healthy"
        services = {}
        
        if context_aggregator_service:
            services["context_aggregator"] = "healthy"
        else:
            services["context_aggregator"] = "not_initialized"
            status = "degraded"
            
        if intelligence_engine:
            services["intelligence_engine"] = "healthy"
        else:
            services["intelligence_engine"] = "not_initialized"
            
        if event_processor:
            services["event_processor"] = "healthy"
        else:
            services["event_processor"] = "not_initialized"
        
        return {
            "status": status,
            "service": "ai_context_store",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "services": services
        }
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "ai_context_store",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

@app.get("/api/v1/context/user/{user_id}")
async def get_user_context(
    user_id: str, 
    request: Request,
    current_user: User = Depends(get_current_user),
    refresh_data: bool = False
):
    """Get comprehensive user context"""
    try:
        # Verify user access - handle both dictionary and object current_user
        if hasattr(current_user, 'id'):
            current_user_id = str(current_user.id)
            user_role = getattr(current_user, 'role', 'user')
        elif isinstance(current_user, dict):
            current_user_id = str(current_user.get('user_id', current_user.get('sub', '')))
            user_role = current_user.get('role', 'user')
        else:
            current_user_id = str(current_user)
            user_role = 'user'
        
        if current_user_id != str(user_id) and user_role != "admin":
            logger.warning(f"Authorization failed: current_user_id={current_user_id}, requested_user_id={user_id}, role={user_role}")
            raise HTTPException(status_code=403, detail="Not authorized to access this user's context")
        
        # If refresh requested, collect fresh data
        if refresh_data and context_aggregator_service:
            # Extract JWT token from request headers
            from fastapi import Request
            request = Request
            auth_header = request.headers.get("authorization", "")
            jwt_token = auth_header.replace("Bearer ", "") if auth_header.startswith("Bearer ") else ""
            
            if jwt_token:
                context = await context_aggregator_service.collect_comprehensive_user_data(
                    user_id, 
                    jwt_token
                )
            else:
                context = await context_aggregator_service.get_user_context(user_id)
        else:
            context = await context_aggregator_service.get_user_context(user_id) if context_aggregator_service else None
        
        if not context:
            return {"user_id": user_id, "context": None, "message": "No context found"}
            
        return context.model_dump()
        
    except Exception as e:
        logger.error(f"Error getting user context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/context/user/{user_id}/refresh")
async def refresh_user_context(
    user_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Trigger comprehensive data collection for user context"""
    try:
        # Verify user access
        if current_user.id != user_id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to refresh this user's context")
        
        if not context_aggregator_service:
            raise HTTPException(status_code=503, detail="Context aggregator service not available")
        
        # Add to background tasks to avoid blocking
        background_tasks.add_task(
            trigger_context_refresh,
            user_id
        )
        
        return {
            "status": "context_refresh_triggered",
            "user_id": user_id,
            "message": "Context refresh started in background"
        }
        
    except Exception as e:
        logger.error(f"Error triggering context refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def trigger_context_refresh(user_id: str):
    """Background task to refresh user context"""
    try:
        if context_aggregator_service:
            # For now, we'll collect context without JWT token
            # In production, this should be enhanced to get proper auth
            await context_aggregator_service.get_user_context(user_id)
            logger.info(f"✅ Context refresh completed for user {user_id}")
        else:
            logger.warning(f"Cannot refresh context for user {user_id} - service not available")
    except Exception as e:
        logger.error(f"Background context refresh failed for user {user_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AI_CONTEXT_STORE_PORT", 8013))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
