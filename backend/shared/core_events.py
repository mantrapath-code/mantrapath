"""
EventBus abstraction for real-time streaming pipeline.
Provides in-memory implementation with optional Kafka upgrade path.

Usage:
    from shared.events import get_event_bus
    
    bus = get_event_bus()
    await bus.publish("mood_entry_created", {"user_id": "123", "mood": 7})
    
    @bus.subscribe("mood_entry_created")
    async def handle_mood_update(event_data):
        print(f"New mood entry: {event_data}")
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
from shared.feature_flags import get_flag_bool

logger = logging.getLogger(__name__)

@dataclass
class Event:
    """Event data structure"""
    channel: str
    data: Dict[str, Any]
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    event_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.event_id is None:
            import uuid
            self.event_id = str(uuid.uuid4())

class EventBus(ABC):
    """Abstract EventBus interface"""
    
    @abstractmethod
    async def publish(self, channel: str, data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Publish an event to a channel"""
        pass
    
    @abstractmethod
    async def subscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
        """Subscribe to events on a channel"""
        pass
    
    @abstractmethod
    async def unsubscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
        """Unsubscribe from events on a channel"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the event bus and cleanup resources"""
        pass

class InMemoryEventBus(EventBus):
    """In-memory implementation using asyncio.Queue"""
    
    def __init__(self):
        self.channels: Dict[str, List[Callable[[Event], Any]]] = {}
        self.queues: Dict[str, asyncio.Queue[Event]] = {}
        self.tasks: Dict[str, asyncio.Task[None]] = {}
        self.running = True
        logger.info("🚀 InMemoryEventBus initialized")
    
    async def publish(self, channel: str, data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Publish an event to a channel"""
        try:
            event = Event(channel=channel, data=data, user_id=user_id)
            
            # Ensure channel queue exists
            if channel not in self.queues:
                self.queues[channel] = asyncio.Queue[Event]()
                self.channels[channel] = []
                # Start worker for this channel
                task = asyncio.create_task(self._channel_worker(channel))
                self.tasks[channel] = task
            
            # Put event in queue
            await self.queues[channel].put(event)
            logger.debug(f"📤 Published event to {channel}: {data}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to publish event to {channel}: {e}")
            return False
    
    async def subscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
        """Subscribe to events on a channel"""
        if channel not in self.channels:
            self.channels[channel] = []
            self.queues[channel] = asyncio.Queue[Event]()
            # Start worker for this channel
            task = asyncio.create_task(self._channel_worker(channel))
            self.tasks[channel] = task
        
        self.channels[channel].append(handler)
        logger.info(f"🔔 Subscribed to channel: {channel}")
    
    async def unsubscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
        """Unsubscribe from events on a channel"""
        if channel in self.channels and handler in self.channels[channel]:
            self.channels[channel].remove(handler)
            logger.info(f"🔕 Unsubscribed from channel: {channel}")
    
    async def _channel_worker(self, channel: str):
        """Worker to process events for a specific channel"""
        logger.info(f"🔄 Starting worker for channel: {channel}")
        
        while self.running:
            try:
                # Wait for events with timeout to allow graceful shutdown
                event = await asyncio.wait_for(self.queues[channel].get(), timeout=1.0)
                
                # Process event with all handlers for this channel
                handlers = self.channels.get(channel, [])
                for handler in handlers:
                    try:
                        # Call handler (support both sync and async)
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"❌ Error in event handler for {channel}: {e}")
                
                # Mark task as done
                self.queues[channel].task_done()
                
            except asyncio.TimeoutError:
                # Normal timeout, continue loop
                continue
            except Exception as e:
                logger.error(f"❌ Error in channel worker for {channel}: {e}")
                break
        
        logger.info(f"🛑 Channel worker stopped for: {channel}")
    
    async def close(self) -> None:
        """Close the event bus and cleanup resources"""
        logger.info("🛑 Closing InMemoryEventBus...")
        self.running = False
        
        # Cancel all worker tasks
        for task in self.tasks.values():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Clear all data structures
        self.channels.clear()
        self.queues.clear()
        self.tasks.clear()
        
        logger.info("✅ InMemoryEventBus closed")

class KafkaEventBus(EventBus):
    """Kafka implementation (placeholder for future use)"""
    
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        logger.warning("⚠️  KafkaEventBus is not implemented yet. Using InMemoryEventBus fallback.")
        # For now, fallback to in-memory
        self._fallback = InMemoryEventBus()
    
    async def publish(self, channel: str, data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        return await self._fallback.publish(channel, data, user_id)
    
    async def subscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
        await self._fallback.subscribe(channel, handler)
    
    async def unsubscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
        await self._fallback.unsubscribe(channel, handler)
    
    async def close(self) -> None:
        await self._fallback.close()

# Global event bus instance
_global_event_bus: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    global _global_event_bus
    
    if _global_event_bus is None:
        if get_flag_bool('USE_EVENT_BUS_KAFKA'):
            kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
            _global_event_bus = KafkaEventBus(kafka_servers)
        else:
            _global_event_bus = InMemoryEventBus()
    
    return _global_event_bus

async def cleanup_event_bus():
    """Cleanup the global event bus (call on app shutdown)"""
    global _global_event_bus
    if _global_event_bus:
        await _global_event_bus.close()
        _global_event_bus = None

# Common event channels
class EventChannels:
    """Standard event channel names"""
    MOOD_ENTRY_CREATED = "mood_entry_created"
    JOURNAL_ENTRY_CREATED = "journal_entry_created"
    CHALLENGE_PROGRESS_UPDATED = "challenge_progress_updated"
    COMMUNITY_POST_CREATED = "community_post_created"
    INSIGHT_DELTA = "insight_delta"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"

# Helper functions for common event publishing
async def publish_mood_entry_created(user_id: str, mood_entry_data: Dict[str, Any]) -> bool:
    """Publish mood entry created event"""
    bus = get_event_bus()
    return await bus.publish(EventChannels.MOOD_ENTRY_CREATED, mood_entry_data, user_id)

async def publish_journal_entry_created(user_id: str, journal_entry_data: Dict[str, Any]) -> bool:
    """Publish journal entry created event"""
    bus = get_event_bus()
    return await bus.publish(EventChannels.JOURNAL_ENTRY_CREATED, journal_entry_data, user_id)

async def publish_challenge_progress_updated(user_id: str, challenge_data: Dict[str, Any]) -> bool:
    """Publish challenge progress updated event"""
    bus = get_event_bus()
    return await bus.publish(EventChannels.CHALLENGE_PROGRESS_UPDATED, challenge_data, user_id)

async def publish_community_post_created(user_id: str, post_data: Dict[str, Any]) -> bool:
    """Publish community post created event"""
    bus = get_event_bus()
    return await bus.publish(EventChannels.COMMUNITY_POST_CREATED, post_data, user_id)

async def publish_insight_delta(user_id: str, delta_data: Dict[str, Any]) -> bool:
    """Publish insight delta event"""
    bus = get_event_bus()
    return await bus.publish(EventChannels.INSIGHT_DELTA, delta_data, user_id)
