"""
Memory Service Database Models
Defines the database schema for user interactions, mood patterns, and behavioral insights
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from datetime import datetime, timezone
import uuid

from shared.models import Base

class UserInteraction(Base):
    """
    Stores all user interactions across the platform
    Enables comprehensive behavior tracking and pattern analysis
    """
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(100), nullable=False, index=True)  # mood, journal, chat, community, voice
    interaction_data = Column(JSONB, nullable=False)
    cultural_context = Column(JSONB, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    interaction_metadata = Column(JSONB, nullable=True)
    
    # Source information
    source_service = Column(String(100), nullable=False, index=True)  # mood_service, chatbot_service, etc.
    session_id = Column(String(255), nullable=True, index=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    platform = Column(String(50), nullable=True)  # web, ios, android
    
    # Performance and analytics
    processing_time_ms = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    
    # Soft delete support
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Indexes for performance
    __table_args__ = (
        Index('idx_user_interactions_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_user_interactions_type_timestamp', 'interaction_type', 'timestamp'),
        Index('idx_user_interactions_source_timestamp', 'source_service', 'timestamp'),
        Index('idx_user_interactions_session', 'session_id', 'timestamp'),
        Index('idx_user_interactions_cultural', 'user_id', 'cultural_context'),
    )

class MoodPattern(Base):
    """
    Stores aggregated mood patterns and analysis results
    Enables pattern recognition and trend analysis
    """
    __tablename__ = "mood_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    pattern_type = Column(String(100), nullable=False, index=True)  # daily, weekly, monthly, seasonal
    pattern_data = Column(JSONB, nullable=False)
    
    # Pattern characteristics
    confidence_score = Column(Float, nullable=False, default=0.0)
    frequency = Column(String(50), nullable=True)  # daily, weekly, monthly
    intensity = Column(Float, nullable=True)  # 0.0 to 1.0
    stability = Column(Float, nullable=True)  # how stable the pattern is
    
    # Time range
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Cultural and contextual information
    cultural_context = Column(JSONB, nullable=True)
    environmental_factors = Column(JSONB, nullable=True)
    triggers = Column(JSONB, nullable=True)
    
    # Analysis metadata
    analysis_version = Column(String(20), nullable=True)  # track algorithm versions
    sample_size = Column(Integer, nullable=True)  # number of interactions analyzed
    
    # Soft delete support
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index('idx_mood_patterns_user_type', 'user_id', 'pattern_type'),
        Index('idx_mood_patterns_date_range', 'start_date', 'end_date'),
        Index('idx_mood_patterns_confidence', 'confidence_score'),
        Index('idx_mood_patterns_active', 'is_active', 'is_deleted'),
    )

class BehavioralInsight(Base):
    """
    Stores generated behavioral insights and recommendations
    Enables personalized recommendations and interventions
    """
    __tablename__ = "behavioral_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False, index=True)  # recommendation, warning, trend, achievement
    insight_data = Column(JSONB, nullable=False)
    
    # Insight characteristics
    accuracy_score = Column(Float, nullable=False, default=0.0)
    relevance_score = Column(Float, nullable=False, default=0.0)
    urgency_level = Column(String(20), nullable=False, default='low')  # low, medium, high, critical
    priority = Column(Integer, nullable=False, default=1)  # 1-10 scale
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    action_items = Column(JSONB, nullable=True)
    
    # Timing and context
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Cultural and personalization
    cultural_context = Column(JSONB, nullable=True)
    personalization_factors = Column(JSONB, nullable=True)
    delivery_channels = Column(JSONB, nullable=True)  # preferred delivery methods
    
    # Feedback and effectiveness
    user_feedback = Column(JSONB, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    follow_up_required = Column(Boolean, default=False, nullable=False)
    
    # Source tracking
    source_patterns = Column(JSONB, nullable=True)  # which patterns led to this insight
    source_interactions = Column(JSONB, nullable=True)  # which interactions contributed
    algorithm_version = Column(String(20), nullable=True)
    
    # State management
    status = Column(String(50), nullable=False, default='generated')  # generated, delivered, acknowledged, expired
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index('idx_behavioral_insights_user_type', 'user_id', 'insight_type'),
        Index('idx_behavioral_insights_urgency', 'urgency_level', 'priority'),
        Index('idx_behavioral_insights_timing', 'generated_at', 'expires_at'),
        Index('idx_behavioral_insights_status', 'status', 'is_active'),
        Index('idx_behavioral_insights_delivery', 'delivered_at', 'acknowledged_at'),
    )

class MemorySession(Base):
    """
    Tracks user sessions for better context understanding
    Enables session-based analysis and recommendations
    """
    __tablename__ = "memory_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Session characteristics
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True, index=True)
    duration_seconds = Column(Integer, nullable=True)
    interaction_count = Column(Integer, default=0, nullable=False)
    
    # Context
    device_type = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    location_data = Column(JSONB, nullable=True)
    
    # Session analysis
    mood_trend = Column(JSONB, nullable=True)
    activity_summary = Column(JSONB, nullable=True)
    engagement_score = Column(Float, nullable=True)
    session_quality = Column(String(20), nullable=True)  # high, medium, low
    
    # Cultural context
    cultural_context = Column(JSONB, nullable=True)
    language_preference = Column(String(10), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # State
    is_active = Column(Boolean, default=True, nullable=False)
    closed_reason = Column(String(100), nullable=True)  # timeout, logout, error, etc.

    # Indexes for performance
    __table_args__ = (
        Index('idx_memory_sessions_user_time', 'user_id', 'start_time'),
        Index('idx_memory_sessions_active', 'is_active', 'end_time'),
        Index('idx_memory_sessions_duration', 'duration_seconds'),
    )

class MemoryAggregation(Base):
    """
    Stores pre-computed aggregations for performance
    Enables fast retrieval of user statistics and trends
    """
    __tablename__ = "memory_aggregations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    aggregation_type = Column(String(100), nullable=False, index=True)  # daily, weekly, monthly
    aggregation_key = Column(String(255), nullable=False, index=True)  # specific aggregation identifier
    
    # Aggregated data
    aggregation_data = Column(JSONB, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    sum_value = Column(Float, nullable=True)
    avg_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    
    # Time range
    period_start = Column(DateTime(timezone=True), nullable=False, index=True)
    period_end = Column(DateTime(timezone=True), nullable=False, index=True)
    computed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Metadata
    computation_version = Column(String(20), nullable=True)
    source_count = Column(Integer, nullable=True)  # number of source records
    confidence_score = Column(Float, nullable=True)
    
    # State
    is_current = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Indexes for performance
    __table_args__ = (
        Index('idx_memory_aggregations_user_type_key', 'user_id', 'aggregation_type', 'aggregation_key'),
        Index('idx_memory_aggregations_period', 'period_start', 'period_end'),
        Index('idx_memory_aggregations_current', 'is_current', 'is_deleted'),
    )
