"""
Pydantic models for Translation Service API requests and responses
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum

class TranslationEngine(str, Enum):
    """Supported translation engines"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    OPENAI = "openai"
    LOCAL = "local"
    AUTO = "auto"  # Automatic engine selection

class Priority(str, Enum):
    """Translation priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class TranslationStatus(str, Enum):
    """Translation request status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

class LanguageDetectionRequest(BaseModel):
    """Request for language detection"""
    text: str = Field(..., min_length=1, max_length=5000)
    engines: Optional[List[str]] = Field(default=["langdetect", "fasttext"])
    include_alternatives: bool = Field(default=True)
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()

class LanguageDetectionResponse(BaseModel):
    """Response for language detection"""
    detected_language: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    alternative_languages: Optional[List[Dict[str, Union[str, float]]]] = None
    processing_time_ms: int
    engine_used: str

class TranslationRequest(BaseModel):
    """Request for text translation"""
    text: str = Field(..., min_length=1, max_length=5000)
    source_language: Optional[str] = Field(default=None, pattern=r'^[a-z]{2}$')
    target_language: str = Field(..., pattern=r'^[a-z]{2}$')
    
    # Optional parameters
    engine: TranslationEngine = Field(default=TranslationEngine.AUTO)
    domain: Optional[str] = Field(default=None)
    context_type: Optional[str] = Field(default=None)
    cultural_adaptation: bool = Field(default=True)
    use_custom_glossary: bool = Field(default=True)
    priority: Priority = Field(default=Priority.NORMAL)
    
    # Caching options
    use_cache: bool = Field(default=True)
    cache_duration: Optional[int] = Field(default=None, ge=0)
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()

class VoiceTranslationRequest(BaseModel):
    """Request for voice/audio translation"""
    audio_format: str = Field(..., pattern=r'^(wav|mp3|ogg|flac)$')
    audio_duration: float = Field(..., gt=0, le=300)  # max 5 minutes
    source_language: Optional[str] = Field(default=None, pattern=r'^[a-z]{2}$')
    target_language: str = Field(..., pattern=r'^[a-z]{2}$')
    
    # Voice-specific options
    return_audio: bool = Field(default=False)
    voice_gender: Optional[str] = Field(default=None, pattern=r'^(male|female|neutral)$')
    speech_rate: float = Field(default=1.0, ge=0.5, le=2.0)
    
    # General translation options
    engine: TranslationEngine = Field(default=TranslationEngine.AUTO)
    domain: Optional[str] = Field(default=None)
    cultural_adaptation: bool = Field(default=True)

class TranslationResponse(BaseModel):
    """Response for translation request"""
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    
    # Processing details
    engine_used: str
    processing_time_ms: int
    cache_hit: bool = Field(default=False)
    cultural_adaptations_applied: List[str] = Field(default_factory=list)
    custom_terms_used: List[str] = Field(default_factory=list)
    
    # Request tracking
    request_id: str
    status: TranslationStatus

class VoiceTranslationResponse(BaseModel):
    """Response for voice translation request"""
    transcribed_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    quality_score: float = Field(..., ge=0.0, le=1.0)
    
    # Audio-specific data
    audio_url: Optional[str] = None  # URL to translated audio file
    audio_duration: Optional[float] = None
    speech_rate_used: float
    
    # Processing details
    transcription_engine: str
    translation_engine: str
    tts_engine: Optional[str] = None
    processing_time_ms: int
    request_id: str

class BatchTranslationRequest(BaseModel):
    """Request for batch translation"""
    texts: List[str] = Field(..., min_items=1, max_items=100)
    source_language: Optional[str] = Field(default=None, pattern=r'^[a-z]{2}$')
    target_language: str = Field(..., pattern=r'^[a-z]{2}$')
    
    # Batch-specific options
    preserve_order: bool = Field(default=True)
    fail_fast: bool = Field(default=False)
    
    # General options
    engine: TranslationEngine = Field(default=TranslationEngine.AUTO)
    domain: Optional[str] = Field(default=None)
    cultural_adaptation: bool = Field(default=True)
    use_custom_glossary: bool = Field(default=True)
    
    @validator('texts')
    def validate_texts(cls, v):
        total_length = sum(len(text) for text in v)
        if total_length > 50000:  # 50KB total limit
            raise ValueError("Total text length exceeds 50KB limit")
        return v

class BatchTranslationResponse(BaseModel):
    """Response for batch translation"""
    translations: List[TranslationResponse]
    total_processing_time_ms: int
    success_count: int
    failure_count: int
    batch_id: str

class TranslationFeedbackRequest(BaseModel):
    """Request to submit translation feedback"""
    translation_request_id: str
    rating: int = Field(..., ge=1, le=5)
    accuracy_rating: Optional[int] = Field(default=None, ge=1, le=5)
    cultural_appropriateness: Optional[int] = Field(default=None, ge=1, le=5)
    naturalness_rating: Optional[int] = Field(default=None, ge=1, le=5)
    
    # Detailed feedback
    suggested_translation: Optional[str] = Field(default=None, max_length=5000)
    comments: Optional[str] = Field(default=None, max_length=1000)
    reported_issues: Optional[List[str]] = Field(default=None)

class CustomGlossaryRequest(BaseModel):
    """Request to add/update custom glossary term"""
    source_term: str = Field(..., min_length=1, max_length=100)
    source_language: str = Field(..., pattern=r'^[a-z]{2}$')
    target_term: str = Field(..., min_length=1, max_length=100)
    target_language: str = Field(..., pattern=r'^[a-z]{2}$')
    domain: str = Field(...)
    
    # Optional metadata
    definition: Optional[str] = Field(default=None, max_length=500)
    cultural_context: Optional[str] = Field(default=None, max_length=500)
    usage_examples: Optional[List[str]] = Field(default=None)
    pronunciation: Optional[str] = Field(default=None, max_length=100)

class LanguageInfo(BaseModel):
    """Information about a supported language"""
    code: str
    name: str
    native_name: str
    rtl: bool
    tier: int
    features: List[str]

class SupportedLanguagesResponse(BaseModel):
    """Response listing all supported languages"""
    languages: List[LanguageInfo]
    total_count: int
    tiers: Dict[int, Dict[str, Any]]

class TranslationStatsResponse(BaseModel):
    """Translation usage statistics"""
    total_translations: int
    cache_hit_rate: float
    average_quality_score: float
    average_processing_time_ms: float
    popular_language_pairs: List[Dict[str, Any]]
    engine_usage: Dict[str, int]
    domain_usage: Dict[str, int]

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    engines_status: Dict[str, str]
    cache_status: str
    database_status: str
    uptime_seconds: int

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
