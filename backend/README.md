# MantraPath Backend - Complete Microservices Architecture

## Overview
MantraPath backend is a comprehensive microservices architecture built with FastAPI, designed to handle mental wellness applications at scale. The system consists of 8 microservices with proper authentication, caching, and data persistence.

## Architecture

### Core Services
1. **API Gateway** (Port 8000) - Main entry point with routing and load balancing
2. **Auth Service** (Port 8001) - Authentication, authorization, and user management
3. **Profile Service** (Port 8002) - User profiles and preferences
4. **Mood Service** (Port 8003) - Mood tracking, analytics, and insights
5. **Chatbot Service** (Port 8004) - AI-powered wellness chatbot
6. **Content Service** (Port 8005) - Content management and recommendations
7. **Community Service** (Port 8006) - Forums, discussions, and social features
8. **Notification Service** (Port 8007) - Push notifications and alerts
9. **Media Service** (Port 8009) - File uploads and media management

### Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session management and caching
- **Authentication**: JWT tokens with refresh mechanism
- **Message Queue**: Redis Pub/Sub for inter-service communication
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Containerization**: Docker with docker-compose

### Key Features
- **Scalable Architecture**: Each service can be scaled independently
- **Data Consistency**: ACID transactions with proper isolation
- **Real-time Features**: WebSocket support for live updates
- **Security**: JWT authentication, rate limiting, input validation
- **Observability**: Comprehensive logging and health checks
- **Performance**: Redis caching, connection pooling, async operations

## Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Installation
```bash
# Clone and setup
cd backend
pip install -r requirements.txt

# Start infrastructure
docker-compose up -d postgres redis

# Initialize databases
python scripts/init_db.py

# Start all services
./scripts/start_services.sh
```

### Environment Configuration
Copy `.env.example` to `.env` and configure:
```env
DATABASE_URL=postgresql://mantrapath:password@localhost:5432/mantrapath
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Service Details

### API Gateway (8000)
- Request routing to appropriate services
- Rate limiting and authentication middleware
- Load balancing and health monitoring
- Centralized CORS and security headers

### Auth Service (8001)
- User registration and login
- JWT token management (access + refresh)
- Role-based access control (RBAC)
- Password reset and email verification
- Admin user management

### Profile Service (8002)
- User profile management
- Preferences and settings
- Privacy controls
- Profile customization
- Theme and notification preferences

### Mood Service (8003)
- Mood entry tracking with timestamps
- Journal entries with sentiment analysis
- Habit tracking and streaks
- Advanced analytics and insights
- Pattern recognition and predictions
- Weekly/monthly reports

### Chatbot Service (8004)
- AI-powered conversation engine
- Session management
- Sentiment analysis integration
- Crisis detection and response
- Breathing exercises and guided activities
- Chat history and analytics

### Content Service (8005)
- Article and resource management
- Personalized content recommendations
- Affirmations and daily quotes
- Bookmark system
- Content categorization and search
- Reading progress tracking

### Community Service (8006)
- Forum management with categories
- Thread and post creation
- Like/comment system
- User reputation and moderation
- Community events and challenges
- Reporting and safety features

### Notification Service (8007)
- Push notification delivery
- Email notifications
- In-app notification center
- Notification preferences
- Scheduled notifications
- Event-driven notifications

### Media Service (8009)
- File upload and storage
- Image/video processing
- Media moderation queue
- Thumbnail generation
- Media analytics
- CDN integration ready

## API Documentation

Each service exposes comprehensive API documentation:
- Swagger UI: `http://localhost:{port}/docs`
- ReDoc: `http://localhost:{port}/redoc`
- OpenAPI JSON: `http://localhost:{port}/openapi.json`

## Database Schema

The system uses a multi-database approach:
- **Core DB**: Users, profiles, authentication
- **Mood DB**: Mood entries, journal, habits, analytics
- **Community DB**: Forums, posts, comments, likes
- **Content DB**: Articles, affirmations, bookmarks
- **Media DB**: File metadata and processing status

## Security

### Authentication Flow
1. User registers/logs in via Auth Service
2. Receives JWT access token (30min) + refresh token (7 days)
3. All API requests include Bearer token
4. Gateway validates tokens with Auth Service
5. Automatic token refresh when needed

### Data Protection
- All passwords hashed with bcrypt
- Sensitive data encrypted at rest
- Input validation and sanitization
- SQL injection prevention
- Rate limiting on all endpoints
- CORS configuration

## Monitoring and Observability

### Health Checks
Each service provides multiple health endpoints:
- `/health` - Basic service status
- `/health/detailed` - Comprehensive health info
- `/health/live` - Kubernetes liveness probe
- `/health/ready` - Kubernetes readiness probe

### Logging
- Structured JSON logging
- Request/response logging
- Error tracking with stack traces
- Performance metrics
- User activity logs (privacy compliant)

### Metrics
- Prometheus-compatible metrics endpoint
- Request latency and throughput
- Database connection pool status
- Cache hit rates
- Error rates by endpoint

## Development

### Running Locally
```bash
# Start individual service
cd services/auth_service
uvicorn main:app --reload --port 8001

# Or use the helper script
./scripts/dev_start.sh auth

# Run tests
pytest services/auth_service/tests/
```

### Adding New Features
1. Define data models in `models/`
2. Create database migrations in `alembic/`
3. Implement business logic in `services/`
4. Add API endpoints in `routers/`
5. Write comprehensive tests
6. Update API documentation

### Database Migrations
```bash
# Create migration
cd services/mood_service
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head
```

## Production Deployment

### Docker Deployment
```bash
# Build all services
docker-compose build

# Deploy with scaling
docker-compose up -d --scale mood_service=3 --scale community_service=2
```

### Kubernetes
See `k8s/` directory for Kubernetes manifests:
- Service deployments
- ConfigMaps and Secrets
- Ingress configuration
- Persistent volume claims

### Performance Optimization
- Connection pooling for databases
- Redis caching for frequent queries
- Background task processing
- Database indexing strategy
- Query optimization
- Response compression

## API Usage Examples

### Authentication
```python
# Register user
POST /auth/register
{
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "John Doe"
}

# Login
POST /auth/login
{
    "email": "user@example.com", 
    "password": "securepassword"
}
```

### Mood Tracking
```python
# Log mood
POST /api/v1/mood/
{
    "mood_score": 7,
    "energy_level": 6,
    "context_tags": ["work", "exercise"],
    "notes": "Great day at work"
}

# Get analytics
GET /api/v1/analytics/overview?period=week
```

### Community
```python
# Create forum post
POST /forums/thread
{
    "forum_id": "anxiety-support",
    "title": "Dealing with work stress",
    "content": "Anyone have tips for managing workplace anxiety?"
}

# Like a post
POST /forums/like
{
    "content_type": "thread",
    "content_id": "123"
}
```

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Submit pull request with detailed description

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For questions and support:
- Create GitHub issue for bugs
- Check documentation at `/docs`
- Review API specs at service endpoints
- Contact team for deployment assistance