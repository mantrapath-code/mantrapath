"""
Enhanced Chatbot Service - Demo Implementation
Shows how to integrate the User Context Engine for personalized responses
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import sys
import json
import logging

# Add parent directories to path
sys.path.append('/app')
sys.path.append('/app/shared')

from shared.database import get_db, engine
from shared.models import ChatSession, ChatMessage, Base
from shared.auth import get_current_user

# Import the new context engine
from context_engine import UserContextEngine, UserContext

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MantraPath Enhanced Chatbot Service",
    description="AI chatbot with personalized support using complete user context",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the context engine
context_engine = UserContextEngine()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Pydantic models
class EnhancedChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context_refresh: bool = False

class EnhancedChatResponse(BaseModel):
    response: str
    session_id: str
    message_type: str = "personalized"
    personalization_score: float = 0.0
    context_insights: Dict[str, Any] = {}
    user_state: str = "neutral"

class ContextualResponseGenerator:
    """Generate responses using user context"""
    
    def __init__(self):
        self.response_templates = {
            'greeting': {
                'high_mood': "Hello {name}! I can see you've been feeling pretty good lately. What's on your mind today?",
                'neutral_mood': "Hi {name}! How are you feeling today?",
                'low_mood': "Hello {name}. I've noticed things might be challenging lately. I'm here to support you."
            },
            'check_in': {
                'improving_trend': "I've noticed your mood has been improving recently, {name}. That's wonderful! What's been helping you feel better?",
                'declining_trend': "I can see you might be going through a tough time, {name}. Would you like to talk about what's been bothering you?",
                'stable_trend': "You seem to be maintaining a steady emotional state, {name}. How can I support you today?"
            },
            'support': {
                'high_engagement': "I know you're active in the community forums, {name}. Sometimes sharing with others can be really helpful.",
                'low_engagement': "I'm here to listen, {name}. Sometimes it helps to just talk through what's on your mind.",
                'journal_writer': "I see you've been journaling regularly, {name}. That's a great way to process your thoughts."
            }
        }
    
    async def generate_personalized_response(
        self, 
        user_input: str, 
        context: UserContext
    ) -> Dict[str, Any]:
        """Generate a personalized response based on user context"""
        
        name = context.profile.get('first_name', 'friend')
        mood_trend = context.mood_patterns.get('trend', 'stable')
        current_mood = context.current_state.get('current_mood_score', 3)
        engagement_level = context.community_behavior.get('engagement_level', 'minimal')
        
        # Determine response strategy based on context
        response_strategy = self._determine_response_strategy(user_input, context)
        
        # Generate appropriate response
        if response_strategy == 'greeting':
            response = self._generate_greeting_response(name, current_mood)
        elif response_strategy == 'mood_check':
            response = self._generate_mood_check_response(name, mood_trend)
        elif response_strategy == 'support':
            response = self._generate_support_response(name, engagement_level, context)
        elif response_strategy == 'crisis':
            response = self._generate_crisis_response(name, context)
        else:
            response = self._generate_default_response(name, user_input, context)
        
        # Calculate personalization score
        personalization_score = self._calculate_personalization_score(context)
        
        return {
            'response': response,
            'message_type': 'personalized',
            'personalization_score': personalization_score,
            'context_insights': self._extract_context_insights(context),
            'user_state': self._assess_user_state(context)
        }
    
    def _determine_response_strategy(self, user_input: str, context: UserContext) -> str:
        """Determine the best response strategy based on input and context"""
        
        user_input_lower = user_input.lower()
        current_mood = context.current_state.get('current_mood_score', 3)
        
        # Check for crisis indicators
        crisis_keywords = ['suicide', 'kill myself', 'end it all', 'want to die', 'no point']
        if any(keyword in user_input_lower for keyword in crisis_keywords):
            return 'crisis'
        
        # Check for greetings
        greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good evening']
        if any(keyword in user_input_lower for keyword in greeting_keywords):
            return 'greeting'
        
        # Check for mood-related queries
        mood_keywords = ['feeling', 'mood', 'emotions', 'how am i']
        if any(keyword in user_input_lower for keyword in mood_keywords):
            return 'mood_check'
        
        # Check if user needs support
        support_keywords = ['help', 'support', 'struggling', 'difficult', 'hard time']
        if any(keyword in user_input_lower for keyword in support_keywords) or current_mood < 3:
            return 'support'
        
        return 'general'
    
    def _generate_greeting_response(self, name: str, current_mood: float) -> str:
        """Generate a greeting response based on current mood"""
        
        if current_mood >= 4:
            mood_category = 'high_mood'
        elif current_mood >= 3:
            mood_category = 'neutral_mood'
        else:
            mood_category = 'low_mood'
        
        template = self.response_templates['greeting'][mood_category]
        return template.format(name=name)
    
    def _generate_mood_check_response(self, name: str, mood_trend: str) -> str:
        """Generate a mood check response based on trend"""
        
        if mood_trend == 'improving':
            trend_category = 'improving_trend'
        elif mood_trend == 'declining':
            trend_category = 'declining_trend'
        else:
            trend_category = 'stable_trend'
        
        template = self.response_templates['check_in'][trend_category]
        return template.format(name=name)
    
    def _generate_support_response(
        self, 
        name: str, 
        engagement_level: str, 
        context: UserContext
    ) -> str:
        """Generate a support response based on user's engagement patterns"""
        
        # Check if user writes journals
        journal_entries = context.writing_style.get('total_entries', 0)
        
        if journal_entries > 5:
            response_type = 'journal_writer'
        elif engagement_level == 'high':
            response_type = 'high_engagement'
        else:
            response_type = 'low_engagement'
        
        template = self.response_templates['support'][response_type]
        return template.format(name=name)
    
    def _generate_crisis_response(self, name: str, context: UserContext) -> str:
        """Generate immediate crisis response"""
        
        return f"""
{name}, I'm really concerned about what you just shared. Your life has value and meaning, 
and I want to help you through this difficult time. Please know that you're not alone.

If you're having thoughts of suicide, please reach out for immediate help:
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911

Would you like me to help you connect with a crisis counselor right now?
        """.strip()
    
    def _generate_default_response(
        self, 
        name: str, 
        user_input: str, 
        context: UserContext
    ) -> str:
        """Generate a default personalized response"""
        
        # Use context to personalize the response
        mood_trend = context.mood_patterns.get('trend', 'stable')
        common_themes = context.writing_style.get('common_themes', [])
        
        response = f"Thank you for sharing that with me, {name}."
        
        # Add context-specific insights
        if mood_trend == 'declining':
            response += " I've noticed you might be going through a challenging time lately."
        elif mood_trend == 'improving':
            response += " I can see you've been making positive progress recently."
        
        if common_themes:
            theme = common_themes[0]
            response += f" I remember you've been reflecting on {theme} in your journal entries."
        
        response += " How can I best support you right now?"
        
        return response
    
    def _calculate_personalization_score(self, context: UserContext) -> float:
        """Calculate how personalized the response is"""
        
        score = 0.5  # Base score
        
        # Add points for available context data
        if context.mood_patterns.get('total_entries', 0) > 0:
            score += 0.1
        
        if context.writing_style.get('total_entries', 0) > 0:
            score += 0.1
        
        if context.community_behavior.get('total_posts', 0) > 0:
            score += 0.1
        
        if context.conversation_history.get('total_sessions', 0) > 0:
            score += 0.1
        
        if context.profile.get('first_name') != 'Friend':
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_context_insights(self, context: UserContext) -> Dict[str, Any]:
        """Extract key insights from user context"""
        
        return {
            'mood_trend': context.mood_patterns.get('trend'),
            'engagement_level': context.community_behavior.get('engagement_level'),
            'writing_frequency': context.writing_style.get('writing_frequency', 0),
            'conversation_frequency': context.conversation_history.get('conversation_frequency', 0),
            'days_since_last_mood': context.current_state.get('days_since_mood_entry'),
            'overall_state': context.current_state.get('overall_state')
        }
    
    def _assess_user_state(self, context: UserContext) -> str:
        """Assess overall user state"""
        
        current_mood = context.current_state.get('current_mood_score', 3)
        mood_trend = context.mood_patterns.get('trend', 'stable')
        
        if current_mood < 2:
            return 'concerning'
        elif current_mood < 3 and mood_trend == 'declining':
            return 'needs_support'
        elif current_mood >= 4:
            return 'positive'
        else:
            return 'neutral'

# Initialize response generator
response_generator = ContextualResponseGenerator()

@app.post("/api/chatbot/enhanced/chat", response_model=EnhancedChatResponse)
async def enhanced_chat_with_bot(
    chat_request: EnhancedChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced chat with full user context and personalization"""
    
    user_id = current_user["user_id"]
    
    try:
        # Get comprehensive user context
        logger.info(f"Getting context for user {user_id}")
        user_context = await context_engine.get_user_context(
            user_id, 
            db, 
            force_refresh=chat_request.context_refresh
        )
        
        # Get or create session
        session = await get_or_create_session(chat_request.session_id, user_id, db)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            sender="user",
            content=chat_request.message,
            message_type="text"
        )
        db.add(user_message)
        
        # Generate personalized response
        response_data = await response_generator.generate_personalized_response(
            chat_request.message,
            user_context
        )
        
        # Save AI message
        ai_message = ChatMessage(
            session_id=session.id,
            sender="assistant",
            content=response_data['response'],
            message_type=response_data['message_type'],
            metadata={
                "personalization_score": response_data['personalization_score'],
                "context_insights": response_data['context_insights'],
                "user_state": response_data['user_state']
            }
        )
        db.add(ai_message)
        db.commit()
        
        logger.info(f"Generated personalized response for user {user_id}")
        
        return EnhancedChatResponse(
            response=response_data['response'],
            session_id=str(session.id),
            message_type=response_data['message_type'],
            personalization_score=response_data['personalization_score'],
            context_insights=response_data['context_insights'],
            user_state=response_data['user_state']
        )
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {e}")
        # Fallback to simple response
        return EnhancedChatResponse(
            response=f"I'm here to help you. Can you tell me more about what's on your mind?",
            session_id=chat_request.session_id or "fallback",
            message_type="fallback",
            personalization_score=0.0
        )

@app.get("/api/chatbot/context/{user_id}")
async def get_user_context_summary(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user context summary for debugging/admin purposes"""
    
    # Only allow users to see their own context
    if current_user["user_id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        context = await context_engine.get_user_context(user_id, db)
        
        # Return sanitized context summary
        return {
            "user_id": context.user_id,
            "profile_summary": {
                "name": context.profile.get('first_name'),
                "account_age_days": context.profile.get('account_age_days'),
                "timezone": context.profile.get('timezone')
            },
            "mood_summary": {
                "trend": context.mood_patterns.get('trend'),
                "average_mood": context.mood_patterns.get('average_mood'),
                "total_entries": context.mood_patterns.get('total_entries')
            },
            "writing_summary": {
                "total_entries": context.writing_style.get('total_entries'),
                "avg_word_count": context.writing_style.get('avg_word_count'),
                "common_themes": context.writing_style.get('common_themes')
            },
            "community_summary": {
                "engagement_level": context.community_behavior.get('engagement_level'),
                "forums_joined": context.community_behavior.get('forums_joined'),
                "total_posts": context.community_behavior.get('total_posts')
            },
            "current_state": context.current_state,
            "last_updated": context.last_updated.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting context summary: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving context")

# Keeping the original endpoints for backward compatibility
@app.post("/api/chatbot/chat")
async def chat_with_bot(
    chat_request: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Original chat endpoint with basic functionality"""
    
    # Convert to enhanced request and delegate
    enhanced_request = EnhancedChatRequest(
        message=chat_request.get('message', ''),
        session_id=chat_request.get('session_id')
    )
    
    response = await enhanced_chat_with_bot(enhanced_request, current_user, db)
    
    # Return in original format
    return {
        "response": response.response,
        "session_id": response.session_id,
        "message_type": response.message_type
    }

# Helper functions
async def get_or_create_session(session_id: Optional[str], user_id: str, db: Session) -> ChatSession:
    """Get existing session or create new one"""
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        if session:
            return session
    
    # Create new session
    session = ChatSession(
        user_id=user_id,
        title="Enhanced Chat Session",
        session_type="personalized"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@app.get("/health")
async def health_check():
    """Enhanced health check with context engine status"""
    return {
        "status": "healthy",
        "service": "enhanced_chatbot_service",
        "version": "2.0.0",
        "timestamp": datetime.utcnow(),
        "features": [
            "user_context_awareness",
            "personalized_responses",
            "mood_trend_analysis",
            "community_behavior_insights",
            "writing_style_adaptation"
        ],
        "context_engine": {
            "status": "ready",
            "cache_entries": len(context_engine.context_cache)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
