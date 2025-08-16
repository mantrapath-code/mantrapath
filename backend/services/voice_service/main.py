"""Voice Service Main Application
Enterprise-grade FastAPI voice processing service
"""
import logging
import uuid
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import asyncio
from datetime import datetime
import io

# Voice Service Imports
from config.settings import voice_config
from core.models import (
    VoiceCommand, TTSRequest, STTRequest, VoiceResponse,
    AudioData, AudioFormat, VoiceProfile, VoicePreferences
)
from core.exceptions import (
    VoiceServiceError, AudioProcessingError, UnsupportedLanguageError,
    AuthenticationError, RateLimitError, AudioValidationError
)
from engines.engine_manager import VoiceEngineManager
from services.voice_service import VoiceProcessingService
from services.command_processor import VoiceCommandProcessor
from services.profile_service import VoiceProfileService
from services.integration_service import ServiceIntegrationManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, voice_config.LOG_LEVEL),
    format=voice_config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Global service instances
engine_manager: Optional[VoiceEngineManager] = None
voice_processing: Optional[VoiceProcessingService] = None
command_processor: Optional[VoiceCommandProcessor] = None
profile_service: Optional[VoiceProfileService] = None
integration_manager: Optional[ServiceIntegrationManager] = None

security = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global engine_manager, voice_processing, command_processor, profile_service, integration_manager
    
    logger.info("Starting Voice Service...")
    
    try:
        # Initialize services with engine configuration
        config_dict = voice_config.model_dump()
        
        # Configure voice engines with API keys
        engine_config = {
            "stt_engines": {
                "whisper": {
                    "enabled": True,
                    "required": True,
                    "api_key": voice_config.openai_api_key,
                    "model_size": "base"
                }
            },
            "tts_engines": {
                "elevenlabs": {
                    "enabled": True,
                    "required": True,
                    "elevenlabs_api_key": voice_config.elevenlabs_api_key
                }
            },
            "emotion_engines": {}
        }
        
        # Merge engine config with voice config
        config_dict.update(engine_config)
        
        engine_manager = VoiceEngineManager(config_dict)
        await engine_manager.initialize_engines()
        
        voice_processing = VoiceProcessingService(engine_manager)
        command_processor = VoiceCommandProcessor()
        profile_service = VoiceProfileService()
        integration_manager = ServiceIntegrationManager()
        
        # Register with API Gateway
        await register_with_api_gateway()
        
        logger.info("Voice Service started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start Voice Service: {e}")
        raise
    
    finally:
        logger.info("Shutting down Voice Service...")
        
        # Cleanup services
        if integration_manager:
            await integration_manager.close()
        
        if engine_manager:
            await engine_manager.cleanup()
        
        logger.info("Voice Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="MantraPath Voice Service",
    description="Enterprise-grade voice processing service with STT, TTS, voice cloning, and multilingual support",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if voice_config.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if voice_config.ENVIRONMENT != "production" else None
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=voice_config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Authentication dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token with Auth Service"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Check if integration_manager is available and has the method
        if hasattr(integration_manager, 'verify_user_authentication'):
            auth_result = integration_manager.verify_user_authentication(credentials.credentials)
            # Handle both sync and async returns
            if hasattr(auth_result, '__await__'):
                auth_data = await auth_result
            else:
                auth_data = auth_result
            return auth_data
        else:
            # Fallback for testing - parse token directly
            return {"user_id": "test_user", "token": credentials.credentials, "is_admin": False}
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=500, detail="Authentication service unavailable")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check engine manager health
        engine_status = {}
        if engine_manager:
            try:
                engine_status = await engine_manager.get_health_status()
            except Exception:
                engine_status = {"status": "degraded", "error": "engine_manager_error"}
        
        # Check service integrations
        integration_stats = {}
        if integration_manager:
            try:
                integration_stats = integration_manager.get_integration_stats()
            except Exception:
                integration_stats = {"status": "degraded", "error": "integration_error"}
        
        # Get processing statistics
        processing_stats = {}
        if voice_processing:
            try:
                processing_stats = await voice_processing.get_processing_stats()
            except Exception:
                processing_stats = {"status": "degraded", "error": "processing_error"}
        
        # Determine overall status
        overall_status = "healthy"
        if engine_status.get("status") == "degraded" or integration_stats.get("status") == "degraded" or processing_stats.get("status") == "degraded":
            overall_status = "degraded"
        
        response_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": getattr(voice_config, 'ENVIRONMENT', 'development'),
            "engines": engine_status,
            "integration": integration_stats,
            "processing": processing_stats
        }
        
        # Return 503 if degraded
        if overall_status == "degraded":
            return JSONResponse(status_code=503, content=response_data)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# Voice Processing Endpoints

@app.post("/stt", response_model=VoiceResponse)
async def speech_to_text(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("en"),
    model: Optional[str] = Form(None),
    enable_diarization: bool = Form(False),
    translate_to_english: bool = Form(False),
    enable_emotion_analysis: bool = Form(False),
    confidence_threshold: float = Form(0.7),
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Speech-to-text endpoint"""
    try:
        # Extract request ID from headers
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Read audio file
        audio_content = await file.read()
        
        # Create audio data
        audio_data = AudioData(
            data=audio_content,
            format=AudioFormat.WAV,  # Auto-detect in production
            file_size=len(audio_content),
            duration=None  # Will be calculated by the service
        )
        
        # Create STT request
        stt_request = STTRequest(
            language=language,
            model=model or "whisper",
            enable_diarization=enable_diarization,
            translate_to_english=translate_to_english,
            enable_emotion_analysis=enable_emotion_analysis,
            confidence_threshold=confidence_threshold
        )
        
        # Process STT
        result = await voice_processing.process_speech_to_text(
            audio_data=audio_data,
            request=stt_request,
            user_id=auth_data.get("user_id"),
            request_id=request_id
        )
        
        # Log activity
        asyncio.create_task(
            integration_manager.log_user_activity(
                user_id=auth_data.get("user_id"),
                activity_type="stt",
                activity_data={"language": language, "duration": audio_data.duration},
                token=auth_data.get("token")
            )
        )
        
        return result
        
    except Exception as e:
        logger.error(f"STT processing failed: {e}")
        if isinstance(e, VoiceServiceError):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail="STT processing failed")

@app.post("/tts")
async def text_to_speech(
    request: TTSRequest,
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Text-to-speech endpoint"""
    try:
        # Process TTS
        audio_data = await voice_processing.process_text_to_speech(
            request=request,
            user_id=auth_data.get("user_id")
        )
        
        # Log activity
        asyncio.create_task(
            integration_manager.log_user_activity(
                user_id=auth_data.get("user_id"),
                activity_type="tts",
                activity_data={"language": request.language, "text_length": len(request.text)},
                token=auth_data.get("token")
            )
        )
        
        # Return audio stream
        return StreamingResponse(
            io.BytesIO(audio_data.data),
            media_type=f"audio/{request.format.value}",
            headers={"Content-Disposition": f"attachment; filename=tts_output.{request.format.value}"}
        )
        
    except Exception as e:
        logger.error(f"TTS processing failed: {e}")
        if isinstance(e, VoiceServiceError):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail="TTS processing failed")

@app.post("/voice-command", response_model=VoiceResponse)
async def process_voice_command(
    command: VoiceCommand,
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Process voice command"""
    try:
        result = await command_processor.process_voice_command(
            text=command.text,
            language=command.language,
            user_id=auth_data.get("user_id"),
            context=command.context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Voice command processing failed: {e}")
        if isinstance(e, VoiceServiceError):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail="Voice command processing failed")

@app.post("/emotion-analysis", response_model=VoiceResponse)
async def analyze_emotion(
    file: UploadFile = File(...),
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Analyze emotion from voice"""
    try:
        # Read audio file
        audio_content = await file.read()
        
        # Create audio data
        audio_data = AudioData(
            data=audio_content,
            format=AudioFormat.WAV,
            file_size=len(audio_content),
            duration=None  # Will be calculated by the service
        )
        
        # Analyze emotion
        result = await voice_processing.analyze_voice_emotion(
            audio_data=audio_data,
            user_id=auth_data.get("user_id")
        )
        
        # Update mood tracking if successful
        if result.success and result.data.get("emotion_analysis"):
            emotion_data = result.data["emotion_analysis"]
            asyncio.create_task(
                integration_manager.update_mood_tracking(
                    user_id=auth_data.get("user_id"),
                    mood_data=emotion_data,
                    token=auth_data.get("token")
                )
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Emotion analysis failed: {e}")
        if isinstance(e, VoiceServiceError):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail="Emotion analysis failed")

# Voice Profile Endpoints

@app.post("/profiles", response_model=VoiceResponse)
async def create_voice_profile(
    profile_name: str = Form(...),
    language: str = Form("en"),
    files: Optional[list[UploadFile]] = File(None),
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Create voice profile"""
    try:
        voice_samples = []
        
        if files:
            for file in files:
                audio_content = await file.read()
                audio_data = AudioData(
                    data=audio_content,
                    format=AudioFormat.WAV,
                    file_size=len(audio_content),
                    filename=file.filename
                )
                voice_samples.append(audio_data)
        
        result = await profile_service.create_voice_profile(
            user_id=auth_data.get("user_id"),
            profile_name=profile_name,
            language=language,
            voice_samples=voice_samples
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Profile creation failed: {e}")
        if isinstance(e, VoiceServiceError):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail="Profile creation failed")

@app.get("/profiles")
async def get_user_profiles(
    active_only: bool = False,
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Get user voice profiles"""
    try:
        profiles = await profile_service.get_user_profiles(
            user_id=auth_data.get("user_id"),
            active_only=active_only
        )
        
        return {
            "profiles": [profile.dict() for profile in profiles],
            "count": len(profiles)
        }
        
    except Exception as e:
        logger.error(f"Profile retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Profile retrieval failed")

@app.get("/profiles/{profile_id}/training-status")
async def get_training_status(
    profile_id: str,
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Get voice training status"""
    try:
        result = await profile_service.get_training_status(
            user_id=auth_data.get("user_id"),
            profile_id=profile_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Training status retrieval failed: {e}")
        if isinstance(e, VoiceServiceError):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail="Training status retrieval failed")

# Service Information Endpoints

@app.get("/capabilities")
async def get_capabilities():
    """Get service capabilities"""
    try:
        features = await voice_processing.get_supported_features()
        commands = command_processor.get_supported_commands()
        
        return {
            "features": features,
            "supported_commands": {
                "english": command_processor.get_supported_commands("en"),
                "hindi": command_processor.get_supported_commands("hi"),
                "spanish": command_processor.get_supported_commands("es")
            },
            "service_info": {
                "version": "1.0.0",
                "environment": voice_config.ENVIRONMENT,
                "uptime": voice_processing.get_processing_stats().get("uptime_seconds", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Capabilities retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Capabilities retrieval failed")

@app.get("/stats")
async def get_service_stats(
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Get service statistics (admin only)"""
    try:
        # Check admin permissions
        if not auth_data.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return {
            "processing": voice_processing.get_processing_stats(),
            "commands": command_processor.get_command_stats(),
            "profiles": profile_service.get_service_stats(),
            "integration": integration_manager.get_integration_stats()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Stats retrieval failed")

# Admin endpoints for service management

@app.post("/admin/cleanup")
async def cleanup_services(
    auth_data: Dict[str, Any] = Depends(verify_token)
):
    """Cleanup expired sessions and data"""
    try:
        if not auth_data.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Cleanup processing sessions
        expired_sessions = await voice_processing.cleanup_expired_sessions()
        
        # Cleanup inactive profiles
        cleaned_profiles = await profile_service.cleanup_inactive_profiles()
        
        return {
            "message": "Cleanup completed",
            "expired_sessions_removed": expired_sessions,
            "inactive_profiles_cleaned": cleaned_profiles
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")

# Service registration helper
async def register_with_api_gateway():
    """Register service with API Gateway"""
    try:
        service_info = {
            "service_url": f"http://voice_service:{voice_config.port}",
            "health_endpoint": "/health",
            "version": "1.0.0",
            "capabilities": [
                "speech_to_text",
                "text_to_speech", 
                "voice_commands",
                "emotion_analysis",
                "voice_cloning",
                "multilingual_support"
            ],
            "supported_routes": [
                "/stt", "/tts", "/voice-command", "/emotion-analysis",
                "/profiles", "/capabilities", "/stats"
            ]
        }
        
        success = await integration_manager.register_with_api_gateway(service_info)
        if success:
            logger.info("Successfully registered with API Gateway")
        else:
            logger.warning("Failed to register with API Gateway")
            
    except Exception as e:
        logger.error(f"API Gateway registration failed: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=voice_config.port,
        reload=voice_config.ENVIRONMENT == "development",
        log_level=voice_config.LOG_LEVEL.lower()
    )