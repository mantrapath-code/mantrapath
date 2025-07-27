# MantraPath Backend - Microservices Architecture

## Architecture Overview

MantraPath backend is built using a microservices architecture with Python FastAPI, designed to handle high-scale wellness data processing with real-time synchronization to the frontend.

## Services Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  API Gateway    │    │  Load Balancer  │
│   (React)       │◄───┤  (Port 8000)    │◄───┤  (Nginx/HAProxy)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │ Auth Service │ │Mood Service│ │Chat Service │
        │ (Port 8001)  │ │(Port 8003) │ │(Port 8004)  │
        └──────────────┘ └───────────┘ └─────────────┘
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │Profile Service│ │Content Svc│ │Community Svc│
        │ (Port 8002)  │ │(Port 8005) │ │(Port 8006)  │
        └──────────────┘ └───────────┘ └─────────────┘
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │Notification  │ │Media Svc  │ │Analytics Svc│
        │Service       │ │(Port 8009)│ │(Port 8010)  │
        │(Port 8007)   │ └───────────┘ └─────────────┘
        └──────────────┘
```

## Technology Stack

### Core Framework
- **FastAPI**: High-performance async API framework
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization

### Databases
- **PostgreSQL**: Primary relational database for user data, mood tracking, journal entries
- **Redis**: Caching, session storage, real-time notifications, rate limiting
- **MongoDB**: Document storage for flexible content, community posts, media metadata
- **InfluxDB**: Time-series data for mood analytics and patterns
- **Elasticsearch**: Full-text search for journal entries, community content

### Security & Authentication
- **JWT**: Stateless authentication tokens
- **OAuth2**: Social login integration
- **bcrypt**: Password hashing
- **Rate Limiting**: Redis-based request throttling
- **CORS**: Cross-origin resource sharing

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Jaeger**: Distributed tracing
- **Structured Logging**: JSON-based logging with correlation IDs

### Message Queue & Event Streaming
- **Redis Pub/Sub**: Real-time notifications
- **Apache Kafka**: Event streaming for analytics
- **Celery**: Background task processing

## Service Breakdown

### 1. API Gateway (Port 8000)
- Request routing and load balancing
- Authentication validation
- Rate limiting and request throttling
- Request/response transformation
- API versioning and backward compatibility

### 2. Auth Service (Port 8001)
- User registration and authentication
- JWT token management
- Role-based access control (RBAC)
- OAuth2 social login integration
- Password reset and email verification

### 3. Profile Service (Port 8002)
- User profile management
- Preferences and settings
- Theme and personalization data
- Privacy controls

### 4. Mood Service (Port 8003)
- Mood tracking and analytics
- Journal entry management
- Habits tracking with streak calculations
- Insights generation using ML algorithms
- Pattern detection and trend analysis

### 5. Chatbot Service (Port 8004)
- AI-powered conversation handling
- Context-aware responses
- Mood inference from conversations
- Integration with external AI services
- Session management and history

### 6. Content Service (Port 8005)
- Affirmations and wellness content
- Personalized content recommendations
- Challenge and goal management
- Content categorization and tagging

### 7. Community Service (Port 8006)
- Forum and discussion management
- Post creation, likes, and comments
- Community moderation tools
- Event and challenge coordination
- User reputation system

### 8. Notification Service (Port 8007)
- Real-time push notifications
- Email notification system
- Notification preferences management
- Scheduled reminder system

### 9. Media Service (Port 8009)
- File upload and management
- Image processing and optimization
- Video/audio handling
- Content moderation and approval workflow

### 10. Analytics Service (Port 8010)
- Data aggregation and processing
- Machine learning model serving
- Predictive analytics for mood patterns
- Performance metrics and KPIs

## Data Models & Relationships

### User Management
```python
User -> Profile (1:1)
User -> MoodEntries (1:many)
User -> JournalEntries (1:many)
User -> Habits (1:many)
User -> CommunityPosts (1:many)
```

### Mood & Wellness
```python
MoodEntry -> MoodAnalytics (1:1)
JournalEntry -> SentimentAnalysis (1:1)
Habit -> HabitEvents (1:many)
User -> WeeklyInsights (1:many)
```

### Community & Social
```python
Forum -> Posts (1:many)
Post -> Comments (1:many)
Post -> Likes (1:many)
User -> CommunityReputation (1:1)
```

## Performance Optimizations

### Caching Strategy
- **Redis**: Session data, frequently accessed user profiles, API responses
- **Application-level**: In-memory caching for static content
- **Database**: Query result caching with intelligent invalidation

### Database Optimizations
- **Connection Pooling**: Efficient database connection management
- **Read Replicas**: Separate read/write database instances
- **Partitioning**: Time-based partitioning for mood and analytics data
- **Indexing**: Optimized indexes for common query patterns

### Async Processing
- **Background Tasks**: Heavy computations moved to background workers
- **Event-Driven Architecture**: Loose coupling between services
- **Stream Processing**: Real-time data pipeline for analytics

## Security Measures

### Authentication & Authorization
- JWT with short expiration times and refresh tokens
- Role-based access control (User, Moderator, Admin)
- API key authentication for service-to-service communication

### Data Protection
- Encryption at rest and in transit
- PII data anonymization for analytics
- GDPR compliance with data export/deletion
- Input validation and sanitization

### Infrastructure Security
- Rate limiting per user and IP
- DDoS protection at gateway level
- SQL injection prevention
- XSS protection headers

## Development & Deployment

### Local Development
```bash
# Start all services
docker-compose up -d

# Individual service development
cd services/auth_service
python -m uvicorn main:app --reload --port 8001
```

### Production Deployment
- **Containerization**: Docker containers for each service
- **Orchestration**: Kubernetes for container management
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Monitoring**: Comprehensive logging and alerting

## API Standards

### RESTful Design
- Consistent URL patterns
- Proper HTTP status codes
- Standardized error responses
- API versioning strategy

### Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Operation successful",
  "timestamp": "2024-01-20T12:00:00Z",
  "request_id": "uuid"
}
```

### Error Handling
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {}
  },
  "timestamp": "2024-01-20T12:00:00Z",
  "request_id": "uuid"
}
```

## Getting Started

1. **Prerequisites**
   - Python 3.11+
   - Docker & Docker Compose
   - PostgreSQL 14+
   - Redis 7+

2. **Installation**
   ```bash
   git clone <repository>
   cd mantrapath-backend
   docker-compose up -d
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Configure environment variables
   ```

4. **Database Migration**
   ```bash
   alembic upgrade head
   ```

5. **Start Development**
   ```bash
   make dev
   ```

## Testing Strategy

### Unit Tests
- Service-level testing with pytest
- Mock external dependencies
- Database testing with test containers

### Integration Tests
- End-to-end API testing
- Service communication testing
- Database integration testing

### Performance Tests
- Load testing with locust
- Database performance benchmarking
- Memory and CPU profiling

## Monitoring & Observability

### Metrics Collection
- Request/response times
- Database query performance
- Cache hit/miss ratios
- Error rates and patterns

### Alerting
- Service health monitoring
- Performance threshold alerts
- Error rate spike detection
- Resource utilization alerts

---

For detailed service documentation, see individual service README files in their respective directories.