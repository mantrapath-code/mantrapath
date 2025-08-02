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
    username = Column(String, nullable=False, index=True)  # Remove unique constraint
    password_hash = Column(String, nullable=False)
    first_name = Column(String, default="")
    last_name = Column(String, default="")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification status
    verification_token = Column(String, unique=True, nullable=True)  # Email verification token
    verification_token_expires = Column(DateTime, nullable=True)  # Token expiration
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
    """Mood tracking entries with Phase 1 enhancements"""
    __tablename__ = "mood_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    mood_score = Column(Integer, nullable=False)  # 1-10 scale (expanded from 1-5 for more granularity)
    energy_level = Column(Integer, default=5)  # 1-10 scale
    stress_level = Column(Integer, default=5)  # 1-10 scale
    sleep_quality = Column(Integer, default=5)  # 1-10 scale
    notes = Column(Text)
    context_tags = Column(JSON, default=list)  # ["work", "family", etc.]
    
    # Phase 1 Enhancement Fields (with defaults for backward compatibility)
    emotional_granularity = Column(Integer, default=3)  # 1-5 scale for detail level user prefers
    environmental_context = Column(JSON, default=dict)  # Weather, location, calendar context
    mood_confidence = Column(Float, default=1.0)  # User's confidence in their mood rating (0.0-1.0)
    collection_method = Column(String, default="manual")  # manual, prompted, adaptive
    follow_up_responses = Column(JSON, default=list)  # Responses to adaptive follow-up questions
    celebration_triggers = Column(JSON, default=list)  # What triggered celebration moments
    
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
    message_metadata = Column(JSON)  # Additional data like breathing exercise details
    
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
    notification_type = Column(String, default="info")  # mood_reminder, insight, community, system, crisis
    priority = Column(String, default="normal")  # low, normal, high, urgent
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    action_url = Column(String)  # URL to navigate to when clicked
    
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    sent_at = Column(DateTime)

class ScheduledNotification(Base):
    """Scheduled notifications for optimal timing"""
    __tablename__ = "scheduled_notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    notification_type = Column(String, nullable=False)  # mood_reminder, weekly_insight, etc.
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    timezone = Column(String, default="UTC")
    is_sent = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    cancelled_at = Column(DateTime)

# Create aliases for backward compatibility
Forum = CommunityForum
ForumReply = ThreadReply

class ForumMembership(Base):
    """Forum membership tracking"""
    __tablename__ = "forum_memberships"  # Reverted back
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    forum_id = Column(String, ForeignKey("community_forums.id"), nullable=False)
    role = Column(String, default="member")  # member, moderator, admin
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Like(Base):
    """Likes for content (threads, replies, etc.)"""
    __tablename__ = "likes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content_type = Column(String, nullable=False)  # thread, reply, etc.
    content_id = Column(String, nullable=False)  # ID of the liked content
    created_at = Column(DateTime, default=datetime.utcnow)

class Content(Base):
    """Content articles and resources"""
    __tablename__ = "content"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content_type = Column(String, default="article")  # article, guide, resource
    category = Column(String)
    tags = Column(JSON)  # Array of tags
    is_published = Column(Boolean, default=False)
    featured = Column(Boolean, default=False)
    read_time = Column(Integer)  # Estimated read time in minutes
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)

class Affirmation(Base):
    """Daily affirmations and positive messages"""
    __tablename__ = "affirmations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    category = Column(String)  # self-love, confidence, peace, etc.
    author = Column(String)
    is_daily = Column(Boolean, default=False)
    popularity_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class CommunityEvent(Base):
    """Community events"""
    __tablename__ = "community_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String)  # Physical location or meeting link
    is_virtual = Column(Boolean, default=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    max_participants = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Challenge(Base):
    """Wellness challenges"""
    __tablename__ = "challenges"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # mindfulness, fitness, nutrition, etc.
    duration_days = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EventParticipant(Base):
    """Event participation tracking"""
    __tablename__ = "event_participants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event_id = Column(String, ForeignKey("community_events.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    attended = Column(Boolean, default=False)
    feedback = Column(Text)
    rating = Column(Integer)  # 1-5 scale

class ChallengeParticipant(Base):
    """Challenge participation tracking"""
    __tablename__ = "challenge_participants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
    completion_date = Column(DateTime)
    progress_data = Column(JSON)  # Track daily progress

class MediaFile(Base):
    """Uploaded media files"""
    __tablename__ = "media_files"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # image, audio, video, document
    
    # Image-specific fields
    width = Column(Integer)
    height = Column(Integer)
    
    # Audio-specific fields
    duration = Column(Float)  # Duration in seconds
    
    is_public = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Phase 1 Enhancement Models
class EmotionalWeatherForecast(Base):
    """Daily emotional weather predictions for users"""
    __tablename__ = "emotional_weather_forecasts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    predicted_mood_range = Column(JSON)  # {"min": float, "max": float}
    risk_factors = Column(JSON, default=list)  # List of potential challenges
    protective_factors = Column(JSON, default=list)  # List of strengths/supports
    recommendations = Column(JSON, default=list)  # Personalized suggestions
    confidence_score = Column(Float, default=0.5)  # 0.0-1.0 prediction confidence
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CelebrationMoment(Base):
    """Celebration moments and achievements for user motivation"""
    __tablename__ = "celebration_moments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    celebration_type = Column(String, nullable=False)  # improvement_streak, consistency, breakthrough
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    achievement_level = Column(String, default="bronze")  # bronze, silver, gold, platinum
    reward_type = Column(String)  # insight_unlock, feature_unlock, badge_earned
    reward_data = Column(JSON)  # Additional reward information
    is_shown = Column(Boolean, default=False)
    shown_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AdaptiveQuestion(Base):
    """Adaptive follow-up questions based on user patterns"""
    __tablename__ = "adaptive_questions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    question_type = Column(String, nullable=False)  # stress_exploration, energy_context, etc.
    question_text = Column(Text, nullable=False)
    question_options = Column(JSON)  # Multiple choice options or scale info
    trigger_pattern = Column(String)  # What pattern triggered this question
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.5)  # How helpful users find it
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EnvironmentalData(Base):
    """Environmental context data for mood correlation"""
    __tablename__ = "environmental_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    data_date = Column(DateTime, nullable=False)
    weather_data = Column(JSON)  # Temperature, conditions, etc.
    calendar_events = Column(JSON)  # Upcoming events that might affect mood
    location_data = Column(JSON)  # Location context if available
    digital_context = Column(JSON)  # Screen time, app usage patterns
    
    created_at = Column(DateTime, default=datetime.utcnow)