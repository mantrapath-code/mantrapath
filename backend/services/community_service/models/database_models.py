"""
Enhanced Database Models for Community Service
Clean, database-driven models without mock data
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, Boolean, Float, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import sys
sys.path.append('/app/shared')
from shared.models import Base

# Association tables for many-to-many relationships
challenge_participants = Table(
    'challenge_participants',
    Base.metadata,
    Column('challenge_id', String, ForeignKey('challenges.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('joined_at', DateTime, default=datetime.utcnow),
    extend_existing=True
)

event_participants = Table(
    'event_participants', 
    Base.metadata,
    Column('event_id', String, ForeignKey('community_events.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('joined_at', DateTime, default=datetime.utcnow),
    extend_existing=True
)

class Challenge(Base):
    """Community challenges with database persistence"""
    __tablename__ = 'challenges'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    duration_days = Column(Integer, default=30)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    created_by = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships (remove back_populates to avoid User model conflicts)
    progress_entries = relationship("ChallengeProgress", back_populates="challenge", cascade="all, delete-orphan")
    comments = relationship("ChallengeComment", back_populates="challenge", cascade="all, delete-orphan")

class ChallengeProgress(Base):
    """User progress tracking for challenges"""
    __tablename__ = 'challenge_progress'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String, ForeignKey('challenges.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)
    notes = Column(Text)
    reflection = Column(Text)
    mood_rating = Column(Integer)  # 1-5
    difficulty_rating = Column(Integer)  # 1-5
    streak_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    challenge = relationship("Challenge", back_populates="progress_entries")

class ChallengeComment(Base):
    """Comments on challenges with threading support"""
    __tablename__ = 'challenge_comments'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String, ForeignKey('challenges.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(String, ForeignKey('challenge_comments.id'))
    like_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    challenge = relationship("Challenge", back_populates="comments")
    replies = relationship("ChallengeComment", backref="parent", remote_side=[id])

class CommunityEvent(Base):
    """Community events with database persistence"""
    __tablename__ = 'community_events'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    event_type = Column(String, default='workshop')  # workshop, webinar, group_session, etc.
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    max_participants = Column(Integer)
    created_by = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    location = Column(String)  # online, physical address, etc.
    meeting_link = Column(String)
    
    # Relationships
    participants = relationship("User", secondary=event_participants, back_populates="joined_events")

class Forum(Base):
    """Community forums for discussions"""
    __tablename__ = 'forums'
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    color_theme = Column(String, default='calm_blue')
    psychological_focus = Column(JSON)  # list of focus areas
    created_by = Column(String, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    member_count = Column(Integer, default=0)
