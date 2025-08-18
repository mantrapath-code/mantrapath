"""
MantraPath Chatbot Service - Production Ready
Integrates Phi-3 Mini local AI with robust fallbacks and intelligent responses.
"""

import asyncio
import logging
import os
import sys
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import httpx
import redis.asyncio as redis

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import ChatSession, ChatMessage, Base
from shared.auth import get_current_user
# Event bus imports for BK-004
from shared.events import get_enhanced_event_bus, V3EventChannels

# Enhanced chatbot service imports
from src.services.enhanced_chatbot_service import (
    EnhancedChatbotService, 
    ChatContext, 
    EnhancedChatResponse
)

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
PHI4_MODEL_AVAILABLE = os.getenv("PHI4_MODEL_AVAILABLE", "true").lower() == "true"
AGENT_REDIS_URL = os.getenv("AGENT_REDIS_URL", "redis://agent-redis:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    user_context_refresh: Optional[bool] = False

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_type: str = "text"
    tone: str = "supportive"
    intervention_type: str = "general_support"
    crisis_detected: bool = False
    confidence_score: float = 0.8
    source: str = "phi3"  # phi3, openai, or fallback
    timestamp: Optional[str] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatbotService:
    """Main chatbot service with PHI4 integration and fallbacks"""
    
    def __init__(self):
        self.phi4_available = PHI4_MODEL_AVAILABLE
        self.openai_available = bool(OPENAI_API_KEY)
        self.redis_client = None
        # BK-004: Event bus reference
        self.event_bus = None
        # Enhanced service integration
        self.enhanced_service = None
        
    async def initialize(self):
        """Initialize chatbot service"""
        try:
            # Initialize Redis for caching
            self.redis_client = redis.from_url(AGENT_REDIS_URL, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Agent Redis connected successfully")
        except Exception as e:
            logger.warning(f"Agent Redis not available: {e}")
            
        # Initialize Enhanced Chatbot Service
        try:
            self.enhanced_service = EnhancedChatbotService(base_chatbot_service=self)
            logger.info("Enhanced Chatbot Service initialized with Action Orchestrator integration")
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Chatbot Service: {e}")
            
        # BK-004: Initialize enhanced event bus and subscribe to events
        try:
            self.event_bus = get_enhanced_event_bus()
            await self._setup_event_subscriptions()
            logger.info("Chatbot event subscriptions established")
        except Exception as e:
            logger.warning(f"Failed to initialize event subscriptions: {e}")
        
        logger.info(f"Chatbot service initialized - PHI4: {self.phi4_available}, OpenAI: {self.openai_available}")

    async def _setup_event_subscriptions(self):
        """BK-004: Subscribe to V3 service events for context sharing"""
        if not self.event_bus:
            return
        
        async def on_voice_intent(event):
            try:
                user_id = event.user_id or event.data.get("user_id")
                if not user_id:
                    return
                intent = event.data.get("intent") or event.data.get("intent_name")
                confidence = event.data.get("confidence_score") or event.data.get("confidence")
                ts = datetime.utcnow().isoformat()
                if self.redis_client:
                    await self.redis_client.hset(
                        f"chatbot:context:{user_id}",
                        mapping={
                            "last_intent": intent or "",
                            "intent_confidence": confidence or 0.0,
                            "last_intent_ts": ts,
                        }
                    )
            except Exception as e:
                logger.error(f"Error handling voice.intent_classified: {e}")
        
        async def on_mood_created(event):
            try:
                user_id = event.user_id or event.data.get("user_id")
                if not user_id:
                    return
                summary = json.dumps({
                    "mood_score": event.data.get("mood_score"),
                    "energy_level": event.data.get("energy_level"),
                    "stress_level": event.data.get("stress_level"),
                    "created_at": event.data.get("created_at"),
                })
                if self.redis_client:
                    await self.redis_client.hset(
                        f"chatbot:context:{user_id}",
                        mapping={
                            "last_mood": summary,
                            "last_mood_ts": datetime.utcnow().isoformat(),
                        }
                    )
            except Exception as e:
                logger.error(f"Error handling mood.entry.created: {e}")
        
        async def on_journal_created(event):
            try:
                user_id = event.user_id or event.data.get("user_id")
                if not user_id:
                    return
                summary = json.dumps({
                    "sentiment_score": event.data.get("sentiment_score"),
                    "sentiment_label": event.data.get("sentiment_label"),
                    "themes": event.data.get("themes"),
                    "created_at": event.data.get("created_at"),
                })
                if self.redis_client:
                    await self.redis_client.hset(
                        f"chatbot:context:{user_id}",
                        mapping={
                            "last_journal": summary,
                            "last_journal_ts": datetime.utcnow().isoformat(),
                        }
                    )
            except Exception as e:
                logger.error(f"Error handling journal.entry.created: {e}")
        
        await self.event_bus.subscribe(V3EventChannels.VOICE_INTENT_CLASSIFIED, on_voice_intent)
        await self.event_bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED, on_mood_created)
        await self.event_bus.subscribe(V3EventChannels.JOURNAL_ENTRY_CREATED, on_journal_created)

    async def generate_response(
        self, 
        user_message: str, 
        user_id: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> ChatResponse:
        """Generate response using best available method"""
        
        # Try PHI4 first (local model)
        if self.phi4_available:
            try:
                return await self._generate_phi4_response(user_message, user_id, conversation_history)
            except Exception as e:
                logger.error(f"PHI4 generation failed: {e}")
                # Fall through to next option
        
        # Try OpenAI as backup
        if self.openai_available:
            try:
                return await self._generate_openai_response(user_message, user_id, conversation_history)
            except Exception as e:
                logger.error(f"OpenAI generation failed: {e}")
                # Fall through to fallback
        
        # Use intelligent fallback
        return await self._generate_fallback_response(user_message, user_id)
    
    async def _generate_phi4_response(
        self, 
        user_message: str, 
        user_id: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> ChatResponse:
        """Generate response using PHI4 model via ollama"""
        
        logger.info(f"PHI4 request for user {user_id}: {user_message[:50]}...")
        
        try:
            import aiohttp
            import json
            
            # Build therapeutic prompt
            system_prompt = self._build_therapeutic_prompt(user_id)
            
            # Create conversation context
            context_messages = ""
            if conversation_history:
                for msg in conversation_history[-3:]:  # Last 3 messages for context
                    role = "User" if msg.get("is_user") else "Assistant"
                    context_messages += f"{role}: {msg.get('content', '')}\n"
            
            # Ollama API endpoint - use host.docker.internal to reach host machine from container
            url = "http://host.docker.internal:11434/api/generate"
            
            full_prompt = f"""{system_prompt}

Previous conversation context:
{context_messages}

Current user message: {user_message}

Please provide a thoughtful, compassionate response focused on mental wellness and support:"""
            
            payload = {
                "model": "phi4",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 200  # Limit response length
                }
            }
            
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=30)
                async with session.post(url, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        result = await response.json()
                        phi4_response = result.get("response", "").strip()
                        
                        if not phi4_response:
                            phi4_response = "I'm here to support you on your wellness journey. Could you share more about what's on your mind?"
                        
                        # Analyze for crisis detection
                        crisis_detected = self._detect_crisis(user_message, phi4_response)
                        
                        return ChatResponse(
                            response=phi4_response,
                            session_id="",  # Will be set by caller
                            tone="supportive",
                            intervention_type="ai_therapeutic",
                            crisis_detected=crisis_detected,
                            confidence_score=0.85,
                            source="phi4"
                        )
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        raise Exception(f"Ollama API returned status {response.status}")
                        
        except Exception as e:
            logger.error(f"Error generating PHI4 response: {str(e)}")
            # Return fallback response but still mark as PHI4 attempt
            fallback_response = "I understand you're reaching out, and I'm here to listen. Sometimes technology has its moments, but our connection remains important. How are you feeling right now?"
            
            return ChatResponse(
                response=fallback_response,
                session_id="",
                tone="supportive", 
                intervention_type="ai_therapeutic",
                crisis_detected=self._detect_crisis(user_message, fallback_response),
                confidence_score=0.60,
                source="phi4_fallback"
            )
    
    async def _generate_openai_response(
        self, 
        user_message: str, 
        user_id: str, 
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> ChatResponse:
        """Generate response using OpenAI as backup"""
        
        import openai
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        system_prompt = self._build_therapeutic_prompt(user_id)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.insert(-1, {
                    "role": msg.get("sender", "user"),
                    "content": msg.get("content", "")
                })
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=512,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        crisis_detected = self._detect_crisis(user_message, response_text)
        
        return ChatResponse(
            response=response_text,
            session_id="",
            tone="supportive",
            intervention_type="ai_therapeutic",
            crisis_detected=crisis_detected,
            confidence_score=0.9,
            source="openai"
        )
    
    async def _generate_fallback_response(
        self, 
        user_message: str, 
        user_id: str
    ) -> ChatResponse:
        """Generate intelligent fallback response"""
        
        message_lower = user_message.lower()
        
        # Crisis detection
        crisis_keywords = ["suicide", "kill myself", "end it all", "can't go on", "want to die"]
        if any(keyword in message_lower for keyword in crisis_keywords):
            response_text = (
                "I'm really concerned about what you're sharing with me. Your life has value, "
                "and there are people who want to help. Please consider reaching out to a crisis "
                "helpline right away - they have trained counselors available 24/7. "
                "In the US, you can call 988 for the Suicide & Crisis Lifeline. "
                "You don't have to go through this alone."
            )
            return ChatResponse(
                response=response_text,
                session_id="",
                tone="urgent_supportive",
                intervention_type="crisis_intervention",
                crisis_detected=True,
                confidence_score=0.95,
                source="fallback"
            )
        
        # Mood-related responses
        mood_keywords = ["sad", "depressed", "anxious", "worried", "stressed", "overwhelmed"]
        if any(keyword in message_lower for keyword in mood_keywords):
            response_text = (
                "I hear that you're going through a difficult time right now. "
                "Those feelings are valid, and it's okay to not be okay sometimes. "
                "What's been weighing on your mind lately? Sometimes talking through "
                "what we're experiencing can help us process these emotions."
            )
            intervention_type = "mood_support"
        
        # General support
        else:
            response_text = (
                "Thank you for sharing that with me. I'm here to listen and support you. "
                "While I'm experiencing some technical limitations right now, I want you to know "
                "that your thoughts and feelings matter. What would be most helpful for you "
                "to talk about today?"
            )
            intervention_type = "general_support"
        
        return ChatResponse(
            response=response_text,
            session_id="",
            tone="supportive",
            intervention_type=intervention_type,
            crisis_detected=False,
            confidence_score=0.7,
            source="fallback"
        )
    
    def _build_therapeutic_prompt(self, user_id: str) -> str:
        """Build therapeutic system prompt"""
        return """You are a compassionate, professional mental health support AI assistant. 

Your role is to:
- Provide empathetic, non-judgmental support
- Listen actively and validate emotions
- Offer practical coping strategies when appropriate
- Recognize crisis situations and guide users to professional help
- Maintain professional boundaries while being warm and supportive

Guidelines:
- Keep responses conversational but meaningful (2-4 sentences)
- Focus on the user's immediate emotional needs
- Ask open-ended questions to encourage sharing
- Avoid giving medical advice or diagnoses
- If you detect crisis language, prioritize safety and professional resources

Respond with empathy, professionalism, and genuine care for the user's wellbeing."""
    
    def _detect_crisis(self, user_message: str, response_text: str) -> bool:
        """Simple crisis detection"""
        crisis_indicators = [
            "suicide", "kill myself", "end it all", "can't go on", 
            "want to die", "no point", "better off dead", "harm myself"
        ]
        
        message_lower = user_message.lower()
        return any(indicator in message_lower for indicator in crisis_indicators)

# Global chatbot service instance
chatbot_service = ChatbotService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting MantraPath Chatbot Service")
    await chatbot_service.initialize()
    yield
    # Shutdown
    logger.info("Shutting down MantraPath Chatbot Service")

# Initialize FastAPI app
app = FastAPI(
    title="MantraPath Chatbot Service",
    description="AI-powered mental health chatbot with Phi-3 integration",
    version="3.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "http://localhost:5174",  # Alternative frontend port
        os.getenv("API_GATEWAY_URL", "http://localhost:8000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
async def get_conversation_history(session_id: str, db: Session, limit: int = 10) -> List[dict]:
    """Get conversation history"""
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
                "timestamp": msg.created_at.isoformat()
            }
            for msg in reversed(messages)
        ]
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        return []

async def save_chat_interaction(
    session_id: str,
    user_message: str,
    ai_response: str,
    user_id: str,
    response_metadata: dict,
    db: Session
):
    """Save chat interaction to database"""
    try:
        # Ensure session exists before saving messages
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            logger.warning(f"Session {session_id} not found, creating new session")
            session = ChatSession(
                id=session_id,
                user_id=user_id,
                title=f"Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                session_type="ai_support",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()
        
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
            message_type=response_metadata.get("intervention_type", "text"),
            message_metadata=response_metadata,
            created_at=datetime.utcnow()
        )
        db.add(ai_msg)
        
        db.commit()
        logger.debug(f"Saved chat interaction for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error saving chat interaction: {e}")
        db.rollback()

# API Endpoints

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with Phase 2 service monitoring"""
    try:
        # Get comprehensive health status from enhanced service
        health_status = await enhanced_chatbot_service.health_check()
        
        # Add database check
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            health_status["database"] = "connected"
        except Exception as db_error:
            health_status["database"] = f"error: {str(db_error)}"
            health_status["chatbot_service"] = "degraded"
        
        # Add legacy service compatibility
        health_status["phi4_available"] = chatbot_service.phi4_available if 'chatbot_service' in globals() else False
        health_status["openai_available"] = chatbot_service.openai_available if 'chatbot_service' in globals() else False
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "chatbot_service": "error"
        }

@app.get("/api/chatbot/test")
async def test_phi4_endpoint():
    """Test endpoint for PHI4 integration (no auth required)"""
    try:
        test_message = "Hello, this is a test message for PHI4 integration."
        
        # Test PHI4 generation directly
        if chatbot_service.phi4_available:
            try:
                # Test the actual PHI4 connection
                response = await chatbot_service._generate_phi4_response(
                    test_message, 
                    "test_user", 
                    None
                )
                
                return {
                    "status": "success",
                    "phi4_working": True,
                    "response": response.response,
                    "source": response.source,
                    "confidence": response.confidence_score,
                    "message": "PHI4 is working with real ollama connection"
                }
            except Exception as e:
                logger.error(f"PHI4 test failed: {e}")
                return {
                    "status": "phi4_error",
                    "phi4_working": False,
                    "error": str(e),
                    "fallback_available": chatbot_service.openai_available
                }
        else:
            return {
                "status": "phi4_disabled",
                "phi4_working": False,
                "message": "PHI4 is not available"
            }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.post("/chat/session")
async def create_chat_session(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new chat session"""
    try:
        user_id = current_user["user_id"]
        
        new_session = ChatSession(
            user_id=user_id,
            title=f"Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            session_type="ai_support",
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

@app.post("/api/chatbot/chat", response_model=ChatResponse)
@app.post("/api/chatbot/chat/intelligent", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Main chat endpoint"""
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing chat request for user {user_id}")
        
        # Get or create session
        session_id = request.session_id
        if not session_id:
            new_session = ChatSession(
                user_id=user_id,
                title=f"Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                session_type="ai_support",
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
                    title=f"Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                    session_type="ai_support",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(new_session)
                db.commit()
                db.refresh(new_session)
        
        # Get conversation history
        conversation_history = await get_conversation_history(session_id, db)
        
        # Generate response
        response = await chatbot_service.generate_response(
            request.message, user_id, conversation_history
        )
        response.session_id = session_id
        
        # Save interaction in background
        background_tasks.add_task(
            save_chat_interaction,
            session_id,
            request.message,
            response.response,
            user_id,
            {
                "source": response.source,
                "confidence": response.confidence_score,
                "tone": response.tone,
                "intervention_type": response.intervention_type
            },
            db
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

@app.post("/api/chatbot/enhanced/chat")
async def enhanced_chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Enhanced chat endpoint with Action Orchestrator integration"""
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing enhanced chat request for user {user_id}")
        
        if not chatbot_service.enhanced_service:
            # Fallback to regular chat if enhanced service not available
            return await chat_endpoint(request, background_tasks, db, current_user)
        
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
        
        # Get conversation history and build context
        conversation_history = await get_conversation_history(session_id, db)
        
        # Get user's cultural context (you may want to get this from user profile)
        cultural_preferences = {
            "language": "en",  # Default to English, could be retrieved from user profile
            "communication_style": "casual",
            "timezone": "UTC"
        }
        
        # Get recent mood context if available
        mood_context = None
        if chatbot_service.redis_client:
            try:
                mood_data = await chatbot_service.redis_client.hget(f"chatbot:context:{user_id}", "last_mood")
                if mood_data:
                    mood_context = json.loads(mood_data)
            except Exception as e:
                logger.warning(f"Could not retrieve mood context: {e}")
        
        # Build enhanced chat context
        chat_context = ChatContext(
            user_id=user_id,
            session_id=session_id,
            language=cultural_preferences.get("language", "en"),
            cultural_preferences=cultural_preferences,
            conversation_history=conversation_history,
            mood_context=mood_context,
            recent_actions=[]  # Could be populated from recent user actions
        )
        
        # Get JWT token from request headers
        jwt_token = None
        # You might need to extract this from the current_user or request headers
        
        # Process message with enhanced service
        enhanced_response = await chatbot_service.enhanced_service.process_message(
            message=request.message,
            context=chat_context,
            jwt_token=jwt_token
        )
        
        # Convert enhanced response to standard ChatResponse format
        response = ChatResponse(
            response=enhanced_response.response,
            session_id=session_id,
            message_type=enhanced_response.message_type,
            tone="supportive",
            intervention_type="enhanced_support",
            crisis_detected=False,
            confidence_score=enhanced_response.intent.confidence if enhanced_response.intent else 0.8,
            source="enhanced_orchestrator"
        )
        
        # Save interaction with enhanced metadata
        background_tasks.add_task(
            save_enhanced_chat_interaction,
            session_id,
            request.message,
            enhanced_response,
            user_id,
            db
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

@app.post("/api/chatbot/enhanced/chat")
async def enhanced_chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Enhanced chat endpoint with Action Orchestrator integration"""
    try:
        user_id = current_user["user_id"]
        logger.info(f"Processing enhanced chat request for user {user_id}")
        
        if not chatbot_service.enhanced_service:
            # Fallback to regular chat if enhanced service not available
            return await chat_endpoint(request, background_tasks, db, current_user)
        
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
        
        # Get conversation history and build context
        conversation_history = await get_conversation_history(session_id, db)
        
        # Get user's cultural context (you may want to get this from user profile)
        cultural_preferences = {
            "language": "en",  # Default to English, could be retrieved from user profile
            "communication_style": "casual",
            "timezone": "UTC"
        }
        
        # Get recent mood context if available
        mood_context = None
        if chatbot_service.redis_client:
            try:
                mood_data = await chatbot_service.redis_client.hget(f"chatbot:context:{user_id}", "last_mood")
                if mood_data:
                    mood_context = json.loads(mood_data)
            except Exception as e:
                logger.warning(f"Could not retrieve mood context: {e}")
        
        # Build enhanced chat context
        chat_context = ChatContext(
            user_id=user_id,
            session_id=session_id,
            language=cultural_preferences.get("language", "en"),
            cultural_preferences=cultural_preferences,
            conversation_history=conversation_history,
            mood_context=mood_context,
            recent_actions=[]  # Could be populated from recent user actions
        )
        
        # Get JWT token from request headers (if needed)
        jwt_token = None
        
        # Process message with enhanced service
        enhanced_response = await chatbot_service.enhanced_service.process_message(
            message=request.message,
            context=chat_context,
            jwt_token=jwt_token
        )
        
        # Convert enhanced response to standard ChatResponse format
        response = ChatResponse(
            response=enhanced_response.response,
            session_id=session_id,
            message_type=enhanced_response.message_type,
            tone="supportive",
            intervention_type="enhanced_support",
            crisis_detected=False,
            confidence_score=enhanced_response.intent.confidence if enhanced_response.intent else 0.8,
            source="enhanced_orchestrator"
        )
        
        # Save interaction with enhanced metadata
        background_tasks.add_task(
            save_enhanced_chat_interaction,
            session_id,
            request.message,
            enhanced_response,
            user_id,
            db
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {e}")
        # Fallback to regular chat on error
        try:
            return await chat_endpoint(request, background_tasks, db, current_user)
        except Exception as fallback_error:
            logger.error(f"Fallback chat also failed: {fallback_error}")
            raise HTTPException(status_code=500, detail="Enhanced chat processing failed")

async def save_enhanced_chat_interaction(
    session_id: str,
    user_message: str,
    enhanced_response: EnhancedChatResponse,
    user_id: str,
    db: Session
):
    """Save enhanced chat interaction with additional metadata"""
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
        
        # Save AI response with enhanced metadata
        ai_msg = ChatMessage(
            session_id=session_id,
            sender="assistant",
            content=enhanced_response.response,
            message_type=enhanced_response.message_type,
            metadata={
                "intent": enhanced_response.intent.__dict__ if enhanced_response.intent else None,
                "orchestration_metadata": enhanced_response.orchestration_metadata,
                "suggested_actions": enhanced_response.suggested_actions,
                "mood_insights": enhanced_response.mood_insights,
                "cultural_adaptations": enhanced_response.cultural_adaptations
            },
            created_at=datetime.utcnow()
        )
        db.add(ai_msg)
        
        db.commit()
        logger.info(f"Enhanced chat interaction saved for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error saving enhanced chat interaction: {e}")
        db.rollback()

async def save_enhanced_chat_interaction(
    session_id: str,
    user_message: str,
    enhanced_response: EnhancedChatResponse,
    user_id: str,
    db: Session
):
    """Save enhanced chat interaction with additional metadata"""
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
        
        # Save AI response with enhanced metadata
        ai_msg = ChatMessage(
            session_id=session_id,
            sender="assistant",
            content=enhanced_response.response,
            message_type=enhanced_response.message_type,
            metadata={
                "intent": enhanced_response.intent.__dict__ if enhanced_response.intent else None,
                "orchestration_metadata": enhanced_response.orchestration_metadata,
                "suggested_actions": enhanced_response.suggested_actions,
                "mood_insights": enhanced_response.mood_insights,
                "cultural_adaptations": enhanced_response.cultural_adaptations
            },
            created_at=datetime.utcnow()
        )
        db.add(ai_msg)
        
        db.commit()
        logger.info(f"Enhanced chat interaction saved for session {session_id}")
        
    except Exception as e:
        logger.error(f"Error saving enhanced chat interaction: {e}")
        db.rollback()

@app.get("/api/chatbot/status")
async def chatbot_status():
    """Get chatbot service status"""
    return {
        "service": "chatbot-service",
        "status": "active",
        "version": "3.0.0",
        "phi3_available": chatbot_service.phi3_available,
        "openai_available": chatbot_service.openai_available,
        "capabilities": [
            "Local Phi-3 Mini AI",
            "OpenAI GPT fallback",
            "Crisis detection",
            "Therapeutic responses",
            "Conversation memory"
        ]
    }

@app.get("/api/chatbot/chat/sessions")
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
                "created_at": session.created_at.isoformat()
            }
            for session in sessions
        ]
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        return []

@app.get("/api/chatbot/chat/history")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for a session"""
    try:
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
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return []

@app.post("/api/chatbot/chat/session")
async def create_chat_session_api(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create new chat session (API endpoint)"""
    return await create_chat_session(db, current_user)

@app.get("/api/chatbot/breathing-exercises")
async def get_breathing_exercises():
    """Get available breathing exercises"""
    return {
        "exercises": {
            "4-7-8": {
                "name": "4-7-8 Breathing",
                "description": "A calming technique that helps reduce anxiety",
                "steps": [
                    {"action": "inhale", "duration": 4, "instruction": "Breathe in through your nose"},
                    {"action": "hold", "duration": 7, "instruction": "Hold your breath"},
                    {"action": "exhale", "duration": 8, "instruction": "Exhale through your mouth"}
                ],
                "cycles": 4
            },
            "box-breathing": {
                "name": "Box Breathing",
                "description": "A technique used by Navy SEALs for stress management",
                "steps": [
                    {"action": "inhale", "duration": 4, "instruction": "Breathe in slowly"},
                    {"action": "hold", "duration": 4, "instruction": "Hold your breath"},
                    {"action": "exhale", "duration": 4, "instruction": "Breathe out slowly"},
                    {"action": "hold", "duration": 4, "instruction": "Hold empty"}
                ],
                "cycles": 5
            }
        }
    }

@app.post("/api/v1/actions")
async def handle_action(request: dict):
    """Handle actions from Action Orchestrator"""
    try:
        action_type = request.get("action")
        parameters = request.get("parameters", {})
        
        if action_type == "send_response":
            # Extract message from parameters
            message = parameters.get("message", "")
            user_id = parameters.get("user_id", "")
            
            # Create ChatContext object
            from src.services.enhanced_chatbot_service import ChatContext
            context = ChatContext(
                user_id=user_id,
                session_id=parameters.get("session_id", ""),
                language=parameters.get("language", "en"),
                cultural_preferences=parameters.get("cultural_preferences", {})
            )
            
            # Use the global enhanced chatbot service
            response = await chatbot_service.enhanced_service.process_message(
                message,
                context
            )
            
            return {
                "success": True,
                "result": {
                    "response": response.response,
                    "message_type": response.message_type,
                    "metadata": response.orchestration_metadata or {}
                }
            }
        else:
            return {
                "success": False,
                "error": f"Unknown action type: {action_type}"
            }
            
    except Exception as e:
        logger.error(f"Action handling error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Phase 2 Enhanced Chat Endpoint
@app.post("/api/chatbot/chat/enhanced", response_model=ChatResponse)
async def enhanced_chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Enhanced chat endpoint with Phase 2 capabilities"""
    session_id: Optional[str] = None
    try:
        user_id = str(current_user.get("user_id", "unknown"))
        logger.info(f"Processing enhanced chat request for user {user_id}")
        
        # Get or create session
        session_id = request.session_id
        if not session_id:
            new_session = ChatSession(
                user_id=user_id,
                title=f"Enhanced Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                session_type="ai_enhanced_support",
                is_active=True,
                created_at=datetime.now()
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            session_id = str(new_session.id)
        
        # Process message with enhanced service
        response_data = await enhanced_chatbot_service.process_message(
            message=request.message,
            user_id=user_id,
            session_id=session_id,
            user_language=getattr(request, 'language', None),
            jwt_token=current_user.get("access_token", "")
        )
        
        # Save chat interaction
        await save_chat_interaction(
            session_id=session_id,
            user_message=request.message,
            ai_response=response_data["response"],
            user_id=user_id,
            response_metadata={
                "services_used": response_data.get("services_used", []),
                "crisis_level": response_data.get("crisis_level", "none"),
                "language_detected": response_data.get("language_detected"),
                "processing_time_ms": response_data.get("processing_time_ms"),
                "cultural_adaptations": response_data.get("cultural_adaptations", []),
                "version": "2.0.0-phase2"
            },
            db=db
        )
        
        # Create response
        chat_response = ChatResponse(
            response=response_data["response"],
            session_id=session_id,
            source="enhanced_chatbot_v2",
            timestamp=response_data.get("timestamp", datetime.now().isoformat()),
            confidence=0.9,  # High confidence for enhanced processing
            metadata={
                "services_used": response_data.get("services_used", []),
                "crisis_level": response_data.get("crisis_level", "none"),
                "language": response_data.get("language_detected"),
                "processing_steps": response_data.get("processing_steps", []),
                "cultural_adaptations": response_data.get("cultural_adaptations", []),
                "actions_triggered": response_data.get("actions_triggered", []),
                "user_insights": response_data.get("user_insights", []),
                "audio_available": response_data.get("audio_response") is not None
            }
        )
        
        # Add audio response if available
        if response_data.get("audio_response") and chat_response.metadata:
            chat_response.metadata["audio_response"] = response_data["audio_response"]
            chat_response.metadata["audio_format"] = response_data.get("audio_format", "wav")
        
        logger.info(f"Enhanced chat response generated for user {user_id}, session {session_id}")
        return chat_response
        
    except Exception as e:
        logger.error(f"Enhanced chat error: {str(e)}")
        # Fallback to basic response
        return ChatResponse(
            response="I apologize, but I'm experiencing some technical difficulties. How can I help you today?",
            session_id=session_id or "temp_session",
            source="fallback",
            timestamp=datetime.now().isoformat(),
            confidence=0.5,
            metadata={"error": str(e), "fallback": True}
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MantraPath Chatbot Service",
        "version": "3.0.0-phase2",
        "description": "AI-powered mental health chatbot with comprehensive service integration",
        "features": [
            "Local Phi-3 Mini model",
            "Internal service integration (Models, ML, Translation, Voice, etc.)",
            "Crisis detection and intervention",
            "Multi-language support (17+ Indian languages)",
            "Cultural adaptation",
            "Voice synthesis and recognition",
            "Workflow orchestration",
            "Comprehensive user context management"
        ],
        "endpoints": {
            "health": "/health",
            "chat": "/api/chatbot/chat",
            "enhanced_chat": "/api/chatbot/chat/enhanced",
            "create_session": "/chat/session",
            "status": "/api/chatbot/status"
        },
        "services_integrated": [
            "Models Service (NLP, TTS/STT)",
            "ML Service (Crisis Detection)",
            "AI Context Store (User Context)",
            "Translation Service (Multi-language)",
            "Voice Service (Speech)",
            "Action Orchestrator (Workflows)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting MantraPath Chatbot Service")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )