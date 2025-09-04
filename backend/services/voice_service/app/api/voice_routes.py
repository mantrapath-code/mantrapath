"""
Voice Processing Routes
Handles STT, TTS, and voice enhancement endpoints
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from ..core.models_client import ModelsServiceClient
from ..core.voice_enhancer import VoiceEnhancer
from ..core.audio_cache_manager import AudioCacheManager
from ..core.language_detector import LanguageDetector
from ..models.requests import TTSRequest, VoiceEnhancementRequest
from ..models.responses import STTResponse, VoiceStatusResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice", tags=["voice"])

# Initialize core components
models_client = ModelsServiceClient()
voice_enhancer = VoiceEnhancer()
audio_cache = AudioCacheManager()
language_detector = LanguageDetector()

@router.post("/stt", response_model=STTResponse)
async def speech_to_text(
    audio: UploadFile = File(..., description="Audio file for transcription"),
    language: str = Form("auto", description="Language code or 'auto' for detection"),
    model_preference: Optional[str] = Form(None, description="Preferred STT model"),
    enhance_audio: bool = Form(False, description="Apply audio enhancement before STT"),
    session_id: Optional[str] = Form(None, description="Session ID for context")
):
    """
    Convert speech to text with optional enhancement and language detection
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Enhance audio if requested
        if enhance_audio:
            enhancement_result = voice_enhancer.enhance_audio(audio_data, audio.content_type)
            audio_data = enhancement_result.enhanced_audio
            logger.info(f"Audio enhanced with score: {enhancement_result.improvement_score}")
        
        # Detect language if auto
        if language == "auto":
            # For audio, we'll let the models service handle detection
            # In a full implementation, we might do preliminary detection
            language = "auto"
        
        # Send to Models Service
        stt_result = await models_client.speech_to_text(
            audio_data=audio_data,
            language=language,
            model_preference=model_preference
        )
        
        if not stt_result.success:
            raise HTTPException(status_code=500, detail=stt_result.error)
        
        # Detect language from transcribed text if available
        language_info = None
        if stt_result.text:
            detection = language_detector.detect_language(stt_result.text)
            language_info = {
                "detected_language": detection.primary_language,
                "confidence": detection.confidence,
                "is_mixed": detection.is_mixed,
                "script": detection.script_detected
            }
        
        return STTResponse(
            text=stt_result.text,
            confidence=stt_result.confidence,
            language=stt_result.language,
            model_used=stt_result.model_used,
            language_detection=language_info,
            enhanced=enhance_audio,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech with caching and enhancement
    """
    try:
        # Check cache first
        cached_audio = audio_cache.get_cached_audio(
            text=request.text,
            language=request.language,
            voice=request.voice,
            model=request.model_preference
        )
        
        if cached_audio and not request.force_regenerate:
            logger.info(f"Serving cached audio for: {request.text[:50]}...")
            
            # Apply enhancement if requested
            if request.enhance_output:
                enhancement_result = voice_enhancer.enhance_audio(
                    cached_audio.audio_data, 
                    cached_audio.content_type
                )
                audio_data = enhancement_result.enhanced_audio
                content_type = "audio/wav"  # Enhanced audio is always WAV
            else:
                audio_data = cached_audio.audio_data
                content_type = cached_audio.content_type
            
            return StreamingResponse(
                io.BytesIO(audio_data),
                media_type=content_type,
                headers={
                    "Content-Disposition": "attachment; filename=synthesized.wav",
                    "X-Sample-Rate": str(cached_audio.sample_rate),
                    "X-Duration": str(cached_audio.duration),
                    "X-Model-Used": cached_audio.model_used,
                    "X-From-Cache": "true",
                    "X-Enhanced": str(request.enhance_output)
                }
            )
        
        # Generate new audio
        tts_result = await models_client.text_to_speech(
            text=request.text,
            language=request.language,
            voice=request.voice,
            model_preference=request.model_preference
        )
        
        if not tts_result.success:
            raise HTTPException(status_code=500, detail=tts_result.error)
        
        audio_data = tts_result.audio_data
        content_type = tts_result.content_type
        
        # Cache the generated audio
        if request.cache_audio and audio_data:
            cache_key = audio_cache.cache_audio(
                text=request.text,
                language=request.language,
                audio_data=audio_data,
                content_type=content_type,
                sample_rate=tts_result.sample_rate,
                duration=tts_result.duration,
                model_used=tts_result.model_used,
                voice=request.voice
            )
            logger.info(f"Cached audio with key: {cache_key}")
        
        # Apply enhancement if requested
        if request.enhance_output and audio_data:
            enhancement_result = voice_enhancer.enhance_audio(audio_data, content_type)
            audio_data = enhancement_result.enhanced_audio
            content_type = "audio/wav"  # Enhanced audio is always WAV
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type=content_type,
            headers={
                "Content-Disposition": "attachment; filename=synthesized.wav",
                "X-Sample-Rate": str(tts_result.sample_rate),
                "X-Duration": str(tts_result.duration),
                "X-Model-Used": tts_result.model_used,
                "X-From-Cache": "false",
                "X-Enhanced": str(request.enhance_output)
            }
        )
        
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enhance")
async def enhance_audio(
    audio: UploadFile = File(..., description="Audio file to enhance"),
    settings: Optional[str] = Form(None, description="Enhancement settings as JSON")
):
    """
    Enhance audio quality
    """
    try:
        audio_data = await audio.read()
        
        # Parse enhancement settings if provided
        if settings:
            import json
            enhancement_settings = json.loads(settings)
            voice_enhancer.configure_enhancement(enhancement_settings)
        
        # Enhance audio
        enhancement_result = voice_enhancer.enhance_audio(audio_data, audio.content_type)
        
        return StreamingResponse(
            io.BytesIO(enhancement_result.enhanced_audio),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=enhanced.wav",
                "X-Enhancement-Score": str(enhancement_result.improvement_score),
                "X-Processing-Time": str(enhancement_result.processing_time),
                "X-Enhancements-Applied": ",".join(enhancement_result.enhancements_applied),
                "X-Original-SNR": str(enhancement_result.original_metrics.snr_ratio),
                "X-Enhanced-SNR": str(enhancement_result.enhanced_metrics.snr_ratio)
            }
        )
        
    except Exception as e:
        logger.error(f"Audio enhancement error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages/stt")
async def get_stt_languages():
    """Get supported STT languages"""
    try:
        models_languages = await models_client.get_supported_languages("stt")
        detector_languages = language_detector.get_supported_languages()
        
        return {
            "models_service": models_languages,
            "language_detector": detector_languages,
            "enhanced_languages": list(detector_languages.keys())
        }
    except Exception as e:
        logger.error(f"Failed to get STT languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages/tts")
async def get_tts_languages():
    """Get supported TTS languages"""
    try:
        return await models_client.get_supported_languages("tts")
    except Exception as e:
        logger.error(f"Failed to get TTS languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=VoiceStatusResponse)
async def get_voice_status():
    """Get comprehensive voice service status"""
    try:
        # Check all components
        models_health = await models_client.health_check(use_cache=False)
        enhancer_health = voice_enhancer.health_check()
        cache_health = audio_cache.health_check()
        detector_health = language_detector.health_check()
        
        # Determine overall status
        component_statuses = [
            models_health.get("status") == "healthy",
            enhancer_health.get("status") == "healthy", 
            cache_health.get("status") in ["healthy", "degraded"],
            detector_health.get("status") == "healthy"
        ]
        
        overall_status = "healthy" if all(component_statuses) else "degraded"
        if models_health.get("status") != "healthy":
            overall_status = "unhealthy"  # Models service is critical
        
        return VoiceStatusResponse(
            status=overall_status,
            components={
                "models_service": models_health,
                "voice_enhancer": enhancer_health,
                "audio_cache": cache_health,
                "language_detector": detector_health
            },
            features={
                "stt": models_health.get("status") == "healthy",
                "tts": models_health.get("status") == "healthy",
                "enhancement": enhancer_health.get("status") == "healthy",
                "caching": cache_health.get("status") in ["healthy", "degraded"],
                "language_detection": detector_health.get("status") == "healthy",
                "multi_language": True,
                "indian_languages": True
            },
            cache_stats=cache_health.get("total_entries", 0)
        )
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return VoiceStatusResponse(
            status="error",
            components={},
            features={},
            error=str(e)
        )
