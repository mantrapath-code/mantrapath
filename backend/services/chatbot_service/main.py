"""
Chatbot Service - AI-powered wellness chatbot with crisis detection
"""

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any, Set
from datetime import datetime, timedelta
import uuid
from pydantic import BaseModel, UUID4
import json
import redis
import asyncio
import openai
import os
from textblob import TextBlob
import re

# Import shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from shared.database import get_db
from shared.auth import get_current_user, verify_token
from shared.models import ChatSession, ChatMessage, User

app = FastAPI(
    title="MantraPath Chatbot Service", 
    description="AI-powered wellness chatbot with crisis detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.add(websocket)
        self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.discard(websocket)
        self.user_connections.pop(user_id, None)
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)

manager = ConnectionManager()

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[UUID4] = None
    message_type: str = "text"

class ChatResponse(BaseModel):
    message: str
    session_id: UUID4
    message_type: str = "text"
    sentiment_score: Optional[float] = None
    crisis_detected: bool = False
    suggested_actions: Optional[List[str]] = None

class SessionResponse(BaseModel):
    id: UUID4
    title: str
    is_active: bool
    message_count: int
    created_at: datetime
    updated_at: datetime

class MessageResponse(BaseModel):
    id: UUID4
    content: str
    is_user_message: bool
    message_type: str
    sentiment_score: Optional[float] = None
    created_at: datetime

# Crisis detection patterns
CRISIS_PATTERNS = [
    r'\b(suicide|kill myself|end it all|want to die|hurt myself)\b',
    r'\b(can\'t take it|can\'t go on|no point|give up|hopeless)\b',
    r'\b(self harm|cut myself|overdose|jump off)\b',
    r'\b(better off dead|worthless|burden|hate myself)\b'
]

CRISIS_KEYWORDS = [
    'suicide', 'kill myself', 'end it all', 'want to die', 'hurt myself',
    'self harm', 'overdose', 'hopeless', 'worthless', 'burden'
]

def detect_crisis(text: str) -> Dict[str, Any]:
    """Detect crisis indicators in text"""
    text_lower = text.lower()
    
    # Check for crisis patterns
    crisis_indicators = []
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, text_lower):
            crisis_indicators.append(pattern)
    
    # Check for crisis keywords
    found_keywords = [keyword for keyword in CRISIS_KEYWORDS if keyword in text_lower]
    
    # Calculate crisis score (0-1)
    crisis_score = min(1.0, (len(crisis_indicators) * 0.3) + (len(found_keywords) * 0.2))
    
    return {
        "is_crisis": crisis_score > 0.5,
        "crisis_score": crisis_score,
        "indicators": crisis_indicators,
        "keywords": found_keywords
    }

def analyze_sentiment(text: str) -> float:
    """Analyze sentiment of text (-1 to 1)"""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0.0

def generate_crisis_response() -> Dict[str, Any]:
    """Generate crisis response with resources"""
    return {
        "message": """I'm really concerned about what you're going through right now. Your life has value and there are people who want to help you.

**Immediate Help:**
• **Crisis Text Line**: Text HOME to 741741
• **National Suicide Prevention Lifeline**: 988
• **Emergency Services**: 911

**You're not alone in this.** Would you like to try a grounding exercise together, or would you prefer to talk about what's making you feel this way?""",
        "message_type": "crisis_support",
        "suggested_actions": [
            "Call 988 (Suicide Prevention Lifeline)",
            "Text HOME to 741741 (Crisis Text Line)",
            "Try a 5-4-3-2-1 grounding exercise",
            "Reach out to a trusted friend or family member",
            "Contact emergency services if in immediate danger"
        ]
    }

async def generate_ai_response(user_message: str, context: List[Dict[str, str]] = None) -> str:
    """Generate AI response using OpenAI GPT"""
    if not OPENAI_API_KEY:
        return "I'm here to listen and support you. Can you tell me more about how you're feeling?"
    
    try:
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": """You are Mantra-Mitra, a compassionate AI wellness companion. You provide emotional support, mindfulness guidance, and mental health resources. 

Key principles:
- Be empathetic, warm, and non-judgmental
- Provide practical coping strategies
- Encourage professional help when appropriate
- Never provide medical advice or diagnose
- Focus on mindfulness, self-care, and emotional wellness
- Keep responses concise but meaningful
- Use gentle, encouraging language

If someone expresses crisis thoughts, immediately provide crisis resources and encourage them to seek professional help."""
            }
        ]
        
        # Add conversation context
        if context:
            for msg in context[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": "user" if msg["is_user"] else "assistant",
                    "content": msg["content"]
                })
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"AI response generation failed: {e}")
        return "I'm here to support you. Can you tell me more about what's on your mind?"

def get_breathing_exercise() -> Dict[str, Any]:
    """Get breathing exercise content"""
    return {
        "message": """Let's try a simple breathing exercise together. This can help calm your nervous system.

**4-7-8 Breathing:**
1. **Inhale** through your nose for 4 counts
2. **Hold** your breath for 7 counts  
3. **Exhale** through your mouth for 8 counts
4. Repeat 3-4 times

Find a comfortable position and we'll do this together. Ready? Let's start with a slow inhale... 1, 2, 3, 4...""",
        "message_type": "breathing_exercise",
        "suggested_actions": [
            "Continue breathing exercise",
            "Try box breathing (4-4-4-4)",
            "Practice progressive muscle relaxation",
            "Try a body scan meditation"
        ]
    }

def get_grounding_exercise() -> Dict[str, Any]:
    """Get 5-4-3-2-1 grounding exercise"""
    return {
        "message": """Let's try a grounding exercise to help you feel more present and calm.

**5-4-3-2-1 Grounding Technique:**
Look around you and name:
• **5 things you can SEE** (a lamp, your phone, a book...)
• **4 things you can TOUCH** (your chair, a soft fabric, the table...)
• **3 things you can HEAR** (traffic, music, your breathing...)
• **2 things you can SMELL** (coffee, fresh air, a candle...)
• **1 thing you can TASTE** (gum, your last drink, or just your mouth...)

Take your time with each sense. This helps bring your mind back to the present moment.""",
        "message_type": "grounding_exercise",
        "suggested_actions": [
            "Practice the 5-4-3-2-1 technique",
            "Try mindful breathing",
            "Do a body scan",
            "Practice loving-kindness meditation"
        ]
    }

# Chat endpoints
@app.post("/api/chatbot/chat", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send message to chatbot"""
    user_id = current_user["user_id"]
    
    # Get or create session
    if chat_request.session_id:
        session = db.query(ChatSession).filter(
            and_(
                ChatSession.id == chat_request.session_id,
                ChatSession.user_id == user_id
            )
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        # Create new session
        session = ChatSession(
            id=uuid.uuid4(),
            user_id=user_id,
            title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
            is_active=True,
            session_type="general"
        )
        db.add(session)
        db.flush()
    
    # Analyze user message
    sentiment_score = analyze_sentiment(chat_request.message)
    crisis_analysis = detect_crisis(chat_request.message)
    
    # Save user message
    user_message = ChatMessage(
        id=uuid.uuid4(),
        session_id=session.id,
        content=chat_request.message,
        is_user_message=True,
        message_type=chat_request.message_type,
        sentiment_score=sentiment_score,
        crisis_indicators=crisis_analysis if crisis_analysis["is_crisis"] else None
    )
    db.add(user_message)
    
    # Generate response
    if crisis_analysis["is_crisis"]:
        # Crisis detected - provide immediate support
        response_data = generate_crisis_response()
        session.session_type = "crisis"
    elif "breathing" in chat_request.message.lower() or "breathe" in chat_request.message.lower():
        # User requested breathing exercise
        response_data = get_breathing_exercise()
    elif "grounding" in chat_request.message.lower() or "anxious" in chat_request.message.lower():
        # User might benefit from grounding
        response_data = get_grounding_exercise()
    else:
        # Get conversation context
        recent_messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(desc(ChatMessage.created_at)).limit(10).all()
        
        context = [
            {
                "content": msg.content,
                "is_user": msg.is_user_message
            }
            for msg in reversed(recent_messages)
        ]
        
        # Generate AI response
        ai_response = await generate_ai_response(chat_request.message, context)
        response_data = {
            "message": ai_response,
            "message_type": "text"
        }
    
    # Save bot response
    bot_message = ChatMessage(
        id=uuid.uuid4(),
        session_id=session.id,
        content=response_data["message"],
        is_user_message=False,
        message_type=response_data.get("message_type", "text")
    )
    db.add(bot_message)
    
    # Update session
    session.message_count = session.message_count + 2  # User + bot message
    if sentiment_score:
        # Update average sentiment (simple average for now)
        if session.avg_sentiment:
            session.avg_sentiment = (session.avg_sentiment + sentiment_score) / 2
        else:
            session.avg_sentiment = sentiment_score
    
    db.commit()
    
    return ChatResponse(
        message=response_data["message"],
        session_id=session.id,
        message_type=response_data.get("message_type", "text"),
        sentiment_score=sentiment_score,
        crisis_detected=crisis_analysis["is_crisis"],
        suggested_actions=response_data.get("suggested_actions")
    )

@app.get("/api/chatbot/chat/sessions", response_model=List[SessionResponse])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user's chat sessions"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user["user_id"]
    ).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()
    
    return [
        SessionResponse(
            id=session.id,
            title=session.title or "Untitled Chat",
            is_active=session.is_active,
            message_count=session.message_count,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
        for session in sessions
    ]

@app.get("/api/chatbot/chat/history")
async def get_chat_history(
    session_id: UUID4,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get chat history for a session"""
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        and_(
            ChatSession.id == session_id,
            ChatSession.user_id == current_user["user_id"]
        )
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
    
    return {
        "session": {
            "id": str(session.id),
            "title": session.title,
            "session_type": session.session_type,
            "created_at": session.created_at.isoformat()
        },
        "messages": [
            MessageResponse(
                id=message.id,
                content=message.content,
                is_user_message=message.is_user_message,
                message_type=message.message_type,
                sentiment_score=message.sentiment_score,
                created_at=message.created_at
            )
            for message in messages
        ]
    }

@app.post("/api/chatbot/chat/session")
async def create_chat_session(
    title: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new chat session"""
    session = ChatSession(
        id=uuid.uuid4(),
        user_id=current_user["user_id"],
        title=title or "New Chat",
        is_active=True,
        session_type="general"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "id": str(session.id),
        "title": session.title,
        "created_at": session.created_at.isoformat()
    }

# WebSocket endpoint for real-time chat
@app.websocket("/api/chatbot/chat/ws")
async def websocket_chat(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    try:
        # Verify token
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=4001)
            return
        
        # Connect user
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Process message (similar to REST endpoint logic)
                # This would contain the same logic as send_message endpoint
                # but with WebSocket response
                
                response = {
                    "type": "message",
                    "content": "I received your message and I'm here to help.",
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                await manager.send_personal_message(json.dumps(response), user_id)
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=4000)

# Analytics endpoints
@app.get("/api/chatbot/analytics")
async def get_chat_analytics(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get chat analytics for user"""
    user_id = current_user["user_id"]
    
    # Get session stats
    total_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).count()
    
    total_messages = db.query(ChatMessage).join(ChatSession).filter(
        ChatSession.user_id == user_id
    ).count()
    
    # Get recent activity (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_sessions = db.query(ChatSession).filter(
        and_(
            ChatSession.user_id == user_id,
            ChatSession.created_at >= thirty_days_ago
        )
    ).count()
    
    # Average sentiment
    avg_sentiment = db.query(func.avg(ChatSession.avg_sentiment)).filter(
        and_(
            ChatSession.user_id == user_id,
            ChatSession.avg_sentiment.isnot(None)
        )
    ).scalar() or 0
    
    return {
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "recent_sessions": recent_sessions,
        "avg_sentiment": float(avg_sentiment),
        "analysis_period": "30_days"
    }

# Health check
@app.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "chatbot_service",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_enabled": bool(OPENAI_API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)