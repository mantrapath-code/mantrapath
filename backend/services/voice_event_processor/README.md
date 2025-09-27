# Voice Event Processor Service

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-active-green.svg)
![Port](https://img.shields.io/badge/port-8015-orange.svg)
![Framework](https://img.shields.io/badge/framework-FastAPI-green.svg)

## 📋 Table of Contents

- [🎯 Service Overview](#-service-overview)
- [📂 Directory Structure](#-directory-structure)
- [⚙️ Service Functionality](#️-service-functionality)
- [🌐 API Endpoints & Routing](#-api-endpoints--routing)
- [🔌 Port & Configuration](#-port--configuration)
- [🔄 Request Flow](#-request-flow)
- [🔗 Service Communication](#-service-communication)
- [🧠 Design Documentation](#-design-documentation)
- [🚧 Incomplete Implementations](#-incomplete-implementations--todos)
- [🌟 Future Development Plans](#-future-development-plans)
- [🚀 Quick Start](#-quick-start)
- [🧪 Testing](#-testing)
- [📊 Monitoring & Logging](#-monitoring--logging)

---

## 🎯 Service Overview

The **Voice Event Processor Service** is a real-time voice analytics and event processing engine that handles live voice stream processing, voice activity detection, emotion recognition from voice patterns, and real-time event broadcasting. It serves as the central hub for voice-related services communication within the MantraPath platform.

### Primary Functions:
- **Real-time Voice Stream Processing**: Handles continuous audio streams via WebSockets
- **Voice Activity Detection (VAD)**: Intelligent detection of speech vs. silence
- **Emotion Analysis**: Advanced emotion recognition from voice patterns
- **Event Broadcasting**: Real-time event distribution to connected clients
- **Multi-language Support**: Processes voice events in multiple languages
- **Cultural Speech Analysis**: Analyzes cultural patterns in speech

### Integration Role:
This service acts as the bridge between voice input and the broader MantraPath ecosystem, processing voice events and triggering appropriate responses from other services like the chatbot, translation, and AI event processing services.

---

## 📂 Directory Structure

```
voice_event_processor/
├── main.py                    # 🎯 Basic implementation with core functionality
├── main_enhanced.py          # 🚀 Enhanced version with full features
├── requirements.txt          # 📦 Full dependency list
├── requirements.min.txt      # 📦 Minimal dependencies for basic functionality
├── Dockerfile               # 🐳 Full Docker configuration with audio processing
├── Dockerfile.minimal       # 🐳 Lightweight Docker configuration
└── README.md               # 📚 This comprehensive documentation
```

### File Descriptions:

- **`main.py`** (281 lines): Core voice event processor with basic WebSocket streaming, voice activity detection, and simple emotion analysis
- **`main_enhanced.py`** (602 lines): Advanced implementation with multi-language support, NATS integration, cultural analysis, and enhanced voice processing pipeline
- **`requirements.txt`**: Complete dependencies including audio processing libraries (librosa, soundfile, etc.)
- **`requirements.min.txt`**: Minimal runtime dependencies (FastAPI, uvicorn, pydantic only)
- **`Dockerfile`**: Full container with audio processing system dependencies
- **`Dockerfile.minimal`**: Lightweight container for basic functionality

---

## ⚙️ Service Functionality

### Core Features

#### 1. **Voice Activity Detection (VAD)**
```python
class VoiceStreamConfig(BaseModel):
    sample_rate: int = 16000
    chunk_size: int = 1024
    vad_sensitivity: float = 0.7
    emotion_analysis: bool = True
```

#### 2. **Real-time Stream Processing**
- WebSocket-based continuous audio processing
- Chunked audio data handling
- Stream management with connection tracking
- Configurable processing parameters per stream

#### 3. **Emotion Recognition**
```python
class EmotionAnalysisResult(BaseModel):
    emotion: str
    confidence: float
    valence: Optional[float] = None
    arousal: Optional[float] = None
```

#### 4. **Event Generation**
```python
class VoiceEvent(BaseModel):
    event_type: str  # "speech_start", "speech_end", "emotion_detected", "silence"
    timestamp: float
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
```

### Enhanced Features (main_enhanced.py)

#### 1. **Multi-language Processing**
- Automatic language detection
- Language-specific voice processing
- Cultural speech pattern analysis

#### 2. **Service Integration**
- NATS event publishing/subscribing
- Integration with chatbot service
- Voice service STT integration
- AI event processor communication

#### 3. **Advanced Analytics**
- Voice emotion analysis
- Cultural context detection
- Quality assessment
- Performance metrics

---

## 🌐 API Endpoints & Routing

### Basic Version (main.py)

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|--------|--------|
| `GET` | `/` | Root endpoint | None | Service info |
| `GET` | `/health` | Health check | None | Service health status |
| `GET` | `/api/v1/streams/status` | Stream status | None | Active streams info |
| `POST` | `/api/v1/voice/process` | Process voice chunk | audio_data, config | Processing result |
| `WebSocket` | `/ws/voice/{client_id}` | Real-time streaming | WebSocket connection | Live voice events |
| `GET` | `/api/v1/config` | Get configuration | None | Processing config |
| `GET` | `/api/v1/stats` | Get statistics | None | Processing stats |

### Enhanced Version (main_enhanced.py)

| Method | Endpoint | Purpose | Input | Output |
|--------|----------|---------|--------|--------|
| `GET` | `/health` | Enhanced health check | None | Detailed service status |
| `POST` | `/api/voice/process` | Process voice event | VoiceEventRequest | Event processing result |
| `POST` | `/api/voice/stream/start` | Start voice stream | user_id, session_id, language_hint | Stream initialization |
| `POST` | `/api/voice/stream/chunk/{stream_id}` | Process stream chunk | audio file, chunk_id, is_final | Chunk processing result |
| `GET` | `/api/voice/streams/active` | Active streams | None | Current active streams |
| `POST` | `/api/voice/analyze` | Analyze voice content | audio file, transcription, language | Voice analysis results |

### WebSocket Communication

#### Connection Flow:
1. **Connect**: `ws://localhost:8015/ws/voice/{client_id}`
2. **Start Stream**: Send `{"type": "start_stream"}`
3. **Send Audio**: Send `{"type": "audio_chunk", "data": "base64_audio"}`
4. **Receive Events**: Get real-time voice events
5. **Stop Stream**: Send `{"type": "stop_stream"}`

#### Message Types:
```javascript
// Control Messages
{"type": "start_stream"}
{"type": "stop_stream"}
{"type": "ping"}

// Audio Data
{"type": "audio_chunk", "data": "base64_encoded_audio"}

// Response Events
{"type": "connection_established", "client_id": "...", "timestamp": ...}
{"type": "voice_event", "event": {...}}
{"type": "stream_started", "timestamp": ...}
```

---

## 🔌 Port & Configuration

### Default Port
- **Service Port**: `8015`
- **Environment Variable**: `VOICE_EVENT_PROCESSOR_PORT`

### Environment Configuration

#### Core Configuration:
```bash
# Service Configuration
VOICE_EVENT_PROCESSOR_HOST=0.0.0.0
VOICE_EVENT_PROCESSOR_PORT=8015
LOG_LEVEL=INFO
ENVIRONMENT=development

# Database & Message Queue
DATABASE_URL=postgresql://mantrapath:mantrapath123@postgres:5432/mantrapath
REDIS_URL=redis://redis:6379
NATS_URL=nats://nats:4222

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

#### Voice Processing Configuration:
```bash
# Stream Management
MAX_CONCURRENT_STREAMS=100
VAD_SENSITIVITY=0.7
VOICE_STREAMING_ENABLED=true

# Audio Processing
AUDIO_SAMPLE_RATE=16000
AUDIO_CHUNK_SIZE=1024
VOICE_EMOTION_MODEL=speechbrain/emotion-recognition-wav2vec2-IEMOCAP

# Performance Tuning
STREAM_TIMEOUT=30
ACTIVITY_DETECTION_TIMEOUT=50
EMOTION_ANALYSIS_TIMEOUT=200
```

#### Service URLs (Enhanced Version):
```python
SERVICE_URLS = {
    'chatbot_service': 'http://chatbot-service:8004',
    'voice_service': 'http://voice-service:8011',
    'translation_service': 'http://translation-service:8010',
    'models_service': 'http://models-service:8080',
    'ai_event_processor': 'http://ai-event-processor:8014',
    'memory_service': 'http://memory-service:8017',
}
```

---

## 🔄 Request Flow

### Basic Voice Processing Flow

```mermaid
graph TD
    A[Client] -->|WebSocket Connect| B[Connection Manager]
    B -->|Accept Connection| C[Voice Stream Active]
    C -->|Audio Chunk| D[Voice Processing]
    D -->|VAD Analysis| E[Voice Activity Detection]
    E -->|Speech Detected| F[Emotion Analysis]
    F -->|Generate Event| G[Voice Event Created]
    G -->|Broadcast| H[Send to Client]
    H -->|Continue| C
```

### Enhanced Processing Flow

```mermaid
graph TD
    A[Audio Input] -->|Stream Chunk| B[Voice Event Manager]
    B -->|Process Stream| C[Audio Combination]
    C -->|STT Request| D[Voice Service]
    D -->|Transcription| E[Language Detection]
    E -->|Emotion Analysis| F[AI Event Processor]
    F -->|Cultural Analysis| G[Cultural Context]
    G -->|Create Event| H[Voice Interaction Event]
    H -->|NATS Publish| I[Event Distribution]
    I -->|Trigger Response| J[Chatbot Service]
    J -->|Audio Response| K[Complete Interaction]
```

### Step-by-Step Request Processing

#### 1. **WebSocket Connection**
```python
async def websocket_voice_stream(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    # Send connection confirmation
    # Enter message processing loop
```

#### 2. **Audio Chunk Processing**
```python
# Receive audio data
data = await websocket.receive_text()
message = json.loads(data)

if message_type == "audio_chunk":
    # Process voice activity detection
    # Perform emotion analysis if enabled
    # Generate voice events
    # Send real-time feedback
```

#### 3. **Enhanced Stream Processing**
```python
async def process_voice_stream(self, stream_event: VoiceStreamEvent):
    # Accumulate chunks
    # Process complete stream when final
    # Speech-to-text conversion
    # Emotion and cultural analysis
    # Publish interaction event
```

---

## 🔗 Service Communication

### Outbound Communications

#### 1. **Voice Service Integration** (Port 8011)
```python
# Speech-to-Text Processing
response = await self.http_client.post(
    f"{SERVICE_URLS['voice_service']}/api/v1/voice/stt",
    files={"audio": audio_bytes},
    data={"language": language_hint or "auto"}
)
```

#### 2. **AI Event Processor** (Port 8014)
```python
# Voice Emotion Analysis
emotion_result = await self.http_client.post(
    f"{SERVICE_URLS['ai_event_processor']}/api/analyze/voice_emotion",
    json={
        "audio_data": audio_data,
        "transcription": transcription,
        "language": language
    }
)

# Cultural Pattern Analysis  
cultural_result = await self.http_client.post(
    f"{SERVICE_URLS['ai_event_processor']}/api/analyze/cultural_speech",
    json={
        "transcription": transcription,
        "language": language,
        "voice_features": emotion_data.get("voice_features", {})
    }
)
```

#### 3. **Chatbot Service** (Port 8004)
```python
# Trigger Voice Response
response = await self.http_client.post(
    f"{SERVICE_URLS['chatbot_service']}/api/chat/text",
    json={
        "message": interaction_event.transcribed_text,
        "session_id": interaction_event.session_id,
        "language": interaction_event.detected_language,
        "voice_response": True
    }
)
```

### NATS Event Publishing

#### Voice Events Published:
```python
# Voice Interaction Processed
await self.nats_client.publish(
    "voice.interaction.processed",
    interaction_event.dict()
)

# Voice Interaction Completed
await self.nats_client.publish(
    "voice.interaction.completed",
    interaction_event.dict()
)
```

#### NATS Event Subscriptions:
```python
# Voice Interaction Processing
await nats_client.subscribe("voice.interaction.processed", handle_voice_interaction)

# Real-time Stream Chunks
await nats_client.subscribe("voice.stream.chunk", handle_voice_stream_chunk)

# Voice Events by Type
await nats_client.subscribe(f"voice.event.{event_type}", handle_voice_event)
```

### Inbound Communications

#### 1. **API Gateway Integration** (Port 8000)
- Registered as `voice-event-processor` service
- Health check endpoint monitoring
- Request routing and load balancing

#### 2. **Frontend Integration** (WebSocket & REST)
- Real-time voice streaming from web clients
- Voice analysis requests
- Stream status monitoring

### Service Discovery

The service is registered in the API Gateway's service registry:

```python
# In API Gateway configuration
voice_event_processor_url = "http://voice-event-processor:8015"
voice_event_processor_health_path = "/health"

# Service registry entry
("voice-events", service_config.voice_event_processor_url, service_config.voice_event_processor_health_path)
```

---

## 🧠 Design Documentation

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Voice Event Processor                    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ Connection  │  │ Voice Event  │  │ Stream          │ │
│  │ Manager     │  │ Manager      │  │ Processing      │ │
│  │             │  │              │  │                 │ │
│  └─────────────┘  └──────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ VAD         │  │ Emotion      │  │ Language        │ │
│  │ Engine      │  │ Analysis     │  │ Detection       │ │
│  │             │  │              │  │                 │ │
│  └─────────────┘  └──────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │ NATS        │  │ HTTP         │  │ WebSocket       │ │
│  │ Client      │  │ Client       │  │ Manager         │ │
│  │             │  │              │  │                 │ │
│  └─────────────┘  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Low-Level Design

#### 1. **Connection Management**
```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.voice_streams: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str)
    def disconnect(self, websocket: WebSocket, client_id: str)
    async def send_personal_message(self, message: str, websocket: WebSocket)
    async def broadcast(self, message: str)
```

#### 2. **Voice Event Processing**
```python
class VoiceEventManager:
    def __init__(self, http_client: httpx.AsyncClient, nats_client: NATSClient):
        self.http_client = http_client
        self.nats_client = nats_client
        self.active_streams = {}
        self.processing_queue = asyncio.Queue()
        self.emotion_cache = {}
```

#### 3. **Event Models**
```python
# Basic Events
class VoiceEvent(BaseModel):
    event_type: str
    timestamp: float
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

# Enhanced Events
class VoiceInteractionEvent(BaseModel):
    interaction_id: str
    user_id: str
    session_id: Optional[str] = None
    audio_input: str
    detected_language: str
    transcribed_text: str
    emotion_analysis: Dict[str, Any]
    cultural_context: Dict[str, Any]
    response_generated: bool = False
    response_audio_url: Optional[str] = None
```

### Design Decisions & Rationale

#### 1. **Dual Implementation Strategy**
- **Basic Version (`main.py`)**: Provides core functionality with minimal dependencies for lightweight deployment
- **Enhanced Version (`main_enhanced.py`)**: Full-featured implementation with advanced integrations

**Rationale**: Allows for flexible deployment based on requirements and infrastructure capabilities

#### 2. **WebSocket-First Architecture**
- Real-time voice streaming requires low-latency communication
- WebSocket connections provide persistent, bidirectional communication
- Supports multiple concurrent streams with efficient resource usage

#### 3. **Asynchronous Processing Pipeline**
- Voice processing operations are inherently I/O bound
- Async/await pattern enables high concurrency
- Non-blocking operations maintain responsiveness

#### 4. **Service Integration Pattern**
- HTTP client for synchronous service communication
- NATS for asynchronous event-driven communication
- Separation of concerns with dedicated service endpoints

#### 5. **Configuration-Driven Processing**
- Flexible audio processing parameters per stream
- Environment-based configuration for different deployment scenarios
- Runtime configuration updates for optimization

---

## 🚧 Incomplete Implementations & TODOs

### Current Limitations

#### 1. **Audio Processing (Both Versions)**
```python
# TODO: Implement actual audio processing algorithms
# Current implementation uses mock/simulated processing

def _combine_audio_chunks(self, chunks: List[Dict[str, Any]]) -> str:
    """Combine audio chunks into single audio data"""
    # Sort chunks by chunk_id
    sorted_chunks = sorted(chunks, key=lambda x: x["chunk_id"])
    
    # For now, return the first chunk's audio data
    # TODO: In production, you'd properly concatenate audio
    if sorted_chunks:
        return sorted_chunks[0]["audio_data"]
    return ""
```

#### 2. **Voice Activity Detection**
```python
# TODO: Implement real VAD algorithms
# Current: Simulated detection based on audio data length
if len(audio_data) > 0:
    events.append(VoiceEvent(
        event_type="speech_detected",
        timestamp=asyncio.get_event_loop().time(),
        confidence=0.85,  # Mock confidence
        metadata={"chunk_size": len(audio_data)}
    ))
```

#### 3. **Emotion Recognition**
```python
# TODO: Integrate actual emotion recognition models
# Current: Mock emotion analysis
emotion_result = EmotionAnalysisResult(
    emotion="neutral",  # Mock result
    confidence=0.75,
    valence=0.5,
    arousal=0.4
)
```

### Missing Features

#### 1. **Real Audio Processing Libraries**
- Integration with librosa for advanced audio analysis
- WebRTC VAD implementation
- Proper audio format handling (WAV, MP3, etc.)

#### 2. **Machine Learning Models**
- Voice emotion recognition model integration
- Speaker identification capabilities
- Language detection from voice patterns

#### 3. **Production-Ready Features**
- Audio compression and optimization
- Quality metrics and monitoring
- Error recovery and fallback mechanisms
- Rate limiting and resource management

#### 4. **Security & Authentication**
- JWT token validation for WebSocket connections
- User authorization for voice streams
- Audio data encryption in transit

#### 5. **Performance Optimization**
- Audio chunk caching
- Batch processing optimization
- GPU acceleration for ML models
- Memory management for long-running streams

### Immediate TODOs

1. **Implement Real VAD Algorithm**
   ```python
   # Priority: High
   # Replace mock VAD with actual voice activity detection
   import webrtcvad
   
   def detect_voice_activity(self, audio_data: bytes, sample_rate: int) -> bool:
       vad = webrtcvad.Vad(self.vad_sensitivity)
       return vad.is_speech(audio_data, sample_rate)
   ```

2. **Add Proper Audio Format Support**
   ```python
   # Priority: High  
   # Support multiple audio formats and proper conversion
   import soundfile as sf
   import librosa
   
   def process_audio_format(self, audio_data: bytes) -> np.ndarray:
       # Convert various audio formats to consistent format
       pass
   ```

3. **Integrate Emotion Recognition Model**
   ```python
   # Priority: Medium
   # Replace mock emotion analysis with actual model
   from transformers import pipeline
   
   emotion_classifier = pipeline("audio-classification", 
                               model="speechbrain/emotion-recognition-wav2vec2-IEMOCAP")
   ```

4. **Add Authentication & Security**
   ```python
   # Priority: Medium
   # Add JWT validation for WebSocket connections
   @app.websocket("/ws/voice/{client_id}")
   async def websocket_voice_stream(
       websocket: WebSocket, 
       client_id: str,
       token: str = Depends(get_current_user)
   ):
   ```

---

## 🌟 Future Development Plans

### Short-term Enhancements (1-3 months)

#### 1. **Real Audio Processing Integration**
- **WebRTC VAD**: Replace mock VAD with actual voice activity detection
- **Audio Format Support**: Handle multiple audio formats (WAV, MP3, FLAC, etc.)
- **Quality Assessment**: Real-time audio quality metrics and noise detection
- **Compression**: Implement audio compression for efficient streaming

#### 2. **Machine Learning Model Integration**
- **Emotion Recognition**: Deploy SpeechBrain emotion recognition models
- **Language Detection**: Automatic language detection from voice patterns
- **Speaker Identification**: Voice biometric identification capabilities
- **Sentiment Analysis**: Voice-based sentiment detection

#### 3. **Performance & Scalability**
- **GPU Acceleration**: Utilize CUDA for ML model inference
- **Batch Processing**: Optimize chunk processing with batching
- **Caching Layer**: Redis-based caching for processed audio segments
- **Load Balancing**: Support horizontal scaling with multiple instances

### Medium-term Features (3-6 months)

#### 1. **Advanced Voice Analytics**
- **Stress Detection**: Real-time stress level monitoring from voice patterns
- **Mood Tracking**: Long-term mood pattern analysis from voice interactions
- **Health Indicators**: Voice-based health status indicators
- **Behavioral Analysis**: Voice pattern changes for behavioral insights

#### 2. **Enhanced Multi-language Support**
- **Code-Switching Detection**: Handle mixed-language conversations
- **Accent Recognition**: Identify and adapt to regional accents
- **Cultural Speech Patterns**: Advanced cultural context analysis
- **Pronunciation Assessment**: Voice coaching and feedback

#### 3. **Integration Enhancements**
- **Real-time Translation**: Voice-to-voice translation pipeline
- **Voice Synthesis**: Integration with TTS for complete voice loops
- **Wearable Integration**: Connect with physiological data from devices
- **Mobile Optimization**: Optimized processing for mobile voice streams

### Long-term Vision (6+ months)

#### 1. **AI-Powered Voice Coaching**
- **Therapeutic Voice Exercises**: Guided voice-based mental health exercises
- **Breathing Analysis**: Respiratory pattern analysis from voice
- **Meditation Guidance**: Voice-guided meditation with real-time feedback
- **Progress Tracking**: Long-term voice therapy progress monitoring

#### 2. **Advanced Machine Learning**
- **Personalized Models**: User-specific emotion and behavior models
- **Federated Learning**: Privacy-preserving model updates across users
- **Continuous Learning**: Models that improve with user interactions
- **Multimodal Integration**: Combine voice with facial expressions and gestures

#### 3. **Research & Innovation**
- **Voice Biomarkers**: Research voice patterns for mental health indicators
- **Predictive Analytics**: Early warning systems for mental health episodes
- **Clinical Integration**: Integration with healthcare systems and providers
- **Privacy-First Analytics**: Advanced privacy-preserving voice analysis

### Technical Roadmap

#### Phase 1: Foundation (Months 1-2)
```python
# Real audio processing
├── WebRTC VAD integration
├── Audio format standardization
├── Quality assessment metrics
└── Basic ML model deployment

# Performance optimization
├── Async processing improvements
├── Memory management
├── Connection pooling
└── Error handling enhancement
```

#### Phase 2: Intelligence (Months 3-4)
```python
# ML model integration
├── Emotion recognition deployment
├── Language detection
├── Speaker identification
└── Cultural context analysis

# Advanced analytics
├── Stress detection algorithms
├── Mood pattern analysis
├── Health indicator extraction
└── Behavioral change detection
```

#### Phase 3: Scale & Integration (Months 5-6)
```python
# Scalability
├── Horizontal scaling support
├── Load balancing
├── Distributed processing
└── High availability setup

# Service integration
├── Real-time translation pipeline
├── Voice synthesis integration
├── Wearable device connectivity
└── Mobile optimization
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker and Docker Compose
- Audio processing libraries (for full functionality)

### Basic Setup (Minimal Dependencies)

1. **Clone and Navigate**
   ```bash
   cd /home/sachin/mantrapath/backend/services/voice_event_processor
   ```

2. **Install Minimal Dependencies**
   ```bash
   pip install -r requirements.min.txt
   ```

3. **Run Basic Version**
   ```bash
   python main.py
   ```

4. **Test WebSocket Connection**
   ```javascript
   const ws = new WebSocket('ws://localhost:8015/ws/voice/test_client');
   ws.onopen = () => console.log('Connected to voice processor');
   ws.send(JSON.stringify({"type": "start_stream"}));
   ```

### Enhanced Setup (Full Features)

1. **Install Full Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Enhanced Version**
   ```bash
   python main_enhanced.py
   ```

3. **Docker Deployment**
   ```bash
   # From backend directory
   docker-compose up -d voice-event-processor
   ```

### Testing the Service

1. **Health Check**
   ```bash
   curl http://localhost:8015/health
   ```

2. **Stream Status**
   ```bash
   curl http://localhost:8015/api/v1/streams/status
   ```

3. **WebSocket Test** (JavaScript)
   ```javascript
   const ws = new WebSocket('ws://localhost:8015/ws/voice/user123');
   
   ws.onmessage = (event) => {
       const data = JSON.parse(event.data);
       console.log('Voice event:', data);
   };
   
   // Start streaming
   ws.send(JSON.stringify({"type": "start_stream"}));
   
   // Send mock audio data
   ws.send(JSON.stringify({
       "type": "audio_chunk", 
       "data": "mock_audio_data"
   }));
   ```

---

## 🧪 Testing

### Running Tests

The service is covered by integration tests in the MantraPath test suite:

```bash
# Run voice event processor tests
cd /home/sachin/mantrapath/backend
python -m pytest tests/integration/sprint2/test_sprint2_integration.py::TestSprint2Services::test_voice_event_processor_health -v
```

### Test Coverage

#### Integration Tests (Existing)
- **Health endpoint validation**
- **Service availability checks**
- **Basic API response validation**

#### Unit Tests (Needed)
```python
# TODO: Add comprehensive unit tests
# Test categories needed:

# Connection Management Tests
├── WebSocket connection handling
├── Multiple client management  
├── Connection cleanup
└── Error scenarios

# Voice Processing Tests  
├── Audio chunk processing
├── VAD algorithm testing
├── Emotion analysis validation
└── Event generation

# Service Integration Tests
├── NATS event publishing
├── HTTP service communication
├── Error handling and retries
└── Timeout management
```

### Manual Testing Scripts

#### WebSocket Test Client
```python
import asyncio
import websockets
import json

async def test_voice_stream():
    uri = "ws://localhost:8015/ws/voice/test_client"
    
    async with websockets.connect(uri) as websocket:
        # Start stream
        await websocket.send(json.dumps({"type": "start_stream"}))
        
        # Send mock audio chunks
        for i in range(10):
            await websocket.send(json.dumps({
                "type": "audio_chunk",
                "data": f"mock_audio_chunk_{i}"
            }))
            
            response = await websocket.recv()
            print(f"Response {i}: {response}")
            
        # Stop stream
        await websocket.send(json.dumps({"type": "stop_stream"}))

# Run test
asyncio.run(test_voice_stream())
```

#### API Test Script
```bash
#!/bin/bash
# Voice Event Processor API Tests

echo "=== Voice Event Processor API Tests ==="

# Test health endpoint
echo "Testing health endpoint..."
curl -s http://localhost:8015/health | jq .

# Test configuration endpoint  
echo "Testing configuration endpoint..."
curl -s http://localhost:8015/api/v1/config | jq .

# Test streams status
echo "Testing streams status..."
curl -s http://localhost:8015/api/v1/streams/status | jq .

# Test voice processing (mock data)
echo "Testing voice processing..."
curl -s -X POST http://localhost:8015/api/v1/voice/process \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "mock_audio", "config": {"vad_sensitivity": 0.7}}' | jq .

echo "=== Tests completed ==="
```

---

## 📊 Monitoring & Logging

### Logging Configuration

The service uses structured logging with configurable levels:

```python
# Logging setup
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
```

### Log Categories

#### 1. **Connection Events**
```python
logger.info(f"Client {client_id} connected")
logger.info(f"Client {client_id} disconnected")
logger.warning(f"Cannot publish to {subject}: not connected")
```

#### 2. **Processing Events**
```python
logger.info(f"Processed voice interaction {interaction_event.interaction_id}: {result.get('success')}")
logger.debug(f"Processed voice stream chunk: {result}")
logger.error(f"Voice processing error: {e}")
```

#### 3. **Service Integration**
```python
logger.info("NATS client connected (mock)")
logger.info("Voice event subscriptions established")
logger.error(f"STT processing error: {e}")
```

### Health Monitoring

#### Health Check Endpoints
```python
# Basic health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "voice_event_processor", 
        "version": "1.0.0",
        "active_connections": len(manager.active_connections),
        "active_streams": len([s for s in manager.voice_streams.values() if s.get("stream_active")])
    }
```

#### Docker Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://voice-event-processor:8015/health || exit 1
```

### Performance Metrics

#### Available Metrics
- **Active Connections**: Current WebSocket connections
- **Active Streams**: Number of processing voice streams  
- **Processing Time**: Time taken for voice event processing
- **Event Counts**: Number of events processed by type
- **Error Rates**: Failed processing attempts

#### Metrics Endpoint
```python
@app.get("/api/v1/stats")
async def get_stats():
    return {
        "service_uptime": "running",
        "total_connections": len(manager.active_connections),
        "active_streams": len([s for s in manager.voice_streams.values() if s.get("stream_active")]),
        "processed_events": 0,  # TODO: Implement actual tracking
        "detected_emotions": 0,  # TODO: Implement actual tracking  
        "voice_activity_events": 0  # TODO: Implement actual tracking
    }
```

### Monitoring Integration

The service integrates with the MantraPath monitoring ecosystem:

#### 1. **Service Registry**
- Registered in API Gateway service registry
- Automatic health check monitoring
- Service discovery and load balancing

#### 2. **Docker Compose Monitoring**
```yaml
voice-event-processor:
  # ... other config ...
  healthcheck:
    test: ["CMD", "curl", "-f", "http://voice-event-processor:8015/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 60s
```

#### 3. **Log Aggregation**
- Structured logging format for log aggregation
- Environment-based log level configuration
- Integration with centralized logging systems

---

## 📚 Additional Resources

### Related Documentation
- [Voice Service Documentation](../voice_service/README.md)
- [AI Event Processor Documentation](../ai_event_processor/README.md)
- [Voice Event Schemas](../../docs/architecture/voice_event_schemas.md)
- [Service Architecture Overview](../../docs/architecture/SERVICE_INVENTORY.md)

### API Documentation
- Interactive API docs: `http://localhost:8015/docs`
- OpenAPI specification: `http://localhost:8015/openapi.json`

### Contributing
1. Follow the existing code structure and patterns
2. Add comprehensive tests for new features
3. Update this documentation for any changes
4. Ensure proper error handling and logging
5. Maintain backward compatibility when possible

### Support
- **Development Team**: MantraPath Development Team
- **Repository**: [mantrapath-code/mantrapath](https://github.com/mantrapath-code/mantrapath)
- **Issues**: Use GitHub Issues for bug reports and feature requests

---

*Last Updated: September 27, 2025*
*Version: 2.0.0*
*Service Port: 8015*