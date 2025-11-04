"""Event Publisher Service for NATS-based event publishing to ai-context-store."""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from src.models.schemas import MoodEntryResponse

logger = logging.getLogger(__name__)


class MoodEventPublisher:
    """Publish mood events to ai-context-store and ai-event-processor via NATS."""
    
    def __init__(self):
        """Initialize the event publisher."""
        self.nats_client = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize NATS connection."""
        try:
            from shared.events.enhanced_bus import get_enhanced_event_bus
            self.nats_client = get_enhanced_event_bus()
            await self.nats_client.initialize()
            self._initialized = True
            logger.info("MoodEventPublisher initialized with NATS connection")
        except Exception as e:
            logger.error(f"Failed to initialize MoodEventPublisher: {e}")
            self._initialized = False
    
    async def publish_mood_created(self, mood_entry: MoodEntryResponse):
        """Publish mood.entry.created event to NATS for ai-context-store."""
        if not self._initialized:
            logger.warning("EventPublisher not initialized, skipping event publication")
            return
        
        try:
            # Extract emotion data
            text_emotions = []
            voice_emotions = []
            
            if mood_entry.emotion_analysis:
                text_emotions = mood_entry.emotion_analysis.get("top_emotions", [])
                voice_emotions = mood_entry.emotion_analysis.get("voice_emotions", [])
            
            # Create event payload
            event_payload = {
                "event_type": "mood.entry.created",
                "user_id": mood_entry.user_id,
                "mood_entry_id": mood_entry.id,
                "input_type": mood_entry.input_type,
                "input_text": mood_entry.input_text,
                "ai_scores": {
                    "mood_score": mood_entry.mood_score,
                    "stress_level": mood_entry.stress_level or 5,
                    "energy_level": mood_entry.energy_level or 5
                },
                "text_emotions": text_emotions,
                "voice_emotions": voice_emotions,
                "combined_emotion": mood_entry.primary_emotion or "neutral",
                "combined_sentiment": mood_entry.primary_sentiment.value if mood_entry.primary_sentiment else "neutral",
                "confidence": mood_entry.combined_emotion_confidence or 0.5,
                "timestamp": mood_entry.created_at.isoformat(),
                "context_tags": mood_entry.context_tags or [],
                "location": mood_entry.location,
                "activity": mood_entry.activity
            }
            
            # Publish to multiple subjects for different consumers
            subjects = [
                "mood.events",           # General mood events
                "ai.context.mood",       # AI Context Store
                "ai.event.mood",         # AI Event Processor
                "memory.mood"            # Memory Service
            ]
            
            for subject in subjects:
                await self.nats_client.publish(subject, event_payload)
                logger.debug(f"Published mood event to {subject}")
            
            logger.info(f"Published mood.entry.created event for user {mood_entry.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish mood event: {e}")
    
    async def publish_mood_updated(self, mood_entry: MoodEntryResponse):
        """Publish mood.entry.updated event to NATS."""
        if not self._initialized:
            logger.warning("EventPublisher not initialized, skipping event publication")
            return
        
        try:
            event_payload = {
                "event_type": "mood.entry.updated",
                "user_id": mood_entry.user_id,
                "mood_entry_id": mood_entry.id,
                "input_type": mood_entry.input_type,
                "ai_scores": {
                    "mood_score": mood_entry.mood_score,
                    "stress_level": mood_entry.stress_level or 5,
                    "energy_level": mood_entry.energy_level or 5
                },
                "timestamp": mood_entry.updated_at.isoformat() if mood_entry.updated_at else datetime.utcnow().isoformat()
            }
            
            await self.nats_client.publish("mood.events", event_payload)
            await self.nats_client.publish("ai.context.mood", event_payload)
            
            logger.info(f"Published mood.entry.updated event for user {mood_entry.user_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish mood update event: {e}")
    
    async def publish_mood_deleted(self, user_id: str, mood_entry_id: str):
        """Publish mood.entry.deleted event to NATS."""
        if not self._initialized:
            logger.warning("EventPublisher not initialized, skipping event publication")
            return
        
        try:
            event_payload = {
                "event_type": "mood.entry.deleted",
                "user_id": user_id,
                "mood_entry_id": mood_entry_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.nats_client.publish("mood.events", event_payload)
            await self.nats_client.publish("ai.context.mood", event_payload)
            
            logger.info(f"Published mood.entry.deleted event for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish mood deletion event: {e}")
    
    async def publish_analytics_update(self, user_id: str, analytics_data: Dict[str, Any]):
        """Publish mood analytics update event."""
        if not self._initialized:
            logger.warning("EventPublisher not initialized, skipping event publication")
            return
        
        try:
            event_payload = {
                "event_type": "mood.analytics.updated",
                "user_id": user_id,
                "analytics_data": analytics_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.nats_client.publish("mood.analytics", event_payload)
            await self.nats_client.publish("ai.context.analytics", event_payload)
            
            logger.info(f"Published mood analytics update for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish analytics update event: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the event publisher."""
        return {
            "initialized": self._initialized,
            "nats_connected": self.nats_client is not None,
            "status": "healthy" if self._initialized else "unhealthy"
        }


# Global instance
event_publisher = MoodEventPublisher()


