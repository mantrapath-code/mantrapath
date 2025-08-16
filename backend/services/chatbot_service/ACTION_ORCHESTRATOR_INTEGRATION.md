# Action Orchestrator Integration with Chatbot Service

## Overview

This integration enhances the MantraPath Chatbot Service with intelligent cross-service coordination through the Action Orchestrator. The integration enables:

- **ML-powered intent classification** with confidence scoring
- **Cross-service workflow coordination** for mood tracking, translation, and more
- **Cultural context adaptation** with multi-language support
- **Intelligent fallback mechanisms** for reliability

## Architecture

```
Frontend → API Gateway → Chatbot Service → Action Orchestrator → Multiple Services
                    ↓
              Enhanced Chat Response with Orchestration Metadata
```

## Key Components

### 1. Action Orchestrator Client (`src/clients/action_orchestrator_client.py`)
- Handles communication with Action Orchestrator service
- Provides request/response models and error handling
- Configurable timeouts and retry logic
- Health checking capabilities

### 2. Enhanced Chatbot Service (`src/services/enhanced_chatbot_service.py`)
- Wraps existing chatbot service with orchestration capabilities
- Provides intelligent intent-based response generation
- Handles cultural adaptation and mood context integration
- Fallback to base chatbot service for reliability

### 3. New API Endpoint (`/api/chatbot/enhanced/chat`)
- Enhanced chat endpoint with Action Orchestrator integration
- Builds rich conversation context with mood and cultural data
- Returns enhanced responses with orchestration metadata
- Saves enhanced chat interactions with intent and action data

## Configuration Variables

All configuration is variablized for flexibility:

```bash
# Action Orchestrator Integration
ACTION_ORCHESTRATOR_URL=http://action-orchestrator:8012
ACTION_ORCHESTRATOR_ENABLED=true
ACTION_ORCHESTRATOR_TIMEOUT=60
ACTION_ORCHESTRATOR_MAX_RETRIES=3

# Enhanced Chatbot Configuration
ACTION_ORCHESTRATOR_INTEGRATION=true
CHATBOT_FALLBACK_TO_BASE=true

# Intent Processing Thresholds
MOOD_INTENT_THRESHOLD=0.7
TRANSLATION_INTENT_THRESHOLD=0.6
CROSS_SERVICE_THRESHOLD=0.8
```

## API Gateway Routes Added

Added routes for Action Orchestrator endpoints:

```python
# Action Orchestrator routes
/api/v1/orchestrate
/api/v1/workflow/*
/api/v1/intents
/api/v1/cultural-contexts
```

## Enhanced Chat Response Format

The enhanced chat endpoint returns responses with additional metadata:

```json
{
  "response": "I understand you'd like to track your mood...",
  "session_id": "session_123",
  "message_type": "enhanced_chat",
  "intent": {
    "intent_type": "mood_tracking",
    "confidence": 0.95,
    "confidence_level": "high",
    "parameters": {...}
  },
  "orchestration_metadata": {
    "workflow_id": "wf_456",
    "execution_time_ms": 150,
    "services_involved": ["mood_service", "chatbot_service"],
    "success_rate": 1.0
  },
  "suggested_actions": [
    {
      "action": "track_mood",
      "label": "Track Current Mood",
      "description": "Record how you're feeling right now",
      "confidence": 0.95
    }
  ],
  "mood_insights": {...},
  "cultural_adaptations": {
    "language": "en",
    "communication_style": "casual"
  }
}
```

## Benefits of Integration

### 1. **Intelligent Intent Recognition**
- ML-powered classification of user intents
- Cultural context-aware processing
- Confidence scoring for decision making

### 2. **Cross-Service Coordination**
- Automatic mood tracking from conversations
- Translation integration for multi-language support
- Journal entry creation from chat context

### 3. **Enhanced User Experience**
- Contextual suggestions based on user intent
- Cultural adaptation for different regions/languages
- Mood-aware conversation handling

### 4. **Reliability & Fallback**
- Graceful degradation when Action Orchestrator is unavailable
- Fallback to existing chatbot service
- Configurable error handling and retry logic

## Usage Examples

### 1. Basic Enhanced Chat
```bash
POST /api/chatbot/enhanced/chat
{
  "message": "I'm feeling anxious today",
  "session_id": "session_123"
}
```

### 2. Multi-language Support
```bash
POST /api/chatbot/enhanced/chat
{
  "message": "मुझे आज चिंता हो रही है",
  "session_id": "session_123"
}
```

### 3. Intent-based Actions
```bash
POST /api/chatbot/enhanced/chat
{
  "message": "I want to track my mood and write in my journal",
  "session_id": "session_123"
}
```

## Future Enhancements

1. **Voice Integration**: Connect with Voice Service for speech-to-text processing
2. **Advanced Analytics**: Leverage conversation insights for personalized recommendations
3. **Proactive Interventions**: Use mood patterns to suggest preventive actions
4. **Cultural Intelligence**: Expand cultural adaptation capabilities

## Testing

The integration includes comprehensive testing through:

1. **Unit Tests**: Test individual components with mocks
2. **Integration Tests**: Test end-to-end workflows
3. **Fallback Tests**: Verify graceful degradation
4. **Performance Tests**: Ensure response time targets

## Monitoring

Monitor the integration through:

1. **Health Checks**: Both services expose health endpoints
2. **Metrics**: Track response times, success rates, and error rates
3. **Logging**: Structured logging with correlation IDs
4. **Alerts**: Automated alerts for service failures

## Deployment

The integration is containerized and ready for deployment:

1. Update environment variables in `.env`
2. Rebuild Docker containers
3. Deploy with updated docker-compose configuration
4. Verify health checks and connectivity

This integration represents a significant step forward in creating an intelligent, culturally-aware, and contextually-rich chat experience for MantraPath users.
