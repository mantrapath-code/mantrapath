# MantraPath Backend - Complete Microservices Architecture

This backend provides a complete, production-ready microservices architecture for the MantraPath mental wellness application.

## 🏗️ Architecture Overview

The backend consists of 8 microservices, all orchestrated through a central API Gateway:

- **API Gateway** (Port 8000) - Central routing and load balancing
- **Auth Service** (Port 8001) - Authentication and user management
- **Profile Service** (Port 8002) - User profiles and preferences
- **Mood Service** (Port 8003) - Mood tracking, analytics, and insights
- **Chatbot Service** (Port 8004) - AI-powered conversational support
- **Content Service** (Port 8005) - Content management and recommendations
- **Community Service** (Port 8006) - Forums, threads, and social features
- **Notification Service** (Port 8007) - Push notifications and alerts
- **Media Service** (Port 8009) - File uploads and media management

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ 
- PostgreSQL 15+
- Redis 7+

### Option 1: Docker Compose (Recommended)

```bash
cd backend
docker-compose up -d
```

This will start all services, PostgreSQL, and Redis automatically.

### Option 2: Local Development

1. **Setup Database & Redis**
   ```bash
   # Install PostgreSQL and Redis locally
   # Create database 'mantrapath' with user 'mantrapath'
   ```

2. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start Services**
   ```bash
   # Make the startup script executable and run
   bash start-dev.sh
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://mantrapath:mantrapath123@localhost:5432/mantrapath

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# AI Services (Optional)
OPENAI_API_KEY=your-openai-api-key

# Service URLs (for development)
AUTH_SERVICE_URL=http://localhost:8001
PROFILE_SERVICE_URL=http://localhost:8002
MOOD_SERVICE_URL=http://localhost:8003
CHATBOT_SERVICE_URL=http://localhost:8004
CONTENT_SERVICE_URL=http://localhost:8005
COMMUNITY_SERVICE_URL=http://localhost:8006
NOTIFICATION_SERVICE_URL=http://localhost:8007
MEDIA_SERVICE_URL=http://localhost:8009
```

## 📊 Database Schema

The system uses PostgreSQL with the following key tables:

- `users` - User accounts and authentication
- `user_profiles` - Extended user information
- `mood_entries` - Daily mood tracking data
- `journal_entries` - User journal posts with sentiment analysis
- `chat_sessions` & `chat_messages` - Chatbot conversations
- `forums`, `forum_threads`, `forum_replies` - Community features
- `likes` - Social interactions
- `notifications` - User notifications
- `media` - File uploads and attachments

## 🛡️ Security Features

- JWT-based authentication with refresh tokens
- Role-based access control (user, moderator, admin)
- Input validation and sanitization
- CORS protection
- Rate limiting (production ready)
- Secure password hashing with bcrypt

## 📈 Key Features

### Mood Service
- Real-time mood tracking with multiple dimensions
- Advanced analytics and pattern recognition
- Weekly trend analysis with automatic alerts
- Correlation analysis between activities and mood
- Predictive modeling for intervention timing

### Chatbot Service
- Context-aware conversational AI
- Integrated breathing exercises
- Crisis detection and response
- Session management and history
- Sentiment analysis for mood inference

### Community Service
- Multi-forum discussion system
- Threaded conversations with replies
- Like/reaction system
- Moderation tools and content reporting
- User reputation and roles

### Analytics & Insights
- Personal wellness dashboards
- Trend analysis and pattern detection
- Automated insights generation
- Health score calculations
- Intervention recommendations

## 🔌 API Endpoints

All requests go through the API Gateway at `http://localhost:8000`

### Authentication
- `POST /register` - Create new account
- `POST /login` - User login
- `POST /refresh-token` - Refresh access token
- `GET /me` - Get current user info

### Mood Tracking
- `GET/POST /api/v1/mood/` - Mood entries
- `GET /api/v1/analytics/overview` - Wellness analytics
- `GET /api/v1/analytics/patterns/weekly` - Pattern analysis

### Journal
- `GET/POST /api/v1/journal/` - Journal entries with sentiment analysis

### Community
- `GET /forums` - List forums
- `POST /forums/{id}/join` - Join forum
- `GET /forums/{id}/threads` - Forum threads
- `POST /forums/thread` - Create thread
- `POST /forums/thread/{id}/reply` - Reply to thread

### Chatbot
- `POST /api/chatbot/chat` - Send message to AI
- `GET /api/chatbot/chat/sessions` - Chat history
- `GET /api/chatbot/breathing-exercises` - Wellness exercises

## 🧪 Testing

Run the test suite:

```bash
cd backend
pytest
```

## 🚀 Production Deployment

### Using Docker

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment

1. Set production environment variables
2. Configure reverse proxy (nginx recommended)
3. Set up SSL certificates
4. Configure database backups
5. Set up monitoring and logging

## 📊 Monitoring & Observability

- Health check endpoints for all services (`/health`)
- Prometheus metrics exposed at `/metrics`
- Structured logging with correlation IDs
- Request/response timing and error tracking

## 🔄 Development Workflow

1. **Add New Features**: Extend existing services or create new microservices
2. **Database Changes**: Use Alembic migrations for schema updates
3. **API Changes**: Update OpenAPI docs automatically
4. **Testing**: Add unit and integration tests
5. **Deployment**: Use CI/CD with Docker containers

## 📚 API Documentation

When services are running, visit:
- **API Gateway**: http://localhost:8000/docs
- **Individual Services**: http://localhost:{port}/docs

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add proper error handling and logging
3. Include unit tests for new features
4. Update API documentation
5. Follow security best practices

## 📝 License

This project is licensed under the MIT License.

---

**Note**: This backend is designed to scale horizontally and can handle thousands of concurrent users. For production use, ensure proper infrastructure monitoring, database optimization, and security hardening.