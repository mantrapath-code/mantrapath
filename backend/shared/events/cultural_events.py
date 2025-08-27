"""
Cultural Intelligence and Regional Event Schemas
Supporting cultural context adaptation and regional intelligence processing.

Multilingual Support:
- Full Unicode support for all cultural text data
- Regional adaptation rules for different cultures
- Multi-regional pattern detection and analysis
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
import uuid


class CulturalEventType(str, Enum):
    """Cultural context event types"""
    # Cultural Detection
    CONTEXT_DETECTED = "cultural.context_detected"
    PREFERENCE_UPDATED = "cultural.preference_updated"
    ADAPTATION_APPLIED = "cultural.adaptation_applied"
    
    # Cultural Learning
    PATTERN_LEARNED = "cultural.pattern_learned"
    RULE_UPDATED = "cultural.rule_updated"
    FEEDBACK_RECEIVED = "cultural.feedback_received"
    
    # Cultural Conflicts
    CONFLICT_DETECTED = "cultural.conflict_detected"
    ADAPTATION_FAILED = "cultural.adaptation_failed"
    FALLBACK_APPLIED = "cultural.fallback_applied"


class RegionalEventType(str, Enum):
    """Regional intelligence event types"""
    # Regional Analysis
    TREND_DETECTED = "regional.trend_detected"
    PATTERN_IDENTIFIED = "regional.pattern_identified"
    RECOMMENDATION_GENERATED = "regional.recommendation_generated"
    
    # Regional Learning
    BEHAVIOR_LEARNED = "regional.behavior_learned"
    PREFERENCE_MAPPED = "regional.preference_mapped"
    CORRELATION_FOUND = "regional.correlation_found"
    
    # Regional Alerts
    ANOMALY_DETECTED = "regional.anomaly_detected"
    THRESHOLD_EXCEEDED = "regional.threshold_exceeded"
    SHIFT_DETECTED = "regional.shift_detected"


class CulturalDimensions(BaseModel):
    """Hofstede's cultural dimensions model"""
    power_distance: float = Field(..., ge=0.0, le=100.0, description="Power distance index")
    individualism: float = Field(..., ge=0.0, le=100.0, description="Individualism vs collectivism")
    uncertainty_avoidance: float = Field(..., ge=0.0, le=100.0, description="Uncertainty avoidance index")
    long_term_orientation: float = Field(..., ge=0.0, le=100.0, description="Long-term vs short-term orientation")
    masculinity: Optional[float] = Field(None, ge=0.0, le=100.0, description="Masculinity vs femininity")
    indulgence: Optional[float] = Field(None, ge=0.0, le=100.0, description="Indulgence vs restraint")


class CulturalData(BaseModel):
    """Cultural context data"""
    # Basic Cultural Information
    region: str = Field(..., description="Cultural region code (ISO 3166-1)")
    language: str = Field(..., description="Primary language (ISO 639-1)")
    country: Optional[str] = Field(None, description="Country code")
    
    # Cultural Dimensions
    cultural_dimensions: CulturalDimensions = Field(..., description="Cultural dimension scores")
    
    # Language-Specific Context
    dialect: Optional[str] = Field(None, description="Specific dialect or variant")
    script_direction: str = Field(default="ltr", description="Text direction (ltr, rtl)")
    number_format: Optional[str] = Field(None, description="Number formatting preference")
    date_format: Optional[str] = Field(None, description="Date formatting preference")
    
    # Communication Style
    communication_style: Dict[str, Any] = Field(
        default_factory=dict,
        description="Communication style preferences"
    )
    
    # Religious and Social Context
    religious_considerations: List[str] = Field(
        default_factory=list,
        description="Religious or cultural considerations"
    )
    
    social_norms: Dict[str, Any] = Field(
        default_factory=dict,
        description="Social norms and expectations"
    )


class AdaptationMetadata(BaseModel):
    """Cultural adaptation metadata"""
    # UI Adaptations
    ui_adaptations: Dict[str, Any] = Field(
        default_factory=dict,
        description="User interface adaptations applied"
    )
    
    # Content Adaptations
    content_adaptations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Content adaptations applied"
    )
    
    # Interaction Style
    interaction_style: str = Field(
        default="neutral",
        description="Adapted interaction style (formal, casual, respectful, etc.)"
    )
    
    # Language Adaptations
    language_adaptations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Language-specific adaptations"
    )
    
    # Visual Adaptations
    visual_adaptations: Dict[str, Any] = Field(
        default_factory=dict,
        description="Visual and design adaptations"
    )


class ProcessingInfo(BaseModel):
    """Cultural processing information"""
    detection_confidence: float = Field(..., ge=0.0, le=1.0, description="Cultural detection confidence")
    
    adaptation_rules_applied: List[str] = Field(
        default_factory=list,
        description="List of adaptation rules applied"
    )
    
    fallback_used: bool = Field(default=False, description="Whether fallback cultural rules were used")
    
    processing_time_ms: int = Field(default=0, ge=0, description="Cultural processing time")
    
    # Quality Metrics
    adaptation_quality_score: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Quality score of cultural adaptation"
    )
    
    # Warning and Errors
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
    cultural_conflicts: List[str] = Field(default_factory=list, description="Detected cultural conflicts")


class CulturalContextEvent(BaseModel):
    """Cultural context detection and adaptation event"""
    
    # Core Event Data
    event_type: CulturalEventType = Field(..., description="Type of cultural event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    
    # Cultural Data
    cultural_data: CulturalData = Field(..., description="Cultural context data")
    adaptation_metadata: AdaptationMetadata = Field(..., description="Adaptation metadata")
    processing_info: ProcessingInfo = Field(..., description="Processing information")
    
    # Context
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    service_name: str = Field(..., description="Service detecting/applying cultural context")
    
    # Source Information
    detection_source: str = Field(
        default="auto",
        description="Source of cultural detection (auto, manual, learned, etc.)"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    @validator('cultural_data')
    def validate_cultural_data(cls, v: CulturalData) -> CulturalData:
        """Validate cultural data consistency"""
        # Validate region and language compatibility
        if v.region and v.language:
            # Add validation logic for region-language compatibility
            pass
        return v


class RegionalData(BaseModel):
    """Regional intelligence data"""
    region_code: str = Field(..., description="Region identifier")
    trend_type: str = Field(..., description="Type of trend or pattern")
    pattern_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of detected pattern")
    
    # Trend Data
    recommendation_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Generated recommendations based on regional data"
    )
    
    # Statistical Information
    sample_size: int = Field(..., ge=1, description="Sample size for analysis")
    time_period: str = Field(..., description="Time period for analysis")
    statistical_confidence: float = Field(..., ge=0.0, le=1.0, description="Statistical confidence level")
    
    # Trend Details
    trend_direction: Optional[str] = Field(None, description="Trend direction (up, down, stable)")
    trend_velocity: Optional[float] = Field(None, description="Rate of change")
    seasonal_factors: List[str] = Field(default_factory=list, description="Seasonal factors affecting trend")
    
    # Comparative Analysis
    regional_comparisons: Dict[str, Any] = Field(
        default_factory=dict,
        description="Comparisons with other regions"
    )
    
    # Cultural Factors
    cultural_influences: List[str] = Field(
        default_factory=list,
        description="Cultural factors influencing regional patterns"
    )


class RegionalIntelligenceEvent(BaseModel):
    """Regional intelligence and pattern detection event"""
    
    # Core Event Data
    event_type: RegionalEventType = Field(..., description="Type of regional event")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique event ID")
    
    # Regional Data
    regional_data: RegionalData = Field(..., description="Regional intelligence data")
    
    # Analysis Metadata
    analysis_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Analysis methodology and metadata"
    )
    
    # Context
    service_name: str = Field(..., description="Service generating regional intelligence")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used in analysis")
    
    # Quality and Reliability
    reliability_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Reliability of intelligence")
    data_freshness: str = Field(default="current", description="Freshness of data used")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
    @validator('regional_data')
    def validate_regional_data(cls, v: RegionalData) -> RegionalData:
        """Validate regional data quality"""
        if v.statistical_confidence < 0.7:
            # Low statistical confidence - should be flagged
            pass
        return v


# Helper Functions for Event Creation

def create_cultural_context_event(
    event_type: CulturalEventType,
    region: str,
    language: str,
    cultural_dimensions: CulturalDimensions,
    service_name: str,
    detection_confidence: float,
    user_id: Optional[str] = None,
    **kwargs: Any
) -> CulturalContextEvent:
    """Create a cultural context event with default values"""
    
    cultural_data = CulturalData(
        region=region,
        language=language,
        cultural_dimensions=cultural_dimensions
    )
    
    adaptation_metadata = AdaptationMetadata()
    
    processing_info = ProcessingInfo(
        detection_confidence=detection_confidence
    )
    
    return CulturalContextEvent(
        event_type=event_type,
        cultural_data=cultural_data,
        adaptation_metadata=adaptation_metadata,
        processing_info=processing_info,
        service_name=service_name,
        user_id=user_id,
        **kwargs
    )


def create_regional_intelligence_event(
    event_type: RegionalEventType,
    region_code: str,
    trend_type: str,
    pattern_strength: float,
    sample_size: int,
    time_period: str,
    statistical_confidence: float,
    service_name: str,
    **kwargs: Any
) -> RegionalIntelligenceEvent:
    """Create a regional intelligence event"""
    
    regional_data = RegionalData(
        region_code=region_code,
        trend_type=trend_type,
        pattern_strength=pattern_strength,
        sample_size=sample_size,
        time_period=time_period,
        statistical_confidence=statistical_confidence
    )
    
    return RegionalIntelligenceEvent(
        event_type=event_type,
        regional_data=regional_data,
        service_name=service_name,
        **kwargs
    )


# Event Validation Functions

def validate_cultural_event_schema(event_data: Dict[str, Any], event_type: str) -> bool:
    """Validate cultural event data against schema"""
    try:
        if "cultural." in event_type:
            CulturalContextEvent(**event_data)
        elif "regional." in event_type:
            RegionalIntelligenceEvent(**event_data)
        else:
            return False
        return True
    except Exception:
        return False


# Cultural Rule Engine Support

CULTURAL_RULES = {
    "US": {
        "formality": "medium",
        "directness": "high",
        "time_sensitivity": "high",
        "personal_space": "medium",
        "communication_style": "direct"
    },
    "JP": {
        "formality": "high",
        "directness": "low",
        "time_sensitivity": "high",
        "personal_space": "high",
        "communication_style": "indirect"
    },
    "DE": {
        "formality": "medium",
        "directness": "very_high",
        "time_sensitivity": "very_high",
        "personal_space": "high",
        "communication_style": "very_direct"
    },
    "BR": {
        "formality": "low",
        "directness": "medium",
        "time_sensitivity": "low",
        "personal_space": "low",
        "communication_style": "warm"
    },
    "IN": {
        "formality": "high",
        "directness": "low",
        "time_sensitivity": "medium",
        "personal_space": "medium",
        "communication_style": "respectful"
    }
}


def get_cultural_rules(region: str) -> Dict[str, str]:
    """Get cultural adaptation rules for a region"""
    return CULTURAL_RULES.get(region, CULTURAL_RULES["US"])  # Default to US


def apply_cultural_adaptation(content: str, region: str, adaptation_type: str) -> str:
    """Apply cultural adaptation to content"""
    rules = get_cultural_rules(region)
    
    # This is a simplified example - real implementation would be more sophisticated
    if adaptation_type == "formality":
        if rules["formality"] == "high":
            # Apply formal language adaptations
            content = content.replace("Hi", "Dear")
            content = content.replace("Thanks", "Thank you")
        elif rules["formality"] == "low":
            # Apply casual language adaptations
            content = content.replace("Dear", "Hi")
            content = content.replace("Thank you", "Thanks")
    
    return content


# Regional Pattern Detection

REGIONAL_PATTERNS = {
    "mood_trends": {
        "US": {"seasonal_sad": 0.15, "holiday_stress": 0.25},
        "JP": {"work_stress": 0.35, "seasonal_factors": 0.20},
        "DE": {"efficiency_focus": 0.30, "winter_blues": 0.20},
        "BR": {"social_energy": 0.40, "carnival_effect": 0.15},
        "IN": {"festival_cycles": 0.25, "monsoon_mood": 0.20}
    },
    "interaction_preferences": {
        "US": {"voice_adoption": 0.65, "direct_commands": 0.70},
        "JP": {"polite_interactions": 0.85, "formal_requests": 0.75},
        "DE": {"efficiency_preference": 0.80, "precise_instructions": 0.75},
        "BR": {"conversational_style": 0.75, "emotional_expression": 0.80},
        "IN": {"multilingual_switching": 0.60, "respectful_tone": 0.85}
    }
}


def get_regional_patterns(region: str, pattern_type: str) -> Dict[str, float]:
    """Get regional patterns for analysis"""
    return REGIONAL_PATTERNS.get(pattern_type, {}).get(region, {})


def detect_regional_anomaly(current_metrics: Dict[str, float], region: str, pattern_type: str) -> List[str]:
    """Detect anomalies in regional patterns"""
    expected_patterns = get_regional_patterns(region, pattern_type)
    anomalies = []
    
    for metric, current_value in current_metrics.items():
        expected_value = expected_patterns.get(metric, 0.5)  # Default to 50%
        deviation = abs(current_value - expected_value)
        
        if deviation > 0.3:  # 30% deviation threshold
            anomalies.append(f"{metric}_deviation")
    
    return anomalies
