# Story V3-BK-014: Memory Service Event Integration
**Epic**: Memory Service Foundation  
**Priority**: P0 | **Points**: 5 | **Assignee**: Mid Dev 1

## Story Description
Integrate Memory Service with event-driven architecture to enable real-time memory updates and cross-service communication through NATS Event Bus.

## Current State Analysis
**Available Foundation**:
- ✅ NATS JetStream (operational)
- ✅ Event bus patterns established (from existing services)
- ✅ Memory Service core implementation (V3-BK-013)
- ✅ Existing event publishers (mood, chatbot, community services)

**Missing Components**:
- ❌ Memory Service event subscribers
- ❌ Memory Service event publishers  
- ❌ Event schema definitions for memory
- ❌ Event-driven memory synchronization

## Acceptance Criteria

### AC1: Subscribe to Mood, Journal, Chat, and Community Events
- [ ] Subscribe to `mood.entry_created` events from Mood Service
- [ ] Subscribe to `journal.entry_created` events from Journal Service
- [ ] Subscribe to `chat.message_sent` events from Chatbot Service
- [ ] Subscribe to `community.post_created` events from Community Service
- [ ] Subscribe to `challenge.progress_updated` events from Challenge system
- [ ] Event validation and error handling for malformed events
- [ ] Dead letter queue handling for failed event processing

### AC2: Publish Memory Events for Other Services
- [ ] Publish `memory.interaction_recorded` when new interactions are stored
- [ ] Publish `memory.pattern_updated` when mood patterns are analyzed
- [ ] Publish `memory.insight_generated` when behavioral insights are created
- [ ] Event schema validation before publishing
- [ ] Event metadata inclusion (timestamps, correlation IDs, source tracking)

### AC3: Real-Time Memory Updates via Event Bus
- [ ] Immediate memory storage upon receiving interaction events
- [ ] Real-time pattern analysis triggers from memory events
- [ ] Cross-service memory state synchronization
- [ ] Event ordering and duplicate handling
- [ ] Graceful handling of event bus downtime

### AC4: Event-Driven Memory Synchronization
- [ ] Memory consistency across service restarts
- [ ] Event replay capability for data recovery
- [ ] Conflict resolution for concurrent updates
- [ ] Event versioning and backward compatibility
- [ ] Monitoring and alerting for event processing failures

## Detailed Implementation Plan

### Task 1: Event Schema Design (1h)

#### 1.1: Memory Event Schemas
```python
# File: backend/services/memory_service/src/models/events.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class InteractionType(str, Enum):
    MOOD = "mood"
    JOURNAL = "journal" 
    CHAT = "chat"
    COMMUNITY = "community"
    CHALLENGE = "challenge"
    VOICE = "voice"

class MemoryInteractionEvent(BaseModel):
    """Event published when memory interaction is recorded"""
    event_type: str = "memory.interaction_recorded"
    user_id: str
    interaction_id: int
    interaction_type: InteractionType
    interaction_data: Dict[str, Any]
    cultural_context: Optional[Dict[str, Any]] = None
    source_service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class MemoryPatternEvent(BaseModel):
    """Event published when mood pattern is updated"""
    event_type: str = "memory.pattern_updated"
    user_id: str
    pattern_id: int
    pattern_type: str
    pattern_data: Dict[str, Any]
    confidence_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None

class MemoryInsightEvent(BaseModel):
    """Event published when behavioral insight is generated"""
    event_type: str = "memory.insight_generated"
    user_id: str
    insight_id: int
    insight_type: str
    insight_data: Dict[str, Any]
    accuracy_score: float
    recommendations: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None

# Incoming event schemas from other services
class MoodEntryEvent(BaseModel):
    """Mood service event schema"""
    event_type: str = "mood.entry_created"
    user_id: str
    mood_entry_id: int
    mood_data: Dict[str, Any]
    cultural_context: Optional[Dict[str, Any]] = None
    timestamp: datetime
    correlation_id: Optional[str] = None

class JournalEntryEvent(BaseModel):
    """Journal service event schema"""
    event_type: str = "journal.entry_created"
    user_id: str
    journal_entry_id: int
    entry_data: Dict[str, Any]
    sentiment_analysis: Optional[Dict[str, Any]] = None
    timestamp: datetime
    correlation_id: Optional[str] = None

class ChatMessageEvent(BaseModel):
    """Chatbot service event schema"""
    event_type: str = "chat.message_sent"
    user_id: str
    message_id: int
    message_data: Dict[str, Any]
    emotion_analysis: Optional[Dict[str, Any]] = None
    cultural_context: Optional[Dict[str, Any]] = None
    timestamp: datetime
    correlation_id: Optional[str] = None

class CommunityPostEvent(BaseModel):
    """Community service event schema"""
    event_type: str = "community.post_created"
    user_id: str
    post_id: int
    post_data: Dict[str, Any]
    engagement_context: Optional[Dict[str, Any]] = None
    timestamp: datetime
    correlation_id: Optional[str] = None
```

#### 1.2: Event Validation and Processing
```python
# File: backend/services/memory_service/src/core/event_processor.py
from typing import Dict, Any, Callable
import structlog
from ..models.events import (
    MoodEntryEvent, JournalEntryEvent, ChatMessageEvent, 
    CommunityPostEvent, InteractionType
)
from ..models.interaction import InteractionCreate

logger = structlog.get_logger(__name__)

class EventProcessor:
    """Process incoming events and convert to memory interactions"""
    
    def __init__(self, memory_engine):
        self.memory_engine = memory_engine
        self.event_handlers: Dict[str, Callable] = {
            "mood.entry_created": self._handle_mood_event,
            "journal.entry_created": self._handle_journal_event,
            "chat.message_sent": self._handle_chat_event,
            "community.post_created": self._handle_community_event,
            "challenge.progress_updated": self._handle_challenge_event
        }
    
    async def process_event(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Process incoming event and create memory interaction"""
        try:
            handler = self.event_handlers.get(event_type)
            if not handler:
                logger.warning("No handler for event type", event_type=event_type)
                return False
            
            interaction = await handler(event_data)
            if interaction:
                await self.memory_engine.record_interaction(interaction)
                logger.info("Event processed successfully", event_type=event_type, 
                           user_id=interaction.user_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error("Event processing failed", event_type=event_type, error=str(e))
            return False
    
    async def _handle_mood_event(self, event_data: Dict[str, Any]) -> InteractionCreate:
        """Handle mood entry event"""
        event = MoodEntryEvent(**event_data)
        
        return InteractionCreate(
            user_id=event.user_id,
            interaction_type=InteractionType.MOOD,
            interaction_data={
                "mood_entry_id": event.mood_entry_id,
                "mood_data": event.mood_data,
                "original_event": "mood.entry_created"
            },
            cultural_context=event.cultural_context,
            metadata={
                "correlation_id": event.correlation_id,
                "original_timestamp": event.timestamp.isoformat()
            },
            source_service="mood_service"
        )
    
    async def _handle_journal_event(self, event_data: Dict[str, Any]) -> InteractionCreate:
        """Handle journal entry event"""
        event = JournalEntryEvent(**event_data)
        
        return InteractionCreate(
            user_id=event.user_id,
            interaction_type=InteractionType.JOURNAL,
            interaction_data={
                "journal_entry_id": event.journal_entry_id,
                "entry_data": event.entry_data,
                "sentiment_analysis": event.sentiment_analysis,
                "original_event": "journal.entry_created"
            },
            cultural_context=None,  # Extract from entry_data if available
            metadata={
                "correlation_id": event.correlation_id,
                "original_timestamp": event.timestamp.isoformat()
            },
            source_service="journal_service"
        )
    
    async def _handle_chat_event(self, event_data: Dict[str, Any]) -> InteractionCreate:
        """Handle chat message event"""
        event = ChatMessageEvent(**event_data)
        
        return InteractionCreate(
            user_id=event.user_id,
            interaction_type=InteractionType.CHAT,
            interaction_data={
                "message_id": event.message_id,
                "message_data": event.message_data,
                "emotion_analysis": event.emotion_analysis,
                "original_event": "chat.message_sent"
            },
            cultural_context=event.cultural_context,
            metadata={
                "correlation_id": event.correlation_id,
                "original_timestamp": event.timestamp.isoformat()
            },
            source_service="chatbot_service"
        )
    
    async def _handle_community_event(self, event_data: Dict[str, Any]) -> InteractionCreate:
        """Handle community post event"""
        event = CommunityPostEvent(**event_data)
        
        return InteractionCreate(
            user_id=event.user_id,
            interaction_type=InteractionType.COMMUNITY,
            interaction_data={
                "post_id": event.post_id,
                "post_data": event.post_data,
                "engagement_context": event.engagement_context,
                "original_event": "community.post_created"
            },
            cultural_context=None,  # Extract from post_data if available
            metadata={
                "correlation_id": event.correlation_id,
                "original_timestamp": event.timestamp.isoformat()
            },
            source_service="community_service"
        )
```

### Task 2: Event Subscribers Implementation (2h)

#### 2.1: NATS Event Subscriber Setup
```python
# File: backend/services/memory_service/src/integrations/event_subscriber.py
import asyncio
import json
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig, ConsumerConfig
import structlog
from typing import Dict, Any

from ..core.event_processor import EventProcessor

logger = structlog.get_logger(__name__)

class MemoryEventSubscriber:
    """NATS event subscriber for memory service"""
    
    def __init__(self, nats_url: str, memory_engine):
        self.nats_url = nats_url
        self.nats_client = NATS()
        self.js = None
        self.event_processor = EventProcessor(memory_engine)
        self.subscriptions = []
        
    async def initialize(self):
        """Initialize NATS connection and JetStream"""
        try:
            await self.nats_client.connect(self.nats_url)
            self.js = self.nats_client.jetstream()
            
            # Ensure required streams exist
            await self._ensure_streams()
            
            # Setup subscriptions
            await self._setup_subscriptions()
            
            logger.info("Memory event subscriber initialized")
            
        except Exception as e:
            logger.error("Failed to initialize event subscriber", error=str(e))
            raise
    
    async def _ensure_streams(self):
        """Ensure required NATS streams exist"""
        streams = [
            ("MOOD_EVENTS", ["mood.>"]),
            ("JOURNAL_EVENTS", ["journal.>"]),
            ("CHAT_EVENTS", ["chat.>"]),
            ("COMMUNITY_EVENTS", ["community.>"]),
            ("CHALLENGE_EVENTS", ["challenge.>"])
        ]
        
        for stream_name, subjects in streams:
            try:
                await self.js.stream_info(stream_name)
                logger.debug("Stream exists", stream=stream_name)
            except:
                # Create stream if it doesn't exist
                await self.js.add_stream(StreamConfig(
                    name=stream_name,
                    subjects=subjects,
                    max_age=86400 * 7  # 7 days retention
                ))
                logger.info("Stream created", stream=stream_name)
    
    async def _setup_subscriptions(self):
        """Setup event subscriptions"""
        events_to_subscribe = [
            ("mood.entry_created", "MOOD_EVENTS"),
            ("journal.entry_created", "JOURNAL_EVENTS"),
            ("chat.message_sent", "CHAT_EVENTS"),
            ("community.post_created", "COMMUNITY_EVENTS"),
            ("challenge.progress_updated", "CHALLENGE_EVENTS")
        ]
        
        for event_type, stream_name in events_to_subscribe:
            try:
                subscription = await self.js.subscribe(
                    event_type,
                    stream=stream_name,
                    durable=f"memory_service_{event_type.replace('.', '_')}",
                    cb=self._create_event_handler(event_type)
                )
                self.subscriptions.append(subscription)
                logger.info("Subscribed to event", event_type=event_type)
                
            except Exception as e:
                logger.error("Failed to subscribe to event", event_type=event_type, error=str(e))
    
    def _create_event_handler(self, event_type: str):
        """Create event handler for specific event type"""
        async def handler(msg):
            try:
                # Decode message
                event_data = json.loads(msg.data.decode())
                
                # Process event
                success = await self.event_processor.process_event(event_type, event_data)
                
                if success:
                    await msg.ack()
                    logger.debug("Event processed successfully", event_type=event_type)
                else:
                    await msg.nak()
                    logger.warning("Event processing failed", event_type=event_type)
                    
            except Exception as e:
                logger.error("Event handler error", event_type=event_type, error=str(e))
                await msg.nak()
        
        return handler
    
    async def cleanup(self):
        """Cleanup subscriptions and connections"""
        try:
            for subscription in self.subscriptions:
                await subscription.unsubscribe()
            
            await self.nats_client.close()
            logger.info("Memory event subscriber cleaned up")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
```

### Task 3: Event Publishers Implementation (1.5h)

#### 3.1: Event Publisher for Memory Events
```python
# File: backend/services/memory_service/src/integrations/event_publisher.py
import json
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig
import structlog
from datetime import datetime
from typing import Dict, Any

from ..models.events import MemoryInteractionEvent, MemoryPatternEvent, MemoryInsightEvent

logger = structlog.get_logger(__name__)

class MemoryEventPublisher:
    """NATS event publisher for memory service"""
    
    def __init__(self, nats_url: str):
        self.nats_url = nats_url
        self.nats_client = NATS()
        self.js = None
        
    async def initialize(self):
        """Initialize NATS connection and JetStream"""
        try:
            await self.nats_client.connect(self.nats_url)
            self.js = self.nats_client.jetstream()
            
            # Ensure memory events stream exists
            await self._ensure_memory_stream()
            
            logger.info("Memory event publisher initialized")
            
        except Exception as e:
            logger.error("Failed to initialize event publisher", error=str(e))
            raise
    
    async def _ensure_memory_stream(self):
        """Ensure MEMORY_EVENTS stream exists"""
        try:
            await self.js.stream_info("MEMORY_EVENTS")
        except:
            # Create stream if it doesn't exist
            await self.js.add_stream(StreamConfig(
                name="MEMORY_EVENTS",
                subjects=["memory.>"],
                max_age=86400 * 30  # 30 days retention
            ))
            logger.info("MEMORY_EVENTS stream created")
    
    async def publish_interaction_recorded(
        self, 
        user_id: str,
        interaction_id: int,
        interaction_type: str,
        interaction_data: Dict[str, Any],
        cultural_context: Dict[str, Any] = None,
        source_service: str = None,
        correlation_id: str = None
    ):
        """Publish memory interaction recorded event"""
        try:
            event = MemoryInteractionEvent(
                user_id=user_id,
                interaction_id=interaction_id,
                interaction_type=interaction_type,
                interaction_data=interaction_data,
                cultural_context=cultural_context,
                source_service=source_service,
                correlation_id=correlation_id
            )
            
            await self.js.publish(
                "memory.interaction_recorded",
                json.dumps(event.dict()).encode(),
                headers={"correlation_id": correlation_id} if correlation_id else None
            )
            
            logger.debug("Interaction event published", user_id=user_id, 
                        interaction_id=interaction_id)
            
        except Exception as e:
            logger.error("Failed to publish interaction event", error=str(e))
    
    async def publish_pattern_updated(
        self,
        user_id: str,
        pattern_id: int,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        confidence_score: float,
        correlation_id: str = None
    ):
        """Publish memory pattern updated event"""
        try:
            event = MemoryPatternEvent(
                user_id=user_id,
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                pattern_data=pattern_data,
                confidence_score=confidence_score,
                correlation_id=correlation_id
            )
            
            await self.js.publish(
                "memory.pattern_updated",
                json.dumps(event.dict()).encode(),
                headers={"correlation_id": correlation_id} if correlation_id else None
            )
            
            logger.debug("Pattern event published", user_id=user_id, pattern_id=pattern_id)
            
        except Exception as e:
            logger.error("Failed to publish pattern event", error=str(e))
    
    async def publish_insight_generated(
        self,
        user_id: str,
        insight_id: int,
        insight_type: str,
        insight_data: Dict[str, Any],
        accuracy_score: float,
        recommendations: Dict[str, Any] = None,
        correlation_id: str = None
    ):
        """Publish memory insight generated event"""
        try:
            event = MemoryInsightEvent(
                user_id=user_id,
                insight_id=insight_id,
                insight_type=insight_type,
                insight_data=insight_data,
                accuracy_score=accuracy_score,
                recommendations=recommendations,
                correlation_id=correlation_id
            )
            
            await self.js.publish(
                "memory.insight_generated", 
                json.dumps(event.dict()).encode(),
                headers={"correlation_id": correlation_id} if correlation_id else None
            )
            
            logger.debug("Insight event published", user_id=user_id, insight_id=insight_id)
            
        except Exception as e:
            logger.error("Failed to publish insight event", error=str(e))
    
    async def cleanup(self):
        """Cleanup publisher connection"""
        try:
            await self.nats_client.close()
            logger.info("Memory event publisher cleaned up")
        except Exception as e:
            logger.error("Error during publisher cleanup", error=str(e))
```

### Task 4: Testing & Monitoring (0.5h)

#### 4.1: Event Integration Tests
```python
# File: backend/services/memory_service/tests/test_event_integration.py
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

from src.integrations.event_subscriber import MemoryEventSubscriber
from src.integrations.event_publisher import MemoryEventPublisher
from src.core.event_processor import EventProcessor

@pytest.mark.asyncio
async def test_mood_event_processing():
    """Test mood event subscription and processing"""
    # Mock memory engine
    memory_engine = AsyncMock()
    
    # Create event processor
    event_processor = EventProcessor(memory_engine)
    
    # Test mood event
    mood_event = {
        "event_type": "mood.entry_created",
        "user_id": "test_user",
        "mood_entry_id": 123,
        "mood_data": {"mood": "happy", "intensity": 8},
        "timestamp": "2025-08-25T10:00:00Z"
    }
    
    # Process event
    success = await event_processor.process_event("mood.entry_created", mood_event)
    
    assert success
    memory_engine.record_interaction.assert_called_once()

@pytest.mark.asyncio
async def test_event_publishing():
    """Test memory event publishing"""
    # Mock NATS client
    mock_nats = AsyncMock()
    mock_js = AsyncMock()
    mock_nats.jetstream.return_value = mock_js
    
    publisher = MemoryEventPublisher("nats://localhost:4222")
    publisher.nats_client = mock_nats
    publisher.js = mock_js
    
    # Test interaction event publishing
    await publisher.publish_interaction_recorded(
        user_id="test_user",
        interaction_id=123,
        interaction_type="mood",
        interaction_data={"mood": "happy"},
        source_service="mood_service"
    )
    
    mock_js.publish.assert_called_once()
    call_args = mock_js.publish.call_args
    assert call_args[0][0] == "memory.interaction_recorded"

@pytest.mark.asyncio 
async def test_event_flow_end_to_end():
    """Test complete event flow from subscription to publishing"""
    # This would be a full integration test
    # Testing the complete flow from receiving an event to publishing memory events
    pass
```

#### 4.2: Event Monitoring
```python
# File: backend/services/memory_service/src/monitoring/event_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import structlog

logger = structlog.get_logger(__name__)

# Event processing metrics
events_processed_total = Counter(
    'memory_events_processed_total',
    'Total number of events processed',
    ['event_type', 'status']
)

event_processing_duration = Histogram(
    'memory_event_processing_duration_seconds',
    'Time spent processing events',
    ['event_type']
)

events_in_queue = Gauge(
    'memory_events_in_queue',
    'Number of events waiting to be processed',
    ['event_type']
)

events_published_total = Counter(
    'memory_events_published_total',
    'Total number of memory events published',
    ['event_type']
)

class EventMetrics:
    """Event processing metrics collection"""
    
    @staticmethod
    def record_event_processed(event_type: str, success: bool):
        """Record event processing metrics"""
        status = "success" if success else "failure"
        events_processed_total.labels(event_type=event_type, status=status).inc()
    
    @staticmethod
    def record_processing_time(event_type: str, duration: float):
        """Record event processing duration"""
        event_processing_duration.labels(event_type=event_type).observe(duration)
    
    @staticmethod
    def record_event_published(event_type: str):
        """Record event publishing"""
        events_published_total.labels(event_type=event_type).inc()
    
    @staticmethod
    def set_queue_size(event_type: str, size: int):
        """Set current queue size"""
        events_in_queue.labels(event_type=event_type).set(size)
```

## Integration Points

### Incoming Events (Subscriptions)
```python
# Events the Memory Service subscribes to:
{
    "mood.entry_created": {
        "source": "mood_service",
        "stream": "MOOD_EVENTS",
        "handler": "_handle_mood_event"
    },
    "journal.entry_created": {
        "source": "journal_service", 
        "stream": "JOURNAL_EVENTS",
        "handler": "_handle_journal_event"
    },
    "chat.message_sent": {
        "source": "chatbot_service",
        "stream": "CHAT_EVENTS", 
        "handler": "_handle_chat_event"
    },
    "community.post_created": {
        "source": "community_service",
        "stream": "COMMUNITY_EVENTS",
        "handler": "_handle_community_event"
    },
    "challenge.progress_updated": {
        "source": "challenge_service",
        "stream": "CHALLENGE_EVENTS",
        "handler": "_handle_challenge_event"
    }
}
```

### Outgoing Events (Publications)
```python
# Events the Memory Service publishes:
{
    "memory.interaction_recorded": {
        "description": "New user interaction stored",
        "consumers": ["ai_event_processor", "proactive_assistance_engine"]
    },
    "memory.pattern_updated": {
        "description": "User mood pattern updated",
        "consumers": ["mood_service", "ai_context_store"]
    },
    "memory.insight_generated": {
        "description": "New behavioral insight generated",
        "consumers": ["proactive_assistance_engine", "notification_service"]
    }
}
```

## Performance Requirements
- **Event Processing Latency**: <50ms per event
- **Event Publishing Latency**: <25ms per published event
- **Event Queue Processing**: Handle 1000+ events per minute
- **Error Rate**: <1% event processing failures
- **Recovery Time**: <30 seconds for event bus reconnection

## Error Handling & Resilience
- **Dead Letter Queues**: Failed events moved to DLQ for manual processing
- **Retry Logic**: Exponential backoff for transient failures
- **Circuit Breaker**: Stop processing if error rate exceeds threshold
- **Event Replay**: Ability to replay events from specific timestamp
- **Graceful Degradation**: Continue operation if some event streams unavailable

## Security Considerations
- **Event Validation**: Schema validation for all incoming events
- **Access Control**: NATS subject-based access control
- **Data Privacy**: No sensitive data in event metadata
- **Audit Trail**: Event processing audit logs with correlation IDs

## Monitoring & Alerting
- **Event Processing Rate**: Monitor events processed per minute
- **Processing Latency**: Alert on processing delays >100ms
- **Error Rate**: Alert on error rate >5%
- **Queue Depth**: Alert on queue backup >1000 events
- **Connection Health**: Monitor NATS connection status

## Risk Mitigation
1. **Event Ordering**: Handle out-of-order events gracefully
2. **Duplicate Events**: Implement idempotent event processing
3. **Data Consistency**: Ensure eventual consistency across services
4. **Resource Usage**: Limit memory usage for event processing
5. **Scalability**: Design for horizontal scaling of event processors

## Definition of Done
- [ ] Event subscriber receiving all required event types
- [ ] Event processor converting events to memory interactions
- [ ] Event publisher publishing memory events
- [ ] Error handling and retry mechanisms implemented
- [ ] Event processing metrics and monitoring
- [ ] Integration tests passing for all event flows
- [ ] Performance requirements met
- [ ] Dead letter queue handling implemented
- [ ] Documentation and runbooks complete
