"""
Voice Service - Clean Implementation
FastAPI-based voice processing service
"""
import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import io

from models_client import models_client

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Voice Service",
    description="Clean voice processing service for MantraPath",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class TextToSpeechRequest(BaseModel):
    text: str
    language: str = "en"
    voice: Optional[str] = None
    model_preference: Optional[str] = None

class ConversationRequest(BaseModel):
    text: str
    language: str = "auto"
    context: Optional[dict] = None
    user_id: Optional[str] = None

class CreateSessionRequest(BaseModel):
    """Create session request model"""
    user_id: Optional[str] = None
    language: str = "en"
    preferences: Optional[dict] = None
    voice_settings: Optional[dict] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Voice Service v2.0 - Clean Implementation", "status": "active"}

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint - supports both GET and HEAD requests"""
    return {"status": "healthy", "service": "voice_service", "version": "2.0.0"}

# Models Service Integration - Real implementation
@app.get("/api/v1/models/status")
async def models_status():
    """Check Models Service connection status"""
    return await models_client.health_check()

@app.post("/api/v1/voice/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form("auto"),
    model_preference: Optional[str] = Form(None)
):
    """Speech to Text endpoint - Routes to Models Service"""
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Send to Models Service
        result = await models_client.speech_to_text(
            audio_data=audio_data,
            language=language,
            model_preference=model_preference
        )
        
        return result
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/voice/tts") 
async def text_to_speech(request: TextToSpeechRequest):
    """Text to Speech endpoint - Routes to Models Service"""
    try:
        result = await models_client.text_to_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            model_preference=request.model_preference
        )
        
        # If we got audio data, return it as streaming response
        if result.get("success") and result.get("audio_data"):
            return StreamingResponse(
                io.BytesIO(result["audio_data"]),
                media_type=result.get("content_type", "audio/wav"),
                headers={
                    "Content-Disposition": "attachment; filename=synthesized.wav",
                    "X-Sample-Rate": str(result.get("sample_rate", "22050")),
                    "X-Duration": str(result.get("duration", "0")),
                    "X-Model-Used": str(result.get("model_used", "unknown"))
                }
            )
        
        return result
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/voice/conversation")
async def voice_conversation(request: ConversationRequest):
    """Voice conversation endpoint with context awareness"""
    try:
        # Step 1: Analyze sentiment for context
        sentiment_result = await models_client.analyze_sentiment(
            text=request.text,
            language=request.language if request.language != "auto" else "en"
        )
        
        # Step 2: For now, echo back the text (TODO: Add Rasa dialogue management)
        response_text = f"I understand you said: '{request.text}'. Sentiment: {sentiment_result.get('sentiment', 'neutral')}"
        
        # Step 3: Convert response to speech
        tts_result = await models_client.text_to_speech(
            text=response_text,
            language=request.language if request.language != "auto" else "en"
        )
        
        return {
            "success": True,
            "user_input": request.text,
            "sentiment_analysis": sentiment_result,
            "response_text": response_text,
            "audio_available": tts_result.get("success", False),
            "context": request.context,
            "message": "Conversation processed - Phase 2 features coming soon"
        }
        
    except Exception as e:
        logger.error(f"Conversation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional endpoints for language support
@app.get("/api/v1/voice/languages/stt")
async def get_stt_languages():
    """Get supported STT languages"""
    return await models_client.get_supported_languages("stt")

@app.get("/api/v1/voice/languages/tts")
async def get_tts_languages():
    """Get supported TTS languages"""
    return await models_client.get_supported_languages("tts")

@app.get("/api/v1/voice/status")
async def voice_service_status():
    """Get comprehensive voice service status and capabilities"""
    try:
        # Check Models Service connection
        models_status = await models_client.health_check()
        
        # Get language support
        stt_languages = await models_client.get_supported_languages("stt")
        tts_languages = await models_client.get_supported_languages("tts")
        
        return {
            "voice_service": {
                "status": "healthy",
                "version": "2.0.0",
                "features_implemented": [
                    "speech_to_text",
                    "text_to_speech", 
                    "conversation_flow",
                    "sentiment_analysis",
                    "models_service_integration"
                ],
                "features_coming_soon": [
                    "voice_cloning",
                    "real_time_streaming",
                    "rasa_dialogue_management",
                    "websocket_support"
                ]
            },
            "models_service_integration": models_status,
            "language_support": {
                "stt": stt_languages.get("supported_languages", {}),
                "tts": tts_languages.get("supported_languages", {})
            },
            "endpoints": {
                "stt": "/api/v1/voice/stt",
                "tts": "/api/v1/voice/tts",
                "conversation": "/api/v1/voice/conversation",
                "models_status": "/api/v1/models/status",
                "languages_stt": "/api/v1/voice/languages/stt",
                "languages_tts": "/api/v1/voice/languages/tts"
            }
        }
        
    except Exception as e:
        return {
            "voice_service": {
                "status": "degraded",
                "error": str(e)
            }
        }

# Simple session management for compatibility
class SimpleSessionManager:
    def __init__(self):
        self.sessions = {}
        self.counter = 0
    
    def create_session(self, user_id=None, language="en", preferences=None):
        self.counter += 1
        session_id = f"session_{self.counter}"
        import time
        self.sessions[session_id] = {
            "user_id": user_id,
            "language": language,
            "preferences": preferences or {},
            "status": "active",
            "created_at": time.time(),
            "last_activity": time.time()
        }
        return session_id
    
    def get_session(self, session_id):
        return self.sessions.get(session_id)

session_manager = SimpleSessionManager()

# Alias endpoints for frontend compatibility
@app.post("/api/v1/session/start")
async def start_session_alias(payload: CreateSessionRequest = Body(default=CreateSessionRequest())):
    """Alias endpoint expected by frontend for session creation"""
    try:
        session_id = session_manager.create_session(
            user_id=payload.user_id,
            language=payload.language,
            preferences=payload.preferences
        )
        data = session_manager.get_session(session_id)
        return {
            "success": True,
            "session": {
                "session_id": session_id,
                "user_id": data.get("user_id"),
                "language": data.get("language"),
                "created_at": data.get("created_at"),
                "last_activity": data.get("last_activity"),
                "status": data.get("status")
            }
        }
    except Exception as e:
        logger.error(f"Session start alias error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/v1/voice/text-to-speech")
async def text_to_speech_legacy(request: TextToSpeechRequest):
    """Legacy alias for /api/v1/voice/tts used by earlier frontend code."""
    try:
        result = await models_client.text_to_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            model_preference=request.model_preference
        )
        
        # If we got audio data, return it as streaming response
        if result.get("success") and result.get("audio_data"):
            return StreamingResponse(
                io.BytesIO(result["audio_data"]),
                media_type=result.get("content_type", "audio/wav"),
                headers={
                    "Content-Disposition": "attachment; filename=synthesized.wav",
                    "X-Sample-Rate": str(result.get("sample_rate", "22050")),
                    "X-Duration": str(result.get("duration", "0")),
                    "X-Model-Used": str(result.get("model_used", "unknown")),
                    "X-Legacy-Alias": "true"
                }
            )
        
        return result
        
    except Exception as e:
        logger.error(f"TTS legacy alias error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# New Indic Language Support Endpoints
@app.post("/api/v1/language/detect")
async def detect_language(audio: UploadFile = File(...)):
    """Detect language from audio using Indic models"""
    try:
        audio_data = await audio.read()
        result = await models_client.detect_language(audio_data)
        return result
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class VoicePipelineTestRequest(BaseModel):
    text: str
    language: str = "hi"

@app.post("/api/v1/test/voice-pipeline")
async def test_voice_pipeline(request: VoicePipelineTestRequest):
    """Test full voice pipeline with Indic models (TTS + STT roundtrip)"""
    try:
        result = await models_client.test_voice_pipeline(
            text=request.text,
            language=request.language
        )
        return result
        
    except Exception as e:
        logger.error(f"Voice pipeline test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models/languages")
async def get_supported_languages():
    """Get all supported languages for STT and TTS"""
    try:
        stt_result = await models_client.get_supported_languages("stt")
        tts_result = await models_client.get_supported_languages("tts")
        
        return {
            "success": True,
            "stt_languages": stt_result.get("languages", []),
            "tts_languages": tts_result.get("languages", []),
            "indic_languages": ["hi", "mr", "ta", "te", "bn", "gu", "kn", "ml", "or", "pa", "ur"],
            "supported_models": {
                "stt": ["indicwav2vec", "whisper", "wav2vec2"],
                "tts": ["indic-tts", "mms", "parler"]
            }
        }
        
    except Exception as e:
        logger.error(f"Get languages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# TODO: Add voice processing endpoints
# - POST /voice-clone (Voice cloning)
# - WebSocket /ws/voice (Real-time voice)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("VOICE_SERVICE_PORT", 8011))
    
    # SSL configuration
    ssl_keyfile = os.getenv("SSL_KEYFILE", "/app/ssl_certs/key.pem")
    ssl_certfile = os.getenv("SSL_CERTFILE", "/app/ssl_certs/cert.pem")
    ssl_enabled = os.getenv("SSL_ENABLED", "true").lower() == "true"
    
    if ssl_enabled and os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        logger.info(f"Starting voice service with SSL on port {port}")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port, 
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            reload=True
        )
    else:
        logger.warning(f"SSL disabled or certificates not found. Starting without SSL on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
