"""
Database models for MantraPath
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, default="")
    last_name = Column(String, default="")
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # user, moderator, admin
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    mood_entries = relationship("MoodEntry", back_populates="user")
    journal_entries = relationship("JournalEntry", back_populates="user")
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base):
    """User profile and preferences"""
    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    avatar_url = Column(String)
    bio = Column(Text)
    timezone = Column(String, default="UTC")
    
    # Preferences
    notifications_enabled = Column(Boolean, default=True)
    daily_reminder_enabled = Column(Boolean, default=True)
    daily_reminder_time = Column(String, default="20:00")  # HH:MM format
    weekly_report_enabled = Column(Boolean, default=True)
    theme_preference = Column(String, default="default")
    privacy_mode = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")

class MoodEntry(Base):
    """Mood tracking entries"""
    __tablename__ = "mood_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-5 scale
    energy_level = Column(Integer, default=3)  # 1-5 scale
    stress_level = Column(Integer, default=3)  # 1-5 scale
    sleep_quality = Column(Integer, default=3)  # 1-5 scale
    notes = Column(Text)
    context_tags = Column(JSON, default=list)  # ["work", "family", etc.]
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="mood_entries")

class JournalEntry(Base):
    """Journal entries"""
    __tablename__ = "journal_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    content = Column(Text, nullable=False)
    mood_before = Column(Integer)  # 1-5 scale
    mood_after = Column(Integer)  # 1-5 scale
    sentiment_score = Column(Float)  # -1 to 1
    sentiment_label = Column(String)  # positive, negative, neutral
    themes = Column(JSON, default=list)  # Extracted themes
    is_private = Column(Boolean, default=True)
    word_count = Column(Integer, default=0)
    reading_time = Column(Integer, default=0)  # in seconds
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="journal_entries")

class ChatSession(Base):
    """Chat sessions with the AI bot"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="Chat Session")
    session_type = Column(String, default="general")  # general, crisis, guided
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    """Individual chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" or "mitra"
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, breathing_exercise, etc.
    metadata = Column(JSON)  # Additional data like breathing exercise details
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class CommunityForum(Base):
    """Community forums"""
    __tablename__ = "community_forums"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, default="general")
    is_private = Column(Boolean, default=False)
    created_by = Column(String, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    threads = relationship("ForumThread", back_populates="forum")

class ForumThread(Base):
    """Forum discussion threads"""
    __tablename__ = "forum_threads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    forum_id = Column(String, ForeignKey("community_forums.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    forum = relationship("CommunityForum", back_populates="threads")
    replies = relationship("ThreadReply", back_populates="thread")

class ThreadReply(Base):
    """Replies to forum threads"""
    __tablename__ = "thread_replies"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey("forum_threads.id"), nullable=False)
    parent_id = Column(String, ForeignKey("thread_replies.id"))  # For nested replies
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    thread = relationship("ForumThread", back_populates="replies")

class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, default="info")  # info, warning, achievement, reminder
    is_read = Column(Boolean, default=False)
    action_url = Column(String)  # URL to navigate to when clicked
    
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)