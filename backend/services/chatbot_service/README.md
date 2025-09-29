# MantraPath Intelligent Chatbot Service

## Overview

The **Intelligent Chatbot Service** is a sophisticated, AI-powered mental health support chatbot that provides mood-aware, personalized responses with comprehensive multi-language support and voice interaction capabilities. This service serves as the conversational interface for the MantraPath platform, delivering intelligent therapeutic interventions, crisis detection, and contextual support.

### Key Features

- 🧠 **Intelligent Response Generation** - Context-aware responses using advanced engine components
- 🎯 **Mood-Aware Interactions** - Responses tailored to user emotional state and mood trends  
- 🌍 **Multi-Language Support** - Automatic language detection with real-time translation
- 🎙️ **Voice Integration** - Speech-to-text and text-to-speech capabilities
- 🚨 **Crisis Detection** - Automatic identification and appropriate intervention suggestions
- 📊 **Conversation Analytics** - Response effectiveness tracking and user engagement metrics
- 🔄 **Service Integration** - Seamless integration with mood, profile, and ML services
- 💾 **Session Management** - Persistent conversation history and context

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chatbot Service (Port 8004)             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────────────────────┐   │
│  │   FastAPI App   │  │     Intelligent Engine          │   │
│  │                 │  │  ┌─────────────────────────────┐ │   │
│  │  • Auth Layer   │  │  │  Response Generator         │ │   │
│  │  • Rate Limits  │  │  │  • Context Analyzer        │ │   │
│  │  • CORS Config  │  │  │  • Mood-Aware Responder    │ │   │
│  │  • Endpoints    │  │  │  • Service Integrator      │ │   │
│  └─────────────────┘  │  └─────────────────────────────┘ │   │
│                       └─────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Service Clients                        │   │
│  │  • Mood Service      • Models Service              │   │
│  │  • Voice Service     • ML Service                  │   │
│  │  • Translation      • Profile Service             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Data Models & Database                   │   │
│  │  • ChatSession       • ChatMessage                 │   │
│  │  • SQLAlchemy ORM    • PostgreSQL                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
chatbot_service/
├── main.py                     # FastAPI application entry point (1025 lines)
├── requirements.txt            # Service dependencies
├── Dockerfile                  # Container configuration
├── src/                        # Source code modules
│   ├── intelligent_engine/     # AI engine components
│   │   ├── response_generator.py     # Central response orchestration (340 lines)
│   │   ├── context_analyzer.py       # Conversation context analysis (279 lines)  
│   │   ├── mood_aware_responder.py   # Mood-based response generation
│   │   └── service_integrator.py     # Multi-service data integration
│   ├── clients/                # External service clients
│   │   ├── mood_service_client.py         # Mood service integration (330 lines)
│   │   ├── models_service_client.py       # Translation & ML models access
│   │   ├── voice_service_client.py        # Voice processing integration
│   │   ├── ml_service_client.py           # Machine learning service
│   │   └── translation_service_client.py  # Translation service client
│   └── models/                 # Data models
│       └── chat_context.py     # Chat context and response models (59 lines)
└── tests/                      # Test files
    └── ...                     # Unit and integration tests
```

## API Endpoints

### Core Chat Endpoints

#### POST `/chat/intelligent`
**Intelligent Chat Interface**
```json
Request:
{
  "message": "I'm feeling overwhelmed today",
  "session_id": "uuid-string",
  "language": "auto",
  "preferred_response_language": "en",
  "user_context_refresh": false
}

Response:
{
  "response": "I understand you're feeling overwhelmed. That's completely valid...",
  "session_id": "uuid-string",
  "tone": "supportive",
  "intervention_type": "emotional_support",
  "breathing_exercise": {
    "name": "4-7-8 Breathing",
    "steps": ["Inhale for 4 counts...", "Hold for 7 counts...", "Exhale for 8 counts..."]
  },
  "follow_up_suggestions": ["Consider taking a short break", "Try gentle stretching"],
  "crisis_detected": false,
  "confidence_score": 0.92,
  "context_summary": {
    "mood_score": 4.2,
    "mood_trend": "declining",
    "user_intent": "seeking_help"
  },
  "detected_language": "en",
  "response_language": "en",
  "translation_used": false
}
```

### Voice Integration

#### POST `/api/chatbot/voice`
**Voice Input Processing**
- Accepts audio file uploads
- Converts speech-to-text using voice service
- Processes through intelligent chat pipeline
- Returns comprehensive response with voice metadata

### Session Management

#### GET `/chat/sessions`
**Get User Chat Sessions**
- Returns list of conversation sessions
- Includes session metadata and message counts
- Supports pagination and filtering

#### GET `/chat/history/{session_id}`
**Get Conversation History**
- Retrieves complete conversation thread
- Includes message timestamps and metadata
- Supports pagination for long conversations

### Analytics & Monitoring

#### GET `/chat/analytics/{user_id}`
**Chat Analytics**
```json
Response:
{
  "total_messages": 245,
  "session_count": 18,
  "average_response_confidence": 0.87,
  "crisis_interactions": 2,
  "most_common_intervention": "emotional_support",
  "user_engagement_score": 0.94
}
```

#### GET `/chat/engine/status`
**Engine Status Monitoring**
- Real-time status of intelligent engine components
- Performance metrics and health checks
- Component uptime and response tracking

### Frontend Compatibility

#### POST `/api/chatbot/chat`
#### POST `/api/chatbot/enhanced/chat`
**Frontend-Compatible Endpoints**
- Mirror functionality of core intelligent chat
- Standardized API format for frontend integration
- Enhanced error handling and response formatting

## Configuration

### Environment Variables

```bash
# Service Configuration
CHATBOT_SERVICE_PORT=8004
CHATBOT_SERVICE_HOST=0.0.0.0

# Database Configuration  
DATABASE_URL=postgresql://user:pass@localhost/mantrapath
SQLALCHEMY_DATABASE_URL=postgresql://user:pass@localhost/mantrapath

# External Service URLs
MODELS_SERVICE_URL=http://models-service:8080
VOICE_SERVICE_URL=http://voice-service:8011
MOOD_SERVICE_URL=http://mood-service:8003
ML_SERVICE_URL=http://ml-service:8007
PROFILE_SERVICE_URL=http://profile-service:8002

# JWT Configuration (from shared auth)
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Feature Flags
CHATBOT_DEBUG=false
ENABLE_VOICE_INTEGRATION=true
ENABLE_TRANSLATION=true
ENABLE_CRISIS_DETECTION=true
```

### Service Dependencies

- **Models Service** (Port 8080) - Language detection and translation
- **Voice Service** (Port 8011) - Speech-to-text processing
- **Mood Service** (Port 8003) - User mood data and analytics
- **ML Service** (Port 8007) - Machine learning predictions
- **Profile Service** (Port 8002) - User profile information
- **PostgreSQL** - Session and message persistence
- **Redis** (Optional) - Caching and rate limiting

## Intelligent Engine Components

### Response Generator
**Central orchestration component** that coordinates all intelligent engine modules:
- Gathers comprehensive user context from multiple services
- Analyzes conversation context and user intent
- Generates mood-aware responses with personalization
- Provides fallback mechanisms for service failures
- Tracks response effectiveness and user engagement

### Context Analyzer  
**Conversation analysis engine** that provides contextual understanding:
- **Intent Classification**: Seeking help, sharing feelings, crisis situations
- **Emotional Intensity**: Measures emotional state (0-1 scale)
- **Conversation Stage**: Opening, deepening, sustained support, crisis
- **Sentiment Analysis**: Overall conversation sentiment (-1 to 1)
- **Urgency Detection**: Crisis level assessment (1-5 scale)

### Mood-Aware Responder
**Mood-sensitive response generation** with therapeutic interventions:
- Integrates real-time mood data from mood service
- Provides crisis detection and intervention suggestions  
- Generates breathing exercises and coping strategies
- Adapts communication style to user emotional state
- Supports multiple intervention types (emotional support, cognitive reframing, etc.)

### Service Integrator
**Multi-service data aggregation** for comprehensive user context:
- Collects user profile information and preferences
- Retrieves mood history and trend analysis
- Gathers ML-based predictions and insights
- Manages service timeouts and fallback strategies
- Provides unified context interface for response generation

## Request Flow

```mermaid
sequenceDiagram
    participant User
    participant ChatBot as Chatbot Service
    participant Engine as Intelligent Engine
    participant Mood as Mood Service
    participant Models as Models Service
    participant Voice as Voice Service
    participant DB as Database

    User->>ChatBot: Send message (text/voice)
    
    alt Voice Input
        ChatBot->>Voice: Convert speech-to-text
        Voice-->>ChatBot: Transcript + language
    end
    
    ChatBot->>Engine: Generate intelligent response
    Engine->>Mood: Get user mood context
    Engine->>Models: Detect language & translate
    Engine->>Engine: Analyze conversation context
    Engine->>Engine: Generate mood-aware response
    Engine-->>ChatBot: Intelligent response
    
    ChatBot->>DB: Save interaction (async)
    ChatBot-->>User: Response with metadata
```

## Data Models

### ChatSession
```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id: UUID = Column(UUID, primary_key=True)
    user_id: str = Column(String, nullable=False, index=True)
    title: str = Column(String, nullable=True)
    session_type: str = Column(String, default="general")
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime)
    updated_at: datetime = Column(DateTime)
```

### ChatMessage  
```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id: UUID = Column(UUID, primary_key=True)
    session_id: str = Column(String, nullable=False, index=True)
    user_id: str = Column(String, nullable=False, index=True)
    message_type: str = Column(String)  # 'user', 'assistant'
    content: str = Column(Text, nullable=False)
    metadata: JSON = Column(JSON, nullable=True)
    created_at: datetime = Column(DateTime)
```

## Multi-Language Support

### Automatic Language Detection
- Real-time language detection via Models Service
- Supports 50+ languages with confidence scoring
- Fallback to English for unsupported languages
- Context-aware language switching

### Translation Pipeline
- Enhanced translation with context preservation
- Fallback to simplified responses for translation failures
- Cultural adaptation for responses
- Maintains therapeutic tone across languages

### Language Features
```python
# Supported languages with confidence thresholds
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "threshold": 0.8},
    "es": {"name": "Spanish", "threshold": 0.7},
    "fr": {"name": "French", "threshold": 0.7},
    "de": {"name": "German", "threshold": 0.7},
    "hi": {"name": "Hindi", "threshold": 0.6},
    "zh": {"name": "Chinese", "threshold": 0.6}
}
```

## Voice Integration

### Speech-to-Text Processing
- Real-time audio processing via Voice Service
- Multi-language speech recognition
- Audio quality assessment and enhancement
- Noise reduction and clarity optimization

### Voice Features
- Supports common audio formats (MP3, WAV, M4A)
- Automatic language detection from speech
- Confidence scoring for transcription accuracy
- Voice activity detection and endpoint detection

## Crisis Detection & Intervention

### Crisis Indicators
The service monitors for crisis situations using multiple detection mechanisms:

```python
# Crisis detection patterns
CRISIS_INDICATORS = {
    "high_urgency": ["suicide", "kill myself", "end it all", "can't go on"],
    "medium_urgency": ["hopeless", "worthless", "no point", "give up"],
    "emotional_distress": ["overwhelmed", "breaking down", "can't cope"]
}
```

### Intervention Strategies
- **Immediate Response**: Crisis hotline information and emergency contacts
- **Breathing Exercises**: Guided breathing techniques for acute stress
- **Grounding Techniques**: 5-4-3-2-1 sensory grounding exercises  
- **Professional Resources**: Referrals to mental health professionals
- **Safety Planning**: Collaborative safety planning tools

## Development & Testing

### Running Locally

```bash
# Install dependencies
cd /home/sachin/mantrapath/backend/services/chatbot_service
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/mantrapath"
export MODELS_SERVICE_URL="http://localhost:8080"
export VOICE_SERVICE_URL="http://localhost:8011"

# Run the service
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

### Using VS Code Tasks

```bash
# Available tasks:
# - Start Translation Service Development
# - Test Translation Service  
# - Install Translation Service Dependencies

# Start development server
# Task: "Start Translation Service Development" (if available)
```

### Docker Deployment

```bash
# Build image
docker build -t mantrapath/chatbot-service .

# Run container
docker run -d \
  --name chatbot-service \
  -p 8004:8004 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/mantrapath" \
  -e MODELS_SERVICE_URL="http://models-service:8080" \
  mantrapath/chatbot-service
```

### Testing

```bash
# Run all tests
python -m pytest tests/ -v --cov=. --cov-report=term-missing

# Test specific components
python -m pytest tests/test_intelligent_engine.py -v
python -m pytest tests/test_voice_integration.py -v
python -m pytest tests/test_multilanguage.py -v
```

## Monitoring & Health Checks

### Health Check Endpoint
**GET `/health`**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "database": "connected", 
  "intelligent_engine": "active",
  "components": {
    "response_generator": "healthy",
    "context_analyzer": "healthy",
    "mood_responder": "healthy",
    "service_integrator": "healthy"
  }
}
```

### Performance Metrics
- Response generation time tracking
- Service integration latency monitoring
- Crisis detection accuracy metrics
- User engagement and satisfaction scores
- Translation quality and success rates

### Logging
```python
# Comprehensive logging for debugging and monitoring
logger.info(f"Generated intelligent response for user {user_id} in {generation_time:.2f}s with confidence {confidence_score:.2f}")
logger.warning(f"⚠️ Translation failed for {language}, using English")
logger.error(f"Error in intelligent chat endpoint: {str(e)}")
```

## Security & Authentication

### JWT Authentication
- Integrates with shared authentication system
- Bearer token validation for all protected endpoints
- User context extraction from validated tokens
- Rate limiting and request throttling

### Data Protection
- Sensitive conversation data encryption at rest
- PII anonymization in logs and metrics
- GDPR compliance for user data handling
- Secure multi-service communication

## Service Integration Patterns

### Mood Service Integration
```python
# Real-time mood context retrieval
mood_context = await mood_client.get_user_mood_context(
    user_id=user_id,
    token=auth_token,
    time_range_hours=24
)
```

### Models Service Integration  
```python
# Language detection and translation
detected_language = await detect_language(user_message, http_client)
translated_response = await translate_text_enhanced(
    response_text, "en", target_language, http_client
)
```

### Voice Service Integration
```python
# Speech-to-text processing
stt_result = await voice_client.convert_speech_to_text(
    audio_file=audio_content,
    language="auto"
)
```

## Performance Considerations

### Response Time Optimization
- **Target Response Time**: < 2 seconds for text, < 5 seconds for voice
- **Service Timeout Strategy**: 10s primary, 5s fallback
- **Parallel Processing**: Concurrent service calls where possible
- **Caching Strategy**: Context and translation caching for repeated requests

### Scalability Features
- **Horizontal Scaling**: Stateless design supports multiple instances
- **Database Connection Pooling**: Efficient database resource management
- **Async Processing**: Non-blocking I/O for all external service calls
- **Background Tasks**: Async database saves and analytics processing

## Future Development Plans

### Phase 1 - Enhanced Intelligence (Q2 2024)
- [ ] **Advanced NLP Models**: Integration with larger language models
- [ ] **Emotion Recognition**: Real-time emotional state analysis from text
- [ ] **Personality Adaptation**: Response style matching to user personality
- [ ] **Context Memory**: Long-term conversation context retention

### Phase 2 - Expanded Capabilities (Q3 2024) 
- [ ] **Video Integration**: Facial expression analysis for mood assessment
- [ ] **Group Chat Support**: Multi-user therapeutic group sessions
- [ ] **Therapeutic Exercises**: Interactive CBT and mindfulness exercises
- [ ] **Progress Tracking**: Longitudinal mental health progress monitoring

### Phase 3 - Advanced Features (Q4 2024)
- [ ] **Predictive Analytics**: Proactive intervention based on pattern recognition
- [ ] **Integration Hub**: Third-party mental health service integrations
- [ ] **Offline Capabilities**: Limited functionality without internet connectivity
- [ ] **Professional Dashboard**: Clinician interface for supervised interactions

## Contributing

### Development Guidelines
1. **Code Style**: Follow PEP 8 standards with type hints
2. **Testing**: Maintain >90% test coverage for critical components
3. **Documentation**: Update README and API docs for all changes
4. **Security**: Security review required for authentication changes

### Key Areas for Contribution
- **Language Support**: Adding new language detection and translation capabilities
- **Intervention Strategies**: New therapeutic intervention techniques
- **Voice Processing**: Enhanced voice recognition and synthesis features
- **Analytics**: Advanced conversation analysis and reporting tools

---

**Service Status**: ✅ Active Development  
**Port**: 8004  
**Version**: 2.0.0  
**Last Updated**: January 2024  
**Maintainer**: MantraPath Development Team