# Enhanced Chatbot Service - Voice Integration & Multi-Language Support

## Overview

The Enhanced Chatbot Service (v3.0.0) provides comprehensive voice-enabled chatbot functionality with multi-language support, platform awareness, and advanced AI integration for the MantraPath wellness platform.

## 🚀 Key Features

### Voice Integration
- **Real-time voice processing** with speech-to-text (STT) and text-to-speech (TTS)
- **Voice emotion detection** and cultural speech pattern analysis
- **Streaming voice support** for real-time conversations
- **High-quality voice responses** in multiple languages

### Multi-Language Support
- **Automatic language detection** from both text and voice inputs
- **20+ supported languages** including English, Hindi, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Chinese, Korean, Arabic, Bengali, Tamil, Telugu, Gujarati, Marathi, Punjabi, Urdu, Malayalam, Kannada, and Assamese
- **Cultural adaptation** with region-specific response patterns
- **Cross-language conversation flow** with seamless translation

### Platform Awareness
- **Mood service integration** for emotion-aware responses
- **Journal activity analysis** for personalized insights
- **Community engagement context** for social support
- **Memory service integration** for conversation continuity
- **Profile-based customization** for user preferences

### Advanced AI Features
- **Crisis detection** with appropriate intervention strategies
- **Sentiment analysis** with cultural context awareness
- **Behavioral pattern recognition** from conversation history
- **Predictive context** for proactive support
- **Action orchestration** for complex multi-step interactions

## 🏗️ Architecture

### Service Components

```
Enhanced Chatbot Service (Port 8104)
├── Voice Integration Module
│   ├── Speech-to-Text Processing
│   ├── Text-to-Speech Generation
│   └── Voice Emotion Analysis
├── Language Processing Module
│   ├── Auto Language Detection
│   ├── Translation Service Integration
│   └── Cultural Context Analysis
├── Platform Context Manager
│   ├── Mood Service Integration
│   ├── Profile Service Integration
│   ├── Community Service Integration
│   ├── Memory Service Integration
│   └── Content Service Integration
├── Intelligent Response Engine
│   ├── Response Generator
│   ├── Crisis Detection
│   ├── Sentiment Analysis
│   └── Follow-up Suggestions
└── Conversation Memory
    ├── Session Management
    ├── History Tracking
    └── Pattern Recognition

Voice Event Processor Enhanced (Port 8115)
├── Real-time Voice Stream Processing
├── Voice Chunk Management
├── Emotion & Cultural Analysis
├── NATS Event Integration
└── Chatbot Service Coordination
```

### Data Flow

1. **Voice Input** → Voice Event Processor → Speech-to-Text → Language Detection
2. **Text Processing** → Sentiment Analysis → Cultural Context Analysis
3. **Platform Context** → Mood/Profile/Community/Memory Services → Context Aggregation
4. **Response Generation** → Action Orchestrator → Intelligent Response Engine
5. **Response Delivery** → Translation (if needed) → Text-to-Speech (if requested)

## 🛠️ Installation & Deployment

### Prerequisites

```bash
# Required services
- Docker & Docker Compose
- Python 3.9+
- MantraPath Backend Services (Voice, Translation, Mood, Profile, etc.)
```

### Quick Start

```bash
# 1. Navigate to scripts directory
cd /Users/sachin/Desktop/mantrapath/scripts

# 2. Deploy enhanced services
./deploy_enhanced_chatbot.sh deploy

# 3. Check service status
./deploy_enhanced_chatbot.sh status

# 4. Run integration tests
./deploy_enhanced_chatbot.sh test
```

### Manual Deployment

```bash
# 1. Build enhanced services
cd /Users/sachin/Desktop/mantrapath/backend
docker-compose -f docker-compose.yml -f docker-compose-enhanced-voice.yml build

# 2. Start dependencies
docker-compose -f docker-compose.yml up -d postgres redis nats voice-service translation-service

# 3. Start enhanced services
docker-compose -f docker-compose.yml -f docker-compose-enhanced-voice.yml up -d chatbot-service-enhanced voice-event-processor-enhanced
```

## 📡 API Reference

### Base URL
```
http://localhost:8104
```

### Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "enhanced_chatbot_service",
  "version": "3.0.0",
  "features": [
    "voice_integration",
    "multi_language_support",
    "platform_awareness",
    "cultural_intelligence",
    "conversation_memory"
  ]
}
```

#### Voice Chat
```http
POST /api/chat/voice
Content-Type: multipart/form-data
```

**Request:**
```
audio: <audio_file> (WAV, MP3, or other supported formats)
request_data: {
  "session_id": "optional_session_id",
  "preferred_language": "auto",
  "include_platform_context": true,
  "voice_response": true
}
```

**Response:**
```json
{
  "response_text": "I understand you're feeling anxious. Let me help you with some breathing exercises.",
  "session_id": "session_123",
  "detected_language": "en",
  "response_language": "en",
  "sentiment": {
    "compound": -0.2,
    "positive": 0.1,
    "neutral": 0.6,
    "negative": 0.3
  },
  "cultural_context": {
    "region": "western",
    "cultural_markers": ["anxiety_expression"]
  },
  "platform_insights": {
    "mood_data": {
      "current_mood": "anxious",
      "recent_patterns": ["stress", "worry"]
    },
    "profile_data": {
      "wellness_goals": ["stress_management"]
    }
  },
  "intervention_type": "emotional_support",
  "confidence_score": 0.85,
  "follow_up_suggestions": [
    "Would you like to try a breathing exercise?",
    "Tell me more about what's causing your anxiety",
    "Have you tried our guided meditation?"
  ],
  "crisis_detected": false,
  "audio_url": "https://storage.example.com/audio/response_123.mp3",
  "conversation_memory": {
    "session_id": "session_123",
    "total_messages": 3,
    "key_topics": ["anxiety", "breathing_exercises"]
  }
}
```

#### Text Chat
```http
POST /api/chat/text
Content-Type: application/json
```

**Request:**
```json
{
  "message": "I'm feeling stressed about work",
  "session_id": "optional_session_id",
  "language": "auto",
  "preferred_response_language": "en",
  "include_platform_context": true,
  "voice_response": false
}
```

**Response:** (Same structure as Voice Chat response)

#### Language Detection
```http
POST /api/language/detect
Content-Type: multipart/form-data
```

**Request:**
```
text: "Hello, how are you feeling today?"
```

**Response:**
```json
{
  "detected_language": "en",
  "confidence": 0.95,
  "supported_languages": [
    "en", "hi", "es", "fr", "de", "it", "pt", "ru", 
    "ja", "zh", "ko", "ar", "bn", "ta", "te", "gu",
    "mr", "pa", "ur", "ml", "kn", "as"
  ]
}
```

#### Chat Sessions
```http
GET /api/chat/sessions
```

**Response:**
```json
[
  {
    "id": "session_123",
    "title": "Chat 2024-01-20 14:30",
    "session_type": "enhanced_chat",
    "is_active": true,
    "created_at": "2024-01-20T14:30:00",
    "message_count": 5
  }
]
```

#### Chat History
```http
GET /api/chat/history/{session_id}
```

**Response:**
```json
[
  {
    "id": "msg_1",
    "sender": "user",
    "content": "I'm feeling stressed",
    "message_type": "text",
    "created_at": "2024-01-20T14:30:00"
  },
  {
    "id": "msg_2",
    "sender": "assistant",
    "content": "I understand your stress. Let's work through this together.",
    "message_type": "enhanced_response",
    "created_at": "2024-01-20T14:30:15"
  }
]
```

## 🔧 Configuration

### Environment Variables

#### Enhanced Chatbot Service
```bash
# Service Configuration
SERVICE_NAME=chatbot_service_enhanced
SERVICE_VERSION=3.0.0
LOG_LEVEL=INFO

# Database
POSTGRES_URL=postgresql://user:pass@postgres:5432/mantrapath
REDIS_URL=redis://redis:6379/1

# Voice Integration
VOICE_SERVICE_URL=http://voice-service:8011
VOICE_EVENT_PROCESSOR_URL=http://voice-event-processor-enhanced:8115
VOICE_INTEGRATION_ENABLED=true
VOICE_RESPONSE_DEFAULT=true

# Multi-language Support
TRANSLATION_SERVICE_URL=http://translation-service:8010
AUTO_LANGUAGE_DETECTION=true
CULTURAL_ADAPTATION_ENABLED=true

# Platform Integration
MOOD_SERVICE_URL=http://mood-service:8003
PROFILE_SERVICE_URL=http://profile-service:8002
CONTENT_SERVICE_URL=http://content-service:8005
COMMUNITY_SERVICE_URL=http://community-service:8006
MEMORY_SERVICE_URL=http://memory-service:8017

# AI Services
ACTION_ORCHESTRATOR_URL=http://action-orchestrator:8012
AI_CONTEXT_STORE_URL=http://ai-context-store:8013
AI_EVENT_PROCESSOR_URL=http://ai-event-processor:8014

# Features
PLATFORM_CONTEXT_ENABLED=true
CONVERSATION_MEMORY_ENABLED=true
CRISIS_DETECTION_ENABLED=true
EMOTIONAL_INTELLIGENCE_ENABLED=true
CONTEXT_CACHE_TTL=600
```

#### Voice Event Processor Enhanced
```bash
# Service Configuration
SERVICE_NAME=voice_event_processor_enhanced
SERVICE_VERSION=2.0.0
LOG_LEVEL=INFO

# Voice Processing
VOICE_SERVICE_URL=http://voice-service:8011
MODELS_SERVICE_URL=http://models-service:8080
VOICE_STREAM_ENABLED=true
VOICE_CHUNK_SIZE=1024
VOICE_TIMEOUT=30

# Language Support
TRANSLATION_SERVICE_URL=http://translation-service:8010
MULTI_LANGUAGE_ENABLED=true
LANGUAGE_AUTO_DETECTION=true

# AI Integration
AI_EVENT_PROCESSOR_URL=http://ai-event-processor:8014
EMOTION_ANALYSIS_ENABLED=true
CULTURAL_ANALYSIS_ENABLED=true

# Enhanced Chatbot Integration
CHATBOT_SERVICE_URL=http://chatbot-service-enhanced:8004
MEMORY_SERVICE_URL=http://memory-service:8017
```

## 🧪 Testing

### Integration Tests
```bash
# Run comprehensive test suite
cd /Users/sachin/Desktop/mantrapath/scripts
python3 test_enhanced_chatbot_voice.py
```

### Test Coverage
- ✅ Health checks for all services
- ✅ Language detection accuracy
- ✅ Text chat with multi-language support
- ✅ Voice chat integration (STT/TTS)
- ✅ Conversation memory and history
- ✅ Platform context integration
- ✅ Crisis detection functionality
- ✅ Cultural adaptation responses

### Manual Testing

#### Voice Chat Test
```bash
# Upload audio file for voice chat
curl -X POST http://localhost:8104/api/chat/voice \
  -H "Authorization: Bearer <token>" \
  -F "audio=@test_audio.wav" \
  -F 'request_data={"preferred_language":"auto","voice_response":true}'
```

#### Text Chat Test
```bash
# Send multilingual text message
curl -X POST http://localhost:8104/api/chat/text \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "मुझे आज चिंता हो रही है। क्या आप मेरी मदद कर सकते हैं?",
    "language": "hi",
    "preferred_response_language": "hi",
    "include_platform_context": true
  }'
```

## 🔍 Monitoring & Debugging

### Service Logs
```bash
# Enhanced Chatbot Service logs
./deploy_enhanced_chatbot.sh logs chatbot-service-enhanced

# Voice Event Processor logs
./deploy_enhanced_chatbot.sh logs voice-event-processor-enhanced

# All enhanced services logs
./deploy_enhanced_chatbot.sh logs
```

### Health Monitoring
```bash
# Check service status
./deploy_enhanced_chatbot.sh status

# Health check endpoints
curl http://localhost:8104/health
curl http://localhost:8115/health
```

### Performance Metrics
- **Response time**: < 2 seconds for text, < 5 seconds for voice
- **Language detection accuracy**: > 95%
- **Voice recognition accuracy**: > 90%
- **Platform context retrieval**: < 1 second
- **Concurrent conversations**: Up to 100 simultaneous sessions

## 🛡️ Security Considerations

### Authentication
- JWT token validation for all API endpoints
- User session isolation and data privacy
- Rate limiting for voice processing endpoints

### Data Protection
- Voice data encrypted in transit and at rest
- Conversation history encrypted in database
- PII redaction in logs and analytics

### Platform Integration Security
- Service-to-service authentication via internal networks
- Context data access control based on user permissions
- Audit logging for all platform data access

## 🔄 Troubleshooting

### Common Issues

#### Voice Processing Fails
```bash
# Check voice service connectivity
curl http://localhost:8011/health

# Check voice event processor logs
docker logs voice-event-processor-enhanced
```

#### Language Detection Issues
```bash
# Check translation service
curl http://localhost:8010/health

# Test language detection directly
curl -X POST http://localhost:8010/api/detect \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

#### Platform Context Not Loading
```bash
# Check individual services
curl http://localhost:8003/health  # Mood service
curl http://localhost:8002/health  # Profile service
curl http://localhost:8006/health  # Community service
```

#### Database Connection Issues
```bash
# Check PostgreSQL connectivity
docker exec -it backend_postgres_1 psql -U mantrapath -d mantrapath -c "\dt"

# Check Redis connectivity
docker exec -it backend_redis_1 redis-cli ping
```

### Debug Mode
Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## 📈 Future Enhancements

### Planned Features
- **Real-time voice streaming** with WebSocket support
- **Voice biometrics** for user identification
- **Advanced emotion recognition** from voice patterns
- **Multi-party conversation** support
- **Voice command processing** for app navigation
- **Personalized voice synthesis** based on user preferences

### Performance Optimizations
- **Response caching** for common queries
- **Predictive context loading** based on user patterns
- **Voice processing optimization** with model compression
- **Load balancing** for high-availability deployment

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup development environment
git clone <repository>
cd mantrapath/backend/services/chatbot_service

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main_enhanced_voice.py
```

### Code Standards
- Follow PEP 8 for Python code formatting
- Use type hints for all function parameters and returns
- Add comprehensive docstrings for all classes and methods
- Include unit tests for new functionality

---

**Enhanced Chatbot Service v3.0.0** - Bringing voice-enabled, culturally-aware, and platform-integrated conversational AI to MantraPath wellness platform.

For support or questions, contact the MantraPath Development Team.
