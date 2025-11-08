"""Voice Service Client for STT and voice emotion integration."""

import logging
import httpx
import asyncio
from typing import Dict, Any, Optional
from src.core.config import settings

logger = logging.getLogger(__name__)


class VoiceServiceClient:
    """Client for Voice Service and Voice Event Processor integration."""
    
    def __init__(self):
        """Initialize the voice service client."""
        self.voice_service_url = getattr(settings, 'voice_service_url', 'http://voice-service:8011')
        self.voice_event_processor_url = getattr(settings, 'voice_event_processor_url', 'http://voice-event-processor:8015')
        self.timeout = 30.0
    
    async def speech_to_text(self, audio_data: bytes, language: str = "auto") -> str:
        """
        Send audio to Voice Service for transcription.
        
        Args:
            audio_data: Raw audio bytes
            language: Language code for transcription
            
        Returns:
            Transcribed text
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                files = {"audio": ("audio.wav", audio_data, "audio/wav")}
                data = {"language": language}
                
                response = await client.post(
                    f"{self.voice_service_url}/api/v1/voice/stt",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("success", False):
                    return result.get("text", "")
                else:
                    logger.error(f"STT failed: {result.get('error', 'Unknown error')}")
                    return ""
                    
        except httpx.TimeoutException:
            logger.error("STT request timed out")
            return ""
        except httpx.HTTPStatusError as e:
            logger.error(f"STT HTTP error: {e.response.status_code}")
            return ""
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""
    
    async def get_voice_emotions(self, audio_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Get voice tone emotions from Voice Event Processor.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Voice emotion analysis results
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                files = {"audio": ("audio.wav", audio_data, "audio/wav")}
                
                response = await client.post(
                    f"{self.voice_event_processor_url}/api/v1/voice/analyze-emotion",
                    files=files
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get("success", False):
                    return result.get("emotion_analysis", {})
                else:
                    logger.error(f"Voice emotion analysis failed: {result.get('error', 'Unknown error')}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error("Voice emotion analysis request timed out")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Voice emotion analysis HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Voice emotion analysis error: {e}")
            return None
    
    async def analyze_voice_conversation(self, audio_data: bytes, language: str = "auto") -> Dict[str, Any]:
        """
        Analyze voice conversation for both transcription and emotions.
        
        Args:
            audio_data: Raw audio bytes
            language: Language code
            
        Returns:
            Combined transcription and emotion analysis
        """
        try:
            # Run STT and voice emotion analysis in parallel
            stt_task = asyncio.create_task(self.speech_to_text(audio_data, language))
            emotion_task = asyncio.create_task(self.get_voice_emotions(audio_data))
            
            # Wait for both to complete
            transcribed_text, voice_emotions = await asyncio.gather(
                stt_task, emotion_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(transcribed_text, Exception):
                logger.error(f"STT task failed: {transcribed_text}")
                transcribed_text = ""
            
            if isinstance(voice_emotions, Exception):
                logger.error(f"Voice emotion task failed: {voice_emotions}")
                voice_emotions = None
            
            return {
                "transcribed_text": transcribed_text,
                "voice_emotions": voice_emotions,
                "success": bool(transcribed_text),
                "language": language
            }
            
        except Exception as e:
            logger.error(f"Voice conversation analysis error: {e}")
            return {
                "transcribed_text": "",
                "voice_emotions": None,
                "success": False,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of voice services."""
        health_status = {
            "voice_service": False,
            "voice_event_processor": False,
            "overall": False
        }
        
        try:
            # Check Voice Service
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.voice_service_url}/health")
                health_status["voice_service"] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Voice Service health check failed: {e}")
        
        try:
            # Check Voice Event Processor
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.voice_event_processor_url}/health")
                health_status["voice_event_processor"] = response.status_code == 200
        except Exception as e:
            logger.warning(f"Voice Event Processor health check failed: {e}")
        
        health_status["overall"] = health_status["voice_service"] and health_status["voice_event_processor"]
        
        return health_status
    
    def get_service_urls(self) -> Dict[str, str]:
        """Get the configured service URLs."""
        return {
            "voice_service": self.voice_service_url,
            "voice_event_processor": self.voice_event_processor_url
        }


# Global instance
voice_service_client = VoiceServiceClient()


