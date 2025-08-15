"""
Voice Endpoints for Enhanced API Gateway V3
Provides voice command processing endpoints with WebSocket support
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from src.voice import (
    VoiceCommandRouter, VoiceRoutingMiddleware, 
    MultilingualVoiceSupport, VoiceIntentClassifier
)

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Initialize voice components
ml_support = MultilingualVoiceSupport()
intent_classifier = VoiceIntentClassifier()
voice_router = VoiceCommandRouter(intent_classifier)
voice_middleware = VoiceRoutingMiddleware(voice_router)

# Router for voice endpoints
voice_api = APIRouter(prefix="/voice", tags=["voice"])


# Pydantic models for requests/responses
class VoiceCommandRequest(BaseModel):
    """Voice command request model"""
    text: str = Field(..., description="Voice command text")
    language: Optional[str] = Field("en", description="Language code")
    cultural_context: Optional[str] = Field(None, description="Cultural context")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")


class VoiceCommandResponse(BaseModel):
    """Voice command response model"""
    success: bool
    target_service: Optional[str] = None
    endpoint: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class LanguageDetectionRequest(BaseModel):
    """Language detection request model"""
    text: str = Field(..., description="Text to analyze")
    hint: Optional[str] = Field(None, description="Language hint")


class LanguageDetectionResponse(BaseModel):
    """Language detection response model"""
    detected_language: str
    confidence: float
    cultural_context: Optional[str] = None
    supported: bool


class VoiceCapabilitiesResponse(BaseModel):
    """Voice capabilities response model"""
    supported_languages: List[Dict[str, Any]]
    supported_intents: List[str]
    cultural_regions: List[str]
    voice_examples: Dict[str, List[Dict[str, str]]]


# WebSocket connection manager
class VoiceWebSocketManager:
    """Manages WebSocket connections for voice streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: Optional[str] = None):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.connection_metadata[session_id] = {
            "user_id": user_id,
            "connected_at": datetime.now(timezone.utc),
            "language": "en",
            "cultural_context": None,
            "message_count": 0
        }
        logger.info(f"Voice WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """Handle WebSocket disconnection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.connection_metadata:
            del self.connection_metadata[session_id]
        logger.info(f"Voice WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, Any]):
        """Send message to specific WebSocket"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
                self.connection_metadata[session_id]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connections"""
        for session_id in list(self.active_connections.keys()):
            await self.send_message(session_id, message)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "total_messages": sum(
                meta["message_count"] for meta in self.connection_metadata.values()
            ),
            "connections": [
                {
                    "session_id": session_id,
                    "user_id": meta["user_id"],
                    "connected_at": meta["connected_at"].isoformat(),
                    "language": meta["language"],
                    "message_count": meta["message_count"]
                }
                for session_id, meta in self.connection_metadata.items()
            ]
        }


# Initialize WebSocket manager
ws_manager = VoiceWebSocketManager()


@voice_api.post("/command", response_model=VoiceCommandResponse)
async def process_voice_command(
    request: VoiceCommandRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Process a voice command and route to appropriate service
    
    This endpoint handles voice command classification, intent detection,
    and routing to the appropriate microservice.
    """
    try:
        # Extract user ID from token if available
        user_id = request.user_id
        if credentials and not user_id:
            # In production, decode JWT to get user_id
            user_id = "authenticated_user"
        
        # Detect language if not provided
        language = request.language
        if not language or language == "auto":
            language = await ml_support.detect_language(request.text)
        
        # Get cultural context if not provided
        cultural_context = request.cultural_context
        if not cultural_context:
            cultural_context = ml_support.get_cultural_context(language)
        
        # Process voice command
        request_data = {
            "text": request.text,
            "language": language,
            "user_id": user_id,
            "cultural_context": cultural_context
        }
        
        result = await voice_middleware.process_voice_request(request_data)
        
        # Create response
        response = VoiceCommandResponse(
            success=result["success"],
            target_service=result.get("target_service"),
            endpoint=result.get("endpoint"),
            intent=result.get("rule", {}).get("intent") if result.get("rule") else None,
            processing_time_ms=result.get("processing_time_ms"),
            error_message=result.get("error")
        )
        
        logger.info(
            f"Voice command processed: intent={response.intent}, "
            f"service={response.target_service}, success={response.success}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Voice command processing error: {e}", exc_info=True)
        return VoiceCommandResponse(
            success=False,
            error_message=f"Processing error: {str(e)}"
        )


@voice_api.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: LanguageDetectionRequest):
    """
    Detect language from text input
    
    Analyzes text to determine the most likely language and provides
    cultural context information.
    """
    try:
        detected_lang = await ml_support.detect_language(request.text, request.hint)
        cultural_context = ml_support.get_cultural_context(detected_lang)
        is_supported = ml_support.is_language_supported(detected_lang)
        
        # Simple confidence calculation (in production, use proper ML model)
        confidence = 0.95 if request.hint == detected_lang else 0.80
        
        return LanguageDetectionResponse(
            detected_language=detected_lang,
            confidence=confidence,
            cultural_context=cultural_context,
            supported=is_supported
        )
        
    except Exception as e:
        logger.error(f"Language detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")


@voice_api.get("/capabilities", response_model=VoiceCapabilitiesResponse)
async def get_voice_capabilities():
    """
    Get voice system capabilities and supported features
    
    Returns information about supported languages, intents, cultural regions,
    and example voice commands.
    """
    try:
        # Get supported languages with details
        supported_languages = []
        for lang_code, lang_support in ml_support.supported_languages.items():
            supported_languages.append({
                "code": lang_code,
                "name": lang_support.name,
                "support_level": lang_support.support_level,
                "cultural_context": lang_support.cultural_context,
                "regional_variants": lang_support.regional_variants
            })
        
        # Get supported intents
        supported_intents = [intent.value for intent in voice_router.get_supported_intents()]
        
        # Get cultural regions
        cultural_regions = list(ml_support.cultural_regions.keys())
        
        # Get voice examples for major languages
        voice_examples = {}
        for lang in ["en", "hi", "es", "fr", "de"]:
            if ml_support.is_language_supported(lang):
                voice_examples[lang] = ml_support.get_voice_examples_for_language(lang)
        
        return VoiceCapabilitiesResponse(
            supported_languages=supported_languages,
            supported_intents=supported_intents,
            cultural_regions=cultural_regions,
            voice_examples=voice_examples
        )
        
    except Exception as e:
        logger.error(f"Capabilities retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")


@voice_api.get("/statistics")
async def get_voice_statistics(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get voice system statistics and performance metrics
    
    Requires authentication and returns detailed statistics about
    voice command processing, routing performance, and language usage.
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Get routing statistics
        routing_stats = voice_router.get_routing_statistics()
        
        # Get language statistics
        language_stats = ml_support.get_language_statistics()
        
        # Get WebSocket statistics
        ws_stats = ws_manager.get_connection_stats()
        
        return {
            "routing": routing_stats,
            "languages": language_stats,
            "websockets": ws_stats,
            "system": {
                "total_intents": len(voice_router.get_supported_intents()),
                "total_routing_rules": routing_stats.get("total_rules", 0),
                "uptime": "calculated_in_production"
            }
        }
        
    except Exception as e:
        logger.error(f"Statistics retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@voice_api.websocket("/stream/{session_id}")
async def voice_stream_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time voice streaming
    
    Handles voice streaming, real-time transcription, and voice command processing.
    Supports continuous voice interaction with immediate feedback.
    """
    user_id = None  # Extract from query params or headers in production
    
    try:
        await ws_manager.connect(websocket, session_id, user_id)
        
        # Send welcome message
        await ws_manager.send_message(session_id, {
            "type": "welcome",
            "session_id": session_id,
            "capabilities": {
                "languages": ["en", "hi", "es", "fr", "de"],
                "intents": [intent.value for intent in voice_router.get_supported_intents()],
                "real_time": True
            }
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "voice_command":
                # Process voice command
                command_data = message.get("data", {})
                result = await voice_middleware.process_voice_request(command_data)
                
                # Send response
                await ws_manager.send_message(session_id, {
                    "type": "voice_response",
                    "data": result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
            elif message_type == "language_detection":
                # Detect language
                text = message.get("data", {}).get("text", "")
                detected_lang = ml_support.detect_language(text)
                cultural_context = ml_support.get_cultural_context(detected_lang)
                
                await ws_manager.send_message(session_id, {
                    "type": "language_detected",
                    "data": {
                        "language": detected_lang,
                        "cultural_context": cultural_context,
                        "supported": ml_support.is_language_supported(detected_lang)
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
            elif message_type == "ping":
                # Respond to ping
                await ws_manager.send_message(session_id, {
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
            else:
                # Unknown message type
                await ws_manager.send_message(session_id, {
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message_type}"},
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
    except WebSocketDisconnect:
        logger.info(f"Voice WebSocket disconnected: {session_id}")
        ws_manager.disconnect(session_id)
        
    except Exception as e:
        logger.error(f"Voice WebSocket error for {session_id}: {e}", exc_info=True)
        try:
            await ws_manager.send_message(session_id, {
                "type": "error",
                "data": {"message": f"Server error: {str(e)}"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except:
            pass
        ws_manager.disconnect(session_id)


# Health check for voice system
@voice_api.get("/health")
async def voice_health_check():
    """Voice system health check"""
    try:
        # Test basic components
        test_command = voice_router.route_voice_command("test", "en", "health_check")
        
        return {
            "status": "healthy",
            "voice_router": "operational",
            "ml_support": "operational",
            "intent_classifier": "operational",
            "supported_languages": len(ml_support.supported_languages),
            "routing_rules": len(voice_router.routing_rules),
            "active_websockets": len(ws_manager.active_connections),
            "test_routing": test_command.success is not None
        }
        
    except Exception as e:
        logger.error(f"Voice health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Export the router
__all__ = ["voice_api", "ws_manager"]
