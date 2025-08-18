# Chatbot Service Enhancement - Phase 1 Implementation

## Overview
This document describes Phase 1 implementation of the MantraPath Chatbot Service enhancement, focusing on eliminating external API dependencies and integrating with internal MantraPath services.

## Architecture

### Service Integration Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│                    Chatbot Service (Enhanced)                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Response      │  │    Context      │  │   Workflow      │ │
│  │   Generator     │  │   Manager       │  │   Manager       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      Service Clients                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌──────────── │
│  │   Models    │ │     ML      │ │    AI       │ │Translation  │ │
│  │   Service   │ │   Service   │ │  Context    │ │   Service   │ │
│  │   Client    │ │   Client    │ │   Store     │ │   Client    │ │
│  │             │ │             │ │   Client    │ │             │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│  ┌─────────────┐ ┌─────────────┐                                │
│  │    Voice    │ │   Action    │                                │
│  │   Service   │ │Orchestrator │                                │
│  │   Client    │ │   Client    │                                │
│  └─────────────┘ └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

## Implemented Components

### 1. Models Service Client (`models_service_client.py`)
**Purpose**: Integration with MantraPath Models Service for NLP capabilities

**Features**:
- **Sentiment Analysis**: Multi-language sentiment detection with emotion mapping
- **Text Embeddings**: 500-dimensional vectors for semantic understanding
- **Intent Classification**: Crisis support, emotional support, general chat detection
- **Response Generation**: Culturally-aware response generation
- **Text-to-Speech**: Hindi and English voice synthesis
- **Speech-to-Text**: Audio transcription capabilities
- **Batch Processing**: Efficient bulk operations

**Supported Languages**: 17+ Indian languages including Hindi, Bengali, Tamil, Telugu, Urdu, etc.

### 2. AI Context Store Client (`ai_context_store_client.py`)
**Purpose**: Comprehensive user context management and aggregation

**Features**:
- **User Context Management**: Preferences, history, cultural background
- **Conversation Context**: Session tracking, mood patterns, topics
- **AI Insights**: Behavioral patterns, intervention suggestions
- **Context Aggregation**: Multi-dimensional user understanding
- **Health Checks**: Service availability monitoring

### 3. ML Service Client (`ml_service_client.py`)
**Purpose**: Crisis detection and machine learning insights

**Features**:
- **Crisis Risk Assessment**: Multi-level risk evaluation (low, medium, high, critical)
- **User Insights**: Behavioral pattern analysis
- **Need Prediction**: Proactive user need identification
- **Intervention Recommendations**: Action suggestions based on user state
- **Conversation Effectiveness**: Outcome measurement and optimization

### 4. Translation Service Client (`translation_service_client.py`)
**Purpose**: Cultural adaptation and multi-language support

**Features**:
- **Language Detection**: Automatic language identification
- **Text Translation**: 17+ language translation with cultural adaptation
- **Cultural Context**: Region-specific communication styles
- **Cultural Adaptation**: Response modification for cultural appropriateness
- **Batch Translation**: Efficient multi-text processing

### 5. Voice Service Client (`voice_service_client.py`)
**Purpose**: Voice interaction capabilities

**Features**:
- **Text-to-Speech**: Multi-language voice synthesis
- **Speech-to-Text**: Audio transcription
- **Voice Profiles**: Multiple voice options per language
- **Emotional Synthesis**: Emotion-aware speech generation
- **Batch Processing**: Multiple audio processing

### 6. Action Orchestrator Client (`orchestrator_client.py`)
**Purpose**: Workflow management and action coordination

**Features**:
- **Action Execution**: Single and batch action processing
- **Workflow Management**: Multi-step process orchestration
- **Status Tracking**: Real-time execution monitoring
- **Workflow Creation**: Dynamic workflow definition
- **Priority Handling**: Urgent, high, medium, low priority actions

## Configuration Management

### Configuration System (`config.py`)
**Purpose**: Centralized configuration for all service integrations

**Features**:
- **Environment-based Configuration**: All settings from environment variables
- **Service Configuration**: URL, timeout, retry settings for each service
- **Feature Toggles**: Enable/disable specific capabilities
- **Validation**: Configuration validation with error reporting
- **Language Settings**: Multi-language support configuration

## Testing Strategy

### Unit Testing (`test_models_service_client.py`)
**Comprehensive test coverage (80%+)**:
- Service client initialization
- HTTP request/response handling
- Error handling and fallbacks
- Data parsing and validation
- Authentication token handling
- Configuration management

## Deployment Considerations

### Environment Variables
```bash
# Service URLs
MODELS_SERVICE_URL=http://models-service:8085
ML_SERVICE_URL=http://ml-service:8008
AI_CONTEXT_STORE_URL=http://ai-context-store:8007
TRANSLATION_SERVICE_URL=http://translation-service:8005
VOICE_SERVICE_URL=http://voice-service:8003
ACTION_ORCHESTRATOR_URL=http://action-orchestrator:8009

# Service Settings
MODELS_SERVICE_TIMEOUT=30
MODELS_SERVICE_ENABLED=true
CHATBOT_DEFAULT_LANGUAGE=hi
CHATBOT_CRISIS_THRESHOLD=0.7

# Feature Toggles
CHATBOT_ENABLE_VOICE=true
CHATBOT_ENABLE_TRANSLATION=true
CHATBOT_ENABLE_ML_INSIGHTS=true
CHATBOT_CULTURAL_ADAPTATION_ENABLED=true
```

## Dependencies

### Required Python Packages
```
httpx>=0.24.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
dataclasses  # Built-in Python 3.7+
asyncio      # Built-in Python 3.7+
logging      # Built-in Python
```

### Internal Services
- Models Service (8085) - NLP and TTS/STT
- ML Service (8008) - Crisis detection and insights
- AI Context Store (8007) - User context management
- Translation Service (8005) - Multi-language support
- Voice Service (8003) - Voice interactions
- Action Orchestrator (8009) - Workflow management

All services must be running and healthy for full functionality, with graceful degradation when services are unavailable.
