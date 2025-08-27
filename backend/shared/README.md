# MantraPath Shared Components

The `shared` directory contains core components that are used across multiple services in the MantraPath ecosystem. These components provide essential functionality for database access, authentication, event handling, and cross-service communication.

## 📋 Component Overview

| Component | Purpose | Usage |
|-----------|---------|-------|
| `database.py` | Database connection and session management | All services requiring database access |
| `models.py` | Shared SQLAlchemy models and schemas | Cross-service data consistency |
| `auth.py` | JWT authentication and user verification | Protected endpoints across services |
| `redis_client.py` | Redis connection and caching utilities | Services requiring caching/sessions |
| `core_events.py` | Core event definitions and schemas | Event-driven communication |
| `events/` | Advanced event handling system | Real-time communication |
| `achievement_models.py` | Achievement and gamification models | Progress tracking features |
| `feature_flags.py` | Feature flag management | A/B testing and gradual rollouts |
| `user_display.py` | User display utilities | Consistent user representation |

## 🗄️ Database Components

### `database.py`
Provides centralized database connection management for PostgreSQL.

**Key Features:**
- Connection pooling with automatic reconnection
- Session management with proper cleanup
- Health check functionality
- Environment-based configuration

**Usage Example:**
```python
from shared.database import get_db_session, get_database_url

# Get database session
async with get_db_session() as session:
    result = await session.execute(query)
```

### `models.py`
Contains shared SQLAlchemy models used across multiple services.

**Core Models:**
- **User**: Base user information and authentication
- **UserProfile**: Extended user profile data
- **MoodEntry**: Mood tracking entries
- **JournalEntry**: Journal and reflection entries
- **ChatSession**: AI chatbot conversations
- **VoiceCommand**: Voice interaction records
- **TranslationRequest**: Translation service records

**Relationships:**
- Cross-service foreign key relationships
- Proper cascade configurations
- Index optimization for performance

## 🔐 Authentication Components

### `auth.py`
Centralized authentication and authorization utilities.

**Features:**
- JWT token generation and validation
- User authentication decorators
- Role-based access control
- Session management
- Password hashing and verification

**Usage Example:**
```python
from shared.auth import verify_token, get_current_user

@verify_token
async def protected_endpoint(request, user_id: int):
    # Access user_id from verified token
    pass
```

## 🧠 Cache and Redis Components

### `redis_client.py`
Redis connection management and caching utilities.

**Features:**
- Connection pooling and health checks
- Cache key management with namespacing
- TTL management and expiration policies
- Pub/Sub support for real-time features
- Session storage for stateful operations

**Usage Example:**
```python
from shared.redis_client import get_redis, cache_set, cache_get

# Cache user data
await cache_set(f"user:{user_id}", user_data, ttl=3600)

# Retrieve cached data
user_data = await cache_get(f"user:{user_id}")
```

## 🚀 Event System Components

### `core_events.py`
Core event definitions and base event handling functionality.

**Event Types:**
- `UserEvent`: User-related events (registration, login, profile updates)
- `MoodEvent`: Mood tracking and emotional events
- `ChatEvent`: AI conversation events
- `VoiceEvent`: Voice command and interaction events
- `TranslationEvent`: Translation request events
- `AchievementEvent`: Gamification and progress events

### `events/` Directory
Advanced event handling system with specialized event buses.

#### `enhanced_bus.py`
Enhanced event bus with advanced features:
- Event filtering and routing
- Event aggregation and correlation
- Cross-service event orchestration
- Event replay and recovery

#### `nats_bus.py`
NATS-based event bus for high-performance messaging:
- Persistent streams with JetStream
- Subject-based routing
- Load balancing and scaling
- Event durability and replay

#### `ai_events.py`
AI-specific events for machine learning services:
- Model training events
- Prediction events
- Anomaly detection events
- Cross-service ML coordination

#### `voice_events.py`
Voice processing events:
- Speech-to-text events
- Text-to-speech events
- Voice command events
- Language detection events

#### `cultural_events.py`
Cultural intelligence events:
- Language preference updates
- Cultural context events
- Translation quality events
- Cultural adaptation triggers

## 🏆 Achievement and Gamification

### `achievement_models.py`
Achievement system models and utilities.

**Components:**
- **Achievement**: Achievement definitions and metadata
- **UserAchievement**: User progress tracking
- **Milestone**: Progress milestones and rewards
- **Badge**: Visual achievement representations

**Features:**
- Progress calculation and tracking
- Notification integration
- Leaderboard support
- Custom achievement criteria

## 🎛️ Feature Management

### `feature_flags.py`
Feature flag management for A/B testing and gradual rollouts.

**Features:**
- User-based feature toggles
- Percentage rollouts
- Environment-based flags
- Real-time flag updates
- Analytics integration

**Usage Example:**
```python
from shared.feature_flags import is_feature_enabled

if await is_feature_enabled("new_mood_tracking", user_id):
    # Use new mood tracking feature
    pass
```

## 👤 User Utilities

### `user_display.py`
User display and representation utilities.

**Features:**
- Anonymous user display names
- Avatar generation
- Privacy-safe user representation
- Consistent formatting across services

## 🔧 Configuration and Environment

### Environment Variables
The shared components use the following environment variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath

# Redis Configuration  
REDIS_URL=redis://redis:6379/0

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# NATS Configuration
NATS_URL=nats://nats:4222
NATS_STREAM_NAME=mantrapath-events

# Feature Flags
FEATURE_FLAGS_CACHE_TTL=300
```

## 🧪 Testing

### Unit Tests
Each component includes comprehensive unit tests:

```bash
# Run shared component tests
cd backend
python -m pytest shared/tests/ -v
```

### Integration Tests
Cross-service integration tests ensure proper component interaction:

```bash
# Run integration tests
python -m pytest tests/integration/ -v
```

## 📚 Development Guidelines

### Adding New Shared Components

1. **Create the component file** in the appropriate location
2. **Add proper type hints** and documentation
3. **Include error handling** and logging
4. **Write comprehensive tests**
5. **Update this README** with component documentation
6. **Version the component** for compatibility tracking

### Best Practices

- **Maintain backwards compatibility** when updating shared components
- **Use dependency injection** for testability
- **Implement proper error handling** with meaningful error messages
- **Log important operations** for debugging and monitoring
- **Cache frequently accessed data** with appropriate TTL
- **Use async/await** for I/O operations

### Component Dependencies

```mermaid
graph TD
    A[Services] --> B[auth.py]
    A --> C[database.py]
    A --> D[redis_client.py]
    A --> E[core_events.py]
    
    B --> C
    B --> D
    E --> F[events/enhanced_bus.py]
    E --> G[events/nats_bus.py]
    
    F --> D
    G --> D
```

## 🚀 Performance Considerations

- **Connection Pooling**: Database and Redis connections use pooling for efficiency
- **Caching Strategy**: Intelligent caching with TTL management
- **Event Batching**: Events are batched for performance in high-load scenarios
- **Lazy Loading**: Components are loaded only when needed
- **Memory Management**: Proper cleanup and resource management

## 🔐 Security Features

- **JWT Security**: Secure token generation with configurable expiration
- **Input Validation**: All inputs are validated and sanitized
- **SQL Injection Prevention**: Parameterized queries and ORM usage
- **Redis Security**: Secure Redis connections with authentication
- **Event Security**: Event payload validation and sanitization

---

For service-specific documentation, see individual service README files in their respective directories.
