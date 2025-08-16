# Before Sprint 2: Critical Components Implementation Plan
**Generated on**: August 16, 2025  
**Scope**: Implementation roadmap for missing critical components  
**Timeline**: Must be completed before Sprint 2 (V3-BK-005 AI Event Processing Pipeline)

## Executive Summary

Based on deep analysis of 15+ services and shared modules, this document outlines the precise implementation steps needed to activate the event-driven architecture, implement cross-service AI context sharing, add real-time infrastructure, and ensure seamless service integration before Sprint 2.

### Current State Analysis
- ✅ **Enhanced Event Bus**: Fully implemented in `shared/events/enhanced_bus.py` (805 lines)
- ❌ **Event Publishing**: Commented out across all services (`# from shared.events`)
- ✅ **WebSocket Infrastructure**: Implemented in notification service only
- ❌ **AI Context Sharing**: No unified context aggregation
- ❌ **Real-time Processing**: Limited to notification service

### Success Criteria
- [ ] All services actively publishing events to enhanced event bus
- [ ] Cross-service AI context sharing implemented
- [ ] Real-time WebSocket infrastructure across critical services
- [ ] End-to-end event flow testing completed

---

## 1. Event Bus Integration Activation

### 1.1 Current State Analysis

**Enhanced Event Bus Status**: ✅ READY
- **Location**: `/backend/shared/events/enhanced_bus.py`
- **Features**: NATS + in-memory fallback, performance monitoring, event validation
- **Channels**: Voice, AI, Cultural, Mood, Journal events
- **Status**: Fully implemented but not used by services

**Event Publishing Status**: ❌ COMMENTED OUT
```python
# Current state across services:
# from shared.events import publish_mood_entry_created  # COMMENTED
# await event_bus.publish("mood_entry_created", data)  # COMMENTED
```

**Services with Commented Events**:
1. **Mood Service**: `mood_entry_created`, `journal_entry_created`
2. **Community Service**: `community_post_created`, `challenge_progress_updated`  
3. **ML Service**: `insight_delta`, AI processing events
4. **Voice Service**: Voice activity events (partially implemented)
5. **Translation Service**: Translation events (implemented but not fully integrated)

### 1.2 Implementation Tasks

#### Task 1.1: Activate Event Publishing in Services (HIGH PRIORITY)
**Estimate**: 4 hours  
**Dependencies**: None  
**Risk**: Low

**Mood Service Activation**:
```python
# File: /backend/services/mood_service/main.py
# BEFORE (lines 34-36):
# from shared.events import publish_mood_entry_created, publish_journal_entry_created
# from shared.events import get_enhanced_event_bus, V3EventChannels

# AFTER:
from shared.events import publish_mood_entry_created, publish_journal_entry_created
from shared.events import get_enhanced_event_bus, V3EventChannels

# Uncomment lines 809, 939:
# await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, build_v3_mood_payload(mood_entry), current_user["user_id"])
await bus.publish(V3EventChannels.MOOD_ENTRY_CREATED, build_v3_mood_payload(mood_entry), current_user["user_id"])
```

**Community Service Activation**:
```python
# File: /backend/services/community_service/main.py
# BEFORE (line 27):
# from shared.events import publish_community_post_created, publish_challenge_progress_updated

# AFTER:
from shared.events import publish_community_post_created, publish_challenge_progress_updated
```

**ML Service Activation**:
```python
# File: /backend/services/ml_service/main.py
# BEFORE (lines 26-28):
# from shared.events import get_event_bus, EventChannels, Event, publish_insight_delta
# from shared.events import get_enhanced_event_bus, V3EventChannels

# AFTER:
from shared.events import get_event_bus, EventChannels, Event, publish_insight_delta
from shared.events import get_enhanced_event_bus, V3EventChannels
```

#### Task 1.2: Initialize Enhanced Event Bus in Services (HIGH PRIORITY)
**Estimate**: 2 hours  
**Dependencies**: Task 1.1  
**Risk**: Low

**Service Startup Integration**:
```python
# Add to each service's main.py startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize enhanced event bus
    event_bus = get_enhanced_event_bus()
    await event_bus.initialize()
    
    yield
    
    # Cleanup
    await cleanup_enhanced_event_bus()

app = FastAPI(lifespan=lifespan)
```

#### Task 1.3: Add Event Subscriptions for Cross-Service Communication (MEDIUM PRIORITY)
**Estimate**: 6 hours  
**Dependencies**: Task 1.1, 1.2  
**Risk**: Medium

**Content Service - Subscribe to Mood Events**:
```python
# File: /backend/services/content_service/main.py
async def setup_event_subscriptions():
    event_bus = get_enhanced_event_bus()
    
    @event_bus.subscribe(V3EventChannels.MOOD_ENTRY_CREATED)
    async def handle_mood_change(event: Event):
        # Update content recommendations based on mood
        await update_mood_based_recommendations(
            event.user_id, 
            event.data.get("mood_score", 5)
        )
```

**Community Service - Subscribe to AI Events**:
```python
# File: /backend/services/community_service/main.py
async def setup_event_subscriptions():
    event_bus = get_enhanced_event_bus()
    
    @event_bus.subscribe(V3EventChannels.AI_CONTEXT_UPDATED)
    async def handle_ai_context_update(event: Event):
        # Update community recommendations
        await update_community_suggestions(event.user_id, event.data)
```

### 1.4 Verification and Testing
```bash
# Test event flow between services
curl -X POST "http://localhost:8003/mood-entries" \\
  -H "Authorization: Bearer $TOKEN" \\
  -d '{"mood_score": 7, "energy_level": 6}'

# Check event bus health
curl "http://localhost:8000/health/event-bus"
```

---

## 2. Cross-Service AI Context Implementation

### 2.1 Current State Analysis

**Unified Insights Aggregator**: ✅ PARTIAL
- **Location**: `/backend/services/ml_service/integrations/unified_insights_aggregator.py`
- **Features**: Mood statistics aggregation, caching, basic insights
- **Limitations**: Only mood data, no cross-service intelligence

**Missing Components**:
- No unified user context store
- No real-time context updates
- No cross-service context queries
- No AI processing pipeline integration

### 2.2 Implementation Tasks

#### Task 2.1: Create AI Context Store Service (HIGH PRIORITY)
**Estimate**: 8 hours  
**Dependencies**: Task 1.1 completed  
**Risk**: Medium

**New Service Structure**:
```
/backend/services/ai_context_store/
├── main.py                    # FastAPI service
├── models/
│   ├── context_models.py      # Pydantic models
│   └── ai_context.py          # AI context aggregation
├── storage/
│   ├── redis_store.py         # Redis-based context caching
│   └── postgres_store.py      # PostgreSQL persistence
└── api/
    ├── context_api.py         # Context CRUD operations
    └── aggregation_api.py     # Context aggregation endpoints
```

**Core Context Model**:
```python
# File: /backend/services/ai_context_store/models/context_models.py
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

class UserAIContext(BaseModel):
    user_id: str
    last_updated: datetime
    
    # Mood Intelligence
    mood_context: Optional[Dict[str, Any]] = None
    mood_patterns: List[Dict[str, Any]] = []
    mood_predictions: Optional[Dict[str, Any]] = None
    
    # Community Intelligence  
    community_engagement: Optional[Dict[str, Any]] = None
    social_patterns: List[Dict[str, Any]] = []
    connection_suggestions: List[str] = []
    
    # Content Intelligence
    content_preferences: Optional[Dict[str, Any]] = None
    reading_patterns: List[Dict[str, Any]] = []
    content_recommendations: List[str] = []
    
    # Conversation Intelligence
    conversation_history: List[Dict[str, Any]] = []
    conversation_patterns: Optional[Dict[str, Any]] = None
    crisis_risk_level: float = 0.0
    
    # Cultural Intelligence
    cultural_context: Optional[Dict[str, Any]] = None
    language_preferences: List[str] = []
    regional_adaptations: List[Dict[str, Any]] = []
    
    # AI Processing Metadata
    context_confidence: float = 0.0
    last_ai_analysis: Optional[datetime] = None
    processing_version: str = "1.0"

class ContextUpdateRequest(BaseModel):
    user_id: str
    context_type: str  # "mood", "community", "content", "conversation", "cultural"
    context_data: Dict[str, Any]
    merge_strategy: str = "update"  # "update", "replace", "append"

class ContextQueryRequest(BaseModel):
    user_id: str
    context_types: List[str] = []  # Empty means all types
    include_patterns: bool = True
    include_predictions: bool = False
```

**AI Context Aggregator**:
```python
# File: /backend/services/ai_context_store/models/ai_context.py
import asyncio
from typing import Dict, List, Optional
from shared.database import get_db
from shared.events import get_enhanced_event_bus, V3EventChannels

class AIContextAggregator:
    def __init__(self):
        self.event_bus = get_enhanced_event_bus()
        self.context_store = {}  # Redis integration
    
    async def initialize(self):
        """Initialize context aggregator with event subscriptions"""
        await self._setup_event_subscriptions()
    
    async def _setup_event_subscriptions(self):
        """Subscribe to all relevant events for context building"""
        
        # Mood events
        await self.event_bus.subscribe(
            V3EventChannels.MOOD_ENTRY_CREATED,
            self._handle_mood_update
        )
        
        # Journal events  
        await self.event_bus.subscribe(
            V3EventChannels.JOURNAL_ENTRY_CREATED,
            self._handle_journal_update
        )
        
        # Community events
        await self.event_bus.subscribe(
            "community.post_created",
            self._handle_community_update
        )
        
        # Voice events
        await self.event_bus.subscribe(
            V3EventChannels.VOICE_INTENT_CLASSIFIED,
            self._handle_voice_update
        )
    
    async def _handle_mood_update(self, event):
        """Update mood context when mood entry is created"""
        user_id = event.user_id
        mood_data = event.data
        
        # Get current context
        context = await self.get_user_context(user_id)
        
        # Update mood context
        context.mood_context = {
            "current_mood": mood_data.get("mood_score", 5),
            "energy_level": mood_data.get("energy_level", 5),
            "stress_level": mood_data.get("stress_level", 5),
            "last_entry": event.timestamp,
            "context_tags": mood_data.get("context_tags", [])
        }
        
        # Add to mood patterns
        pattern_entry = {
            "timestamp": event.timestamp,
            "mood_score": mood_data.get("mood_score", 5),
            "energy_level": mood_data.get("energy_level", 5),
            "stress_level": mood_data.get("stress_level", 5)
        }
        context.mood_patterns.append(pattern_entry)
        
        # Keep only recent patterns (last 100 entries)
        context.mood_patterns = context.mood_patterns[-100:]
        
        # Store updated context
        await self.store_user_context(user_id, context)
        
        # Publish context update event
        await self.event_bus.publish(
            V3EventChannels.AI_CONTEXT_UPDATED,
            {
                "user_id": user_id,
                "context_type": "mood",
                "context_data": context.mood_context
            },
            user_id
        )
    
    async def get_user_context(self, user_id: str) -> UserAIContext:
        """Get comprehensive user AI context"""
        # Try Redis cache first
        cached = await self._get_cached_context(user_id)
        if cached:
            return cached
        
        # Build from database if not cached
        context = await self._build_context_from_db(user_id)
        
        # Cache the result
        await self._cache_context(user_id, context)
        
        return context
    
    async def update_user_context(
        self, 
        user_id: str, 
        context_type: str, 
        context_data: Dict,
        merge_strategy: str = "update"
    ):
        """Update specific part of user context"""
        context = await self.get_user_context(user_id)
        
        if context_type == "mood":
            if merge_strategy == "replace":
                context.mood_context = context_data
            else:
                context.mood_context = {**(context.mood_context or {}), **context_data}
        
        elif context_type == "community":
            if merge_strategy == "replace":
                context.community_engagement = context_data
            else:
                context.community_engagement = {**(context.community_engagement or {}), **context_data}
        
        # Add other context types...
        
        await self.store_user_context(user_id, context)
        
        # Publish update event
        await self.event_bus.publish(
            V3EventChannels.AI_CONTEXT_UPDATED,
            {
                "user_id": user_id,
                "context_type": context_type,
                "context_data": context_data
            },
            user_id
        )
```

#### Task 2.2: Integrate Context Store with Existing Services (HIGH PRIORITY)
**Estimate**: 6 hours  
**Dependencies**: Task 2.1  
**Risk**: Medium

**Mood Service Integration**:
```python
# File: /backend/services/mood_service/main.py
# Add context integration to mood entry creation

@app.post("/mood-entries")
async def create_mood_entry(mood_data: MoodCreate):
    # Create mood entry (existing code)
    mood_entry = await create_enhanced_mood_entry(mood_data, user_id, db)
    
    # Update AI context
    context_client = AIContextClient()
    await context_client.update_context(
        user_id=user_id,
        context_type="mood",
        context_data={
            "current_mood": mood_entry.mood_score,
            "energy_level": mood_entry.energy_level,
            "stress_level": mood_entry.stress_level,
            "timestamp": mood_entry.created_at
        }
    )
    
    return mood_entry
```

**Content Service Integration**:
```python
# File: /backend/services/content_service/main.py
# Add AI context-aware content recommendations

@app.get("/content/personalized")
async def get_personalized_content(user_id: str):
    # Get AI context
    context_client = AIContextClient()
    user_context = await context_client.get_context(user_id)
    
    # Use mood and preferences for content ranking
    mood_score = user_context.mood_context.get("current_mood", 5)
    content_prefs = user_context.content_preferences or {}
    
    # Adjust content selection based on mood
    if mood_score < 4:
        # Low mood - recommend uplifting content
        category_boost = ["motivation", "mindfulness", "self-care"]
    elif mood_score > 7:
        # High mood - recommend growth content  
        category_boost = ["challenges", "learning", "community"]
    else:
        # Neutral mood - use preferences
        category_boost = content_prefs.get("preferred_categories", [])
    
    # Query content with context-aware ranking
    content = await get_mood_aware_content(category_boost, mood_score)
    
    return content
```

#### Task 2.3: Implement Context Query API (MEDIUM PRIORITY)
**Estimate**: 4 hours  
**Dependencies**: Task 2.1, 2.2  
**Risk**: Low

**Context API Endpoints**:
```python
# File: /backend/services/ai_context_store/api/context_api.py

@app.get("/context/{user_id}")
async def get_user_context(
    user_id: str,
    include_patterns: bool = True,
    include_predictions: bool = False,
    context_types: List[str] = Query([])
):
    """Get user AI context with optional filtering"""
    aggregator = AIContextAggregator()
    context = await aggregator.get_user_context(user_id)
    
    # Filter context types if specified
    if context_types:
        filtered_context = UserAIContext(
            user_id=context.user_id,
            last_updated=context.last_updated
        )
        
        for context_type in context_types:
            if context_type == "mood" and context.mood_context:
                filtered_context.mood_context = context.mood_context
                if include_patterns:
                    filtered_context.mood_patterns = context.mood_patterns
            # Add other context types...
        
        return filtered_context
    
    return context

@app.post("/context/{user_id}/update")
async def update_user_context(
    user_id: str,
    update_request: ContextUpdateRequest
):
    """Update specific part of user context"""
    aggregator = AIContextAggregator()
    await aggregator.update_user_context(
        user_id=user_id,
        context_type=update_request.context_type,
        context_data=update_request.context_data,
        merge_strategy=update_request.merge_strategy
    )
    
    return {"status": "updated", "user_id": user_id}

@app.get("/context/{user_id}/summary")
async def get_context_summary(user_id: str):
    """Get high-level context summary for quick access"""
    aggregator = AIContextAggregator()
    context = await aggregator.get_user_context(user_id)
    
    summary = {
        "user_id": user_id,
        "last_updated": context.last_updated,
        "context_confidence": context.context_confidence,
        "crisis_risk_level": context.crisis_risk_level,
        "active_context_types": []
    }
    
    if context.mood_context:
        summary["active_context_types"].append("mood")
        summary["current_mood"] = context.mood_context.get("current_mood")
    
    if context.community_engagement:
        summary["active_context_types"].append("community")
    
    if context.content_preferences:
        summary["active_context_types"].append("content")
    
    return summary
```

---

## 3. Real-time Infrastructure Implementation

### 3.1 Current State Analysis

**WebSocket Implementation**: ✅ PARTIAL
- **Location**: `/backend/services/notification_service/main.py`
- **Features**: User connections, heartbeat, message handling
- **Limitations**: Only in notification service, no cross-service coordination

**Missing Real-time Features**:
- No WebSocket in mood, content, community services
- No real-time event streaming to frontend
- No live collaboration features
- No real-time AI processing updates

### 3.2 Implementation Tasks

#### Task 3.1: Create Shared WebSocket Manager (HIGH PRIORITY)
**Estimate**: 6 hours  
**Dependencies**: None  
**Risk**: Medium

**Shared WebSocket Infrastructure**:
```python
# File: /backend/shared/websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List, Any, Optional
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Centralized WebSocket connection manager for all services"""
    
    def __init__(self):
        # user_id -> Set[WebSocket connections]
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # connection_id -> user_id mapping for cleanup
        self.connection_users: Dict[int, str] = {}
        # service-specific channels
        self.service_channels: Dict[str, Set[str]] = {}  # service -> user_ids
        
    async def connect(self, websocket: WebSocket, user_id: str, service: str = "general"):
        """Connect a WebSocket for a user to a specific service"""
        await websocket.accept()
        
        # Add to user connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Track connection-user mapping
        self.connection_users[id(websocket)] = user_id
        
        # Add to service channel
        if service not in self.service_channels:
            self.service_channels[service] = set()
        self.service_channels[service].add(user_id)
        
        logger.info(f"WebSocket connected: user={user_id}, service={service}")
        
        # Send connection confirmation
        await self.send_to_user(user_id, {
            "type": "connection_established",
            "service": service,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id
        })
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket"""
        connection_id = id(websocket)
        user_id = self.connection_users.get(connection_id)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Clean up empty sets
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Remove from service channels
                for service, users in self.service_channels.items():
                    users.discard(user_id)
        
        # Clean up connection mapping
        if connection_id in self.connection_users:
            del self.connection_users[connection_id]
        
        logger.info(f"WebSocket disconnected: user={user_id}")
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to all connections for a user"""
        if user_id not in self.active_connections:
            return False
        
        message_json = json.dumps(message, default=str)
        disconnected = []
        
        for websocket in self.active_connections[user_id].copy():
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.append(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected:
            self.disconnect(websocket)
        
        return len(self.active_connections.get(user_id, [])) > 0
    
    async def send_to_service_users(self, service: str, message: Dict[str, Any]):
        """Send message to all users connected to a service"""
        if service not in self.service_channels:
            return 0
        
        sent_count = 0
        for user_id in self.service_channels[service]:
            if await self.send_to_user(user_id, message):
                sent_count += 1
        
        return sent_count
    
    async def broadcast(self, message: Dict[str, Any], exclude_users: Set[str] = None):
        """Broadcast message to all connected users"""
        exclude_users = exclude_users or set()
        sent_count = 0
        
        for user_id in self.active_connections.keys():
            if user_id not in exclude_users:
                if await self.send_to_user(user_id, message):
                    sent_count += 1
        
        return sent_count
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(connections) for connections in self.active_connections.values())
        
        return {
            "connected_users": len(self.active_connections),
            "total_connections": total_connections,
            "service_channels": {
                service: len(users) for service, users in self.service_channels.items()
            },
            "users_per_service": dict(self.service_channels)
        }
    
    async def handle_heartbeat(self, user_id: str):
        """Handle heartbeat from client"""
        await self.send_to_user(user_id, {
            "type": "heartbeat_ack",
            "timestamp": datetime.utcnow().isoformat()
        })

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

# WebSocket endpoint decorator for services
def websocket_endpoint(service_name: str):
    """Decorator to add WebSocket support to a service"""
    def decorator(app):
        @app.websocket(f"/ws/{service_name}")
        async def websocket_handler(websocket: WebSocket, user_id: str):
            try:
                await websocket_manager.connect(websocket, user_id, service_name)
                
                # Keep connection alive
                while True:
                    try:
                        data = await websocket.receive_json()
                        
                        # Handle different message types
                        if data.get("type") == "heartbeat":
                            await websocket_manager.handle_heartbeat(user_id)
                        elif data.get("type") == "subscribe":
                            # Handle subscription to specific events
                            await handle_subscription(user_id, data, service_name)
                        
                    except WebSocketDisconnect:
                        break
                    except Exception as e:
                        logger.error(f"WebSocket error for {service_name}: {e}")
                        break
                        
            except Exception as e:
                logger.error(f"WebSocket connection error for {service_name}: {e}")
            finally:
                websocket_manager.disconnect(websocket)
        
        # Add connection status endpoint
        @app.get(f"/ws/{service_name}/status")
        async def websocket_status():
            return websocket_manager.get_connection_stats()
        
        return app
    return decorator

async def handle_subscription(user_id: str, data: Dict, service_name: str):
    """Handle WebSocket subscription requests"""
    event_types = data.get("event_types", [])
    
    # Store subscription preferences
    # This would integrate with the event bus for targeted delivery
    logger.info(f"User {user_id} subscribed to events: {event_types} in {service_name}")
```

#### Task 3.2: Add WebSocket Support to Critical Services (HIGH PRIORITY)
**Estimate**: 8 hours  
**Dependencies**: Task 3.1  
**Risk**: Medium

**Mood Service WebSocket Integration**:
```python
# File: /backend/services/mood_service/main.py
from shared.websocket_manager import websocket_endpoint, websocket_manager

# Add WebSocket decorator
app = websocket_endpoint("mood")(app)

# Integrate with mood entry creation
@app.post("/mood-entries")
async def create_mood_entry(mood_data: MoodCreate):
    # Create mood entry (existing code)
    mood_entry = await create_enhanced_mood_entry(mood_data, user_id, db)
    
    # Send real-time update to user
    await websocket_manager.send_to_user(user_id, {
        "type": "mood_entry_created",
        "data": {
            "id": str(mood_entry.id),
            "mood_score": mood_entry.mood_score,
            "energy_level": mood_entry.energy_level,
            "created_at": mood_entry.created_at.isoformat()
        },
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Send insights update if available
    if mood_entry.mood_score < 4:  # Low mood
        await websocket_manager.send_to_user(user_id, {
            "type": "mood_insight",
            "data": {
                "message": "I notice your mood is lower today. Would you like some personalized support?",
                "suggestions": ["breathing exercise", "uplifting content", "connect with community"],
                "urgency": "medium"
            }
        })
    
    return mood_entry
```

**Content Service WebSocket Integration**:
```python
# File: /backend/services/content_service/main.py
from shared.websocket_manager import websocket_endpoint, websocket_manager

# Add WebSocket decorator
app = websocket_endpoint("content")(app)

# Real-time content recommendations
@app.get("/content/feed")
async def get_personalized_feed(user_id: str):
    # Get content (existing code)
    content_items = await get_content_feed(user_id)
    
    # Send real-time content update
    await websocket_manager.send_to_user(user_id, {
        "type": "content_feed_updated",
        "data": {
            "total_items": len(content_items),
            "featured_content": content_items[:3],  # Top 3 items
            "categories": list(set(item.category for item in content_items))
        },
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return content_items
```

**Community Service WebSocket Integration**:
```python
# File: /backend/services/community_service/main.py
from shared.websocket_manager import websocket_endpoint, websocket_manager

# Add WebSocket decorator
app = websocket_endpoint("community")(app)

# Real-time forum updates
@app.post("/forums/{forum_id}/threads")
async def create_thread(forum_id: str, thread_data: ThreadCreate):
    # Create thread (existing code)
    thread = await create_forum_thread(forum_id, thread_data, user_id)
    
    # Notify all forum members in real-time
    forum_members = await get_forum_members(forum_id)
    
    for member_id in forum_members:
        await websocket_manager.send_to_user(member_id, {
            "type": "forum_thread_created",
            "data": {
                "forum_id": forum_id,
                "thread_id": str(thread.id),
                "title": thread.title,
                "author": thread.author_id,
                "created_at": thread.created_at.isoformat()
            }
        })
    
    return thread
```

#### Task 3.3: Integrate WebSocket with Event Bus (HIGH PRIORITY)
**Estimate**: 4 hours  
**Dependencies**: Task 3.1, 3.2, Task 1.1  
**Risk**: Medium

**Event-to-WebSocket Bridge**:
```python
# File: /backend/shared/websocket_event_bridge.py
from shared.events import get_enhanced_event_bus, V3EventChannels
from shared.websocket_manager import websocket_manager
import asyncio
import logging

logger = logging.getLogger(__name__)

class WebSocketEventBridge:
    """Bridge between event bus and WebSocket connections"""
    
    def __init__(self):
        self.event_bus = get_enhanced_event_bus()
        self.ws_manager = websocket_manager
        self.subscriptions = {}
    
    async def initialize(self):
        """Initialize event subscriptions for WebSocket forwarding"""
        
        # Subscribe to all major events
        await self.event_bus.subscribe(
            V3EventChannels.MOOD_ENTRY_CREATED,
            self._forward_mood_event
        )
        
        await self.event_bus.subscribe(
            V3EventChannels.AI_CONTEXT_UPDATED,
            self._forward_ai_context_event
        )
        
        await self.event_bus.subscribe(
            "community.post_created",
            self._forward_community_event
        )
        
        await self.event_bus.subscribe(
            "content.recommendation_updated",
            self._forward_content_event
        )
        
        logger.info("WebSocket-Event bridge initialized")
    
    async def _forward_mood_event(self, event):
        """Forward mood events to WebSocket clients"""
        await self.ws_manager.send_to_user(event.user_id, {
            "type": "mood_update",
            "source": "event_bus",
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _forward_ai_context_event(self, event):
        """Forward AI context updates to WebSocket clients"""
        await self.ws_manager.send_to_user(event.user_id, {
            "type": "ai_context_update",
            "source": "event_bus", 
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _forward_community_event(self, event):
        """Forward community events to relevant users"""
        # Send to all community service users
        await self.ws_manager.send_to_service_users("community", {
            "type": "community_update",
            "source": "event_bus",
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        })
    
    async def _forward_content_event(self, event):
        """Forward content events to WebSocket clients"""
        await self.ws_manager.send_to_user(event.user_id, {
            "type": "content_update",
            "source": "event_bus",
            "data": event.data,
            "timestamp": event.timestamp.isoformat()
        })

# Global bridge instance
websocket_event_bridge = WebSocketEventBridge()

# Initialize bridge when services start
async def initialize_websocket_event_bridge():
    await websocket_event_bridge.initialize()
```

---

## 4. Service Integration Testing

### 4.1 End-to-End Integration Tests

#### Task 4.1: Create Integration Test Suite (MEDIUM PRIORITY)
**Estimate**: 6 hours  
**Dependencies**: Tasks 1-3 completed  
**Risk**: Low

**Integration Test Structure**:
```python
# File: /backend/tests/integration/test_event_flow.py
import pytest
import asyncio
import json
from shared.events import get_enhanced_event_bus, V3EventChannels
from shared.websocket_manager import websocket_manager

class TestEventFlow:
    """Test end-to-end event flow between services"""
    
    async def test_mood_to_content_flow(self):
        """Test mood entry triggers content recommendation update"""
        
        # Setup event bus
        event_bus = get_enhanced_event_bus()
        await event_bus.initialize()
        
        # Track received events
        received_events = []
        
        @event_bus.subscribe(V3EventChannels.AI_CONTEXT_UPDATED)
        async def track_context_updates(event):
            received_events.append(event)
        
        # Simulate mood entry creation
        mood_data = {
            "mood_score": 3,  # Low mood
            "energy_level": 2,
            "stress_level": 8,
            "user_id": "test-user-123"
        }
        
        # Publish mood event
        await event_bus.publish(
            V3EventChannels.MOOD_ENTRY_CREATED,
            mood_data,
            "test-user-123"
        )
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        # Verify context was updated
        assert len(received_events) > 0
        context_event = received_events[0]
        assert context_event.user_id == "test-user-123"
        assert context_event.data["context_type"] == "mood"
    
    async def test_websocket_event_delivery(self):
        """Test events are delivered via WebSocket"""
        
        # Setup mock WebSocket connection
        # This would use a test WebSocket client
        
        # Publish event
        event_bus = get_enhanced_event_bus()
        await event_bus.publish(
            V3EventChannels.MOOD_ENTRY_CREATED,
            {"mood_score": 7, "user_id": "test-user-456"},
            "test-user-456"
        )
        
        # Verify WebSocket message delivery
        # Assert WebSocket received the event
    
    async def test_cross_service_context_sharing(self):
        """Test AI context is shared between services"""
        
        # Update context in mood service
        # Verify content service can access the context
        # Verify community service receives context updates
        pass

class TestPerformance:
    """Test performance under load"""
    
    async def test_event_throughput(self):
        """Test event processing throughput"""
        
        event_bus = get_enhanced_event_bus()
        await event_bus.initialize()
        
        # Publish 1000 events rapidly
        start_time = asyncio.get_event_loop().time()
        
        for i in range(1000):
            await event_bus.publish(
                "test.performance",
                {"event_number": i},
                f"user-{i % 100}"
            )
        
        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time
        
        # Should process 1000 events in under 1 second
        assert duration < 1.0
        
        # Check performance stats
        stats = event_bus.get_performance_stats()
        assert stats["total_events"] >= 1000
        assert stats["avg_latency_ms"] < 10  # Under 10ms average
```

#### Task 4.2: Create Service Health Monitoring (MEDIUM PRIORITY)
**Estimate**: 4 hours  
**Dependencies**: Tasks 1-3 completed  
**Risk**: Low

**Health Check Dashboard**:
```python
# File: /backend/monitoring/integration_health.py
from fastapi import FastAPI
from shared.events import get_enhanced_event_bus
from shared.websocket_manager import websocket_manager
import asyncio
import time

app = FastAPI(title="Integration Health Monitor")

@app.get("/health/integration")
async def get_integration_health():
    """Comprehensive integration health check"""
    
    health_status = {
        "timestamp": time.time(),
        "status": "healthy",
        "components": {}
    }
    
    # Check event bus health
    try:
        event_bus = get_enhanced_event_bus()
        bus_health = await event_bus.health_check()
        health_status["components"]["event_bus"] = bus_health
    except Exception as e:
        health_status["components"]["event_bus"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check WebSocket connections
    try:
        ws_stats = websocket_manager.get_connection_stats()
        health_status["components"]["websockets"] = {
            "status": "healthy",
            "stats": ws_stats
        }
    except Exception as e:
        health_status["components"]["websockets"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check service connectivity
    service_health = await check_service_connectivity()
    health_status["components"]["services"] = service_health
    
    if any(service["status"] != "healthy" for service in service_health.values()):
        health_status["status"] = "degraded"
    
    return health_status

async def check_service_connectivity():
    """Check if all services are responding"""
    services = {
        "mood_service": "http://localhost:8003/health",
        "content_service": "http://localhost:8005/health", 
        "community_service": "http://localhost:8004/health",
        "profile_service": "http://localhost:8002/health",
        "translation_service": "http://localhost:8005/health"
    }
    
    service_health = {}
    
    for service_name, health_url in services.items():
        try:
            # Make HTTP request to service health endpoint
            # This would use httpx or aiohttp
            service_health[service_name] = {"status": "healthy"}
        except Exception as e:
            service_health[service_name] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    return service_health

@app.get("/health/events/flow-test")
async def test_event_flow():
    """Test complete event flow between services"""
    
    test_user_id = f"health-check-{int(time.time())}"
    test_results = []
    
    try:
        event_bus = get_enhanced_event_bus()
        
        # Test mood event
        mood_success = await event_bus.publish(
            V3EventChannels.MOOD_ENTRY_CREATED,
            {"mood_score": 5, "test": True},
            test_user_id
        )
        test_results.append({
            "test": "mood_event_publish",
            "success": mood_success
        })
        
        # Test AI context event
        context_success = await event_bus.publish(
            V3EventChannels.AI_CONTEXT_UPDATED,
            {"context_type": "test", "test": True},
            test_user_id
        )
        test_results.append({
            "test": "ai_context_event_publish",
            "success": context_success
        })
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        return {
            "status": "completed",
            "test_user_id": test_user_id,
            "results": test_results,
            "all_passed": all(result["success"] for result in test_results)
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "results": test_results
        }
```

---

## 5. Implementation Timeline and Tracking

### 5.1 Implementation Phases

**Phase 1: Event Bus Activation** (2 days)
- [ ] Task 1.1: Activate Event Publishing in Services (4h)
- [ ] Task 1.2: Initialize Enhanced Event Bus in Services (2h) 
- [ ] Task 1.3: Add Event Subscriptions for Cross-Service Communication (6h)
- [ ] Verification: Event flow testing (2h)

**Phase 2: AI Context Implementation** (3 days)
- [ ] Task 2.1: Create AI Context Store Service (8h)
- [ ] Task 2.2: Integrate Context Store with Existing Services (6h)
- [ ] Task 2.3: Implement Context Query API (4h)
- [ ] Verification: Context sharing testing (6h)

**Phase 3: Real-time Infrastructure** (3 days)
- [ ] Task 3.1: Create Shared WebSocket Manager (6h)
- [ ] Task 3.2: Add WebSocket Support to Critical Services (8h)
- [ ] Task 3.3: Integrate WebSocket with Event Bus (4h)
- [ ] Verification: Real-time feature testing (6h)

**Phase 4: Integration and Testing** (2 days)
- [ ] Task 4.1: Create Integration Test Suite (6h)
- [ ] Task 4.2: Create Service Health Monitoring (4h)
- [ ] End-to-end testing and validation (6h)

**Total Estimated Time**: 10 days (80 hours)

### 5.2 Progress Tracking

#### Daily Checkpoints
```bash
# Day 1: Event Bus Activation
./scripts/test_event_bus_activation.sh
curl http://localhost:8000/health/event-bus

# Day 2-4: AI Context Implementation  
./scripts/test_context_sharing.sh
curl http://localhost:8007/context/test-user/summary

# Day 5-7: Real-time Infrastructure
./scripts/test_websocket_connectivity.sh
wscat -c ws://localhost:8003/ws/mood/test-user

# Day 8-10: Integration Testing
./scripts/test_end_to_end_flow.sh
```

#### Success Metrics
- [ ] **Event Bus**: 100% of services publishing events
- [ ] **Context Sharing**: <200ms context query response time
- [ ] **WebSocket**: Real-time updates delivered within 100ms
- [ ] **Integration**: All services communicating successfully

#### Risk Mitigation
- **High Risk**: NATS connectivity issues → Fallback to in-memory event bus
- **Medium Risk**: Context store performance → Implement Redis caching  
- **Low Risk**: WebSocket connection drops → Implement reconnection logic

### 5.3 Rollback Plan

If critical issues arise:
1. **Event Bus**: Revert to commented state, services work independently
2. **Context Store**: Fallback to individual service data stores
3. **WebSocket**: Disable real-time features, use polling
4. **Integration**: Run services in isolation mode

---

## 6. Post-Implementation Validation

### 6.1 Acceptance Criteria

**Event Bus Integration** ✅
- [ ] All 6 core services publishing events
- [ ] Event delivery success rate >99.5%
- [ ] Average event processing latency <50ms

**AI Context Sharing** ✅  
- [ ] Unified context available for all users
- [ ] Context updates propagated within 100ms
- [ ] Context query API response time <200ms

**Real-time Infrastructure** ✅
- [ ] WebSocket connections stable for >1 hour
- [ ] Real-time updates delivered to frontend
- [ ] Support for 100+ concurrent connections

**Service Integration** ✅
- [ ] All services communicating via events
- [ ] Cross-service data consistency maintained
- [ ] No regression in existing functionality

### 6.2 Ready for Sprint 2 Checklist

- [ ] Enhanced event bus activated and tested
- [ ] AI context store operational with caching
- [ ] WebSocket infrastructure deployed to critical services
- [ ] End-to-end event flow validated
- [ ] Performance monitoring in place
- [ ] Health checks passing for all components
- [ ] Integration test suite passing
- [ ] Documentation updated

**Sprint 2 Dependencies Met**:
- ✅ Event-driven architecture ready for AI Event Processing Pipeline
- ✅ Cross-service intelligence sharing infrastructure
- ✅ Real-time processing capabilities established
- ✅ Service communication patterns validated

---

## Conclusion

This implementation plan provides a clear roadmap to activate the missing critical components needed for Sprint 2. The enhanced event bus is already fully implemented and ready for activation. The main work involves uncommenting existing event publishing code, implementing the AI context store, and adding WebSocket infrastructure to critical services.

**Estimated Timeline**: 10 days  
**Resource Requirements**: 1-2 senior developers  
**Risk Level**: Medium (most components already exist)  
**Sprint 2 Readiness**: 100% achievable with this plan

The successful completion of this plan will enable the V3-BK-005 AI Event Processing Pipeline to build upon a solid, event-driven, real-time infrastructure with unified AI context sharing across all services.
