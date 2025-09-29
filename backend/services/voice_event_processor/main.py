"""
Voice Event Processor Service
Real-time voice event processing with streaming capabilities
"""
import os
import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
import json

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Voice Event Processor",
    description="Real-time voice event processing service with streaming capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.voice_streams: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.voice_streams[client_id] = {
            "websocket": websocket,
            "status": "connected",
            "stream_active": False
        }
        logger.info(f"Client {client_id} connected")

    def disconnect(self, websocket: WebSocket, client_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if client_id in self.voice_streams:
            del self.voice_streams[client_id]
        logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Pydantic models
class VoiceEvent(BaseModel):
    event_type: str  # "speech_start", "speech_end", "emotion_detected", "silence"
    timestamp: float
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class EmotionAnalysisResult(BaseModel):
    emotion: str
    confidence: float
    valence: Optional[float] = None
    arousal: Optional[float] = None

class VoiceStreamConfig(BaseModel):
    sample_rate: int = 16000
    chunk_size: int = 1024
    vad_sensitivity: float = 0.7
    emotion_analysis: bool = True

# Basic endpoints
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "message": "Voice Event Processor v1.0 - Real-time Voice Processing",
        "status": "active",
        "features": [
            "real_time_voice_streaming",
            "voice_activity_detection",
            "emotion_recognition",
            "event_broadcasting"
        ]
    }

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "voice_event_processor",
        "version": "1.0.0",
        "active_connections": len(manager.active_connections),
        "active_streams": len([s for s in manager.voice_streams.values() if s.get("stream_active")])
    }

@app.get("/api/v1/streams/status")
async def get_streams_status() -> Dict[str, Any]:
    """Get status of all active voice streams"""
    return {
        "total_connections": len(manager.active_connections),
        "active_streams": len([s for s in manager.voice_streams.values() if s.get("stream_active")]),
        "streams": {
            client_id: {
                "status": stream_info["status"],
                "stream_active": stream_info["stream_active"]
            }
            for client_id, stream_info in manager.voice_streams.items()
        }
    }

@app.post("/api/v1/voice/process")
async def process_voice_chunk(
    audio_data: bytes,
    config: VoiceStreamConfig = VoiceStreamConfig()
) -> Dict[str, Any]:
    """Process a single voice chunk (non-streaming)"""
    try:
        # Simulate voice processing
        # In a real implementation, this would:
        # 1. Apply VAD (Voice Activity Detection)
        # 2. Detect emotions if enabled
        # 3. Generate events
        
        # Mock processing result
        events = []
        
        # Simulate VAD detection
        if len(audio_data) > 0:
            events.append(VoiceEvent(
                event_type="speech_detected",
                timestamp=asyncio.get_event_loop().time(),
                confidence=0.85,
                metadata={"chunk_size": len(audio_data)}
            ))
        
        # Simulate emotion detection
        if config.emotion_analysis:
            emotion_result = EmotionAnalysisResult(
                emotion="neutral",
                confidence=0.75,
                valence=0.5,
                arousal=0.4
            )
            events.append(VoiceEvent(
                event_type="emotion_detected",
                timestamp=asyncio.get_event_loop().time(),
                confidence=emotion_result.confidence,
                metadata=emotion_result.dict()
            ))
        
        return {
            "success": True,
            "events": [event.dict() for event in events],
            "processed_bytes": len(audio_data)
        }
        
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time voice streaming
@app.websocket("/ws/voice/{client_id}")
async def websocket_voice_stream(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time voice streaming"""
    await manager.connect(websocket, client_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "client_id": client_id,
            "timestamp": asyncio.get_event_loop().time()
        }))
        
        while True:
            # Receive audio data or control messages
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "start_stream":
                    manager.voice_streams[client_id]["stream_active"] = True
                    await websocket.send_text(json.dumps({
                        "type": "stream_started",
                        "timestamp": asyncio.get_event_loop().time()
                    }))
                    
                elif message_type == "stop_stream":
                    manager.voice_streams[client_id]["stream_active"] = False
                    await websocket.send_text(json.dumps({
                        "type": "stream_stopped",
                        "timestamp": asyncio.get_event_loop().time()
                    }))
                    
                elif message_type == "audio_chunk":
                    # Process audio chunk (base64 encoded in real implementation)
                    # For now, just acknowledge
                    if manager.voice_streams[client_id]["stream_active"]:
                        # Simulate voice event detection
                        voice_event = {
                            "type": "voice_event",
                            "event": {
                                "event_type": "speech_activity",
                                "timestamp": asyncio.get_event_loop().time(),
                                "confidence": 0.8,
                                "client_id": client_id
                            }
                        }
                        await websocket.send_text(json.dumps(voice_event))
                        
                elif message_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(websocket, client_id)

# Configuration endpoints
@app.get("/api/v1/config")
async def get_config() -> Dict[str, Any]:
    """Get current voice processing configuration"""
    return {
        "max_concurrent_streams": int(os.getenv("MAX_CONCURRENT_STREAMS", 100)),
        "vad_sensitivity": float(os.getenv("VAD_SENSITIVITY", 0.7)),
        "voice_streaming_enabled": os.getenv("VOICE_STREAMING_ENABLED", "true").lower() == "true",
        "audio_sample_rate": int(os.getenv("AUDIO_SAMPLE_RATE", 16000)),
        "audio_chunk_size": int(os.getenv("AUDIO_CHUNK_SIZE", 1024)),
        "voice_emotion_model": os.getenv("VOICE_EMOTION_MODEL", "speechbrain/emotion-recognition-wav2vec2-IEMOCAP"),
        "stream_timeout": int(os.getenv("STREAM_TIMEOUT", 30)),
        "activity_detection_timeout": int(os.getenv("ACTIVITY_DETECTION_TIMEOUT", 50)),
        "emotion_analysis_timeout": int(os.getenv("EMOTION_ANALYSIS_TIMEOUT", 200))
    }

@app.post("/api/voice-events/track")
async def track_voice_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Track voice analytics event"""
    try:
        logger.info(f"📊 Voice Event Tracked: {event_data.get('event_type', 'unknown')}")
        
        # In a real implementation, this would:
        # 1. Validate event data structure
        # 2. Store in analytics database (ClickHouse, etc.)
        # 3. Update real-time metrics
        # 4. Trigger any real-time processing
        
        # For now, just log and confirm receipt
        processed_event = {
            "event_id": f"evt_{asyncio.get_event_loop().time()}",
            "status": "processed",
            "timestamp": asyncio.get_event_loop().time(),
            "event_type": event_data.get("event_type"),
            "user_id": event_data.get("user_id"),
            "session_id": event_data.get("session_id")
        }
        
        return {
            "success": True,
            "message": "Event tracked successfully",
            "event": processed_event
        }
        
    except Exception as e:
        logger.error(f"Failed to track voice event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")

@app.get("/api/v1/stats")
async def get_stats() -> Dict[str, Any]:
    """Get voice processing statistics"""
    return {
        "service_uptime": "running",
        "total_connections": len(manager.active_connections),
        "active_streams": len([s for s in manager.voice_streams.values() if s.get("stream_active")]),
        "processed_events": 0,  # Would be tracked in real implementation
        "detected_emotions": 0,  # Would be tracked in real implementation
        "voice_activity_events": 0  # Would be tracked in real implementation
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("VOICE_EVENT_PROCESSOR_PORT", 8015))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
