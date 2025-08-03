"""
Enhanced Community Models with Psychology-Based Design
Implements calming colors, unified community management, and personalized feeds
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum

# Psychology-based color system
class WellnessColors:
    """Color psychology mapping for mental wellness"""
    
    CALM_PALETTE = {
        "calm_blue": "#4A90E2",      # Trust, stability, peace
        "sage_green": "#87A96B",     # Growth, harmony, balance  
        "soft_purple": "#9B8CE8",    # Creativity, mindfulness
        "warm_beige": "#F5F1E8",     # Comfort, grounding
        "gentle_teal": "#5DADE2",    # Clarity, refreshing
        "sunset_orange": "#F39C12",  # Warmth, optimism (used sparingly)
        "forest_green": "#27AE60",   # Nature, healing
        "lavender": "#BB8FCE",       # Relaxation, tranquility
        "soft_pink": "#F8BBD9",      # Nurturing, compassion
        "warm_yellow": "#F7DC6F"     # Hope, gentle energy
    }
    
    MOOD_MAPPINGS = {
        "anxious": ["calm_blue", "sage_green", "lavender"],
        "depressed": ["warm_beige", "sunset_orange", "gentle_teal"],
        "stressed": ["forest_green", "soft_purple", "calm_blue"],
        "overwhelmed": ["lavender", "warm_beige", "sage_green"],
        "lonely": ["soft_pink", "warm_yellow", "gentle_teal"],
        "happy": ["gentle_teal", "sage_green", "sunset_orange"],
        "peaceful": ["sage_green", "lavender", "calm_blue"],
        "hopeful": ["warm_yellow", "forest_green", "gentle_teal"],
        "neutral": ["calm_blue", "sage_green", "warm_beige"]
    }
    
    @classmethod
    def get_mood_colors(cls, mood: str) -> List[str]:
        """Get calming colors for specific mood"""
        return cls.MOOD_MAPPINGS.get(mood.lower(), cls.MOOD_MAPPINGS["neutral"])
    
    @classmethod
    def get_calming_score(cls, colors: List[str]) -> float:
        """Calculate psychological calming score for color combination"""
        calming_weights = {
            "calm_blue": 0.9, "sage_green": 0.85, "lavender": 0.9,
            "warm_beige": 0.8, "gentle_teal": 0.75, "soft_purple": 0.8,
            "forest_green": 0.85, "soft_pink": 0.75, "warm_yellow": 0.7,
            "sunset_orange": 0.6  # Less calming, use sparingly
        }
        if not colors:
            return 0.5
        return sum(calming_weights.get(color, 0.5) for color in colors) / len(colors)

class PsychologicalFocus(str, Enum):
    """Community psychological focus areas"""
    ANXIETY_SUPPORT = "anxiety_support"
    DEPRESSION_HELP = "depression_help" 
    STRESS_MANAGEMENT = "stress_management"
    MINDFULNESS = "mindfulness"
    GRIEF_SUPPORT = "grief_support"
    ADDICTION_RECOVERY = "addiction_recovery"
    RELATIONSHIP_WELLNESS = "relationship_wellness"
    WORKPLACE_WELLNESS = "workplace_wellness"
    PARENTING_SUPPORT = "parenting_support"
    GENERAL_WELLNESS = "general_wellness"

class CommunityHubType(str, Enum):
    """Types of community hubs"""
    PUBLIC = "public"
    PRIVATE = "private"
    INTEREST_BASED = "interest_based"
    LOCATION_BASED = "location_based"
    SUPPORT_GROUP = "support_group"
    PROFESSIONAL_LED = "professional_led"

# Pydantic models for API
class CommunityThemeConfig(BaseModel):
    """Psychology-based theme configuration"""
    primary_colors: List[str]
    mood_responsive: bool = True
    calming_score: float
    psychological_focus: str
    time_based_adjustment: bool = True
    stress_response_colors: List[str]
    
class PersonalizedFeedPreferences(BaseModel):
    """User preferences for personalized community feed"""
    psychological_profile: Dict[str, float]  # mood tendencies, stress levels, etc.
    interaction_patterns: Dict[str, int]     # engagement with different content types
    wellness_goals: List[str]
    calming_preferences: Dict[str, float]    # preference for different calming strategies
    content_type_weights: Dict[str, float]   # weights for forums, challenges, events
    community_interests: List[str]
    notification_preferences: Dict[str, bool]

class FeedItem(BaseModel):
    """Individual item in personalized community feed"""
    id: str
    content_type: str  # "forum_post", "challenge_update", "event", "conversation", "resource"
    content_id: str
    community_hub_id: str
    title: str
    preview: str
    author: Dict[str, str]
    created_at: datetime
    psychological_relevance_score: float
    engagement_prediction: float
    calming_effect_rating: float
    interaction_count: int
    urgency_level: str  # "low", "medium", "high", "crisis"
    wellness_tags: List[str]

class CommunityRecommendation(BaseModel):
    """Community recommendation based on psychological profile"""
    community_hub_id: str
    name: str
    psychological_match_score: float
    description: str
    member_count: int
    activity_level: str
    wellness_focus: str
    recommended_reason: str
    calming_score: float
    support_quality_rating: float

class CalmingInteraction(BaseModel):
    """Framework for psychologically supportive interactions"""
    interaction_type: str
    calming_score: float
    recommended_colors: List[str]
    suggested_tone: str
    breathing_prompt: Optional[str] = None
    mindfulness_tip: Optional[str] = None
    supportive_language_suggestions: List[str]
    crisis_escalation_threshold: float

class ConversationStream(BaseModel):
    """Unified conversation management"""
    community_hub_id: str
    conversation_threads: List[Dict]
    psychological_tone: str
    support_level: str
    moderation_flags: List[str]
    wellness_check_prompts: List[str]
    calming_interventions: List[Dict]

class WellnessResource(BaseModel):
    """Community wellness resources"""
    id: str
    title: str
    content_type: str  # "article", "video", "audio", "exercise", "technique"
    psychological_benefits: List[str]
    calming_rating: float
    difficulty_level: str
    estimated_time: int  # minutes
    crisis_appropriate: bool
    accessibility_features: List[str]

class CommunityAnalytics(BaseModel):
    """Psychology-aware community analytics"""
    community_hub_id: str
    wellness_score_trend: List[float]
    emotional_climate: Dict[str, float]  # mood distribution
    support_effectiveness: float
    crisis_intervention_count: int
    calming_interaction_ratio: float
    member_retention_rate: float
    psychological_safety_score: float

# Response models for API
class CommunityHubResponse(BaseModel):
    """Response model for community hub data"""
    id: str
    name: str
    description: str
    hub_type: str
    psychological_focus: str
    member_count: int
    activity_level: str
    wellness_score: float
    calming_score: float
    theme_config: CommunityThemeConfig
    recent_activity: List[FeedItem]
    support_quality_rating: float
    crisis_support_available: bool
    
class PersonalizedFeedResponse(BaseModel):
    """Response model for personalized community feed"""
    user_id: str
    feed_items: List[FeedItem]
    psychological_wellness_tips: List[str]
    calming_suggestions: List[str]
    community_recommendations: List[CommunityRecommendation]
    crisis_resources: List[WellnessResource]
    mood_check_prompt: Optional[str] = None

class CommunityDashboardResponse(BaseModel):
    """Mood-responsive community dashboard"""
    user_mood_context: str
    recommended_colors: List[str]
    calming_score: float
    active_communities: List[CommunityHubResponse]
    suggested_interactions: List[CalmingInteraction]
    wellness_goals_progress: Dict[str, float]
    support_network_status: Dict[str, int]
    crisis_support_access: Dict[str, str]

# Request models
class CreateCommunityHubRequest(BaseModel):
    """Request to create new community hub"""
    name: str
    description: str
    hub_type: CommunityHubType
    psychological_focus: PsychologicalFocus
    privacy_level: str = "public"
    theme_preferences: Optional[CommunityThemeConfig] = None
    initial_resources: Optional[List[str]] = None

class FeedRequest(BaseModel):
    """Request for personalized community feed"""
    user_id: str
    mood_context: Optional[str] = None
    time_of_day: Optional[str] = None
    stress_level: Optional[float] = None
    content_preferences: Optional[Dict[str, float]] = None
    limit: int = 20

class CommunityJoinRequest(BaseModel):
    """Request to join community with psychological consideration"""
    user_id: str
    community_hub_id: str
    join_reason: str
    wellness_goals: List[str]
    support_needs: List[str]
    privacy_preferences: Dict[str, bool]

# Utility functions for psychological support
class CommunityPsychologyUtils:
    """Utility functions for psychology-based community features"""
    
    @staticmethod
    def calculate_psychological_match(user_profile: Dict, community_focus: str) -> float:
        """Calculate psychological compatibility between user and community"""
        # Implementation would use ML/AI for sophisticated matching
        # For now, simple rule-based matching
        focus_weights = {
            "anxiety_support": user_profile.get("anxiety_level", 0.5),
            "depression_help": user_profile.get("depression_indicators", 0.5),
            "stress_management": user_profile.get("stress_level", 0.5),
            "mindfulness": user_profile.get("mindfulness_interest", 0.5),
        }
        return focus_weights.get(community_focus, 0.5)
    
    @staticmethod
    def get_crisis_intervention_resources(severity_level: str) -> List[WellnessResource]:
        """Get appropriate crisis intervention resources"""
        # Would return actual crisis resources based on severity
        return []
    
    @staticmethod
    def generate_calming_suggestions(mood: str, stress_level: float) -> List[str]:
        """Generate personalized calming suggestions"""
        suggestions = []
        
        if stress_level > 0.7:
            suggestions.extend([
                "Take 5 deep breaths using the 4-7-8 technique",
                "Try a quick 2-minute grounding exercise",
                "Listen to calming nature sounds"
            ])
        
        if mood in ["anxious", "overwhelmed"]:
            suggestions.extend([
                "Focus on what you can control right now",
                "Practice progressive muscle relaxation",
                "Connect with a supportive community member"
            ])
        
        return suggestions
