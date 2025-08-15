# V3-BK-003 Quick Reference: NATS Event Bus Enhancement

## 🎯 Story Overview
**Enhance NATS setup for real-time voice and AI event processing**  
**Sprint 1 | 8 Points | Mid Dev 1 | 5 Days**

## 📋 Quick Checklist

### Day 1: Voice Foundation ✅
- [ ] Voice event schemas (`voice_events.py`)
- [ ] Audio metadata validation
- [ ] Voice feature extraction models
- [ ] Unit tests >90% coverage

### Day 2: AI Coordination ✅  
- [ ] AI processing events (`ai_events.py`)
- [ ] Cross-service intelligence sharing
- [ ] Performance optimizations
- [ ] Integration testing

### Day 3: Cultural Intelligence ✅
- [ ] Cultural context events (`cultural_events.py`)  
- [ ] Regional intelligence processing
- [ ] Service integrations
- [ ] Cultural validation

### Day 4: Performance Tuning ✅
- [ ] JetStream configuration
- [ ] Enhanced NATS client (`nats_event_bus.py`)
- [ ] Metrics collection (`event_metrics.py`)
- [ ] <100ms latency validation

### Day 5: Integration & Testing ✅
- [ ] End-to-end testing
- [ ] Documentation completion
- [ ] Performance validation
- [ ] Story handoff

## 🔧 Key Files to Create

```
backend/shared/
├── voice_events.py          # Voice activity & intent events
├── ai_events.py            # AI processing & intelligence events  
├── cultural_events.py      # Cultural context & regional events
├── nats_event_bus.py       # Enhanced NATS client with JetStream
└── event_metrics.py        # Performance monitoring & metrics
```

## 🎤 Voice Events Schema
```python
VoiceActivityEvent:
  - event_type: voice.activity_detected | speech_start | speech_end
  - audio_metadata: duration, sample_rate, channels, format
  - voice_features: volume_level, pitch, emotion_confidence
  - context: session_id, user_id, device_info
  - processing_time_ms, confidence_score

VoiceIntentEvent:
  - event_type: voice.intent_classified | confidence_low | ambiguous
  - intent_data: primary_intent, confidence, parameters, language
  - context: session_id, user_id, cultural_context
  - classification_model, processing_time_ms
```

## 🤖 AI Events Schema
```python
AIProcessingEvent:
  - event_type: ai.inference_requested | completed | failed
  - processing_data: model_name, input_hash, processing_time
  - context_data: user_context, cultural_context, session_context
  - resource_metadata: memory_usage, gpu_utilization, cpu_usage

CrossServiceIntelligenceEvent:
  - event_type: intelligence.context_shared | insight_generated
  - intelligence_data: source_service, insight_type, confidence
  - sharing_metadata: target_services, ttl, priority_level
```

## 🌍 Cultural Events Schema
```python
CulturalContextEvent:
  - event_type: cultural.context_detected | adaptation_applied
  - cultural_data: region, language, cultural_dimensions
  - adaptation_metadata: ui_adaptations, interaction_style
  - processing_info: detection_confidence, rules_applied

RegionalIntelligenceEvent:
  - event_type: regional.trend_detected | pattern_identified
  - regional_data: region_code, trend_type, pattern_strength
  - metadata: sample_size, statistical_confidence
```

## ⚡ NATS Configuration

### JetStream Streams
```yaml
voice_events:
  subjects: ["voice.>"]
  retention: workqueue
  max_age: 1h
  replicas: 3

ai_events:
  subjects: ["ai.>", "intelligence.>"]  
  retention: interest
  max_age: 24h
  replicas: 3

cultural_events:
  subjects: ["cultural.>", "regional.>"]
  retention: limits
  max_age: 1w
  replicas: 3
```

### Performance Targets
- **Latency**: <100ms event propagation
- **Throughput**: >10,000 events/second
- **Reliability**: >99.9% message delivery
- **CPU**: <70% under normal load
- **Memory**: <80% under normal load

## 🔌 Service Integration Example

```python
# In mood service
from shared.nats_event_bus import get_nats_event_bus

async def handle_voice_intent(event_data, event_type, subject):
    if event_data['intent_data']['primary_intent'] == 'log_mood':
        user_id = event_data['context']['user_id'] 
        mood_level = event_data['intent_data']['parameters']['mood_level']
        await create_mood_entry(user_id, mood_level)

# Subscribe to voice intents
event_bus = await get_nats_event_bus()
await event_bus.subscribe_to_events(
    subject="voice.intent_classified",
    handler=handle_voice_intent,
    durable_name="mood_service_voice"
)
```

## 📊 Monitoring Setup

### Prometheus Metrics
- `nats_events_published_total{event_type, subject}`
- `nats_events_consumed_total{event_type, subject}`  
- `nats_event_processing_duration_seconds{event_type}`
- `nats_event_size_bytes{event_type}`

### Grafana Dashboards
- Event throughput by type
- Processing latency percentiles  
- Error rates and failures
- Resource utilization

## 🧪 Testing Strategy

### Unit Tests
```bash
# Voice events
pytest backend/tests/test_voice_events.py -v

# AI events  
pytest backend/tests/test_ai_events.py -v

# Cultural events
pytest backend/tests/test_cultural_events.py -v

# NATS client
pytest backend/tests/test_nats_event_bus.py -v
```

### Performance Tests
```bash
# Latency benchmark
python -m pytest backend/tests/perf_test_latency.py

# Throughput test
python -m pytest backend/tests/perf_test_throughput.py

# Load test
python -m pytest backend/tests/load_test_concurrent.py
```

## 🚨 Acceptance Criteria

### ✅ Voice activity event streaming
**Test**: Voice events flow with <100ms latency  
**Validation**: Load test with 1000+ voice events/sec

### ✅ AI processing event coordination  
**Test**: AI services coordinate through events  
**Validation**: Cross-service intelligence sharing <50ms

### ✅ Cultural intelligence event processing
**Test**: Cultural events with regional context  
**Validation**: Cultural adaptation <200ms latency

### ✅ Real-time cross-service intelligence sharing
**Test**: Intelligence events shared real-time  
**Validation**: All services receive intelligence <100ms

## 🔗 Dependencies

### Before Starting
- [ ] NATS 2.10+ server running
- [ ] Python nats-py library installed
- [ ] Prometheus metrics endpoint available
- [ ] Redis cache available (optional)

### Blocking Dependencies
- Voice service requirements definition
- AI model serving endpoints
- Cultural intelligence models

### Unblocks for Next Stories
- V3-BK-004: Service Event Integration
- V3-BK-005: AI Event Processing Pipeline  
- V3-BK-006: Voice Event Streaming Foundation

## ⚠️ Common Gotchas

1. **JetStream Setup**: Ensure JetStream is enabled in NATS config
2. **Event Ordering**: Use stream sequence numbers for ordering guarantees
3. **Schema Evolution**: Plan for backward-compatible schema changes
4. **Memory Usage**: Monitor event payload sizes for large AI contexts
5. **Error Handling**: Implement circuit breakers for failing consumers

## 📞 Who to Contact

- **NATS Issues**: DevOps Team (NATS infrastructure)
- **Voice Requirements**: Voice Processing Team  
- **AI Coordination**: AI/ML Team
- **Cultural Intelligence**: Localization Team
- **Performance Issues**: Platform Team

## 🏁 Definition of Done

- [ ] All acceptance criteria validated
- [ ] Unit tests >90% coverage passing
- [ ] Integration tests passing
- [ ] Performance targets met (<100ms latency)
- [ ] Documentation complete
- [ ] Code review approved
- [ ] Monitoring dashboards operational
- [ ] Demo completed for stakeholders

---

*This quick reference should be bookmarked by the development team for easy access during implementation.*
