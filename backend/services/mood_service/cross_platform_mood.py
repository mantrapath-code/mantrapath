"""
Cross-Platform Mood Intelligence System
Tracks and infers mood from all user interactions across MantraPath
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class MoodSource(Enum):
    """Sources of mood data across the platform"""
    DIRECT_ENTRY = "direct_entry"          # User manually logs mood
    JOURNAL_SENTIMENT = "journal_sentiment" # Inferred from journal writing
    CHAT_ANALYSIS = "chat_analysis"        # Inferred from chatbot conversations
    COMMUNITY_ENGAGEMENT = "community_engagement"  # Inferred from community posts
    CHALLENGE_PROGRESS = "challenge_progress"       # Inferred from challenge completion
    ACTIVITY_PATTERN = "activity_pattern"          # Inferred from app usage patterns

@dataclass
class MoodSignal:
    """A single mood indicator from any platform interaction"""
    source: MoodSource
    mood_score: float  # -1.0 to 1.0 normalized
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    context: Dict[str, Any]
    raw_data: Dict[str, Any]

class CrossPlatformMoodIntelligence:
    """
    Unified mood tracking across all MantraPath interactions
    Provides intelligent mood inference and real-time updates
    """
    
    def __init__(self):
        self.mood_weights = {
            MoodSource.DIRECT_ENTRY: 1.0,        # Highest weight - direct user input
            MoodSource.JOURNAL_SENTIMENT: 0.8,   # High weight - reflective content
            MoodSource.CHAT_ANALYSIS: 0.6,       # Medium weight - conversational context
            MoodSource.COMMUNITY_ENGAGEMENT: 0.5, # Medium weight - social interaction
            MoodSource.CHALLENGE_PROGRESS: 0.4,   # Lower weight - activity-based
            MoodSource.ACTIVITY_PATTERN: 0.3     # Lowest weight - behavioral inference
        }
        
    async def process_mood_signal(self, signal: MoodSignal, user_id: str) -> Dict[str, Any]:
        """Process a new mood signal and update user's mood profile"""
        
        # Store the signal
        await self._store_mood_signal(signal, user_id)
        
        # Calculate updated mood state
        current_mood_state = await self._calculate_current_mood(user_id)
        
        # Detect mood changes and patterns
        mood_insights = await self._analyze_mood_patterns(user_id, signal)
        
        # Generate real-time updates if significant change
        if mood_insights.get('significant_change'):
            await self._publish_mood_update(user_id, current_mood_state, mood_insights)
            
        return {
            "mood_state": current_mood_state,
            "insights": mood_insights,
            "signal_processed": True
        }
    
    async def infer_mood_from_journal(self, journal_data: Dict[str, Any], user_id: str) -> MoodSignal:
        """Infer mood from journal entry sentiment and content"""
        try:
            from textblob import TextBlob
            
            content = journal_data.get('content', '')
            blob = TextBlob(content)
            
            # Sentiment analysis
            sentiment_score = blob.sentiment.polarity  # -1 to 1
            confidence = abs(blob.sentiment.subjectivity)  # 0 to 1
            
            # Content analysis for mood indicators
            mood_keywords = self._extract_mood_keywords(content)
            
            # Adjust sentiment based on mood keywords
            adjusted_score = self._adjust_sentiment_with_keywords(sentiment_score, mood_keywords)
            
            return MoodSignal(
                source=MoodSource.JOURNAL_SENTIMENT,
                mood_score=adjusted_score,
                confidence=min(confidence + 0.2, 1.0),  # Boost confidence for journal entries
                timestamp=datetime.utcnow(),
                context={
                    "word_count": len(content.split()),
                    "themes": mood_keywords,
                    "sentiment_raw": sentiment_score
                },
                raw_data=journal_data
            )
            
        except Exception as e:
            logger.error(f"Error processing journal mood: {e}")
            return self._create_neutral_signal(MoodSource.JOURNAL_SENTIMENT)
    
    async def infer_mood_from_chat(self, chat_data: Dict[str, Any], user_id: str) -> MoodSignal:
        """Infer mood from chatbot conversation analysis"""
        try:
            user_message = chat_data.get('user_message', '')
            bot_response = chat_data.get('bot_response', '')
            
            # Analyze user's emotional state from their messages
            mood_indicators = self._analyze_chat_emotional_indicators(user_message)
            
            # Consider conversation context
            conversation_type = chat_data.get('conversation_type', 'general')
            
            # Calculate mood score based on conversation analysis
            mood_score = self._calculate_chat_mood_score(mood_indicators, conversation_type)
            
            return MoodSignal(
                source=MoodSource.CHAT_ANALYSIS,
                mood_score=mood_score,
                confidence=0.6,  # Moderate confidence for chat analysis
                timestamp=datetime.utcnow(),
                context={
                    "conversation_type": conversation_type,
                    "emotional_indicators": mood_indicators,
                    "message_length": len(user_message)
                },
                raw_data=chat_data
            )
            
        except Exception as e:
            logger.error(f"Error processing chat mood: {e}")
            return self._create_neutral_signal(MoodSource.CHAT_ANALYSIS)
    
    async def infer_mood_from_community(self, community_data: Dict[str, Any], user_id: str) -> MoodSignal:
        """Infer mood from community participation and engagement"""
        try:
            interaction_type = community_data.get('type')  # post, comment, like, join_event
            content = community_data.get('content', '')
            
            mood_score = 0.0
            confidence = 0.4
            
            if interaction_type == 'post_created':
                # Analyze post content sentiment
                if content:
                    from textblob import TextBlob
                    blob = TextBlob(content)
                    mood_score = blob.sentiment.polarity * 0.8  # Slightly dampened
                    confidence = 0.6
                    
            elif interaction_type == 'event_joined':
                # Joining events indicates positive engagement
                mood_score = 0.3
                confidence = 0.5
                
            elif interaction_type == 'comment_added':
                # Comments indicate engagement, analyze sentiment
                if content:
                    from textblob import TextBlob
                    blob = TextBlob(content)
                    mood_score = blob.sentiment.polarity * 0.6
                    confidence = 0.5
            
            return MoodSignal(
                source=MoodSource.COMMUNITY_ENGAGEMENT,
                mood_score=mood_score,
                confidence=confidence,
                timestamp=datetime.utcnow(),
                context={
                    "interaction_type": interaction_type,
                    "engagement_level": self._calculate_engagement_level(community_data)
                },
                raw_data=community_data
            )
            
        except Exception as e:
            logger.error(f"Error processing community mood: {e}")
            return self._create_neutral_signal(MoodSource.COMMUNITY_ENGAGEMENT)
    
    async def infer_mood_from_challenge(self, challenge_data: Dict[str, Any], user_id: str) -> MoodSignal:
        """Infer mood from challenge progress and completion"""
        try:
            event_type = challenge_data.get('event_type')
            progress = challenge_data.get('progress', 0)
            completed = challenge_data.get('completed', False)
            
            mood_score = 0.0
            confidence = 0.4
            
            if completed:
                # Challenge completion indicates positive mood
                mood_score = 0.4
                confidence = 0.6
            elif progress > 0:
                # Progress indicates positive engagement
                mood_score = 0.2
                confidence = 0.5
            
            # Consider streak information
            streak = challenge_data.get('streak', 0)
            if streak > 3:
                mood_score += 0.1  # Bonus for streaks
                
            return MoodSignal(
                source=MoodSource.CHALLENGE_PROGRESS,
                mood_score=min(mood_score, 1.0),
                confidence=confidence,
                timestamp=datetime.utcnow(),
                context={
                    "event_type": event_type,
                    "progress": progress,
                    "streak": streak,
                    "completed": completed
                },
                raw_data=challenge_data
            )
            
        except Exception as e:
            logger.error(f"Error processing challenge mood: {e}")
            return self._create_neutral_signal(MoodSource.CHALLENGE_PROGRESS)
    
    def _extract_mood_keywords(self, text: str) -> List[str]:
        """Extract mood-related keywords from text"""
        mood_keywords = {
            'positive': ['happy', 'joy', 'excited', 'grateful', 'blessed', 'amazing', 'wonderful', 'great', 'good', 'love'],
            'negative': ['sad', 'depressed', 'angry', 'frustrated', 'worried', 'anxious', 'stressed', 'tired', 'exhausted'],
            'neutral': ['okay', 'fine', 'normal', 'average', 'usual']
        }
        
        found_keywords = []
        words = text.lower().split()
        
        for category, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword in words:
                    found_keywords.append(f"{category}:{keyword}")
        
        return found_keywords
    
    def _adjust_sentiment_with_keywords(self, sentiment_score: float, keywords: List[str]) -> float:
        """Adjust sentiment score based on specific mood keywords"""
        adjustment = 0.0
        
        for keyword in keywords:
            if keyword.startswith('positive:'):
                adjustment += 0.1
            elif keyword.startswith('negative:'):
                adjustment -= 0.1
        
        return max(-1.0, min(1.0, sentiment_score + adjustment))
    
    def _analyze_chat_emotional_indicators(self, message: str) -> Dict[str, Any]:
        """Analyze emotional indicators in chat messages"""
        indicators = {
            'exclamation_marks': message.count('!'),
            'question_marks': message.count('?'),
            'caps_ratio': sum(1 for c in message if c.isupper()) / max(len(message), 1),
            'positive_words': len([w for w in message.lower().split() if w in ['great', 'good', 'happy', 'yes', 'awesome']]),
            'negative_words': len([w for w in message.lower().split() if w in ['bad', 'no', 'sad', 'terrible', 'awful']]),
            'length': len(message)
        }
        return indicators
    
    def _calculate_chat_mood_score(self, indicators: Dict[str, Any], conversation_type: str) -> float:
        """Calculate mood score from chat indicators"""
        score = 0.0
        
        # Positive indicators
        if indicators['positive_words'] > 0:
            score += 0.3
        if indicators['exclamation_marks'] > 0:
            score += 0.1
            
        # Negative indicators  
        if indicators['negative_words'] > 0:
            score -= 0.3
        if indicators['caps_ratio'] > 0.5:  # Too much caps might indicate stress
            score -= 0.1
            
        # Conversation type context
        if conversation_type in ['crisis', 'support']:
            score -= 0.2  # User seeking help typically indicates lower mood
        elif conversation_type in ['celebration', 'achievement']:
            score += 0.2  # Positive conversation topics
            
        return max(-1.0, min(1.0, score))
    
    def _calculate_engagement_level(self, community_data: Dict[str, Any]) -> str:
        """Calculate user's engagement level from community interaction"""
        # This would analyze posting frequency, interaction depth, etc.
        return "moderate"  # Placeholder
    
    def _create_neutral_signal(self, source: MoodSource) -> MoodSignal:
        """Create a neutral mood signal as fallback"""
        return MoodSignal(
            source=source,
            mood_score=0.0,
            confidence=0.1,
            timestamp=datetime.utcnow(),
            context={},
            raw_data={}
        )
    
    async def _store_mood_signal(self, signal: MoodSignal, user_id: str):
        """Store mood signal in database for historical analysis"""
        # This would store in a mood_signals table
        logger.info(f"Storing mood signal: {signal.source.value} for user {user_id}")
    
    async def _calculate_current_mood(self, user_id: str) -> Dict[str, Any]:
        """Calculate user's current mood state from recent signals"""
        # This would aggregate recent signals with weighted average
        return {
            "overall_mood": 0.0,
            "confidence": 0.5,
            "primary_source": "multiple",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def _analyze_mood_patterns(self, user_id: str, latest_signal: MoodSignal) -> Dict[str, Any]:
        """Analyze mood patterns and detect significant changes"""
        return {
            "significant_change": False,
            "pattern": "stable",
            "trend": "neutral"
        }
    
    async def _publish_mood_update(self, user_id: str, mood_state: Dict, insights: Dict):
        """Publish real-time mood update via E4 pipeline"""
        from shared.events import publish_insight_delta
        
        delta_data = {
            "type": "mood_update",
            "mood_state": mood_state,
            "insights": insights,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await publish_insight_delta(user_id, delta_data)

# Global instance
cross_platform_mood = CrossPlatformMoodIntelligence()
