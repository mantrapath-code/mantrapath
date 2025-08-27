"""
AI Event Processor Client for Chatbot Service
Handles communication with AI Event Processor for event-driven processing and notifications
"""
import os
import asyncio
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

@dataclass
class ChatEvent:
    """Chat event for AI Event Processor"""
    event_type: str  # chat_start, chat_message, chat_end, crisis_detected, etc.
    user_id: str
    session_id: str
    data: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1-5, 5 being highest

@dataclass
class ProcessedEvent:
    """Processed event result from AI Event Processor"""
    event_id: str
    processed_at: datetime
    actions_triggered: List[str]
    notifications_sent: List[str]
    metadata: Dict[str, Any]

class AIEventProcessorClient:
    """Client for communicating with AI Event Processor"""
    
    def __init__(self):
        """Initialize AI Event Processor client"""
        self.event_processor_url = os.getenv("AI_EVENT_PROCESSOR_URL", "http://ai-event-processor:8014")
        self.timeout = int(os.getenv("AI_EVENT_PROCESSOR_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("AI_EVENT_PROCESSOR_MAX_RETRIES", "3"))
        
        # Feature flags
        self.is_enabled = os.getenv("AI_EVENT_PROCESSOR_ENABLED", "true").lower() == "true"
        
        logger.info(f"AI Event Processor Client initialized - URL: {self.event_processor_url}, Enabled: {self.is_enabled}")
    
    async def check_health(self) -> bool:
        """Check if AI Event Processor is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.event_processor_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"AI Event Processor health check failed: {e}")
            return False
    
    # Alias for compatibility
    async def health_check(self) -> bool:
        """Alias for check_health for compatibility"""
        return await self.check_health()
    
    async def publish_chat_event(
        self, 
        event: ChatEvent,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Publish chat event to AI Event Processor"""
        if not self.is_enabled:
            logger.debug("AI Event Processor is disabled, skipping event publishing")
            return True
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"{self.event_processor_url}/api/v1/events/publish",
                            headers=headers,
                            json={
                                "event_type": event.event_type,
                                "user_id": event.user_id,
                                "session_id": event.session_id,
                                "data": event.data,
                                "timestamp": event.timestamp.isoformat(),
                                "priority": event.priority
                            }
                        )
                        
                        if response.status_code == 200:
                            logger.debug(f"Event published successfully: {event.event_type}")
                            return True
                        else:
                            logger.warning(f"AI Event Processor returned status {response.status_code}")
                            return False
                            
                except httpx.TimeoutException:
                    logger.warning(f"AI Event Processor timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return False
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error publishing chat event: {e}")
            return False
    
    async def publish_chat_start_event(
        self,
        user_id: str,
        session_id: str,
        user_context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Publish chat start event"""
        event = ChatEvent(
            event_type="chat_start",
            user_id=user_id,
            session_id=session_id,
            data={
                "user_context": user_context or {},
                "platform": "chatbot_service"
            },
            timestamp=datetime.now(),
            priority=2
        )
        return await self.publish_chat_event(event, jwt_token)
    
    async def publish_chat_message_event(
        self,
        user_id: str,
        session_id: str,
        message: str,
        response: str,
        sentiment: Optional[str] = None,
        emotion: Optional[str] = None,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Publish chat message event"""
        event = ChatEvent(
            event_type="chat_message",
            user_id=user_id,
            session_id=session_id,
            data={
                "user_message": message,
                "bot_response": response,
                "sentiment": sentiment,
                "emotion": emotion,
                "platform": "chatbot_service"
            },
            timestamp=datetime.now(),
            priority=1
        )
        return await self.publish_chat_event(event, jwt_token)
    
    async def publish_crisis_detected_event(
        self,
        user_id: str,
        session_id: str,
        crisis_indicators: List[str],
        risk_level: str,
        immediate_action_required: bool = False,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Publish crisis detected event"""
        event = ChatEvent(
            event_type="crisis_detected",
            user_id=user_id,
            session_id=session_id,
            data={
                "crisis_indicators": crisis_indicators,
                "risk_level": risk_level,
                "immediate_action_required": immediate_action_required,
                "platform": "chatbot_service"
            },
            timestamp=datetime.now(),
            priority=5  # Highest priority
        )
        return await self.publish_chat_event(event, jwt_token)
    
    async def publish_mood_change_event(
        self,
        user_id: str,
        session_id: str,
        previous_mood: Optional[str],
        current_mood: str,
        mood_trend: str,
        jwt_token: Optional[str] = None
    ) -> bool:
        """Publish mood change event"""
        event = ChatEvent(
            event_type="mood_change",
            user_id=user_id,
            session_id=session_id,
            data={
                "previous_mood": previous_mood,
                "current_mood": current_mood,
                "mood_trend": mood_trend,
                "platform": "chatbot_service"
            },
            timestamp=datetime.now(),
            priority=3
        )
        return await self.publish_chat_event(event, jwt_token)
    
    async def get_event_status(
        self,
        event_id: str,
        jwt_token: Optional[str] = None
    ) -> Optional[ProcessedEvent]:
        """Get status of a processed event"""
        if not self.is_enabled:
            logger.debug("AI Event Processor is disabled, returning None")
            return None
            
        try:
            headers = {}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.get(
                            f"{self.event_processor_url}/api/v1/events/{event_id}/status",
                            headers=headers
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            processed_event = ProcessedEvent(
                                event_id=data.get("event_id"),
                                processed_at=datetime.fromisoformat(data.get("processed_at")),
                                actions_triggered=data.get("actions_triggered", []),
                                notifications_sent=data.get("notifications_sent", []),
                                metadata=data.get("metadata", {})
                            )
                            
                            logger.debug(f"Event status retrieved for {event_id}")
                            return processed_event
                        else:
                            logger.warning(f"AI Event Processor returned status {response.status_code}")
                            return None
                            
                except httpx.TimeoutException:
                    logger.warning(f"AI Event Processor timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        return None
                    await asyncio.sleep(1 * (attempt + 1))
                    
        except Exception as e:
            logger.error(f"Error getting event status: {e}")
            return None

# Global instance
ai_event_processor_client = AIEventProcessorClient()
