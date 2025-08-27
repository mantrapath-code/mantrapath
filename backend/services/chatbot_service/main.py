"""
MantraPath Chatbot Service - Cleaned and Consolidated
Single source of truth for chatbot endpoints with proper Phase 2 integration
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import httpx
import redis.asyncio as redis

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine, SessionLocal
from shared.models import ChatSession, ChatMessage, Base
from shared.auth import get_current_user
from shared.events import get_enhanced_event_bus, V3EventChannels

# Phase 2 Enhanced Service
from src.enhanced_chatbot_service_v2 import enhanced_chatbot_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Configuration
AGENT_REDIS_URL = os.getenv("AGENT_REDIS_URL", "redis://agent-redis:6379")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    user_context_refresh: Optional[bool] = False
    language: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_type: str = "text"
    tone: str = "supportive"
    intervention_type: str = "general_support"
    crisis_detected: bool = False
    confidence_score: float = 0.8
    source: str = "enhanced_v2"
    timestamp: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    audio_response: Optional[str] = None
    cultural_adaptations: Optional[List[Dict[str, Any]]] = None
    actions_triggered: Optional[List[Dict[str, Any]]] = None

class ChatbotServiceManager:
    """Simplified chatbot service manager"""
    
    def __init__(self):
        self.redis_client = None
        self.event_bus = None
        
    async def initialize(self):
        """Initialize chatbot service"""
        try:
            # Initialize Redis for caching
            self.redis_client = redis.from_url(AGENT_REDIS_URL, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Agent Redis connected successfully")
        except Exception as e:
            logger.warning(f"Agent Redis not available: {e}")
            
        # Initialize Event Bus for BK-004
        try:
            self.event_bus = await get_enhanced_event_bus()
            logger.info("Enhanced Event Bus connected")
        except Exception as e:
            logger.warning(f"Event Bus not available: {e}")
            
        logger.info("Chatbot Service Manager initialized successfully")

# Global service manager
service_manager = ChatbotServiceManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    await service_manager.initialize()
    yield
    # Shutdown
    if service_manager.redis_client:
        await service_manager.redis_client.close()

# Create FastAPI app
app = FastAPI(
    title="MantraPath Chatbot Service",
    description="Enhanced AI Chatbot with Phase 2 Integration",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return await enhanced_chatbot_service.health_check()

# Main Chat Endpoint - Single source of truth
@app.post("/api/chatbot/chat/enhanced", response_model=ChatResponse)
@app.post("/api/chatbot/enhanced/chat", response_model=ChatResponse)  # Frontend compatibility
async def enhanced_chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    request_obj: Request,  # Add request object to extract headers
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Enhanced chat endpoint - Single consolidated endpoint for all chat interactions
    Uses Phase 2 enhanced service with all integrations
    """
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing enhanced chat request for user {user_id}")
        
        # Get or create session
        session_id = request.session_id
        if not session_id:
            new_session = ChatSession(
                user_id=user_id,
                title=f"Enhanced Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                session_type="enhanced_ai_support",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = str(new_session.id)
        else:
            # Ensure session exists
            existing_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not existing_session:
                new_session = ChatSession(
                    id=session_id,
                    user_id=user_id,
                    title=f"Enhanced Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                    session_type="enhanced_ai_support",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(new_session)
                db.commit()
                db.refresh(new_session)

        # Extract JWT token from request headers
        jwt_token = None
        auth_header = request_obj.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            jwt_token = auth_header.split(" ")[1]
        
        # Process message with Phase 2 enhanced service
        logger.info(f"🚀 CALLING enhanced_chatbot_service.process_message for user {user_id} with token: {jwt_token is not None}")
        enhanced_response_data = await enhanced_chatbot_service.process_message(
            message=request.message,
            user_id=user_id,
            session_id=session_id,
            user_language=request.language,
            jwt_token=jwt_token
        )
        
        logger.info(f"Enhanced service response: {enhanced_response_data.get('status', 'unknown')}")
        
        # Convert enhanced response to standard ChatResponse format
        response = ChatResponse(
            response=enhanced_response_data.get("response", "I'm here to help. How can I support you today?"),
            session_id=session_id,
            message_type="enhanced_chat",
            tone="supportive",
            intervention_type="enhanced_support",
            crisis_detected=enhanced_response_data.get("crisis_level", "none") != "none",
            confidence_score=0.9,
            source="enhanced_v2",
            timestamp=enhanced_response_data.get("timestamp"),
            metadata={
                "services_used": enhanced_response_data.get("services_used", []),
                "processing_time_ms": enhanced_response_data.get("processing_time_ms"),
                "processing_steps": enhanced_response_data.get("processing_steps", []),
                "language_detected": enhanced_response_data.get("language_detected"),
                "crisis_level": enhanced_response_data.get("crisis_level", "none")
            },
            audio_response=enhanced_response_data.get("audio_response"),
            cultural_adaptations=enhanced_response_data.get("cultural_adaptations", []),
            actions_triggered=enhanced_response_data.get("actions_triggered", [])
        )
        
        # Save interaction to database and publish events
        background_tasks.add_task(
            save_chat_interaction,
            session_id,
            request.message,
            enhanced_response_data,
            user_id
        )
        
        # Publish chat event for real-time updates
        background_tasks.add_task(
            publish_chat_event,
            user_id,
            session_id,
            request.message,
            response.response,
            enhanced_response_data
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {e}", exc_info=True)
        
        # Return fallback response
        fallback_response = ChatResponse(
            response=f"I apologize, but I'm experiencing some technical difficulties. Please try again in a moment.",
            session_id=session_id or "error-session",
            message_type="error_fallback",
            source="fallback",
            confidence_score=0.0,
            metadata={"error": str(e)}
        )
        
        return fallback_response

async def get_chat_history(session_id: str, limit: int = 10, db: Session = None) -> List[Dict[str, Any]]:
    """Get recent chat history for context"""
    try:
        if not db:
            return []
            
        messages = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.timestamp.desc())\
            .limit(limit)\
            .all()
        
        history = []
        for msg in reversed(messages):  # Reverse to get chronological order
            history.append({
                "role": "user" if msg.message_type == "user" else "assistant",
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                "metadata": msg.metadata or {}
            })
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return []

async def save_chat_interaction(
    session_id: str,
    user_message: str,
    enhanced_response_data: Dict[str, Any],
    user_id: str
):
    """Save chat interaction to database"""
    try:
        # Create new database session for background task
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Save user message
        user_chat_message = ChatMessage(
            session_id=session_id,
            sender="user",
            content=user_message,
            message_type="text",
            message_metadata={"language_detected": enhanced_response_data.get("language_detected")},
            created_at=datetime.utcnow()
        )
        db.add(user_chat_message)
        
        # Save bot response
        bot_chat_message = ChatMessage(
            session_id=session_id,
            sender="mitra",
            content=enhanced_response_data.get("response", ""),
            message_type="enhanced_chat",
            message_metadata={
                "services_used": enhanced_response_data.get("services_used", []),
                "processing_time_ms": enhanced_response_data.get("processing_time_ms"),
                "crisis_level": enhanced_response_data.get("crisis_level", "none"),
                "cultural_adaptations": enhanced_response_data.get("cultural_adaptations", []),
                "actions_triggered": enhanced_response_data.get("actions_triggered", [])
            },
            created_at=datetime.utcnow()
        )
        db.add(bot_chat_message)
        
        db.commit()
        logger.info(f"Successfully saved chat interaction for session {session_id}: user_message='{user_message[:50]}...', bot_response='{enhanced_response_data.get('response', '')[:50]}...'")
        
    except Exception as e:
        logger.error(f"Error saving chat interaction: {e}")
        logger.exception("Full error traceback:")
        if 'db' in locals():
            try:
                db.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
    finally:
        if 'db' in locals():
            try:
                db.close()
            except Exception as close_error:
                logger.error(f"Error closing db: {close_error}")

async def publish_chat_event(
    user_id: str,
    session_id: str,
    user_message: str,
    bot_response: str,
    enhanced_response_data: Dict[str, Any]
):
    """Publish chat events for real-time updates"""
    try:
        if service_manager.event_bus:
            # Publish user message event
            await service_manager.event_bus.publish(
                V3EventChannels.CHAT_MESSAGE,
                {
                    "event_type": "user_message",
                    "user_id": user_id,
                    "session_id": session_id,
                    "message": user_message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "language": enhanced_response_data.get("language_detected", "en")
                }
            )
            
            # Publish bot response event
            await service_manager.event_bus.publish(
                V3EventChannels.CHAT_RESPONSE,
                {
                    "event_type": "bot_response",
                    "user_id": user_id,
                    "session_id": session_id,
                    "response": bot_response,
                    "timestamp": datetime.utcnow().isoformat(),
                    "metadata": {
                        "services_used": enhanced_response_data.get("services_used", []),
                        "processing_time_ms": enhanced_response_data.get("processing_time_ms"),
                        "crisis_level": enhanced_response_data.get("crisis_level", "none"),
                        "language_detected": enhanced_response_data.get("language_detected", "en"),
                        "audio_response": enhanced_response_data.get("audio_response") is not None
                    }
                }
            )
            
            # Publish crisis event if detected
            if enhanced_response_data.get("crisis_level", "none") != "none":
                await service_manager.event_bus.publish(
                    V3EventChannels.CRISIS_ALERT,
                    {
                        "event_type": "crisis_detected",
                        "user_id": user_id,
                        "session_id": session_id,
                        "crisis_level": enhanced_response_data.get("crisis_level"),
                        "message": user_message,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )
            
            logger.info(f"Published chat events for session {session_id}")
    except Exception as e:
        logger.error(f"Error publishing chat events: {e}")

# Session Management Endpoints
@app.post("/api/chatbot/chat/session")
async def create_chat_session(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new chat session"""
    try:
        user_id = current_user["user_id"]
        
        new_session = ChatSession(
            user_id=user_id,
            title=f"Enhanced Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            session_type="enhanced_ai_support",
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return {
            "id": new_session.id,
            "title": new_session.title,
            "session_type": new_session.session_type,
            "is_active": new_session.is_active,
            "created_at": new_session.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@app.get("/api/chatbot/chat/sessions")
async def get_chat_sessions(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user's chat sessions"""
    try:
        user_id = current_user["user_id"]
        
        sessions = db.query(ChatSession)\
            .filter(ChatSession.user_id == user_id)\
            .order_by(ChatSession.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [
            {
                "id": str(session.id),
                "title": session.title,
                "session_type": session.session_type,
                "is_active": session.is_active,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            }
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat sessions")

@app.get("/api/chatbot/chat/history")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for a session"""
    try:
        user_id = current_user["user_id"]
        
        # Verify session belongs to user
        session = db.query(ChatSession)\
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)\
            .first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .limit(limit)\
            .all()
        
        return [
            {
                "id": str(message.id),
                "sender": message.sender,
                "message_type": message.message_type,
                "content": message.content,
                "timestamp": message.created_at.isoformat(),
                "metadata": message.message_metadata
            }
            for message in messages
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

# Status and Monitoring
@app.get("/api/chatbot/status")
async def chatbot_status():
    """Get chatbot service status"""
    return {
        "service": "chatbot",
        "version": "2.0.0-clean",
        "status": "healthy",
        "enhanced_service": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

# Test Endpoint
@app.get("/api/chatbot/test")
async def test_chatbot():
    """Test endpoint for service verification"""
    try:
        health_status = await enhanced_chatbot_service.health_check()
        return {
            "status": "success",
            "message": "Enhanced Chatbot Service V2 is operational",
            "health": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MantraPath Chatbot Service",
        "version": "2.0.0-clean",
        "description": "Enhanced AI Chatbot with Phase 2 Integration",
        "status": "operational",
        "endpoints": {
            "chat": "/api/chatbot/chat/enhanced",
            "health": "/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
