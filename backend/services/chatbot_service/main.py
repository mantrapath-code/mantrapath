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

# Service URLs configuration for translation integration via Models Service
SERVICE_URLS = {
    'models_service': os.getenv('MODELS_SERVICE_URL', 'http://models-service:8080'),
    'voice_service': os.getenv('VOICE_SERVICE_URL', 'http://voice-service:8011'),
}

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Add parent directories to path for shared imports
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import ChatSession, ChatMessage, Base
from shared.auth import get_current_user

# Import our intelligent engine components
from src.intelligent_engine import (
    MoodAwareResponder, 
    ServiceIntegrator, 
    ContextAnalyzer, 
    ResponseGenerator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown tasks
    """
    # Startup tasks
    logger.info("Starting MantraPath Intelligent Chatbot Service v2.0.0 with Translation Support")
    
    # Initialize HTTP client for service communication
    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    
    # Initialize intelligent engine components
    app.state.response_generator = ResponseGenerator()
    logger.info("Intelligent engine with translation support initialized successfully")
    
    # Startup health check
    engine_status = app.state.response_generator.get_engine_status()
    logger.info(f"Engine status: {engine_status}")
    
    yield
    
    # Shutdown tasks
    await app.state.http_client.aclose()
    logger.info("Shutting down MantraPath Intelligent Chatbot Service")

# Initialize FastAPI application with intelligent capabilities
app = FastAPI(
    title="MantraPath Intelligent Chatbot Service",
    description="AI-powered, mood-aware chatbot with comprehensive mental health support",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- Pydantic Models for API ---

class IntelligentChatRequest(BaseModel):
    """
    Request model for intelligent chat interactions with multi-language support
    
    Attributes:
        message (str): User's message text
        session_id (Optional[str]): Existing session ID or None for new session
        user_context_refresh (bool): Force refresh of user context from services
        language (Optional[str]): Input language (auto-detect if not provided)
        preferred_response_language (Optional[str]): Preferred response language
    """
    message: str = Field(..., description="User's message text", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="Existing chat session ID")
    user_context_refresh: bool = Field(False, description="Force refresh user context")
    language: Optional[str] = Field("auto", description="Input language or 'auto' for detection")
    preferred_response_language: Optional[str] = Field(None, description="Preferred response language")

class IntelligentChatResponse(BaseModel):
    """
    Response model for intelligent chat interactions with multi-language support
    
    Attributes:
        response (str): AI-generated response text
        session_id (str): Chat session identifier
        message_type (str): Type of response (text, breathing_exercise, crisis, etc.)
        tone (str): Response tone and style
        intervention_type (str): Type of intervention provided
        breathing_exercise (Optional[dict]): Breathing exercise data if applicable
        follow_up_suggestions (List[str]): Suggested follow-up actions
        crisis_detected (bool): Whether crisis situation was detected
        confidence_score (float): AI confidence in response appropriateness
        context_summary (dict): Summary of context used for response generation
        detected_language (str): Detected language of user input
        response_language (str): Language of the response
        translation_used (bool): Whether translation was used
    """
    response: str
    session_id: str
    message_type: str = "intelligent_text"
    tone: str
    intervention_type: str
    breathing_exercise: Optional[dict] = None
    follow_up_suggestions: List[str] = []
    crisis_detected: bool = False
    confidence_score: float
    context_summary: dict
    detected_language: str = "en"
    response_language: str = "en"
    translation_used: bool = False

class ChatAnalyticsResponse(BaseModel):
    """Response model for chat analytics"""
    total_messages: int
    session_count: int
    average_response_confidence: float
    crisis_interactions: int
    most_common_intervention: str
    user_engagement_score: float

class EngineStatusResponse(BaseModel):
    """Response model for engine status"""
    status: str
    version: str
    components: dict
    uptime_seconds: float
    total_responses_generated: int

# --- Helper Functions ---

async def get_conversation_history(
    session_id: str, 
    db: Session, 
    limit: int = 10
) -> List[dict]:
    """
    Retrieve conversation history for context
    
    Args:
        session_id (str): Chat session ID
        db (Session): Database session
        limit (int): Maximum number of messages to retrieve
        
    Returns:
        List[dict]: Conversation history
    """
    try:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat(),
                "message_type": msg.message_type
            }
            for msg in reversed(messages)  # Return in chronological order
        ]
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return []

# --- Translation Service Integration ---

async def detect_language(text: str, http_client: httpx.AsyncClient) -> Dict[str, Any]:
    """
    Detect language using models service with Phi-3
    
    Args:
        text (str): Text to analyze for language detection
        http_client: HTTP client for making requests
        
    Returns:
        Dict containing detected language and confidence
    """
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['models_service']}/api/v1/translation/detect-language",
            json={"text": text},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "language": data.get("language", "en"),
                "confidence": data.get("confidence", 0.0)
            }
        else:
            logger.warning(f"Language detection failed with status {response.status_code}")
            return {"language": "en", "confidence": 0.0}
            
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
        return {"language": "en", "confidence": 0.0}

async def translate_text(
    text: str,
    source_language: str,
    target_language: str,
    http_client: httpx.AsyncClient
) -> str:
    """
    Translate text using translation service
    
    Args:
        text: Text to translate
        source_language: Source language code
        target_language: Target language code
        http_client: HTTP client for making requests
        
    Returns:
        Translated text
    """
    try:
        response = await http_client.post(
            f"{SERVICE_URLS['models_service']}/api/v1/translation/translate",
            json={
                "text": text,
                "source_language": source_language,
                "target_language": target_language
            },
            timeout=15.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success", False):
                return data.get("translated_text", text)
            else:
                logger.warning(f"Translation failed: {data.get('error', 'Unknown error')}")
                return text
        else:
            logger.warning(f"Translation failed with status {response.status_code}")
            return text
            
    except Exception as e:
        logger.warning(f"Translation failed: {e}")
        return text

async def save_chat_interaction(
    session_id: str,
    user_message: str,
    ai_response: str,
    user_id: str,
    response_metadata: dict,
    db: Session
):
    """
    Save chat interaction to database for history and analytics
    
    Args:
        session_id (str): Chat session ID
        user_message (str): User's message
        ai_response (str): AI-generated response
        user_id (str): User identifier
        response_metadata (dict): Response generation metadata
        db (Session): Database session
    """
    try:
        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            sender="user",
            content=user_message,
            message_type="text",
            created_at=datetime.utcnow()
        )
        db.add(user_msg)
        
        # Save AI response
        ai_msg = ChatMessage(
            session_id=session_id,
            sender="ai",
            content=ai_response,
            message_type=response_metadata.get("intervention_type", "intelligent_text"),
            metadata=response_metadata,
            created_at=datetime.utcnow()
        )
        db.add(ai_msg)
        
        db.commit()
        logger.debug(f"Saved chat interaction for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error saving chat interaction: {str(e)}")
        db.rollback()

# --- API Endpoints ---

# Session Management Endpoints (Frontend Compatibility)
@app.post("/api/chatbot/chat/session", response_model=dict)
async def create_chatbot_session_frontend(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new chat session for frontend compatibility
    Frontend expects this endpoint for session creation
    
    Returns:
        dict: Session information with ID and metadata
    """
    return await create_chat_session(db, current_user)

@app.post("/chat/session", response_model=dict)
async def create_chat_session(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new chat session for persistent conversation tracking
    
    Returns:
        dict: Session information with ID and metadata
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Creating new chat session for user {user_id}")
        
        # Create new session
        new_session = ChatSession(
            user_id=user_id,
            title=f"Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            session_type="intelligent_support",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        logger.info(f"Created session {new_session.id} for user {user_id}")
        
        return {
            "id": new_session.id,
            "title": new_session.title,
            "session_type": new_session.session_type,
            "is_active": new_session.is_active,
            "created_at": new_session.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@app.get("/chat/sessions", response_model=List[dict])
async def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all chat sessions for the current user
    
    Returns:
        List[dict]: List of user's chat sessions
    """
    try:
        user_id = current_user["user_id"]
        
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.created_at.desc()).all()
        
        return [
            {
                "id": session.id,
                "title": session.title,
                "session_type": session.session_type,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat()
            }
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat sessions")

@app.get("/chat/history", response_model=List[dict])
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get chat history for a specific session
    
    Args:
        session_id: ID of the chat session
    
    Returns:
        List[dict]: List of messages in the session
    """
    try:
        user_id = current_user["user_id"]
        
        # Verify session belongs to user
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
        logger.error(f"Error fetching chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

@app.post("/chat/intelligent", response_model=IntelligentChatResponse)
async def intelligent_chat(
    request: IntelligentChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Main intelligent chat endpoint with full context awareness and multi-language support
    
    This endpoint provides sophisticated, mood-aware responses by integrating
    data from all MantraPath services and analyzing conversation context.
    
    Features:
    - Mood-aware response generation
    - Crisis detection and intervention
    - Personalized communication style
    - Therapeutic intervention suggestions
    - Context-aware follow-up recommendations
    - Multi-language support with auto-detection
    - Cultural adaptation
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing intelligent chat request for user {user_id}")
        
        # Language detection if auto mode
        detected_language = "en"
        if request.language == "auto":
            lang_detection = await detect_language(request.message, app.state.http_client)
            detected_language = lang_detection.get("language", "en")
            logger.info(f"Auto-detected language: {detected_language} (confidence: {lang_detection.get('confidence', 0.0)})")
        else:
            detected_language = request.language or "en"
        
        # Determine response language
        response_language = request.preferred_response_language or detected_language
        
        # Get or create chat session
        session_id = request.session_id
        if not session_id:
            # Create new session
            new_session = ChatSession(
                user_id=user_id,
                title=f"Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                session_type="intelligent_support",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(new_session)
            db.commit()
            session_id = str(new_session.id)
            logger.info(f"Created new chat session {session_id} for user {user_id}")
        
        # Get conversation history for context
        conversation_history = await get_conversation_history(session_id, db)
        
        # Translate user message to English for processing if needed
        processing_message = request.message
        if detected_language != "en":
            processing_message = await translate_text(
                request.message, 
                detected_language, 
                "en", 
                app.state.http_client
            )
            logger.info(f"Translated message for processing: {processing_message[:100]}...")
        
        # Generate intelligent response using our engine
        intelligent_response = await app.state.response_generator.generate_intelligent_response(
            user_id=user_id,
            user_message=processing_message,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        # Translate response to target language if needed
        final_response = intelligent_response.response_text
        translation_used = False
        if response_language != "en":
            # For complex responses, try translation with enhanced logic
            translated_response = await translate_text_enhanced(
                intelligent_response.response_text,
                "en",
                response_language,
                app.state.http_client
            )
            if translated_response != intelligent_response.response_text:
                final_response = translated_response
                translation_used = True
                logger.info(f"✅ Translated response to {response_language}")
            else:
                # If translation failed, try with simplified response
                simplified_response = await get_simplified_response(
                    response_language, 
                    intelligent_response.intervention_type,
                    app.state.http_client
                )
                if simplified_response:
                    final_response = simplified_response
                    translation_used = True
                    logger.info(f"✅ Used simplified response for {response_language}")
                else:
                    logger.warning(f"⚠️ Translation failed for {response_language}, using English")
        
        # Prepare response data
        response_data = IntelligentChatResponse(
            response=final_response,
            session_id=session_id,
            tone=intelligent_response.tone,
            intervention_type=intelligent_response.intervention_type,
            breathing_exercise=intelligent_response.breathing_exercise,
            follow_up_suggestions=intelligent_response.follow_up_suggestions or [],
            crisis_detected=intelligent_response.crisis_detected,
            confidence_score=intelligent_response.confidence_score,
            context_summary=intelligent_response.context_used or {},
            detected_language=detected_language,
            response_language=response_language,
            translation_used=translation_used
        )
        
        # Save interaction to database (async background task)
        background_tasks.add_task(
            save_chat_interaction,
            session_id=session_id,
            user_message=request.message,
            ai_response=final_response,
            user_id=user_id,
            response_metadata={
                **intelligent_response.generation_metadata,
                "detected_language": detected_language,
                "response_language": response_language,
                "translation_used": translation_used
            } if intelligent_response.generation_metadata else {
                "detected_language": detected_language,
                "response_language": response_language,
                "translation_used": translation_used
            },
            db=db
        )
        
        logger.info(
            f"Generated intelligent response for user {user_id} with confidence "
            f"{intelligent_response.confidence_score:.2f}, language: {detected_language}->{response_language}"
        )
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in intelligent chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while generating response. Please try again."
        )

# Frontend-compatible chatbot endpoints
@app.post("/api/chatbot/chat", response_model=IntelligentChatResponse)
async def chatbot_chat_frontend(
    request: IntelligentChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Frontend-compatible chatbot endpoint
    Routes to the intelligent chat functionality
    """
    return await intelligent_chat(request, background_tasks, db, current_user)

@app.post("/api/chatbot/enhanced/chat", response_model=IntelligentChatResponse)
async def chatbot_enhanced_chat_frontend(
    request: IntelligentChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Enhanced chatbot endpoint for frontend compatibility
    Routes to the intelligent chat functionality
    """
    return await intelligent_chat(request, background_tasks, db, current_user)

@app.get("/api/chatbot/chat/sessions", response_model=List[dict])
async def get_chatbot_sessions_frontend(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Frontend-compatible chat sessions endpoint
    Routes to the chat sessions functionality
    """
    return await get_chat_sessions(db, current_user)

@app.get("/api/chatbot/chat/history", response_model=List[dict])
async def get_chatbot_history_frontend(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Frontend-compatible chat history endpoint
    Routes to the chat history functionality
    """
    return await get_chat_history(session_id, db, current_user)

# Voice input endpoint for frontend
@app.post("/api/chatbot/voice")
async def chatbot_voice_input(
    audio_file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Voice input endpoint that processes audio and returns chat response
    
    This endpoint:
    1. Receives audio file from frontend
    2. Converts speech to text using voice service
    3. Detects language automatically
    4. Generates intelligent response
    5. Optionally converts response back to speech
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing voice input for user {user_id}")
        
        # Read audio file
        audio_content = await audio_file.read()
        logger.info(f"Received audio file: {len(audio_content)} bytes, type: {audio_file.content_type}")
        
        # Send audio to voice service for speech-to-text
        try:
            files = {
                'audio_file': (audio_file.filename, audio_content, audio_file.content_type)
            }
            
            response = await app.state.http_client.post(
                f"{SERVICE_URLS['voice_service']}/api/v1/voice/stt",
                files=files,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Voice service STT failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=500, detail="Speech recognition failed")
                
            stt_result = response.json()
            transcript = stt_result.get('transcript', '')
            detected_language = stt_result.get('language', 'en')
            confidence = stt_result.get('confidence', 0.0)
            
            logger.info(f"STT Result: '{transcript}' (lang: {detected_language}, confidence: {confidence})")
            
            if not transcript.strip():
                raise HTTPException(status_code=400, detail="No speech detected in audio")
                
        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            raise HTTPException(status_code=500, detail="Failed to process voice input")
        
        # Create chat request from voice input
        chat_request = IntelligentChatRequest(
            message=transcript,
            session_id=session_id,
            language=detected_language,
            preferred_response_language=detected_language,  # Respond in same language
            user_context_refresh=True  # Always refresh context for voice
        )
        
        # Process through intelligent chat
        chat_response = await intelligent_chat(chat_request, background_tasks, db, current_user)
        
        # Add voice-specific metadata
        voice_response: Dict[str, Any] = {
            **chat_response.model_dump(),
            "voice_input": {
                "transcript": transcript,
                "detected_language": detected_language,
                "confidence": confidence,
                "audio_duration_ms": stt_result.get('duration_ms', 0)
            }
        }
        
        logger.info(f"Completed voice chat for user {user_id}")
        return voice_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing voice input. Please try again."
        )

@app.get("/chat/sessions/{user_id}")
async def get_user_chat_sessions(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get chat sessions for a specific user
    
    Returns list of chat sessions with basic metadata for session management.
    """
    try:
        # Verify user can access these sessions
        if current_user["user_id"] != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        sessions = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .limit(50)
            .all()
        )
        
        return [
            {
                "id": str(session.id),
                "title": session.title,
                "session_type": session.session_type,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat(),
                "message_count": db.query(ChatMessage)
                    .filter(ChatMessage.session_id == str(session.id))
                    .count()
            }
            for session in sessions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving chat sessions")

@app.get("/chat/analytics/{user_id}", response_model=ChatAnalyticsResponse)
async def get_chat_analytics(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get chat interaction analytics and insights for a user
    
    Provides comprehensive analytics about chat interactions, response effectiveness,
    and engagement patterns for continuous improvement.
    """
    try:
        # Verify user can access these analytics
        if current_user["user_id"] != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get analytics from response generator
        analytics = await app.state.response_generator.get_response_analytics(user_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=404, detail="No analytics data found")
        
        return ChatAnalyticsResponse(
            total_messages=analytics["total_responses"],
            session_count=analytics.get("session_count", 0),
            average_response_confidence=analytics["average_confidence"],
            crisis_interactions=analytics["crisis_responses"],
            most_common_intervention=analytics["most_common_intervention"],
            user_engagement_score=min(1.0, analytics["average_confidence"] * 1.2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chat analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving analytics")

@app.get("/chat/engine/status", response_model=EngineStatusResponse)
async def get_engine_status(current_user: dict = Depends(get_current_user)):
    """
    Get intelligent engine status and health information
    
    Provides comprehensive status information about all intelligent engine
    components for monitoring and debugging purposes.
    """
    try:
        status_data = app.state.response_generator.get_engine_status()
        
        return EngineStatusResponse(
            status="active",
            version="2.0.0",
            components=status_data,
            uptime_seconds=0.0,  # Will be implemented with proper startup tracking
            total_responses_generated=status_data.get("total_responses_tracked", 0)
        )
        
    except Exception as e:
        logger.error(f"Error retrieving engine status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving engine status")

@app.post("/chat/context/refresh/{user_id}")
async def refresh_user_context(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Force refresh of user context from all MantraPath services
    
    Useful when user data has been updated in other services and chatbot
    context needs to be refreshed for accurate responses.
    """
    try:
        # Verify user can refresh this context
        if current_user["user_id"] != user_id and not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Refresh context through service integrator
        await app.state.response_generator.service_integrator.refresh_user_context(user_id)
        
        return {
            "message": f"User context refreshed successfully for user {user_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing user context: {str(e)}")
        raise HTTPException(status_code=500, detail="Error refreshing context")

# --- Health Check and Utility Endpoints ---

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        
        # Test intelligent engine
        engine_status = app.state.response_generator.get_engine_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "intelligent_engine": "active",
            "components": engine_status
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "MantraPath Intelligent Chatbot Service",
        "version": "2.0.0",
        "description": "AI-powered, mood-aware chatbot with comprehensive mental health support",
        "features": [
            "Mood-aware response generation",
            "Multi-service data integration", 
            "Crisis detection and intervention",
            "Personalized communication styles",
            "Therapeutic intervention suggestions",
            "Conversation context analysis"
        ],
        "docs_url": "/docs",
        "health_check": "/health"
    }

# --- Error Handlers ---

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "An unexpected error occurred",
        "message": "Please try again later or contact support if the problem persists",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting MantraPath Intelligent Chatbot Service directly")
    uvicorn.run(
        "main_intelligent:app", 
        host="0.0.0.0", 
        port=8004, 
        reload=True,
        log_level="info"
    )
