"""
Voice Routing Middleware for API Gateway V3 Enhanced
Handles voice command detection and routing preparation
"""

import time
import logging
from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from ..services.voice_router import VoiceCommandRouter
from ..models.voice_models import VoiceCommand, VoiceIntentType
from ..utils.language_detector import LanguageDetector

logger = structlog.get_logger(__name__)


class VoiceRoutingMiddleware(BaseHTTPMiddleware):
    """Middleware for voice command routing and preparation"""
    
    def __init__(self, app, voice_router: VoiceCommandRouter):
        super().__init__(app)
        self.voice_router = voice_router
        self.language_detector = LanguageDetector()
        self.stats = {
            "total_requests": 0,
            "voice_requests": 0,
            "routing_errors": 0,
            "avg_processing_time": 0.0
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through voice routing middleware"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        # Check if this is a voice-related request
        is_voice_request = self._is_voice_request(request)
        
        if is_voice_request:
            self.stats["voice_requests"] += 1
            
            # Add voice processing headers
            request.state.is_voice_request = True
            request.state.voice_processing_start = start_time
            
            # Pre-process voice command if needed
            await self._preprocess_voice_request(request)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Post-process voice response if needed
            if is_voice_request:
                response = await self._postprocess_voice_response(request, response)
            
            # Update processing time stats
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=True)
            
            return response
            
        except Exception as e:
            self.stats["routing_errors"] += 1
            processing_time = time.time() - start_time
            self._update_stats(processing_time, success=False)
            logger.error("Voice routing middleware error", error=str(e))
            return JSONResponse(
                status_code=500,
                content={"error": "Voice routing processing failed"}
            )
    
    def _is_voice_request(self, request: Request) -> bool:
        """Determine if this is a voice-related request"""
        # Check URL patterns
        voice_patterns = [
            "/api/v3/voice/",
            "/voice/",
            "/speech/"
        ]
        
        if any(pattern in request.url.path for pattern in voice_patterns):
            return True
        
        # Check headers
        voice_headers = [
            "x-voice-command",
            "x-speech-input",
            "content-type: audio/"
        ]
        
        for header_name, header_value in request.headers.items():
            header_check = f"{header_name.lower()}: {header_value.lower()}"
            if any(pattern in header_check for pattern in voice_headers):
                return True
        
        # Check for voice intent in query params
        if "voice_intent" in request.query_params:
            return True
        
        return False
    
    async def _preprocess_voice_request(self, request: Request):
        """Preprocess voice request for enhanced routing"""
        try:
            # Extract voice command information
            voice_info = await self._extract_voice_info(request)
            
            if voice_info:
                # Store voice information in request state
                request.state.voice_intent = voice_info.get("intent")
                request.state.voice_language = voice_info.get("language")
                request.state.voice_confidence = voice_info.get("confidence")
                request.state.voice_parameters = voice_info.get("parameters", {})
                
                logger.info(
                    "Voice request preprocessed",
                    intent=voice_info.get("intent"),
                    language=voice_info.get("language"),
                    confidence=voice_info.get("confidence"),
                    path=request.url.path
                )
        
        except Exception as e:
            logger.exception(
                "Voice preprocessing failed",
                error=str(e),
                path=request.url.path
            )
            # Don't fail the request for preprocessing errors
    
    async def _extract_voice_info(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract voice command information from request"""
        voice_info = {}
        
        # Check headers for voice intent
        voice_intent = request.headers.get("x-voice-intent")
        if voice_intent:
            voice_info["intent"] = voice_intent
        
        # Check for language information
        language = request.headers.get("x-language") or request.headers.get("accept-language")
        if language:
            # Parse language header (e.g., "en-US,en;q=0.9" -> "en")
            primary_language = language.split(",")[0].split("-")[0]
            voice_info["language"] = primary_language
        
        # Check for confidence score
        confidence = request.headers.get("x-voice-confidence")
        if confidence:
            try:
                voice_info["confidence"] = float(confidence)
            except ValueError:
                pass
        
        # Extract parameters from query string for voice commands
        voice_params = {}
        for key, value in request.query_params.items():
            if key.startswith("voice_"):
                param_name = key[6:]  # Remove "voice_" prefix
                voice_params[param_name] = value
        
        if voice_params:
            voice_info["parameters"] = voice_params
        
        return voice_info if voice_info else None
    
    async def _postprocess_voice_response(self, request: Request, response: Response) -> Response:
        """Post-process response for voice requests"""
        try:
            # Add voice-specific headers to response
            if hasattr(request.state, "voice_intent"):
                response.headers["X-Voice-Intent-Processed"] = request.state.voice_intent
            
            if hasattr(request.state, "voice_language"):
                response.headers["X-Voice-Language"] = request.state.voice_language
            
            # Add processing time
            if hasattr(request.state, "voice_processing_start"):
                processing_time = (time.time() - request.state.voice_processing_start) * 1000
                response.headers["X-Voice-Processing-Time"] = str(round(processing_time, 2))
            
            # Add voice routing information
            response.headers["X-Voice-Routing"] = "enhanced"
            
            logger.info(
                "Voice response post-processed",
                path=request.url.path,
                status_code=response.status_code,
                intent=getattr(request.state, "voice_intent", None)
            )
        
        except Exception as e:
            logger.exception(
                "Voice response post-processing failed",
                error=str(e),
                path=request.url.path
            )
            # Don't fail the response for post-processing errors
        
        return response
    
    def _update_stats(self, processing_time: float, success: bool):
        """Update processing statistics"""
        # Update average processing time using exponential moving average
        alpha = 0.1  # Smoothing factor
        if self.stats["avg_processing_time"] == 0:
            self.stats["avg_processing_time"] = processing_time
        else:
            self.stats["avg_processing_time"] = (
                alpha * processing_time + 
                (1 - alpha) * self.stats["avg_processing_time"]
            )
        
        # Update success/error rates
        if not success:
            self.stats["routing_errors"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics"""
        voice_request_ratio = (
            self.stats["voice_requests"] / self.stats["total_requests"] 
            if self.stats["total_requests"] > 0 else 0
        )
        
        error_rate = (
            self.stats["routing_errors"] / self.stats["total_requests"]
            if self.stats["total_requests"] > 0 else 0
        )
        
        return {
            **self.stats,
            "voice_request_ratio": round(voice_request_ratio, 3),
            "error_rate": round(error_rate, 3),
            "avg_processing_time": round(self.stats["avg_processing_time"], 2)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for voice routing middleware"""
        try:
            # Test voice router health
            router_health = await self.voice_router.health_check()
            
            # Check language detector
            detector_health = await self.language_detector.health_check()
            
            # Check middleware stats
            stats = self.get_stats()
            healthy = (
                router_health.get("status") == "healthy" and
                detector_health.get("status") == "healthy" and
                stats["error_rate"] < 0.1  # Less than 10% error rate
            )
            
            return {
                "status": "healthy" if healthy else "degraded",
                "voice_router": router_health,
                "language_detector": detector_health,
                "middleware_stats": stats,
                "timestamp": time.time()
            }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
