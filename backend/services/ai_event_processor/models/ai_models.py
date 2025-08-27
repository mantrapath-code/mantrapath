from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def utc_now():
    return datetime.now(timezone.utc)

class EmotionAnalysisRequest(BaseModel):
    """Request model for emotion analysis"""
    text: str = Field(..., description="Text to analyze for emotion")
    language: str = Field(default="en", description="Language code (ISO 639-1)")
    user_id: str = Field(..., description="User ID for context")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class EmotionResult(BaseModel):
    """Emotion analysis result"""
    emotion: str = Field(..., description="Primary detected emotion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    emotions: Dict[str, float] = Field(..., description="All emotion scores")
    cultural_context: Optional[str] = Field(default=None, description="Cultural interpretation")
    processing_time_ms: Optional[float] = Field(default=None, description="Processing time in milliseconds")
    language: Optional[str] = Field(default=None, description="Detected or provided language")
    has_cultural_adaptation: Optional[bool] = Field(default=False, description="Whether cultural adaptation was applied")
    analysis_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Analysis metadata")
    
    # Legacy field aliases for backward compatibility
    @property
    def primary_emotion(self) -> str:
        """Backward compatibility alias for emotion"""
        return self.emotion
    
    @property
    def emotion_scores(self) -> Dict[str, float]:
        """Backward compatibility alias for emotions"""
        return self.emotions

class EmotionAnalysisResponse(BaseModel):
    """Response model for emotion analysis"""
    user_id: str
    result: EmotionResult
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=utc_now)
    language: str
    cultural_adaptation: Optional[Dict[str, Any]] = None

class ContextUpdateRequest(BaseModel):
    """Request model for context updates"""
    user_id: str = Field(..., description="User ID")
    context_data: Dict[str, Any] = Field(..., description="Context data to update")
    source: str = Field(..., description="Source service/component")
    timestamp: datetime = Field(default_factory=utc_now)

class PredictiveAnalysisResult(BaseModel):
    """Predictive analysis result"""
    intervention_needed: bool = Field(..., description="Whether intervention is needed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence")
    intervention_type: Optional[str] = Field(default=None, description="Type of intervention")
    urgency_level: str = Field(..., description="Urgency level: low, medium, high, critical")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    cultural_considerations: Optional[Dict[str, Any]] = Field(default=None)

class PredictiveAnalysisResponse(BaseModel):
    """Response model for predictive analysis"""
    user_id: str
    result: PredictiveAnalysisResult
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=utc_now)
    factors_analyzed: List[str] = Field(default_factory=list)

class AIMetrics(BaseModel):
    """AI processing metrics"""
    total_events_processed: int = 0
    events_per_minute: float = 0.0
    average_processing_time_ms: float = 0.0
    error_rate: float = 0.0
    active_users: int = 0
    emotion_analysis_count: int = 0
    cultural_adaptations: int = 0
    predictive_analyses: int = 0

class CulturalContext(BaseModel):
    """Cultural context information"""
    culture: str = Field(..., description="Cultural identifier")
    language: str = Field(..., description="Language code")
    region: Optional[str] = Field(default=None, description="Regional context")
    adaptation_rules: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Cultural detection confidence")

class EventProcessingStatus(BaseModel):
    """Event processing status"""
    event_id: str
    status: str = Field(..., description="processing, completed, failed")
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=utc_now)
