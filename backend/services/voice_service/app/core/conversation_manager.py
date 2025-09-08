"""
Conversation Manager
Handles conversation flow, context, and dialogue management
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ConversationTurn:
    """Represents a single turn in conversation"""
    id: str
    user_input: str
    bot_response: str
    timestamp: datetime
    sentiment: str
    confidence: float
    language: str
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConversationSession:
    """Represents a conversation session"""
    session_id: str
    user_id: Optional[str]
    created_at: datetime
    last_activity: datetime
    turns: List[ConversationTurn] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

class ConversationManager:
    """Manages conversation flow and context"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self.max_turns_per_session = 50
        self.session_timeout_minutes = 30
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created conversation session {session_id} for user {user_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get conversation session by ID"""
        return self.sessions.get(session_id)
    
    def add_turn(self, session_id: str, user_input: str, bot_response: str,
                 sentiment: str = "neutral", confidence: float = 0.0,
                 language: str = "en", context: Optional[Dict[str, Any]] = None) -> bool:
        """Add a conversation turn to session"""
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return False
        
        turn_id = str(uuid.uuid4())
        turn = ConversationTurn(
            id=turn_id,
            user_input=user_input,
            bot_response=bot_response,
            timestamp=datetime.now(),
            sentiment=sentiment,
            confidence=confidence,
            language=language,
            context=context or {}
        )
        
        session.turns.append(turn)
        session.last_activity = datetime.now()
        
        # Limit number of turns to prevent memory issues
        if len(session.turns) > self.max_turns_per_session:
            session.turns = session.turns[-self.max_turns_per_session:]
        
        logger.debug(f"Added turn to session {session_id}: {user_input[:50]}...")
        return True
    
    def get_conversation_context(self, session_id: str, max_turns: int = 5) -> Dict[str, Any]:
        """Get recent conversation context"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        recent_turns = session.turns[-max_turns:] if session.turns else []
        
        return {
            "session_id": session_id,
            "user_id": session.user_id,
            "conversation_length": len(session.turns),
            "recent_turns": [
                {
                    "user": turn.user_input,
                    "bot": turn.bot_response,
                    "sentiment": turn.sentiment,
                    "language": turn.language,
                    "timestamp": turn.timestamp.isoformat()
                }
                for turn in recent_turns
            ],
            "session_context": session.context,
            "preferences": session.preferences
        }
    
    def update_session_context(self, session_id: str, context_update: Dict[str, Any]) -> bool:
        """Update session context"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.context.update(context_update)
        session.last_activity = datetime.now()
        return True
    
    def update_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences for session"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.preferences.update(preferences)
        return True
    
    def get_sentiment_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get sentiment history for session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        recent_turns = session.turns[-limit:] if session.turns else []
        return [
            {
                "sentiment": turn.sentiment,
                "confidence": turn.confidence,
                "timestamp": turn.timestamp.isoformat(),
                "user_input": turn.user_input[:100]  # Truncated for privacy
            }
            for turn in recent_turns
        ]
    
    def detect_conversation_patterns(self, session_id: str) -> Dict[str, Any]:
        """Analyze conversation patterns"""
        session = self.get_session(session_id)
        if not session or not session.turns:
            return {"patterns": []}
        
        # Simple pattern detection
        sentiments = [turn.sentiment for turn in session.turns]
        languages = [turn.language for turn in session.turns]
        
        # Count sentiment distribution
        sentiment_counts = {}
        for sentiment in sentiments:
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        # Count language distribution
        language_counts = {}
        for language in languages:
            language_counts[language] = language_counts.get(language, 0) + 1
        
        patterns = []
        
        # Detect mood patterns
        if len(sentiments) >= 3:
            recent_sentiments = sentiments[-3:]
            if all(s == "negative" for s in recent_sentiments):
                patterns.append("consecutive_negative_sentiment")
            elif all(s == "positive" for s in recent_sentiments):
                patterns.append("consecutive_positive_sentiment")
        
        # Detect language switching
        unique_languages = set(languages)
        if len(unique_languages) > 1:
            patterns.append("multilingual_conversation")
        
        return {
            "patterns": patterns,
            "sentiment_distribution": sentiment_counts,
            "language_distribution": language_counts,
            "total_turns": len(session.turns),
            "session_duration_minutes": (
                (session.last_activity - session.created_at).total_seconds() / 60
            )
        }
    
    def generate_contextual_response(self, session_id: str, user_input: str, 
                                   sentiment: str, language: str) -> str:
        """Generate contextual response based on conversation history"""
        session = self.get_session(session_id)
        if not session:
            return "I'm sorry, I don't have the context of our conversation."
        
        # Get conversation patterns
        patterns = self.detect_conversation_patterns(session_id)
        
        # Basic contextual responses based on patterns
        if "consecutive_negative_sentiment" in patterns["patterns"]:
            if language == "hi":
                return "मुझे लगता है कि आप परेशान हैं। क्या मैं आपकी कुछ मदद कर सकता हूँ?"
            else:
                return "I notice you seem upset. Is there something specific I can help you with?"
        
        elif "consecutive_positive_sentiment" in patterns["patterns"]:
            if language == "hi":
                return "यह बहुत अच्छी बात है! आपकी खुशी मुझे भी खुश करती है।"
            else:
                return "That's wonderful! I'm glad you're feeling positive."
        
        elif "multilingual_conversation" in patterns["patterns"]:
            if language == "hi":
                return "मैं देख रहा हूँ कि आप कई भाषाओं में बात कर रहे हैं। मैं हिंदी और अंग्रेजी दोनों में आपकी मदद कर सकता हूँ।"
            else:
                return "I notice you're using multiple languages. I can help you in both Hindi and English."
        
        # Default contextual response
        turn_count = len(session.turns)
        if turn_count == 0:
            if language == "hi":
                return "नमस्ते! मैं आपकी कैसे सहायता कर सकता हूँ?"
            else:
                return "Hello! How can I assist you today?"
        else:
            if language == "hi":
                return f"मैं समझ गया। आपने कहा: '{user_input}'. मैं आपकी और कैसे मदद कर सकता हूँ?"
            else:
                return f"I understand. You said: '{user_input}'. How else can I help you?"
    
    def cleanup_inactive_sessions(self) -> int:
        """Clean up inactive sessions"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            time_diff = (now - session.last_activity).total_seconds() / 60
            if time_diff > self.session_timeout_minutes:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session {session_id}")
        
        return len(expired_sessions)
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about all sessions"""
        active_sessions = len(self.sessions)
        total_turns = sum(len(session.turns) for session in self.sessions.values())
        
        return {
            "active_sessions": active_sessions,
            "total_turns": total_turns,
            "average_turns_per_session": total_turns / active_sessions if active_sessions > 0 else 0
        }
