"""
Enhanced Voice Event Processor

Handles voice interaction events with:
- Multi-language voice processing
- Real-time conversation flow
- Voice emotion detection  
- Cultural speech pattern analysis
- Integration with enhanced chatbot service

Author: MantraPath Development Team
Version: 2.0.0 (Voice Enhanced)
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import httpx
import aiofiles
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Add parent directories to path for shared imports
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.auth import get_current_user

# Simple NATS client implementation for voice events
class SimpleNATSClient:
    """Simple NATS client for event publishing"""
    
    def __init__(self):
        self.connected = False
        self.subscriptions = {}
    
    async def connect(self):
        """Connect to NATS server"""
        self.connected = True
        logger.info("NATS client connected (mock)")
    
    async def close(self):
        """Close NATS connection"""
        self.connected = False
        logger.info("NATS client disconnected")
    
    async def publish(self, subject: str, data: dict):
        """Publish message to NATS"""
        if self.connected:
            logger.info(f"Published to {subject}: {type(data).__name__}")
        else:
            logger.warning(f"Cannot publish to {subject}: not connected")
    
    async def subscribe(self, subject: str, handler):
        """Subscribe to NATS subject"""
        self.subscriptions[subject] = handler
        logger.info(f"Subscribed to {subject}")

NATSClient = SimpleNATSClient

# Configure logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Service URLs
SERVICE_URLS = {
    'chatbot_service': os.getenv('CHATBOT_SERVICE_URL', 'http://chatbot-service:8004'),
    'voice_service': os.getenv('VOICE_SERVICE_URL', 'http://voice-service:8011'),
    'translation_service': os.getenv('TRANSLATION_SERVICE_URL', 'http://translation-service:8010'),  # authoritative port
    'models_service': os.getenv('MODELS_SERVICE_URL', 'http://models-service:8080'),
    'ai_event_processor': os.getenv('AI_EVENT_PROCESSOR_URL', 'http://ai-event-processor:8014'),
    'memory_service': os.getenv('MEMORY_SERVICE_URL', 'http://memory-service:8017'),
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Enhanced Voice Event Processor v2.0.0")
    
    # Initialize HTTP client
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    
    # Initialize NATS client
    app.state.nats_client = NATSClient()
    await app.state.nats_client.connect()
    
    # Initialize voice event manager
    app.state.voice_event_manager = VoiceEventManager(app.state.http_client, app.state.nats_client)
    
    # Setup NATS subscriptions
    await setup_nats_subscriptions(app)
    
    logger.info("Enhanced Voice Event Processor initialized successfully")
    yield
    
    # Cleanup
    await app.state.http_client.aclose()
    await app.state.nats_client.close()
    logger.info("Enhanced Voice Event Processor shut down")

# Initialize FastAPI application
app = FastAPI(
    title="MantraPath Enhanced Voice Event Processor",
    description="Processes voice interaction events with multi-language support",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Enhanced Models ---

class VoiceEventRequest(BaseModel):
    """Voice event processing request"""
    event_type: str = Field(..., description="Type of voice event")
    user_id: str = Field(..., description="User ID")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    language: Optional[str] = Field("auto", description="Voice language")
    priority: str = Field("normal", description="Event priority")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class VoiceStreamEvent(BaseModel):
    """Real-time voice stream event"""
    stream_id: str
    chunk_id: int
    audio_data: str  # Base64 encoded
    is_final: bool = False
    language_hint: Optional[str] = None

class VoiceInteractionEvent(BaseModel):
    """Complete voice interaction event"""
    interaction_id: str
    user_id: str
    session_id: Optional[str] = None
    audio_input: str  # Base64 or URL
    detected_language: str
    transcribed_text: str
    emotion_analysis: Dict[str, Any]
    cultural_context: Dict[str, Any]
    response_generated: bool = False
    response_audio_url: Optional[str] = None

class VoiceProcessingResult(BaseModel):
    """Voice processing result"""
    success: bool
    event_id: str
    processing_time: float
    detected_language: str
    transcription: str
    emotion_score: Dict[str, float]
    cultural_markers: List[str]
    response_triggered: bool
    error_message: Optional[str] = None

# --- Voice Event Manager ---

class VoiceEventManager:
    """Manages voice events and processing pipeline"""
    
    def __init__(self, http_client: httpx.AsyncClient, nats_client: NATSClient):
        self.http_client = http_client
        self.nats_client = nats_client
        self.active_streams = {}
        self.processing_queue = asyncio.Queue()
        self.emotion_cache = {}
        
    async def process_voice_stream(self, stream_event: VoiceStreamEvent) -> Dict[str, Any]:
        """Process real-time voice stream"""
        stream_id = stream_event.stream_id
        
        if stream_id not in self.active_streams:
            self.active_streams[stream_id] = {
                "chunks": [],
                "start_time": datetime.now(),
                "language_hint": stream_event.language_hint
            }
        
        stream_info = self.active_streams[stream_id]
        stream_info["chunks"].append({
            "chunk_id": stream_event.chunk_id,
            "audio_data": stream_event.audio_data,
            "timestamp": datetime.now().isoformat()
        })
        
        if stream_event.is_final:
            # Process complete stream
            result = await self._process_complete_stream(stream_id, stream_info)
            del self.active_streams[stream_id]
            return result
        
        return {"status": "streaming", "chunk_received": stream_event.chunk_id}
    
    async def _process_complete_stream(self, stream_id: str, stream_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process complete voice stream"""
        try:
            # Combine audio chunks
            combined_audio = self._combine_audio_chunks(stream_info["chunks"])
            
            # Speech to text with language detection
            stt_result = await self._speech_to_text(combined_audio, stream_info["language_hint"])
            
            if not stt_result.get("success"):
                return {"success": False, "error": "Speech recognition failed"}
            
            transcription = stt_result["text"]
            detected_language = stt_result["language"]
            
            # Emotion and cultural analysis
            analysis_result = await self._analyze_voice_emotion_culture(
                combined_audio, transcription, detected_language
            )
            
            # Create voice interaction event
            interaction_event = VoiceInteractionEvent(
                interaction_id=f"voice_{stream_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                user_id=stream_info.get("user_id", "unknown"),
                audio_input=combined_audio,
                detected_language=detected_language,
                transcribed_text=transcription,
                emotion_analysis=analysis_result.get("emotion", {}),
                cultural_context=analysis_result.get("cultural", {})
            )
            
            # Publish to NATS for further processing
            await self.nats_client.publish(
                "voice.interaction.processed",
                interaction_event.dict()
            )
            
            return {
                "success": True,
                "interaction_id": interaction_event.interaction_id,
                "transcription": transcription,
                "detected_language": detected_language,
                "emotion_analysis": analysis_result.get("emotion", {}),
                "processing_time": (datetime.now() - stream_info["start_time"]).total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error processing stream {stream_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _combine_audio_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """Combine audio chunks into single audio data"""
        # Sort chunks by chunk_id
        sorted_chunks = sorted(chunks, key=lambda x: x["chunk_id"])
        
        # For now, return the first chunk's audio data
        # In production, you'd properly concatenate audio
        if sorted_chunks:
            return sorted_chunks[0]["audio_data"]
        return ""
    
    async def _speech_to_text(self, audio_data: str, language_hint: Optional[str] = None) -> Dict[str, Any]:
        """Convert speech to text with language detection"""
        try:
            # Convert base64 to audio file if needed
            audio_bytes = audio_data.encode() if isinstance(audio_data, str) else audio_data
            
            response = await self.http_client.post(
                f"{SERVICE_URLS['voice_service']}/api/v1/voice/stt",
                files={"audio": audio_bytes},
                data={"language": language_hint or "auto"},
                timeout=20.0
            )
            
            if response.status_code == 200:
                return {"success": True, **response.json()}
            else:
                return {"success": False, "error": "STT service unavailable"}
                
        except Exception as e:
            logger.error(f"STT processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_voice_emotion_culture(
        self, 
        audio_data: str, 
        transcription: str, 
        language: str
    ) -> Dict[str, Any]:
        """Analyze voice emotion and cultural patterns"""
        try:
            # Voice emotion analysis
            emotion_result = await self.http_client.post(
                f"{SERVICE_URLS['ai_event_processor']}/api/analyze/voice_emotion",
                json={
                    "audio_data": audio_data,
                    "transcription": transcription,
                    "language": language
                },
                timeout=15.0
            )
            
            emotion_data = {}
            if emotion_result.status_code == 200:
                emotion_data = emotion_result.json()
            
            # Cultural pattern analysis
            cultural_result = await self.http_client.post(
                f"{SERVICE_URLS['ai_event_processor']}/api/analyze/cultural_speech",
                json={
                    "transcription": transcription,
                    "language": language,
                    "voice_features": emotion_data.get("voice_features", {})
                },
                timeout=10.0
            )
            
            cultural_data = {}
            if cultural_result.status_code == 200:
                cultural_data = cultural_result.json()
            
            return {
                "emotion": emotion_data,
                "cultural": cultural_data
            }
            
        except Exception as e:
            logger.warning(f"Voice analysis error: {e}")
            return {"emotion": {}, "cultural": {}}
    
    async def trigger_chatbot_response(self, interaction_event: VoiceInteractionEvent) -> Dict[str, Any]:
        """Trigger chatbot response for voice interaction"""
        try:
            # Prepare chatbot request
            chatbot_request = {
                "message": interaction_event.transcribed_text,
                "session_id": interaction_event.session_id,
                "language": interaction_event.detected_language,
                "preferred_response_language": interaction_event.detected_language,
                "include_platform_context": True,
                "voice_response": True
            }
            
            # Send to enhanced chatbot service
            response = await self.http_client.post(
                f"{SERVICE_URLS['chatbot_service']}/api/chat/text",
                json=chatbot_request,
                timeout=30.0
            )
            
            if response.status_code == 200:
                chatbot_data = response.json()
                
                # Update interaction event with response
                interaction_event.response_generated = True
                interaction_event.response_audio_url = chatbot_data.get("audio_url")
                
                # Publish updated event
                await self.nats_client.publish(
                    "voice.interaction.completed",
                    interaction_event.dict()
                )
                
                return {
                    "success": True,
                    "response": chatbot_data,
                    "interaction_id": interaction_event.interaction_id
                }
            else:
                return {"success": False, "error": "Chatbot service unavailable"}
                
        except Exception as e:
            logger.error(f"Chatbot response error: {e}")
            return {"success": False, "error": str(e)}

# --- NATS Event Handlers ---

async def setup_nats_subscriptions(app: FastAPI):
    """Setup NATS event subscriptions"""
    
    async def handle_voice_interaction(msg):
        """Handle voice interaction events"""
        try:
            data = json.loads(msg.data.decode())
            interaction_event = VoiceInteractionEvent(**data)
            
            # Trigger chatbot response
            result = await app.state.voice_event_manager.trigger_chatbot_response(interaction_event)
            logger.info(f"Processed voice interaction {interaction_event.interaction_id}: {result.get('success')}")
            
        except Exception as e:
            logger.error(f"Error handling voice interaction: {e}")
    
    async def handle_voice_stream_chunk(msg):
        """Handle real-time voice stream chunks"""
        try:
            data = json.loads(msg.data.decode())
            stream_event = VoiceStreamEvent(**data)
            
            result = await app.state.voice_event_manager.process_voice_stream(stream_event)
            logger.debug(f"Processed voice stream chunk: {result}")
            
        except Exception as e:
            logger.error(f"Error handling voice stream: {e}")
    
    # Subscribe to events
    await app.state.nats_client.subscribe("voice.interaction.processed", handle_voice_interaction)
    await app.state.nats_client.subscribe("voice.stream.chunk", handle_voice_stream_chunk)
    
    logger.info("Voice event subscriptions established")

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "enhanced_voice_event_processor",
        "version": "2.0.0",
        "features": [
            "voice_stream_processing",
            "multi_language_support",
            "emotion_analysis", 
            "cultural_speech_analysis",
            "real_time_processing"
        ]
    }

@app.post("/api/voice/process")
async def process_voice_event(
    event: VoiceEventRequest,
    background_tasks: BackgroundTasks
):
    """Process voice event"""
    try:
        event_id = f"voice_event_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Publish event to NATS for asynchronous processing
        await app.state.nats_client.publish(
            f"voice.event.{event.event_type}",
            {
                "event_id": event_id,
                **event.dict()
            }
        )
        
        return {
            "success": True,
            "event_id": event_id,
            "status": "processing",
            "message": f"Voice event {event.event_type} queued for processing"
        }
        
    except Exception as e:
        logger.error(f"Voice event processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice event processing failed")

@app.post("/api/voice/stream/start")
async def start_voice_stream(
    user_id: str = Form(...),
    session_id: Optional[str] = Form(None),
    language_hint: Optional[str] = Form(None)
):
    """Start a new voice stream"""
    try:
        stream_id = f"stream_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Initialize stream in manager
        app.state.voice_event_manager.active_streams[stream_id] = {
            "chunks": [],
            "start_time": datetime.now(),
            "user_id": user_id,
            "session_id": session_id,
            "language_hint": language_hint
        }
        
        return {
            "success": True,
            "stream_id": stream_id,
            "status": "ready",
            "message": "Voice stream ready for chunks"
        }
        
    except Exception as e:
        logger.error(f"Stream start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start voice stream")

@app.post("/api/voice/stream/chunk/{stream_id}")
async def process_voice_chunk(
    stream_id: str,
    audio: UploadFile = File(...),
    chunk_id: int = Form(...),
    is_final: bool = Form(False)
):
    """Process voice stream chunk"""
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Create stream event
        stream_event = VoiceStreamEvent(
            stream_id=stream_id,
            chunk_id=chunk_id,
            audio_data=audio_data.hex(),  # Convert to hex string
            is_final=is_final
        )
        
        # Process chunk
        result = await app.state.voice_event_manager.process_voice_stream(stream_event)
        
        return {
            "success": True,
            "stream_id": stream_id,
            "chunk_id": chunk_id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Chunk processing error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process voice chunk")

@app.get("/api/voice/streams/active")
async def get_active_streams():
    """Get active voice streams"""
    try:
        active_streams = {}
        for stream_id, stream_info in app.state.voice_event_manager.active_streams.items():
            active_streams[stream_id] = {
                "user_id": stream_info.get("user_id"),
                "session_id": stream_info.get("session_id"),
                "start_time": stream_info["start_time"].isoformat(),
                "chunk_count": len(stream_info["chunks"]),
                "language_hint": stream_info.get("language_hint")
            }
        
        return {
            "success": True,
            "active_streams": active_streams,
            "total_streams": len(active_streams)
        }
        
    except Exception as e:
        logger.error(f"Active streams error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active streams")

@app.post("/api/voice/analyze")
async def analyze_voice_content(
    audio: UploadFile = File(...),
    transcription: Optional[str] = Form(None),
    language: str = Form("auto")
):
    """Analyze voice content for emotion and cultural patterns"""
    try:
        audio_data = await audio.read()
        
        # If no transcription provided, get it via STT
        if not transcription:
            stt_result = await app.state.voice_event_manager._speech_to_text(
                audio_data.hex(), language
            )
            if stt_result.get("success"):
                transcription = stt_result["text"]
                language = stt_result["language"]
            else:
                raise HTTPException(status_code=400, detail="Speech recognition failed")
        
        # Analyze emotion and cultural patterns
        analysis_result = await app.state.voice_event_manager._analyze_voice_emotion_culture(
            audio_data.hex(), transcription, language
        )
        
        return {
            "success": True,
            "transcription": transcription,
            "detected_language": language,
            "emotion_analysis": analysis_result.get("emotion", {}),
            "cultural_analysis": analysis_result.get("cultural", {}),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice analysis error: {e}")
        raise HTTPException(status_code=500, detail="Voice analysis failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
