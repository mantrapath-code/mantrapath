"""
Voice Processing Service
Main business logic service for voice processing operations
"""
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from core.models import (
    VoiceCommand, TTSRequest, STTRequest, VoiceResponse, 
    AudioData, STTResult, EmotionAnalysis, VoiceStreamChunk
)
from core.exceptions import (
    VoiceServiceError, AudioProcessingError, UnsupportedLanguageError,
    AuthenticationError, AudioValidationError, FileSizeError, AudioDurationError
)
from engines.engine_manager import VoiceEngineManager
from config.settings import voice_config
from config.language_config import is_language_supported

logger = logging.getLogger(__name__)

class VoiceProcessingService:
    """Main voice processing service orchestrating all voice operations"""
    
    def __init__(self, engine_manager: VoiceEngineManager):
        self.engine_manager = engine_manager
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.processing_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "languages_processed": set(),
            "start_time": datetime.utcnow()
        }
        
    async def process_speech_to_text(
        self,
        audio_data: AudioData,
        request: STTRequest,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> VoiceResponse:
        """Process speech-to-text with comprehensive validation and error handling"""
        
        request_id = request_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Update stats
            self.processing_stats["total_requests"] += 1
            
            # Validate language support
            if not is_language_supported(request.language):
                raise UnsupportedLanguageError(request.language)
            
            # Validate audio data
            self._validate_audio_data(audio_data)
            
            # Process STT with engine manager
            result = await self.engine_manager.transcribe_audio(
                audio_data=audio_data,
                language=request.language,
                preferred_engine=request.model,
                enable_diarization=request.enable_diarization,
                translate_to_english=request.translate_to_english,
                confidence_threshold=request.confidence_threshold
            )
            
            # Add emotion analysis if enabled
            if request.enable_emotion_analysis:
                emotion_analysis = await self.engine_manager.analyze_emotion(audio_data)
                result.emotion_analysis = emotion_analysis
            
            # Update stats
            self.processing_stats["successful_requests"] += 1
            self.processing_stats["languages_processed"].add(request.language)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return VoiceResponse(
                success=True,
                message="Speech successfully converted to text",
                data={
                    "transcription": result.dict(),
                    "processing_time_ms": processing_time,
                    "engine_used": getattr(result, 'engine_used', 'unknown')
                },
                request_id=request_id,
                processing_time_ms=processing_time,
                language=request.language
            )
            
        except Exception as e:
            self.processing_stats["failed_requests"] += 1
            logger.error(f"STT processing failed for request {request_id}: {e}")
            
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise AudioProcessingError(f"STT processing failed: {str(e)}")
    
    async def process_text_to_speech(
        self,
        request: TTSRequest,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AudioData:
        """Process text-to-speech with comprehensive validation and error handling"""
        
        request_id = request_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Update stats
            self.processing_stats["total_requests"] += 1
            
            # Validate language support
            if not is_language_supported(request.language):
                raise UnsupportedLanguageError(request.language)
            
            # Validate text length
            if len(request.text) > voice_config.MAX_TEXT_LENGTH:
                raise AudioValidationError(f"Text length exceeds maximum of {voice_config.MAX_TEXT_LENGTH} characters")
            
            # Process TTS with engine manager
            audio_data = await self.engine_manager.synthesize_speech(
                text=request.text,
                language=request.language,
                voice_id=request.voice,
                preferred_engine=request.engine.value if request.engine else None,
                speed=request.speed,
                pitch=request.pitch,
                format=request.format.value
            )
            
            # Update stats
            self.processing_stats["successful_requests"] += 1
            self.processing_stats["languages_processed"].add(request.language)
            
            # Add metadata to audio data
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            audio_data.processing_time_ms = processing_time
            audio_data.request_id = request_id
            
            return audio_data
            
        except Exception as e:
            self.processing_stats["failed_requests"] += 1
            logger.error(f"TTS processing failed for request {request_id}: {e}")
            
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise AudioProcessingError(f"TTS processing failed: {str(e)}")
    
    async def analyze_voice_emotion(
        self,
        audio_data: AudioData,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> VoiceResponse:
        """Analyze emotion from voice audio"""
        
        request_id = request_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Validate audio data
            self._validate_audio_data(audio_data)
            
            # Process emotion analysis
            emotion_analysis = await self.engine_manager.analyze_emotion(audio_data)
            
            if not emotion_analysis:
                return VoiceResponse(
                    success=False,
                    message="Emotion analysis not available",
                    request_id=request_id
                )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return VoiceResponse(
                success=True,
                message="Voice emotion analysis completed",
                data={
                    "emotion_analysis": emotion_analysis.dict(),
                    "processing_time_ms": processing_time
                },
                request_id=request_id,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Emotion analysis failed for request {request_id}: {e}")
            
            if isinstance(e, VoiceServiceError):
                raise e
            else:
                raise AudioProcessingError(f"Emotion analysis failed: {str(e)}")
    
    def _validate_audio_data(self, audio_data: AudioData) -> None:
        """Validate audio data against service constraints"""
        
        # Check file size
        if audio_data.file_size and audio_data.file_size > voice_config.MAX_FILE_SIZE:
            raise FileSizeError(audio_data.file_size, voice_config.MAX_FILE_SIZE)
        elif len(audio_data.data) > voice_config.MAX_FILE_SIZE:
            raise FileSizeError(len(audio_data.data), voice_config.MAX_FILE_SIZE)
        
        # Check duration
        if audio_data.duration and audio_data.duration > voice_config.MAX_AUDIO_DURATION:
            raise AudioDurationError(audio_data.duration, voice_config.MAX_AUDIO_DURATION)
        
        # Check format
        if audio_data.format.value not in voice_config.SUPPORTED_AUDIO_FORMATS:
            raise UnsupportedFormatError(
                audio_data.format.value, 
                voice_config.SUPPORTED_AUDIO_FORMATS
            )
    
    async def create_processing_session(
        self,
        user_id: str,
        session_type: str = "general",
        language: str = "en",
        **kwargs
    ) -> str:
        """Create a processing session for batch or streaming operations"""
        
        session_id = str(uuid.uuid4())
        
        session_info = {
            "session_id": session_id,
            "user_id": user_id,
            "session_type": session_type,
            "language": language,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "processed_items": 0,
            "status": "active",
            "metadata": kwargs
        }
        
        self.active_sessions[session_id] = session_info
        
        logger.info(f"Created processing session {session_id} for user {user_id}")
        return session_id
    
    async def close_processing_session(self, session_id: str) -> bool:
        """Close a processing session"""
        
        if session_id not in self.active_sessions:
            return False
        
        session_info = self.active_sessions[session_id]
        session_info["status"] = "closed"
        session_info["closed_at"] = datetime.utcnow()
        
        # Remove from active sessions after a delay (for audit purposes)
        # In production, you might want to move this to a database
        del self.active_sessions[session_id]
        
        logger.info(f"Closed processing session {session_id}")
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a processing session"""
        return self.active_sessions.get(session_id)
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get service processing statistics"""
        
        uptime = datetime.utcnow() - self.processing_stats["start_time"]
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.processing_stats["total_requests"],
            "successful_requests": self.processing_stats["successful_requests"],
            "failed_requests": self.processing_stats["failed_requests"],
            "success_rate": (
                self.processing_stats["successful_requests"] / 
                max(1, self.processing_stats["total_requests"])
            ),
            "languages_processed": list(self.processing_stats["languages_processed"]),
            "active_sessions": len(self.active_sessions),
            "engine_status": await self._get_engine_status()
        }
    
    async def _get_engine_status(self) -> Dict[str, Any]:
        """Get engine manager status"""
        try:
            return await self.engine_manager.get_health_status()
        except Exception as e:
            logger.error(f"Failed to get engine status: {e}")
            return {"error": str(e)}
    
    async def get_supported_features(self) -> Dict[str, Any]:
        """Get supported features and capabilities"""
        
        return {
            "supported_languages": voice_config.SUPPORTED_LANGUAGES,
            "supported_audio_formats": voice_config.SUPPORTED_AUDIO_FORMATS,
            "max_file_size_mb": voice_config.MAX_FILE_SIZE / (1024 * 1024),
            "max_duration_seconds": voice_config.MAX_AUDIO_DURATION,
            "features": {
                "speech_to_text": True,
                "text_to_speech": True,
                "emotion_analysis": voice_config.emotion_analysis_enabled,
                "voice_cloning": voice_config.voice_cloning_enabled,
                "real_time_streaming": True,
                "multilingual_support": True,
                "voice_commands": True
            },
            "available_engines": self.engine_manager.get_available_engines(),
            "engine_capabilities": self.engine_manager.get_supported_languages()
        }
    
    async def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        expired_sessions = []
        
        for session_id, session_info in self.active_sessions.items():
            if session_info["last_activity"] < cutoff_time:
                expired_sessions.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
