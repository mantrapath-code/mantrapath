"""
E3 Achievement Database Schema - User Achievement Progress Table
Extends existing models with user-specific achievement tracking
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Float, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# Import the existing Base from shared models
from models import Base

class UserAchievementProgress(Base):
    """
    E3 Achievement & Engagement Cohesion - User Progress Tracking
    Tracks individual user progress on specific achievements with metadata
    """
    __tablename__ = "user_achievement_progress"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(String, nullable=False, index=True)  # Achievement definition ID
    
    # Progress tracking
    current_progress = Column(Integer, default=0)
    max_progress = Column(Integer, nullable=False)
    is_unlocked = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)
    
    # Achievement metadata
    achievement_title = Column(String, nullable=False)
    achievement_description = Column(Text)
    achievement_category = Column(String, nullable=False)  # getting-started, consistency, etc.
    achievement_level = Column(String, default="bronze")  # bronze, silver, gold, platinum
    achievement_icon = Column(String, default="🎯")
    
    # Progress metadata and tracking data
    progress_metadata = Column(JSON, default=dict)  # Streaks, patterns, etc.
    last_progress_update = Column(DateTime, default=datetime.utcnow)
    
    # Celebration integration
    celebration_triggered = Column(Boolean, default=False)
    celebration_moment_id = Column(String, ForeignKey("celebration_moments.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_achievement_lookup', 'user_id', 'achievement_id'),
        Index('idx_achievement_category', 'achievement_category', 'achievement_level'),
        Index('idx_user_unlocked', 'user_id', 'is_unlocked', 'unlocked_at'),
        Index('idx_progress_updates', 'user_id', 'last_progress_update'),
    )

class AchievementDefinitionCache(Base):
    """
    Cache table for achievement definitions to avoid recalculating
    Stores the canonical achievement definitions from the engine
    """
    __tablename__ = "achievement_definition_cache"
    
    id = Column(String, primary_key=True)  # Achievement ID
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    level = Column(String, default="bronze")
    max_progress = Column(Integer, default=1)
    icon = Column(String, default="🎯")
    criteria_function = Column(String)
    celebration_type = Column(String)
    
    # Cache management
    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_achievement_category_level', 'category', 'level'),
        Index('idx_active_achievements', 'is_active', 'category'),
    )

class UserAchievementEvent(Base):
    """
    Event log for achievement-related user actions
    Enables analytics and trigger pattern recognition
    """
    __tablename__ = "user_achievement_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(String, nullable=False)
    
    # Event details
    event_type = Column(String, nullable=False)  # progress_update, unlock, celebration_view
    event_data = Column(JSON, default=dict)  # Event-specific metadata
    trigger_source = Column(String)  # mood_entry, journal_entry, manual_check, etc.
    
    # Progress state at time of event
    progress_before = Column(Integer, default=0)
    progress_after = Column(Integer, default=0)
    was_unlocked_before = Column(Boolean, default=False)
    was_unlocked_after = Column(Boolean, default=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Indexes for analytics
    __table_args__ = (
        Index('idx_user_achievement_events', 'user_id', 'achievement_id', 'event_type'),
        Index('idx_event_timeline', 'user_id', 'created_at'),
        Index('idx_trigger_analysis', 'trigger_source', 'event_type'),
    )
