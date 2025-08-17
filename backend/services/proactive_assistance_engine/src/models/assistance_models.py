"""
Data models for the Proactive Assistance Engine service.

This module defines the Pydantic models used for assistance evaluation,
timing analysis, cultural sensitivity, and help content.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

class AssistanceType(str, Enum):
    """Types of proactive assistance"""
    CRISIS_INTERVENTION = "crisis_intervention"
    PROACTIVE_SUPPORT = "proactive_support"
    GENTLE_CHECK_IN = "gentle_check_in"
    MOOD_SUPPORT = "mood_support"
    BEHAVIORAL_GUIDANCE = "behavioral_guidance"
    CULTURAL_ADAPTATION = "cultural_adaptation"

class UrgencyLevel(str, Enum):
    """Urgency levels for assistance"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

class CulturalProfile(BaseModel):
    """User cultural profile for assistance adaptation"""
    primary_culture: str = Field(..., description="Primary cultural background")
    communication_style: str = Field(..., description="Preferred communication style")
    family_involvement: Optional[bool] = Field(None, description="Whether to involve family")
    hierarchical_respect: Optional[bool] = Field(None, description="Respect for hierarchical relationships")
    indirect_communication: Optional[bool] = Field(None, description="Preference for indirect communication")

class TimingEvaluation(BaseModel):
    """Timing appropriateness evaluation"""
    timing_appropriate: bool = Field(..., description="Whether timing is appropriate for assistance")
    timing_confidence: float = Field(..., description="Confidence in timing evaluation (0.0-1.0)")
    can_proceed: bool = Field(..., description="Whether assistance can proceed")
    recommended_delay_minutes: int = Field(0, description="Recommended delay in minutes")
    recent_assistance_check: Dict[str, Any] = Field(..., description="Recent assistance gap analysis")
    activity_analysis: Dict[str, Any] = Field(..., description="Current activity state analysis")
    cultural_timing: Dict[str, Any] = Field(..., description="Cultural timing considerations")
    urgency_override: bool = Field(False, description="Whether urgency overrides timing restrictions")

class CulturalEvaluation(BaseModel):
    """Cultural appropriateness evaluation"""
    culturally_appropriate: bool = Field(..., description="Whether assistance is culturally appropriate")
    appropriateness_score: float = Field(..., description="Cultural appropriateness score (0.0-1.0)")
    content_evaluation: Dict[str, Any] = Field(..., description="Content appropriateness evaluation")
    timing_evaluation: Dict[str, Any] = Field(..., description="Timing appropriateness evaluation")
    adapted_content: Optional[Dict[str, Any]] = Field(None, description="Culturally adapted assistance content")
    cultural_considerations: List[str] = Field(..., description="Cultural considerations applied")

class InterventionAnalysis(BaseModel):
    """Analysis of intervention needs from AI Event Processor"""
    intervention_needed: bool = Field(..., description="Whether intervention is needed")
    confidence: float = Field(..., description="Confidence in intervention analysis (0.0-1.0)")
    intervention_type: Optional[AssistanceType] = Field(None, description="Type of intervention needed")
    urgency_level: UrgencyLevel = Field(..., description="Urgency level of intervention")
    recommended_actions: List[str] = Field(..., description="Recommended actions")
    risk_factors: Dict[str, Any] = Field(..., description="Identified risk factors")
    fallback_reason: Optional[str] = Field(None, description="Reason for fallback if service unavailable")

class AssistanceContent(BaseModel):
    """Proactive assistance content and actions"""
    content_id: str = Field(..., description="Unique identifier for assistance content")
    title: str = Field(..., description="Assistance title")
    content: str = Field(..., description="Main assistance message")
    actions: List[str] = Field(..., description="Recommended actions for user")
    urgency: UrgencyLevel = Field(..., description="Urgency level of assistance")
    cultural_adaptations: Dict[str, str] = Field(..., description="Cultural adaptations applied")
    confidence_score: float = Field(..., description="Confidence in content relevance (0.0-1.0)")

class AssistanceDecision(BaseModel):
    """Final assistance decision and reasoning"""
    should_provide_assistance: bool = Field(..., description="Whether to provide assistance")
    confidence: float = Field(..., description="Overall confidence in decision (0.0-1.0)")
    reasoning: List[str] = Field(..., description="Reasons for decision")
    assistance_type: Optional[AssistanceType] = Field(None, description="Type of assistance to provide")
    priority_score: float = Field(..., description="Priority score for assistance (0.0-1.0)")
    user_preferences_respected: bool = Field(..., description="Whether user preferences are respected")

class AssistanceEvaluation(BaseModel):
    """Complete assistance evaluation result"""
    user_id: str = Field(..., description="User identifier")
    evaluation_timestamp: datetime = Field(..., description="When evaluation was performed")
    intervention_analysis: InterventionAnalysis = Field(..., description="AI intervention analysis")
    timing_evaluation: TimingEvaluation = Field(..., description="Timing appropriateness evaluation")
    cultural_evaluation: CulturalEvaluation = Field(..., description="Cultural appropriateness evaluation")
    assistance_decision: AssistanceDecision = Field(..., description="Final assistance decision")
    assistance_content: Optional[AssistanceContent] = Field(..., description="Assistance content if needed")
    confidence_score: float = Field(..., description="Overall confidence score (0.0-1.0)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class UserAssistanceNeeds(BaseModel):
    """User's current assistance needs and preferences"""
    user_id: str = Field(..., description="User identifier")
    current_needs: List[AssistanceType] = Field(..., description="Current assistance needs")
    assistance_preferences: Dict[str, Any] = Field(..., description="User assistance preferences")
    cultural_profile: CulturalProfile = Field(..., description="User cultural profile")
    assistance_history: List[Dict[str, Any]] = Field(..., description="Recent assistance history")
    last_assistance_time: Optional[datetime] = Field(None, description="Last assistance provided")
    assistance_frequency: str = Field(..., description="Preferred assistance frequency")

class HealthStatus(BaseModel):
    """Service health status"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(..., description="Health check timestamp")
    components: Dict[str, Any] = Field(..., description="Component health status")
    integrations: Dict[str, Any] = Field(..., description="Integration service status")

class IntegrationStatus(BaseModel):
    """Integration service status"""
    ai_event_processor: Dict[str, Any] = Field(..., description="AI Event Processor status")
    ai_context_store: Dict[str, Any] = Field(..., description="AI Context Store status")
    cultural_intelligence: Dict[str, Any] = Field(..., description="Cultural Intelligence status")
    overall_status: str = Field(..., description="Overall integration status")
    last_check: datetime = Field(..., description="Last integration check")

class ServiceMetrics(BaseModel):
    """Service performance metrics"""
    timestamp: datetime = Field(..., description="Metrics timestamp")
    service: str = Field(..., description="Service name")
    total_evaluations: int = Field(..., description="Total assistance evaluations")
    successful_evaluations: int = Field(..., description="Successful evaluations")
    average_response_time_ms: float = Field(..., description="Average response time in milliseconds")
    cultural_adaptation_rate: float = Field(..., description="Rate of cultural adaptations applied")
    assistance_acceptance_rate: float = Field(..., description="Rate of assistance acceptance")
    error_rate: float = Field(..., description="Error rate")
    performance_indicators: Dict[str, Any] = Field(..., description="Additional performance indicators")
