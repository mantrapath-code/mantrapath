"""
Action Orchestrator Models
Core data models for voice-driven cross-service workflows
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


def utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


class IntentType(str, Enum):
    """Voice intent classification types"""
    MOOD_TRACKING = "mood_tracking"
    JOURNAL_ENTRY = "journal_entry"
    CHAT_CONVERSATION = "chat_conversation"
    PROFILE_UPDATE = "profile_update"
    COMMUNITY_INTERACTION = "community_interaction"
    ANALYTICS_QUERY = "analytics_query"
    CONTENT_SEARCH = "content_search"
    VOICE_COMMAND = "voice_command"
    CRISIS_INTERVENTION = "crisis_intervention"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """Confidence levels for intent classification"""
    HIGH = "high"      # > 0.8
    MEDIUM = "medium"  # 0.5 - 0.8
    LOW = "low"       # 0.3 - 0.5
    VERY_LOW = "very_low"  # < 0.3


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class CulturalContext(BaseModel):
    """Cultural adaptation context for workflows"""
    model_config = ConfigDict(from_attributes=True)
    
    language: str = Field(description="Detected/specified language code")
    cultural_region: Optional[str] = Field(None, description="Cultural region context")
    communication_style: Optional[str] = Field(None, description="Communication style preference")
    formality_level: Optional[str] = Field(None, description="Formality level preference")
    cultural_sensitivities: List[str] = Field(default_factory=list, description="Cultural considerations")
    time_zone: Optional[str] = Field(None, description="User timezone")
    date_format: Optional[str] = Field(None, description="Preferred date format")


class VoiceIntent(BaseModel):
    """Voice intent processing result"""
    model_config = ConfigDict(from_attributes=True)
    
    intent_id: UUID = Field(default_factory=uuid4)
    intent_type: IntentType
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    confidence_level: ConfidenceLevel
    raw_text: str = Field(description="Original voice input text")
    processed_text: str = Field(description="Cleaned and normalized text")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters")
    cultural_context: CulturalContext
    timestamp: datetime = Field(default_factory=utc_now)
    user_id: UUID
    session_id: Optional[UUID] = None


class ServiceAction(BaseModel):
    """Individual service action within a workflow"""
    model_config = ConfigDict(from_attributes=True)
    
    action_id: UUID = Field(default_factory=uuid4)
    service_name: str = Field(description="Target service name")
    action_type: str = Field(description="Action type to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    cultural_adaptations: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=30, description="Action timeout")
    retry_count: int = Field(default=3, description="Maximum retry attempts")
    rollback_action: Optional[Dict[str, Any]] = None
    dependencies: List[UUID] = Field(default_factory=list, description="Dependent action IDs")


class WorkflowStep(BaseModel):
    """Single step in workflow execution"""
    model_config = ConfigDict(from_attributes=True)
    
    step_id: UUID = Field(default_factory=uuid4)
    actions: List[ServiceAction]
    parallel_execution: bool = Field(default=False)
    success_condition: Optional[str] = None
    failure_handling: Optional[str] = None


class ActionWorkflow(BaseModel):
    """Complete cross-service workflow definition"""
    model_config = ConfigDict(from_attributes=True)
    
    workflow_id: UUID = Field(default_factory=uuid4)
    intent: VoiceIntent
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    rollback_steps: List[WorkflowStep] = Field(default_factory=list)
    cultural_context: CulturalContext
    
    # Execution tracking
    current_step_index: int = 0
    executed_actions: List[UUID] = Field(default_factory=list)
    failed_actions: List[UUID] = Field(default_factory=list)
    rollback_actions: List[UUID] = Field(default_factory=list)


class ActionResult(BaseModel):
    """Result of a single service action"""
    model_config = ConfigDict(from_attributes=True)
    
    action_id: UUID
    service_name: str
    success: bool
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: int
    cultural_adaptations_applied: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)


class WorkflowResult(BaseModel):
    """Complete workflow execution result"""
    model_config = ConfigDict(from_attributes=True)
    
    workflow_id: UUID
    intent: VoiceIntent
    status: WorkflowStatus
    action_results: List[ActionResult]
    total_execution_time_ms: int
    successful_actions: int
    failed_actions: int
    cultural_context: CulturalContext
    started_at: datetime
    completed_at: datetime
    error_summary: Optional[str] = None


# Request/Response Models
class OrchestrationRequest(BaseModel):
    """Request to orchestrate cross-service actions"""
    model_config = ConfigDict(from_attributes=True)
    
    voice_input: str = Field(description="Voice input text")
    user_id: UUID
    session_id: Optional[UUID] = None
    cultural_preferences: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class OrchestrationResponse(BaseModel):
    """Response from action orchestration"""
    model_config = ConfigDict(from_attributes=True)
    
    workflow_id: UUID
    intent: VoiceIntent
    workflow_result: Optional[WorkflowResult] = None
    estimated_completion_time: Optional[int] = None  # seconds
    status: WorkflowStatus
    message: str = Field(description="Human-readable response")
    cultural_adaptations: Dict[str, Any] = Field(default_factory=dict)


# Event Models for NATS
class VoiceEvent(BaseModel):
    """Voice activity event for streaming"""
    model_config = ConfigDict(from_attributes=True)
    
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str = Field(description="voice.activity_detected, voice.intent_classified, etc.")
    user_id: UUID
    session_id: Optional[UUID] = None
    intent: Optional[VoiceIntent] = None
    workflow_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=utc_now)
    cultural_context: Optional[CulturalContext] = None


class WorkflowEvent(BaseModel):
    """Workflow execution event for coordination"""
    model_config = ConfigDict(from_attributes=True)
    
    event_id: UUID = Field(default_factory=uuid4)
    event_type: str = Field(description="workflow.started, workflow.step_completed, etc.")
    workflow_id: UUID
    user_id: UUID
    step_id: Optional[UUID] = None
    action_id: Optional[UUID] = None
    status: WorkflowStatus
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=utc_now)
    cultural_context: CulturalContext


# Configuration Models
class ServiceEndpoint(BaseModel):
    """Service endpoint configuration"""
    model_config = ConfigDict(from_attributes=True)
    
    service_name: str
    base_url: str
    port: int
    health_endpoint: str = "/health"
    timeout_seconds: int = 30
    max_retries: int = 3
    circuit_breaker_enabled: bool = True


class OrchestratorConfig(BaseModel):
    """Action Orchestrator configuration"""
    model_config = ConfigDict(from_attributes=True)
    
    # Service configuration
    service_endpoints: List[ServiceEndpoint]
    
    # Intent processing
    intent_confidence_threshold: float = 0.5
    language_detection_threshold: float = 0.7
    
    # Workflow execution
    max_workflow_duration_seconds: int = 300  # 5 minutes
    max_concurrent_workflows: int = 100
    default_timeout_seconds: int = 30
    
    # Cultural context
    supported_languages: List[str] = ["en", "hi", "es", "fr", "de"]
    default_cultural_region: str = "global"
    
    # Event processing
    nats_url: str = "nats://localhost:4222"
    event_stream_name: str = "mantrapath.orchestrator"
    
    # Monitoring
    metrics_enabled: bool = True
    logging_level: str = "INFO"
