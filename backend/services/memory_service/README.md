# Memory Service 🧠

**Port: 8017**  
**Version: 1.0.0**  
**Sprint: 3 Implementation**

## Overview

The Memory Service is a comprehensive user interaction tracking and behavioral insights system that serves as the foundation for MantraPath's intelligent, memory-driven mental wellness platform. It records, analyzes, and generates insights from all user interactions across the platform.

## Features

### 🔍 Core Capabilities
- **User Interaction Recording**: Comprehensive tracking of all user activities
- **Mood Pattern Analysis**: Intelligent pattern detection in user mood data
- **Behavioral Insights Generation**: AI-powered personalized recommendations
- **Cross-Platform Aggregation**: Unified view of user interactions across all services
- **Real-Time Event Processing**: Event-driven updates via NATS event bus
- **Cultural Context Integration**: Culturally-aware analysis and recommendations

### 📊 Analytics & Intelligence
- **Daily Patterns**: Hour-by-hour mood and activity analysis
- **Weekly Patterns**: Day-of-week mood and engagement trends
- **Trend Analysis**: Long-term mood trajectory detection
- **Engagement Insights**: Platform usage pattern analysis
- **Cultural Adaptation**: Context-aware cultural intelligence

### 🚀 Performance Features
- **Redis Caching**: Fast data retrieval with intelligent caching
- **PostgreSQL Storage**: Robust data persistence with optimized schemas
- **Event-Driven Architecture**: Real-time updates via NATS JetStream
- **Batch Processing**: Efficient bulk data processing
- **Performance Monitoring**: Built-in metrics and health checks

## API Endpoints

### Health & Status
```
GET  /                          # Service information
GET  /health/live               # Liveness probe
GET  /health/ready              # Readiness probe  
GET  /health/status             # Detailed health status
```

### Interactions API
```
POST /api/v1/memory/interactions           # Record new interaction
GET  /api/v1/memory/interactions           # Get user interactions (with filters)
GET  /api/v1/memory/interactions/{id}      # Get specific interaction
DELETE /api/v1/memory/interactions/{id}    # Delete interaction
POST /api/v1/memory/interactions/bulk     # Bulk create interactions
GET  /api/v1/memory/interactions/stats/summary  # Interaction statistics
GET  /api/v1/memory/interactions/export   # Export interactions (JSON/CSV)
```

### Patterns API
```
POST /api/v1/memory/patterns/analyze       # Trigger pattern analysis
GET  /api/v1/memory/patterns               # Get mood patterns (with filters)
GET  /api/v1/memory/patterns/{id}          # Get specific pattern
GET  /api/v1/memory/patterns/summary       # Pattern summary statistics
GET  /api/v1/memory/patterns/types/{type}/details  # Pattern type details
PUT  /api/v1/memory/patterns/{id}/activate # Activate pattern
PUT  /api/v1/memory/patterns/{id}/deactivate # Deactivate pattern
DELETE /api/v1/memory/patterns/{id}        # Delete pattern
GET  /api/v1/memory/patterns/recommendations # Pattern-based recommendations
```

### Insights API
```
POST /api/v1/memory/insights/generate      # Generate behavioral insights
GET  /api/v1/memory/insights               # Get insights (with filters)
GET  /api/v1/memory/insights/{id}          # Get specific insight
PUT  /api/v1/memory/insights/{id}/acknowledge # Acknowledge insight
PUT  /api/v1/memory/insights/{id}/dismiss  # Dismiss insight
DELETE /api/v1/memory/insights/{id}        # Delete insight
GET  /api/v1/memory/insights/summary       # Insights summary
GET  /api/v1/memory/insights/cross-platform # Cross-platform insights
GET  /api/v1/memory/insights/types         # Available insight types
```

## Database Schema

### Tables

#### `user_interactions`
Primary table for storing all user interactions across the platform.

```sql
- id (SERIAL PRIMARY KEY)
- user_id (VARCHAR(255), NOT NULL, INDEXED)
- interaction_type (VARCHAR(100), NOT NULL, INDEXED) 
- interaction_data (JSONB, NOT NULL)
- cultural_context (JSONB)
- timestamp (TIMESTAMP WITH TIME ZONE, INDEXED)
- source_service (VARCHAR(100), NOT NULL, INDEXED)
- session_id (VARCHAR(255), INDEXED)
- metadata (JSONB)
- processing_time_ms (FLOAT)
- confidence_score (FLOAT)
- quality_score (FLOAT)
```

#### `mood_patterns`
Stores aggregated mood patterns and analysis results.

```sql
- id (SERIAL PRIMARY KEY)
- user_id (VARCHAR(255), NOT NULL, INDEXED)
- pattern_type (VARCHAR(100), NOT NULL, INDEXED)
- pattern_data (JSONB, NOT NULL)
- confidence_score (FLOAT, NOT NULL)
- start_date (TIMESTAMP, INDEXED)
- end_date (TIMESTAMP, INDEXED)
- cultural_context (JSONB)
```

#### `behavioral_insights`
Generated insights and recommendations for users.

```sql
- id (SERIAL PRIMARY KEY)
- user_id (VARCHAR(255), NOT NULL, INDEXED)
- insight_type (VARCHAR(100), NOT NULL, INDEXED)
- insight_data (JSONB, NOT NULL)
- accuracy_score (FLOAT, NOT NULL)
- urgency_level (VARCHAR(20), NOT NULL)
- title (VARCHAR(255), NOT NULL)
- description (TEXT)
- recommendation (TEXT)
```

## Event Integration

### Subscribed Events
The Memory Service automatically processes events from other services:

```javascript
// Mood Service Events
mood.entry_created
mood.entry_updated

// Content Service Events (Journal)
journal.entry_created
journal.entry_updated

// Chatbot Service Events
chat.message_sent

// Community Service Events
community.post_created
community.comment_created

// Voice Service Events
voice.command_processed
voice.interaction_completed

// Session Events
user.session_started
user.session_ended
```

### Published Events
```javascript
// Memory Events
memory.interaction_recorded    // New interaction recorded
memory.pattern_updated        // Pattern analysis completed
memory.insight_generated      // New insight generated
```

## Configuration

### Environment Variables

#### Core Service Configuration
```bash
MEMORY_SERVICE_HOST=0.0.0.0
MEMORY_SERVICE_PORT=8017
SERVICE_NAME=memory_service
SERVICE_VERSION=1.0.0
```

#### Database Configuration
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db
NATS_URL=nats://host:port
```

#### Memory Engine Configuration
```bash
PATTERN_ANALYSIS_WINDOW_DAYS=30      # Days of data for pattern analysis
INSIGHT_GENERATION_THRESHOLD=10      # Min interactions for insights
CACHE_TTL_SECONDS=3600              # Cache expiration time
BATCH_SIZE=100                      # Batch processing size
MAX_PATTERNS_PER_USER=50            # Max patterns to store per user
```

#### Pattern Detection Thresholds
```bash
MOOD_STABILITY_THRESHOLD=0.7         # Mood stability threshold
PATTERN_CONFIDENCE_THRESHOLD=0.6     # Pattern confidence minimum
INSIGHT_RELEVANCE_THRESHOLD=0.5      # Insight relevance minimum
CULTURAL_SENSITIVITY_THRESHOLD=0.8   # Cultural adaptation threshold
```

#### Cultural Adaptation
```bash
CULTURAL_ADAPTATION_ENABLED=true
CULTURAL_FALLBACK_ENABLED=true
DEFAULT_CULTURE=neutral
```

## Usage Examples

### Recording an Interaction

```python
# POST /api/v1/memory/interactions
{
    "interaction_type": "mood",
    "interaction_data": {
        "mood_score": 0.8,
        "mood_label": "happy",
        "energy_level": 0.7,
        "notes": "Feeling great today!"
    },
    "source_service": "mood_service",
    "session_id": "user_session_123",
    "cultural_context": {
        "language": "en",
        "cultural_background": "western"
    }
}
```

### Analyzing Patterns

```python
# POST /api/v1/memory/patterns/analyze
{
    "pattern_types": ["daily", "weekly", "trend"],
    "force_refresh": true
}
```

### Generating Insights

```python
# POST /api/v1/memory/insights/generate
{
    "force_refresh": true,
    "insight_types": ["mood_optimization", "engagement_pattern"],
    "priority_filter": "high"
}
```

## Development

### Setup

1. **Install Dependencies**
```bash
cd backend/services/memory_service
pip install -r requirements.txt
```

2. **Environment Variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Database Setup**
```bash
# Database will be created automatically via shared models
```

4. **Run Service**
```bash
# Development
uvicorn main:app --host 0.0.0.0 --port 8017 --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8017
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test
pytest tests/test_memory_api.py::TestMemoryServiceAPI::test_interactions_crud
```

### Docker

```bash
# Build image
docker build -t memory-service .

# Run container
docker run -p 8017:8017 memory-service

# Run with docker-compose
docker-compose up memory-service
```

## Architecture

### Memory Engine
The core `MemoryEngine` class handles:
- Pattern detection algorithms
- Insight generation logic  
- Cross-platform data aggregation
- Performance optimization

### Event Handler
The `MemoryEventHandler` processes:
- Real-time event streaming
- Event transformation and storage
- Error handling and retry logic
- Performance metrics

### API Layer
FastAPI-based REST API providing:
- CRUD operations for all data types
- Advanced filtering and search
- Export capabilities
- Real-time statistics

## Performance

### Benchmarks
- **API Response Time**: <100ms for simple operations
- **Cross-Service Latency**: <200ms for complex operations  
- **Event Processing**: <50ms event propagation
- **Database Queries**: Optimized with proper indexing
- **Cache Hit Rate**: >90% for frequently accessed data

### Optimization Features
- **Redis Caching**: Multi-level caching strategy
- **Database Indexing**: Optimized indexes for query performance
- **Batch Processing**: Efficient bulk operations
- **Connection Pooling**: Optimized database connections
- **Query Optimization**: Optimized SQLAlchemy queries

## Monitoring

### Health Checks
- **Liveness**: Basic service availability
- **Readiness**: Database and Redis connectivity
- **Status**: Detailed component health

### Metrics
- Interactions processed per second
- Pattern analysis completion time
- Insight generation accuracy
- Cache hit/miss ratios
- Event processing latency

### Logging
Structured logging with:
- Request/response logging
- Performance metrics
- Error tracking
- Event processing logs

## Integration with Other Services

### Mood Service
- Receives mood entry events
- Enhances mood tracking with memory
- Provides cross-platform mood insights

### Chatbot Service  
- Processes chat interactions
- Provides conversation context
- Enables memory-aware responses

### Community Service
- Tracks community engagement
- Analyzes social interaction patterns
- Provides community insights

### Voice Service
- Processes voice interactions
- Analyzes speech patterns
- Provides voice-based insights

## Sprint 3 Implementation Status

### ✅ Completed
- [x] Memory Service core architecture
- [x] Database schema and models
- [x] Interactions API (full CRUD)
- [x] Patterns API (analysis and retrieval)  
- [x] Insights API (generation and management)
- [x] Event handler for real-time processing
- [x] Memory Engine with pattern detection
- [x] Cross-platform aggregation
- [x] Cultural context integration
- [x] Docker configuration
- [x] Comprehensive testing
- [x] API documentation

### 🔄 In Progress  
- [ ] Advanced ML pattern detection
- [ ] Enhanced cultural intelligence
- [ ] Performance optimization
- [ ] Integration testing with all services

### 📋 Planned
- [ ] Real-time streaming analytics
- [ ] Advanced recommendation engine
- [ ] Machine learning model integration
- [ ] Enhanced cultural adaptation
- [ ] Advanced visualization support

## Future Enhancements

### Sprint 4 Preparation
- Cross-platform mood collection foundation ✅
- Memory-aware chatbot integration ready ✅
- Real-time insights infrastructure ✅
- Advanced pattern recognition algorithms
- Enhanced cultural intelligence

### Long-term Goals
- Predictive mood modeling
- Advanced behavioral analytics
- Real-time intervention systems
- Comprehensive wellness scoring
- Multi-cultural adaptation

## Contributing

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Follow cultural sensitivity guidelines
5. Ensure performance benchmarks are met

## License

Part of the MantraPath platform - proprietary license.

---

*The Memory Service forms the foundation for MantraPath's intelligent, memory-driven mental wellness platform, enabling personalized insights and recommendations based on comprehensive user interaction analysis.*
