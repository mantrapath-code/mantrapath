# MantraPath Chatbot Service

## Overview

The MantraPath Chatbot Service is an AI-powered mental health support chatbot that integrates Microsoft's Phi-3 Mini model for local, privacy-focused conversations. It provides therapeutic support, crisis detection, and intelligent responses while maintaining user privacy through local AI processing.

## 🚀 Key Features

### AI Integration
- **Local Phi-3 Mini Model**: Privacy-focused local AI processing
- **OpenAI GPT Fallback**: Backup when local model unavailable
- **Intelligent Fallbacks**: Rule-based responses when AI unavailable

### Mental Health Support
- **Crisis Detection**: Automatic detection of crisis language
- **Therapeutic Responses**: Evidence-based therapeutic communication
- **Mood-Aware Conversations**: Context-aware emotional support
- **Conversation Memory**: Persistent session management

### Technical Features
- **FastAPI Backend**: Modern async Python framework
- **Docker Integration**: Containerized deployment
- **Health Monitoring**: Comprehensive health checks
- **Redis Caching**: Performance optimization

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   API Gateway    │───▶│ Chatbot Service │
│   (React)       │    │   (Port 8000)    │    │   (Port 8004)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Database       │    │  Phi-3 Agent    │
                       │   (PostgreSQL)   │    │  (Port 8010)    │
                       └──────────────────┘    └─────────────────┘
```

## 🛠️ Setup & Installation

### Prerequisites
- Docker Desktop
- 4GB+ available RAM (for Phi-3 model)
- Python 3.11+ (for development)

### Quick Start

1. **Start the complete service:**
   ```bash
   cd backend
   ./scripts/start-chatbot-with-phi3.sh
   ```

2. **Test the service:**
   ```bash
   python scripts/test-chatbot.py
   ```

### Manual Setup

1. **Start core services:**
   ```bash
   docker-compose up -d postgres redis agent-redis
   ```

2. **Start Phi-3 agent (may take 5-10 minutes first time):**
   ```bash
   docker-compose up -d phi3-agent
   ```

3. **Start chatbot service:**
   ```bash
   docker-compose up -d chatbot-service
   ```

4. **Start API gateway:**
   ```bash
   docker-compose up -d api-gateway
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath

# Redis
REDIS_URL=redis://redis:6379
AGENT_REDIS_URL=redis://agent-redis:6379

# AI Configuration
PHI3_AGENT_URL=http://phi3-agent:8000/v1/chat/completions
OPENAI_API_KEY=your-openai-api-key-here  # Optional fallback

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
```

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| API Gateway | 8000 | Main API entry point |
| Chatbot Service | 8004 | Direct chatbot API |
| Phi-3 Agent | 8010 | Local AI model |
| Agent Redis | 6380 | AI caching |

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Chat Session Management
```bash
# Create new session
POST /chat/session
Authorization: Bearer <jwt_token>

# Response
{
  "id": "session-uuid",
  "title": "Chat - 2025-01-15 10:30",
  "session_type": "ai_support",
  "is_active": true,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Chat Interaction
```bash
# Send message
POST /api/chatbot/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "I'm feeling anxious today",
  "session_id": "optional-session-id"
}

# Response
{
  "response": "I hear that you're feeling anxious today. That's a completely valid emotion...",
  "session_id": "session-uuid",
  "message_type": "text",
  "tone": "supportive",
  "intervention_type": "anxiety_support",
  "crisis_detected": false,
  "confidence_score": 0.85,
  "source": "phi3"
}
```

### Service Status
```bash
GET /api/chatbot/status

# Response
{
  "service": "chatbot-service",
  "status": "active",
  "version": "3.0.0",
  "phi3_available": true,
  "openai_available": true,
  "capabilities": [
    "Local Phi-3 Mini AI",
    "OpenAI GPT fallback",
    "Crisis detection",
    "Therapeutic responses",
    "Conversation memory"
  ]
}
```

## 🧠 AI Response Flow

### 1. Primary: Phi-3 Mini (Local)
- **Privacy**: All processing happens locally
- **Speed**: Fast responses (1-3 seconds)
- **Customization**: Therapeutic prompt engineering
- **Fallback**: If model unavailable or overloaded

### 2. Secondary: OpenAI GPT
- **Reliability**: Cloud-based backup
- **Quality**: High-quality responses
- **Cost**: API usage costs
- **Fallback**: If API key not provided or fails

### 3. Tertiary: Intelligent Fallback
- **Availability**: Always available
- **Crisis Detection**: Rule-based crisis identification
- **Basic Support**: Template-based responses
- **Reliability**: Never fails

## 🚨 Crisis Detection

The service includes comprehensive crisis detection:

### Crisis Keywords
- Suicide-related language
- Self-harm indicators
- Hopelessness expressions
- Emergency situations

### Crisis Response
```json
{
  "response": "I'm really concerned about what you're sharing...",
  "crisis_detected": true,
  "intervention_type": "crisis_intervention",
  "tone": "urgent_supportive"
}
```

### Resources Provided
- Crisis hotline numbers
- Emergency contacts
- Professional help guidance
- Immediate safety planning

## 🔍 Monitoring & Debugging

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health

# Check chatbot directly
curl http://localhost:8004/health

# Check Phi-3 agent
curl http://localhost:8010/health
```

### Logs
```bash
# View chatbot logs
docker-compose logs -f chatbot-service

# View Phi-3 agent logs
docker-compose logs -f phi3-agent

# View all logs
docker-compose logs -f
```

### Common Issues

#### Phi-3 Model Not Loading
```bash
# Check agent logs
docker-compose logs phi3-agent

# Common causes:
# - Insufficient memory (need 4GB+)
# - Model download in progress
# - Network connectivity issues

# Solution: Wait for model download or increase memory
```

#### Chatbot Returning Fallback Responses
```bash
# Check service connectivity
curl http://localhost:8010/health

# Verify environment variables
docker-compose exec chatbot-service env | grep PHI3

# Restart services
docker-compose restart phi3-agent chatbot-service
```

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive test suite
python scripts/test-chatbot.py
```

### Manual Testing
```bash
# Test health endpoints
curl http://localhost:8004/health

# Test chat (requires authentication)
curl -X POST http://localhost:8004/api/chatbot/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### Performance Testing
```bash
# Test response times
time curl -X POST http://localhost:8004/api/chatbot/chat \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
```

## 🔒 Security Features

### Authentication
- JWT token-based authentication
- User session management
- Secure token validation

### Privacy
- Local AI processing (Phi-3)
- No data sent to external services (when using Phi-3)
- Conversation encryption in transit

### Input Validation
- Message length limits
- Content sanitization
- SQL injection prevention

## 📊 Performance Metrics

### Expected Performance
- **Phi-3 Response Time**: 1-3 seconds
- **OpenAI Response Time**: 2-5 seconds
- **Fallback Response Time**: <100ms
- **Memory Usage**: 4-6GB (with Phi-3)
- **Concurrent Users**: 50+ (depending on hardware)

### Optimization Tips
- Increase Docker memory allocation
- Use SSD storage for model caching
- Monitor Redis cache hit rates
- Scale horizontally for high load

## 🚀 Deployment

### Development
```bash
# Start with hot reload
docker-compose up --build chatbot-service
```

### Production
```bash
# Use production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Scaling
```bash
# Scale chatbot service
docker-compose up --scale chatbot-service=3

# Load balance with nginx
# (nginx configuration required)
```

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run tests: `python scripts/test-chatbot.py`

### Code Structure
```
chatbot_service/
├── main.py                 # Main FastAPI application
├── agent_service.py        # Phi-3 integration (advanced)
├── main_intelligent.py     # Intelligent engine (legacy)
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
└── intelligent_engine/    # Advanced AI components
```

## 📝 Changelog

### Version 3.0.0 (Current)
- ✅ Phi-3 Mini local AI integration
- ✅ Robust fallback mechanisms
- ✅ Crisis detection and intervention
- ✅ Docker containerization
- ✅ Comprehensive testing suite

### Version 2.0.0 (Legacy)
- Intelligent engine with service integration
- OpenAI GPT integration
- Advanced context analysis

### Version 1.0.0 (Deprecated)
- Basic chatbot functionality
- Simple response templates

## 🆘 Support

### Common Commands
```bash
# Restart everything
docker-compose restart

# Clean rebuild
docker-compose down && docker-compose up --build

# View resource usage
docker stats

# Clean up
docker-compose down -v
docker system prune
```

### Getting Help
1. Check logs: `docker-compose logs -f chatbot-service`
2. Run health checks: `curl http://localhost:8004/health`
3. Test connectivity: `python scripts/test-chatbot.py`
4. Check documentation: This README
5. Review Docker resources: `docker stats`

---

**MantraPath Chatbot Service** - Providing compassionate, AI-powered mental health support with privacy and reliability at its core.