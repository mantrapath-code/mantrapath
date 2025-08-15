# Voice Event Schemas Documentation

## Overview

The Voice Event Schemas provide comprehensive support for real-time voice interactions, emotion detection, and intent classification with full multilingual capabilities.

## Event Types

### VoiceActivityEvent

Captures voice activity detection events including speech start/end, quality metrics, and environmental context.

#### Schema

```python
class VoiceActivityEvent(BaseModel):
    event_type: VoiceEventType
    timestamp: datetime
    event_id: str
    audio_metadata: AudioMetadata
    voice_features: VoiceFeatures
    context: VoiceContext
    processing_time_ms: Optional[int]
    confidence_score: float
    audio_chunk_id: Optional[str]
```

#### Example

```python
from shared.events.voice_events import create_voice_activity_event, VoiceEventType
from shared.events.voice_events import DeviceInfo

# Create device info
device = DeviceInfo(
    device_id="mic-001",
    device_type="microphone",
    manufacturer="Apple"
)

# Create voice activity event
event = create_voice_activity_event(
    event_type=VoiceEventType.SPEECH_START,
    audio_duration_ms=1500,
    volume_level=0.7,
    pitch_frequency=150.0,
    device_info=device,
    user_id="user123"
)
```

### VoiceIntentEvent

Captures intent classification results with multilingual support and cultural context.

#### Schema

```python
class VoiceIntentEvent(BaseModel):
    event_type: VoiceIntentType
    timestamp: datetime
    event_id: str
    intent_data: IntentData
    processing_metadata: ProcessingMetadata
    voice_activity_event_id: Optional[str]
    context: VoiceContext
    transcription_quality: Optional[float]
    raw_transcription: Optional[str]
    processed_text: Optional[str]
```

#### Example

```python
from shared.events.voice_events import create_voice_intent_event, VoiceIntentType

# Create intent event
event = create_voice_intent_event(
    event_type=VoiceIntentType.INTENT_CLASSIFIED,
    primary_intent="meditation_request",
    confidence_score=0.95,
    language_detected="en",
    classification_model="intent-classifier-v2",
    processing_time_ms=250,
    device_info=device,
    user_id="user123"
)
```

## Multilingual Support

### Supported Languages

The voice event system supports the following languages:

- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Chinese (zh)
- Japanese (ja)
- Korean (ko)
- Arabic (ar)
- Hindi (hi)
- Thai (th)
- Vietnamese (vi)
- Turkish (tr)
- Polish (pl)
- Dutch (nl)
- Swedish (sv)
- Danish (da)
- Norwegian (no)

### Cultural Context

Each voice event includes cultural context that adapts the processing based on:

- Communication style (formal, casual, respectful)
- Cultural dimensions (power distance, individualism, etc.)
- Regional preferences
- Language-specific patterns

#### Example Cultural Adaptation

```python
from shared.events.voice_events import get_cultural_context_for_language

# Get cultural context for Japanese
context = get_cultural_context_for_language("ja")
# Returns: {"formality": "high", "directness": "low", "context": "high"}

# Get cultural context for German
context = get_cultural_context_for_language("de")
# Returns: {"formality": "medium", "directness": "high", "context": "low"}
```

## Audio Processing

### Audio Metadata

The system captures comprehensive audio metadata:

```python
class AudioMetadata(BaseModel):
    duration_ms: int  # Duration in milliseconds
    sample_rate: int = 16000  # Default 16kHz
    channels: int = 1  # Mono by default
    format: str = "wav"  # Audio format
    bitrate: Optional[int]  # Bitrate if available
    encoding: str = "pcm_s16le"  # Audio encoding
```

### Voice Features

Advanced voice feature extraction:

```python
class VoiceFeatures(BaseModel):
    volume_level: float  # 0.0 to 1.0
    pitch_frequency: float  # Hz
    emotion_confidence: Dict[str, float]  # Emotion scores
    speech_rate: Optional[float]  # Words per minute
    pause_duration: Optional[float]  # Pause duration
    energy_level: Optional[float]  # Voice energy
    accent_confidence: Optional[Dict[str, float]]  # Accent detection
    cultural_markers: Optional[Dict[str, Any]]  # Cultural patterns
```

## Intent Classification

### Intent Data

Comprehensive intent classification results:

```python
class IntentData(BaseModel):
    primary_intent: str  # Main classified intent
    confidence_score: float  # 0.0 to 1.0
    parameters: Dict[str, Any]  # Extracted parameters
    language_detected: str  # ISO 639-1 language code
    language_confidence: float  # Language detection confidence
    alternative_intents: List[Dict[str, Any]]  # Alternative interpretations
    cultural_adaptations: Optional[Dict[str, Any]]  # Cultural adaptations
```

### Processing Metadata

Details about the processing pipeline:

```python
class ProcessingMetadata(BaseModel):
    classification_model: str  # Model used
    model_version: str  # Model version
    processing_time_ms: int  # Processing time
    cultural_context_applied: bool  # Cultural context used
    cultural_rules_applied: List[str]  # Applied rules
    multimodal_inputs: Optional[List[str]]  # Additional inputs
    fallback_used: bool  # Fallback processing
    warning_messages: List[str]  # Warnings
```

## Event Publishing

### Using Enhanced Event Bus

```python
from shared.events.enhanced_bus import publish_voice_activity_event

# Publish voice activity event
success = await publish_voice_activity_event(
    activity_type="speech_start",
    audio_data={
        "duration_ms": 1500,
        "volume_level": 0.7,
        "pitch_frequency": 150.0,
        "quality_score": 0.9
    },
    user_id="user123"
)
```

### Using Direct Event Creation

```python
from shared.events.enhanced_bus import get_enhanced_event_bus
from shared.events.voice_events import VoiceEventType

bus = get_enhanced_event_bus()

# Create and publish event
await bus.publish(
    channel=VoiceEventType.SPEECH_START,
    data={
        "audio_metadata": {...},
        "voice_features": {...},
        "context": {...}
    },
    user_id="user123"
)
```

## Event Subscription

### Subscribe to Voice Events

```python
from shared.events.enhanced_bus import get_enhanced_event_bus
from shared.events.voice_events import VoiceEventType

bus = get_enhanced_event_bus()

async def handle_speech_start(event):
    print(f"Speech started: {event.data}")
    # Process speech start event

# Subscribe to speech start events
await bus.subscribe(
    channel=VoiceEventType.SPEECH_START,
    handler=handle_speech_start
)
```

### Pattern-Based Subscription

```python
# Subscribe to all voice events
async def handle_voice_event(event):
    print(f"Voice event: {event.channel}")

await bus.subscribe("voice.*", handle_voice_event)
```

## Validation

### Event Validation

All voice events are automatically validated against their schemas:

```python
from shared.events.voice_events import validate_voice_event_schema

# Validate event data
is_valid = validate_voice_event_schema(
    event_data={"event_type": "voice.speech_start", ...},
    event_type="voice.speech_start"
)
```

### Custom Validation

Add custom validation rules:

```python
def custom_voice_validator(event_data: Dict[str, Any]) -> bool:
    # Custom validation logic
    return event_data.get("volume_level", 0) > 0.1

# Register validator with enhanced bus
bus = get_enhanced_event_bus()
bus.event_validators["voice."] = custom_voice_validator
```

## Performance Considerations

### Latency Optimization

- Voice events are prioritized for sub-100ms processing
- Audio chunks are referenced by ID to reduce payload size
- Compression is applied to large audio metadata

### Memory Management

- Audio data is stored separately from events
- Event history is automatically pruned
- Emotion confidence scores are normalized to prevent memory bloat

### Scalability

- Events can be processed by multiple consumers
- NATS JetStream provides replay capabilities
- Horizontal scaling through service instances

## Error Handling

### Common Error Scenarios

1. **Audio Quality Issues**: Low signal-to-noise ratio
2. **Language Detection Failures**: Unknown or mixed languages
3. **Intent Classification Ambiguity**: Low confidence scores
4. **Cultural Context Missing**: Fallback to default rules

### Error Recovery

```python
# Example error handling
try:
    event = create_voice_activity_event(...)
except ValidationError as e:
    logger.error(f"Voice event validation failed: {e}")
    # Apply fallback or retry logic
```

## Integration Examples

### With Mood Service

```python
# Subscribe to voice emotion events in mood service
async def process_voice_emotion(event):
    if "emotion_confidence" in event.data:
        emotions = event.data["emotion_confidence"]
        # Update user mood based on voice emotions
        await update_mood_from_voice(event.user_id, emotions)

await bus.subscribe("voice.activity_detected", process_voice_emotion)
```

### With AI Service

```python
# Subscribe to intent events in AI service
async def process_voice_intent(event):
    intent_data = event.data.get("intent_data", {})
    if intent_data.get("primary_intent") == "meditation_request":
        # Trigger meditation recommendation AI
        await generate_meditation_recommendation(event.user_id, intent_data)

await bus.subscribe("voice.intent_classified", process_voice_intent)
```

## Testing

### Unit Tests

```python
import pytest
from shared.events.voice_events import VoiceActivityEvent, VoiceEventType

def test_voice_activity_event_creation():
    event_data = {
        "event_type": VoiceEventType.SPEECH_START,
        "audio_metadata": {...},
        "voice_features": {...},
        "context": {...}
    }
    
    event = VoiceActivityEvent(**event_data)
    assert event.event_type == VoiceEventType.SPEECH_START
    assert event.event_id is not None
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_voice_event_publishing():
    bus = get_enhanced_event_bus()
    
    success = await publish_voice_activity_event(
        activity_type="speech_start",
        audio_data={"duration_ms": 1000, "volume_level": 0.5},
        user_id="test_user"
    )
    
    assert success == True
```

## Best Practices

1. **Always include user context** for personalization
2. **Use appropriate confidence thresholds** for decision making
3. **Handle multiple languages gracefully** with fallbacks
4. **Monitor event latency** to ensure real-time performance
5. **Validate cultural adaptations** for appropriateness
6. **Log processing warnings** for debugging
7. **Use event correlation IDs** for tracing across services
