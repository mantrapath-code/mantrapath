"""
Voice Service Core Models
Pydantic models for request/response validation and data structures
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum

class AudioFormat(str, Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"
    WEBM = "webm"
    M4A = "m4a"

class VoiceEngine(str, Enum):
    """Available voice processing engines"""
    WHISPER = "whisper"
    GOOGLE_STT = "google_stt"
    AZURE_STT = "azure_stt"
    ELEVENLABS = "elevenlabs"
    GOOGLE_TTS = "google_tts"
    AZURE_TTS = "azure_tts"

class EmotionType(str, Enum):
    """Emotion categories for voice analysis"""
    CALM = "calm"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    STRESSED = "stressed"
    PEACEFUL = "peaceful"
    ANXIOUS = "anxious"

class CommandType(str, Enum):
    """Voice command types"""
    # Meditation Commands
    START_MEDITATION = "start_meditation"
    STOP_MEDITATION = "stop_meditation"
    PAUSE_MEDITATION = "pause_meditation"
    RESUME_MEDITATION = "resume_meditation"
    GUIDED_MEDITATION = "guided_meditation"
    
    # Audio Control Commands
    PLAY_MUSIC = "play_music"
    STOP_MUSIC = "stop_music"
    PAUSE_MUSIC = "pause_music"
    RESUME_MUSIC = "resume_music"
    NEXT_TRACK = "next_track"
    PREVIOUS_TRACK = "previous_track"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    VOLUME_CONTROL = "volume_control"
    MUTE = "mute"
    
    # Navigation Commands
    OPEN_MENU = "open_menu"
    GO_BACK = "go_back"
    GO_HOME = "go_home"
    NAVIGATE_HOME = "navigate_home"
    NAVIGATE_PROFILE = "navigate_profile"
    NAVIGATE_SETTINGS = "navigate_settings"
    SEARCH = "search"
    SEARCH_CONTENT = "search_content"
    SHOW_PROGRESS = "show_progress"
    
    # Profile Commands
    UPDATE_PROFILE = "update_profile"
    VIEW_PROFILE = "view_profile"
    SET_PREFERENCE = "set_preference"
    
    # Community Commands
    JOIN_SESSION = "join_session"
    LEAVE_SESSION = "leave_session"
    SHARE_PROGRESS = "share_progress"
    BOOKMARK_CONTENT = "bookmark_content"
    SHARE_CONTENT = "share_content"
    
    # System Commands
    HELP = "help"
    SETTINGS = "settings"
    LOGOUT = "logout"
    EXIT_APP = "exit_app"
    SHUTDOWN = "shutdown"
    CUSTOM = "custom"
    
    # General Categories (for backward compatibility)
    MEDITATION = "meditation"
    NAVIGATION = "navigation"
    AUDIO_CONTROL = "audio_control"
    PROFILE = "profile"
    COMMUNITY = "community"
    SYSTEM = "system"

class VoiceCommand(BaseModel):
    """Voice command processing model"""
    text: str = Field(..., description="Voice command text", min_length=1, max_length=1000)
    command_type: Optional[CommandType] = Field(None, description="Parsed command type")
    language: str = Field(default="en", description="Language code", pattern=r"^[a-z]{2}$")
    service: Optional[str] = Field(None, description="Target service name")
    action: Optional[str] = Field(None, description="Specific action to perform")
    confidence: Optional[float] = Field(None, description="Recognition confidence", ge=0.0, le=1.0)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Command parameters")
    user_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="User context data")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Command context data")

class TTSRequest(BaseModel):
    """Text-to-speech request model"""
    text: str = Field(..., description="Text to convert to speech", min_length=1, max_length=5000)
    language: str = Field(default="en", description="Language code", pattern=r"^[a-z]{2}$")
    voice: Optional[str] = Field(None, description="Voice ID or engine preference")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0, description="Voice pitch multiplier")
    format: AudioFormat = Field(default=AudioFormat.MP3, description="Output audio format")
    engine: Optional[VoiceEngine] = Field(None, description="Preferred TTS engine")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()

class STTRequest(BaseModel):
    """Speech-to-text request model"""
    language: str = Field(default="en", description="Expected language code", pattern=r"^[a-z]{2}$")
    model: str = Field(default="whisper", description="STT engine/model to use")
    enable_diarization: bool = Field(default=False, description="Enable speaker diarization")
    enable_punctuation: bool = Field(default=True, description="Enable automatic punctuation")
    translate_to_english: bool = Field(default=False, description="Translate result to English")
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum confidence threshold")
    enable_emotion_analysis: bool = Field(default=True, description="Include emotion analysis")

class AudioData(BaseModel):
    """Audio data representation"""
    data: bytes = Field(..., description="Raw audio data")
    format: AudioFormat = Field(..., description="Audio format")
    sample_rate: int = Field(default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    engine_used: Optional[str] = Field(None, description="Engine used for processing")

class EmotionAnalysis(BaseModel):
    """Voice emotion analysis result"""
    primary_emotion: EmotionType = Field(..., description="Primary detected emotion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    emotion_scores: Dict[EmotionType, float] = Field(..., description="Scores for all emotions")
    arousal: float = Field(..., ge=0.0, le=1.0, description="Arousal level (energy)")
    valence: float = Field(..., ge=0.0, le=1.0, description="Valence (positive/negative)")
    stress_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Detected stress level")

class WordTiming(BaseModel):
    """Word-level timing information"""
    word: str = Field(..., description="The spoken word")
    start_time: float = Field(..., ge=0.0, description="Start time in seconds")
    end_time: float = Field(..., ge=0.0, description="End time in seconds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Word confidence score")

class STTResult(BaseModel):
    """Speech-to-text processing result"""
    text: str = Field(..., description="Transcribed text")
    language: str = Field(..., description="Detected language")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    duration: float = Field(..., ge=0.0, description="Audio duration in seconds")
    word_timings: List[WordTiming] = Field(default_factory=list, description="Word-level timing")
    emotion_analysis: Optional[EmotionAnalysis] = Field(None, description="Emotion analysis results")
    translated_text: Optional[str] = Field(None, description="English translation if requested")

class VoicePreferences(BaseModel):
    """User voice preferences model"""
    user_id: str = Field(..., description="User identifier")
    preferred_voice: Optional[str] = Field(None, description="Preferred voice ID")
    preferred_language: str = Field(default="en", description="Preferred language code")
    speech_rate: float = Field(default=1.0, description="Speech rate multiplier", ge=0.5, le=2.0)
    speech_pitch: float = Field(default=1.0, description="Speech pitch multiplier", ge=0.5, le=2.0)
    volume: float = Field(default=1.0, description="Audio volume level", ge=0.0, le=1.0)
    auto_play: bool = Field(default=True, description="Auto-play TTS responses")
    noise_reduction: bool = Field(default=True, description="Enable noise reduction")
    echo_cancellation: bool = Field(default=True, description="Enable echo cancellation")
    voice_activation: bool = Field(default=False, description="Enable voice activation")
    wake_word: Optional[str] = Field(None, description="Custom wake word")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class VoiceProfile(BaseModel):
    """User voice profile model"""
    user_id: str = Field(..., description="User identifier")
    voice_id: str = Field(default_factory=lambda: f"voice_{uuid.uuid4().hex[:8]}", description="Unique voice ID")
    name: Optional[str] = Field(None, description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    preferred_language: str = Field(default="en", description="User's preferred language")
    voice_settings: Dict[str, Any] = Field(default_factory=dict, description="Voice processing settings")
    sample_count: int = Field(default=0, description="Number of voice samples")
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Voice profile quality")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Profile active status")

class VoiceCommandResult(BaseModel):
    """Voice command processing result"""
    understood: bool = Field(..., description="Whether command was understood")
    intent: Optional[str] = Field(None, description="Detected intent")
    target_service: Optional[str] = Field(None, description="Target service for routing")
    action: Optional[str] = Field(None, description="Specific action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Command understanding confidence")
    alternative_interpretations: List[Dict[str, Any]] = Field(default_factory=list, description="Alternative command interpretations")

class VoiceResponse(BaseModel):
    """Standard voice service response"""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data payload")
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    language: Optional[str] = Field(None, description="Response language")

class VoiceStreamChunk(BaseModel):
    """Real-time voice streaming chunk"""
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Chunk identifier")
    sequence: int = Field(..., description="Chunk sequence number")
    audio_data: Optional[bytes] = Field(None, description="Audio data chunk")
    text_partial: Optional[str] = Field(None, description="Partial transcription")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Chunk timestamp")
    confidence: Optional[float] = Field(None, description="Partial confidence score")

class ServiceIntegration(BaseModel):
    """Service integration configuration"""
    service_name: str = Field(..., description="Target service name")
    supported_commands: List[str] = Field(..., description="Supported voice commands")
    description: str = Field(..., description="Service description")
    endpoint_url: Optional[str] = Field(None, description="Service endpoint URL")
    authentication_required: bool = Field(default=True, description="Whether auth is required")
    rate_limit: Optional[int] = Field(None, description="Rate limit per minute")

class HealthStatus(BaseModel):
    """Service health status"""
    status: str = Field(..., description="Health status (healthy/unhealthy)")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime_seconds: Optional[float] = Field(None, description="Service uptime in seconds")
    active_sessions: int = Field(default=0, description="Number of active sessions")
    supported_languages: int = Field(default=0, description="Number of supported languages")
    voice_profiles: int = Field(default=0, description="Number of voice profiles")
    system_info: Optional[Dict[str, Any]] = Field(None, description="Additional system information")

# Alias for backward compatibility
ServiceHealthStatus = HealthStatus
