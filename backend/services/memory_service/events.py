"""
Memory Service Event Integration
Handles NATS JetStream events for real-time memory updates
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

import nats
from nats.js import JetStreamContext

logger = logging.getLogger(__name__)

class MemoryEventHandler:
    """Handles incoming and outgoing events for Memory Service"""
    
    def __init__(self, nats_url: str = "nats://localhost:4222"):
        self.nats_url = nats_url
        self.nc = None
        self.js = None
        self.is_connected = False
        self.stats = {
            "events_processed": 0,
            "events_published": 0,
            "last_event_time": None,
            "connection_status": "disconnected"
        }
    
    async def connect(self):
        """Connect to NATS JetStream"""
        try:
            self.nc = await nats.connect(self.nats_url)
            self.js = self.nc.jetstream()
            self.is_connected = True
            self.stats["connection_status"] = "connected"
            logger.info("✅ Connected to NATS JetStream")
            
            # Ensure required streams exist
            await self._ensure_streams()
            
            # Start subscriptions
            await self._start_subscriptions()
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to NATS: {e}")
            self.is_connected = False
            self.stats["connection_status"] = "error"
            raise
    
    async def disconnect(self):
        """Disconnect from NATS"""
        if self.nc:
            await self.nc.close()
            self.is_connected = False
            self.stats["connection_status"] = "disconnected"
            logger.info("🔌 Disconnected from NATS")
    
    async def _ensure_streams(self):
        """Ensure required JetStream streams exist"""
        streams = [
            {
                "name": "MEMORY_EVENTS",
                "subjects": ["memory.interaction", "memory.pattern", "memory.insight"],
                "description": "Memory service events"
            },
            {
                "name": "USER_EVENTS", 
                "subjects": ["user.mood.updated", "user.chat.message", "user.journal.entry"],
                "description": "User activity events"
            }
        ]
        
        for stream_config in streams:
            try:
                await self.js.add_stream(
                    name=stream_config["name"],
                    subjects=stream_config["subjects"],
                    description=stream_config.get("description", "")
                )
                logger.info(f"✅ Stream {stream_config['name']} ready")
            except Exception as e:
                if "stream name already in use" in str(e).lower():
                    logger.info(f"📋 Stream {stream_config['name']} already exists")
                else:
                    logger.error(f"❌ Failed to create stream {stream_config['name']}: {e}")
    
    async def _start_subscriptions(self):
        """Start event subscriptions"""
        try:
            # Subscribe to user mood updates
            await self.js.subscribe(
                "user.mood.updated",
                cb=self._handle_mood_event,
                durable="memory-mood-consumer"
            )
            
            # Subscribe to chat messages
            await self.js.subscribe(
                "user.chat.message",
                cb=self._handle_chat_event,
                durable="memory-chat-consumer"
            )
            
            # Subscribe to journal entries
            await self.js.subscribe(
                "user.journal.entry", 
                cb=self._handle_journal_event,
                durable="memory-journal-consumer"
            )
            
            logger.info("✅ Event subscriptions started")
            
        except Exception as e:
            logger.error(f"❌ Failed to start subscriptions: {e}")
    
    async def _handle_mood_event(self, msg):
        """Handle mood update events"""
        try:
            data = json.loads(msg.data.decode())
            logger.info(f"📊 Processing mood event for user {data.get('user_id')}")
            
            # Create interaction record from mood event
            interaction = {
                "user_id": data.get("user_id"),
                "interaction_type": "mood",
                "interaction_data": {
                    "mood_score": data.get("mood_score"),
                    "emotions": data.get("emotions", {}),
                    "timestamp": data.get("timestamp")
                },
                "source_service": "mood_service",
                "metadata": {
                    "event_source": "mood_update",
                    "processed_by": "memory_service"
                }
            }
            
            # Process the interaction (would normally call database/cache)
            await self._process_interaction(interaction)
            
            # Acknowledge message
            await msg.ack()
            self._update_stats()
            
        except Exception as e:
            logger.error(f"❌ Failed to handle mood event: {e}")
            await msg.nak()
    
    async def _handle_chat_event(self, msg):
        """Handle chat message events"""
        try:
            data = json.loads(msg.data.decode())
            logger.info(f"💬 Processing chat event for user {data.get('user_id')}")
            
            # Create interaction record from chat event
            interaction = {
                "user_id": data.get("user_id"),
                "interaction_type": "chat",
                "interaction_data": {
                    "message": data.get("message"),
                    "response": data.get("response"),
                    "emotion_analysis": data.get("emotion_analysis", {}),
                    "timestamp": data.get("timestamp")
                },
                "source_service": "chatbot_service",
                "cultural_context": data.get("cultural_context"),
                "metadata": {
                    "event_source": "chat_message",
                    "processed_by": "memory_service"
                }
            }
            
            # Process the interaction
            await self._process_interaction(interaction)
            
            # Acknowledge message
            await msg.ack()
            self._update_stats()
            
        except Exception as e:
            logger.error(f"❌ Failed to handle chat event: {e}")
            await msg.nak()
    
    async def _handle_journal_event(self, msg):
        """Handle journal entry events"""
        try:
            data = json.loads(msg.data.decode())
            logger.info(f"📓 Processing journal event for user {data.get('user_id')}")
            
            # Create interaction record from journal event
            interaction = {
                "user_id": data.get("user_id"),
                "interaction_type": "journal",
                "interaction_data": {
                    "entry_content": data.get("content"),
                    "entry_type": data.get("entry_type"),
                    "sentiment": data.get("sentiment", {}),
                    "timestamp": data.get("timestamp")
                },
                "source_service": "journal_service",
                "metadata": {
                    "event_source": "journal_entry",
                    "processed_by": "memory_service"
                }
            }
            
            # Process the interaction
            await self._process_interaction(interaction)
            
            # Acknowledge message
            await msg.ack()
            self._update_stats()
            
        except Exception as e:
            logger.error(f"❌ Failed to handle journal event: {e}")
            await msg.nak()
    
    async def _process_interaction(self, interaction: Dict[str, Any]):
        """Process an interaction (would normally save to database)"""
        try:
            # For now, just log the interaction
            logger.info(f"🔄 Processing interaction: {interaction['interaction_type']} for user {interaction['user_id']}")
            
            # Here you would:
            # 1. Save to database
            # 2. Update user patterns
            # 3. Generate insights if needed
            # 4. Cache recent interactions
            
            # Simulate processing delay
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"❌ Failed to process interaction: {e}")
    
    async def publish_memory_event(self, event_type: str, data: Dict[str, Any]):
        """Publish memory-related events"""
        try:
            if not self.is_connected:
                logger.warning("⚠️ Not connected to NATS, cannot publish event")
                return False
            
            subject = f"memory.{event_type}"
            message_data = {
                "event_type": event_type,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "memory_service",
                **data
            }
            
            await self.js.publish(subject, json.dumps(message_data).encode())
            self.stats["events_published"] += 1
            logger.info(f"📤 Published event: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish event: {e}")
            return False
    
    async def publish_pattern_discovered(self, user_id: str, pattern_data: Dict[str, Any]):
        """Publish when a new pattern is discovered"""
        await self.publish_memory_event("pattern", {
            "user_id": user_id,
            "pattern_data": pattern_data
        })
    
    async def publish_insight_generated(self, user_id: str, insight_data: Dict[str, Any]):
        """Publish when a new insight is generated"""
        await self.publish_memory_event("insight", {
            "user_id": user_id,
            "insight_data": insight_data
        })
    
    async def publish_interaction_recorded(self, user_id: str, interaction_data: Dict[str, Any]):
        """Publish when an interaction is recorded"""
        await self.publish_memory_event("interaction", {
            "user_id": user_id,
            "interaction_data": interaction_data
        })
    
    def _update_stats(self):
        """Update event processing statistics"""
        self.stats["events_processed"] += 1
        self.stats["last_event_time"] = datetime.now(timezone.utc).isoformat()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event handler statistics"""
        return {
            **self.stats,
            "is_connected": self.is_connected
        }
    
    def is_running(self) -> bool:
        """Check if event handler is running"""
        return self.is_connected

# Global event handler instance
event_handler: Optional[MemoryEventHandler] = None

async def initialize_event_handler(nats_url: str = "nats://localhost:4222"):
    """Initialize the global event handler"""
    global event_handler
    
    try:
        event_handler = MemoryEventHandler(nats_url)
        await event_handler.connect()
        logger.info("✅ Memory event handler initialized")
        return event_handler
    except Exception as e:
        logger.error(f"❌ Failed to initialize event handler: {e}")
        return None

async def shutdown_event_handler():
    """Shutdown the global event handler"""
    global event_handler
    
    if event_handler:
        await event_handler.disconnect()
        event_handler = None
        logger.info("🔌 Memory event handler shutdown")

def get_event_handler() -> Optional[MemoryEventHandler]:
    """Get the global event handler instance"""
    return event_handler
