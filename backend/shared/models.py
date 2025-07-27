"""
Shared database models and utilities for MantraPath microservices
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class User(Base, TimestampMixin):
    """Core user model - shared across services"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(50), default="user")  # user, moderator, admin
    
    # Profile relationship
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base, TimestampMixin):
    """Extended user profile information"""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Profile data
    bio = Column(Text)
    avatar_url = Column(String(500))
    timezone = Column(String(50), default="UTC")
    date_of_birth = Column(DateTime)
    location = Column(String(255))
    
    # Preferences
    theme = Column(String(50), default="light")
    privacy_level = Column(String(50), default="private")  # public, friends, private
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    mood_reminders = Column(Boolean, default=True)
    weekly_reports = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="profile")

class MoodEntry(Base, TimestampMixin):
    """User mood tracking entries"""
    __tablename__ = "mood_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Mood data
    mood_score = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    anxiety_level = Column(Integer)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    
    # Context
    context_tags = Column(JSON)  # ["work", "exercise", "social"]
    notes = Column(Text)
    location = Column(String(255))
    weather = Column(String(100))
    
    # Analysis
    sentiment_score = Column(Float)
    detected_emotions = Column(JSON)

class JournalEntry(Base, TimestampMixin):
    """User journal entries"""
    __tablename__ = "journal_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255))
    content = Column(Text, nullable=False)
    mood_before = Column(Integer)  # 1-10
    mood_after = Column(Integer)   # 1-10
    
    # Analysis
    sentiment_score = Column(Float)
    key_themes = Column(JSON)
    word_count = Column(Integer)
    
    # Privacy
    is_private = Column(Boolean, default=True)
    tags = Column(JSON)

class Habit(Base, TimestampMixin):
    """User habit tracking"""
    __tablename__ = "habits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))  # exercise, mindfulness, sleep, etc.
    target_frequency = Column(String(50))  # daily, weekly, etc.
    is_active = Column(Boolean, default=True)
    
    # Tracking
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_completions = Column(Integer, default=0)

class HabitEvent(Base, TimestampMixin):
    """Individual habit completion events"""
    __tablename__ = "habit_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    completed_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    rating = Column(Integer)  # How did it go? 1-5
    duration_minutes = Column(Integer)

class ChatSession(Base, TimestampMixin):
    """Chatbot conversation sessions"""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255))
    is_active = Column(Boolean, default=True)
    session_type = Column(String(50), default="general")  # general, crisis, guided
    
    # Analytics
    message_count = Column(Integer, default=0)
    avg_sentiment = Column(Float)
    topics_discussed = Column(JSON)

class ChatMessage(Base, TimestampMixin):
    """Individual chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, nullable=False)
    message_type = Column(String(50), default="text")  # text, image, exercise
    
    # Analysis
    sentiment_score = Column(Float)
    detected_emotions = Column(JSON)
    crisis_indicators = Column(JSON)

class Forum(Base, TimestampMixin):
    """Community forums"""
    __tablename__ = "forums"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    is_public = Column(Boolean, default=True)
    
    # Moderation
    requires_approval = Column(Boolean, default=False)
    moderator_ids = Column(JSON)
    
    # Stats
    thread_count = Column(Integer, default=0)
    member_count = Column(Integer, default=0)

class ForumThread(Base, TimestampMixin):
    """Forum discussion threads"""
    __tablename__ = "forum_threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forum_id = Column(UUID(as_uuid=True), ForeignKey("forums.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    # Engagement
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Moderation
    is_approved = Column(Boolean, default=True)
    tags = Column(JSON)

class ForumPost(Base, TimestampMixin):
    """Replies to forum threads"""
    __tablename__ = "forum_posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("forum_threads.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    is_approved = Column(Boolean, default=True)

class Like(Base, TimestampMixin):
    """Universal like system"""
    __tablename__ = "likes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    content_type = Column(String(50), nullable=False)  # thread, post, content
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)

class Content(Base, TimestampMixin):
    """Wellness content (articles, videos, etc.)"""
    __tablename__ = "content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False)  # article, video, audio, exercise
    category = Column(String(100))
    
    # Metadata
    author = Column(String(255))
    source_url = Column(String(500))
    duration_minutes = Column(Integer)
    difficulty_level = Column(String(50))  # beginner, intermediate, advanced
    
    # Engagement
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    
    # Content properties
    tags = Column(JSON)
    is_published = Column(Boolean, default=False)

class Affirmation(Base, TimestampMixin):
    """Daily affirmations"""
    __tablename__ = "affirmations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    category = Column(String(100))
    mood_context = Column(JSON)  # When to show this affirmation
    
    # Usage stats
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)

class Notification(Base, TimestampMixin):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # mood_reminder, insight, community
    
    # Delivery
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    
    # Metadata
    action_url = Column(String(500))
    priority = Column(String(50), default="normal")  # low, normal, high, urgent

class MediaFile(Base, TimestampMixin):
    """User uploaded media files"""
    __tablename__ = "media_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    
    # Processing
    is_processed = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    thumbnail_path = Column(String(500))
    
    # Metadata
    alt_text = Column(String(500))
    caption = Column(Text)
    tags = Column(JSON)

# Indexes for better performance
from sqlalchemy import Index

# User indexes
Index('idx_users_email', User.email)
Index('idx_users_role', User.role)

# Mood tracking indexes
Index('idx_mood_entries_user_date', MoodEntry.user_id, MoodEntry.created_at)
Index('idx_journal_entries_user_date', JournalEntry.user_id, JournalEntry.created_at)

# Community indexes
Index('idx_forum_threads_forum_date', ForumThread.forum_id, ForumThread.created_at)
Index('idx_forum_posts_thread_date', ForumPost.thread_id, ForumPost.created_at)
Index('idx_likes_content', Like.content_type, Like.content_id)

# Notification indexes
Index('idx_notifications_user_unread', Notification.user_id, Notification.is_read)
Index('idx_notifications_type_date', Notification.notification_type, Notification.created_at)