"""
Mood Service Client for Chatbot Integration

Provides integration between the chatbot service and the modular mood service
for accessing user mood data and analytics.
"""

import asyncio
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MoodServiceClient:
    """Client for communicating with the modular mood service"""
    
    def __init__(self, mood_service_url: str = "http://mood-service:8003"):
        """
        Initialize the mood service client.
        
        Args:
            mood_service_url: Base URL for the mood service
        """
        self.base_url = mood_service_url.rstrip('/')
        self.http_client = None
        logger.info(f"MoodServiceClient initialized with URL: {self.base_url}")
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(timeout=30.0)
        return self.http_client
    
    async def get_user_mood_context(
        self, 
        user_id: str, 
        token: str,
        time_range_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Get mood context for a user over a specified time period.
        
        Args:
            user_id: User identifier
            token: Authorization token
            time_range_hours: Time range to analyze (default: 24 hours)
            
        Returns:
            Mood context data or None if failed
        """
        try:
            client = await self._get_http_client()
            
            # Create mood context request
            response = await client.post(
                f"{self.base_url}/api/v1/mood/context",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "time_range_hours": time_range_hours,
                    "context_summary": f"Chatbot context for {time_range_hours}h period"
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get mood context: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting mood context: {e}")
            return None
    
    async def get_recent_mood_entries(
        self, 
        user_id: str, 
        token: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent mood entries for a user.
        
        Args:
            user_id: User identifier
            token: Authorization token
            limit: Maximum number of entries to retrieve
            
        Returns:
            List of recent mood entries
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(
                f"{self.base_url}/api/v1/mood/entries",
                headers={"Authorization": f"Bearer {token}"},
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get mood entries: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting mood entries: {e}")
            return []
    
    async def get_mood_analytics(
        self, 
        user_id: str, 
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get mood analytics overview for a user.
        
        Args:
            user_id: User identifier
            token: Authorization token
            
        Returns:
            Mood analytics data or None if failed
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(
                f"{self.base_url}/api/v1/mood/analytics/overview",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get mood analytics: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting mood analytics: {e}")
            return None
    
    async def analyze_text_emotion(
        self, 
        text: str, 
        token: str,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze emotions in text using the mood service AI.
        
        Args:
            text: Text to analyze
            token: Authorization token
            user_id: Optional user identifier
            
        Returns:
            Emotion analysis results or None if failed
        """
        try:
            client = await self._get_http_client()
            
            response = await client.post(
                f"{self.base_url}/api/v1/mood/analyze",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "text": text,
                    "include_mood_entry": False
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to analyze emotion: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            return None
    
    async def create_mood_entry_for_user(
        self,
        user_id: str,
        token: str,
        mood_score: int,
        description: str = None,
        context_tags: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a mood entry for a user (used when chatbot infers mood).
        
        Args:
            user_id: User identifier
            token: Authorization token
            mood_score: Mood score (1-10)
            description: Optional description
            context_tags: Optional context tags
            
        Returns:
            Created mood entry or None if failed
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "mood_score": mood_score,
                "description": description or "Inferred from chatbot conversation",
                "activity": "chatbot_conversation"
            }
            
            if context_tags:
                payload["context_tags"] = context_tags
            
            response = await client.post(
                f"{self.base_url}/api/v1/mood/entries",
                headers={"Authorization": f"Bearer {token}"},
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to create mood entry: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating mood entry: {e}")
            return None
    
    async def get_mood_insights(
        self,
        user_id: str,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get mood patterns and insights for a user.
        
        Args:
            user_id: User identifier
            token: Authorization token
            
        Returns:
            Mood patterns and insights or None if failed
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(
                f"{self.base_url}/api/v1/mood/analytics/patterns",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get mood insights: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting mood insights: {e}")
            return None
    
    async def check_service_health(self) -> bool:
        """
        Check if the mood service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(f"{self.base_url}/api/v1/health")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error checking mood service health: {e}")
            return False
    
    async def notify_mood_event(
        self,
        user_id: str,
        token: str,
        event_type: str,
        event_data: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> bool:
        """
        Notify the mood service about mood-related events from the chatbot.
        
        Args:
            user_id: User identifier
            token: Authorization token
            event_type: Type of mood event
            event_data: Event data
            session_id: Optional session identifier
            
        Returns:
            True if notification was successful, False otherwise
        """
        try:
            # This would be used for events like:
            # - Crisis detection in conversation
            # - Mood improvement suggestions
            # - Therapeutic interventions
            
            logger.info(f"Mood event notification: {event_type} for user {user_id}")
            
            # For now, we can log the event
            # In the future, this could send events to the mood service
            # for tracking interventions and their effectiveness
            
            return True
            
        except Exception as e:
            logger.error(f"Error notifying mood event: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None


# Global mood service client instance
mood_service_client = MoodServiceClient()