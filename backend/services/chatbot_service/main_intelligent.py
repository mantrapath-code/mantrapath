"""
MantraPath Intelligent Chatbot Service

This is the main FastAPI application for the intelligent, mood-aware chatbot service.
It replaces mock responses with real intelligence that integrates with all MantraPath
services to provide contextually appropriate, personalized support.

Key Features:
    - Mood-aware response generation
    - Multi-service data integration
    - Context-aware conversation analysis
    - Crisis detection and intervention
    - Adaptive learning and personalization
    - Comprehensive response tracking

Author: MantraPath Development Team
Version: 2.0.0 (Intelligent Engine)
"""

import asyncio
import logging
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
from intelligent_engine import (
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
    logger.info("Starting MantraPath Intelligent Chatbot Service v2.0.0")
    
    # Initialize intelligent engine components
    app.state.response_generator = ResponseGenerator()
    logger.info("Intelligent engine initialized successfully")
    
    # Startup health check
    engine_status = app.state.response_generator.get_engine_status()
    logger.info(f"Engine status: {engine_status}")
    
    yield
    
    # Shutdown tasks
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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# --- Pydantic Models for API ---

class IntelligentChatRequest(BaseModel):
    """
    Request model for intelligent chat interactions
    
    Attributes:
        message (str): User's message text
        session_id (Optional[str]): Existing session ID or None for new session
        user_context_refresh (bool): Force refresh of user context from services
    """
    message: str = Field(..., description="User's message text", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="Existing chat session ID")
    user_context_refresh: bool = Field(False, description="Force refresh user context")

class IntelligentChatResponse(BaseModel):
    """
    Response model for intelligent chat interactions
    
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
    Main intelligent chat endpoint with full context awareness
    
    This endpoint provides sophisticated, mood-aware responses by integrating
    data from all MantraPath services and analyzing conversation context.
    
    Features:
    - Mood-aware response generation
    - Crisis detection and intervention
    - Personalized communication style
    - Therapeutic intervention suggestions
    - Context-aware follow-up recommendations
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing intelligent chat request for user {user_id}")
        
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
        
        # Generate intelligent response using our engine
        intelligent_response = await app.state.response_generator.generate_intelligent_response(
            user_id=user_id,
            user_message=request.message,
            session_id=session_id,
            conversation_history=conversation_history
        )
        
        # Prepare response data
        response_data = IntelligentChatResponse(
            response=intelligent_response.response_text,
            session_id=session_id,
            tone=intelligent_response.tone,
            intervention_type=intelligent_response.intervention_type,
            breathing_exercise=intelligent_response.breathing_exercise,
            follow_up_suggestions=intelligent_response.follow_up_suggestions or [],
            crisis_detected=intelligent_response.crisis_detected,
            confidence_score=intelligent_response.confidence_score,
            context_summary=intelligent_response.context_used or {}
        )
        
        # Save interaction to database (async background task)
        background_tasks.add_task(
            save_chat_interaction,
            session_id=session_id,
            user_message=request.message,
            ai_response=intelligent_response.response_text,
            user_id=user_id,
            response_metadata=intelligent_response.generation_metadata or {},
            db=db
        )
        
        logger.info(
            f"Generated intelligent response for user {user_id} with confidence "
            f"{intelligent_response.confidence_score:.2f}"
        )
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error in intelligent chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while generating response. Please try again."
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
