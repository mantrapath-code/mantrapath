"""
Event Processor Service
Processes events from all services and updates user context accordingly
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from datetime import datetime, timezone

import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
service_root = os.path.dirname(current_dir)
backend_root = os.path.dirname(os.path.dirname(service_root))

sys.path.insert(0, backend_root)
sys.path.insert(0, service_root)

from shared.events.enhanced_bus import get_enhanced_event_bus, Event
from models.context_models import ContextEntry, ContextType, ContextPriority, ContextUpdate

if TYPE_CHECKING:
    from services.context_aggregator import ContextAggregatorService
    from services.intelligence_engine import IntelligenceEngine

logger = logging.getLogger(__name__)

class EventProcessor:
    """
    Processes events from all services and updates user context
    """
    
    def __init__(self, context_aggregator: "ContextAggregatorService", intelligence_engine: "IntelligenceEngine"):
        self.context_aggregator = context_aggregator
        self.intelligence_engine = intelligence_engine
        self.event_bus = get_enhanced_event_bus()
        self.is_running = False
        
        # Event processing statistics
        self.processed_events = 0
        self.failed_events = 0
        self.events_by_type: Dict[str, int] = {}
        
        logger.info("🔄 EventProcessor initialized")
    
    async def start_subscriptions(self):
        """Start subscribing to all relevant events"""
        self.is_running = True
        logger.info("🚀 Starting event subscriptions...")
        
        try:
            # Subscribe to all events from the 7 active services
            await self._subscribe_to_mood_events()
            await self._subscribe_to_community_events()
            await self._subscribe_to_ml_events()
            await self._subscribe_to_translation_events()
            await self._subscribe_to_voice_events()
            await self._subscribe_to_notification_events()
            await self._subscribe_to_content_events()
            
            logger.info("✅ All event subscriptions started successfully")
            
        except Exception as e:
            logger.error(f"❌ Error starting event subscriptions: {e}")
            raise
    
    async def stop_subscriptions(self):
        """Stop all event subscriptions"""
        self.is_running = False
        logger.info("🛑 Stopping event subscriptions")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get event processing metrics"""
        return {
            "processed_events": self.processed_events,
            "failed_events": self.failed_events,
            "success_rate": (
                self.processed_events / (self.processed_events + self.failed_events)
                if (self.processed_events + self.failed_events) > 0 else 0
            ),
            "events_by_type": self.events_by_type,
            "is_running": self.is_running
        }
    
    # Event subscription methods
    
    async def _subscribe_to_mood_events(self):
        """Subscribe to mood service events"""
        try:
            await self.event_bus.subscribe("mood.entry.created", self._handle_mood_entry_created)
            await self.event_bus.subscribe("journal.entry.created", self._handle_journal_entry_created)
            logger.info("✅ Subscribed to mood service events")
        except Exception as e:
            logger.error(f"❌ Error subscribing to mood events: {e}")
    
    async def _subscribe_to_community_events(self):
        """Subscribe to community service events"""
        try:
            await self.event_bus.subscribe("community.challenge.progress.updated", self._handle_challenge_progress)
            await self.event_bus.subscribe("community.post.created", self._handle_community_post_created)
            logger.info("✅ Subscribed to community service events")
        except Exception as e:
            logger.error(f"❌ Error subscribing to community events: {e}")
    
    async def _subscribe_to_ml_events(self):
        """Subscribe to ML service events"""
        try:
            await self.event_bus.subscribe("ml.insight.delta", self._handle_ml_insight_delta)
            logger.info("✅ Subscribed to ML service events")
        except Exception as e:
            logger.error(f"❌ Error subscribing to ML events: {e}")
    
    async def _subscribe_to_translation_events(self):
        """Subscribe to translation service events"""
        try:
            await self.event_bus.subscribe("translation.completed", self._handle_translation_completed)
            logger.info("✅ Subscribed to translation service events")
        except Exception as e:
            logger.error(f"❌ Error subscribing to translation events: {e}")
    
    async def _subscribe_to_voice_events(self):
        """Subscribe to voice service events"""
        try:
            await self.event_bus.subscribe("voice.activity_detected", self._handle_voice_activity_detected)
            await self.event_bus.subscribe("voice.intent_classified", self._handle_voice_intent_classified)
            logger.info("✅ Subscribed to voice service events")
        except Exception as e:
            logger.error(f"❌ Error subscribing to voice events: {e}")
    
    async def _subscribe_to_notification_events(self):
        """Subscribe to notification service events"""
        try:
            await self.event_bus.subscribe("notification.sent", self._handle_notification_sent)
            await self.event_bus.subscribe("notification.delivered", self._handle_notification_delivered)
            logger.info("✅ Subscribed to notification service events")
        except Exception as e:
            logger.error(f"❌ Error subscribing to notification events: {e}")
    
    async def _subscribe_to_content_events(self):
        """Subscribe to content service events"""
        try:
            await self.event_bus.subscribe("content.recommendation.created", self._handle_content_recommendation_created)
            logger.info("✅ Subscribed to content service events")
        except Exception as e:
            logger.error(f"❌ Error subscribing to content events: {e}")
    
    # Event handler methods
    
    async def _handle_mood_entry_created(self, event: Event):
        """Handle mood entry created event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "mood_score": event.data.get("mood_score", 5.0),
                "energy_level": event.data.get("energy_level", 5.0),
                "stress_level": event.data.get("stress_level"),
                "sleep_quality": event.data.get("sleep_quality"),
                "notes": event.data.get("notes", "")
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.MOOD,
                "mood_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"📊 Processed mood entry event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling mood entry event: {e}")
    
    async def _handle_journal_entry_created(self, event: Event):
        """Handle journal entry created event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "sentiment_score": event.data.get("sentiment_score"),
                "content_length": len(event.data.get("content", "")),
                "tags": event.data.get("tags", []),
                "journal_type": event.data.get("type", "general")
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.MOOD,
                "mood_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"📝 Processed journal entry event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling journal entry event: {e}")
    
    async def _handle_challenge_progress(self, event: Event):
        """Handle challenge progress update event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "challenge_id": event.data.get("challenge_id"),
                "progress": event.data.get("progress", 0),
                "completed": event.data.get("completed", False),
                "engagement_level": event.data.get("engagement_level", "moderate"),
                "challenges": [event.data.get("challenge_id")] if event.data.get("challenge_id") else []
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.COMMUNITY,
                "community_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"🏆 Processed challenge progress event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling challenge progress event: {e}")
    
    async def _handle_community_post_created(self, event: Event):
        """Handle community post created event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "post_type": event.data.get("type", "general"),
                "topics": event.data.get("tags", []),
                "engagement_level": "active",
                "posts_increment": 1,
                "interactions_increment": 0
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.COMMUNITY,
                "community_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"💬 Processed community post event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling community post event: {e}")
    
    async def _handle_ml_insight_delta(self, event: Event):
        """Handle ML insight delta event"""
        try:
            if not event.user_id:
                return
            
            # Trigger intelligence processing for this user
            await self.intelligence_engine.process_ml_insight(event.user_id, event.data)
            
            logger.debug(f"🧠 Processed ML insight delta for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling ML insight delta event: {e}")
    
    async def _handle_translation_completed(self, event: Event):
        """Handle translation completed event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "source_languages": [event.data.get("source_language", "")],
                "target_languages": [event.data.get("target_language", "")],
                "content_types": [event.data.get("content_type", "text")],
                "cultural_preferences": event.data.get("cultural_context", {})
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.TRANSLATION,
                "translation_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"🌍 Processed translation event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling translation event: {e}")
    
    async def _handle_voice_activity_detected(self, event: Event):
        """Handle voice activity detected event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "commands": [event.data.get("command", "")],
                "speech_patterns": event.data.get("speech_analysis", {}),
                "sentiment": event.data.get("sentiment_score")
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.VOICE,
                "voice_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"🎤 Processed voice activity event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling voice activity event: {e}")
    
    async def _handle_voice_intent_classified(self, event: Event):
        """Handle voice intent classified event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "intents": [event.data.get("intent", "")],
                "confidence": event.data.get("confidence", 0.0),
                "commands": [event.data.get("command", "")]
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.VOICE,
                "voice_service",
                event.channel,
                context_data,
                ContextPriority.HIGH  # Intent classification is important
            )
            
            logger.debug(f"🎯 Processed voice intent event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling voice intent event: {e}")
    
    async def _handle_notification_sent(self, event: Event):
        """Handle notification sent event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "types": [event.data.get("type", "general")],
                "delivery_preferences": {
                    "channel": event.data.get("channel", "push"),
                    "timing": event.data.get("sent_at")
                },
                "response_patterns": {}
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.NOTIFICATION,
                "notification_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"📧 Processed notification sent event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling notification sent event: {e}")
    
    async def _handle_notification_delivered(self, event: Event):
        """Handle notification delivered event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "engagement_rates": {
                    event.data.get("type", "general"): 
                    1.0 if event.data.get("opened", False) else 0.0
                },
                "response_patterns": {
                    "delivery_time": event.data.get("delivered_at"),
                    "opened": event.data.get("opened", False),
                    "response_time": event.data.get("response_time")
                },
                "optimal_timing": [event.data.get("delivered_at")] if event.data.get("opened") else []
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.NOTIFICATION,
                "notification_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"📬 Processed notification delivered event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling notification delivered event: {e}")
    
    async def _handle_content_recommendation_created(self, event: Event):
        """Handle content recommendation created event"""
        try:
            if not event.user_id:
                return
            
            context_data = {
                "preferences": event.data.get("categories", []),
                "content_types": [event.data.get("content_type", "article")],
                "engagement_patterns": {
                    "recommendation_reason": event.data.get("reason", ""),
                    "score": event.data.get("relevance_score", 0.0)
                },
                "feedback": []
            }
            
            await self._process_context_update(
                event.user_id,
                ContextType.CONTENT,
                "content_service",
                event.channel,
                context_data,
                ContextPriority.NORMAL
            )
            
            logger.debug(f"📚 Processed content recommendation event for user {event.user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error handling content recommendation event: {e}")
    
    # Helper methods
    
    async def _process_context_update(
        self,
        user_id: str,
        context_type: ContextType,
        source_service: str,
        event_channel: str,
        context_data: Dict[str, Any],
        priority: ContextPriority
    ):
        """Process a context update"""
        try:
            # Create context entry
            context_entry = ContextEntry(
                user_id=user_id,
                context_type=context_type,
                source_service=source_service,
                event_channel=event_channel,
                raw_data=context_data,
                processed_data=context_data,
                priority=priority,
                timestamp=datetime.now(timezone.utc),
                metadata={"processor": "event_processor"}
            )
            
            # Add to context aggregator
            success = await self.context_aggregator.add_context_entry(context_entry)
            
            if success:
                self.processed_events += 1
                self.events_by_type[context_type.value] = self.events_by_type.get(context_type.value, 0) + 1
                
                # Trigger intelligence processing if high priority
                if priority in [ContextPriority.HIGH, ContextPriority.CRITICAL]:
                    await self.intelligence_engine.process_high_priority_update(user_id, context_entry)
            else:
                self.failed_events += 1
                logger.warning(f"⚠️ Failed to process context update for user {user_id}")
            
        except Exception as e:
            self.failed_events += 1
            logger.error(f"❌ Error processing context update: {e}")
            raise
