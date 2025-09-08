"""
Response Models  
Pydantic models for API responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    """Generic API response wrapper"""
    success: bool = Field(..., description="Request success status")
    data: Optional[T] = Field(None, description="Response data")
    message: str = Field("", description="Response message")
    error: Optional[str] = Field(None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

class STTResponse(BaseModel):
    """Speech-to-Text response model"""
    text: str = Field(..., description="Transcribed text")
    confidence: float = Field(..., description="Confidence score")
    language: str = Field(..., description="Detected/used language")
    model_used: str = Field(..., description="Model used for transcription")
    language_detection: Optional[Dict[str, Any]] = Field(None, description="Language detection details")
    enhanced: bool = Field(False, description="Whether audio was enhanced")
    session_id: Optional[str] = Field(None, description="Session ID")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class TTSResponse(BaseModel):
    """Text-to-Speech response model"""
    success: bool = Field(..., description="Success status")
    audio_url: Optional[str] = Field(None, description="URL to audio file")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    sample_rate: Optional[int] = Field(None, description="Audio sample rate")
    model_used: str = Field(..., description="Model used for synthesis")
    cached: bool = Field(False, description="Whether audio was served from cache")
    enhanced: bool = Field(False, description="Whether audio was enhanced")
    cache_key: Optional[str] = Field(None, description="Cache key for the audio")

class ConversationResponse(BaseModel):
    """Conversation response model"""
    success: bool = Field(..., description="Success status")
    user_input: str = Field(..., description="Original user input")
    bot_response: str = Field(..., description="Bot response text")
    sentiment_analysis: Optional[Dict[str, Any]] = Field(None, description="Sentiment analysis results")
    language_info: Optional[Dict[str, Any]] = Field(None, description="Language information")
    context_used: Optional[Dict[str, Any]] = Field(None, description="Context information used")
    audio_response: Optional[Dict[str, Any]] = Field(None, description="Audio response details")
    session_id: Optional[str] = Field(None, description="Session ID")
    conversation_turn: Optional[int] = Field(None, description="Turn number in conversation")

class SessionResponse(BaseModel):
    """Session response model"""
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    voice_settings: Dict[str, Any] = Field(..., description="Voice settings")
    context: Dict[str, Any] = Field(..., description="Session context")
    is_active: bool = Field(..., description="Session active status")
    total_turns: Optional[int] = Field(None, description="Total conversation turns")

class VoiceStatusResponse(BaseModel):
    """Voice service status response model"""
    status: str = Field(..., description="Overall service status")
    components: Dict[str, Any] = Field(..., description="Component health status")
    features: Dict[str, bool] = Field(..., description="Available features")
    cache_stats: Optional[int] = Field(None, description="Cache statistics")
    version: str = Field("2.0.0", description="Service version")
    uptime: Optional[float] = Field(None, description="Service uptime in seconds")
    error: Optional[str] = Field(None, description="Error message if any")

class LanguageDetectionResponse(BaseModel):
    """Language detection response model"""
    primary_language: str = Field(..., description="Primary detected language")
    confidence: float = Field(..., description="Detection confidence")
    is_mixed: bool = Field(..., description="Whether text contains multiple languages")
    language_scores: Dict[str, float] = Field(..., description="Scores for each language")
    script_detected: Optional[str] = Field(None, description="Writing script detected")
    regions_detected: Optional[List[str]] = Field(None, description="Geographical regions")
    code_switching: Optional[Dict[str, Any]] = Field(None, description="Code switching analysis")
    suggestions: Optional[List[str]] = Field(None, description="Language suggestions")

class EnhancementResponse(BaseModel):
    """Audio enhancement response model"""
    success: bool = Field(..., description="Enhancement success status")
    improvement_score: float = Field(..., description="Improvement score (0-1)")
    enhancements_applied: List[str] = Field(..., description="List of applied enhancements")
    original_metrics: Dict[str, Any] = Field(..., description="Original audio metrics")
    enhanced_metrics: Dict[str, Any] = Field(..., description="Enhanced audio metrics")
    processing_time: float = Field(..., description="Processing time in seconds")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field("2.0.0", description="Service version")
    components: Dict[str, Any] = Field(..., description="Component health details")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")
    
class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
