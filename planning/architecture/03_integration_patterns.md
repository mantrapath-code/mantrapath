# MantraPath Integration Patterns

This document outlines the key integration patterns between MantraPath services, focusing on how they communicate, share data, and collaborate to create a unified platform experience with the Mood Service as the central hub.

## 1. Event-Driven Communication

### 1.1 Platform Event Bus

The MantraPath platform uses a centralized event bus for asynchronous communication between services. This enables loose coupling while ensuring all services can react to relevant platform events.

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Mood Service   │  │ Chatbot Service│  │Community Service│  │ Journal Service│
└───────┬────────┘  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
        │                    │                   │                    │
        ▼                    ▼                   ▼                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                             PLATFORM EVENT BUS                            │
│                                                                           │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐        │
│   │  User Events    │   │ Content Events  │   │ System Events   │        │
│   └─────────────────┘   └─────────────────┘   └─────────────────┘        │
└──────────────────────────────────────────────────────────────────────────┘
```

#### Key Event Types

1. **User Events**
   - `UserInteracted` - User interaction with any service
   - `UserAuthenticated` - User login events
   - `UserProfileUpdated` - Profile changes
   - `UserPreferencesChanged` - Preference updates

2. **Content Events**
   - `ContentCreated` - New content creation
   - `ContentEngaged` - User engagement with content
   - `ContentAnalyzed` - Content analysis complete

3. **Mood Events**
   - `MoodRecorded` - Direct mood records
   - `MoodInferred` - Mood inferred from interaction
   - `MoodTrendDetected` - Significant mood patterns

4. **Service-Specific Events**
   - `ChatConversationCompleted` - Chatbot conversation
   - `JournalEntryCreated` - New journal entry
   - `CommunityPostCreated` - Community activity

### 1.2 Event Schema Example

```json
{
  "eventType": "MoodInferred",
  "version": "1.0",
  "timestamp": "2025-08-04T10:15:30Z",
  "userId": "user-123",
  "source": {
    "service": "ChatbotService",
    "context": "conversation-456"
  },
  "payload": {
    "moodState": {
      "valence": 0.75,
      "arousal": 0.3,
      "primaryEmotions": {
        "joy": 0.65,
        "contentment": 0.40,
        "hope": 0.55
      }
    },
    "confidence": 0.82,
    "triggers": [
      {
        "type": "conversation_theme",
        "value": "accomplishment"
      }
    ],
    "context": {
      "timeOfDay": "morning",
      "recentActivities": ["journal_writing", "community_browsing"]
    }
  },
  "metadata": {
    "processingPriority": "high",
    "correlationId": "corr-789"
  }
}
```

### 1.3 Event Processing

Each service implements event handlers for relevant events:

```python
class MoodServiceEventHandler:
    """
    Processes platform events in the Mood Service
    """
    
    async def handle_event(self, event: PlatformEvent) -> None:
        """
        Route event to appropriate handler
        """
        if event.type.startswith("User"):
            await self.handle_user_event(event)
        elif event.type.startswith("Content"):
            await self.handle_content_event(event)
        elif event.type.startswith("Chat"):
            await self.handle_chat_event(event)
        # ... other event types
    
    async def handle_chat_event(self, event: PlatformEvent) -> None:
        """
        Handle chatbot-related events
        """
        if event.type == "ChatConversationCompleted":
            await self.process_conversation_for_mood(event)
        elif event.type == "ChatBreakthroughDetected":
            await self.process_breakthrough(event)
```

## 2. Context Propagation

### 2.1 User Context Object

The Mood Service maintains a comprehensive user context that is shared across services to ensure consistent user experience.

```python
class UserContext:
    """
    Comprehensive user context shared across services
    """
    user_id: str
    timestamp: datetime
    
    # Emotional state
    emotional_state: EmotionalState
    emotional_trajectory: EmotionalTrajectory
    
    # Behavioral patterns
    interaction_patterns: InteractionPatterns
    engagement_trends: EngagementTrends
    
    # Social context
    social_connections: SocialConnections
    community_engagement: CommunityEngagement
    
    # Contextual factors
    temporal_patterns: TemporalPatterns
    environmental_factors: EnvironmentalFactors
    
    # Service-specific contexts
    chatbot_context: ChatbotContext
    journal_context: JournalContext
    community_context: CommunityContext
    
    # Personalization data
    preferences: UserPreferences
    intervention_history: InterventionHistory
    
    # Context metadata
    context_quality: float  # 0.0 to 1.0
    context_sources: List[ContextSource]
```

### 2.2 Context Propagation Flow

```
┌────────────────┐
│                │
│  Mood Service  │◄────────── Initial Context Request ─────────┐
│                │                                             │
└───────┬────────┘                                             │
        │                                                      │
        │ Context                                              │
        │ Response                                             │
        ▼                                                      │
┌────────────────┐         ┌────────────────┐         ┌───────┴────────┐
│                │         │                │         │                │
│ Chatbot Service│         │ Other Services │         │ Requesting     │
│                │         │                │         │ Service        │
└───────┬────────┘         └────────────────┘         └────────────────┘
        │                                                      ▲
        │ Context                                              │
        │ Updates                                              │
        ▼                                                      │
┌────────────────┐                                             │
│                │                                             │
│  Mood Service  │─────────── Updated Context ─────────────────┘
│                │
└────────────────┘
```

### 2.3 Context Request Example

```http
GET /api/v1/mood/context/user-123?minimal=false&include=emotional,social,preferences

HTTP/1.1 200 OK
Content-Type: application/json

{
  "userId": "user-123",
  "timestamp": "2025-08-04T10:20:45Z",
  "emotional": {
    "currentState": {
      "valence": 0.65,
      "arousal": 0.4,
      "primaryEmotions": {
        "joy": 0.7,
        "interest": 0.6
      }
    },
    "trajectory": {
      "trend": "improving",
      "volatility": 0.3,
      "recentStressors": ["work_deadline"]
    }
  },
  "social": {
    "connectionQuality": 0.75,
    "recentEngagements": [
      {
        "type": "community_post",
        "timestamp": "2025-08-03T14:30:00Z",
        "quality": 0.8
      }
    ],
    "supportNetwork": {
      "strength": 0.65,
      "diversity": 0.7
    }
  },
  "preferences": {
    "communicationStyle": "supportive",
    "contentTypes": ["practical", "science-backed"],
    "interventionPreferences": ["mindfulness", "cognitive"]
  },
  "metadata": {
    "contextQuality": 0.88,
    "sources": ["direct_mood_entry", "journal_analysis", "chat_inference"]
  }
}
```

## 3. Cross-Service Learning

### 3.1 Federated Insight Generation

Each service contributes insights to the central Mood Intelligence Engine, which aggregates and synthesizes them into a unified understanding of the user.

```
                    ┌─────────────────┐
                    │                 │
┌──────────┐        │ Mood Service    │        ┌──────────┐
│          │        │ (Intelligence   │        │          │
│ Chatbot  │───────►│  Engine)        │◄───────│ Journal  │
│ Service  │        │                 │        │ Service  │
│          │        └────────┬────────┘        │          │
└──────────┘                 │                 └──────────┘
                             │
                             │
                     ┌───────▼───────┐
                     │               │
                     │  ML Service   │
                     │               │
                     └───────┬───────┘
                             │
                             │
                    ┌────────▼────────┐
                    │                 │
                    │  Community      │
                    │  Service        │
                    │                 │
                    └─────────────────┘
```

### 3.2 Learning Examples

#### Chatbot → Mood → Community Flow

```python
# In Chatbot Service
async def process_conversation(self, conversation: Conversation) -> None:
    # Extract insights
    insights = await self.insight_extractor.extract(conversation)
    
    # Share with Mood Service
    await self.mood_service.update_from_chat_insights(
        user_id=conversation.user_id,
        insights=insights,
        conversation_context=conversation.context
    )
```

```python
# In Mood Service
async def update_from_chat_insights(self, user_id: str, insights: ChatInsights, 
                                  conversation_context: dict) -> None:
    # Update user context
    user_context = await self.context_repository.get(user_id)
    updated_context = await self.context_updater.apply_chat_insights(
        context=user_context,
        insights=insights
    )
    await self.context_repository.update(user_id, updated_context)
    
    # Generate community suggestions
    if insights.has_sharable_breakthroughs:
        community_suggestions = await self.community_suggestion_generator.generate(
            insights=insights,
            user_context=updated_context
        )
        
        # Share with Community Service
        await self.community_service.suggest_content(
            user_id=user_id,
            suggestions=community_suggestions,
            source_context={
                "service": "mood_service",
                "trigger": "chat_insights"
            }
        )
```

```python
# In Community Service
async def suggest_content(self, user_id: str, suggestions: ContentSuggestions, 
                        source_context: dict) -> None:
    # Store suggestions for user
    await self.suggestion_repository.store(user_id, suggestions)
    
    # Notify user if appropriate
    if await self.should_notify_user(user_id, suggestions, source_context):
        await self.notification_service.notify(
            user_id=user_id,
            notification_type="content_suggestion",
            content=await self.format_suggestions_for_notification(suggestions)
        )
    
    # Learn from this interaction
    await self.suggestion_learner.learn(
        user_id=user_id,
        suggestions=suggestions,
        source_context=source_context
    )
```

## 4. API-Based Integration

### 4.1 RESTful API Standards

All services expose RESTful APIs for synchronous communication following these standards:

- **URL Structure**: `/api/v1/{service}/{resource}/{id?}`
- **Authentication**: JWT-based with service-to-service credentials
- **Request/Response Format**: JSON
- **Status Codes**: Standard HTTP status codes
- **Error Format**: Consistent error schema
- **Versioning**: URL-based versioning
- **Documentation**: OpenAPI specifications

### 4.2 Core API Endpoints

#### Mood Service Core APIs

```
GET    /api/v1/mood/context/{userId}        # Get user context
PATCH  /api/v1/mood/context/{userId}        # Update user context
POST   /api/v1/mood/entries                 # Record direct mood entry
GET    /api/v1/mood/analysis/{userId}       # Get mood analysis
POST   /api/v1/mood/predictions/{userId}    # Generate mood predictions
GET    /api/v1/mood/recommendations/{userId} # Get recommendations
```

#### Chatbot Service Core APIs

```
POST   /api/v1/chat/conversations           # Start conversation
POST   /api/v1/chat/messages                # Send message
GET    /api/v1/chat/history/{userId}        # Get conversation history
POST   /api/v1/chat/analyze                 # Analyze conversation
POST   /api/v1/chat/generate/content        # Generate content
```

#### Community Service Core APIs

```
GET    /api/v1/community/matches/{userId}   # Get user matches
POST   /api/v1/community/posts              # Create post
GET    /api/v1/community/feed/{userId}      # Get personalized feed
POST   /api/v1/community/challenges         # Create challenge
GET    /api/v1/community/events             # Get upcoming events
```

### 4.3 API Request/Response Example

Request:
```http
POST /api/v1/mood/context/updates HTTP/1.1
Host: mood-service.mantrapath.com
Authorization: Bearer eyJhbGc...
Content-Type: application/json

{
  "userId": "user-123",
  "source": {
    "service": "journal_service",
    "contextId": "entry-456"
  },
  "updates": [
    {
      "path": "emotional_state.primary_emotions",
      "value": {
        "gratitude": 0.75,
        "contentment": 0.65,
        "hope": 0.55
      },
      "confidence": 0.85,
      "operation": "merge"
    },
    {
      "path": "emotional_trajectory.trend",
      "value": "improving",
      "confidence": 0.7,
      "operation": "replace"
    }
  ],
  "metadata": {
    "timestamp": "2025-08-04T15:30:22Z",
    "analysisQuality": 0.82
  }
}
```

Response:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "updatedContext": {
    "userId": "user-123",
    "timestamp": "2025-08-04T15:30:25Z",
    "emotional": {
      "currentState": {
        "valence": 0.7,
        "arousal": 0.4,
        "primaryEmotions": {
          "gratitude": 0.75,
          "contentment": 0.65,
          "hope": 0.55,
          "joy": 0.4
        }
      },
      "trajectory": {
        "trend": "improving",
        "volatility": 0.25
      }
    },
    "metadata": {
      "contextQuality": 0.85,
      "lastUpdateSource": "journal_service"
    }
  },
  "adaptations": [
    {
      "service": "chatbot",
      "type": "tone_adjustment",
      "parameters": {
        "primary_tone": "encouraging",
        "focus_areas": ["gratitude_reinforcement"]
      }
    },
    {
      "service": "community",
      "type": "content_suggestion",
      "parameters": {
        "content_types": ["gratitude_practices", "positive_reflection"],
        "suggestion_strength": "subtle"
      }
    }
  ]
}
```

## 5. Database Integration Patterns

### 5.1 Service-Specific Databases

Each service maintains its own database for service-specific data, but shared data models ensure consistency across services.

```
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Mood Service   │  │ Chatbot Service│  │Community Service│  │ Journal Service│
└───────┬────────┘  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘
        │                    │                   │                    │
        ▼                    ▼                   ▼                    ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Mood DB        │  │ Chatbot DB     │  │ Community DB   │  │ Journal DB     │
└────────────────┘  └────────────────┘  └────────────────┘  └────────────────┘
```

### 5.2 Data Synchronization

For necessary cross-service data, the platform uses these synchronization patterns:

1. **Event-Based Synchronization**: Services publish data change events that are consumed by interested services
2. **API-Based Fetching**: Services request data from other services' APIs as needed
3. **Background Synchronization**: Scheduled jobs ensure data consistency across services

### 5.3 Shared Data Models

Key data models are standardized across services:

```python
# Shared user model across services
class SharedUser:
    id: str
    display_name: str
    created_at: datetime
    preferences: Dict[str, Any]
    privacy_settings: PrivacySettings

# Shared mood state model
class SharedMoodState:
    valence: float  # -1.0 to 1.0
    arousal: float  # -1.0 to 1.0
    primary_emotions: Dict[str, float]
    confidence: float
    timestamp: datetime
    source: str
```

## 6. Real-Time Integration

### 6.1 WebSocket Communication

For real-time interactions, the platform uses WebSockets for bidirectional communication.

```
       WebSocket Connection
┌──────────────────────────────┐
│                              │
│  Client                      │
│  (Browser/Mobile App)        │
│                              │
└──────────────┬───────────────┘
               │
               │
┌──────────────▼───────────────┐
│                              │
│  API Gateway                 │
│  (WebSocket Manager)         │
│                              │
└──────────────┬───────────────┘
               │
               │
┌──────────────▼───────────────┐
│                              │
│  Real-Time Event Processor   │
│                              │
└───┬─────────┬─────────┬──────┘
    │         │         │
    ▼         ▼         ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│         │ │         │ │         │
│ Chatbot │ │  Mood   │ │ Other   │
│ Service │ │ Service │ │ Services│
│         │ │         │ │         │
└─────────┘ └─────────┘ └─────────┘
```

### 6.2 Real-Time Event Types

1. **User Interaction Events**:
   - `message_received` - New chat message
   - `typing_indicator` - User typing
   - `content_viewed` - Content being viewed

2. **Service Response Events**:
   - `message_response` - Chat response
   - `context_changed` - User context updated
   - `recommendation_available` - New recommendation

3. **State Synchronization Events**:
   - `mood_updated` - Mood state changed
   - `profile_updated` - Profile changes
   - `preferences_changed` - Preference updates

### 6.3 WebSocket Message Example

```json
{
  "type": "message_response",
  "timestamp": "2025-08-04T16:45:12Z",
  "payload": {
    "conversationId": "conv-789",
    "message": {
      "id": "msg-456",
      "text": "It sounds like you've made great progress with your mindfulness practice. How has this affected your stress levels?",
      "responseType": "follow_up",
      "sentiment": "supportive",
      "suggestions": [
        {
          "type": "journal_prompt",
          "text": "Reflect on how mindfulness has changed your response to stressful situations"
        },
        {
          "type": "community_challenge",
          "text": "7-Day Mindfulness Streak"
        }
      ]
    },
    "context": {
      "emotionalState": {
        "primary": "proud",
        "secondary": "hopeful"
      },
      "conversationFocus": "mindfulness_practice"
    }
  }
}
```

## 7. Security Integration Patterns

### 7.1 Authentication & Authorization Flow

```
┌──────────────┐     ┌─────────────┐     ┌────────────────┐
│              │     │             │     │                │
│   Client     │────►│ Auth Service│────►│ Token Issuer   │
│              │     │             │     │                │
└──────────────┘     └─────────────┘     └────────┬───────┘
                                                   │
                                                   │ JWT
                                                   ▼
                        ┌─────────────────────────────────┐
                        │                                 │
                        │       API Gateway               │
                        │                                 │
                        └─────┬──────────────────┬────────┘
                              │                  │
                              │                  │
                              ▼                  ▼
                      ┌──────────────┐    ┌────────────┐
                      │              │    │            │
                      │ Service A    │    │ Service B  │
                      │              │    │            │
                      └──────────────┘    └────────────┘
```

### 7.2 Service-to-Service Authentication

For service-to-service communication, the platform uses:

1. **Service Accounts**: Each service has its own identity
2. **JWT-Based Authentication**: Services authenticate with JWTs
3. **Scope-Limited Tokens**: Tokens are limited to specific operations
4. **Short Expiration**: Service tokens expire quickly
5. **Token Rotation**: Regular credential rotation

### 7.3 Security Event Propagation

Security-relevant events are propagated across services:

```python
class SecurityEventManager:
    """
    Manages security events across services
    """
    
    async def propagate_security_event(self, event: SecurityEvent) -> None:
        """
        Propagates security event to all services
        """
        # Log security event
        await self.security_logger.log(event)
        
        # Publish to event bus
        await self.event_bus.publish("security.events", event)
        
        # Take immediate actions
        if event.severity >= SecuritySeverity.HIGH:
            await self.take_immediate_actions(event)
    
    async def take_immediate_actions(self, event: SecurityEvent) -> None:
        """
        Takes immediate actions for high-severity events
        """
        if event.type == SecurityEventType.ACCOUNT_COMPROMISED:
            # Invalidate all sessions
            await self.session_manager.invalidate_all(event.user_id)
            
            # Notify user through alternate channels
            await self.notification_service.send_security_alert(event.user_id)
            
            # Restrict sensitive operations
            await self.restriction_manager.apply_restrictions(event.user_id)
```

## 8. Deployment Integration

### 8.1 Container Orchestration

Services are deployed as containers orchestrated by Kubernetes:

```yaml
# mood-service.yaml example
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mood-service
  namespace: mantrapath
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mood-service
  template:
    metadata:
      labels:
        app: mood-service
    spec:
      containers:
      - name: mood-service
        image: mantrapath/mood-service:latest
        ports:
        - containerPort: 8003
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mood-service-secrets
              key: database-url
        - name: EVENT_BUS_URL
          valueFrom:
            configMapKeyRef:
              name: platform-config
              key: event-bus-url
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
          requests:
            cpu: "500m"
            memory: "512Mi"
```

### 8.2 Service Discovery

Services discover each other through Kubernetes service discovery:

```yaml
# mood-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mood-service
  namespace: mantrapath
spec:
  selector:
    app: mood-service
  ports:
  - port: 80
    targetPort: 8003
  type: ClusterIP
```

### 8.3 Deployment Pipeline Integration

All services share a consistent CI/CD pipeline:

1. **Build Phase**:
   - Source code checkout
   - Dependency installation
   - Unit testing
   - Static analysis
   - Container building

2. **Test Phase**:
   - Integration testing
   - API contract testing
   - Security scanning
   - Performance testing

3. **Deployment Phase**:
   - Canary deployment
   - Progressive rollout
   - Health monitoring
   - Automated rollback

## 9. Cross-Service Testing & Monitoring

### 9.1 Integration Testing

Services are tested together to ensure proper integration:

```python
class MoodChatbotIntegrationTest:
    """
    Tests integration between Mood and Chatbot services
    """
    
    async def test_mood_affects_chatbot_response(self):
        # Set up test user
        user_id = await self.create_test_user()
        
        # Record specific mood
        await self.mood_service.record_mood(
            user_id=user_id,
            mood_state={
                "valence": -0.5,
                "arousal": 0.7,
                "primary_emotions": {
                    "anxiety": 0.8,
                    "worry": 0.7
                }
            }
        )
        
        # Send message to chatbot
        response = await self.chatbot_service.send_message(
            user_id=user_id,
            message="I'm thinking about my presentation tomorrow"
        )
        
        # Verify response is appropriate for anxious mood
        assert "anxiety" in response.detected_emotions
        assert response.tone in ["calming", "reassuring", "supportive"]
        assert any(suggestion.type == "anxiety_reduction" for suggestion in response.suggestions)
```

### 9.2 Distributed Tracing

Requests are traced across services to monitor performance and troubleshoot issues:

```
┌──────────────┐
│              │
│   Client     │
│              │
└──────┬───────┘
       │
       │ Request (trace_id=abc-123)
       ▼
┌──────────────┐
│              │
│ API Gateway  │
│              │
└──────┬───────┘
       │
       │ Forward (trace_id=abc-123, span_id=1)
       ▼
┌──────────────┐         ┌──────────────┐
│              │         │              │
│ Mood Service │────────►│ ML Service   │
│              │         │              │
└──────┬───────┘         └──────┬───────┘
       │ span_id=2              │ span_id=3
       │                        │
       │                        │
       ▼                        ▼
┌─────────────────────────────────────────┐
│                                         │
│           Tracing System                │
│                                         │
└─────────────────────────────────────────┘
```

### 9.3 Health Monitoring

Services report health and metrics for platform-wide monitoring:

```python
class HealthReporter:
    """
    Reports service health metrics
    """
    
    async def report_health(self):
        # Collect health metrics
        metrics = {
            "service": self.service_name,
            "version": self.service_version,
            "status": "healthy" if self.is_healthy() else "unhealthy",
            "indicators": {
                "cpu_usage": await self.get_cpu_usage(),
                "memory_usage": await self.get_memory_usage(),
                "request_latency": await self.get_average_latency(),
                "error_rate": await self.get_error_rate(),
                "database_connection": await self.check_database_connection(),
                "dependencies": await self.check_dependencies()
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Report to monitoring system
        await self.monitoring_client.report_health(metrics)
        
        # Publish health event
        await self.event_bus.publish(
            "system.health",
            {
                "service": self.service_name,
                "status": metrics["status"],
                "timestamp": metrics["timestamp"]
            }
        )
```

## 10. Integration Optimization Patterns

### 10.1 Request Batching

Services batch requests to reduce network overhead:

```python
class UserContextBatchFetcher:
    """
    Batches user context requests
    """
    
    async def get_contexts(self, user_ids: List[str]) -> Dict[str, UserContext]:
        # Split into batches
        batches = self.split_into_batches(user_ids, batch_size=50)
        
        # Process batches
        results = {}
        for batch in batches:
            batch_results = await self.mood_service.get_contexts_batch(batch)
            results.update(batch_results)
        
        return results
```

### 10.2 Data Caching

Frequently used data is cached to reduce service calls:

```python
class UserContextCache:
    """
    Caches user contexts
    """
    
    async def get_context(self, user_id: str) -> UserContext:
        # Check cache
        cached = await self.cache.get(f"user_context:{user_id}")
        if cached and not self.is_stale(cached):
            return cached
        
        # Fetch from service
        context = await self.mood_service.get_context(user_id)
        
        # Cache with TTL
        await self.cache.set(
            key=f"user_context:{user_id}",
            value=context,
            ttl=self.calculate_ttl(context)
        )
        
        return context
    
    def calculate_ttl(self, context: UserContext) -> int:
        """
        Calculates cache TTL based on context volatility
        """
        if context.emotional_state.volatility > 0.7:
            return 60  # 1 minute for volatile contexts
        elif context.emotional_state.volatility > 0.3:
            return 300  # 5 minutes for moderately volatile contexts
        else:
            return 900  # 15 minutes for stable contexts
```

### 10.3 Circuit Breaking

Services implement circuit breakers to handle dependency failures:

```python
class MoodServiceClient:
    """
    Client for Mood Service with circuit breaker
    """
    
    async def get_context(self, user_id: str) -> UserContext:
        # Check circuit state
        if self.circuit_breaker.is_open:
            # Return fallback data
            return await self.get_fallback_context(user_id)
        
        try:
            # Make request
            response = await self.http_client.get(f"/api/v1/mood/context/{user_id}")
            
            # Reset circuit on success
            self.circuit_breaker.success()
            
            return response.data
        except Exception as e:
            # Record failure
            self.circuit_breaker.failure()
            
            # Log error
            await self.logger.error(f"Mood service request failed: {str(e)}")
            
            # Return fallback if circuit still closed
            if not self.circuit_breaker.is_open:
                return await self.get_fallback_context(user_id)
            
            # Rethrow if circuit now open
            raise
```

## 11. Implementation Roadmap

The integration patterns will be implemented in phases:

### Phase 1: Core Integration Framework
- Establish event bus infrastructure
- Implement basic context sharing
- Set up service authentication

### Phase 2: Mood-Chatbot Integration
- Implement mood-aware chatbot responses
- Establish chatbot-to-mood learning
- Create content generation pipeline

### Phase 3: Journal-Mood Integration
- Implement journal analysis pipeline
- Create bidirectional mood-journal updates
- Establish writing assistance based on mood

### Phase 4: Community Integration
- Implement mood-based community matching
- Create cross-service challenge system
- Establish community-to-mood learning

### Phase 5: Advanced Cross-Service Features
- Implement predictive capabilities
- Create advanced personalization
- Establish platform-wide adaptation system
