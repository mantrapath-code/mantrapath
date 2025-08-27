"""
Proactive Assistance Engine Service
Main entry point for the proactive assistance orchestration service.

This service coordinates existing AI capabilities into a cohesive proactive assistance system,
providing timely, contextually relevant, and culturally sensitive assistance.
Enhanced with Models Service integration for voice and multilingual support.
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import structlog
import sys
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Ensure backend root is on sys.path so `shared` package is importable
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from src.core.assistance_orchestrator import ProactiveAssistanceOrchestrator
# Use shared assistance models when available
try:
    from shared.models.assistance import AssistanceEvaluation, UserAssistanceNeeds
except Exception:
    from src.models.assistance_models import AssistanceEvaluation, UserAssistanceNeeds

logger = structlog.get_logger(__name__)

# Global orchestrator
assistance_orchestrator: ProactiveAssistanceOrchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global assistance_orchestrator
    
    logger.info("Starting Proactive Assistance Engine")
    
    try:
        # Initialize orchestrator with existing service integrations
        assistance_orchestrator = ProactiveAssistanceOrchestrator()
        await assistance_orchestrator.initialize()
        
        logger.info("Proactive Assistance Engine started successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to start Proactive Assistance Engine", error=str(e))
        raise
    finally:
        if assistance_orchestrator:
            await assistance_orchestrator.cleanup()

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Proactive Assistance Engine",
        description="Real-time proactive assistance orchestration for MantraPath V3",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        health_status = await assistance_orchestrator.get_health_status()
        return health_status
    
    @app.get("/health/live")
    async def liveness_check():
        """Kubernetes liveness probe"""
        return {"status": "alive"}
    
    @app.get("/health/ready")
    async def readiness_check():
        """Kubernetes readiness probe"""
        if not assistance_orchestrator or not assistance_orchestrator.is_initialized:
            raise HTTPException(status_code=503, detail="Service not ready")
        return {"status": "ready"}
    
    @app.post("/api/v1/assistance/evaluate/{user_id}")
    async def evaluate_assistance_needs(user_id: str):
        """Evaluate and potentially trigger proactive assistance for user"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        assistance_evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        return assistance_evaluation
    
    @app.get("/api/v1/assistance/status/{user_id}")
    async def get_assistance_status(user_id: str):
        """Get current assistance status for user"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        status = await assistance_orchestrator.get_user_assistance_status(user_id)
        return status
    
    @app.post("/api/v1/assistance/trigger/{user_id}")
    async def trigger_assistance(user_id: str, background_tasks: BackgroundTasks):
        """Manually trigger proactive assistance for user"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Process assistance trigger asynchronously
        background_tasks.add_task(
            assistance_orchestrator.trigger_assistance,
            user_id
        )
        
        return {"status": "accepted", "message": "Assistance trigger queued"}
    
    @app.get("/api/v1/integrations/status")
    async def get_integrations_status():
        """Check status of all integrated services"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        integration_status = await assistance_orchestrator.get_integration_status()
        return integration_status
    
    @app.get("/metrics")
    async def metrics_prometheus():
        """Prometheus metrics endpoint"""
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    @app.get("/api/v1/metrics")
    async def get_metrics():
        """Get service performance metrics"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        metrics = await assistance_orchestrator.get_metrics()
        return metrics
    
    # NEW - Voice Assistance Endpoints (BK-008 Integration)
    @app.post("/api/v1/assistance/voice/{user_id}")
    async def process_voice_assistance_request(
        user_id: str,
        audio: UploadFile = File(...),
        language: str = Form("auto"),
        cultural_profile: str = Form("neutral")
    ):
        """Process voice assistance request with full AI pipeline"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        if not assistance_orchestrator.models_service_client:
            raise HTTPException(status_code=503, detail="Models Service not available")
        
        try:
            # Read audio data
            audio_data = await audio.read()
            
            # Prepare context
            context = {
                "user_id": user_id,
                "preferred_language": language,
                "cultural_profile": cultural_profile
            }
            
            # Process voice request
            result = await assistance_orchestrator.models_service_client.process_voice_assistance_request(
                audio_data, user_id, context
            )
            
            return {
                "status": "success",
                "user_id": user_id,
                "analysis": result,
                "timestamp": "2025-08-17T00:00:00Z"  # Would use actual timestamp
            }
            
        except Exception as e:
            logger.error("Voice assistance processing failed", user_id=user_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")
    
    @app.post("/api/v1/assistance/multilingual-response")
    async def generate_multilingual_response(
        request_data: Dict[str, Any]
    ):
        """Generate culturally appropriate multilingual assistance response"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        if not assistance_orchestrator.models_service_client:
            raise HTTPException(status_code=503, detail="Models Service not available")
        
        try:
            response_text = request_data.get("response_text", "")
            target_language = request_data.get("target_language", "en")
            user_context = request_data.get("user_context", {})
            voice_enabled = request_data.get("voice_enabled", True)
            
            if not response_text:
                raise HTTPException(status_code=400, detail="response_text is required")
            
            result = await assistance_orchestrator.models_service_client.generate_multilingual_response(
                response_text, target_language, user_context, voice_enabled
            )
            
            return {
                "status": "success",
                "response": result,
                "timestamp": "2025-08-17T00:00:00Z"
            }
            
        except Exception as e:
            logger.error("Multilingual response generation failed", error=str(e))
            raise HTTPException(status_code=500, detail=f"Response generation failed: {str(e)}")
    
    @app.get("/api/v1/assistance/voice/audio/{response_id}")
    async def get_voice_response_audio(response_id: str):
        """Retrieve audio response for a previously generated multilingual response"""
        # This would typically retrieve cached audio from storage
        # For now, return a placeholder response
        raise HTTPException(status_code=501, detail="Audio retrieval not yet implemented")
    
    @app.post("/api/v1/assistance/sentiment-analysis")
    async def analyze_user_content_sentiment(
        request_data: Dict[str, Any]
    ):
        """Analyze sentiment trends from user's recent content"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        if not assistance_orchestrator.models_service_client:
            raise HTTPException(status_code=503, detail="Models Service not available")
        
        try:
            content_history = request_data.get("content_history", [])
            user_context = request_data.get("user_context", {})
            
            if not content_history:
                raise HTTPException(status_code=400, detail="content_history is required")
            
            result = await assistance_orchestrator.models_service_client.analyze_user_content_sentiment(
                content_history, user_context
            )
            
            return {
                "status": "success",
                "sentiment_analysis": result,
                "timestamp": "2025-08-17T00:00:00Z"
            }
            
        except Exception as e:
            logger.error("Sentiment analysis failed", error=str(e))
            raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")
    
    @app.get("/api/v1/models/status")
    async def get_models_service_status():
        """Get Models Service status and capabilities"""
        if assistance_orchestrator is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        if not assistance_orchestrator.models_service_client:
            raise HTTPException(status_code=503, detail="Models Service not available")
        
        try:
            # Check Models Service health
            is_healthy = await assistance_orchestrator.models_service_client.check_health()
            
            return {
                "models_service_healthy": is_healthy,
                "integration_enabled": True,
                "capabilities": ["stt", "tts", "nlp", "translation", "sentiment_analysis"],
                "timestamp": "2025-08-17T00:00:00Z"
            }
            
        except Exception as e:
            logger.error("Models Service status check failed", error=str(e))
            return {
                "models_service_healthy": False,
                "integration_enabled": False,
                "error": str(e),
                "timestamp": "2025-08-17T00:00:00Z"
            }
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PROACTIVE_ASSISTANCE_PORT", 8018))
    host = os.getenv("PROACTIVE_ASSISTANCE_HOST", "0.0.0.0")
    
    logger.info(f"Starting Proactive Assistance Engine on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
