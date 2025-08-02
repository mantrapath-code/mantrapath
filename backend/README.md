# MantraPath Backend - Comprehensive Technical Documentation

## Executive Overview

**MantraPath Backend** is a sophisticated microservices architecture designed for a holistic mental wellness platform. The system comprises 10 specialized services orchestrated through an advanced API Gateway, implementing both Phase 1 (core functionality) and Phase 2 (advanced features) architecture patterns.

### System Architecture Philosophy
- **Microservices Design**: Each service owns its domain with clear boundaries
- **Database Polyglot**: Multiple database technologies optimized for specific use cases
- **Event-Driven Communication**: Real-time data synchronization across services
- **Hybrid Phase Implementation**: Phase 1/2 architecture for graceful degradation
- **GDPR Compliance**: Complete data privacy and deletion capabilities

## Service Architecture Matrix

| Service | Port | Database | Cache | Primary Functions | Phase Status |
|---------|------|----------|-------|-------------------|--------------|
| **API Gateway** | 8000 | - | Redis | Routing, Rate Limiting, Circuit Breakers | Phase 2 ✅ |
| **Auth Service** | 8001 | PostgreSQL | Redis | JWT Management, RBAC, Token Validation | Phase 1/2 Hybrid ✅ |
| **Profile Service** | 8002 | MongoDB | Redis | User Profiles, Privacy Settings, File Storage | Phase 1/2 Hybrid ✅ |
| **Mood Service** | 8003 | PostgreSQL | Redis | Mood Tracking, Analytics, Adaptive Features | Phase 1 ✅ |
| **Chatbot Service** | 8004 | PostgreSQL | Redis | AI Conversations, Context Management | Phase 1 ✅ |
| **Content Service** | 8005 | PostgreSQL | Redis | Content Management, Bookmarking | Phase 1 ✅ |
| **Community Service** | 8006 | PostgreSQL | Redis | Forums, Discussions, Social Features | Phase 1 ✅ |
| **Notification Service** | 8007 | PostgreSQL | Redis | Real-time Notifications, Scheduling | Phase 1 ✅ |
| **Media Service** | 8009 | PostgreSQL | Redis | Media Processing, Thumbnails, Engagement | Phase 1/2 Hybrid ✅ |
| **ML Service** | 8010 | File System | Memory | Pattern Analysis, ML Models, Predictions | Phase 1 ✅ |

## Database Integration Architecture

### PostgreSQL Integration (Primary Database)
**Services**: Auth, Mood, Chatbot, Content, Community, Notification, Media
- **Connection Pool**: 20 base connections, 30 max overflow
- **Health Checks**: Pool pre-ping enabled, 1-hour recycle
- **Cross-Service Relations**: User ID foreign keys across all services

### MongoDB Integration (Document Store) 
**Service**: Profile Service
- **GridFS**: Profile picture and file storage
- **Document Structure**: User profiles with privacy settings, mental health info
- **Indexing**: User ID, email, privacy settings for optimal queries

### Redis Caching Strategy
**All Services**: Multi-level caching architecture
- **Auth**: JWT token blacklist, session management  
- **Profile**: User profile data, preference caching
- **Mood**: Analytics results, pattern analysis cache
- **Media**: Thumbnail cache, processing status
- **Notification**: Unread counts, delivery status

## Inter-Service Communication Framework

### Authentication-Based Communication
- **Service-to-Service**: JWT token verification via Auth Service
- **Centralized Authorization**: User permissions fetched from Auth Service
- **Token Revocation**: Real-time blacklist checking across services

### Event-Driven Communication (Phase 2)
- **Redis Pub/Sub**: Cross-service event publishing
- **Event Types**: user.created, mood.entry_created, media.uploaded, user.deleted
- **GDPR Events**: Coordinated data deletion across all services

## Core Service Technical Implementation

### Auth Service (Port 8001) - Identity & Access Management
**Database**: PostgreSQL with users, roles, permissions, JWT tokens tables
**Key Features**:
- JWT token management with JTI-based revocation
- Role-based access control (RBAC) with hierarchical permissions  
- Service-to-service token verification endpoint
- Password hashing with bcrypt (12 rounds)
**API Endpoints**: /auth/register, /auth/login, /auth/refresh, /auth/verify-token
**Use Cases**: User registration, authentication, cross-service authorization

### Profile Service (Port 8002) - User Profile & Preferences
**Database**: MongoDB with GridFS for file storage
**Key Features**:
- Comprehensive user profile management
- Privacy-aware data access controls
- Mental health information with consent management
- Profile picture storage with GridFS
**API Endpoints**: /profile/{user_id}, /profile/{user_id}/picture, /profile/preferences
**Use Cases**: Profile management, privacy controls, file storage, GDPR compliance

### Mood Service (Port 8003) - Mood Tracking & Analytics
**Database**: PostgreSQL with mood_entries, adaptive_questions, emotional_weather tables
**Key Features**:
- Multi-dimensional mood tracking (mood, energy, stress, sleep)
- AI-powered adaptive questioning system
- Emotional weather forecasting
- ML integration for pattern analysis
**API Endpoints**: /mood/entries, /mood/analytics, /mood/adaptive-questions, /mood/emotional-weather
**Use Cases**: Mood tracking, analytics, risk assessment, personalized insights

### Media Service (Port 8009) - Media Processing & Management
**Database**: PostgreSQL with media_files, media_reactions, media_views tables
**Key Features**:
- Multi-format media support (images, videos, audio)
- Automatic thumbnail and preview generation
- Engagement tracking (views, reactions)
- Content moderation pipeline
**API Endpoints**: /media/upload, /media/{id}/stream, /media/{id}/react
**Use Cases**: Media upload, processing, streaming, engagement analytics

### ML Service (Port 8010) - Machine Learning & Analytics
**Storage**: File system for model persistence, memory for active models
**Key Features**:
- Advanced ML models (RandomForest, KMeans, IsolationForest)
- 17 engineered features for mood analysis
- Pattern recognition and anomaly detection
- Optimal timing prediction for notifications
**API Endpoints**: /ml/analyze-patterns, /ml/predict-timing, /ml/detect-anomalies
**Use Cases**: Mood pattern analysis, risk prediction, personalized recommendations

## Security & Performance Architecture

### Security Implementation
- **JWT Tokens**: HS256 algorithm with JTI for revocation
- **Password Security**: bcrypt hashing with 12 rounds
- **API Security**: Bearer token authentication across all services
- **GDPR Compliance**: Complete data deletion endpoints in all services

### Performance Optimization  
- **Database Connection Pooling**: Optimized for each service's load
- **Redis Caching**: Multi-level caching strategy across services
- **Event-Driven Architecture**: Asynchronous processing for better performance
- **Load Balancing**: API Gateway with circuit breakers and rate limiting

## Development & Deployment

### Getting Started
```bash
# Install dependencies
pip install -r requirements.txt

# Start all services
./start-dev.sh

# Access API documentation
# API Gateway: http://localhost:8000/docs
# Individual services: http://localhost:{port}/docs
```

### Docker Deployment
```bash
# Start entire stack with Docker Compose
docker-compose up -d

# Phase 2 infrastructure included:
# - Consul (service discovery)
# - Redis (caching)
# - PostgreSQL (primary DB)
# - MongoDB (document store)
# - RabbitMQ (message broker)
```

### Environment Configuration
- **Development**: Local PostgreSQL, Redis, file storage
- **Production**: Distributed databases, cloud storage, monitoring
- **Phase 2**: Advanced features with service discovery, circuit breakers

## Phase Implementation Status

### Phase 1 ✅ COMPLETE
- All 10 services properly separated with clean boundaries
- GDPR compliance implemented across all services  
- Service-to-service authentication established
- Core functionality implemented for all domains

### Phase 2 🔄 PARTIALLY IMPLEMENTED
- Docker-compose with comprehensive infrastructure
- API Gateway with circuit breakers and rate limiting
- Redis pub/sub for event-driven communication
- Service discovery with Consul configured
- Advanced caching strategies implemented

### Future Enhancements
- Advanced monitoring and alerting
- Kubernetes orchestration
- Advanced ML features and real-time predictions
- Enhanced security with OAuth2 and advanced MFA