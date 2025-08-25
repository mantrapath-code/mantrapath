"""
Shared assistance models for backend services.

Single source of truth for assistance evaluation, timing, cultural, decisions,
health/status, integration status, and metrics.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class AssistanceType(str, Enum):
    CRISIS_INTERVENTION = "crisis_intervention"
    PROACTIVE_SUPPORT = "proactive_support"
    GENTLE_CHECK_IN = "gentle_check_in"
    MOOD_SUPPORT = "mood_support"
    BEHAVIORAL_GUIDANCE = "behavioral_guidance"
    CULTURAL_ADAPTATION = "cultural_adaptation"

class UrgencyLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class CulturalProfile(BaseModel):
    primary_culture: str = Field(...)
    communication_style: str = Field(...)
    family_involvement: Optional[bool] = None
    hierarchical_respect: Optional[bool] = None
    indirect_communication: Optional[bool] = None

class TimingEvaluation(BaseModel):
    timing_appropriate: bool = Field(...)
    timing_confidence: float = Field(...)
    can_proceed: bool = Field(...)
    recommended_delay_minutes: int = 0
    recent_assistance_check: Dict[str, Any] = Field(default_factory=dict)
    activity_analysis: Dict[str, Any] = Field(default_factory=dict)
    cultural_timing: Dict[str, Any] = Field(default_factory=dict)
    urgency_override: bool = False

class CulturalEvaluation(BaseModel):
    culturally_appropriate: bool = Field(...)
    appropriateness_score: float = Field(...)
    content_evaluation: Dict[str, Any] = Field(default_factory=dict)
    timing_evaluation: Dict[str, Any] = Field(default_factory=dict)
    adapted_content: Optional[Dict[str, Any]] = None
    cultural_considerations: List[str] = Field(default_factory=list)

class InterventionAnalysis(BaseModel):
    intervention_needed: bool = Field(...)
    confidence: float = Field(...)
    intervention_type: Optional[AssistanceType] = None
    urgency_level: UrgencyLevel = Field(...)
    recommended_actions: List[str] = Field(default_factory=list)
    risk_factors: Dict[str, Any] = Field(default_factory=dict)
    fallback_reason: Optional[str] = None

class AssistanceContent(BaseModel):
    content_id: str = Field(...)
    title: str = Field(...)
    content: str = Field(...)
    actions: List[str] = Field(default_factory=list)
    urgency: UrgencyLevel = Field(...)
    cultural_adaptations: Dict[str, str] = Field(default_factory=dict)
    confidence_score: float = Field(...)

class AssistanceDecision(BaseModel):
    should_provide_assistance: bool = Field(...)
    confidence: float = Field(...)
    reasoning: List[str] = Field(default_factory=list)
    assistance_type: Optional[AssistanceType] = None
    priority_score: float = Field(...)
    user_preferences_respected: bool = Field(...)

class AssistanceEvaluation(BaseModel):
    user_id: str = Field(...)
    evaluation_timestamp: datetime = Field(...)
    intervention_analysis: InterventionAnalysis = Field(...)
    timing_evaluation: TimingEvaluation = Field(...)
    cultural_evaluation: CulturalEvaluation = Field(...)
    assistance_decision: AssistanceDecision = Field(...)
    assistance_content: Optional[AssistanceContent] = Field(...)
    confidence_score: float = Field(...)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class UserAssistanceNeeds(BaseModel):
    user_id: str = Field(...)
    current_needs: List[AssistanceType] = Field(...)
    assistance_preferences: Dict[str, Any] = Field(...)
    cultural_profile: CulturalProfile = Field(...)
    assistance_history: List[Dict[str, Any]] = Field(...)
    last_assistance_time: Optional[datetime] = None
    assistance_frequency: str = Field(...)

class HealthStatus(BaseModel):
    status: str = Field(...)
    service: str = Field(...)
    version: str = Field(...)
    timestamp: datetime = Field(...)
    components: Dict[str, Any] = Field(...)
    integrations: Dict[str, Any] = Field(...)

class IntegrationStatus(BaseModel):
    ai_event_processor: Dict[str, Any] = Field(...)
    ai_context_store: Dict[str, Any] = Field(...)
    cultural_intelligence: Dict[str, Any] = Field(...)
    overall_status: str = Field(...)
    last_check: datetime = Field(...)

class ServiceMetrics(BaseModel):
    timestamp: datetime = Field(...)
    service: str = Field(...)
    total_evaluations: int = Field(...)
    successful_evaluations: int = Field(...)
    average_response_time_ms: float = Field(...)
    cultural_adaptation_rate: float = Field(...)
    assistance_acceptance_rate: float = Field(...)
    error_rate: float = Field(...)
    performance_indicators: Dict[str, Any] = Field(...)
