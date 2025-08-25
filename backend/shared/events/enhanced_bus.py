"""
Enhanced Event Bus Implementation
Extends the existing InMemoryEventBus with NATS capabilities when available.

Features:
- Backward compatibility with existing InMemoryEventBus
- NATS integration when available
- Voice, AI, and Cultural event processing
- Performance monitoring and health checks
- Multilingual event support
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Callable, Any, Optional, Union
from datetime import datetime, timezone
import uuid

# Import existing event system
try:
    from events import Event, EventBus, InMemoryEventBus, get_event_bus, cleanup_event_bus
except ImportError:
    # Define minimal interfaces if import fails
    from abc import ABC, abstractmethod
    from dataclasses import dataclass
    
    @dataclass
    class Event:
        channel: str
        data: Dict[str, Any]
        user_id: Optional[str] = None
        timestamp: Optional[datetime] = None
        event_id: Optional[str] = None
        
        def __post_init__(self):
            if self.timestamp is None:
                self.timestamp = datetime.now(timezone.utc)
            if self.event_id is None:
                self.event_id = str(uuid.uuid4())
    
    class EventBus(ABC):
        @abstractmethod
        async def publish(self, channel: str, data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
            pass
        
        @abstractmethod
        async def subscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
            pass
        
        @abstractmethod
        async def unsubscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
            pass
        
        @abstractmethod
        async def close(self) -> None:
            pass
    
    class InMemoryEventBus(EventBus):
        def __init__(self):
            self.channels: Dict[str, List[Callable[[Event], Any]]] = {}
            self.queues: Dict[str, asyncio.Queue[Event]] = {}
            self.tasks: Dict[str, asyncio.Task[None]] = {}
            self.running = True
        
        async def publish(self, channel: str, data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
            """Publish event to in-memory subscribers"""
            if channel not in self.channels:
                return True  # No subscribers, but success
            
            event = Event(
                channel=channel,
                data=data,
                user_id=user_id,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Call all handlers for this channel
            for handler in self.channels[channel]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for channel {channel}: {e}")
            
            return True
        
        async def subscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
            """Subscribe to a channel with a handler"""
            if channel not in self.channels:
                self.channels[channel] = []
            self.channels[channel].append(handler)
        
        async def unsubscribe(self, channel: str, handler: Callable[[Event], Any]) -> None:
            """Unsubscribe handler from channel"""
            if channel in self.channels and handler in self.channels[channel]:
                self.channels[channel].remove(handler)
        
        async def close(self) -> None:
            """Clean shutdown"""
            self.running = False
            for task in self.tasks.values():
                task.cancel()
            self.tasks.clear()

# Try to import NATS if available
try:
    import nats
    from nats.js import JetStreamContext
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    nats = None

logger = logging.getLogger(__name__)


class EnhancedEventBus(InMemoryEventBus):
    """Enhanced event bus with NATS support and advanced features"""
    
    def __init__(
        self,
        use_nats: bool = True,
        nats_servers: Union[str, List[str]] = "nats://localhost:4222",
        enable_performance_tracking: bool = True
    ):
        super().__init__()
        
        # Configuration
        self.use_nats = use_nats and NATS_AVAILABLE
        self.nats_servers = nats_servers if isinstance(nats_servers, list) else [nats_servers]
        self.enable_performance_tracking = enable_performance_tracking
        
        # NATS connection (optional)
        self.nc = None
        self.js = None
        self.nats_connected = False
        self.stream_cache = set()  # Cache of created streams
        
        # Performance tracking
        self.event_metrics = {
            "total_events": 0,
            "voice_events": 0,
            "ai_events": 0,
            "cultural_events": 0,
            "error_count": 0
        }
        self.latency_samples: List[float] = []
        self.start_time = time.time()
        
        # Event validation and processing
        self.event_validators: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
        self.event_processors: Dict[str, List[Callable[[Event], Event]]] = {}
        
        logger.info(f"🚀 EnhancedEventBus initialized (NATS: {self.use_nats})")
    
    async def initialize(self) -> bool:
        """Initialize the enhanced event bus"""
        try:
            # Initialize parent class - no await needed for InMemoryEventBus
            # The parent __init__ is already called in __init__
            
            # Initialize NATS if enabled
            if self.use_nats:
                await self._initialize_nats()
            
            # Set up event processors
            self._setup_event_processors()
            
            logger.info("✅ EnhancedEventBus initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize EnhancedEventBus: {e}")
            return False
    
    async def _initialize_nats(self) -> bool:
        """Initialize NATS connection with production-ready configuration"""
        if not NATS_AVAILABLE:
            logger.warning("⚠️  NATS package not available, using in-memory fallback")
            return False
        
        try:
            # Production-ready NATS connection with proper timeouts and retry logic
            self.nc = await nats.connect(
                servers=self.nats_servers,
                name="mantrapath-enhanced-bus",
                max_reconnect_attempts=10,     # More attempts for production
                reconnect_time_wait=2.0,       # 2 second wait between attempts
                connect_timeout=10.0,          # 10 second connection timeout
                allow_reconnect=True,          # Allow reconnection for resilience
                ping_interval=60,              # Heartbeat every 60 seconds
                max_outstanding_pings=3       # Max 3 outstanding pings
            )
            
            # Initialize JetStream with production configuration
            self.js = self.nc.jetstream()
            self.nats_connected = True
            
            # Set up basic streams for MantraPath event patterns
            await self._setup_production_streams()
            
            logger.info("✅ NATS JetStream connection established with production configuration")
            return True
            
        except Exception as e:
            logger.error(f"❌ NATS server connection failed: {e}")
            logger.info("🔄 Falling back to in-memory event bus")
            self.nats_connected = False
            self.nc = None
            self.js = None
            return False
    
    async def _setup_production_streams(self) -> None:
        """Set up production NATS streams for MantraPath"""
        if not self.js:
            return
            
        streams_config = [
            {
                "name": "mantrapath-voice",
                "subjects": ["voice.*"],
                "description": "Voice activity and intent processing events"
            },
            {
                "name": "mantrapath-ai", 
                "subjects": ["ai.*", "intelligence.*"],
                "description": "AI processing and intelligence events"
            },
            {
                "name": "mantrapath-mood",
                "subjects": ["mood.*"],
                "description": "Mood tracking and analysis events"
            },
            {
                "name": "mantrapath-journal",
                "subjects": ["journal.*"],
                "description": "Journal entry and analysis events"
            },
            {
                "name": "mantrapath-cultural",
                "subjects": ["cultural.*", "regional.*"],
                "description": "Cultural intelligence and regional adaptation events"
            }
        ]
        
        for stream_config in streams_config:
            try:
                # Check if stream exists
                try:
                    await self.js.stream_info(stream_config["name"])
                    logger.debug(f"✅ Stream {stream_config['name']} already exists")
                except:
                    # Create new stream
                    await self.js.add_stream(
                        name=stream_config["name"],
                        subjects=stream_config["subjects"],
                        max_msgs=1000000,      # 1M messages for production
                        max_age=7*24*3600,     # 7 days retention
                        storage="file",        # Persistent storage
                        description=stream_config["description"]
                    )
                    logger.info(f"✅ Created production stream: {stream_config['name']}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to setup stream {stream_config['name']}: {e}")
                # Continue with other streams even if one fails
    
    def _setup_event_processors(self) -> None:
        """Set up event processors for different event types"""
        
        # Voice event processors
        self.event_processors["voice."] = [
            self._add_voice_metadata,
            self._validate_voice_quality
        ]
        
        # AI event processors
        self.event_processors["ai."] = [
            self._add_ai_metadata,
            self._track_ai_performance
        ]
        
        # Cultural event processors
        self.event_processors["cultural."] = [
            self._add_cultural_metadata,
            self._validate_cultural_data
        ]
    
    async def publish(self, channel: str, data: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """Enhanced publish with processing and validation"""
        try:
            # Create event
            event = Event(channel=channel, data=data, user_id=user_id)
            
            # Process event through processors
            processed_event = await self._process_event(event)
            
            # Validate event if validator exists
            if not await self._validate_event(processed_event):
                logger.warning(f"⚠️  Event validation failed for {channel}")
                self.event_metrics["error_count"] += 1
                return False
            
            # Track performance
            publish_start = time.time()
            
            # Publish to NATS if available (don't fail if NATS is down)
            if self.nats_connected:
                await self._nats_publish(processed_event)
            
            # Always publish to in-memory system as fallback
            success = await super().publish(channel, processed_event.data, user_id)
            
            # Track performance
            if self.enable_performance_tracking:
                latency = (time.time() - publish_start) * 1000  # Convert to milliseconds
                self.latency_samples.append(latency)
                if len(self.latency_samples) > 1000:
                    self.latency_samples = self.latency_samples[-500:]
                
                # Update metrics
                self.event_metrics["total_events"] += 1
                self._update_event_type_metrics(channel)
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Failed to publish enhanced event: {e}")
            self.event_metrics["error_count"] += 1
            return False
    
    async def _process_event(self, event: Event) -> Event:
        """Process event through applicable processors"""
        processed_event = event
        
        # Find applicable processors
        for pattern, processors in self.event_processors.items():
            if event.channel.startswith(pattern):
                for processor in processors:
                    try:
                        processed_event = processor(processed_event)
                    except Exception as e:
                        logger.error(f"❌ Error in event processor: {e}")
        
        return processed_event
    
    async def _validate_event(self, event: Event) -> bool:
        """Validate event data"""
        # Find applicable validator
        for pattern, validator in self.event_validators.items():
            if event.channel.startswith(pattern):
                try:
                    return validator(event.data)
                except Exception as e:
                    logger.error(f"❌ Error in event validator: {e}")
                    return False
        
        return True  # No validator found, assume valid
    
    async def _nats_publish(self, event: Event) -> bool:
        """Publish event using NATS JetStream with automatic stream creation"""
        if not self.nc or not self.js:
            return False
        
        start_time = time.time()
        
        try:
            # Build event data with metadata
            event_data = {
                "channel": event.channel,
                "data": event.data,
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                "event_id": event.event_id
            }
            
            event_json = json.dumps(event_data, ensure_ascii=False).encode('utf-8')
            
            # Ensure the stream exists for this channel pattern with retry logic
            stream_ready = await self._ensure_stream_for_channel(event.channel)
            if stream_ready:
                # Give the stream a moment to be fully ready
                await asyncio.sleep(0.01)  # 10ms delay for stream readiness
            
            # Publish with JetStream and proper timeout
            ack = await asyncio.wait_for(
                self.js.publish(
                    subject=event.channel,
                    payload=event_json,
                    headers={"event_id": event.event_id or "", "user_id": event.user_id or ""}
                ),
                timeout=5.0  # 5 second timeout for production reliability
            )
            
            logger.debug(f"✅ NATS publish successful for {event.channel}: {ack.seq}")
            return True
            
        except asyncio.TimeoutError:
            logger.warning(f"⚠️  NATS publish timeout for {event.channel}, using in-memory fallback")
            self.event_metrics["error_count"] += 1
            return False
        except Exception as e:
            error_msg = str(e).lower()
            if "no response from stream" in error_msg:
                logger.error(f"❌ NATS stream not configured for {event.channel}: {e}")
                # Try to auto-create the stream with longer wait
                try:
                    await self._create_stream_for_channel(event.channel)
                    await asyncio.sleep(0.05)  # 50ms delay after creation
                    # Retry the publish once
                    ack = await asyncio.wait_for(
                        self.js.publish(
                            subject=event.channel,
                            payload=event_json,
                            headers={"event_id": event.event_id or "", "user_id": event.user_id or ""}
                        ),
                        timeout=2.0
                    )
                    logger.info(f"✅ NATS publish successful on retry for {event.channel}: {ack.seq}")
                    return True
                except Exception as retry_error:
                    logger.error(f"❌ NATS retry failed for {event.channel}: {retry_error}")
            elif "connection" in error_msg or "timeout" in error_msg:
                logger.warning(f"⚠️  NATS connection issue for {event.channel}: {e}")
                self.nats_connected = False  # Mark as disconnected for health check
            else:
                logger.error(f"❌ NATS publish failed for {event.channel}: {e}")
            
            self.event_metrics["error_count"] += 1
            return False
    
    async def _ensure_stream_for_channel(self, channel: str) -> bool:
        """Ensure NATS stream exists for the given channel pattern"""
        if not self.js:
            return False
            
        try:
            # Determine stream name based on channel prefix
            stream_name = self._get_stream_name_for_channel(channel)
            
            # Check cache first
            if stream_name in self.stream_cache:
                return True
            
            subjects = self._get_subjects_for_stream(stream_name)
            
            # Try to get existing stream first
            try:
                await self.js.stream_info(stream_name)
                self.stream_cache.add(stream_name)  # Add to cache
                return True  # Stream already exists
            except:
                # Stream doesn't exist, create it
                await self.js.add_stream(
                    name=stream_name,
                    subjects=subjects,
                    max_msgs=100000,  # Increased for production
                    max_age=86400,    # 24 hours retention
                    storage="file",   # Persistent storage
                    discard="old"     # Discard old messages when limit reached
                )
                self.stream_cache.add(stream_name)  # Add to cache
                logger.info(f"✅ Created NATS stream: {stream_name} for subjects: {subjects}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to ensure stream for {channel}: {e}")
            # Try to create a catch-all stream if specific stream creation fails
            try:
                catch_all_name = "mantrapath-catchall"
                if catch_all_name not in self.stream_cache:
                    await self.js.stream_info(catch_all_name)
                    self.stream_cache.add(catch_all_name)
                return True
            except:
                try:
                    await self.js.add_stream(
                        name=catch_all_name,
                        subjects=["*"],
                        max_msgs=50000,
                        max_age=3600,  # 1 hour retention for catch-all
                        storage="memory"  # Use memory for catch-all
                    )
                    self.stream_cache.add(catch_all_name)
                    logger.info(f"✅ Created catch-all stream: {catch_all_name}")
                    return True
                except Exception as e2:
                    logger.error(f"❌ Failed to create catch-all stream: {e2}")
                    return False
    
    async def _create_stream_for_channel(self, channel: str) -> bool:
        """Create NATS stream for channel if it doesn't exist"""
        return await self._ensure_stream_for_channel(channel)
    
    def _get_stream_name_for_channel(self, channel: str) -> str:
        """Get appropriate stream name for a channel"""
        if channel.startswith("voice."):
            return "mantrapath-voice"
        elif channel.startswith("ai."):
            return "mantrapath-ai"
        elif channel.startswith("cultural."):
            return "mantrapath-cultural"
        elif channel.startswith("mood."):
            return "mantrapath-mood"
        elif channel.startswith("journal."):
            return "mantrapath-journal"
        elif channel.startswith("test."):
            return "mantrapath-test"
        else:
            return "mantrapath-general"
    
    def _get_subjects_for_stream(self, stream_name: str) -> List[str]:
        """Get subject patterns for a stream"""
        stream_subjects = {
            "mantrapath-voice": ["voice.*"],
            "mantrapath-ai": ["ai.*", "intelligence.*"],
            "mantrapath-cultural": ["cultural.*", "regional.*"],
            "mantrapath-mood": ["mood.*"],
            "mantrapath-journal": ["journal.*"],
            "mantrapath-test": ["test.*"],
            "mantrapath-general": ["*"]
        }
        return stream_subjects.get(stream_name, ["*"])
    
    def _update_event_type_metrics(self, channel: str) -> None:
        """Update metrics based on event type"""
        if channel.startswith("voice."):
            self.event_metrics["voice_events"] += 1
        elif channel.startswith(("ai.", "intelligence.")):
            self.event_metrics["ai_events"] += 1
        elif channel.startswith(("cultural.", "regional.")):
            self.event_metrics["cultural_events"] += 1
    
    # Event processors
    def _add_voice_metadata(self, event: Event) -> Event:
        """Add voice-specific metadata"""
        if not event.data.get("_metadata"):
            event.data["_metadata"] = {}
        
        event.data["_metadata"]["event_type"] = "voice"
        event.data["_metadata"]["processing_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return event
    
    def _validate_voice_quality(self, event: Event) -> Event:
        """Validate voice event quality"""
        # Add quality validation logic here
        return event
    
    def _add_ai_metadata(self, event: Event) -> Event:
        """Add AI-specific metadata"""
        if not event.data.get("_metadata"):
            event.data["_metadata"] = {}
        
        event.data["_metadata"]["event_type"] = "ai"
        event.data["_metadata"]["processing_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return event
    
    def _track_ai_performance(self, event: Event) -> Event:
        """Track AI performance metrics"""
        # Add AI performance tracking logic here
        return event
    
    def _add_cultural_metadata(self, event: Event) -> Event:
        """Add cultural-specific metadata"""
        if not event.data.get("_metadata"):
            event.data["_metadata"] = {}
        
        event.data["_metadata"]["event_type"] = "cultural"
        event.data["_metadata"]["processing_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return event
    
    def _validate_cultural_data(self, event: Event) -> Event:
        """Validate cultural event data"""
        # Add cultural data validation logic here
        return event
    
    # Monitoring and health checks
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        uptime = time.time() - self.start_time
        
        stats = {
            "uptime_seconds": uptime,
            "total_events": self.event_metrics["total_events"],
            "voice_events": self.event_metrics["voice_events"],
            "ai_events": self.event_metrics["ai_events"],
            "cultural_events": self.event_metrics["cultural_events"],
            "error_count": self.event_metrics["error_count"],
            "events_per_second": self.event_metrics["total_events"] / uptime if uptime > 0 else 0,
            "nats_connected": self.nats_connected,
            "active_subscriptions": len(self.channels),
            "active_workers": len(self.tasks)
        }
        
        if self.latency_samples:
            stats.update({
                "avg_latency_ms": sum(self.latency_samples) / len(self.latency_samples),
                "max_latency_ms": max(self.latency_samples),
                "min_latency_ms": min(self.latency_samples),
                "p95_latency_ms": sorted(self.latency_samples)[int(len(self.latency_samples) * 0.95)],
                "p99_latency_ms": sorted(self.latency_samples)[int(len(self.latency_samples) * 0.99)]
            })
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_bus_type": "enhanced",
            "in_memory_status": "active",
            "nats_status": "connected" if self.nats_connected else "disconnected",
            "performance": self.get_performance_stats()
        }
        
        # Check for issues
        issues = []
        
        if self.event_metrics["error_count"] > 0:
            error_rate = self.event_metrics["error_count"] / max(self.event_metrics["total_events"], 1)
            if error_rate > 0.05:  # 5% error rate
                issues.append(f"High error rate: {error_rate:.2%}")
        
        if self.latency_samples:
            avg_latency = sum(self.latency_samples) / len(self.latency_samples)
            if avg_latency > 100:  # 100ms threshold
                issues.append(f"High latency: {avg_latency:.2f}ms")
        
        if self.use_nats and not self.nats_connected:
            issues.append("NATS connection lost")
        
        if issues:
            health["status"] = "degraded"
            health["issues"] = issues
        
        return health
    
    async def close(self) -> None:
        """Close enhanced event bus"""
        logger.info("🛑 Closing EnhancedEventBus...")
        
        # Close NATS connection
        if self.nc:
            try:
                await self.nc.close()
            except (RuntimeError, Exception) as e:
                # Ignore event loop closure and other shutdown errors
                logger.debug(f"NATS close error (ignored): {e}")
        
        # Close parent
        await super().close()
        
        logger.info("✅ EnhancedEventBus closed")

    async def connect(self) -> bool:
        """Connect the enhanced event bus - compatibility method"""
        return await self.initialize()
    
    async def disconnect(self) -> None:
        """Disconnect the enhanced event bus - compatibility method"""
        await self.close()


# Global enhanced event bus instance
_global_enhanced_event_bus: Optional[EnhancedEventBus] = None


def get_enhanced_event_bus() -> EnhancedEventBus:
    """Get the global enhanced event bus instance with environment-aware configuration"""
    global _global_enhanced_event_bus
    
    if _global_enhanced_event_bus is None:
        # Environment-aware configuration
        env = os.getenv("ENV", "development").lower()
        use_nats = os.getenv("USE_NATS_EVENT_BUS", "true").lower() == "true"
        nats_servers = os.getenv("NATS_SERVERS") or os.getenv("NATS_URL", "nats://localhost:4222")
        
        # If we're in a test environment, check if NATS is actually available
        if env in ["test", "testing"] and use_nats:
            # Quick connectivity check for tests
            try:
                import socket
                host, port = "localhost", 4222
                if "://" in nats_servers:
                    # Parse NATS URL
                    parts = nats_servers.split("://")[1].split(":")
                    host = parts[0]
                    port = int(parts[1]) if len(parts) > 1 else 4222
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result != 0:
                    logger.info(f"🔄 NATS server not available at {host}:{port}, using in-memory fallback for tests")
                    use_nats = False
                    
            except Exception:
                logger.info("🔄 NATS connectivity check failed, using in-memory fallback for tests")
                use_nats = False
        
        _global_enhanced_event_bus = EnhancedEventBus(
            use_nats=use_nats,
            nats_servers=nats_servers
        )
    
    return _global_enhanced_event_bus


async def cleanup_enhanced_event_bus():
    """Cleanup the global enhanced event bus"""
    global _global_enhanced_event_bus
    if _global_enhanced_event_bus:
        await _global_enhanced_event_bus.close()
        _global_enhanced_event_bus = None


# Event channel constants for V3 enhanced events
class V3EventChannels:
    """V3 enhanced event channel names"""
    
    # Voice Events
    VOICE_ACTIVITY_DETECTED = "voice.activity_detected"
    VOICE_SPEECH_START = "voice.speech_start"
    VOICE_SPEECH_END = "voice.speech_end"
    VOICE_INTENT_CLASSIFIED = "voice.intent_classified"
    
    # AI Events
    AI_INFERENCE_REQUESTED = "ai.inference_requested"
    AI_INFERENCE_COMPLETED = "ai.inference_completed"
    AI_MODEL_LOADED = "ai.model_loaded"
    AI_CONTEXT_UPDATED = "ai.context_updated"
    
    # Intelligence Events
    INTELLIGENCE_CONTEXT_SHARED = "intelligence.context_shared"
    INTELLIGENCE_INSIGHT_GENERATED = "intelligence.insight_generated"
    INTELLIGENCE_PREDICTION_MADE = "intelligence.prediction_made"
    
    # Cultural Events
    CULTURAL_CONTEXT_DETECTED = "cultural.context_detected"
    CULTURAL_PREFERENCE_UPDATED = "cultural.preference_updated"
    CULTURAL_ADAPTATION_APPLIED = "cultural.adaptation_applied"
    
    # Regional Events
    REGIONAL_TREND_DETECTED = "regional.trend_detected"
    REGIONAL_PATTERN_IDENTIFIED = "regional.pattern_identified"
    REGIONAL_RECOMMENDATION_GENERATED = "regional.recommendation_generated"
    
    # Translation Events (for backward compatibility)
    TRANSLATION_COMPLETED = "translation.completed"
    TRANSLATION_FAILED = "translation.failed"

    # General Streams - V3 service events
    MOOD_ENTRY_CREATED = "mood.entry.created"
    JOURNAL_ENTRY_CREATED = "journal.entry.created"
    CHALLENGE_PROGRESS_UPDATED = "community.challenge.progress.updated"
    COMMUNITY_POST_CREATED = "community.post.created"
    INSIGHT_DELTA = "ml.insight.delta"
    
    # Notification Events
    NOTIFICATION_SENT = "notification.sent"
    NOTIFICATION_DELIVERED = "notification.delivered"
    NOTIFICATION_FAILED = "notification.failed"
    
    # Content Events
    CONTENT_RECOMMENDATION_CREATED = "content.recommendation.created"
    CONTENT_ACCESSED = "content.accessed"
    CONTENT_RATED = "content.rated"


# Helper functions for publishing V3 events
async def publish_voice_activity_event(
    activity_type: str,
    audio_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> bool:
    """Publish voice activity event"""
    bus = get_enhanced_event_bus()
    channel = f"voice.{activity_type}"
    return await bus.publish(channel, audio_data, user_id)


async def publish_ai_processing_event(
    event_type: str,
    model_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> bool:
    """Publish AI processing event"""
    bus = get_enhanced_event_bus()
    channel = f"ai.{event_type}"
    return await bus.publish(channel, model_data, user_id)


async def publish_cultural_intelligence_event(
    event_type: str,
    cultural_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> bool:
    """Publish cultural intelligence event"""
    bus = get_enhanced_event_bus()
    channel = f"cultural.{event_type}"
    return await bus.publish(channel, cultural_data, user_id)


async def publish_regional_intelligence_event(
    event_type: str,
    regional_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> bool:
    """Publish regional intelligence event"""
    bus = get_enhanced_event_bus()
    channel = f"regional.{event_type}"
    return await bus.publish(channel, regional_data, user_id)
