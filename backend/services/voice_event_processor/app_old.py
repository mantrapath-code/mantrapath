import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog

from core.voice_processor import VoiceEventProcessor, VoiceActivityDetector, VoiceStreamManager

logger = structlog.get_logger(__name__)

# Global services
voice_processor: VoiceEventProcessor = None
activity_detector: VoiceActivityDetector = None
emotion_analyzer: VoiceEmotionAnalyzer = None
stream_manager: VoiceStreamManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global voice_processor, activity_detector, emotion_analyzer, stream_manager
    
    logger.info("Starting Voice Event Processor Service initialization")
    
    try:
        # Initialize core services
        voice_processor = VoiceEventProcessor()
        activity_detector = VoiceActivityDetector()
        emotion_analyzer = VoiceEmotionAnalyzer()
        stream_manager = VoiceStreamManager()
        
        # Start the services
        await voice_processor.start()
        await activity_detector.start()
        await emotion_analyzer.start()
        await stream_manager.start()
        
        logger.info("Voice Event Processor Service started successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to start Voice Event Processor Service", error=str(e))
        raise
    finally:
        # Cleanup
        if voice_processor:
            await voice_processor.stop()
        if activity_detector:
            await activity_detector.stop()
        if emotion_analyzer:
            await emotion_analyzer.stop()
        if stream_manager:
            await stream_manager.stop()
        
        logger.info("Voice Event Processor Service stopped")

async def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Voice Event Processor Service",
        description="Real-time voice event processing pipeline for MantraPath V3",
        version="3.0.0",
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
        try:
            status = {
                "status": "healthy",
                "service": "voice-event-processor",
                "version": "3.0.0",
                "components": {
                    "voice_processor": voice_processor.health_check() if voice_processor else False,
                    "activity_detector": activity_detector.health_check() if activity_detector else False,
                    "emotion_analyzer": emotion_analyzer.health_check() if emotion_analyzer else False,
                    "stream_manager": stream_manager.health_check() if stream_manager else False,
                }
            }
            return status
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            raise HTTPException(status_code=503, detail="Service unhealthy")
    
    @app.get("/health/live")
    async def liveness_check():
        """Kubernetes liveness probe"""
        return {"status": "alive"}
    
    @app.get("/health/ready")
    async def readiness_check():
        """Kubernetes readiness probe"""
        if not voice_processor or not voice_processor.is_ready():
            raise HTTPException(status_code=503, detail="Service not ready")
        return {"status": "ready"}
    
    @app.websocket("/ws/voice/{user_id}")
    async def voice_streaming_websocket(websocket: WebSocket, user_id: str):
        """WebSocket endpoint for real-time voice streaming"""
        try:
            await websocket.accept()
            
            if not stream_manager:
                await websocket.close(code=1011, reason="Service not ready")
                return
            
            # Handle voice streaming
            await stream_manager.handle_voice_stream(websocket, user_id)
            
        except Exception as e:
            logger.error("Voice streaming failed", error=str(e), user_id=user_id)
            try:
                await websocket.close(code=1011, reason="Streaming error")
            except:
                pass
    
    @app.get("/api/v1/metrics")
    async def get_metrics():
        """Get service metrics"""
        try:
            metrics = {}
            
            if voice_processor:
                metrics["voice_processor"] = await voice_processor.get_metrics()
            if activity_detector:
                metrics["activity_detector"] = await activity_detector.get_metrics()
            if emotion_analyzer:
                metrics["emotion_analyzer"] = await emotion_analyzer.get_metrics()
            if stream_manager:
                metrics["stream_manager"] = await stream_manager.get_metrics()
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to get metrics", error=str(e))
            raise HTTPException(status_code=500, detail="Failed to get metrics")
    
    return app
