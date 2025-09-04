"""
Context Analyzer Module

This module analyzes conversation context and user behavior patterns to provide
enhanced understanding for intelligent chatbot responses.

Key Features:
    - Conversation history analysis
    - User intent recognition
    - Emotional state tracking
    - Communication pattern analysis
    
Author: MantraPath Development Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class UserIntent(Enum):
    """User intent classification for response targeting"""
    SEEKING_HELP = "seeking_help"
    SHARING_FEELINGS = "sharing_feelings"
    ASKING_QUESTION = "asking_question"
    EXPRESSING_GRATITUDE = "expressing_gratitude"
    CRISIS_SITUATION = "crisis_situation"
    CASUAL_CONVERSATION = "casual_conversation"

@dataclass
class ConversationContext:
    """
    Comprehensive conversation context analysis
    
    Attributes:
        user_intent (UserIntent): Identified user intent
        emotional_intensity (float): Emotional intensity (0-1)
        conversation_stage (str): Stage of conversation
        key_topics (List[str]): Main topics discussed
        sentiment_score (float): Overall sentiment (-1 to 1)
        urgency_level (int): Urgency level (1-5)
    """
    user_intent: UserIntent
    emotional_intensity: float
    conversation_stage: str
    key_topics: List[str]
    sentiment_score: float
    urgency_level: int

class ContextAnalyzer:
    """
    Context analysis engine for intelligent chatbot responses
    
    Analyzes conversation history, user patterns, and contextual cues
    to provide enhanced understanding for response generation.
    """
    
    def __init__(self):
        """Initialize context analyzer with pattern recognition models"""
        self.intent_keywords = self._load_intent_keywords()
        self.emotion_keywords = self._load_emotion_keywords()
        self.crisis_indicators = self._load_crisis_indicators()
        
        logger.info("ContextAnalyzer initialized successfully")

    async def analyze_conversation_context(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, Any]] = None
    ) -> ConversationContext:
        """
        Analyze conversation context for intelligent response generation
        
        Args:
            user_message (str): Current user message
            conversation_history (List[Dict]): Previous conversation messages
            
        Returns:
            ConversationContext: Analyzed conversation context
        """
        try:
            # Analyze user intent
            user_intent = await self._classify_user_intent(user_message)
            
            # Calculate emotional intensity
            emotional_intensity = await self._calculate_emotional_intensity(user_message)
            
            # Determine conversation stage
            conversation_stage = await self._determine_conversation_stage(
                user_message, conversation_history
            )
            
            # Extract key topics
            key_topics = await self._extract_key_topics(user_message)
            
            # Calculate sentiment score
            sentiment_score = await self._calculate_sentiment(user_message)
            
            # Assess urgency level
            urgency_level = await self._assess_urgency(user_message, emotional_intensity)
            
            return ConversationContext(
                user_intent=user_intent,
                emotional_intensity=emotional_intensity,
                conversation_stage=conversation_stage,
                key_topics=key_topics,
                sentiment_score=sentiment_score,
                urgency_level=urgency_level
            )
            
        except Exception as e:
            logger.error(f"Error analyzing conversation context: {str(e)}")
            return await self._generate_default_context()

    async def _classify_user_intent(self, message: str) -> UserIntent:
        """Classify user intent based on message content"""
        message_lower = message.lower()
        
        # Crisis detection
        crisis_keywords = ["help me", "crisis", "emergency", "can't cope"]
        if any(keyword in message_lower for keyword in crisis_keywords):
            return UserIntent.CRISIS_SITUATION
        
        # Help seeking
        help_keywords = ["help", "advice", "what should i do", "guidance"]
        if any(keyword in message_lower for keyword in help_keywords):
            return UserIntent.SEEKING_HELP
        
        # Sharing feelings
        feeling_keywords = ["feel", "feeling", "i'm", "i am", "experiencing"]
        if any(keyword in message_lower for keyword in feeling_keywords):
            return UserIntent.SHARING_FEELINGS
        
        # Gratitude
        thanks_keywords = ["thank", "appreciate", "grateful", "helped"]
        if any(keyword in message_lower for keyword in thanks_keywords):
            return UserIntent.EXPRESSING_GRATITUDE
        
        # Questions
        question_words = ["how", "what", "why", "when", "where", "can you"]
        if any(word in message_lower for word in question_words) or message.endswith('?'):
            return UserIntent.ASKING_QUESTION
        
        return UserIntent.CASUAL_CONVERSATION

    async def _calculate_emotional_intensity(self, message: str) -> float:
        """Calculate emotional intensity from message content"""
        message_lower = message.lower()
        intensity_score = 0.0
        
        # High intensity indicators
        high_intensity = ["extremely", "very", "really", "so", "overwhelming"]
        intensity_score += sum(0.2 for word in high_intensity if word in message_lower)
        
        # Emotional words
        emotional_words = ["anxious", "depressed", "scared", "excited", "angry"]
        intensity_score += sum(0.15 for word in emotional_words if word in message_lower)
        
        # Punctuation intensity
        intensity_score += message.count('!') * 0.1
        intensity_score += message.count('?') * 0.05
        
        return min(1.0, intensity_score)

    async def _determine_conversation_stage(
        self, 
        message: str, 
        history: List[Dict[str, Any]]
    ) -> str:
        """Determine current stage of conversation"""
        if not history:
            return "opening"
        
        message_count = len(history)
        
        if message_count <= 2:
            return "opening"
        elif message_count <= 5:
            return "exploration"
        elif message_count <= 10:
            return "deepening"
        else:
            return "sustained_support"

    async def _extract_key_topics(self, message: str) -> List[str]:
        """Extract key topics from message"""
        topics = []
        message_lower = message.lower()
        
        topic_keywords = {
            "anxiety": ["anxious", "anxiety", "worried", "panic"],
            "depression": ["depressed", "sad", "down", "hopeless"],
            "relationships": ["relationship", "partner", "friend", "family"],
            "work": ["work", "job", "career", "boss", "colleagues"],
            "sleep": ["sleep", "insomnia", "tired", "exhausted"],
            "stress": ["stress", "stressed", "pressure", "overwhelmed"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

    async def _calculate_sentiment(self, message: str) -> float:
        """Calculate sentiment score (-1 to 1)"""
        message_lower = message.lower()
        
        positive_words = ["good", "better", "happy", "grateful", "hope", "love"]
        negative_words = ["bad", "worse", "sad", "hate", "hopeless", "awful"]
        
        positive_score = sum(1 for word in positive_words if word in message_lower)
        negative_score = sum(1 for word in negative_words if word in message_lower)
        
        total_words = len(message.split())
        if total_words == 0:
            return 0.0
        
        return (positive_score - negative_score) / max(total_words, 1)

    async def _assess_urgency(self, message: str, emotional_intensity: float) -> int:
        """Assess urgency level (1-5)"""
        urgency = 1
        message_lower = message.lower()
        
        # Crisis indicators
        if any(word in message_lower for word in ["crisis", "emergency", "urgent"]):
            urgency = 5
        
        # High emotional intensity
        elif emotional_intensity > 0.7:
            urgency = 4
        elif emotional_intensity > 0.5:
            urgency = 3
        elif emotional_intensity > 0.3:
            urgency = 2
        
        return urgency

    async def _generate_default_context(self) -> ConversationContext:
        """Generate default context when analysis fails"""
        return ConversationContext(
            user_intent=UserIntent.CASUAL_CONVERSATION,
            emotional_intensity=0.3,
            conversation_stage="exploration",
            key_topics=[],
            sentiment_score=0.0,
            urgency_level=2
        )

    def _load_intent_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for intent classification"""
        return {
            "help_seeking": ["help", "advice", "guidance", "support", "what should i do"],
            "crisis": ["crisis", "emergency", "urgent", "can't cope", "desperate"],
            "gratitude": ["thank", "thanks", "grateful", "appreciate"],
            "question": ["how", "what", "why", "when", "where", "can you"]
        }

    def _load_emotion_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for emotion detection"""
        return {
            "anxiety": ["anxious", "worried", "panic", "nervous", "scared"],
            "depression": ["depressed", "sad", "down", "hopeless", "empty"],
            "anger": ["angry", "mad", "frustrated", "irritated", "furious"],
            "joy": ["happy", "excited", "joyful", "elated", "cheerful"]
        }

    def _load_crisis_indicators(self) -> List[str]:
        """Load crisis situation indicators"""
        return [
            "want to die", "kill myself", "end it all", "not worth living",
            "hurt myself", "can't go on", "give up", "suicide"
        ]
