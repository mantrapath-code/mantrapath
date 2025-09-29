# MantraPath Memory Service 🧠

## Overview

The **MantraPath Memory Service** is a sophisticated behavioral analytics and user interaction tracking microservice that forms the cognitive foundation of the MantraPath wellness platform. It serves as the central memory system, capturing, analyzing, and synthesizing user interactions across all platform services to generate actionable behavioral insights and mood patterns.

### Key Capabilities

- 🧠 **User Interaction Tracking** - Comprehensive recording of all user activities across services
- 📊 **Behavioral Pattern Analysis** - Advanced mood and activity pattern detection
- 💡 **Insight Generation** - AI-powered behavioral insights and recommendations  
- 🔄 **Real-time Event Processing** - Live event stream processing via NATS JetStream
- 📈 **Statistical Aggregation** - Performance-optimized data aggregation and caching
- 🌍 **Cultural Context Integration** - Culturally-aware analysis and recommendations
- ⚡ **Cross-Platform Memory** - Unified memory across web, mobile, and voice interfaces

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Platform Services                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Mood      │  │  Chatbot    │  │     Community           │ │
│  │  Service    │  │  Service    │  │     Service             │ │
│  │ (Port 8003) │  │ (Port 8004) │  │   (Port 8006)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Voice     │  │   Media     │  │    Translation          │ │
│  │  Service    │  │  Service    │  │     Service             │ │
│  │ (Port 8011) │  │ (Port 8021) │  │   (Port 8005)          │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ Events & API Calls
┌─────────────────────────────────────────────────────────────────┐
│                  Memory Service (Port 8017)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Event     │  │   Memory    │  │    Pattern              │ │
│  │  Handler    │  │   Engine    │  │    Analysis             │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Insight    │  │   Redis     │  │   PostgreSQL            │ │
│  │ Generator   │  │  Cache      │  │   Database              │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Persistence                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │User         │  │   Mood      │  │   Behavioral            │ │
│  │Interactions │  │  Patterns   │  │   Insights              │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Memory     │  │ Aggregated  │  │     NATS                │ │
│  │ Sessions    │  │ Statistics  │  │   JetStream             │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
memory_service/
├── main.py                            # FastAPI application entry point (522 lines)
├── main_full.py                       # Comprehensive implementation (backup)
├── events.py                          # NATS JetStream event integration (328 lines)
├── models.py                          # Legacy model definitions
├── test_memory_service.py             # Integration tests (comprehensive)
├── requirements.txt                   # Python dependencies (46 lines)
├── Dockerfile                         # Container configuration (Port 8017)
├── __init__.py                        # Package initialization
├── api/                              # API endpoint modules
│   ├── __init__.py
│   ├── interactions.py               # User interaction CRUD API (388 lines)
│   ├── patterns.py                   # Pattern analysis API (549 lines)
│   └── insights.py                   # Behavioral insights API (559 lines)
├── services/                         # Core business logic services
│   ├── __init__.py
│   ├── memory_engine.py              # Core memory processing engine (897 lines)
│   └── event_handler.py              # Real-time event processing (596 lines)
├── models/                           # Data models and schemas
│   ├── __init__.py
│   └── memory_models.py              # SQLAlchemy database models (243 lines)
└── tests/                            # Test suites
    ├── conftest.py                   # Test configuration
    └── test_memory_api.py            # API endpoint tests (250 lines)
```

## API Endpoints

### Health & Status Monitoring

#### GET `/`
**Service Root Information**
```json
Response:
{
  "message": "Memory Service - Running",
  "version": "1.0.0",
  "service": "memory_service",
  "port": 8017,
  "status": "operational"
}
```

#### GET `/health`
**Basic Health Check**
```json
Response:
{
  "status": "healthy",
  "service": "memory_service",
  "timestamp": "2025-09-27T14:30:00Z"
}
```

#### GET `/health/live`
**Kubernetes Liveness Probe**
```json
Response:
{
  "status": "alive",
  "service": "memory_service",
  "version": "1.0.0",
  "timestamp": "2025-09-27T14:30:00Z"
}
```

#### GET `/health/ready`
**Kubernetes Readiness Probe with Dependency Checks**
```json
Response:
{
  "status": "ready",
  "service": "memory_service",
  "checks": {
    "memory_engine": "healthy",
    "event_handler": "healthy",
    "database": "connected",
    "redis": "connected",
    "nats": "connected"
  },
  "overall_status": "ready",
  "timestamp": "2025-09-27T14:30:00Z"
}
```

### User Interaction Management

#### POST `/api/v1/interactions`
**Record New User Interaction**
```json
Request:
{
  "user_id": "user_123",
  "interaction_type": "mood",
  "content": "Feeling peaceful after meditation",
  "metadata": {
    "mood_score": 8.5,
    "activity": "meditation",
    "duration_minutes": 15
  }
}

Response:
{
  "success": true,
  "data": {
    "id": "interaction_456",
    "user_id": "user_123",
    "interaction_type": "mood",
    "processed": true,
    "timestamp": "2025-09-27T14:30:00Z"
  }
}
```

#### GET `/api/v1/interactions`
**Retrieve User Interactions with Filtering**
```json
Query Parameters:
- user_id: str (required)
- interaction_type: str (optional)
- start_date: datetime (optional)
- end_date: datetime (optional)
- limit: int = 50 (max 1000)
- offset: int = 0

Response:
{
  "success": true,
  "data": [
    {
      "id": "interaction_456",
      "user_id": "user_123",
      "interaction_type": "mood",
      "interaction_data": {...},
      "source_service": "mood_service",
      "timestamp": "2025-09-27T14:30:00Z",
      "processing_time_ms": 45.2,
      "confidence_score": 0.89
    }
  ],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

### Behavioral Pattern Analysis

#### POST `/api/v1/patterns/analyze`
**Trigger Pattern Analysis for User**
```json
Request:
{
  "user_id": "user_123",
  "timeframe_days": 30,
  "pattern_types": ["daily", "weekly", "trend"],
  "force_refresh": false
}

Response:
{
  "success": true,
  "data": {
    "analysis_id": "analysis_789",
    "patterns_found": 5,
    "confidence_scores": [0.89, 0.92, 0.76, 0.84, 0.91],
    "processing_time_ms": 1250.5
  }
}
```

#### GET `/api/v1/patterns/{user_id}`
**Get User Behavioral Patterns**
```json
Response:
{
  "success": true,
  "data": {
    "mood_patterns": [
      {
        "pattern_type": "daily",
        "description": "Higher mood scores in morning hours",
        "confidence": 0.89,
        "frequency": "daily",
        "intensity": 0.75,
        "stability": 0.82,
        "triggers": ["meditation", "exercise"],
        "time_range": {
          "start": "2025-08-28T00:00:00Z",
          "end": "2025-09-27T23:59:59Z"
        }
      }
    ],
    "activity_patterns": {
      "most_active_hours": [7, 12, 19],
      "preferred_interaction_types": ["chatbot", "mood_tracking", "meditation"],
      "engagement_trend": "increasing",
      "weekly_consistency": 0.78
    },
    "cultural_context": {
      "timezone": "Asia/Kolkata",
      "language_preference": "hi-IN",
      "cultural_holidays_impact": true
    }
  }
}
```

### Behavioral Insights Generation

#### POST `/api/v1/insights/generate`
**Generate Behavioral Insights**
```json
Request:
{
  "user_id": "user_123",
  "insight_types": ["mood_trends", "activity_recommendations", "wellbeing_alerts"],
  "force_refresh": false,
  "priority_filter": "high"
}

Response:
{
  "success": true,
  "data": {
    "insights": [
      {
        "id": "insight_101",
        "type": "mood_trend",
        "title": "Consistent Morning Mood Improvement",
        "description": "Your mood consistently improves by 15% after morning meditation sessions",
        "recommendation": "Consider extending morning meditation from 10 to 15 minutes",
        "confidence": 0.89,
        "urgency": "medium",
        "action_items": [
          "Schedule 15-minute morning meditation",
          "Track mood before and after sessions"
        ]
      }
    ],
    "summary": {
      "total_insights": 3,
      "high_priority": 1,
      "actionable": 2
    }
  }
}
```

#### GET `/api/v1/insights/{user_id}`
**Get User Behavioral Insights**
```json
Query Parameters:
- status: str = "active" (active|delivered|acknowledged)
- urgency_level: str = "all" (low|medium|high|critical)
- limit: int = 20

Response:
{
  "success": true,
  "data": [
    {
      "id": "insight_101",
      "insight_type": "wellbeing_alert",
      "title": "Declining Evening Mood Pattern Detected",
      "description": "Your evening mood has decreased by 20% over the past week",
      "accuracy_score": 0.87,
      "relevance_score": 0.93,
      "urgency_level": "high",
      "priority": 8,
      "recommendation": "Consider evening relaxation activities or earlier sleep schedule",
      "action_items": {
        "immediate": ["Practice evening breathing exercise"],
        "short_term": ["Establish consistent sleep schedule"],
        "long_term": ["Evaluate evening routine effectiveness"]
      },
      "generated_at": "2025-09-27T14:30:00Z",
      "expires_at": "2025-10-04T14:30:00Z",
      "status": "active"
    }
  ]
}
```

### Aggregated Data & Statistics

#### GET `/api/v1/aggregation/{user_id}`
**Get User Data Aggregation**
```json
Response:
{
  "success": true,
  "data": {
    "user_id": "user_123",
    "summary_stats": {
      "total_interactions": 1250,
      "active_days": 28,
      "average_mood_score": 7.4,
      "engagement_score": 0.89,
      "consistency_score": 0.76
    },
    "trend_analysis": {
      "mood_trend": "improving",
      "activity_trend": "stable",
      "engagement_trend": "increasing"
    },
    "period": {
      "start_date": "2025-08-28T00:00:00Z",
      "end_date": "2025-09-27T23:59:59Z",
      "days_analyzed": 30
    },
    "cultural_insights": {
      "timezone_adaptation": true,
      "cultural_events_impact": ["Diwali", "Weekend_patterns"],
      "language_coherence": 0.95
    },
    "profile_completeness": 0.85
  }
}
```

#### GET `/api/v1/stats`
**Service Statistics & Performance Metrics**
```json
Response:
{
  "service": {
    "name": "memory_service",
    "version": "1.0.0",
    "uptime": "operational",
    "status": "healthy"
  },
  "memory_engine": {
    "interactions_processed": 15420,
    "patterns_analyzed": 234,
    "insights_generated": 89,
    "sessions_created": 156,
    "aggregations_computed": 67
  },
  "event_handler": {
    "events_processed": 8950,
    "events_failed": 12,
    "last_event_time": "2025-09-27T14:29:45Z",
    "events_per_minute": 2.3
  },
  "performance": {
    "cache_hit_ratio": 0.85,
    "avg_response_time_ms": 120,
    "active_sessions": 15,
    "database_connections": 8
  },
  "timestamp": "2025-09-27T14:30:00Z"
}
```

### Service Integration Endpoints

#### POST `/api/v1/integrations/chatbot`
**Chatbot Service Integration**
```json
Request:
{
  "user_id": "user_123",
  "conversation_data": {
    "message": "I'm feeling anxious today",
    "bot_response": "I understand you're feeling anxious. Would you like to try a breathing exercise?",
    "sentiment_score": -0.3,
    "session_id": "chat_session_456"
  }
}

Response:
{
  "success": true,
  "data": {
    "status": "processed",
    "event_id": "evt_789",
    "interaction_recorded": true,
    "pattern_updated": true
  }
}
```

#### POST `/api/v1/integrations/mood`
**Mood Service Integration**
```json
Request:
{
  "user_id": "user_123",
  "mood_data": {
    "mood_score": 8.5,
    "energy_level": 7.2,
    "activity": "meditation",
    "duration_minutes": 20,
    "location": "home"
  }
}

Response:
{
  "success": true,
  "data": {
    "status": "processed",
    "event_id": "evt_790",
    "pattern_analysis_triggered": true,
    "insight_generation_queued": true
  }
}
```

## Port Configuration

### Service Port Details
- **Primary Port**: **8017** (Standardized across all environments)
- **Health Check Port**: Same as primary (8017)
- **Internal Communication**: Port 8017 for container-to-container communication
- **External Access**: Via API Gateway (Port 8000) with routing to `/memory/*`

### Environment Configuration
```bash
# Service Configuration
MEMORY_SERVICE_PORT=8017
MEMORY_SERVICE_HOST=0.0.0.0
ENVIRONMENT=development  # development|staging|production
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://user:pass@postgres:5432/mantrapath
REDIS_URL=redis://redis:6379

# Event System Configuration  
NATS_URL=nats://nats:4222
JETSTREAM_ENABLED=true

# Memory Engine Configuration
PATTERN_ANALYSIS_WINDOW_DAYS=30
INSIGHT_GENERATION_THRESHOLD=10
CACHE_TTL_SECONDS=3600
BATCH_SIZE=100
MAX_PATTERNS_PER_USER=50

# Cultural Configuration
CULTURAL_ADAPTATION_ENABLED=true
SUPPORTED_TIMEZONES=Asia/Kolkata,America/New_York,Europe/London
SUPPORTED_LANGUAGES=en,hi,bn,te,ta

# Performance Configuration
MAX_CONCURRENT_REQUESTS=50
REQUEST_TIMEOUT_SECONDS=30
DATABASE_POOL_SIZE=10
REDIS_POOL_SIZE=5
```

## Request Flow

### Interaction Recording Flow
```mermaid
sequenceDiagram
    participant Service as Source Service
    participant Gateway as API Gateway  
    participant Memory as Memory Service
    participant Engine as Memory Engine
    participant DB as PostgreSQL
    participant Cache as Redis
    participant Events as NATS JetStream

    Service->>Gateway: POST /memory/interactions
    Gateway->>Memory: Route to Memory Service
    Memory->>Memory: Validate request & auth
    
    Memory->>Engine: Process interaction
    Engine->>DB: Store interaction record
    Engine->>Cache: Update user cache
    Engine->>Events: Publish interaction event
    
    alt Pattern Analysis Trigger
        Engine->>Engine: Analyze patterns (async)
        Engine->>DB: Update/create patterns
        Engine->>Cache: Cache pattern results
    end
    
    alt Insight Generation Trigger  
        Engine->>Engine: Generate insights (async)
        Engine->>DB: Store insights
        Engine->>Events: Publish insight events
    end
    
    Memory-->>Gateway: Interaction recorded
    Gateway-->>Service: Success response
```

### Pattern Analysis Flow
```mermaid
sequenceDiagram
    participant Client as Client Application
    participant Memory as Memory Service
    participant Engine as Memory Engine
    participant Analyzer as Pattern Analyzer
    participant DB as PostgreSQL
    participant Cache as Redis

    Client->>Memory: POST /patterns/analyze
    Memory->>Engine: Trigger pattern analysis
    
    Engine->>Cache: Check cached patterns
    alt Cache Miss
        Engine->>DB: Fetch user interactions
        Engine->>Analyzer: Analyze behavioral patterns
        Analyzer->>Analyzer: Detect mood patterns
        Analyzer->>Analyzer: Identify activity patterns
        Analyzer->>Analyzer: Calculate confidence scores
        
        Analyzer->>DB: Store pattern results
        Analyzer->>Cache: Cache pattern data
    else Cache Hit
        Engine->>Cache: Return cached patterns
    end
    
    Engine-->>Memory: Pattern analysis complete
    Memory-->>Client: Analysis results
```

## Service Communication

### Internal Service Dependencies

#### Database Integration
```python
# PostgreSQL Database Schema
Primary Tables:
├── user_interactions        # All user activity records (main table)
├── mood_patterns           # Detected behavioral patterns  
├── behavioral_insights     # Generated recommendations
├── memory_sessions        # User session tracking
└── memory_aggregations    # Pre-computed statistics

# Performance Indexes
Optimized for:
├── User-based queries (user_id + timestamp)
├── Pattern analysis (interaction_type + date range)
├── Real-time lookups (session_id, active patterns)
└── Statistical aggregation (time-based grouping)
```

#### Event Bus Integration
```python
# NATS JetStream Event Processing
Subscribed Events:
├── "mood.entry_created" → Record mood interaction
├── "journal.entry_created" → Process journal content
├── "chat.message_sent" → Analyze conversation patterns
├── "community.post_created" → Track social engagement
├── "voice.command_processed" → Voice interaction patterns
├── "user.session_started" → Session tracking
└── "notification.delivered" → Engagement measurement

Published Events:
├── "memory.pattern_detected" → New pattern identified
├── "memory.insight_generated" → New insight available
├── "memory.anomaly_detected" → Unusual behavior pattern
└── "memory.aggregation_updated" → Statistics refreshed
```

#### Cache Layer Integration
```python
# Redis Caching Strategy
Cache Keys:
├── "interactions:{user_id}:{type}:{date}" → Recent interactions
├── "patterns:{user_id}:{type}" → User behavior patterns
├── "insights:{user_id}:active" → Active insights
├── "stats:{user_id}:daily" → Daily aggregated statistics
└── "sessions:{session_id}" → Session context data

# TTL Configuration
Cache Lifetimes:
├── Interactions: 1 hour (frequently accessed)
├── Patterns: 4 hours (moderate updates)
├── Insights: 8 hours (slower updates)
└── Statistics: 24 hours (daily refresh)
```

### External Service Integration

#### API Gateway Integration (Port 8000)
```python
# Route Registration in API Gateway
Routes:
├── /memory/* → memory-service:8017/*
├── Health checks via /health/live
├── Metrics collection and aggregation
└── Authentication token validation

# Load Balancing & Failover
Configuration:
├── Round-robin request distribution
├── Health-based routing decisions
├── Circuit breaker for failure handling
└── Request timeout management (30s)
```

#### Cross-Service Communication
```python
# Service Integration Patterns
Chatbot Service (Port 8004):
├── Receives conversation events via NATS
├── Analyzes sentiment and engagement patterns
├── Generates conversation-based insights
└── Triggers mood pattern updates

Mood Service (Port 8003):
├── Real-time mood entry processing
├── Mood trend analysis and pattern detection
├── Integration with daily/weekly aggregations
└── Cultural context consideration

Voice Service (Port 8011):
├── Voice command pattern analysis
├── Speech sentiment integration
├── Multi-modal interaction tracking
└── Voice-specific behavioral insights
```

## High-Level Architecture

### System Design Principles

#### 1. **Event-Driven Architecture**
```python
Architecture Pattern:
├── Event Sourcing → All interactions recorded as events
├── CQRS (Command Query Responsibility Segregation)
├── Async Processing → Non-blocking pattern analysis  
├── Event Bus → Decoupled service communication
└── Real-time Updates → Live pattern detection
```

#### 2. **Scalable Data Processing**
```python
Processing Strategy:
├── Batch Processing → Historical pattern analysis
├── Stream Processing → Real-time event handling
├── Incremental Updates → Efficient pattern updates
├── Background Jobs → Async insight generation
└── Caching Layers → Performance optimization
```

#### 3. **Cultural Intelligence Integration**
```python
Cultural Awareness:
├── Timezone Adaptation → Local time pattern analysis
├── Language Processing → Multi-lingual content analysis
├── Cultural Events → Holiday and festival impact analysis
├── Regional Patterns → Geographic behavior patterns
└── Personalization → Individual cultural preferences
```

### Low-Level Design

#### Memory Engine Core Architecture
```python
class MemoryEngine:
    """Core memory processing engine with behavioral analysis"""
    
    async def record_interaction(self, user_id, interaction_data):
        # 1. Validate and sanitize interaction data
        validated_data = self.validate_interaction(interaction_data)
        
        # 2. Store interaction with metadata
        interaction = await self.store_interaction(user_id, validated_data)
        
        # 3. Update user session context
        await self.update_session_context(user_id, interaction)
        
        # 4. Trigger pattern analysis (async)
        if self.should_analyze_patterns(user_id):
            await self.queue_pattern_analysis(user_id)
        
        # 5. Check for insight generation triggers
        if self.should_generate_insights(user_id):
            await self.queue_insight_generation(user_id)
        
        return interaction
    
    async def analyze_patterns(self, user_id, timeframe_days=30):
        # 1. Fetch user interactions within timeframe
        interactions = await self.get_user_interactions(
            user_id, timeframe_days
        )
        
        # 2. Apply pattern detection algorithms
        mood_patterns = self.detect_mood_patterns(interactions)
        activity_patterns = self.detect_activity_patterns(interactions)
        temporal_patterns = self.detect_temporal_patterns(interactions)
        
        # 3. Calculate confidence scores
        patterns_with_confidence = self.calculate_confidence_scores(
            [mood_patterns, activity_patterns, temporal_patterns]
        )
        
        # 4. Store pattern results
        await self.store_patterns(user_id, patterns_with_confidence)
        
        return patterns_with_confidence
```

#### Pattern Analysis Algorithms
```python
class PatternAnalyzer:
    """Advanced pattern detection and analysis"""
    
    def detect_mood_patterns(self, interactions):
        # Daily mood cycles
        daily_patterns = self.analyze_daily_cycles(interactions)
        
        # Weekly patterns (weekday vs weekend)
        weekly_patterns = self.analyze_weekly_cycles(interactions)
        
        # Trend analysis (improving/declining)
        trend_patterns = self.analyze_trends(interactions)
        
        # Activity correlation patterns
        correlation_patterns = self.analyze_activity_correlations(interactions)
        
        return {
            "daily": daily_patterns,
            "weekly": weekly_patterns,
            "trends": trend_patterns,
            "correlations": correlation_patterns
        }
    
    def calculate_confidence_scores(self, patterns):
        # Statistical confidence based on sample size
        # Consistency metrics across time periods
        # Cross-validation with historical data
        # Cultural context consideration
        pass
```

#### Insight Generation Engine
```python
class InsightGenerator:
    """AI-powered behavioral insight generation"""
    
    async def generate_insights(self, user_id, patterns):
        insights = []
        
        # Mood trend insights
        mood_insights = self.analyze_mood_trends(patterns["mood"])
        insights.extend(mood_insights)
        
        # Activity recommendation insights
        activity_insights = self.generate_activity_recommendations(
            patterns["activity"]
        )
        insights.extend(activity_insights)
        
        # Behavioral anomaly detection
        anomaly_insights = self.detect_behavioral_anomalies(patterns)
        insights.extend(anomaly_insights)
        
        # Cultural context insights
        cultural_insights = self.apply_cultural_context(
            insights, user_id
        )
        
        # Prioritize and rank insights
        prioritized_insights = self.prioritize_insights(cultural_insights)
        
        return prioritized_insights
```

## Design Documentation

### Database Schema Design

#### Core User Interactions Table
```sql
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    interaction_type VARCHAR(100) NOT NULL,  -- mood, journal, chat, voice, etc.
    interaction_data JSONB NOT NULL,
    cultural_context JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    interaction_metadata JSONB,
    
    -- Source tracking
    source_service VARCHAR(100) NOT NULL,  -- mood_service, chatbot_service, etc.
    session_id VARCHAR(255),
    device_type VARCHAR(50),
    platform VARCHAR(50),
    
    -- Analysis metrics
    processing_time_ms FLOAT,
    confidence_score FLOAT,
    quality_score FLOAT,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Performance indexes
    INDEX idx_user_interactions_user_timestamp (user_id, timestamp),
    INDEX idx_user_interactions_type_timestamp (interaction_type, timestamp),
    INDEX idx_user_interactions_source_timestamp (source_service, timestamp),
    INDEX idx_user_interactions_session (session_id, timestamp),
    INDEX idx_user_interactions_cultural (user_id, cultural_context)
);
```

#### Mood Patterns Analysis Table
```sql
CREATE TABLE mood_patterns (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    pattern_type VARCHAR(100) NOT NULL,  -- daily, weekly, monthly, seasonal
    pattern_data JSONB NOT NULL,
    
    -- Pattern characteristics
    confidence_score FLOAT DEFAULT 0.0,
    frequency VARCHAR(50),  -- daily, weekly, monthly
    intensity FLOAT,        -- 0.0 to 1.0
    stability FLOAT,        -- pattern consistency
    
    -- Time range
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    
    -- Context
    cultural_context JSONB,
    environmental_factors JSONB,
    triggers JSONB,
    
    -- Metadata
    analysis_version VARCHAR(20),
    sample_size INTEGER,
    
    -- State management
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Performance indexes
    INDEX idx_mood_patterns_user_type (user_id, pattern_type),
    INDEX idx_mood_patterns_date_range (start_date, end_date),
    INDEX idx_mood_patterns_confidence (confidence_score),
    INDEX idx_mood_patterns_active (is_active, is_deleted)
);
```

#### Behavioral Insights Table
```sql
CREATE TABLE behavioral_insights (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    insight_type VARCHAR(100) NOT NULL,
    insight_data JSONB NOT NULL,
    
    -- Quality metrics
    accuracy_score FLOAT DEFAULT 0.0,
    relevance_score FLOAT DEFAULT 0.0,
    urgency_level VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    priority INTEGER DEFAULT 5,  -- 1-10 scale
    
    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT,
    recommendation TEXT,
    action_items JSONB,
    
    -- Lifecycle
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    
    -- Context
    cultural_context JSONB,
    
    -- State
    status VARCHAR(50) DEFAULT 'active',  -- active, delivered, acknowledged, expired
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Performance indexes
    INDEX idx_behavioral_insights_user_type (user_id, insight_type),
    INDEX idx_behavioral_insights_urgency (urgency_level, priority),
    INDEX idx_behavioral_insights_timing (generated_at, expires_at),
    INDEX idx_behavioral_insights_status (status, is_active)
);
```

#### Memory Sessions Table
```sql
CREATE TABLE memory_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    
    -- Session timing
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    interaction_count INTEGER DEFAULT 0,
    
    -- Context
    device_type VARCHAR(50),
    platform VARCHAR(50),
    user_agent TEXT,
    ip_address VARCHAR(45),  -- IPv6 support
    location_data JSONB,
    
    -- Analysis
    mood_trend JSONB,
    activity_summary JSONB,
    engagement_score FLOAT,
    session_quality VARCHAR(20),  -- high, medium, low
    
    -- Cultural context
    cultural_context JSONB,
    language_preference VARCHAR(10),
    timezone VARCHAR(50),
    
    -- State
    is_active BOOLEAN DEFAULT TRUE,
    closed_reason VARCHAR(100),  -- timeout, logout, error
    
    -- Performance indexes
    INDEX idx_memory_sessions_user_time (user_id, start_time),
    INDEX idx_memory_sessions_active (is_active, end_time),
    INDEX idx_memory_sessions_duration (duration_seconds)
);
```

### API Design Patterns

#### RESTful Resource Design
```python
# Resource-based URL structure
/api/v1/interactions/              # User interactions collection
/api/v1/interactions/{id}         # Individual interaction resource
/api/v1/patterns/                 # Behavioral patterns collection
/api/v1/patterns/analyze         # Pattern analysis operations
/api/v1/insights/                # Behavioral insights collection
/api/v1/insights/generate        # Insight generation operations
/api/v1/aggregation/{user_id}    # User data aggregation
/api/v1/stats                    # Service statistics

# HTTP Methods semantic mapping
GET     /interactions/     → List user interactions (paginated)
POST    /interactions/     → Create new interaction
GET     /interactions/{id} → Retrieve specific interaction
DELETE  /interactions/{id} → Delete interaction (soft delete)

POST    /patterns/analyze  → Trigger pattern analysis
GET     /patterns/         → List user patterns (filtered)
GET     /patterns/{id}     → Retrieve specific pattern

POST    /insights/generate → Trigger insight generation
GET     /insights/         → List user insights (filtered)
PUT     /insights/{id}     → Update insight status (acknowledged)
```

#### Response Format Standardization
```python
# Success Response Format
{
    "success": true,
    "data": { ... },
    "metadata": {
        "timestamp": "2025-09-27T14:30:00Z",
        "processing_time_ms": 125.7,
        "cache_status": "hit|miss",
        "version": "1.0.0"
    },
    "pagination": {  # For list endpoints
        "total": 150,
        "limit": 50,
        "offset": 0,
        "has_more": true
    }
}

# Error Response Format
{
    "success": false,
    "error": {
        "code": "INVALID_INTERACTION_TYPE", 
        "message": "Interaction type 'invalid' is not supported",
        "details": {
            "supported_types": ["mood", "journal", "chat", "voice"],
            "received_type": "invalid"
        }
    },
    "timestamp": "2025-09-27T14:30:00Z"
}
```

### Security & Privacy Design

#### Data Privacy Protection
```python
Privacy Measures:
├── Data Anonymization → Personal identifiers removed from analytics
├── Consent Management → User control over data collection
├── Data Retention → Automatic purging of old data
├── Export/Delete → User data portability and deletion rights
└── Encryption → All sensitive data encrypted at rest

# GDPR Compliance Features
GDPR_Features:
├── Right to Access → Complete data export capability
├── Right to Rectification → Data correction mechanisms
├── Right to Erasure → Complete data deletion
├── Right to Portability → Data export in standard formats
└── Privacy by Design → Default privacy-friendly settings
```

#### Authentication & Authorization
```python
Security Layers:
├── JWT Token Validation → All requests require valid tokens
├── User Context Isolation → Strict user data separation
├── Rate Limiting → Per-user request throttling
├── Input Validation → Comprehensive data sanitization
└── Audit Logging → Complete access logging for security
```

## Incomplete Implementations & TODOs

### Current Limitations

#### 1. **Advanced AI Integration Missing**
```python
# TODO: Machine Learning Pattern Recognition
class AdvancedPatternAnalyzer:
    # Currently using basic statistical analysis
    # Needed: ML-based pattern recognition with scikit-learn/TensorFlow
    
    async def ml_pattern_detection(self, interactions):
        """ML-based pattern detection - NOT YET IMPLEMENTED"""
        # TODO: Clustering algorithms for behavior grouping
        # TODO: Time series analysis with LSTM networks  
        # TODO: Anomaly detection with isolation forests
        # TODO: Predictive modeling for future behavior
        raise NotImplementedError("ML pattern analysis not implemented")
    
    async def sentiment_analysis_integration(self, text_content):
        """Sentiment analysis for text interactions - NOT YET IMPLEMENTED"""
        # TODO: Integration with NLP models for sentiment scoring
        # TODO: Multi-language sentiment analysis
        # TODO: Emotional state classification
        raise NotImplementedError("Sentiment analysis not implemented")
```

#### 2. **Real-time Event Processing Gaps**
```python
# TODO: Complete NATS JetStream Integration
class MemoryEventHandler:
    # Current: Basic event handling framework exists
    # Missing: Full production-ready event processing
    
    async def process_real_time_stream(self):
        """Real-time event stream processing - NOT YET IMPLEMENTED"""
        # TODO: Durable event subscriptions
        # TODO: Event replay capability for service recovery
        # TODO: Dead letter queue for failed events
        # TODO: Event ordering and deduplication
        pass
    
    async def handle_event_failures(self, failed_event):
        """Event failure recovery - NOT YET IMPLEMENTED"""
        # TODO: Retry mechanisms with exponential backoff
        # TODO: Error categorization and routing
        # TODO: Alert system for critical failures
        pass
```

#### 3. **Advanced Analytics Features**
```python
# TODO: Predictive Analytics Engine
class PredictiveAnalytics:
    """Predictive behavior modeling - NOT YET IMPLEMENTED"""
    
    async def predict_mood_trends(self, user_id, forecast_days=7):
        """Mood trend forecasting - NOT YET IMPLEMENTED"""
        # TODO: Time series forecasting models
        # TODO: Seasonal decomposition analysis
        # TODO: External factor integration (weather, events)
        pass
    
    async def recommend_interventions(self, user_id, risk_factors):
        """Proactive intervention recommendations - NOT YET IMPLEMENTED"""
        # TODO: Risk assessment algorithms
        # TODO: Intervention effectiveness tracking  
        # TODO: Personalized recommendation engine
        pass
```

#### 4. **Missing API Endpoints**
```python
# TODO: Advanced Data Export/Import
@app.post("/api/v1/export/comprehensive")
async def export_comprehensive_data():
    """Complete user data export - NOT YET IMPLEMENTED"""
    pass

@app.post("/api/v1/import/historical")  
async def import_historical_data():
    """Historical data import - NOT YET IMPLEMENTED"""
    pass

# TODO: Real-time Pattern Monitoring
@app.get("/api/v1/patterns/real-time/{user_id}")
async def get_real_time_patterns():
    """Real-time pattern updates - NOT YET IMPLEMENTED"""
    pass

# TODO: Cross-User Analytics (Anonymized)
@app.get("/api/v1/analytics/population")
async def get_population_analytics():
    """Population-level insights - NOT YET IMPLEMENTED"""
    pass

# TODO: Advanced Insight Management
@app.post("/api/v1/insights/{id}/feedback")
async def provide_insight_feedback():
    """Insight effectiveness feedback - NOT YET IMPLEMENTED"""
    pass
```

#### 5. **Performance Optimization Gaps**
```python
# TODO: Advanced Caching Strategy
class AdvancedCaching:
    """Multi-tier caching system - NOT YET IMPLEMENTED"""
    
    async def implement_distributed_cache(self):
        # TODO: Redis Cluster support
        # TODO: Cache warming strategies
        # TODO: Intelligent cache eviction
        # TODO: Cache coherency across instances
        pass
    
    async def optimize_database_queries(self):
        # TODO: Query optimization analysis
        # TODO: Connection pooling optimization
        # TODO: Read replica integration
        # TODO: Database partitioning strategy
        pass
```

#### 6. **Cultural Intelligence Enhancement**
```python
# TODO: Advanced Cultural Adaptation
class CulturalIntelligence:
    """Enhanced cultural context processing - PARTIALLY IMPLEMENTED"""
    
    async def analyze_cultural_patterns(self, user_id, cultural_context):
        """Cultural behavior pattern analysis - BASIC IMPLEMENTATION"""
        # TODO: Cultural holiday impact analysis
        # TODO: Regional behavior pattern variations
        # TODO: Language-specific sentiment analysis
        # TODO: Cultural norm adaptation in recommendations
        pass
    
    async def localize_insights(self, insights, cultural_context):
        """Cultural localization of insights - NOT YET IMPLEMENTED"""
        # TODO: Culture-specific recommendation adjustments
        # TODO: Local context consideration in messaging
        # TODO: Cultural sensitivity in behavioral analysis
        pass
```

### Technical Debt

#### 1. **Testing Infrastructure**
```python
# Current: Basic API tests exist
# Missing:
├── Comprehensive unit tests for all modules
├── Integration tests with real event bus
├── Performance tests under load
├── End-to-end workflow testing
└── Mock service testing infrastructure

# TODO: Test Coverage Improvement
Target Coverage:
├── Unit Tests: 90%+ coverage
├── Integration Tests: All service boundaries
├── Performance Tests: Load and stress testing
└── End-to-end Tests: Complete user workflows
```

#### 2. **Error Handling & Resilience**
```python
# TODO: Comprehensive Error Handling
Error_Handling_Gaps:
├── Circuit breaker pattern for external services
├── Graceful degradation during partial failures
├── Retry mechanisms with exponential backoff
├── Dead letter queues for failed events
└── Automated recovery procedures
```

#### 3. **Monitoring & Observability**
```python
# TODO: Production Monitoring
Monitoring_Needs:
├── Structured logging with correlation IDs
├── Custom metrics for pattern analysis performance
├── Distributed tracing for request flows
├── Alert thresholds for business metrics
└── Performance profiling and optimization
```

## Future Development Plans

### Phase 1 - AI Enhancement (Q4 2025)

#### 1.1 **Machine Learning Integration**
- [ ] **Scikit-learn Integration** - Advanced pattern recognition algorithms
- [ ] **TensorFlow Models** - Deep learning for behavioral prediction
- [ ] **NLP Integration** - Sentiment analysis and text classification
- [ ] **Anomaly Detection** - Isolation Forest and One-Class SVM models
- [ ] **Time Series Forecasting** - LSTM networks for mood prediction

#### 1.2 **Real-time Analytics**
```python
Real_Time_Features:
├── Stream processing with Apache Kafka/NATS JetStream
├── Real-time pattern detection and alerting  
├── Live dashboard for behavioral insights
├── Immediate intervention recommendations
└── Real-time mood tracking and analysis
```

#### 1.3 **Predictive Capabilities**
```python
Predictive_Analytics:
├── 7-day mood forecasting with 85%+ accuracy
├── Risk factor identification and early warning
├── Personalized intervention recommendations
├── Optimal timing prediction for notifications
└── Behavioral change probability assessment
```

### Phase 2 - Advanced Features (Q1 2026)

#### 2.1 **Multi-Modal Analysis**
- [ ] **Voice Pattern Analysis** - Integration with voice service for speech patterns
- [ ] **Image Emotion Recognition** - Facial expression analysis from media uploads
- [ ] **Text Sentiment Analysis** - Advanced NLP for journal and chat analysis
- [ ] **Activity Pattern Fusion** - Multi-source data fusion for comprehensive insights
- [ ] **Biometric Integration** - Heart rate and sleep pattern analysis

#### 2.2 **Social Intelligence**
```python
Social_Features:
├── Anonymous population insights and benchmarking
├── Peer group comparison and recommendations
├── Social support network analysis
├── Community behavior pattern identification
└── Collaborative filtering for recommendations
```

#### 2.3 **Cultural Intelligence Enhancement**
```python
Cultural_Intelligence:
├── Cultural holiday and event impact analysis
├── Regional behavior pattern variations
├── Language-specific sentiment nuances
├── Cultural norm adaptation in recommendations
└── Localized insight messaging and recommendations
```

### Phase 3 - Enterprise Features (Q2 2026)

#### 3.1 **Advanced Analytics Platform**
- [ ] **Business Intelligence Dashboard** - Comprehensive analytics interface
- [ ] **Custom Report Generation** - User-defined analysis reports
- [ ] **Data Visualization Tools** - Interactive charts and trend analysis
- [ ] **Export/Import Tools** - Complete data portability solutions
- [ ] **API Analytics** - Detailed usage and performance metrics

#### 3.2 **Scalability & Performance**
```python
Scalability_Improvements:
├── Horizontal scaling with Redis Cluster
├── Database sharding for user data
├── Event sourcing architecture implementation
├── Microservice decomposition for specialized functions
└── Global data replication for multi-region support
```

#### 3.3 **Integration Ecosystem**
```python
Integration_Platform:
├── Webhook system for external integrations
├── Plugin architecture for custom analyzers
├── Third-party wellness app integrations
├── Healthcare provider data sharing (HIPAA compliant)
└── Research collaboration tools for anonymized insights
```

### Phase 4 - Research & Innovation (Q3-Q4 2026)

#### 4.1 **Advanced AI Research**
- [ ] **Behavioral Digital Twins** - Complete user behavior modeling
- [ ] **Causal Inference** - Understanding cause-effect relationships
- [ ] **Federated Learning** - Privacy-preserving ML across users
- [ ] **Explainable AI** - Transparent insight generation explanations
- [ ] **Reinforcement Learning** - Adaptive recommendation systems

#### 4.2 **Innovation Features**
```python
Innovation_Research:
├── Quantum-inspired optimization for pattern matching
├── Graph neural networks for relationship analysis
├── Temporal knowledge graphs for context understanding
├── Multi-agent systems for collaborative insights
└── Edge computing for real-time processing
```

### Development Roadmap Timeline

```
2025 Q4: AI Enhancement & Real-time Analytics
├── Week 1-4: ML pattern recognition integration
├── Week 5-8: Real-time event processing system
├── Week 9-12: Predictive analytics implementation
└── Week 13-16: Testing and production deployment

2026 Q1: Advanced Multi-Modal Analysis
├── Month 1: Voice and image pattern analysis
├── Month 2: Social intelligence features
└── Month 3: Cultural intelligence enhancement

2026 Q2: Enterprise Platform Development
├── Month 1: Advanced analytics dashboard
├── Month 2: Scalability improvements
└── Month 3: Integration ecosystem development

2026 Q3-Q4: Research & Innovation Phase
├── Q3: Advanced AI research implementation
└── Q4: Innovation features and future-proofing
```

## Development & Testing

### Local Development Setup

#### Prerequisites
```bash
# System requirements
Python 3.11+
PostgreSQL 13+
Redis 6+
NATS Server 2.9+
Docker & Docker Compose (optional)

# Python packages (scientific computing)
numpy>=1.25.2
pandas>=2.1.4
scikit-learn>=1.3.2
```

#### Quick Start
```bash
# 1. Clone and navigate to service
cd /home/sachin/mantrapath/backend/services/memory_service

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export MEMORY_SERVICE_PORT=8017
export DATABASE_URL=postgresql://user:pass@localhost:5432/mantrapath
export REDIS_URL=redis://localhost:6379
export NATS_URL=nats://localhost:4222

# 5. Initialize database tables
python -c "
from models.memory_models import Base
from shared.database import engine
Base.metadata.create_all(engine)
"

# 6. Start service
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8017 --reload
```

#### Docker Development
```bash
# Build and run with Docker
docker build -t mantrapath/memory-service .
docker run -d \
  --name memory-service \
  -p 8017:8017 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/mantrapath \
  -e REDIS_URL=redis://redis:6379 \
  -e NATS_URL=nats://nats:4222 \
  mantrapath/memory-service
```

### Testing Strategy

#### Unit Testing
```bash
# Run unit tests
python -m pytest tests/test_memory_api.py -v

# Test specific components
python -m pytest tests/test_memory_engine.py -v
python -m pytest tests/test_pattern_analysis.py -v
python -m pytest tests/test_event_handler.py -v

# Coverage reporting
python -m pytest tests/ --cov=. --cov-report=html
```

#### Integration Testing
```bash
# API endpoint testing
python -m pytest tests/test_memory_api.py -v

# Event system integration testing
python -m pytest tests/test_event_integration.py -v

# Database integration testing
python -m pytest tests/test_database_integration.py -v

# Cross-service communication testing
python test_memory_service.py
```

#### Performance Testing
```bash
# Load testing with locust
pip install locust
locust -f tests/performance/locustfile.py --host=http://localhost:8017

# Memory profiling
python -m memory_profiler tests/test_memory_usage.py

# Pattern analysis performance testing
python tests/performance/test_pattern_analysis_performance.py
```

### Production Deployment

#### Container Deployment
```dockerfile
# Production Dockerfile optimization
FROM python:3.11-slim
WORKDIR /app

# System dependencies for scientific computing
RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev libicu-dev pkg-config curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .
RUN groupadd -r memoryuser && useradd -r -g memoryuser memoryuser
RUN chown -R memoryuser:memoryuser /app
USER memoryuser

# Expose port and health check
EXPOSE 8017
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
    CMD curl -f http://localhost:8017/health/live || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8017"]
```

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: memory-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: memory-service
  template:
    metadata:
      labels:
        app: memory-service
    spec:
      containers:
      - name: memory-service
        image: mantrapath/memory-service:latest
        ports:
        - containerPort: 8017
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: memory-config
              key: database-url
        - name: REDIS_URL
          value: "redis://redis-cluster:6379"
        - name: NATS_URL
          value: "nats://nats-cluster:4222"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8017
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8017
          initialDelaySeconds: 30
          periodSeconds: 5
```

## Monitoring & Observability

### Health Monitoring
```python
# Service health endpoints provide comprehensive status
Health_Checks:
├── /health/live → Basic liveness for Kubernetes
├── /health/ready → Readiness with dependency checks
├── /health → General health status
└── /api/v1/stats → Detailed performance metrics

# Key metrics to monitor
Critical_Metrics:
├── Interaction processing rate (interactions/minute)
├── Pattern analysis completion time (seconds)
├── Insight generation accuracy (percentage)
├── Event processing latency (milliseconds)
├── Cache hit ratio (percentage)
├── Database connection pool usage (count)
└── Memory usage for ML models (MB)
```

### Logging Strategy
```python
# Structured logging format for production
{
    "timestamp": "2025-09-27T14:30:00Z",
    "level": "INFO",
    "service": "memory_service", 
    "user_id": "user_123",
    "operation": "analyze_patterns",
    "processing_time_ms": 1250.7,
    "patterns_found": 5,
    "confidence_avg": 0.87,
    "cache_status": "miss",
    "correlation_id": "req_abc123"
}
```

### Performance Metrics
```python
# Business metrics for monitoring
Business_KPIs:
├── Pattern detection accuracy rate > 85%
├── Insight relevance score > 0.8
├── User engagement with insights > 70%
├── Processing latency < 2 seconds
└── Event processing success rate > 99%
```

## Contributing

### Development Guidelines
1. **Code Quality**: Follow PEP 8 style guidelines and comprehensive type hints
2. **Testing**: Write unit tests for all new pattern analysis algorithms
3. **Documentation**: Update API documentation for all endpoint changes
4. **Privacy**: Ensure all user data handling complies with privacy regulations
5. **Performance**: Consider scalability implications of new analysis algorithms

### Key Areas for Contribution
- **Machine Learning Models** - Advanced pattern recognition and prediction
- **Real-time Processing** - Event stream processing and live analytics
- **Cultural Intelligence** - Enhanced cultural context processing
- **Performance Optimization** - Database query optimization and caching
- **Testing Infrastructure** - Comprehensive test coverage and automation
- **API Enhancement** - Advanced analytics and insight management endpoints

---

**Service Status**: ✅ Active Development  
**Port**: 8017 (Standardized)  
**Version**: 1.0.0  
**Last Updated**: September 2025  
**Maintainer**: MantraPath Development Team  
**License**: MIT License