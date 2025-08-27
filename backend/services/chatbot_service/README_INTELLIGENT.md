# MantraPath Intelligent Chatbot Service

## 🚀 Overview

The MantraPath Intelligent Chatbot Service represents a revolutionary evolution from basic keyword-based responses to a sophisticated, AI-powered therapeutic companion. This service integrates a locally-running **Phi-3 Mini AI agent** with comprehensive mood awareness, ML-driven learning, and robust security validation to provide personalized mental health support.

**Version**: 3.0.0 (Phi-3 Mini + Intelligent Engine)  
**Status**: Phase 2 Complete - Production Ready  
**Architecture**: FastAPI + Phi-3 Mini Agent + ML Learning + Security Framework  
**Primary Model**: Microsoft Phi-3 Mini 4K Instruct (3.8B parameters)  
**Deployment**: Docker + vLLM for GPU acceleration

## 🧠 Core Intelligence Features

### 🤖 Phi-3 Mini AI Agent Integration
- **Local AI Processing**: Microsoft Phi-3 Mini 4K Instruct (3.8B parameters)
- **vLLM Acceleration**: GPU-optimized inference with 40-60 tokens/second
- **Conversation Memory**: 4,096 token context for conversation continuity
- **Therapeutic Alignment**: Fine-tuned for mental health and wellness conversations
- **Graceful Fallback**: Automatic fallback to mood-aware responder if agent unavailable

### 🧪 ML-Driven Learning & Analytics
- **Conversation Analytics**: Real-time emotional state and communication style analysis
- **Response Optimization**: ML-powered prompt optimization for therapeutic effectiveness
- **Pattern Recognition**: Behavioral pattern detection for personalized interventions
- **Continuous Learning**: System learns from conversations to improve response quality
- **Performance Tracking**: Conversation success metrics and user satisfaction analysis

### 🛡️ Advanced Security & Safety
- **Comprehensive Threat Detection**: Multi-layer security validation and content filtering
- **Crisis Intervention**: Advanced suicide/self-harm detection with immediate response protocols
- **Input Sanitization**: Robust input validation and injection prevention
- **Professional Boundaries**: Automated boundary management and therapeutic context maintenance
- **Audit Logging**: Complete security event tracking for compliance and safety

### 🔗 Multi-Service Data Integration
- **User Profile Service** (Port 8002): Personal preferences, mental health info, privacy settings
- **Auth Service** (Port 8001): User authentication, session management, security context
- **Community Service** (Port 8005): Social engagement patterns, support group interactions
- **Content Service** (Port 8006): Learning material consumption, bookmark preferences
- **Media Service** (Port 8007): Media interaction history and engagement analytics
- **Admin Service** (Port 8010): Moderation context and user safety flags

### 🎯 Context-Aware Conversation Analysis
- **Intent Recognition**: Multi-modal intent classification with therapeutic context
- **Emotional Intelligence**: Real-time emotional state assessment and response adaptation
- **Conversation Flow Management**: Session continuity, topic transitions, closure handling
- **Personalization Engine**: Individual communication style adaptation and preference learning
- **Intervention Triggers**: Automated detection of crisis situations requiring immediate attention

## 🏗️ Architecture

### Directory Structure
```
chatbot_service/
├── main_intelligent.py          # FastAPI service with intelligent endpoints
├── agent_service.py             # Phi-3 Mini AI agent service integration
├── ml_learning.py               # ML learning components for conversation analytics
├── security_manager.py          # Security validation and threat detection
├── docker-compose.agent.yml     # Docker deployment for Phi-3 Mini with vLLM
├── intelligent_engine/
│   ├── response_generator.py    # Enhanced response orchestration with agent integration
│   ├── mood_aware_responder.py  # Mood-aware response generation (fallback)
│   ├── service_integrator.py    # Multi-service data integration
│   └── context_analyzer.py      # Conversation context analysis
├── enhancement/plan/
│   ├── LOCAL_AGENT_INTEGRATION.md    # Integration documentation
│   ├── MODEL_RECOMMENDATIONS.md      # Model selection guide
│   └── IMPLEMENTATION_TEMPLATE.md    # Development templates
├── README_INTELLIGENT.md        # Comprehensive technical documentation
├── main.py                      # Deprecated (redirects to main_intelligent)
└── requirements.txt             # Python dependencies
```

### Component Architecture

#### 1. **Phi-3 Mini Agent Service** (`agent_service.py`)
- **Phi3AgentService**: Main service class for AI agent integration
- **Local Agent Manager**: vLLM API communication and model management
- **ML Learning Integration**: Real-time conversation analytics and learning updates
- **Performance Tracking**: Response time, quality metrics, and resource monitoring
- **Health Monitoring**: Service health, model status, and availability checks

#### 2. **ML Learning System** (`ml_learning.py`)
- **ConversationAnalytics**: Emotional state analysis, communication style assessment
- **ResponseOptimizer**: Therapeutic effectiveness scoring and prompt optimization
- **PatternRecognizer**: Behavioral pattern detection and intervention recommendations
- **Redis Integration**: ML insights caching and learning data persistence

#### 3. **Security Framework** (`security_manager.py`)
- **SecurityManager**: Comprehensive threat detection and content validation
- **InputValidator**: Format validation and data integrity checks
- **Crisis Detection**: Advanced self-harm/suicide detection with urgency classification
- **Professional Boundaries**: Therapeutic context maintenance and boundary violation detection

#### 4. **Enhanced Response Generator** (`intelligent_engine/response_generator.py`)
- **Agent Integration**: Seamless Phi-3 Mini agent integration with fallback
- **Response Orchestration**: Multi-service data coordination and response synthesis
- **Context Management**: Conversation memory and user context preservation
- **Quality Assurance**: Response validation and therapeutic alignment verification

## 🔌 Service Data Integration

The chatbot service integrates with **6 core MantraPath services** to provide comprehensive, personalized therapeutic support:

### **1. Auth Service** (Port 8001) - `http://auth-service:8001`
**Data Retrieved:**
- User authentication status and session validation
- Security context and access permissions
- User role and authorization level
- Session expiration and token refresh status

**Integration Method:** JWT token validation endpoint `/auth/verify-token`
**Usage:** Security validation for all chat interactions

### **2. Profile Service** (Port 8002) - `http://profile-service:8002`
**Data Retrieved:**
- Personal preferences and communication style
- Mental health information and therapeutic history
- Privacy settings and consent preferences
- User demographics and personalization data
- Profile completeness score and engagement metrics

**Key Endpoints:**
- `/profile/{user_id}` - Complete user profile
- `/profile/{user_id}/preferences` - Communication preferences
- `/profile/{user_id}/mental-health-info` - Therapeutic context

**Integration Method:** Direct HTTP API calls with profile caching
**Usage:** Personalizing response tone, therapeutic approach, and intervention strategies

### **3. Community Service** (Port 8005) - `http://community-service:8005`
**Data Retrieved:**
- Support group participation and engagement levels
- Social interaction patterns and peer relationships
- Community contribution history and peer support activities
- Group therapy session participation and outcomes

**Key Endpoints:**
- `/community/{user_id}/activity` - Community engagement metrics
- `/community/{user_id}/support-groups` - Active support groups
- `/community/{user_id}/peer-interactions` - Social support context

**Integration Method:** Async API calls with community context caching
**Usage:** Understanding social support context and recommending community resources

### **4. Content Service** (Port 8006) - `http://content-service:8006`
**Data Retrieved:**
- Learning material consumption patterns and preferences
- Educational content progress and completion rates
- Bookmarked resources and favorite therapeutic content
- Content engagement analytics and learning outcomes

**Key Endpoints:**
- `/content/{user_id}/consumption-patterns` - Learning behavior analysis
- `/content/{user_id}/bookmarks` - Saved therapeutic resources
- `/content/{user_id}/progress` - Educational advancement tracking

**Integration Method:** HTTP API with content preference caching
**Usage:** Recommending relevant therapeutic content and educational resources

### **5. Media Service** (Port 8007) - `http://media-service:8007`
**Data Retrieved:**
- Media consumption patterns (guided meditations, therapy videos)
- Engagement metrics with wellness media content
- Preferred media formats and therapeutic content types
- Media interaction history and effectiveness ratings

**Key Endpoints:**
- `/media/{user_id}/wellness-content` - Therapeutic media consumption
- `/media/{user_id}/engagement-metrics` - Media interaction analytics

**Integration Method:** Async API calls with media preference caching
**Usage:** Recommending appropriate wellness media and tracking engagement effectiveness

### **6. Admin Service** (Port 8010) - `http://admin-service:8010`
**Data Retrieved:**
- User safety flags and moderation context
- Crisis intervention history and follow-up status
- Admin notes and therapeutic observations
- Risk assessment scores and safety protocols

**Key Endpoints:**
- `/admin/{user_id}/safety-context` - Safety flags and risk assessment
- `/admin/{user_id}/moderation-history` - Previous interventions

**Integration Method:** Secure API calls with safety context validation
**Usage:** Crisis prevention, safety monitoring, and intervention coordination

## 🤖 Phi-3 Mini Agent Integration

### **Local AI Agent Architecture**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Chat Request  │───▶│  Response        │───▶│   Phi-3 Mini    │
│   + User Data   │    │  Generator       │    │   AI Agent      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   ML Learning    │    │   vLLM Server   │
                       │   Analytics      │    │   (Port 8080)   │
                       └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Redis Cache    │    │  Security       │
                       │   (ML Insights)  │    │  Validation     │
                       └──────────────────┘    └─────────────────┘
```

### **Agent Service Components**

#### **Phi3AgentService** (`agent_service.py`)
- **Model**: Microsoft Phi-3 Mini 4K Instruct (3.8B parameters)
- **Serving**: vLLM with OpenAI-compatible API
- **Performance**: 40-60 tokens/second, ~2.5GB VRAM usage
- **Context**: 4,096 tokens for conversation continuity
- **Deployment**: Docker container with GPU acceleration

#### **ML Learning Integration**
- **ConversationAnalytics**: Real-time conversation analysis and emotional intelligence
- **ResponseOptimizer**: Therapeutic effectiveness scoring and ML-powered prompt optimization
- **PatternRecognizer**: Behavioral pattern detection and intervention recommendations
- **Continuous Learning**: System learns from conversations to improve response quality

#### **Security Framework**
- **Comprehensive Threat Detection**: Multi-layer security validation and content filtering
- **Crisis Intervention**: Advanced self-harm/suicide detection with immediate response protocols
- **Professional Boundaries**: Therapeutic context maintenance and boundary violation detection
- **Audit Logging**: Complete security event tracking for compliance and safety monitoring
- Service health monitoring

#### 3. ContextAnalyzer (`context_analyzer.py`)
**Purpose**: Analyzes conversation context to understand user intent and emotional state

**Analysis Capabilities**:
- **User Intent Classification**: Support-seeking, information, crisis, progress-sharing
- **Emotional Intensity Assessment**: 1-5 scale with keyword analysis
- **Conversation Stage Detection**: Opening, middle, closing phases
- **Topic Extraction**: Mental health themes, triggers, progress indicators
- **Urgency Level Assessment**: Crisis detection and priority scoring
- **Sentiment Analysis**: Positive, negative, neutral emotional tone

#### 4. ResponseGenerator (`response_generator.py`)
**Purpose**: Orchestrates all intelligence components to generate comprehensive responses

**Workflow**:
1. **Context Gathering**: Aggregate user data from all services
2. **Conversation Analysis**: Analyze intent, emotion, and context
3. **Mood-Aware Generation**: Create appropriate response based on mood
4. **Context Enhancement**: Enrich response with conversation insights
5. **Personalization**: Adapt for user preferences and communication style
6. **Response Tracking**: Log for analytics and continuous improvement

**Response Features**:
- Comprehensive intelligent responses with metadata
- Confidence scoring for response quality assessment
- Crisis detection with immediate intervention protocols
- Follow-up suggestions and therapeutic recommendations
- Response analytics and improvement tracking

## 🔄 API Endpoints

### Core Chat Functionality

#### `POST /chat/intelligent` - **Primary Endpoint**
**Description**: Advanced intelligent chat with Phi-3 Mini agent integration, ML learning, and security validation

**Request Model**: `IntelligentChatRequest`
```json
{
  "message": "I've been feeling really anxious lately...",
  "session_id": "optional-existing-session-id", 
  "user_context_refresh": false,
  "use_agent": true
}
```

**Response Model**: `IntelligentChatResponse`
```json
{
  "response": "I hear that you're experiencing anxiety, and I want you to know that what you're feeling is valid and manageable. Let's work through this together...",
  "session_id": "uuid-session-identifier",
  "message_type": "agent_enhanced",
  "tone": "supportive_empathetic",
  "intervention_type": "anxiety_support",
  "agent_used": true,
  "ml_insights": {
    "emotional_state": "moderate_anxiety",
    "communication_style": "direct_support_seeking",
    "therapeutic_alignment": 0.92
  },
  "breathing_exercise": {
    "name": "4-7-8 Breathing",
    "duration": 4,
    "instructions": ["Inhale through nose for 4 seconds...", "Hold breath for 7 seconds..."]
  },
  "follow_up_suggestions": [
    "Consider exploring anxiety management techniques",
    "Try the guided meditation in your content library",
    "Connect with your support group when ready"
  ],
  "crisis_detected": false,
  "security_validated": true,
  "confidence_score": 0.94,
  "context_summary": {
    "mood_context": "available_from_services",
    "user_intent": "support_seeking",
    "conversation_stage": "middle",
    "intervention_priority": "medium"
  }
}
```

#### `POST /chat/agent-direct` - **Phi-3 Mini Direct Access**
**Description**: Direct access to Phi-3 Mini agent with custom prompting

**Request Model**: `AgentChatRequest`
```json
{
  "message": "How can I manage my anxiety?",
  "system_prompt": "optional-custom-therapeutic-context",
  "temperature": 0.7,
  "max_tokens": 512
}
```

#### `GET /chat/agent/health` - **Agent Health Check**
**Description**: Check Phi-3 Mini agent availability and performance

**Response**:
```json
{
  "status": "healthy",
  "agent_available": true,
  "model_loaded": "microsoft/Phi-3-mini-4k-instruct",
  "response_time_ms": 45,
  "gpu_utilization": 0.65,
  "tokens_per_second": 52.3,
  "uptime_seconds": 3600
}
```

#### `GET /chat/agent/performance` - **Performance Metrics**
**Description**: Detailed agent performance and ML learning statistics

**Response**:
```json
{
  "conversation_analytics": {
    "total_conversations": 1247,
    "avg_response_quality": 0.89,
    "crisis_interventions": 12,
    "therapeutic_effectiveness": 0.91
  },
  "ml_learning_metrics": {
    "patterns_recognized": 45,
    "response_optimizations": 156,
    "learning_accuracy": 0.87
  },
  "security_metrics": {
    "threats_detected": 3,
    "crisis_alerts": 12,
    "safety_score": 0.98
  }
}
```

### Session Management

#### `GET /chat/sessions/{session_id}`
**Description**: Retrieve session conversation history and context

#### `DELETE /chat/sessions/{session_id}`
**Description**: Clear session data for privacy

#### `POST /chat/sessions/{session_id}/export`
**Description**: Export conversation history for user (GDPR compliance)

### Health & Monitoring

#### `GET /health/comprehensive`
**Description**: Complete system health including all service integrations

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services_status": {
    "phi3_agent": "healthy",
    "ml_learning": "healthy",
    "security_manager": "healthy",
    "auth_service": "healthy",
    "profile_service": "healthy",
    "community_service": "healthy",
    "content_service": "healthy",
    "media_service": "healthy",
    "admin_service": "healthy"
  },
  "performance_metrics": {
    "avg_response_time": "1.2s",
    "agent_availability": "99.8%",
    "ml_learning_active": true
  }
}
```

### Analytics and Monitoring

#### `GET /chat/analytics/{user_id}`
Returns comprehensive chat interaction analytics including response effectiveness, intervention patterns, and engagement metrics.

#### `GET /chat/engine/status`
Provides intelligent engine status information including component health, performance metrics, and response generation statistics.

#### `POST /chat/context/refresh/{user_id}`
Forces refresh of user context from all MantraPath services for updated response accuracy.

### Session Management

#### `GET /chat/sessions/{user_id}`
Returns user's chat sessions with metadata including message counts, session types, and activity status.

## 🔧 Configuration and Setup

### Dependencies
```python
# Core Framework
fastapi>=0.100.0
uvicorn>=0.20.0
pydantic>=2.0.0
sqlalchemy>=2.0.0

# Async HTTP Client
httpx>=0.24.0

# Data Processing
python-dateutil>=2.8.0
typing-extensions>=4.5.0

# Logging and Monitoring
structlog>=23.0.0
```

### Environment Variables
```bash
# Service Configuration
CHATBOT_SERVICE_PORT=8004
CHATBOT_SERVICE_HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/mantrapath

# External Service URLs
MOOD_SERVICE_URL=http://mood-service:8002
PROFILE_SERVICE_URL=http://profile-service:8001
COMMUNITY_SERVICE_URL=http://community-service:8007
CONTENT_SERVICE_URL=http://content-service:8008
ML_SERVICE_URL=http://ml-service:8009

# Intelligent Engine Configuration
MOOD_CACHE_TTL_MINUTES=30
PROFILE_CACHE_TTL_MINUTES=60
SERVICE_TIMEOUT_SECONDS=10
MAX_CONVERSATION_HISTORY=10
CRISIS_CONFIDENCE_THRESHOLD=0.7

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
```

### Running the Service

#### Development Mode
```bash
cd backend/services/chatbot_service
python main_intelligent.py
# or
uvicorn main_intelligent:app --reload --port 8004
```

#### Production Deployment
```bash
uvicorn main_intelligent:app --host 0.0.0.0 --port 8004 --workers 4
```

#### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main_intelligent:app", "--host", "0.0.0.0", "--port", "8004"]
```

## 🧪 Testing and Validation

### Unit Testing
```bash
# Test individual intelligent engine components
python -m pytest tests/test_mood_aware_responder.py
python -m pytest tests/test_service_integrator.py
python -m pytest tests/test_context_analyzer.py
python -m pytest tests/test_response_generator.py
```

### Integration Testing
```bash
# Test full service integration
python -m pytest tests/test_intelligent_chat_flow.py
python -m pytest tests/test_service_communications.py
```

### Crisis Response Validation
```bash
# Test crisis detection and response protocols
python -m pytest tests/test_crisis_detection.py -v
```

## 📊 Performance and Monitoring

### Key Performance Indicators
- **Response Generation Time**: Target <2 seconds for 95th percentile
- **Service Integration Latency**: Target <500ms for context aggregation  
- **Crisis Detection Accuracy**: Target >95% sensitivity, <5% false positive rate
- **User Engagement Score**: Measured through conversation length and return interactions
- **Response Confidence Average**: Target >0.8 average confidence score

### Monitoring Endpoints
- `/health`: Service health check with database connectivity
- `/chat/engine/status`: Intelligent engine component status
- `/metrics`: Prometheus-compatible metrics (when enabled)

### Logging Strategy
```python
# Structured logging with context
logger.info(
    "Generated intelligent response",
    user_id=user_id,
    response_confidence=confidence_score,
    intervention_type=intervention_type,
    generation_time_ms=generation_time,
    crisis_detected=crisis_detected
)
```

## 🔒 Security and Privacy

### Data Protection
- **User Context Caching**: Limited TTL with automatic expiration
- **Conversation History**: Encrypted storage with user consent
- **Crisis Information**: Secure handling with audit logging
- **Personal Data**: GDPR compliance with data minimization

### Authentication and Authorization
- **JWT-based Authentication**: Secure token validation for all endpoints
- **User-specific Access**: Context isolation and permission validation
- **Admin Endpoints**: Enhanced security for administrative functions
- **Rate Limiting**: Protection against abuse and resource exhaustion

## 🚀 Migration from Legacy Implementation

### Deprecation Notice
The original `main.py` with keyword-based responses has been deprecated. All new development should use `main_intelligent.py` and the intelligent engine.

### Migration Steps
1. **Update Service Calls**: Change endpoint from `/api/chatbot/chat` to `/chat/intelligent`
2. **Response Model Updates**: Use new `IntelligentChatResponse` structure
3. **Enhanced Features**: Leverage crisis detection, breathing exercises, and follow-up suggestions
4. **Analytics Integration**: Implement response analytics and monitoring

### Backward Compatibility
- Legacy endpoints return deprecation notices
- Gradual migration support with feature flags
- Documentation for migration assistance

## 🔮 Future Enhancements (Phase 2)

### Advanced Intelligence Features
- **Behavioral Pattern Learning**: Long-term user behavior analysis
- **Therapeutic Protocol Integration**: Structured therapy session support
- **Group Therapy Support**: Multi-user conversation management
- **Crisis Prevention**: Predictive analysis for intervention timing

### Performance Optimizations
- **Redis Caching**: Distributed caching for improved performance
- **Event-Driven Architecture**: Real-time updates via message queues
- **Load Balancing**: Horizontal scaling for high-availability
- **Circuit Breakers**: Advanced fault tolerance patterns

### Enhanced Personalization
- **Learning Algorithms**: Adaptive response improvement over time
- **Communication Style Learning**: Dynamic tone and approach optimization
- **Cultural Sensitivity**: Localization and cultural adaptation
- **Accessibility Features**: Support for diverse communication needs

## 📚 Development Guidelines

### Code Quality Standards
- **Comprehensive Docstrings**: All classes and methods documented
- **Type Hints**: Full type annotation for improved maintainability
- **Error Handling**: Graceful degradation and informative error messages
- **Testing Coverage**: Minimum 80% test coverage for all components

### Contribution Workflow
1. **Feature Planning**: Create detailed design documents
2. **Implementation**: Follow established patterns and conventions
3. **Testing**: Comprehensive unit and integration testing
4. **Documentation**: Update all relevant documentation
5. **Code Review**: Peer review with focus on quality and security

### Best Practices
- **Async/Await**: Use asynchronous patterns for I/O operations
- **Logging**: Structured logging with appropriate log levels
- **Configuration**: Environment-based configuration management
- **Monitoring**: Comprehensive metrics and health checks

## 🤝 Support and Maintenance

### Troubleshooting Common Issues
1. **Service Integration Failures**: Check service URLs and authentication
2. **Slow Response Times**: Monitor service latency and caching effectiveness
3. **Crisis Detection Issues**: Validate keyword patterns and confidence thresholds
4. **Context Refresh Problems**: Verify service permissions and data availability

### Performance Optimization Tips
- Monitor service integration cache hit rates
- Optimize conversation history retrieval queries  
- Tune crisis detection sensitivity based on usage patterns
- Scale horizontally during high-traffic periods

### Maintenance Schedule
- **Weekly**: Review response analytics and confidence metrics
- **Monthly**: Update crisis detection keywords and intervention protocols
- **Quarterly**: Comprehensive security audit and dependency updates
- **Annually**: Full system architecture review and optimization planning

---

## 📈 Success Metrics

The intelligent chatbot service is considered successful when it achieves:

✅ **User Engagement**: 90% of users continue conversations beyond first interaction  
✅ **Crisis Response**: <30 seconds average response time for crisis situations  
✅ **Personalization Accuracy**: >85% user satisfaction with response relevance  
✅ **System Reliability**: 99.9% uptime with graceful degradation during failures  
✅ **Integration Performance**: All service integrations complete within SLA targets

This intelligent chatbot service represents MantraPath's commitment to providing sophisticated, empathetic, and effective mental health support through advanced AI technology.
