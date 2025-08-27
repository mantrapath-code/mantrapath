"""
AI Context Store Client for Chatbot Service
Provides comprehensive user context aggregation and intelligence insights
"""
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """Comprehensive user context"""
    user_id: str
    mood_history: List[Dict[str, Any]]
    journal_entries: List[Dict[str, Any]]  # Add missing field
    conversation_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]  # Enhanced behavioral patterns
    context_history: List[Dict[str, Any]]  # Context history
    crisis_indicators: Dict[str, Any]
    intervention_history: List[Dict[str, Any]]
    cultural_context: Dict[str, Any]
    language_preferences: Dict[str, Any]
    recent_activities: List[Dict[str, Any]]
    ai_insights: Dict[str, Any]

@dataclass
class ConversationContext:
    """Conversation-specific context"""
    session_id: str
    recent_messages: List[Dict[str, Any]]
    sentiment_trends: List[Dict[str, Any]]
    topic_progression: List[str]
    user_engagement: Dict[str, Any]
    intent_patterns: List[Dict[str, Any]]
    response_effectiveness: Dict[str, Any]

@dataclass
class AIInsight:
    """AI-generated insight"""
    insight_type: str
    confidence: float
    description: str
    recommendation: str
    context: Dict[str, Any]
    generated_at: datetime

class AIContextStoreClient:
    """Client for communicating with AI Context Store"""
    
    def __init__(self):
        import os
        self.ai_context_store_url = os.getenv("AI_CONTEXT_STORE_URL", "http://ai-context-store:8013")
        self.timeout = int(os.getenv("AI_CONTEXT_STORE_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("AI_CONTEXT_STORE_MAX_RETRIES", "3"))
        self.cache_ttl = int(os.getenv("AI_CONTEXT_CACHE_TTL", "1800"))
        self.real_time_sync = os.getenv("AI_CONTEXT_REAL_TIME_SYNC", "true").lower() == "true"
        self.is_enabled = os.getenv("AI_CONTEXT_STORE_ENABLED", "true").lower() == "true"
        
        logger.info(f"AI Context Store Client initialized - URL: {self.ai_context_store_url}, Enabled: {self.is_enabled}")
    
    async def health_check(self) -> bool:
        """Check if AI Context Store is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ai_context_store_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"AI Context Store health check failed: {e}")
            return False
    
    async def get_user_context(self, user_id: str, jwt_token: Optional[str] = None, refresh_data: bool = False) -> Optional[UserContext]:
        """
        Get comprehensive user context from AI Context Store
        
        Args:
            user_id: User ID to get context for
            jwt_token: JWT token for authentication
            refresh_data: Whether to refresh data from all services
            
        Returns:
            UserContext object or None if failed
        """
        if not self.is_enabled:
            logger.debug("AI Context Store is disabled, returning empty context")
            return self._create_empty_user_context(user_id)
            
        logger.info(f"🔄 Requesting user context for user_id={user_id}, refresh_data={refresh_data}")
        
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
                logger.debug(f"🔑 Using JWT token: {jwt_token[:50]}...")
            else:
                logger.warning("⚠️ No JWT token provided")
            
            params = {}
            if refresh_data:
                params["refresh_data"] = "true"
            
            url = f"{self.ai_context_store_url}/api/v1/context/user/{user_id}"
            logger.info(f"📡 Making request to: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)
                
                logger.info(f"📥 Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Successfully retrieved context data: {len(str(data))} characters")
                    
                    # Debug: Log the actual data structure received
                    logger.info(f"🔍 DEBUG - Raw data keys: {list(data.keys()) if isinstance(data, dict) else 'not dict'}")
                    if isinstance(data, dict) and 'behavioral_patterns' in data:
                        logger.info(f"🔍 DEBUG - behavioral_patterns found: {data.get('behavioral_patterns', {})}")
                    if isinstance(data, dict) and 'preferences' in data:
                        logger.info(f"🔍 DEBUG - preferences found: {data.get('preferences', {})}")
                    
                    parsed_context = self._parse_user_context(user_id, data)
                    logger.info(f"📊 Parsed context - mood_history: {len(parsed_context.mood_history)}, journal_entries: {len(parsed_context.journal_entries)}")
                    return parsed_context
                else:
                    logger.error(f"❌ Get user context failed: {response.status_code} - {response.text}")
                    return self._create_empty_user_context(user_id)
                    
        except Exception as e:
            logger.error(f"💥 Error getting user context: {type(e).__name__}: {e}")
            return self._create_empty_user_context(user_id)
    
    async def get_conversation_context(self, session_id: str, jwt_token: Optional[str] = None) -> Optional[ConversationContext]:
        """
        Get conversation-specific context from AI Context Store
        
        Args:
            session_id: Session ID to get context for
            jwt_token: JWT token for authentication
            
        Returns:
            ConversationContext object or None if failed
        """
        if not self.is_enabled:
            logger.debug("AI Context Store is disabled, returning empty conversation context")
            return self._create_empty_conversation_context(session_id)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.ai_context_store_url}/api/v1/context/conversation/{session_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_conversation_context(session_id, data)
                else:
                    logger.error(f"Get conversation context failed: {response.status_code} - {response.text}")
                    return self._create_empty_conversation_context(session_id)
                    
        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return self._create_empty_conversation_context(session_id)
    
    async def get_ai_insights(self, user_id: str, context_type: str = "comprehensive", jwt_token: Optional[str] = None) -> List[AIInsight]:
        """
        Get AI insights for user from AI Context Store
        
        Args:
            user_id: User ID to get insights for
            context_type: Type of insights to retrieve
            jwt_token: JWT token for authentication
            
        Returns:
            List of AIInsight objects
        """
        if not self.is_enabled:
            logger.debug("AI Context Store is disabled, returning empty insights")
            return []
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            params = {"context_type": context_type}
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.ai_context_store_url}/api/v1/insights/user/{user_id}",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_ai_insights(data.get("insights", []))
                else:
                    logger.error(f"Get AI insights failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
            return []
    
    async def update_conversation_context(
        self, 
        session_id: str, 
        user_message: str, 
        bot_response: str,
        metadata: Dict[str, Any],
        jwt_token: Optional[str] = None
    ) -> bool:
        """
        Update conversation context in AI Context Store
        
        Args:
            session_id: Session ID to update
            user_message: User's message
            bot_response: Bot's response
            metadata: Additional metadata
            jwt_token: JWT token for authentication
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            logger.debug("AI Context Store is disabled, skipping context update")
            return True
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "session_id": session_id,
                "user_message": user_message,
                "bot_response": bot_response,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ai_context_store_url}/api/v1/context/conversation/update",
                    headers=headers,
                    json=payload
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Error updating conversation context: {e}")
            return False
    
    def _create_empty_user_context(self, user_id: str) -> UserContext:
        """Create empty user context for fallback"""
        return UserContext(
            user_id=user_id,
            mood_history=[],
            journal_entries=[],  # Add missing field
            conversation_patterns={},
            preferences={},
            behavioral_patterns={},  # Add behavioral patterns field
            context_history=[],  # Add context history field
            crisis_indicators={},
            intervention_history=[],
            cultural_context={},
            language_preferences={"primary": "en"},
            recent_activities=[],
            ai_insights={}
        )
    
    def _create_empty_conversation_context(self, session_id: str) -> ConversationContext:
        """Create empty conversation context for fallback"""
        return ConversationContext(
            session_id=session_id,
            recent_messages=[],
            sentiment_trends=[],
            topic_progression=[],
            user_engagement={},
            intent_patterns=[],
            response_effectiveness={}
        )
    
    def _parse_user_context(self, user_id: str, data: Dict[str, Any]) -> UserContext:
        """Parse user context from AI Context Store API response"""
        
        # The AI Context Store returns data directly in the format:
        # {"user_id": "...", "mood_context": {...}, "behavioral_patterns": {...}, "preferences": {...}}
        
        # Extract mood information
        mood_context = data.get("mood_context", {})
        mood_history = []
        if mood_context.get("recent_moods"):
            mood_history = [{"mood": mood, "timestamp": data.get("last_updated")} 
                          for mood in mood_context.get("recent_moods", [])]
        
        # Extract conversation patterns from journal context (if available)
        journal_context = data.get("content_context", {}) or data.get("journal_context", {})
        conversation_patterns = {
            "themes": journal_context.get("recent_themes", []),
            "sentiment": journal_context.get("sentiment", "neutral"),
            "frequency": journal_context.get("entry_frequency", "unknown")
        }
        
        # Extract activity information from community context
        community_context = data.get("community_context", {})
        recent_activities = [{
            "type": "community_engagement",
            "level": community_context.get("engagement_level", "moderate"),
            "engagement": community_context.get("social_score", 0.5),
            "interactions": community_context.get("interactions", 0)
        }]
        
        # Extract behavioral patterns and preferences from the response
        behavioral_patterns = data.get("behavioral_patterns", {})
        preferences = data.get("preferences", {})
        context_history = data.get("context_history", [])
        
        logger.info(f"📊 Parsed user context: mood_patterns={mood_context.get('mood_trend', 'stable')}, themes={journal_context.get('recent_themes', [])}")
        logger.info(f"📊 Parsed behavioral patterns: {list(behavioral_patterns.keys()) if behavioral_patterns else 'none'}")
        logger.info(f"📊 Parsed preferences: {list(preferences.keys()) if preferences else 'none'}")
        
        return UserContext(
            user_id=user_id,
            mood_history=mood_history,
            journal_entries=journal_context.get("recent_entries", []),  
            conversation_patterns=conversation_patterns,
            preferences=preferences,  # Use parsed preferences
            behavioral_patterns=behavioral_patterns,  # Add behavioral patterns
            context_history=context_history,  # Add context history
            crisis_indicators=data.get("crisis_indicators", {}),
            intervention_history=data.get("intervention_history", []),
            cultural_context=data.get("cultural_context", {}),
            language_preferences=data.get("language_preferences", {"primary": "en"}),
            recent_activities=recent_activities,
            ai_insights={
                "mood_patterns": mood_context.get("patterns", "No patterns identified"),
                "average_intensity": mood_context.get("average_intensity", 0),
                "recent_themes": journal_context.get("recent_themes", []),
                "community_engagement": community_context.get("engagement", "unknown")
            }
        )
    
    def _parse_conversation_context(self, session_id: str, data: Dict[str, Any]) -> ConversationContext:
        """Parse conversation context from API response"""
        return ConversationContext(
            session_id=session_id,
            recent_messages=data.get("recent_messages", []),
            sentiment_trends=data.get("sentiment_trends", []),
            topic_progression=data.get("topic_progression", []),
            user_engagement=data.get("user_engagement", {}),
            intent_patterns=data.get("intent_patterns", []),
            response_effectiveness=data.get("response_effectiveness", {})
        )
    
    def _parse_ai_insights(self, insights_data: List[Dict[str, Any]]) -> List[AIInsight]:
        """Parse AI insights from API response"""
        insights = []
        for insight_data in insights_data:
            try:
                insight = AIInsight(
                    insight_type=insight_data.get("type", "general"),
                    confidence=insight_data.get("confidence", 0.0),
                    description=insight_data.get("description", ""),
                    recommendation=insight_data.get("recommendation", ""),
                    context=insight_data.get("context", {}),
                    generated_at=datetime.fromisoformat(
                        insight_data.get("generated_at", datetime.utcnow().isoformat())
                    )
                )
                insights.append(insight)
            except Exception as e:
                logger.error(f"Error parsing AI insight: {e}")
                continue
        
        return insights

# Global client instance
ai_context_store_client = AIContextStoreClient()
