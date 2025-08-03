"""
Enhanced Community Models with Psychology-Based Design
Clean, organized models for community features
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from typing import Dict, List, Optional
from pydantic import BaseModel
from enum import Enum

import sys
sys.path.append('/app/shared')
from shared.models import Base


class CommunityHub(Base):
    """Unified community hub containing all community features"""
    __tablename__ = 'community_hubs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    hub_type = Column(String, nullable=False)  # 'support', 'discussion', 'wellness', 'crisis'
    color_theme = Column(String, default='calm_blue')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User references with String type
    created_by = Column(String, ForeignKey('users.id'), nullable=False)
    moderator_id = Column(String, ForeignKey('users.id'))
    
    # Psychology config
    psychological_focus = Column(JSON)  # ['anxiety', 'depression', 'stress', 'mindfulness']
    crisis_support_enabled = Column(Boolean, default=False)
    calming_features = Column(JSON)  # Configuration for calming UI elements
    
    # Relationships
    conversations = relationship("CommunityConversation", back_populates="hub")


class CommunityConversation(Base):
    """Community conversations/discussions"""
    __tablename__ = 'community_conversations'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    hub_id = Column(String, ForeignKey('community_hubs.id'), nullable=False)
    content = Column(Text, nullable=False)
    conversation_type = Column(String, default='discussion')  # 'discussion', 'support', 'question'
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User references with String type  
    author_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Psychology features
    mood_tags = Column(JSON)  # ['anxious', 'hopeful', 'stressed']
    trigger_warnings = Column(JSON)  # Content warnings
    calming_score = Column(Float, default=5.0)  # 1-10 scale for content calmness
    crisis_flagged = Column(Boolean, default=False)
    
    # Relationships
    hub = relationship("CommunityHub", back_populates="conversations")
    replies = relationship("ConversationReply", back_populates="conversation")


class ConversationReply(Base):
    """Replies to community conversations"""
    __tablename__ = 'conversation_replies'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey('community_conversations.id'), nullable=False)
    parent_reply_id = Column(String, ForeignKey('conversation_replies.id'))  # For nested replies
    content = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User references with String type
    author_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Psychology features
    supportive_score = Column(Float, default=5.0)  # How supportive/helpful the reply is
    calming_score = Column(Float, default=5.0)
    crisis_response = Column(Boolean, default=False)  # If this is a crisis intervention
    
    # Relationships
    conversation = relationship("CommunityConversation", back_populates="replies")
    parent_reply = relationship("ConversationReply", remote_side=[id])


class CommunityReaction(Base):
    """Reactions to conversations and replies"""
    __tablename__ = 'community_reactions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    conversation_id = Column(String, ForeignKey('community_conversations.id'))
    reply_id = Column(String, ForeignKey('conversation_replies.id'))
    reaction_type = Column(String, nullable=False)  # 'support', 'helpful', 'calming', 'heart'
    created_at = Column(DateTime, default=datetime.utcnow)


class CommunityContent(Base):
    """Shared community content (articles, resources, guided meditations)"""
    __tablename__ = 'community_content'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    hub_id = Column(String, ForeignKey('community_hubs.id'), nullable=False)
    content_type = Column(String, nullable=False)  # 'article', 'meditation', 'resource', 'exercise'
    content_id = Column(String)  # ID of the actual content
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User references with String type
    author_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Psychology features
    target_conditions = Column(JSON)  # ['anxiety', 'depression', 'stress']
    calming_level = Column(Integer, default=5)  # 1-10
    difficulty_level = Column(String, default='beginner')  # 'beginner', 'intermediate', 'advanced'
    estimated_duration = Column(Integer)  # minutes


class UserPsychologicalProfile(Base):
    """User's psychological preferences and progress"""
    __tablename__ = 'user_psychological_profiles'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Preferences
    preferred_color_theme = Column(String, default='calm_blue')
    comfort_level = Column(String, default='medium')  # 'low', 'medium', 'high'
    trigger_sensitivity = Column(JSON)  # List of topics to be sensitive about
    support_preferences = Column(JSON)  # How they like to receive support
    
    # Progress tracking
    community_engagement_score = Column(Float, default=0.0)
    supportiveness_rating = Column(Float, default=5.0)  # How supportive they are to others
    last_mood_check = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CommunityHubMembership(Base):
    """User membership in community hubs"""
    __tablename__ = 'community_hub_memberships'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    hub_id = Column(String, ForeignKey('community_hubs.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Membership details
    role = Column(String, default='member')  # 'member', 'moderator', 'admin'
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Psychology tracking
    engagement_score = Column(Float, default=0.0)
    contribution_rating = Column(Float, default=5.0)


class CommunityFeedItem(Base):
    """Feed items for personalized community content"""
    __tablename__ = 'community_feed_items'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    content_type = Column(String, nullable=False)  # 'conversation', 'event', 'resource'
    content_id = Column(String, nullable=False)
    hub_id = Column(String, ForeignKey('community_hubs.id'), nullable=False)
    
    # Relevance scoring
    psychological_relevance_score = Column(Float, default=5.0)
    engagement_prediction = Column(Float, default=5.0)
    calming_effect_rating = Column(Float, default=5.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    viewed_at = Column(DateTime)
    interacted_at = Column(DateTime)


# Pydantic models for API responses
class CommunityHubResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    hub_type: str
    color_theme: str
    psychological_focus: Optional[List[str]]
    crisis_support_enabled: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: str
    title: str
    content: str
    conversation_type: str
    is_anonymous: bool
    mood_tags: Optional[List[str]]
    calming_score: float
    crisis_flagged: bool
    created_at: datetime
    author_id: str
    hub_id: str
    
    class Config:
        from_attributes = True


class PsychologyTheme(BaseModel):
    """Psychology-based theme configuration"""
    primary_color: str
    accent_color: str
    background_color: str
    text_color: str
    mood_association: str
    calming_elements: Dict[str, str]


class MoodType(str, Enum):
    """Mood types for psychology-based features"""
    CALM = "calm"
    ANXIOUS = "anxious" 
    DEPRESSED = "depressed"
    HOPEFUL = "hopeful"
    STRESSED = "stressed"
    PEACEFUL = "peaceful"
    ENERGIZED = "energized"
    OVERWHELMED = "overwhelmed"


class CommunityCreateRequest(BaseModel):
    """Request model for creating community content"""
    title: str
    content: str
    hub_id: str
    conversation_type: str = "discussion"
    is_anonymous: bool = False
    mood_tags: Optional[List[str]] = None
    trigger_warnings: Optional[List[str]] = None


class CommunityHubCreate(BaseModel):
    """Request model for creating community hubs"""
    name: str
    description: Optional[str] = None
    hub_type: str = "public"
    psychological_focus: Optional[List[str]] = None
    crisis_support_enabled: bool = False
    color_theme: str = "calm_blue"


class ConversationCreate(BaseModel):
    """Request model for creating conversations"""
    title: str
    content: str
    hub_id: str
    conversation_type: str = "discussion"
    is_anonymous: bool = False
    mood_tags: Optional[List[str]] = None
    trigger_warnings: Optional[List[str]] = None


class PersonalizedFeedRequest(BaseModel):
    """Request model for personalized feed"""
    user_id: str
    mood_preferences: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    psychological_focus: Optional[List[str]] = None


class FeedItemResponse(BaseModel):
    """Response model for feed items"""
    content_type: str
    content_id: str
    community_hub_id: str
    title: str
    preview: str
    psychological_relevance_score: float
    calming_effect_rating: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class PsychologyAnalysisResult(BaseModel):
    """Result of psychology analysis"""
    calming_score: float
    mood_detected: Optional[str]
    crisis_detected: bool
    supportive_elements: List[str]
    recommendations: List[str]
    suggested_theme: str
