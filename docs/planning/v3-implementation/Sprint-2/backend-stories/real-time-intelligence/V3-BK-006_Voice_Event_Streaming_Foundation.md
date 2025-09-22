# Story V3-BK-006: Voice Event Streaming Foundation
**Epic**: Real-Time AI Event Processing  
**Priority**: P0 | **Points**: 10 | **Assignee**: Senior Dev 2

## Story Description
Establish a comprehensive foundation for voice event processing including voice activity detection events, voice emotion analysis event processing, speech-to-text event coordination, and voice command event routing.

## Current State Analysis

### Existing Infrastructure
- ✅ Voice service with Whisper integration
- ✅ Voice event schemas in `shared/events/voice_events.py`
- ✅ Enhanced event bus with NATS support
- ✅ API Gateway with voice routing capabilities

### Current Gaps
- ❌ No voice activity detection event streaming
- ❌ Voice emotion analysis not integrated with events
- ❌ No speech-to-text event coordination
- ❌ Voice commands not triggering cross-service events

## Acceptance Criteria

### 🎯 Primary Acceptance Criteria
- [ ] **Voice activity detection events** streaming in real-time with <50ms latency
- [ ] **Voice emotion analysis event processing** integrated with AI pipeline
- [ ] **Speech-to-text event coordination** with translation and language detection
- [ ] **Voice command event routing** to appropriate services and actions

### 🔍 Technical Acceptance Criteria
- [ ] Voice event processing latency <50ms for 95% of events
- [ ] Support for 25+ languages in voice processing
- [ ] Voice activity detection accuracy >95%
- [ ] Emotion analysis from voice with >85% accuracy
- [ ] Real-time voice streaming with <100ms end-to-end latency

### 📊 Performance Acceptance Criteria
- [ ] Handle 100+ concurrent voice streams
- [ ] Voice processing memory usage <1GB per stream
- [ ] CPU utilization <80% under normal voice load
- [ ] Voice command recognition accuracy >90%

## Detailed Implementation Plan

### Task 1: Voice Event Schema Design (2h)
**Objective**: Design comprehensive voice event schemas and validation

#### Implementation Steps
1. **Extend Voice Event Schemas**
   ```python
   # File: backend/shared/events/voice_events.py
   class VoiceActivityEvent(BaseModel):
       event_type: VoiceEventType = VoiceEventType.ACTIVITY_DETECTED
       user_id: str
       session_id: str
       activity_type: VoiceActivityType  # speaking, silence, noise
       confidence: float = Field(ge=0.0, le=1.0)
       audio_level: float
       duration_ms: int
       timestamp: datetime
       language_hint: Optional[str] = None
       
   class VoiceEmotionEvent(BaseModel):
       event_type: VoiceEventType = VoiceEventType.EMOTION_DETECTED
       user_id: str
       session_id: str
       emotions: Dict[str, float]  # emotion -> confidence mapping
       dominant_emotion: str
       confidence: float
       audio_segment_id: str
       timestamp: datetime
   ```

2. **Voice Command Event Schema**
   ```python
   class VoiceCommandEvent(BaseModel):
       event_type: VoiceEventType = VoiceEventType.COMMAND_DETECTED
       user_id: str
       session_id: str
       command_text: str
       intent: str
       parameters: Dict[str, Any]
       confidence: float
       language: str
       cultural_context: Optional[Dict[str, Any]]
       timestamp: datetime
   ```

3. **Speech-to-Text Coordination Events**
   ```python
   class STTEvent(BaseModel):
       event_type: VoiceEventType = VoiceEventType.STT_PROCESSED
       user_id: str
       session_id: str
       original_audio_id: str
       transcribed_text: str
       language_detected: str
       confidence: float
       processing_time_ms: int
       timestamp: datetime
   ```

#### Deliverables
- Enhanced voice event schemas
- Event validation and serialization
- Event schema documentation

### Task 2: Voice Activity Event Processing (3h)
**Objective**: Implement real-time voice activity detection and event streaming

#### Implementation Steps
1. **Voice Activity Detection (VAD) Integration**
   ```python
   # File: backend/services/voice_service/src/vad_processor.py
   class VoiceActivityDetector:
       def __init__(self):
           self.vad_model = webrtcvad.Vad(3)  # Aggressiveness level
           self.event_bus = get_enhanced_event_bus()
           
       async def process_audio_stream(self, audio_stream, user_id: str, session_id: str):
           for audio_chunk in audio_stream:
               is_speech = self.vad_model.is_speech(audio_chunk.raw_data, 16000)
               
               if is_speech:
                   await self.publish_activity_event(
                       user_id, session_id, VoiceActivityType.SPEAKING,
                       confidence=0.95, audio_level=audio_chunk.level
                   )
   ```

2. **Real-Time Activity Streaming**
   ```python
   class VoiceStreamProcessor:
       async def start_voice_session(self, user_id: str) -> str:
           session_id = str(uuid.uuid4())
           
           # Initialize VAD for this session
           vad = VoiceActivityDetector()
           
           # Start activity detection stream
           await self.event_bus.publish(
               V3VoiceChannels.SESSION_STARTED,
               {"user_id": user_id, "session_id": session_id}
           )
           
           return session_id
   ```

3. **Audio Level and Quality Monitoring**
   ```python
   class AudioQualityMonitor:
       def analyze_audio_quality(self, audio_chunk):
           return {
               "audio_level": self.calculate_rms(audio_chunk),
               "noise_level": self.detect_noise(audio_chunk),
               "quality_score": self.assess_quality(audio_chunk)
           }
   ```

#### Deliverables
- Voice activity detection implementation
- Real-time activity event streaming
- Audio quality monitoring

### Task 3: Voice Emotion Event Handling (3h)
**Objective**: Integrate voice emotion analysis with event processing pipeline

#### Implementation Steps
1. **Voice Emotion Analysis Service**
   ```python
   # File: backend/services/voice_service/src/emotion_analyzer.py
   class VoiceEmotionAnalyzer:
       def __init__(self):
           self.emotion_model = self.load_voice_emotion_model()
           self.event_bus = get_enhanced_event_bus()
           
       async def analyze_voice_emotion(self, audio_segment, user_id: str, session_id: str):
           # Extract emotion features from audio
           emotion_features = self.extract_features(audio_segment)
           
           # Predict emotions
           emotions = self.emotion_model.predict(emotion_features)
           
           # Publish emotion event
           await self.publish_emotion_event(user_id, session_id, emotions)
   ```

2. **Emotion Event Processing Pipeline**
   ```python
   @voice_processor.subscribe(V3VoiceChannels.AUDIO_SEGMENT_READY)
   async def process_voice_emotion(event: Event):
       audio_data = event.data
       
       # Analyze emotion from voice
       emotion_result = await emotion_analyzer.analyze_voice_emotion(
           audio_data["audio_segment"],
           event.user_id,
           audio_data["session_id"]
       )
       
       # Publish to AI event processing pipeline
       await event_bus.publish(
           V3AIChannels.EMOTION_DETECTED,
           emotion_result,
           event.user_id
       )
   ```

3. **Cross-Modal Emotion Correlation**
   ```python
   class CrossModalEmotionProcessor:
       async def correlate_voice_text_emotion(self, voice_emotion, text_emotion):
           # Combine voice and text emotion analysis
           # Resolve conflicts and improve accuracy
           # Return unified emotion assessment
   ```

#### Deliverables
- Voice emotion analysis integration
- Emotion event processing pipeline
- Cross-modal emotion correlation

### Task 4: Voice Command Routing (2h)
**Objective**: Implement voice command detection and routing to appropriate services

#### Implementation Steps
1. **Voice Command Detection**
   ```python
   class VoiceCommandDetector:
       def __init__(self):
           self.intent_classifier = IntentClassifier()
           self.parameter_extractor = ParameterExtractor()
           
       async def detect_command(self, transcribed_text: str, language: str, user_context: dict):
           # Classify intent
           intent = await self.intent_classifier.classify(transcribed_text, language)
           
           # Extract parameters
           parameters = await self.parameter_extractor.extract(transcribed_text, intent)
           
           # Create command event
           return VoiceCommandEvent(
               command_text=transcribed_text,
               intent=intent.name,
               parameters=parameters,
               confidence=intent.confidence,
               language=language
           )
   ```

2. **Command Routing Logic**
   ```python
   @voice_processor.subscribe(V3VoiceChannels.STT_COMPLETED)
   async def route_voice_command(event: Event):
       stt_data = event.data
       
       # Detect if this is a command
       if self.is_command(stt_data["transcribed_text"]):
           command_event = await command_detector.detect_command(
               stt_data["transcribed_text"],
               stt_data["language"],
               stt_data["user_context"]
           )
           
           # Route to appropriate service
           await self.route_command(command_event)
   ```

3. **Service-Specific Command Handlers**
   ```python
   class VoiceCommandRouter:
       def __init__(self):
           self.service_routes = {
               "mood_tracking": MoodServiceHandler(),
               "journal_entry": JournalServiceHandler(),
               "chat_response": ChatbotServiceHandler(),
               "translation": TranslationServiceHandler()
           }
       
       async def route_command(self, command_event: VoiceCommandEvent):
           handler = self.service_routes.get(command_event.intent)
           if handler:
               await handler.handle_voice_command(command_event)
   ```

#### Deliverables
- Voice command detection system
- Command routing implementation
- Service-specific command handlers

### Task 5: Testing and Validation (2h)
**Objective**: Comprehensive testing of voice event processing pipeline

#### Implementation Steps
1. **Voice Event Processing Tests**
   ```python
   class TestVoiceEventProcessing:
       async def test_activity_detection_events(self):
           # Test VAD event publishing
           # Verify event schema compliance
           # Check processing latency
           
       async def test_emotion_analysis_pipeline(self):
           # Test voice emotion detection
           # Verify emotion event publishing
           # Check emotion accuracy
           
       async def test_command_routing(self):
           # Test voice command detection
           # Verify command routing
           # Check service integration
   ```

2. **Performance Testing**
   ```python
   class VoicePerformanceTests:
       async def test_concurrent_voice_streams(self):
           # Test 100+ concurrent voice streams
           # Measure latency and throughput
           # Check resource usage
           
       async def test_voice_processing_latency(self):
           # Measure end-to-end voice processing latency
           # Target <50ms for activity detection
           # Target <100ms for emotion analysis
   ```

3. **Integration Testing**
   ```python
   class VoiceIntegrationTests:
       async def test_voice_to_ai_pipeline(self):
           # Test voice events triggering AI processing
           # Verify cross-service integration
           # Check data flow integrity
   ```

#### Deliverables
- Comprehensive test suite
- Performance benchmarks
- Integration validation

## Integration Points

### Service Dependencies
1. **Voice Service**: Audio processing and STT
2. **AI Event Processor**: Emotion and intent analysis
3. **Translation Service**: Language detection and translation
4. **Action Orchestrator**: Voice command execution
5. **API Gateway**: Voice routing and WebSocket management

### External Dependencies
1. **WebRTC VAD**: Voice activity detection
2. **Voice Emotion Models**: Audio emotion analysis
3. **NATS JetStream**: Voice event streaming
4. **Redis**: Voice session management

## Voice Event Channels Definition

```python
class V3VoiceChannels:
    """Voice-specific event channels"""
    # Activity Events
    ACTIVITY_DETECTED = "voice.activity_detected"
    SESSION_STARTED = "voice.session_started"
    SESSION_ENDED = "voice.session_ended"
    
    # Processing Events
    AUDIO_SEGMENT_READY = "voice.audio_segment_ready"
    STT_STARTED = "voice.stt_started"
    STT_COMPLETED = "voice.stt_completed"
    
    # Emotion Events
    EMOTION_DETECTED = "voice.emotion_detected"
    EMOTION_ANALYSIS_FAILED = "voice.emotion_analysis_failed"
    
    # Command Events
    COMMAND_DETECTED = "voice.command_detected"
    COMMAND_ROUTED = "voice.command_routed"
    COMMAND_EXECUTED = "voice.command_executed"
    
    # Quality Events
    AUDIO_QUALITY_LOW = "voice.audio_quality_low"
    PROCESSING_DELAYED = "voice.processing_delayed"
```

## Monitoring and Metrics

### Voice Processing Metrics
```python
voice_metrics = {
    "voice_activity_detection_latency": Histogram("voice_vad_latency_seconds"),
    "voice_emotion_analysis_duration": Histogram("voice_emotion_duration_seconds"),
    "voice_command_detection_accuracy": Gauge("voice_command_accuracy_ratio"),
    "concurrent_voice_sessions": Gauge("voice_concurrent_sessions"),
    "voice_processing_errors": Counter("voice_processing_errors_total"),
    "audio_quality_score": Histogram("voice_audio_quality_score")
}
```

### Health Checks
```python
class VoiceHealthChecker:
    async def check_voice_processing_health(self):
        return {
            "vad_status": await self.check_vad_service(),
            "emotion_model_status": await self.check_emotion_models(),
            "event_bus_status": await self.check_event_bus(),
            "processing_latency": await self.measure_processing_latency()
        }
```

## Risk Mitigation

### High-Priority Risks
1. **Voice Processing Latency**
   - Risk: Real-time requirements not met (<50ms)
   - Mitigation: Optimized audio processing, efficient models

2. **Audio Quality Issues**
   - Risk: Poor audio quality affects accuracy
   - Mitigation: Audio quality monitoring, adaptive processing

3. **Concurrent Stream Handling**
   - Risk: System overload with multiple voice streams
   - Mitigation: Stream prioritization, resource management

### Fallback Strategies
1. **VAD Failure**: Fall back to audio level detection
2. **Emotion Model Unavailable**: Skip emotion analysis, log event
3. **Command Detection Failure**: Fall back to text-based processing

## Definition of Done

### Technical Completion
- [ ] Voice activity detection streaming implemented
- [ ] Voice emotion analysis integrated with events
- [ ] Speech-to-text event coordination working
- [ ] Voice command routing functional
- [ ] All tests passing (>85% coverage)

### Performance Validation
- [ ] <50ms voice activity detection latency
- [ ] <100ms emotion analysis processing time
- [ ] 100+ concurrent voice streams supported
- [ ] >90% voice command recognition accuracy

### Integration Validation
- [ ] Voice events triggering AI processing pipeline
- [ ] Cross-service voice command execution
- [ ] Real-time voice event streaming stable
- [ ] Cultural adaptation working for voice

---

## Implementation Files Structure

```
backend/services/voice_service/
├── src/
│   ├── voice_events/
│   │   ├── activity_detector.py    # VAD implementation
│   │   ├── emotion_analyzer.py     # Voice emotion analysis
│   │   ├── command_detector.py     # Voice command detection
│   │   └── event_publisher.py      # Voice event publishing
│   ├── streaming/
│   │   ├── stream_processor.py     # Audio stream processing
│   │   ├── session_manager.py      # Voice session management
│   │   └── quality_monitor.py      # Audio quality monitoring
│   └── routing/
│       ├── command_router.py       # Voice command routing
│       └── service_handlers.py     # Service-specific handlers
└── tests/
    ├── voice_events/              # Voice event tests
    ├── streaming/                 # Streaming tests
    └── performance/               # Performance tests

backend/shared/events/
├── voice_events.py               # Enhanced voice event schemas
└── voice_channels.py            # Voice event channel definitions
```

This foundation enables real-time voice processing with comprehensive event streaming across all MantraPath services.
