"""
Memory Event Handler - Processes events from other services
Handles real-time memory updates via event bus integration
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Callable
import traceback

from shared.events.enhanced_bus import get_enhanced_event_bus
from services.memory_engine import MemoryEngine

logger = logging.getLogger(__name__)

class MemoryEventHandler:
    """
    Handles events from other services to update memory records
    """
    
    def __init__(self, memory_engine: MemoryEngine):
        self.memory_engine = memory_engine
        self.event_bus = None
        self.is_running = False
        self.subscriptions = []
        
        # Statistics
        self.stats = {
            "events_processed": 0,
            "events_failed": 0,
            "last_event_time": None,
            "processing_time_avg": 0.0
        }
        
        # Event handlers mapping
        self.event_handlers = {
            "mood.entry_created": self._handle_mood_event,
            "mood.entry_updated": self._handle_mood_event,
            "journal.entry_created": self._handle_journal_event,
            "journal.entry_updated": self._handle_journal_event,
            "chat.message_sent": self._handle_chat_event,
            "community.post_created": self._handle_community_event,
            "community.comment_created": self._handle_community_event,
            "voice.command_processed": self._handle_voice_event,
            "voice.interaction_completed": self._handle_voice_event,
            "user.session_started": self._handle_session_event,
            "user.session_ended": self._handle_session_event,
            "notification.delivered": self._handle_notification_event,
            "media.uploaded": self._handle_media_event,
            "translation.completed": self._handle_translation_event
        }

    async def start(self):
        """Start the event handler"""
        try:
            logger.info("🎧 Starting Memory Event Handler...")
            
            # Get event bus instance
            self.event_bus = await get_enhanced_event_bus()
            
            # Subscribe to relevant events
            await self._setup_subscriptions()
            
            self.is_running = True
            logger.info("✅ Memory Event Handler started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Memory Event Handler: {e}")
            raise

    async def stop(self):
        """Stop the event handler"""
        try:
            logger.info("🛑 Stopping Memory Event Handler...")
            
            # Unsubscribe from events
            for subscription in self.subscriptions:
                try:
                    await subscription.unsubscribe()
                except Exception as e:
                    logger.warning(f"Failed to unsubscribe: {e}")
            
            self.subscriptions.clear()
            self.is_running = False
            
            logger.info("✅ Memory Event Handler stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop Memory Event Handler: {e}")

    def is_running_status(self) -> bool:
        """Check if event handler is running"""
        return self.is_running

    def get_stats(self) -> Dict[str, Any]:
        """Get event handler statistics"""
        return self.stats.copy()

    async def _setup_subscriptions(self):
        """Setup event subscriptions"""
        try:
            for event_type, handler in self.event_handlers.items():
                subscription = await self.event_bus.subscribe(
                    event_type,
                    self._event_wrapper(handler),
                    consumer_group="memory_service"
                )
                self.subscriptions.append(subscription)
                logger.info(f"📡 Subscribed to {event_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to setup subscriptions: {e}")
            raise

    def _event_wrapper(self, handler: Callable) -> Callable:
        """Wrap event handler with error handling and metrics"""
        async def wrapper(event_data: Dict[str, Any]):
            start_time = datetime.now(timezone.utc)
            
            try:
                await handler(event_data)
                
                # Update statistics
                self.stats["events_processed"] += 1
                self.stats["last_event_time"] = start_time.isoformat()
                
                # Update average processing time
                processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
                if self.stats["processing_time_avg"] == 0:
                    self.stats["processing_time_avg"] = processing_time
                else:
                    self.stats["processing_time_avg"] = (
                        self.stats["processing_time_avg"] * 0.9 + processing_time * 0.1
                    )
                
                logger.debug(f"✅ Processed event in {processing_time:.3f}s")
                
            except Exception as e:
                self.stats["events_failed"] += 1
                logger.error(f"❌ Event handler failed: {e}")
                logger.error(f"Event data: {event_data}")
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        return wrapper

    async def _handle_mood_event(self, event_data: Dict[str, Any]):
        """Handle mood-related events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Mood event missing user_id")
                return
            
            # Extract mood data
            mood_data = {
                "mood_score": event_data.get("mood_score"),
                "mood_label": event_data.get("mood_label"),
                "energy_level": event_data.get("energy_level"),
                "stress_level": event_data.get("stress_level"),
                "notes": event_data.get("notes"),
                "tags": event_data.get("tags", []),
                "location": event_data.get("location"),
                "weather": event_data.get("weather"),
                "event_id": event_data.get("id"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Extract cultural context if available
            cultural_context = {
                "language": event_data.get("language"),
                "cultural_background": event_data.get("cultural_background"),
                "timezone": event_data.get("timezone"),
                "cultural_preferences": event_data.get("cultural_preferences")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="mood",
                interaction_data=mood_data,
                source_service="mood_service",
                session_id=event_data.get("session_id"),
                cultural_context=cultural_context,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded mood interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle mood event: {e}")
            raise

    async def _handle_journal_event(self, event_data: Dict[str, Any]):
        """Handle journal-related events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Journal event missing user_id")
                return
            
            # Extract journal data
            journal_data = {
                "content": event_data.get("content"),
                "title": event_data.get("title"),
                "mood_before": event_data.get("mood_before"),
                "mood_after": event_data.get("mood_after"),
                "tags": event_data.get("tags", []),
                "word_count": len(event_data.get("content", "").split()),
                "sentiment_score": event_data.get("sentiment_score"),
                "emotion_analysis": event_data.get("emotion_analysis"),
                "event_id": event_data.get("id"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Extract cultural context
            cultural_context = {
                "language": event_data.get("language"),
                "cultural_background": event_data.get("cultural_background"),
                "writing_style": event_data.get("writing_style")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="journal",
                interaction_data=journal_data,
                source_service="content_service",
                session_id=event_data.get("session_id"),
                cultural_context=cultural_context,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded journal interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle journal event: {e}")
            raise

    async def _handle_chat_event(self, event_data: Dict[str, Any]):
        """Handle chat/chatbot-related events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Chat event missing user_id")
                return
            
            # Extract chat data
            chat_data = {
                "message": event_data.get("message"),
                "response": event_data.get("response"),
                "conversation_id": event_data.get("conversation_id"),
                "message_type": event_data.get("message_type"),
                "intent": event_data.get("intent"),
                "confidence": event_data.get("confidence"),
                "sentiment": event_data.get("sentiment"),
                "emotion_detected": event_data.get("emotion_detected"),
                "crisis_level": event_data.get("crisis_level"),
                "response_time_ms": event_data.get("response_time_ms"),
                "event_id": event_data.get("id"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Extract cultural context
            cultural_context = {
                "language": event_data.get("language"),
                "cultural_adaptation": event_data.get("cultural_adaptation"),
                "communication_style": event_data.get("communication_style")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="chat",
                interaction_data=chat_data,
                source_service="chatbot_service",
                session_id=event_data.get("session_id"),
                cultural_context=cultural_context,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded chat interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle chat event: {e}")
            raise

    async def _handle_community_event(self, event_data: Dict[str, Any]):
        """Handle community-related events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Community event missing user_id")
                return
            
            # Extract community data
            community_data = {
                "content": event_data.get("content"),
                "post_type": event_data.get("post_type"),
                "community_id": event_data.get("community_id"),
                "parent_post_id": event_data.get("parent_post_id"),
                "engagement_metrics": event_data.get("engagement_metrics"),
                "visibility": event_data.get("visibility"),
                "tags": event_data.get("tags", []),
                "mood_context": event_data.get("mood_context"),
                "event_id": event_data.get("id"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Extract cultural context
            cultural_context = {
                "language": event_data.get("language"),
                "cultural_community": event_data.get("cultural_community"),
                "community_guidelines": event_data.get("community_guidelines")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="community",
                interaction_data=community_data,
                source_service="community_service",
                session_id=event_data.get("session_id"),
                cultural_context=cultural_context,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded community interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle community event: {e}")
            raise

    async def _handle_voice_event(self, event_data: Dict[str, Any]):
        """Handle voice-related events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Voice event missing user_id")
                return
            
            # Extract voice data
            voice_data = {
                "command": event_data.get("command"),
                "transcript": event_data.get("transcript"),
                "confidence": event_data.get("confidence"),
                "language": event_data.get("language"),
                "emotion_tone": event_data.get("emotion_tone"),
                "speech_rate": event_data.get("speech_rate"),
                "volume_level": event_data.get("volume_level"),
                "processing_time_ms": event_data.get("processing_time_ms"),
                "success": event_data.get("success"),
                "event_id": event_data.get("id"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Extract cultural context
            cultural_context = {
                "language": event_data.get("language"),
                "accent": event_data.get("accent"),
                "cultural_speech_patterns": event_data.get("cultural_speech_patterns")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="voice",
                interaction_data=voice_data,
                source_service="voice_service",
                session_id=event_data.get("session_id"),
                cultural_context=cultural_context,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded voice interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle voice event: {e}")
            raise

    async def _handle_session_event(self, event_data: Dict[str, Any]):
        """Handle user session events"""
        try:
            user_id = event_data.get("user_id")
            session_id = event_data.get("session_id")
            
            if not user_id or not session_id:
                logger.warning("Session event missing user_id or session_id")
                return
            
            # Extract session data
            session_data = {
                "event_type": event_data.get("event_type"),
                "session_duration": event_data.get("session_duration"),
                "device_info": event_data.get("device_info"),
                "platform": event_data.get("platform"),
                "user_agent": event_data.get("user_agent"),
                "location": event_data.get("location"),
                "activities": event_data.get("activities", []),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="session",
                interaction_data=session_data,
                source_service="auth_service",
                session_id=session_id,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded session interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle session event: {e}")
            raise

    async def _handle_notification_event(self, event_data: Dict[str, Any]):
        """Handle notification events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Notification event missing user_id")
                return
            
            # Extract notification data
            notification_data = {
                "notification_type": event_data.get("notification_type"),
                "title": event_data.get("title"),
                "message": event_data.get("message"),
                "channel": event_data.get("channel"),
                "delivery_status": event_data.get("delivery_status"),
                "opened": event_data.get("opened"),
                "interaction_type": event_data.get("interaction_type"),
                "priority": event_data.get("priority"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Extract cultural context
            cultural_context = {
                "language": event_data.get("language"),
                "cultural_preferences": event_data.get("cultural_preferences")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="notification",
                interaction_data=notification_data,
                source_service="notification_service",
                session_id=event_data.get("session_id"),
                cultural_context=cultural_context,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded notification interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle notification event: {e}")
            raise

    async def _handle_media_event(self, event_data: Dict[str, Any]):
        """Handle media upload/interaction events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Media event missing user_id")
                return
            
            # Extract media data
            media_data = {
                "media_type": event_data.get("media_type"),
                "file_size": event_data.get("file_size"),
                "duration": event_data.get("duration"),
                "format": event_data.get("format"),
                "context": event_data.get("context"),
                "tags": event_data.get("tags", []),
                "processing_status": event_data.get("processing_status"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="media",
                interaction_data=media_data,
                source_service="media_service",
                session_id=event_data.get("session_id"),
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded media interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle media event: {e}")
            raise

    async def _handle_translation_event(self, event_data: Dict[str, Any]):
        """Handle translation service events"""
        try:
            user_id = event_data.get("user_id")
            if not user_id:
                logger.warning("Translation event missing user_id")
                return
            
            # Extract translation data
            translation_data = {
                "source_language": event_data.get("source_language"),
                "target_language": event_data.get("target_language"),
                "source_text": event_data.get("source_text"),
                "translated_text": event_data.get("translated_text"),
                "confidence": event_data.get("confidence"),
                "context": event_data.get("context"),
                "cultural_adaptation": event_data.get("cultural_adaptation"),
                "processing_time_ms": event_data.get("processing_time_ms"),
                "event_timestamp": event_data.get("timestamp")
            }
            
            # Extract cultural context
            cultural_context = {
                "source_language": event_data.get("source_language"),
                "target_language": event_data.get("target_language"),
                "cultural_adaptation": event_data.get("cultural_adaptation")
            }
            
            # Record interaction
            await self.memory_engine.record_interaction(
                user_id=user_id,
                interaction_type="translation",
                interaction_data=translation_data,
                source_service="translation_service",
                session_id=event_data.get("session_id"),
                cultural_context=cultural_context,
                metadata={
                    "event_type": event_data.get("event_type"),
                    "original_event": event_data
                }
            )
            
            logger.debug(f"📝 Recorded translation interaction for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to handle translation event: {e}")
            raise

    async def publish_memory_event(
        self, 
        event_type: str, 
        user_id: str, 
        data: Dict[str, Any]
    ):
        """Publish memory-related events"""
        try:
            if not self.event_bus or not self.is_running:
                logger.warning("Event bus not available for publishing")
                return
            
            event_data = {
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source_service": "memory_service",
                **data
            }
            
            await self.event_bus.publish(event_type, event_data)
            logger.debug(f"📡 Published {event_type} event for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to publish memory event: {e}")
