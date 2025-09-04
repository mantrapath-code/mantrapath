"""
Models Service Client
Enhanced client for communicating with the Models Service
"""
import httpx
import os
import logging
from typing import Optional, Dict, Any, Union
import json
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class STTResult:
    """Speech-to-Text result structure"""
    text: str
    confidence: float
    language: str
    model_used: str
    success: bool = True
    error: Optional[str] = None

@dataclass
class TTSResult:
    """Text-to-Speech result structure"""
    audio_data: bytes
    content_type: str
    sample_rate: int
    duration: float
    model_used: str
    success: bool = True
    error: Optional[str] = None

@dataclass
class SentimentResult:
    """Sentiment analysis result structure"""
    sentiment: str
    confidence: float
    scores: Dict[str, float]
    success: bool = True
    error: Optional[str] = None

class ModelsServiceClient:
    """Enhanced client for Models Service communication"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 30.0):
        self.base_url = base_url or os.getenv("MODELS_SERVICE_URL", "http://models-service:8080")
        self.timeout = timeout
        self._health_cache = None
        self._health_cache_time = 0
        self._cache_ttl = 30  # seconds
        
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make HTTP request with error handling"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.base_url}{endpoint}"
            response = await getattr(client, method.lower())(url, **kwargs)
            return response
    
    async def health_check(self, use_cache: bool = True) -> Dict[str, Any]:
        """Check if Models Service is available with caching"""
        import time
        
        # Use cache if recent
        if use_cache and self._health_cache and (time.time() - self._health_cache_time) < self._cache_ttl:
            return self._health_cache
            
        try:
            response = await self._make_request("GET", "/health")
            if response.status_code == 200:
                result = {
                    "status": "healthy",
                    "models_service": "available",
                    "connection": "active",
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            else:
                result = {
                    "status": "unhealthy", 
                    "models_service": "unavailable",
                    "connection": "failed",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Models Service health check failed: {e}")
            result = {
                "status": "unhealthy",
                "models_service": "unavailable", 
                "connection": "failed",
                "error": str(e)
            }
        
        # Cache result
        self._health_cache = result
        self._health_cache_time = time.time()
        return result
    
    async def speech_to_text(self, audio_data: bytes, language: str = "auto", 
                           model_preference: Optional[str] = None) -> STTResult:
        """Enhanced Speech-to-Text with structured result"""
        try:
            files = {"audio": ("audio.wav", audio_data, "audio/wav")}
            data = {"language": language}
            if model_preference:
                data["model_preference"] = model_preference
            
            response = await self._make_request("POST", "/api/v1/stt/transcribe", files=files, data=data)
            
            if response.status_code == 200:
                result_data = response.json()
                return STTResult(
                    text=result_data.get("text", ""),
                    confidence=result_data.get("confidence", 0.0),
                    language=result_data.get("language", language),
                    model_used=result_data.get("model_used", "unknown"),
                    success=True
                )
            else:
                error_msg = f"Models Service returned {response.status_code}: {response.text}"
                return STTResult(
                    text="", confidence=0.0, language=language, 
                    model_used="none", success=False, error=error_msg
                )
                
        except Exception as e:
            logger.error(f"STT request failed: {e}")
            error_msg = f"STT request failed: {str(e)}"
            return STTResult(
                text="", confidence=0.0, language=language,
                model_used="none", success=False, error=error_msg
            )
    
    async def text_to_speech(self, text: str, language: str = "en", 
                           voice: Optional[str] = None, model_preference: Optional[str] = None) -> TTSResult:
        """Enhanced Text-to-Speech with structured result"""
        try:
            request_data = {"text": text, "language": language}
            if voice:
                request_data["voice"] = voice
            if model_preference:
                request_data["model_preference"] = model_preference
            
            response = await self._make_request("POST", "/api/v1/tts/synthesize", json=request_data)
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "audio/wav")
                if "audio" in content_type:
                    return TTSResult(
                        audio_data=response.content,
                        content_type=content_type,
                        sample_rate=int(response.headers.get("X-Sample-Rate", "22050")),
                        duration=float(response.headers.get("X-Duration", "0.0")),
                        model_used=response.headers.get("X-Model-Used", "unknown"),
                        success=True
                    )
                else:
                    # JSON response
                    result_data = response.json()
                    if result_data.get("success"):
                        return TTSResult(
                            audio_data=b"",  # No direct audio data
                            content_type="application/json",
                            sample_rate=result_data.get("sample_rate", 22050),
                            duration=result_data.get("duration", 0.0),
                            model_used=result_data.get("model_used", "unknown"),
                            success=True
                        )
            
            error_msg = f"Models Service returned {response.status_code}: {response.text}"
            return TTSResult(
                audio_data=b"", content_type="", sample_rate=0, duration=0.0,
                model_used="none", success=False, error=error_msg
            )
                
        except Exception as e:
            logger.error(f"TTS request failed: {e}")
            error_msg = f"TTS request failed: {str(e)}"
            return TTSResult(
                audio_data=b"", content_type="", sample_rate=0, duration=0.0,
                model_used="none", success=False, error=error_msg
            )
    
    async def analyze_sentiment(self, text: str, language: str = "en") -> SentimentResult:
        """Enhanced sentiment analysis with structured result"""
        try:
            data = {"text": text, "language": language}
            response = await self._make_request("POST", "/api/v1/nlp/sentiment", data=data)
            
            if response.status_code == 200:
                result_data = response.json()
                return SentimentResult(
                    sentiment=result_data.get("sentiment", "neutral"),
                    confidence=result_data.get("confidence", 0.0),
                    scores=result_data.get("scores", {}),
                    success=True
                )
            else:
                error_msg = f"Sentiment analysis failed: {response.status_code}"
                return SentimentResult(
                    sentiment="neutral", confidence=0.0, scores={},
                    success=False, error=error_msg
                )
                
        except Exception as e:
            logger.error(f"Sentiment analysis request failed: {e}")
            error_msg = f"Sentiment analysis failed: {str(e)}"
            return SentimentResult(
                sentiment="neutral", confidence=0.0, scores={},
                success=False, error=error_msg
            )
    
    async def get_supported_languages(self, service_type: str) -> Dict[str, Any]:
        """Get supported languages from Models Service"""
        try:
            response = await self._make_request("GET", f"/api/v1/{service_type}/languages")
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"Failed to get languages: {response.status_code}",
                    "supported_languages": {}
                }
                
        except Exception as e:
            logger.error(f"Get languages request failed: {e}")
            return {
                "success": False,
                "error": f"Get languages failed: {str(e)}",
                "supported_languages": {}
            }
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Translate text using Models Service"""
        try:
            data = {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang
            }
            response = await self._make_request("POST", "/api/v1/nlp/translate", data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"Translation failed: {response.status_code}",
                    "translated_text": ""
                }
                
        except Exception as e:
            logger.error(f"Translation request failed: {e}")
            return {
                "success": False,
                "error": f"Translation failed: {str(e)}",
                "translated_text": ""
            }
