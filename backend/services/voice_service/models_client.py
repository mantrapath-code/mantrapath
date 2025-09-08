"""
Models Service Client for Voice Service
Handles communication with the Models Service
"""
import httpx
import os
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

class ModelsServiceClient:
    def __init__(self):
        self.base_url = os.getenv("MODELS_SERVICE_URL", "http://models-service:8080")
        self.timeout = 30.0
        
    async def health_check(self) -> Dict[str, Any]:
        """Check if Models Service is available"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "models_service": "available",
                        "connection": "active"
                    }
                else:
                    return {
                        "status": "unhealthy", 
                        "models_service": "unavailable",
                        "connection": "failed",
                        "error": f"HTTP {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"Models Service health check failed: {e}")
            return {
                "status": "unhealthy",
                "models_service": "unavailable", 
                "connection": "failed",
                "error": str(e)
            }
    
    async def speech_to_text(self, audio_data: bytes, language: str = "auto", model_preference: Optional[str] = None) -> Dict[str, Any]:
        """Send audio to Models Service for transcription"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                files = {"audio": ("audio.wav", audio_data, "audio/wav")}
                data = {
                    "language": language,
                }
                if model_preference:
                    data["model_preference"] = model_preference
                
                response = await client.post(
                    f"{self.base_url}/api/v1/stt/transcribe",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"Models Service returned {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"STT request failed: {e}")
            return {
                "success": False,
                "error": f"STT request failed: {str(e)}"
            }
    
    async def text_to_speech(self, text: str, language: str = "en", voice: Optional[str] = None, model_preference: Optional[str] = None) -> Dict[str, Any]:
        """Send text to Models Service for synthesis"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                request_data = {
                    "text": text,
                    "language": language
                }
                if voice:
                    request_data["voice"] = voice
                if model_preference:
                    request_data["model_preference"] = model_preference
                
                response = await client.post(
                    f"{self.base_url}/api/v1/tts/synthesize",
                    json=request_data
                )
                
                if response.status_code == 200:
                    # Check if response is audio data
                    content_type = response.headers.get("content-type", "")
                    if "audio" in content_type:
                        return {
                            "success": True,
                            "audio_data": response.content,
                            "content_type": content_type,
                            "sample_rate": response.headers.get("X-Sample-Rate"),
                            "duration": response.headers.get("X-Duration"),
                            "model_used": response.headers.get("X-Model-Used")
                        }
                    else:
                        return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"Models Service returned {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"TTS request failed: {e}")
            return {
                "success": False,
                "error": f"TTS request failed: {str(e)}"
            }
    
    async def get_supported_languages(self, service_type: str) -> Dict[str, Any]:
        """Get supported languages from Models Service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/{service_type}/languages")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"Failed to get languages: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Get languages request failed: {e}")
            return {
                "success": False,
                "error": f"Get languages failed: {str(e)}"
            }
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Analyze sentiment using Models Service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                data = {
                    "text": text,
                    "language": language
                }
                
                response = await client.post(
                    f"{self.base_url}/api/v1/nlp/sentiment",
                    data=data
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"Sentiment analysis failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Sentiment analysis request failed: {e}")
            return {
                "success": False,
                "error": f"Sentiment analysis failed: {str(e)}"
            }

# Global client instance
models_client = ModelsServiceClient()
