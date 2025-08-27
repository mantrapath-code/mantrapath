import asyncio
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import structlog

from core.voice_processor import VoiceEventProcessor
from models.voice_events import VoiceEvent, VoiceAnalysisResult

logger = structlog.get_logger(__name__)

# Global services
voice_processor: VoiceEventProcessor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global voice_processor
    
    logger.info("Starting Voice Event Processor Service initialization")
    
    try:
        # Initialize core services
        voice_processor = VoiceEventProcessor()
        await voice_processor.initialize()
        
        logger.info("Voice Event Processor Service started successfully")
        yield
        
    except Exception as e:
        logger.error("Failed to start Voice Event Processor Service", error=str(e))
        raise
    finally:
        # Cleanup
        if voice_processor:
            await voice_processor.cleanup()

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="Voice Event Processor Service",
        description="Real-time voice event processing and analysis",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            if voice_processor is None:
                raise HTTPException(status_code=503, detail="Voice processor not initialized")
            
            health_status = await voice_processor.get_health_status()
            # Ensure the response has the expected structure
            return {
                "status": "healthy",
                "service": "voice-event-processor",
                "version": "1.0.0",
                "components": health_status
            }
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health/live")
    async def liveness_check():
        """Kubernetes liveness probe"""
        return {"status": "alive"}
    
    @app.get("/health/ready")
    async def readiness_check():
        """Kubernetes readiness probe"""
        if voice_processor is None:
            raise HTTPException(status_code=503, detail="Voice processor not initialized")
        return {"status": "ready"}
    
    @app.post("/voice/process")
    async def process_voice_event(voice_event: VoiceEvent) -> VoiceAnalysisResult:
        """Process a voice event"""
        try:
            if voice_processor is None:
                raise HTTPException(status_code=503, detail="Voice processor not initialized")
            
            result = await voice_processor.process_voice_event(voice_event)
            return result
            
        except Exception as e:
            logger.error("Voice event processing failed", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.websocket("/voice/stream/{session_id}")
    async def voice_stream_endpoint(websocket: WebSocket, session_id: str):
        """WebSocket endpoint for real-time voice streaming"""
        await websocket.accept()
        logger.info(f"Voice stream connected for session: {session_id}")
        
        try:
            if voice_processor is None:
                await websocket.close(code=1003, reason="Voice processor not initialized")
                return
            
            # Start voice stream
            stream_manager = await voice_processor.start_voice_stream(session_id, websocket)
            
            while True:
                try:
                    # Receive audio data
                    audio_data = await websocket.receive_bytes()
                    
                    # Process audio stream
                    await voice_processor.process_audio_stream(session_id, audio_data)
                    
                except Exception as e:
                    logger.error(f"Error processing audio stream: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket error for session {session_id}: {e}")
        finally:
            # Stop voice stream
            if voice_processor:
                await voice_processor.stop_voice_stream(session_id)
            logger.info(f"Voice stream disconnected for session: {session_id}")
    
    @app.get("/voice/session/{session_id}/analysis")
    async def get_session_analysis(session_id: str):
        """Get voice analysis results for a session"""
        try:
            if voice_processor is None:
                raise HTTPException(status_code=503, detail="Voice processor not initialized")
            
            results = await voice_processor.get_session_analysis(session_id)
            return {"session_id": session_id, "analysis_results": results}
            
        except Exception as e:
            logger.error("Failed to get session analysis", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/metrics")
    async def get_metrics():
        """Get voice processor metrics"""
        try:
            if voice_processor is None:
                raise HTTPException(status_code=503, detail="Voice processor not initialized")
            
            return {
                "processed_events": voice_processor.processed_events,
                "active_connections": voice_processor.active_connections,
                "models_loaded": {
                    "emotion_classifier": voice_processor.emotion_classifier is not None,
                    "speech_recognizer": voice_processor.speech_recognizer is not None
                }
            }
            
        except Exception as e:
            logger.error("Failed to get metrics", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/metrics")
    async def get_api_metrics():
        """Get voice processor metrics via API v1 endpoint"""
        try:
            if voice_processor is None:
                raise HTTPException(status_code=503, detail="Voice processor not initialized")
            
            return {
                "processed_events": voice_processor.processed_events,
                "active_connections": voice_processor.active_connections,
                "models_loaded": {
                    "emotion_classifier": voice_processor.emotion_classifier is not None,
                    "speech_recognizer": voice_processor.speech_recognizer is not None
                }
            }
            
        except Exception as e:
            logger.error("Failed to get API metrics", error=str(e))
            raise HTTPException(status_code=500, detail=str(e))
    
    logger.info("Voice Event Processor FastAPI application created")
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8015, reload=False)
