"""
Voice Activity and Intent Event Schemas
Supporting real-time voice interactions, emotion detection, and intent classification.

Multilingual Support:
- All events support language detection and cultural context
- Text fields support UTF-8 encoding for international characters
- Cultural adaptation metadata included in all voice events
"""

from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
import uuid


class VoiceEventType(str, Enum):
    """Voice activity event types"""
    # Voice Activity Detection
    ACTIVITY_DETECTED = "voice.activity_detected"
    SPEECH_START = "voice.speech_start"
    SPEECH_END = "voice.speech_end"
    SILENCE_DETECTED = "voice.silence_detected"
    
    # Voice Quality
    QUALITY_HIGH = "voice.quality_high"
    QUALITY_DEGRADED = "voice.quality_degraded"
    QUALITY_RESTORED = "voice.quality_restored"


class VoiceIntentType(str, Enum):
    """Voice intent classification event types"""
    INTENT_CLASSIFIED = "voice.intent_classified"
    INTENT_CONFIDENCE_LOW = "voice.intent_confidence_low"
    INTENT_AMBIGUOUS = "voice.intent_ambiguous"
    INTENT_MULTIMODAL = "voice.intent_multimodal"  # Combined voice+gesture/visual
    
    # Cultural Intent Recognition
    CULTURAL_CONTEXT_DETECTED = "voice.cultural_context_detected"
    LANGUAGE_SWITCHED = "voice.language_switched"


class AudioMetadata(BaseModel):
    """Audio processing metadata"""
    duration_ms: int = Field(..., ge=0, description="Audio duration in milliseconds")
    sample_rate: int = Field(default=16000, ge=8000, le=48000, description="Audio sample rate")
    channels: int = Field(default=1, ge=1, le=2, description="Number of audio channels")
    format: str = Field(default="wav", description="Audio format (wav, mp3, etc.)")
    bitrate: Optional[int] = Field(None, ge=64, description="Audio bitrate")
    encoding: str = Field(default="pcm_s16le", description="Audio encoding")


class VoiceFeatures(BaseModel):
    """Voice feature extraction results"""
    volume_level: float = Field(..., ge=0.0, le=1.0, description="Normalized volume level")
    pitch_frequency: float = Field(..., ge=50.0, le=2000.0, description="Fundamental frequency in Hz")
    
    # Emotion Detection (Multilingual)
    emotion_confidence: Dict[str, float] = Field(
        default_factory=dict, 
        description="Emotion scores: joy, anger, sadness, fear, neutral, etc."
    )
    
    # Speech Characteristics
    speech_rate: Optional[float] = Field(None, ge=0.0, description="Words per minute")
    pause_duration: Optional[float] = Field(None, ge=0.0, description="Pause duration in seconds")
    energy_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Voice energy level")
    
    # Language and Cultural Markers
    accent_confidence: Optional[Dict[str, float]] = Field(
        default_factory=dict,
        description="Detected accent confidence scores"
    )
    cultural_markers: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Cultural speech patterns detected"
    )
    
    @validator('emotion_confidence', pre=True)
    def validate_emotion_scores(cls, v: Any) -> Dict[str, float]:
        """Ensure emotion scores sum to reasonable values"""
        if v and isinstance(v, dict):
            total = sum(v.values())
            if total > 1.1:  # Allow small tolerance
                # Normalize scores
                v = {k: score/total for k, score in v.items()}
        return v


class DeviceInfo(BaseModel):
    """Device information for voice capture"""
    device_id: str = Field(..., description="Unique device identifier")
    device_type: str = Field(default="microphone", description="Device type")
    manufacturer: Optional[str] = Field(None, description="Device manufacturer")
    model: Optional[str] = Field(None, description="Device model")
    os_version: Optional[str] = Field(None, description="Operating system version")
    app_version: Optional[str] = Field(None, description="Application version")


class VoiceContext(BaseModel):
    """Voice interaction context"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Voice session ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    device_info: DeviceInfo = Field(..., description="Device information")
    environment_noise_level: float = Field(
        default=0.0, ge=0.0, le=1.0, 
        description="Background noise level"
    )
    
    # Cultural and Linguistic Context
    preferred_language: Optional[str] = Field(None, description="User's preferred language (ISO 639-1)")
    cultural_region: Optional[str] = Field(None, description="Cultural region (ISO 3166-1)")
    timezone: Optional[str] = Field(None, description="User timezone")
    
    # Session Context
    conversation_turn: int = Field(default=1, ge=1, description="Turn number in conversation")
    interaction_mode: str = Field(default="voice_only", description="Interaction mode")


class VoiceActivityEvent(BaseModel):
    """Voice activity detection event"""
    
    # Core Event Data
    event_type: VoiceEventType = Field(..., description="Type of voice activity event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    
    # Audio and Voice Data
    audio_metadata: AudioMetadata = Field(..., description="Audio processing metadata")
    voice_features: VoiceFeatures = Field(..., description="Extracted voice features")
    context: VoiceContext = Field(..., description="Voice interaction context")
    
    # Processing Metadata
    processing_time_ms: Optional[int] = Field(None, ge=0, description="Processing time")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Detection confidence")
    
    # Raw audio data reference (not stored in event)
    audio_chunk_id: Optional[str] = Field(None, description="Reference to audio chunk in storage")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IntentData(BaseModel):
    """Intent classification results"""
    primary_intent: str = Field(..., description="Primary classified intent")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    
    # Intent Parameters (Multilingual)
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted intent parameters and entities"
    )
    
    # Language Processing
    language_detected: str = Field(..., description="Detected language (ISO 639-1)")
    language_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Language detection confidence")
    
    # Alternative Intents
    alternative_intents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Alternative intent interpretations"
    )
    
    # Cultural Context
    cultural_adaptations: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Cultural adaptations applied to intent"
    )


class ProcessingMetadata(BaseModel):
    """Intent processing metadata"""
    classification_model: str = Field(..., description="Model used for classification")
    model_version: str = Field(default="1.0", description="Model version")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")
    
    # Cultural Processing
    cultural_context_applied: bool = Field(default=False, description="Whether cultural context was applied")
    cultural_rules_applied: List[str] = Field(
        default_factory=list,
        description="List of cultural rules applied"
    )
    
    # Multimodal Processing
    multimodal_inputs: Optional[List[str]] = Field(
        default_factory=list,
        description="Additional input modalities used (gesture, visual, etc.)"
    )
    
    # Error Handling
    fallback_used: bool = Field(default=False, description="Whether fallback processing was used")
    warning_messages: List[str] = Field(
        default_factory=list,
        description="Processing warnings"
    )


class VoiceIntentEvent(BaseModel):
    """Voice intent classification event"""
    
    # Core Event Data
    event_type: VoiceIntentType = Field(..., description="Type of voice intent event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    
    # Intent Processing Results
    intent_data: IntentData = Field(..., description="Intent classification results")
    processing_metadata: ProcessingMetadata = Field(..., description="Processing metadata")
    
    # Context (reference to voice activity event)
    voice_activity_event_id: Optional[str] = Field(None, description="Related voice activity event")
    context: VoiceContext = Field(..., description="Voice interaction context")
    
    # Quality Metrics
    transcription_quality: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Quality of speech-to-text transcription"
    )
    
    # Original transcription (for debugging/logging)
    raw_transcription: Optional[str] = Field(None, description="Raw speech-to-text output")
    processed_text: Optional[str] = Field(None, description="Processed/normalized text")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    @validator('intent_data')
    def validate_intent_data(cls, v: IntentData) -> IntentData:
        """Validate intent classification data"""
        if v.confidence_score < 0.3:
            # Low confidence intent should be flagged
            pass
        return v


# Helper Functions for Event Creation

def create_voice_activity_event(
    event_type: VoiceEventType,
    audio_duration_ms: int,
    volume_level: float,
    pitch_frequency: float,
    device_info: DeviceInfo,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> VoiceActivityEvent:
    """Create a voice activity event with default values"""
    
    audio_metadata = AudioMetadata(duration_ms=audio_duration_ms)
    voice_features = VoiceFeatures(
        volume_level=volume_level,
        pitch_frequency=pitch_frequency
    )
    
    context = VoiceContext(
        device_info=device_info,
        user_id=user_id
    )
    
    if session_id:
        context.session_id = session_id
    
    return VoiceActivityEvent(
        event_type=event_type,
        audio_metadata=audio_metadata,
        voice_features=voice_features,
        context=context,
        **kwargs
    )


def create_voice_intent_event(
    event_type: VoiceIntentType,
    primary_intent: str,
    confidence_score: float,
    language_detected: str,
    classification_model: str,
    processing_time_ms: int,
    device_info: DeviceInfo,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> VoiceIntentEvent:
    """Create a voice intent event with default values"""
    
    intent_data = IntentData(
        primary_intent=primary_intent,
        confidence_score=confidence_score,
        language_detected=language_detected
    )
    
    processing_metadata = ProcessingMetadata(
        classification_model=classification_model,
        processing_time_ms=processing_time_ms
    )
    
    context = VoiceContext(
        device_info=device_info,
        user_id=user_id
    )
    
    if session_id:
        context.session_id = session_id
    
    return VoiceIntentEvent(
        event_type=event_type,
        intent_data=intent_data,
        processing_metadata=processing_metadata,
        context=context,
        **kwargs
    )


# Event Validation Functions

def validate_voice_event_schema(event_data: Dict[str, Any], event_type: str) -> bool:
    """Validate voice event data against schema"""
    try:
        if "voice.activity" in event_type:
            VoiceActivityEvent(**event_data)
        elif "voice.intent" in event_type:
            VoiceIntentEvent(**event_data)
        else:
            return False
        return True
    except Exception:
        return False


# Cultural and Multilingual Helpers

SUPPORTED_LANGUAGES = [
    "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", 
    "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no"
]

CULTURAL_REGIONS = [
    "US", "UK", "CA", "AU", "ES", "MX", "FR", "DE", "IT", "BR",
    "RU", "CN", "JP", "KR", "IN", "TH", "VN", "TR", "PL", "NL"
]

def get_cultural_context_for_language(language: str) -> Dict[str, Any]:
    """Get default cultural context for a language"""
    cultural_mappings = {
        "en": {"formality": "medium", "directness": "high", "context": "low"},
        "ja": {"formality": "high", "directness": "low", "context": "high"},
        "de": {"formality": "medium", "directness": "high", "context": "low"},
        "zh": {"formality": "high", "directness": "medium", "context": "high"},
        "es": {"formality": "medium", "directness": "medium", "context": "medium"},
        "fr": {"formality": "high", "directness": "medium", "context": "medium"},
        # Add more as needed
    }
    
    return cultural_mappings.get(language, {"formality": "medium", "directness": "medium", "context": "medium"})
