"""
AI Processing and Cross-Service Intelligence Event Schemas
Supporting real-time AI inference coordination and intelligence sharing.

Multilingual Support:
- AI models support multiple languages
- Cultural context considered in AI processing
- Cross-service intelligence sharing includes cultural adaptations
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
import uuid


class AIEventType(str, Enum):
    """AI processing event types"""
    # AI Inference
    INFERENCE_REQUESTED = "ai.inference_requested"
    INFERENCE_STARTED = "ai.inference_started"
    INFERENCE_COMPLETED = "ai.inference_completed"
    INFERENCE_FAILED = "ai.inference_failed"
    
    # Model Management
    MODEL_LOADED = "ai.model_loaded"
    MODEL_UNLOADED = "ai.model_unloaded"
    MODEL_ERROR = "ai.model_error"
    
    # Context Management
    CONTEXT_UPDATED = "ai.context_updated"
    CONTEXT_CLEARED = "ai.context_cleared"
    
    # Performance
    PERFORMANCE_THRESHOLD_EXCEEDED = "ai.performance_threshold_exceeded"
    MEMORY_WARNING = "ai.memory_warning"


class IntelligenceEventType(str, Enum):
    """Cross-service intelligence event types"""
    # Intelligence Sharing
    CONTEXT_SHARED = "intelligence.context_shared"
    INSIGHT_GENERATED = "intelligence.insight_generated"
    PREDICTION_MADE = "intelligence.prediction_made"
    
    # Pattern Recognition
    PATTERN_DETECTED = "intelligence.pattern_detected"
    ANOMALY_DETECTED = "intelligence.anomaly_detected"
    CORRELATION_FOUND = "intelligence.correlation_found"
    
    # Learning Events
    MODEL_UPDATED = "intelligence.model_updated"
    FEEDBACK_RECEIVED = "intelligence.feedback_received"
    ADAPTATION_APPLIED = "intelligence.adaptation_applied"


class ProcessingData(BaseModel):
    """AI processing metadata"""
    model_config = {"protected_namespaces": ()}
    
    model_name: str = Field(..., description="AI model identifier")
    model_version: str = Field(default="1.0", description="Model version")
    input_data_hash: str = Field(..., description="Hash of input data for caching")
    processing_time_ms: int = Field(..., ge=0, description="Processing time in milliseconds")
    
    # Performance Metrics
    confidence_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Model confidence scores for different outputs"
    )
    
    # Resource Usage
    memory_usage_mb: float = Field(default=0.0, ge=0.0, description="Memory usage in MB")
    gpu_utilization: float = Field(default=0.0, ge=0.0, le=100.0, description="GPU utilization percentage")
    cpu_utilization: float = Field(default=0.0, ge=0.0, le=100.0, description="CPU utilization percentage")
    
    # Quality Metrics
    input_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Input data quality")
    output_quality_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Output quality")


class ContextData(BaseModel):
    """AI context information"""
    # User Context
    user_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="User-specific context (preferences, history, etc.)"
    )
    
    # Cultural Context
    cultural_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Cultural adaptation context"
    )
    
    # Session Context
    session_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current session context"
    )
    
    # Conversation Context
    conversation_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent conversation history"
    )
    
    # External Context
    external_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="External data context (weather, time, location, etc.)"
    )


class ResultMetadata(BaseModel):
    """AI processing result metadata"""
    # Output Statistics
    output_tokens: Optional[int] = Field(None, ge=0, description="Number of output tokens generated")
    input_tokens: Optional[int] = Field(None, ge=0, description="Number of input tokens processed")
    
    # Processing Statistics
    inference_steps: Optional[int] = Field(None, ge=1, description="Number of inference steps")
    batch_size: int = Field(default=1, ge=1, description="Batch size used")
    
    # Quality and Safety
    safety_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Content safety score")
    coherence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Output coherence score")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Output relevance score")
    
    # Cultural Adaptation
    cultural_adaptations_applied: List[str] = Field(
        default_factory=list,
        description="Cultural adaptations applied to output"
    )
    
    # Error Information
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
    error_code: Optional[str] = Field(None, description="Error code if processing failed")


class AIProcessingEvent(BaseModel):
    """AI processing coordination event"""
    
    # Core Event Data
    event_type: AIEventType = Field(..., description="Type of AI processing event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    
    # AI Processing Data
    processing_data: ProcessingData = Field(..., description="AI processing metadata")
    context_data: ContextData = Field(..., description="AI context information")
    result_metadata: Optional[ResultMetadata] = Field(None, description="Processing result metadata")
    
    # Service Information
    source_service: str = Field(..., description="Service that triggered the AI processing")
    target_service: Optional[str] = Field(None, description="Target service for results")
    
    # Request/Response Data References
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Request identifier")
    response_data_reference: Optional[str] = Field(None, description="Reference to response data storage")
    
    # User Information
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    @validator('processing_data')
    def validate_processing_data(cls, v: ProcessingData) -> ProcessingData:
        """Validate AI processing data"""
        if v.processing_time_ms > 30000:  # 30 seconds
            # Long processing time - should be flagged
            pass
        return v


class IntelligenceData(BaseModel):
    """Cross-service intelligence data"""
    source_service: str = Field(..., description="Service generating the intelligence")
    insight_type: str = Field(..., description="Type of insight (pattern, prediction, recommendation)")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in the intelligence")
    
    # Intelligence Content
    correlation_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Data correlations and patterns"
    )
    
    # Predictions
    predictions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Generated predictions"
    )
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Generated recommendations"
    )
    
    # Evidence
    supporting_evidence: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evidence supporting the intelligence"
    )
    
    # Temporal Information
    valid_from: Optional[datetime] = Field(None, description="Intelligence valid from timestamp")
    valid_until: Optional[datetime] = Field(None, description="Intelligence valid until timestamp")
    
    # Cultural Considerations
    cultural_relevance: Dict[str, float] = Field(
        default_factory=dict,
        description="Relevance scores for different cultural contexts"
    )


class SharingMetadata(BaseModel):
    """Intelligence sharing metadata"""
    target_services: List[str] = Field(..., description="Services to share intelligence with")
    ttl_seconds: int = Field(default=3600, ge=60, description="Time-to-live for intelligence")
    priority_level: int = Field(default=1, ge=1, le=5, description="Priority level (1=low, 5=critical)")
    
    # Sharing Constraints
    sharing_constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Constraints on how intelligence can be shared"
    )
    
    # Access Control
    access_level: str = Field(default="internal", description="Access level for intelligence")
    user_consent_required: bool = Field(default=True, description="Whether user consent is required")
    
    # Feedback Mechanism
    feedback_requested: bool = Field(default=False, description="Whether feedback is requested")
    feedback_deadline: Optional[datetime] = Field(None, description="Deadline for feedback")


class CrossServiceIntelligenceEvent(BaseModel):
    """Cross-service intelligence sharing event"""
    
    # Core Event Data
    event_type: IntelligenceEventType = Field(..., description="Type of intelligence event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    
    # Intelligence Data
    intelligence_data: IntelligenceData = Field(..., description="Intelligence content")
    sharing_metadata: SharingMetadata = Field(..., description="Sharing metadata")
    
    # Context
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for related events")
    
    # Processing Information
    processing_chain: List[str] = Field(
        default_factory=list,
        description="Chain of services that processed this intelligence"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    @validator('intelligence_data')
    def validate_intelligence_data(cls, v: IntelligenceData) -> IntelligenceData:
        """Validate intelligence data quality"""
        if v.confidence_level < 0.5:
            # Low confidence intelligence - consider filtering
            pass
        return v


# Helper Functions for Event Creation

def create_ai_processing_event(
    event_type: AIEventType,
    model_name: str,
    input_data_hash: str,
    processing_time_ms: int,
    source_service: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    **kwargs
) -> AIProcessingEvent:
    """Create an AI processing event with default values"""
    
    processing_data = ProcessingData(
        model_name=model_name,
        input_data_hash=input_data_hash,
        processing_time_ms=processing_time_ms
    )
    
    context_data = ContextData()
    
    return AIProcessingEvent(
        event_type=event_type,
        processing_data=processing_data,
        context_data=context_data,
        source_service=source_service,
        user_id=user_id,
        session_id=session_id,
        **kwargs
    )


def create_intelligence_event(
    event_type: IntelligenceEventType,
    source_service: str,
    insight_type: str,
    confidence_level: float,
    target_services: List[str],
    user_id: Optional[str] = None,
    **kwargs
) -> CrossServiceIntelligenceEvent:
    """Create a cross-service intelligence event"""
    
    intelligence_data = IntelligenceData(
        source_service=source_service,
        insight_type=insight_type,
        confidence_level=confidence_level
    )
    
    sharing_metadata = SharingMetadata(
        target_services=target_services
    )
    
    return CrossServiceIntelligenceEvent(
        event_type=event_type,
        intelligence_data=intelligence_data,
        sharing_metadata=sharing_metadata,
        user_id=user_id,
        **kwargs
    )


# Event Validation Functions

def validate_ai_event_schema(event_data: Dict[str, Any], event_type: str) -> bool:
    """Validate AI event data against schema"""
    try:
        if "ai." in event_type:
            AIProcessingEvent(**event_data)
        elif "intelligence." in event_type:
            CrossServiceIntelligenceEvent(**event_data)
        else:
            return False
        return True
    except Exception:
        return False


# AI Model Registry and Performance Tracking

AI_MODELS = {
    "gpt-4": {"type": "language", "max_tokens": 4096, "languages": ["en", "es", "fr", "de", "zh", "ja"]},
    "claude-3": {"type": "language", "max_tokens": 8192, "languages": ["en", "es", "fr", "de", "zh", "ja"]},
    "whisper": {"type": "speech", "languages": ["en", "es", "fr", "de", "zh", "ja", "ko", "pt", "ru"]},
    "emotion-classifier": {"type": "emotion", "languages": ["en", "es", "fr", "de", "zh", "ja"]},
    "cultural-adapter": {"type": "cultural", "regions": ["US", "EU", "ASIA", "LATAM"]},
}


def get_model_capabilities(model_name: str) -> Dict[str, Any]:
    """Get capabilities for a specific AI model"""
    return AI_MODELS.get(model_name, {})


def is_model_multilingual(model_name: str) -> bool:
    """Check if a model supports multiple languages"""
    model_info = AI_MODELS.get(model_name, {})
    languages = model_info.get("languages", [])
    return len(languages) > 1


# Performance Thresholds

PERFORMANCE_THRESHOLDS = {
    "processing_time_ms": 5000,  # 5 seconds
    "memory_usage_mb": 1024,     # 1 GB
    "gpu_utilization": 90.0,     # 90%
    "cpu_utilization": 80.0,     # 80%
}


def check_performance_thresholds(processing_data: ProcessingData) -> List[str]:
    """Check if processing data exceeds performance thresholds"""
    violations = []
    
    if processing_data.processing_time_ms > PERFORMANCE_THRESHOLDS["processing_time_ms"]:
        violations.append("processing_time_exceeded")
        
    if processing_data.memory_usage_mb > PERFORMANCE_THRESHOLDS["memory_usage_mb"]:
        violations.append("memory_usage_exceeded")
        
    if processing_data.gpu_utilization > PERFORMANCE_THRESHOLDS["gpu_utilization"]:
        violations.append("gpu_utilization_exceeded")
        
    if processing_data.cpu_utilization > PERFORMANCE_THRESHOLDS["cpu_utilization"]:
        violations.append("cpu_utilization_exceeded")
    
    return violations
