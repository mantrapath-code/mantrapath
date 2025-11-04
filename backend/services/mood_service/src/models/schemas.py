"""Pydantic models for API request/response schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SentimentType(str, Enum):
    """Sentiment classification types."""
    POSITIVE = "positive"
    NEGATIVE = "negative" 
    NEUTRAL = "neutral"
    AMBIGUOUS = "ambiguous"


class EmotionAnalysis(BaseModel):
    """Individual emotion detection result."""
    emotion: str
    sentiment: SentimentType
    confidence: float = Field(..., ge=0.0, le=100.0)
    color: str  # Hex color for visualization


class MoodAnalysisResult(BaseModel):
    """Complete mood analysis result."""
    top_emotions: List[EmotionAnalysis]
    primary_emotion: str
    primary_sentiment: SentimentType
    confidence_score: float = Field(..., ge=0.0, le=100.0)


# Request Models
class MoodCreateRequest(BaseModel):
    """Request model for creating a mood entry with AI-powered emotion detection."""
    # AI-powered input fields (new format) - make optional for backward compatibility
    input_text: Optional[str] = Field(None, max_length=2000, description="User's text or transcribed speech")
    input_type: str = Field(default="text", description="Input type: 'text' or 'voice'")
    audio_emotion_data: Optional[Dict[str, Any]] = Field(None, description="Voice emotion analysis data from voice service")
    language: Optional[str] = Field(default="en", description="Language code (en, hi, etc.)")
    
    # Optional context fields
    context_tags: Optional[List[str]] = None
    location: Optional[str] = None
    activity: Optional[str] = None
    
    # Legacy fields (for backward compatibility, all optional now as they're AI-inferred)
    mood_score: Optional[int] = Field(None, ge=1, le=10, description="Mood score (AI-inferred if not provided)")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="Stress level (AI-inferred if not provided)")
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="Energy level (AI-inferred if not provided)")
    description: Optional[str] = Field(None, max_length=1000, description="Legacy description field")
    notes: Optional[str] = Field(None, max_length=1000, description="Notes field for journal entries")
    
    model_config = ConfigDict(extra="allow")  # Allow extra fields for backward compatibility


class EmotionAnalysisRequest(BaseModel):
    """Request model for emotion analysis."""
    text: str = Field(..., min_length=1, max_length=1000)
    include_mood_entry: bool = Field(default=False, description="Whether to save as mood entry")
    mood_score: Optional[int] = Field(None, ge=1, le=10)


# Analytics Models
class WellbeingScore(BaseModel):
    """Comprehensive wellbeing score model."""
    score: float = Field(..., ge=0.0, le=10.0, description="Overall wellbeing score")
    category: str = Field(..., description="Score category (excellent, good, moderate, needs_attention, concerning)")
    components: Dict[str, float] = Field(default_factory=dict, description="Score breakdown by component")
    recommendations: List[str] = Field(default_factory=list, description="Personalized recommendations")
    period: str = Field(..., description="Analysis period")
    calculated_at: datetime


class MoodInsight(BaseModel):
    """Personalized mood insight model."""
    type: str = Field(..., description="Insight type (positive, warning, suggestion)")
    title: str = Field(..., description="Insight title")
    message: str = Field(..., description="Insight message")
    actionable: bool = Field(default=False, description="Whether insight includes actionable advice")
    priority: str = Field(default="low", description="Insight priority (high, medium, low)")
    generated_at: datetime


class WeeklyPattern(BaseModel):
    """Weekly mood pattern analysis."""
    week_start: datetime
    week_end: datetime
    average_mood: float = Field(..., ge=0.0, le=10.0)
    average_stress: float = Field(..., ge=0.0, le=10.0)
    average_energy: float = Field(..., ge=0.0, le=10.0)
    entry_count: int = Field(..., ge=0)
    daily_patterns: Dict[str, float] = Field(default_factory=dict, description="Day of week patterns")
    consistency_score: float = Field(..., ge=0.0, le=10.0, description="Mood consistency score")
    dominant_emotions: List[str] = Field(default_factory=list, description="Most frequent emotions")


class EmotionTrend(BaseModel):
    """Emotion trend analysis over time."""
    emotion: str = Field(..., description="Emotion name")
    average_intensity: float = Field(..., ge=0.0, le=1.0, description="Average intensity")
    frequency: float = Field(..., ge=0.0, description="Occurrences per week")
    trend_direction: str = Field(..., description="Trend direction (increasing, decreasing, stable)")
    total_occurrences: int = Field(..., ge=0)
    first_occurrence: datetime
    last_occurrence: datetime


class AnalyticsOverview(BaseModel):
    """Comprehensive analytics overview."""
    period: str = Field(..., description="Analysis period")
    wellbeing_score: WellbeingScore
    total_entries: int = Field(..., ge=0)
    average_mood: float = Field(..., ge=0.0, le=10.0)
    average_stress: float = Field(..., ge=0.0, le=10.0)
    average_energy: float = Field(..., ge=0.0, le=10.0)
    mood_trend: str = Field(..., description="Overall mood trend (improving, declining, stable)")
    insights: List[MoodInsight] = Field(default_factory=list)
    last_updated: datetime


class AnalyticsResponse(BaseModel):
    """Generic analytics response wrapper."""
    success: bool = Field(default=True)
    data: Any = Field(..., description="Analytics data")
    message: str = Field(default="Analytics retrieved successfully")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MoodContextRequest(BaseModel):
    """Request model for creating mood context for memory service."""
    session_id: Optional[str] = None
    context_summary: Optional[str] = None
    time_range_hours: int = Field(default=24, ge=1, le=168)  # 1 hour to 1 week


# Response Models
class MoodEntryResponse(BaseModel):
    """Response model for mood entry."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    
    # AI-powered input fields (optional for backward compatibility)
    input_text: Optional[str] = None
    input_type: Optional[str] = "text"
    language: Optional[str] = None
    
    # AI-inferred scores
    mood_score: int
    stress_level: Optional[int] = None
    energy_level: Optional[int] = None
    
    # Legacy fields
    description: Optional[str] = None
    
    # AI analysis results
    primary_emotion: Optional[str] = None
    primary_sentiment: Optional[SentimentType] = None
    emotion_analysis: Optional[Dict[str, Any]] = None
    text_emotion_analysis: Optional[Dict[str, Any]] = None
    voice_emotion_analysis: Optional[Dict[str, Any]] = None
    combined_emotion_confidence: Optional[float] = None
    ai_inferred_scores: Optional[Dict[str, Any]] = None
    
    # Context fields
    context_tags: Optional[List[str]] = None
    location: Optional[str] = None
    activity: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None


class MoodAnalyticsOverview(BaseModel):
    """Overview analytics for user's mood data."""
    total_entries: int
    average_mood: float
    mood_trend: str  # "improving", "declining", "stable"
    stress_average: Optional[float] = None
    energy_average: Optional[float] = None
    mood_distribution: Dict[str, int]  # mood ranges -> count  
    recent_patterns: List[Any] = []
    # Optional fields for backwards compatibility
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    emotion_distribution: Optional[Dict[str, int]] = None
    last_entry_date: Optional[datetime] = None
    improvement_trend: Optional[float] = None


class WeeklyPattern(BaseModel):
    """Weekly mood pattern data."""
    week: str  # Format: "2024-W01"
    average_mood: float
    dominant_emotion: Optional[str] = None
    entry_count: int


class MoodPatternsResponse(BaseModel):
    """Response model for mood patterns analysis."""
    weekly_patterns: List[WeeklyPattern]
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    trend_analysis: Dict[str, Any]


class MoodContextResponse(BaseModel):
    """Response model for mood context."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    user_id: str
    session_id: Optional[str] = None
    context_summary: Optional[str] = None
    dominant_emotion: Optional[str] = None
    average_mood_score: Optional[float] = None
    emotion_distribution: Optional[Dict[str, Any]] = None
    context_start: datetime
    context_end: datetime
    created_at: datetime


# Health and Status Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    version: str
    dependencies: Dict[str, str]


class ServiceInfo(BaseModel):
    """Service information response."""
    name: str
    version: str
    description: str
    endpoints: List[str]
    features: Dict[str, bool]