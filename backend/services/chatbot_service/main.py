"""
Chatbot Service - AI-powered conversational support with breathing exercises
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import json

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_database, engine
from shared.models import ChatSession, ChatMessage, Base
from shared.auth import get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MantraPath Chatbot Service",
    description="AI chatbot with mental health support and breathing exercises",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_type: str = "text"
    breathing_exercise: Optional[dict] = None

class MessageResponse(BaseModel):
    id: str
    sender: str
    content: str
    message_type: str
    created_at: datetime

class SessionResponse(BaseModel):
    id: str
    title: str
    session_type: str
    is_active: bool
    created_at: datetime

# Breathing exercises data
BREATHING_EXERCISES = {
    "4-7-8": {
        "name": "4-7-8 Breathing",
        "description": "Inhale for 4, hold for 7, exhale for 8",
        "steps": [
            {"action": "inhale", "duration": 4, "instruction": "Breathe in slowly through your nose"},
            {"action": "hold", "duration": 7, "instruction": "Hold your breath"},
            {"action": "exhale", "duration": 8, "instruction": "Exhale slowly through your mouth"}
        ],
        "cycles": 4
    },
    "box": {
        "name": "Box Breathing",
        "description": "Equal timing for inhale, hold, exhale, hold",
        "steps": [
            {"action": "inhale", "duration": 4, "instruction": "Breathe in slowly"},
            {"action": "hold", "duration": 4, "instruction": "Hold your breath"},
            {"action": "exhale", "duration": 4, "instruction": "Breathe out slowly"},
            {"action": "hold", "duration": 4, "instruction": "Hold empty lungs"}
        ],
        "cycles": 5
    },
    "calm": {
        "name": "Calming Breath",
        "description": "Simple rhythm for immediate calm",
        "steps": [
            {"action": "inhale", "duration": 3, "instruction": "Breathe in gently"},
            {"action": "exhale", "duration": 6, "instruction": "Breathe out slowly, releasing tension"}
        ],
        "cycles": 6
    }
}

# Simple AI response logic
def generate_ai_response(message: str, conversation_history: List[dict]) -> dict:
    """Generate AI response based on message content"""
    
    message_lower = message.lower()
    
    # Check for stress/anxiety keywords
    stress_keywords = ["stress", "stressed", "anxious", "anxiety", "worried", "panic", "overwhelmed"]
    sadness_keywords = ["sad", "depressed", "down", "lonely", "hopeless"]
    breathing_keywords = ["breathe", "breathing", "calm", "relax", "exercise"]
    
    # Determine response type and content
    if any(keyword in message_lower for keyword in breathing_keywords):
        return {
            "response": "I'd love to guide you through a breathing exercise. Let's try the 4-7-8 technique - it's very effective for calming the mind and body.",
            "message_type": "breathing_exercise",
            "breathing_exercise": BREATHING_EXERCISES["4-7-8"]
        }
    
    elif any(keyword in message_lower for keyword in stress_keywords):
        return {
            "response": "I can hear that you're feeling stressed or anxious. That's completely understandable. Would you like to try a quick breathing exercise to help you feel more centered? I can guide you through one right now.",
            "message_type": "supportive",
            "breathing_exercise": BREATHING_EXERCISES["box"]
        }
    
    elif any(keyword in message_lower for keyword in sadness_keywords):
        return {
            "response": "I'm sorry you're feeling this way. Your feelings are valid, and it's okay to not be okay sometimes. Remember that you're not alone. Would a gentle breathing exercise help you feel a bit more grounded?",
            "message_type": "supportive",
            "breathing_exercise": BREATHING_EXERCISES["calm"]
        }
    
    elif "help" in message_lower:
        return {
            "response": "I'm here to support you! I can help with:\n• Breathing exercises for stress and anxiety\n• Listening to your concerns\n• Providing coping strategies\n• Guiding you through difficult moments\n\nWhat would be most helpful for you right now?",
            "message_type": "supportive"
        }
    
    elif any(word in message_lower for word in ["thanks", "thank you", "better", "good"]):
        return {
            "response": "I'm so glad to hear that! Remember, taking care of your mental health is an ongoing journey. I'm always here when you need support. Keep up the great work! 💜",
            "message_type": "encouraging"
        }
    
    else:
        # General supportive response
        responses = [
            "I hear you. Can you tell me more about what you're experiencing?",
            "That sounds challenging. How are you feeling about that?",
            "Thank you for sharing that with me. What's been on your mind lately?",
            "I'm here to listen. Would you like to explore that feeling a bit more?",
            "It takes courage to reach out. How can I best support you right now?"
        ]
        
        # Simple selection based on message length
        response_index = len(message) % len(responses)
        
        return {
            "response": responses[response_index],
            "message_type": "supportive"
        }

# Chat endpoints
@app.post("/api/chatbot/chat", response_model=ChatResponse)
async def chat_with_bot(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Chat with the AI bot"""
    
    # Get or create session
    if chat_request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == chat_request.session_id,
            ChatSession.user_id == current_user["user_id"]
        ).first()
    else:
        session = None
    
    if not session:
        session = ChatSession(
            user_id=current_user["user_id"],
            title="Chat Session",
            session_type="general"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save user message
    user_message = ChatMessage(
        session_id=session.id,
        sender="user",
        content=chat_request.message,
        message_type="text"
    )
    db.add(user_message)
    
    # Get conversation history
    history = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at).all()
    
    conversation_history = [
        {"sender": msg.sender, "content": msg.content}
        for msg in history
    ]
    
    # Generate AI response
    ai_response = generate_ai_response(chat_request.message, conversation_history)
    
    # Save AI message
    ai_message = ChatMessage(
        session_id=session.id,
        sender="assistant",
        content=ai_response["response"],
        message_type=ai_response["message_type"],
        metadata={"breathing_exercise": ai_response.get("breathing_exercise")}
    )
    db.add(ai_message)
    db.commit()
    
    return ChatResponse(
        response=ai_response["response"],
        session_id=str(session.id),
        message_type=ai_response["message_type"],
        breathing_exercise=ai_response.get("breathing_exercise")
    )

@app.get("/api/chatbot/chat/sessions", response_model=List[SessionResponse])
async def get_chat_sessions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get user's chat sessions"""
    
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user["user_id"]
    ).order_by(ChatSession.created_at.desc()).limit(10).all()
    
    return [
        SessionResponse(
            id=str(session.id),
            title=session.title,
            session_type=session.session_type,
            is_active=session.is_active,
            created_at=session.created_at
        )
        for session in sessions
    ]

@app.get("/api/chatbot/chat/history")
async def get_chat_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get chat history for a session"""
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user["user_id"]
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return [
        MessageResponse(
            id=str(message.id),
            sender=message.sender,
            content=message.content,
            message_type=message.message_type,
            created_at=message.created_at
        )
        for message in messages
    ]

@app.get("/api/chatbot/breathing-exercises")
async def get_breathing_exercises():
    """Get available breathing exercises"""
    return {"exercises": BREATHING_EXERCISES}

@app.post("/api/chatbot/chat/session")
async def create_chat_session(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Create new chat session"""
    
    session = ChatSession(
        user_id=current_user["user_id"],
        title="New Chat",
        session_type="general"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return SessionResponse(
        id=str(session.id),
        title=session.title,
        session_type=session.session_type,
        is_active=session.is_active,
        created_at=session.created_at
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chatbot-service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)