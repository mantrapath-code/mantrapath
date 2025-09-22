# MantraPath Service Architecture

## 🏗️ Overview

MantraPath is a comprehensive mental health platform built with a microservices architecture. The system consists of 20+ specialized services that work together to provide personalized mental health support, AI-powered insights, and community features.

## 🎯 Core Architecture Principles

- **Microservices Architecture**: Each service has a single responsibility
- **Event-Driven Communication**: Services communicate via NATS JetStream events
- **API Gateway Pattern**: Centralized routing and authentication
- **AI-First Design**: AI services integrated throughout the platform
- **Cultural Intelligence**: Multi-language and culturally-aware features
- **Real-time Processing**: WebSocket support for live interactions

## 🏢 Service Categories

### 1. **Core Platform Services**

#### **API Gateway** (`api_gateway/`)
- **Port**: 8000
- **Purpose**: Central entry point, routing, authentication, rate limiting
- **Key Features**:
  - Request routing to appropriate services
  - JWT token validation and user authentication
  - Rate limiting and circuit breakers
  - CORS and security middleware
  - Voice command routing
  - AI context management
  - Cultural context processing
- **Routes**: All external API calls go through this service
- **Communication**: Routes requests to other services, publishes events

#### **Authentication Service** (`auth_service/`)
- **Port**: 8001
- **Purpose**: User registration, login, token management
- **Key Features**:
  - User registration with email verification
  - JWT token generation and validation
  - Password strength validation
  - Account cleanup for unverified users
  - Development login endpoint
- **Routes**:
  - `POST /register` - User registration
  - `POST /login` - User login
  - `POST /verify-email` - Email verification
  - `POST /refresh-token` - Token refresh
  - `GET /me` - Current user info
- **Communication**: Publishes user events, validates tokens for other services

#### **Profile Service** (`profile_service/`)
- **Port**: 8002
- **Purpose**: User profiles, preferences, and settings
- **Key Features**:
  - Profile management (bio, avatar, timezone)
  - Notification preferences
  - Theme and privacy settings
  - Language preferences (25+ languages)
  - Cultural region settings
- **Routes**:
  - `GET /api/profiles/me` - Get current profile
  - `PATCH /api/profiles/` - Update profile
  - `GET /api/preferences/` - Get preferences
  - `PUT /api/profile/language-preferences` - Language settings
- **Communication**: Updates user preferences, publishes profile events

### 2. **Mental Health Core Services**

#### **Mood Service** (`mood_service/`)
- **Port**: 8003
- **Purpose**: Mood tracking, analytics, and emotional insights
- **Key Features**:
  - Daily mood entry collection
  - Mood pattern analysis
  - Emotional weather forecasting
  - Celebration moment detection
  - Adaptive questioning
  - Cross-platform mood tracking
  - Memory integration
- **Routes**:
  - `POST /mood/entries` - Create mood entry
  - `GET /mood/entries` - Get mood history
  - `GET /mood/analytics` - Mood analytics
  - `GET /mood/patterns` - Pattern analysis
  - `GET /mood/weather` - Emotional weather
- **Communication**: Publishes mood events, integrates with memory service

#### **Memory Service** (`memory_service/`)
- **Port**: 8017
- **Purpose**: User interaction tracking and behavioral analysis
- **Key Features**:
  - Real statistics tracking
  - User interaction processing
  - Behavioral pattern analysis
  - Cultural context integration
  - Event-driven memory updates
- **Routes**:
  - `GET /memory/stats` - Get user statistics
  - `POST /memory/interaction` - Record interaction
  - `GET /memory/patterns` - Behavioral patterns
- **Communication**: Processes events from all services, provides insights

#### **Community Service** (`community_service/`)
- **Port**: 8004
- **Purpose**: Social features, challenges, and community support
- **Key Features**:
  - Community forums and threads
  - Challenge creation and participation
  - Event management
  - Social interactions (likes, comments)
  - Psychology-based community features
- **Routes**:
  - `GET /community/forums` - Get forums
  - `POST /community/posts` - Create posts
  - `GET /community/challenges` - Get challenges
  - `POST /community/challenges/{id}/join` - Join challenge
- **Communication**: Publishes community events, integrates with mood service

### 3. **AI and Intelligence Services**

#### **AI Event Processor** (`ai_event_processor/`)
- **Port**: 8014
- **Purpose**: Real-time AI analysis of all platform events
- **Key Features**:
  - Multi-language emotion analysis (25+ languages)
  - Cultural intelligence processing
  - Predictive intervention recommendations
  - Real-time event processing (<200ms latency)
  - Models Service integration
- **Routes**:
  - `POST /api/v1/emotion/analyze` - Emotion analysis
  - `POST /api/v1/cultural/analyze` - Cultural analysis
  - `POST /api/v1/predictive/analyze` - Risk assessment
- **Communication**: Processes events from all services, provides AI insights

#### **AI Context Store** (`ai_context_store/`)
- **Port**: 8015
- **Purpose**: Centralized AI context management and intelligence
- **Key Features**:
  - User context aggregation
  - Intelligence insights generation
  - Cross-service context building
  - Real-time context updates
  - Redis-based caching
- **Routes**:
  - `GET /api/v1/context/{user_id}` - Get user context
  - `POST /api/v1/context/update` - Update context
  - `GET /api/v1/intelligence/insights` - Get insights
- **Communication**: Aggregates data from all services, provides context

#### **Models Service** (`models_service/`)
- **Port**: 8080
- **Purpose**: Centralized AI model management and inference
- **Key Features**:
  - STT (Speech-to-Text) models
  - TTS (Text-to-Speech) models
  - NLP models for emotion analysis
  - Translation models
  - Model versioning and management
- **Routes**:
  - `POST /api/v1/stt/transcribe` - Speech transcription
  - `POST /api/v1/tts/synthesize` - Text synthesis
  - `POST /api/v1/nlp/analyze` - NLP analysis
  - `POST /api/v1/translate` - Translation
- **Communication**: Serves AI models to other services

#### **ML Service** (`ml_service/`)
- **Port**: 8008
- **Purpose**: Machine learning for personalized notifications and insights
- **Key Features**:
  - Smart notification scheduling
  - Mood pattern analysis
  - Crisis prediction
  - Early warning systems
  - Reinforcement learning for effectiveness
- **Routes**:
  - `POST /predict-timing` - Optimal notification timing
  - `POST /generate-content` - Personalized content
  - `POST /track-effectiveness` - ML effectiveness tracking
- **Communication**: Provides ML insights to notification service

### 4. **Communication Services**

#### **Chatbot Service** (`chatbot_service/`)
- **Port**: 8006
- **Purpose**: AI-powered conversational support
- **Key Features**:
  - Multi-language voice support
  - Platform-aware context
  - Cultural and sentiment analysis
  - Action orchestrator integration
  - Advanced conversation memory
- **Routes**:
  - `POST /chat/send` - Send message
  - `GET /chat/sessions` - Get chat sessions
  - `POST /chat/voice` - Voice interaction
- **Communication**: Integrates with AI services, action orchestrator

#### **Voice Service** (`voice_service/`)
- **Port**: 8009
- **Purpose**: Voice processing and synthesis
- **Key Features**:
  - Speech-to-text processing
  - Text-to-speech synthesis
  - Voice emotion analysis
  - Multi-language voice support
- **Routes**:
  - `POST /voice/transcribe` - Speech transcription
  - `POST /voice/synthesize` - Text synthesis
  - `POST /voice/analyze` - Voice emotion analysis
- **Communication**: Integrates with models service

#### **Translation Service** (`translation_service/`)
- **Port**: 8010
- **Purpose**: Multi-language translation and localization
- **Key Features**:
  - 25+ language support
  - Indian regional language focus
  - Cultural context adaptation
  - Real-time translation
- **Routes**:
  - `POST /translate` - Translate text
  - `GET /languages` - Supported languages
  - `POST /detect` - Language detection
- **Communication**: Provides translation to other services

### 5. **Content and Media Services**

#### **Content Service** (`content_service/`)
- **Port**: 8005
- **Purpose**: Article management and personalized recommendations
- **Key Features**:
  - Wellness content management
  - Personalized content feeds
  - Affirmations system
  - Bookmark functionality
  - Content search and filtering
- **Routes**:
  - `GET /content/feed` - Personalized feed
  - `GET /content/wellness` - Wellness content
  - `GET /affirmations` - Get affirmations
  - `POST /bookmark/{id}` - Bookmark content
- **Communication**: Publishes content recommendation events

#### **Media Service** (`media_service/`)
- **Port**: 8011
- **Purpose**: Media file management and processing
- **Key Features**:
  - File upload and storage
  - Image processing
  - Video processing
  - Media optimization
  - CDN integration
- **Routes**:
  - `POST /upload` - Upload media
  - `GET /media/{id}` - Get media
  - `DELETE /media/{id}` - Delete media
- **Communication**: Handles media requests from other services

### 6. **Notification and Communication**

#### **Notification Service** (`notification_service/`)
- **Port**: 8007
- **Purpose**: Push notifications and real-time messaging
- **Key Features**:
  - WebSocket support for real-time notifications
  - ML-powered smart notifications
  - Notification preferences management
  - Crisis alerts
  - Weekly reports
- **Routes**:
  - `POST /notify/send` - Send notification
  - `GET /notifications` - Get notifications
  - `WebSocket /ws/{user_id}` - Real-time connection
- **Communication**: Receives events from all services, sends notifications

### 7. **Orchestration and Deployment**

#### **Action Orchestrator** (`action_orchestrator/`)
- **Port**: 8012
- **Purpose**: Cross-service workflow coordination
- **Key Features**:
  - Voice-driven workflows
  - Service coordination
  - Epic workflow management
  - Action chaining
- **Routes**:
  - `POST /orchestrate/action` - Execute action
  - `GET /orchestrate/status` - Get status
- **Communication**: Coordinates actions across multiple services

#### **Deployment API** (`deployment_api/`)
- **Port**: 8013
- **Purpose**: Controlled API access for frontend engineers
- **Key Features**:
  - API documentation
  - Model training status
  - Service health monitoring
  - Usage tracking
- **Routes**:
  - `GET /api/docs` - API documentation
  - `GET /api/health` - Service health
  - `GET /api/models/status` - Model status
- **Communication**: Provides deployment and monitoring information

### 8. **Specialized Services**

#### **Proactive Assistance Engine** (`proactive_assistance_engine/`)
- **Port**: 8016
- **Purpose**: Proactive mental health interventions
- **Key Features**:
  - Early intervention detection
  - Proactive support triggers
  - Crisis prevention
  - Wellness recommendations
- **Communication**: Monitors user patterns, triggers interventions

#### **Phi3 Agent** (`phi3_agent/`)
- **Port**: 8018
- **Purpose**: Advanced AI agent for complex interactions
- **Key Features**:
  - Advanced reasoning
  - Complex problem solving
  - Multi-step interactions
- **Communication**: Handles complex AI interactions

## 🔄 Service Communication Patterns

### 1. **Synchronous Communication**
- **HTTP/REST APIs**: Direct service-to-service calls
- **API Gateway**: All external requests routed through gateway
- **Service Discovery**: Services discover each other via configuration

### 2. **Asynchronous Communication**
- **NATS JetStream**: Event-driven communication
- **Event Types**:
  - `mood.entry.created` - Mood tracking events
  - `journal.entry.created` - Journal events
  - `voice.activity_detected` - Voice events
  - `community.post.created` - Community events
  - `ai.insight.generated` - AI insight events
  - `notification.sent` - Notification events

### 3. **Real-time Communication**
- **WebSockets**: Real-time notifications and updates
- **Server-Sent Events**: Live data streaming
- **Event Bus**: Real-time event distribution

## 🗄️ Data Flow Architecture

### 1. **User Request Flow**
```
User → API Gateway → Authentication → Service Router → Target Service → Response
```

### 2. **Event Processing Flow**
```
Service A → Event Bus → AI Event Processor → Context Store → Notification Service → User
```

### 3. **AI Processing Flow**
```
User Input → Voice/Text Service → Models Service → AI Event Processor → Context Store → Response
```

## 🔐 Security Architecture

### 1. **Authentication & Authorization**
- **JWT Tokens**: Stateless authentication
- **Role-based Access**: User roles and permissions
- **API Key Management**: Service-to-service authentication

### 2. **Data Security**
- **Encryption**: Data encrypted in transit and at rest
- **Privacy Controls**: User privacy preferences respected
- **GDPR Compliance**: Data protection and user rights

### 3. **Service Security**
- **Rate Limiting**: Prevents abuse and DoS attacks
- **Circuit Breakers**: Prevents cascade failures
- **Input Validation**: Comprehensive input sanitization

## 📊 Monitoring and Observability

### 1. **Health Checks**
- Each service provides `/health` endpoint
- Centralized health monitoring
- Service dependency tracking

### 2. **Logging**
- Structured logging across all services
- Centralized log aggregation
- Request tracing and correlation

### 3. **Metrics**
- Performance metrics collection
- Business metrics tracking
- Real-time monitoring dashboards

## 🚀 Deployment Architecture

### 1. **Containerization**
- Docker containers for all services
- Docker Compose for local development
- Kubernetes for production deployment

### 2. **Service Discovery**
- Service registry for dynamic discovery
- Load balancing and failover
- Health check integration

### 3. **Scaling**
- Horizontal scaling for stateless services
- Database scaling strategies
- Caching layers for performance

## 🔧 Technology Stack

### **Backend Technologies**
- **Python 3.11+**: Primary language
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **NATS JetStream**: Event streaming

### **AI/ML Technologies**
- **PyTorch**: Deep learning framework
- **Transformers**: NLP models
- **scikit-learn**: Machine learning
- **NLTK/spaCy**: Natural language processing

### **Infrastructure**
- **Docker**: Containerization
- **Kubernetes**: Orchestration
- **Nginx**: Load balancing
- **Prometheus**: Monitoring
- **Grafana**: Visualization

## 📈 Scalability Considerations

### 1. **Service Scaling**
- Stateless service design
- Horizontal scaling capabilities
- Database connection pooling
- Caching strategies

### 2. **Performance Optimization**
- CDN for static content
- Database indexing strategies
- Query optimization
- Background job processing

### 3. **Reliability**
- Circuit breaker patterns
- Retry mechanisms
- Graceful degradation
- Disaster recovery plans

This architecture provides a robust, scalable, and maintainable foundation for the MantraPath mental health platform, enabling personalized, AI-powered support for users worldwide.
