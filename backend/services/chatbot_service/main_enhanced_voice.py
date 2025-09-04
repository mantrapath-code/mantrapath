"""
Enhanced Chatbot Service with Voice Integration and Multi-Language Support

This service provides comprehensive voice-enabled chatbot functionality with:
- Multi-language voice support with auto-detection
- Platform-aware context (mood, journal, community data)
- Cultural and sentiment analysis
- Action orchestrator integration
- Advanced conversation memory
- Real-time voice processing

Author: MantraPath Development Team
Version: 3.0.0 (Voice Enhanced)
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import httpx
import json

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Add parent directories to path for shared imports
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import ChatSession, ChatMessage, Base
from shared.auth import get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Service URLs configuration
SERVICE_URLS = {
    'voice_service': os.getenv('VOICE_SERVICE_URL', 'http://voice-service:8011'),
    'voice_event_processor': os.getenv('VOICE_EVENT_PROCESSOR_URL', 'http://voice-event-processor:8015'),
    'translation_service': os.getenv('TRANSLATION_SERVICE_URL', 'http://translation-service:8010'),
    'models_service': os.getenv('MODELS_SERVICE_URL', 'http://models-service:8080'),
    'action_orchestrator': os.getenv('ACTION_ORCHESTRATOR_URL', 'http://action-orchestrator:8012'),
    'ai_context_store': os.getenv('AI_CONTEXT_STORE_URL', 'http://ai-context-store:8013'),
    'ai_event_processor': os.getenv('AI_EVENT_PROCESSOR_URL', 'http://ai-event-processor:8014'),
    'mood_service': os.getenv('MOOD_SERVICE_URL', 'http://mood-service:8003'),
    'profile_service': os.getenv('PROFILE_SERVICE_URL', 'http://profile-service:8002'),
    'content_service': os.getenv('CONTENT_SERVICE_URL', 'http://content-service:8005'),
    'community_service': os.getenv('COMMUNITY_SERVICE_URL', 'http://community-service:8006'),
    'memory_service': os.getenv('MEMORY_SERVICE_URL', 'http://memory-service:8017'),
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Enhanced Chatbot Service v3.0.0 with Voice Integration")
    
    # Initialize HTTP client for service communication
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    app.state.conversation_cache = {}
    app.state.language_cache = {}
    
    # Initialize platform context manager
    app.state.platform_context = PlatformContextManager()
    
    logger.info("Enhanced Chatbot Service initialized successfully")
    yield
    
    # Cleanup
    await app.state.http_client.aclose()
    logger.info("Enhanced Chatbot Service shut down")

# Initialize FastAPI application
app = FastAPI(
    title="MantraPath Enhanced Chatbot Service",
    description="Voice-enabled, multi-language chatbot with platform awareness",
    version="3.0.0",
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

class VoiceChatRequest(BaseModel):
    """Voice chat request with auto language detection"""
    session_id: Optional[str] = Field(None, description="Chat session ID")
    preferred_language: Optional[str] = Field("auto", description="Preferred response language")
    include_platform_context: bool = Field(True, description="Include mood, journal, community context")
    voice_response: bool = Field(True, description="Generate voice response")

class TextChatRequest(BaseModel):
    """Text chat request with language support"""
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Chat session ID")
    language: Optional[str] = Field("auto", description="Message language")
    preferred_response_language: Optional[str] = Field(None, description="Preferred response language")
    include_platform_context: bool = Field(True, description="Include platform context")
    voice_response: bool = Field(False, description="Generate voice response")

class EnhancedChatResponse(BaseModel):
    """Enhanced chat response with multi-language and platform awareness"""
    response_text: str
    session_id: str
    detected_language: str
    response_language: str
    sentiment: Dict[str, Any]
    cultural_context: Dict[str, Any]
    platform_insights: Dict[str, Any]
    intervention_type: str
    confidence_score: float
    follow_up_suggestions: List[str]
    crisis_detected: bool
    audio_url: Optional[str] = None
    conversation_memory: Dict[str, Any]

class LanguageDetectionResponse(BaseModel):
    """Language detection response"""
    detected_language: str
    confidence: float
    supported_languages: List[str]

# --- Platform Context Manager ---

class PlatformContextManager:
    """Manages platform-wide context for chatbot responses"""
    
    def __init__(self):
        self.context_cache = {}
        self.cache_ttl = timedelta(minutes=10)
    
    async def get_user_platform_context(self, user_id: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get comprehensive platform context for user"""
        cache_key = f"platform_context_{user_id}"
        
        # Check cache
        if cache_key in self.context_cache:
            cached_data, timestamp = self.context_cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                return cached_data
        
        context = {
            "user_id": user_id,
            "mood_data": await self._get_mood_context(user_id, http_client),
            "profile_data": await self._get_profile_context(user_id, http_client),
            "content_activity": await self._get_content_activity(user_id, http_client),
            "community_activity": await self._get_community_activity(user_id, http_client),
            "memory_insights": await self._get_memory_insights(user_id, http_client),
            "ai_insights": await self._get_ai_insights(user_id, http_client),
            "timestamp": datetime.now().isoformat()
        }
        
        # Cache the context
        self.context_cache[cache_key] = (context, datetime.now())
        return context
    
    async def _get_mood_context(self, user_id: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get mood service context"""
        try:
            response = await http_client.get(
                f"{SERVICE_URLS['mood_service']}/api/mood/current/{user_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "current_mood": data.get("mood"),
                    "mood_score": data.get("score"),
                    "recent_patterns": data.get("patterns", []),
                    "mood_trends": data.get("trends", {}),
                    "last_entry": data.get("last_entry")
                }
        except Exception as e:
            logger.warning(f"Failed to get mood context for user {user_id}: {e}")
        
        return {"available": False, "reason": "service_unavailable"}
    
    async def _get_profile_context(self, user_id: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get user profile context"""
        try:
            response = await http_client.get(
                f"{SERVICE_URLS['profile_service']}/api/profiles/{user_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "display_name": data.get("display_name"),
                    "language_preferences": data.get("language_preferences", {}),
                    "cultural_background": data.get("cultural_background", {}),
                    "communication_style": data.get("communication_style", {}),
                    "wellness_goals": data.get("wellness_goals", []),
                    "privacy_settings": data.get("privacy_settings", {})
                }
        except Exception as e:
            logger.warning(f"Failed to get profile context for user {user_id}: {e}")
        
        return {"available": False, "reason": "service_unavailable"}
    
    async def _get_content_activity(self, user_id: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get content service activity"""
        try:
            response = await http_client.get(
                f"{SERVICE_URLS['content_service']}/api/articles/user/{user_id}/recent",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "recent_articles": data.get("articles", [])[:5],
                    "reading_preferences": data.get("preferences", {}),
                    "engagement_metrics": data.get("engagement", {})
                }
        except Exception as e:
            logger.warning(f"Failed to get content activity for user {user_id}: {e}")
        
        return {"available": False, "reason": "service_unavailable"}
    
    async def _get_community_activity(self, user_id: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get community service activity"""
        try:
            response = await http_client.get(
                f"{SERVICE_URLS['community_service']}/api/users/{user_id}/activity",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "recent_posts": data.get("posts", [])[:3],
                    "challenges": data.get("challenges", []),
                    "community_engagement": data.get("engagement", {}),
                    "support_given": data.get("support_metrics", {})
                }
        except Exception as e:
            logger.warning(f"Failed to get community activity for user {user_id}: {e}")
        
        return {"available": False, "reason": "service_unavailable"}
    
    async def _get_memory_insights(self, user_id: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get memory service insights"""
        try:
            response = await http_client.get(
                f"{SERVICE_URLS['memory_service']}/api/memories/{user_id}/insights",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "memory_patterns": data.get("patterns", []),
                    "behavioral_insights": data.get("insights", []),
                    "conversation_context": data.get("conversation_context", {}),
                    "learning_preferences": data.get("learning_preferences", {})
                }
        except Exception as e:
            logger.warning(f"Failed to get memory insights for user {user_id}: {e}")
        
        return {"available": False, "reason": "service_unavailable"}
    
    async def _get_ai_insights(self, user_id: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
        """Get AI context store insights"""
        try:
            response = await http_client.get(
                f"{SERVICE_URLS['ai_context_store']}/api/context/{user_id}",
                timeout=5.0
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "ai_insights": data.get("insights", []),
                    "predictive_context": data.get("predictive_context", {}),
                    "behavioral_patterns": data.get("patterns", []),
                    "risk_factors": data.get("risk_assessment", {})
                }
        except Exception as e:
            logger.warning(f"Failed to get AI insights for user {user_id}: {e}")
        
        return {"available": False, "reason": "service_unavailable"}

# --- Language Processing Functions ---

async def detect_language(text: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Detect language of input text"""
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['translation_service']}/api/detect",
            json={"text": text},
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
    
    return {"language": "en", "confidence": 0.5}

async def translate_text(text: str, target_language: str, source_language: str = "auto", http_client: httpx.AsyncClient = None) -> str:
    """Translate text to target language"""
    if source_language == target_language:
        return text
    
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['translation_service']}/api/translate",
            json={
                "text": text,
                "target_language": target_language,
                "source_language": source_language
            },
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("translated_text", text)
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
    
    return text

async def analyze_sentiment_and_culture(text: str, language: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """Analyze sentiment and cultural context"""
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['ai_event_processor']}/api/analyze/sentiment",
            json={
                "text": text,
                "language": language,
                "include_cultural_context": True
            },
            timeout=10.0
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.warning(f"Sentiment analysis failed: {e}")
    
    return {
        "sentiment": {"compound": 0.0, "positive": 0.33, "neutral": 0.34, "negative": 0.33},
        "cultural_context": {"region": "neutral", "cultural_markers": []},
        "emotional_indicators": []
    }

async def generate_voice_response(text: str, language: str, http_client: httpx.AsyncClient) -> Optional[str]:
    """Generate voice audio for response"""
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['voice_service']}/api/v1/voice/tts",
            json={
                "text": text,
                "language": language,
                "voice": "default",
                "model_preference": "high_quality"
            },
            timeout=15.0
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("audio_url")
    except Exception as e:
        logger.warning(f"Voice generation failed: {e}")
    
    return None

# --- Main Chat Endpoints ---

@app.get("/health")
async def health_check():
    """Enhanced health check"""
    return {
        "status": "healthy",
        "service": "enhanced_chatbot_service",
        "version": "3.0.0",
        "features": [
            "voice_integration",
            "multi_language_support", 
            "platform_awareness",
            "cultural_intelligence",
            "conversation_memory"
        ]
    }

@app.post("/api/chat/voice", response_model=EnhancedChatResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    request_data: str = Form(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Voice chat endpoint with speech-to-text and text-to-speech"""
    try:
        user_id = current_user["user_id"]
        request = VoiceChatRequest.parse_raw(request_data)
        
        # Process voice input
        audio_data = await audio.read()
        
        # Speech to text
        stt_response = await app.state.http_client.post(
            f"{SERVICE_URLS['voice_service']}/api/v1/voice/stt",
            files={"audio": audio_data},
            data={"language": "auto"},
            timeout=20.0
        )
        
        if stt_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Speech recognition failed")
        
        stt_data = stt_response.json()
        user_message = stt_data.get("text", "")
        detected_language = stt_data.get("language", "en")
        
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="No speech detected")
        
        # Process as text chat
        text_request = TextChatRequest(
            message=user_message,
            session_id=request.session_id,
            language=detected_language,
            preferred_response_language=request.preferred_language if request.preferred_language != "auto" else detected_language,
            include_platform_context=request.include_platform_context,
            voice_response=request.voice_response
        )
        
        return await process_chat_request(text_request, user_id, db, background_tasks)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")

@app.post("/api/chat/text", response_model=EnhancedChatResponse)
async def text_chat(
    request: TextChatRequest,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Text chat endpoint with language support"""
    try:
        user_id = current_user["user_id"]
        return await process_chat_request(request, user_id, db, background_tasks)
        
    except Exception as e:
        logger.error(f"Text chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

async def process_chat_request(
    request: TextChatRequest, 
    user_id: str, 
    db: Session, 
    background_tasks: BackgroundTasks
) -> EnhancedChatResponse:
    """Process chat request with full platform integration"""
    
    # Detect language if auto
    if request.language == "auto":
        lang_detection = await detect_language(request.message, app.state.http_client)
        detected_language = lang_detection.get("language", "en")
    else:
        detected_language = request.language
    
    # Determine response language
    response_language = request.preferred_response_language or detected_language
    
    # Get platform context
    platform_context = {}
    if request.include_platform_context:
        platform_context = await app.state.platform_context.get_user_platform_context(
            user_id, app.state.http_client
        )
    
    # Analyze sentiment and cultural context
    sentiment_analysis = await analyze_sentiment_and_culture(
        request.message, detected_language, app.state.http_client
    )
    
    # Get or create session
    session_id = request.session_id
    if not session_id:
        # Create new session
        new_session = ChatSession(
            user_id=user_id,
            title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            session_type="enhanced_chat",
            is_active=True
        )
        db.add(new_session)
        db.commit()
        session_id = new_session.id
    
    # Get conversation history
    conversation_history = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    
    conversation_context = [
        {
            "sender": msg.sender,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat()
        }
        for msg in reversed(conversation_history)
    ]
    
    # Generate intelligent response using Action Orchestrator
    orchestrator_request = {
        "user_id": user_id,
        "session_id": session_id,
        "message": request.message,
        "detected_language": detected_language,
        "response_language": response_language,
        "sentiment_analysis": sentiment_analysis,
        "platform_context": platform_context,
        "conversation_history": conversation_context,
        "capabilities": ["voice", "translation", "cultural_adaptation", "crisis_detection"]
    }
    
    try:
        orchestrator_response = await app.state.http_client.post(
            f"{SERVICE_URLS['action_orchestrator']}/api/chat/process",
            json=orchestrator_request,
            timeout=30.0
        )
        
        if orchestrator_response.status_code == 200:
            response_data = orchestrator_response.json()
        else:
            # Fallback response
            response_data = await generate_fallback_response(
                request.message, detected_language, response_language, 
                platform_context, sentiment_analysis
            )
    except Exception as e:
        logger.warning(f"Action orchestrator failed: {e}")
        response_data = await generate_fallback_response(
            request.message, detected_language, response_language,
            platform_context, sentiment_analysis
        )
    
    # Translate response if needed
    response_text = response_data.get("response", "I understand. How can I help you today?")
    if detected_language != response_language:
        response_text = await translate_text(
            response_text, response_language, detected_language, app.state.http_client
        )
    
    # Generate voice response if requested
    audio_url = None
    if request.voice_response:
        audio_url = await generate_voice_response(
            response_text, response_language, app.state.http_client
        )
    
    # Save conversation
    user_message_record = ChatMessage(
        session_id=session_id,
        sender="user",
        content=request.message,
        message_type="text"
    )
    
    bot_message_record = ChatMessage(
        session_id=session_id,
        sender="assistant",
        content=response_text,
        message_type="enhanced_response"
    )
    
    db.add(user_message_record)
    db.add(bot_message_record)
    db.commit()
    
    # Update conversation memory
    conversation_memory = {
        "session_id": session_id,
        "total_messages": len(conversation_context) + 2,
        "detected_patterns": response_data.get("patterns", []),
        "key_topics": response_data.get("topics", []),
        "emotional_progression": response_data.get("emotional_progression", [])
    }
    
    return EnhancedChatResponse(
        response_text=response_text,
        session_id=session_id,
        detected_language=detected_language,
        response_language=response_language,
        sentiment=sentiment_analysis.get("sentiment", {}),
        cultural_context=sentiment_analysis.get("cultural_context", {}),
        platform_insights=platform_context,
        intervention_type=response_data.get("intervention_type", "conversational"),
        confidence_score=response_data.get("confidence_score", 0.8),
        follow_up_suggestions=response_data.get("follow_up_suggestions", []),
        crisis_detected=response_data.get("crisis_detected", False),
        audio_url=audio_url,
        conversation_memory=conversation_memory
    )

async def generate_fallback_response(
    message: str, 
    detected_language: str, 
    response_language: str,
    platform_context: Dict[str, Any],
    sentiment_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate fallback response when orchestrator is unavailable"""
    
    # Simple sentiment-based responses
    sentiment = sentiment_analysis.get("sentiment", {})
    compound_score = sentiment.get("compound", 0.0)
    
    if compound_score < -0.5:
        # Negative sentiment
        response = "I can sense you're going through a difficult time. I'm here to listen and support you."
        intervention_type = "emotional_support"
    elif compound_score > 0.5:
        # Positive sentiment
        response = "It's wonderful to hear such positivity from you! How can I help you continue this positive momentum?"
        intervention_type = "positive_reinforcement"
    else:
        # Neutral sentiment
        response = "I understand. Tell me more about what's on your mind so I can better support you."
        intervention_type = "exploratory"
    
    # Include platform insights if available
    mood_data = platform_context.get("mood_data", {})
    if mood_data.get("available", False):
        current_mood = mood_data.get("current_mood")
        if current_mood:
            response += f" I notice your recent mood has been {current_mood}."
    
    return {
        "response": response,
        "intervention_type": intervention_type,
        "confidence_score": 0.6,
        "follow_up_suggestions": [
            "Tell me more about your feelings",
            "Would you like some breathing exercises?",
            "How has your day been so far?"
        ],
        "crisis_detected": compound_score < -0.8,
        "patterns": [],
        "topics": ["emotional_support", "conversation"],
        "emotional_progression": [compound_score]
    }

@app.get("/api/chat/sessions")
async def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat sessions"""
    try:
        user_id = current_user["user_id"]
        
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.created_at.desc()).limit(20).all()
        
        return [
            {
                "id": session.id,
                "title": session.title,
                "session_type": session.session_type,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat(),
                "message_count": db.query(ChatMessage).filter(
                    ChatMessage.session_id == session.id
                ).count()
            }
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sessions")

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for session"""
    try:
        user_id = current_user["user_id"]
        
        # Verify session ownership
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return [
            {
                "id": msg.id,
                "sender": msg.sender,
                "content": msg.content,
                "message_type": msg.message_type,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch history")

@app.post("/api/language/detect", response_model=LanguageDetectionResponse)
async def detect_message_language(
    text: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Detect language of text input"""
    try:
        detection_result = await detect_language(text, app.state.http_client)
        
        return LanguageDetectionResponse(
            detected_language=detection_result.get("language", "en"),
            confidence=detection_result.get("confidence", 0.5),
            supported_languages=[
                "en", "hi", "es", "fr", "de", "it", "pt", "ru", "ja", 
                "zh", "ko", "ar", "bn", "ta", "te", "gu", "mr", "pa", "ur"
            ]
        )
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail="Language detection failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
