"""
AI Context Store Models
Defines data models for user context aggregation and storage
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from enum import Enum
import json
import uuid

class ContextType(str, Enum):
    """Types of context data"""
    MOOD = "mood"
    COMMUNITY = "community"
    VOICE = "voice"
    TRANSLATION = "translation"
    CONTENT = "content"
    NOTIFICATION = "notification"
    ML_INSIGHT = "ml_insight"

class ContextPriority(str, Enum):
    """Priority levels for context entries"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class ContextEntry(BaseModel):
    """Individual context entry from any service"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    context_type: ContextType
    source_service: str
    event_channel: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    priority: ContextPriority = ContextPriority.NORMAL
    
    # Raw event data
    raw_data: Dict[str, Any]
    
    # Processed/normalized data
    processed_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Context relationships
    related_entries: List[str] = Field(default_factory=list)
    
    # TTL for context entry (in seconds)
    ttl: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class MoodContext(BaseModel):
    """Mood-specific context data"""
    mood_score: float
    energy_level: float
    stress_level: Optional[float] = None
    sleep_quality: Optional[float] = None
    journal_sentiment: Optional[float] = None
    mood_trend: Optional[str] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CommunityContext(BaseModel):
    """Community engagement context"""
    engagement_level: str
    challenge_participation: List[str] = Field(default_factory=list)
    posts_created: int = 0
    interactions: int = 0
    social_score: float = 0.0
    preferred_topics: List[str] = Field(default_factory=list)
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VoiceContext(BaseModel):
    """Voice interaction context"""
    interaction_frequency: int = 0
    preferred_voice_commands: List[str] = Field(default_factory=list)
    speech_patterns: Dict[str, Any] = Field(default_factory=dict)
    intent_patterns: List[str] = Field(default_factory=list)
    voice_sentiment: Optional[float] = None
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TranslationContext(BaseModel):
    """Translation usage context"""
    source_languages: List[str] = Field(default_factory=list)
    target_languages: List[str] = Field(default_factory=list)
    translation_frequency: int = 0
    content_types: List[str] = Field(default_factory=list)
    cultural_preferences: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ContentContext(BaseModel):
    """Content consumption context"""
    content_preferences: List[str] = Field(default_factory=list)
    engagement_patterns: Dict[str, Any] = Field(default_factory=dict)
    recommendation_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    content_types: List[str] = Field(default_factory=list)
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class NotificationContext(BaseModel):
    """Notification interaction context"""
    delivery_preferences: Dict[str, Any] = Field(default_factory=dict)
    engagement_rates: Dict[str, float] = Field(default_factory=dict)
    optimal_timing: List[str] = Field(default_factory=list)
    notification_types: List[str] = Field(default_factory=list)
    response_patterns: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserContext(BaseModel):
    """Comprehensive user context aggregation"""
    user_id: str
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Context components
    mood_context: Optional[MoodContext] = None
    community_context: Optional[CommunityContext] = None
    voice_context: Optional[VoiceContext] = None
    translation_context: Optional[TranslationContext] = None
    content_context: Optional[ContentContext] = None
    notification_context: Optional[NotificationContext] = None
    
    # Aggregated insights
    user_profile: Dict[str, Any] = Field(default_factory=dict)
    behavioral_patterns: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    # Context health metrics
    context_completeness: float = 0.0
    last_activity: Optional[datetime] = None
    activity_score: float = 0.0
    
    # Context history summary
    context_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ContextAggregator(BaseModel):
    """Context aggregation configuration and rules"""
    aggregation_rules: Dict[str, Any] = Field(default_factory=dict)
    weight_configuration: Dict[str, float] = Field(default_factory=dict)
    time_windows: Dict[str, int] = Field(default_factory=dict)
    
    # Default weights for different context types
    def __init__(self, **data):
        super().__init__(**data)
        if not self.weight_configuration:
            self.weight_configuration = {
                "mood": 0.25,
                "community": 0.15,
                "voice": 0.15,
                "translation": 0.10,
                "content": 0.20,
                "notification": 0.15
            }
        
        if not self.time_windows:
            self.time_windows = {
                "recent": 3600,      # 1 hour
                "short_term": 86400, # 24 hours
                "medium_term": 604800, # 1 week
                "long_term": 2592000   # 30 days
            }

class ContextQuery(BaseModel):
    """Query model for context retrieval"""
    user_id: str
    context_types: Optional[List[ContextType]] = None
    time_range: Optional[Dict[str, datetime]] = None
    include_history: bool = False
    aggregation_level: str = "current"  # current, summary, detailed
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ContextUpdate(BaseModel):
    """Model for context updates from events"""
    user_id: str
    context_type: ContextType
    source_service: str
    event_channel: str
    data: Dict[str, Any]
    priority: ContextPriority = ContextPriority.NORMAL
    metadata: Dict[str, Any] = Field(default_factory=dict)

class IntelligenceInsight(BaseModel):
    """AI-generated insights from context analysis"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    insight_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    description: str
    recommendations: List[str] = Field(default_factory=list)
    supporting_data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Insight metadata
    expires_at: Optional[datetime] = None
    priority: ContextPriority = ContextPriority.NORMAL
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
