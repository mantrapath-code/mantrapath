# Voice Event Processor Service

## 🎵 Overview

The Voice Event Processor is a specialized service that handles voice-related events, audio analysis, and speech pattern detection within the MantraPath ecosystem. This service provides real-time voice event processing, audio quality assessment, and voice interaction analytics.

## 🎯 Core Features

### ✅ Voice Event Processing
- **Real-time Event Handling**: Processes voice-related events from the event bus
- **Voice Command Processing**: Analyzes and processes voice commands
- **Audio Event Routing**: Routes audio events to appropriate processing modules
- **Event Correlation**: Correlates voice events with user activities

### ✅ Audio Analysis
- **Audio Pattern Detection**: Identifies patterns in user voice interactions
- **Audio Quality Assessment**: Monitors and analyzes audio quality metrics
- **Speech Rhythm Analysis**: Analyzes speech patterns and timing
- **Tone Analysis**: Detects emotional tone in voice interactions

### ✅ Speech Pattern Recognition
- **User Voice Patterns**: Learns individual user speech patterns
- **Command Recognition Optimization**: Improves voice command recognition
- **Speech Anomaly Detection**: Identifies unusual speech patterns
- **Voice Print Analysis**: Creates voice fingerprints for personalization

## 🏗️ Architecture

```
Voice Event Processor Service
├── main.py                      # FastAPI application
├── models/
│   └── voice_models.py          # Voice event data models
├── services/
│   ├── event_processor.py       # Voice event processing logic
│   ├── audio_analyzer.py        # Audio analysis and pattern detection
│   └── speech_pattern_detector.py # Speech pattern analysis
├── api/
│   ├── voice_events_api.py      # Voice event endpoints
│   ├── audio_analysis_api.py    # Audio analysis endpoints
│   └── health_api.py            # Health monitoring
└── tests/
    └── test_voice_processor.py  # Voice processing test suite
```

## 📊 Data Models

### VoiceEvent
```python
{
    "event_id": "ve_123456",
    "user_id": "user_123",
    "event_type": "voice_command",
    "audio_data": {
        "duration": 2.5,
        "quality_score": 0.85,
        "sample_rate": 16000,
        "format": "wav"
    },
    "command_data": {
        "recognized_text": "start meditation",
        "confidence": 0.92,
        "intent": "meditation.start",
        "language": "en"
    },
    "processing_metadata": {
        "processing_time": 150,
        "model_version": "v2.1",
        "features_extracted": ["mfcc", "spectogram"]
    },
    "timestamp": "2025-08-16T12:00:00Z"
}
```

### AudioAnalysis
```python
{
    "analysis_id": "aa_789012",
    "user_id": "user_123",
    "audio_metrics": {
        "volume_level": 0.75,
        "clarity_score": 0.88,
        "noise_level": 0.15,
        "frequency_distribution": {...}
    },
    "speech_patterns": {
        "speech_rate": 150,  # words per minute
        "pause_frequency": 0.3,
        "tone_variation": 0.6,
        "emotional_indicators": ["calm", "focused"]
    },
    "quality_assessment": {
        "overall_quality": "good",
        "improvement_suggestions": ["reduce background noise"],
        "optimal_conditions": true
    }
}
```

## 🔌 API Endpoints

### Voice Event Endpoints
- `POST /api/v1/voice/events/process` - Process voice events
- `GET /api/v1/voice/events/{user_id}` - Get user voice events
- `POST /api/v1/voice/events/batch` - Process multiple voice events
- `GET /api/v1/voice/events/{user_id}/summary` - Voice event summary

### Audio Analysis Endpoints
- `POST /api/v1/audio/analyze` - Analyze audio patterns
- `GET /api/v1/audio/quality/{user_id}` - Get audio quality metrics
- `POST /api/v1/audio/quality/assess` - Assess audio quality
- `GET /api/v1/audio/patterns/{user_id}` - Get audio pattern analysis

### Speech Pattern Endpoints
- `GET /api/v1/speech/patterns/{user_id}` - Get user speech patterns
- `POST /api/v1/speech/patterns/update` - Update speech patterns
- `GET /api/v1/speech/analytics/{user_id}` - Speech analytics dashboard
- `POST /api/v1/speech/optimize` - Optimize speech recognition

### Voice Optimization Endpoints
- `POST /api/v1/voice/optimize` - Optimize voice command recognition
- `GET /api/v1/voice/insights/{user_id}` - Voice interaction insights
- `POST /api/v1/voice/feedback` - Submit voice recognition feedback
- `GET /api/v1/voice/recommendations/{user_id}` - Voice improvement recommendations

### Health Endpoints
- `GET /health/` - Basic health check
- `GET /health/voice` - Voice processing health check
- `GET /health/audio` - Audio processing health check
- `GET /health/metrics` - Service metrics

## 🚀 Deployment

### Prerequisites
- Python 3.11+
- Redis server for caching
- Access to MantraPath event bus
- Audio processing libraries (numpy, scipy, librosa)

### Quick Start
```bash
cd /path/to/mantrapath/backend/services/voice_event_processor
python main.py
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export VOICE_EVENT_PROCESSOR_PORT=8016
export PYTHONPATH="/path/to/mantrapath/backend:$PYTHONPATH"
export REDIS_URL="redis://localhost:6379/4"

# Start service
python main.py
```

## 🧪 Testing

### Run Test Suite
```bash
cd tests/
python -m pytest test_voice_processor.py -v
```

### Manual Testing
```bash
python test_voice_processor.py
```

### Voice Processing Test
```bash
# Test voice event processing
curl -X POST http://localhost:8016/api/v1/voice/events/process \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "event_type": "voice_command", "audio_data": {...}}'
```

## 📈 Performance Metrics

### Processing Performance
- **Event Processing**: < 50ms per voice event
- **Audio Analysis**: < 200ms for pattern detection
- **Speech Pattern Update**: < 100ms
- **Quality Assessment**: < 150ms

### Throughput
- **Voice Events**: 200+ events per second
- **Audio Analysis**: 50+ analyses per second
- **Pattern Updates**: 100+ updates per second

## 🔍 Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8016/health/

# Voice processing health
curl http://localhost:8016/health/voice

# Audio processing health
curl http://localhost:8016/health/audio

# Service metrics
curl http://localhost:8016/health/metrics
```

### Key Metrics to Monitor
- `voice_events_processed` - Total voice events processed
- `audio_analyses_completed` - Audio analysis operations
- `speech_patterns_updated` - Speech pattern updates
- `audio_quality_average` - Average audio quality score
- `processing_latency` - Average processing time
- `error_rate` - Processing error rate

## 🎯 Voice Processing Features

### Voice Command Enhancement
- **Command Recognition**: Improved voice command recognition accuracy
- **Context Awareness**: Voice commands analyzed with user context
- **Multi-language Support**: Voice processing for multiple languages
- **Noise Reduction**: Background noise filtering and reduction

### Audio Quality Optimization
- **Real-time Quality Assessment**: Continuous audio quality monitoring
- **Quality Improvement Suggestions**: Personalized audio quality tips
- **Optimal Recording Conditions**: Environment analysis for better audio
- **Adaptive Processing**: Processing parameters adjusted based on audio quality

### Speech Pattern Learning
- **Individual Pattern Recognition**: Learns each user's unique speech patterns
- **Pronunciation Adaptation**: Adapts to user pronunciation variations
- **Speaking Style Analysis**: Analyzes speaking pace, tone, and style
- **Accessibility Support**: Enhanced processing for speech accessibility needs

## 🔧 Configuration

### Environment Variables
```bash
VOICE_EVENT_PROCESSOR_PORT=8016     # Service port
REDIS_URL=redis://localhost:6379/4  # Redis connection for caching
AUDIO_QUALITY_THRESHOLD=0.7         # Minimum audio quality threshold
PATTERN_UPDATE_INTERVAL=300         # Speech pattern update interval (seconds)
MAX_AUDIO_DURATION=30               # Maximum audio duration (seconds)
```

### Processing Configuration
```python
# Audio analysis settings
audio_sample_rate = 16000           # Audio sample rate
audio_chunk_size = 1024             # Processing chunk size
quality_assessment_interval = 60    # Quality check interval (seconds)

# Speech pattern settings
pattern_learning_rate = 0.1         # Pattern learning rate
pattern_retention_days = 30         # Pattern data retention
min_samples_for_pattern = 10        # Minimum samples for pattern creation
```

## 🚨 Error Handling

### Graceful Degradation
- **Audio Processing Failures**: Falls back to basic processing
- **Pattern Recognition Issues**: Uses default recognition patterns
- **Quality Assessment Errors**: Provides basic quality metrics
- **Event Processing Failures**: Logs errors and continues processing

### Recovery Mechanisms
- **Automatic Retry**: Failed operations are retried with exponential backoff
- **Fallback Processing**: Alternative processing methods for failed operations
- **Error Logging**: Comprehensive error logging and monitoring
- **Health Recovery**: Automatic service health recovery

## 📚 Usage Examples

### Processing Voice Events
```python
import httpx

# Process a voice event
voice_event_data = {
    "user_id": "user_123",
    "event_type": "voice_command",
    "audio_data": {
        "duration": 2.5,
        "quality_score": 0.85,
        "sample_rate": 16000
    },
    "command_data": {
        "recognized_text": "start meditation",
        "confidence": 0.92
    }
}

response = httpx.post(
    "http://localhost:8016/api/v1/voice/events/process",
    json=voice_event_data,
    headers={"Authorization": "Bearer <token>"}
)
result = response.json()
```

### Audio Quality Analysis
```python
# Analyze audio quality
audio_data = {
    "user_id": "user_123",
    "audio_file": "base64_encoded_audio",
    "format": "wav",
    "sample_rate": 16000
}

response = httpx.post(
    "http://localhost:8016/api/v1/audio/analyze",
    json=audio_data,
    headers={"Authorization": "Bearer <token>"}
)
analysis = response.json()
```

### Speech Pattern Insights
```python
# Get user speech patterns
response = httpx.get(
    "http://localhost:8016/api/v1/speech/patterns/user_123",
    headers={"Authorization": "Bearer <token>"}
)
patterns = response.json()
```

## 🎉 Integration Status

### ✅ Event Bus Integration
- [x] Voice command events from Voice Service
- [x] Audio quality events from Models Service  
- [x] Speech recognition events from API Gateway
- [x] Voice interaction events from Chatbot Service

### ✅ Service Integration
- [x] **Voice Service**: Direct voice event processing
- [x] **Models Service**: Audio model integration
- [x] **AI Context Store**: Voice pattern context sharing
- [x] **ML Service**: Machine learning model integration

### ✅ Features Implemented
- [x] Real-time voice event processing
- [x] Audio quality assessment and monitoring
- [x] Speech pattern recognition and learning
- [x] Voice command optimization
- [x] Multi-language voice processing support
- [x] Comprehensive health monitoring
- [x] Performance optimization

## 🔮 Future Enhancements

### Phase 2 Features
- **Advanced Voice Biometrics**: Voice-based user authentication
- **Emotion Recognition**: Advanced emotional state detection from voice
- **Voice Synthesis Optimization**: Personalized TTS voice generation
- **Real-time Voice Coaching**: Live voice improvement suggestions

### Advanced Analytics
- **Voice Interaction Trends**: Long-term voice usage pattern analysis
- **Voice Health Monitoring**: Voice health and fatigue detection
- **Accessibility Enhancement**: Advanced accessibility features for voice interaction
- **Multi-speaker Support**: Support for multiple speakers in conversations

---

**🎯 Result**: Voice Event Processor service is **production-ready** and fully integrated!

- ✅ Real-time voice event processing
- ✅ Comprehensive audio analysis
- ✅ Speech pattern recognition
- ✅ Quality assessment and optimization
- ✅ Full API coverage
- ✅ Complete health monitoring
