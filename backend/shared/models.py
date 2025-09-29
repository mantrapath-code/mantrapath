"""
Database models for MantraPath
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Float, ForeignKey, JSON, Date, Time, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()

# Helper function for current timestamp
def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)  # Enforce unique constraint
    password_hash = Column(String, nullable=False)
    first_name = Column(String, default="")
    last_name = Column(String, default="")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Email verification status
    verification_token = Column(String, unique=True, nullable=True)  # Email verification token
    verification_token_expires = Column(DateTime, nullable=True)  # Token expiration
    role = Column(String, default="user")  # user, moderator, admin
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    user = relationship("User", back_populates="profile")

# --- E1: Multilingual Foundations (Added) ---
class UserLanguagePreference(Base):
    """Per-user language & basic cultural preferences (MVP)"""
    __tablename__ = "user_language_preferences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    primary_language = Column(String, nullable=False, default="en")  # ISO 639-1
    secondary_languages = Column(JSON)  # list of ISO codes
    auto_detect_language = Column(Boolean, default=True)
    cultural_region = Column(String)  # ISO 3166-1 alpha-2
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index('idx_user_language_pref_user', 'user_id'),
    )
# --- End E1 addition ---

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
    description = Column(Text)  # Compatibility column for mood service
    context_tags = Column(JSON, default=list)  # ["work", "family", etc.]
    
    # AI Analysis results (for mood service compatibility)
    primary_emotion = Column(String, nullable=True)
    primary_sentiment = Column(String, nullable=True)  # positive, negative, neutral, ambiguous
    emotion_analysis = Column(JSON, nullable=True)  # Full emotion analysis results
    
    # Additional context (for mood service compatibility)
    location = Column(String, nullable=True)
    activity = Column(String, nullable=True)
    memory_context_id = Column(String, nullable=True)  # Links to memory service context
    
    # Phase 1 Enhancement Fields (with defaults for backward compatibility)
    emotional_granularity = Column(Integer, default=3)  # 1-5 scale for detail level user prefers
    environmental_context = Column(JSON, default=dict)  # Weather, location, calendar context
    mood_confidence = Column(Float, default=1.0)  # User's confidence in their mood rating (0.0-1.0)
    collection_method = Column(String, default="manual")  # manual, prompted, adaptive
    follow_up_responses = Column(JSON, default=list)  # Responses to adaptive follow-up questions
    celebration_triggers = Column(JSON, default=list)  # What triggered celebration moments
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
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
    
    created_at = Column(DateTime, default=utcnow)
    
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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
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
    
    created_at = Column(DateTime, default=utcnow)
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
    
    created_at = Column(DateTime, default=utcnow)
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
    joined_at = Column(DateTime, default=utcnow)
    is_active = Column(Boolean, default=True)

class Like(Base):
    """Likes for content (threads, replies, etc.)"""
    __tablename__ = "likes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content_type = Column(String, nullable=False)  # thread, reply, etc.
    content_id = Column(String, nullable=False)  # ID of the liked content
    created_at = Column(DateTime, default=utcnow)

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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
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
    
    created_at = Column(DateTime, default=utcnow)

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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class Challenge(Base):
    """Enhanced wellness challenges with Phase 3A features"""
    __tablename__ = "challenges"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # mindfulness, fitness, nutrition, etc.
    duration_days = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Phase 3A: Privacy and Access Control
    visibility = Column(String, default="public")  # public, private, invite_only
    max_participants = Column(Integer, default=10000)  # Support up to 10K users
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=False)
    
    # Phase 3A: Generic Challenge Structure
    challenge_type = Column(String, default="custom")  # custom, template, guided
    goal_type = Column(String, default="daily")  # daily, weekly, milestone, streak - now with default
    success_criteria = Column(JSON)  # Flexible criteria definition
    reward_points = Column(Integer, default=0)
    difficulty_level = Column(String, default="beginner")  # beginner, intermediate, advanced
    
    # Phase 3A: Invitation System
    invitation_code = Column(String, unique=True)  # Unique invitation code
    invitation_expires_at = Column(DateTime)  # Invitation expiry
    allow_invite_sharing = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class ChallengeInvitation(Base):
    """Phase 3A: Challenge invitation system for private/invite-only challenges"""
    __tablename__ = "challenge_invitations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    invited_by = Column(String, ForeignKey("users.id"), nullable=False)
    invited_user_id = Column(String, ForeignKey("users.id"))  # Null for public invite links
    invited_email = Column(String)  # For inviting non-users
    invitation_code = Column(String, nullable=False, unique=True)
    
    status = Column(String, default="pending")  # pending, accepted, declined, expired
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime)
    declined_at = Column(DateTime)
    
    # Usage tracking
    uses_count = Column(Integer, default=0)
    max_uses = Column(Integer, default=1)  # -1 for unlimited
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class ChallengeLeaderboard(Base):
    """Phase 3A: Efficient leaderboard for challenges supporting 10K+ users"""
    __tablename__ = "challenge_leaderboards"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Denormalized data for fast queries
    total_score = Column(Integer, default=0, index=True)
    completion_percentage = Column(Float, default=0.0, index=True)
    completed_days = Column(Integer, default=0)
    current_streak = Column(Integer, default=0, index=True)
    max_streak = Column(Integer, default=0)
    
    # Ranking data (updated via batch job)
    global_rank = Column(Integer, index=True)
    percentile = Column(Float)
    
    # Timestamps for accurate tracking
    last_activity_at = Column(DateTime, index=True)
    last_updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    # Unique constraint to prevent duplicates
    __table_args__ = (
        Index('idx_challenge_leaderboard', 'challenge_id', 'user_id', unique=True),
        Index('idx_leaderboard_ranking', 'challenge_id', 'total_score', 'completion_percentage'),
    )

class EventParticipant(Base):
    """Event participation tracking"""
    __tablename__ = "event_participants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    event_id = Column(String, ForeignKey("community_events.id"), nullable=False)
    joined_at = Column(DateTime, default=utcnow)
    attended = Column(Boolean, default=False)
    feedback = Column(Text)
    rating = Column(Integer)  # 1-5 scale

class ChallengeParticipant(Base):
    """Challenge participation tracking"""
    __tablename__ = "challenge_participants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    joined_at = Column(DateTime, default=utcnow)
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
    
    created_at = Column(DateTime, default=utcnow)

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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

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
    
    created_at = Column(DateTime, default=utcnow)

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
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

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
    
    created_at = Column(DateTime, default=utcnow)

# Enhanced Community Models for Interactive Events & Challenges
class ChallengeProgress(Base):
    """Daily progress tracking for challenges"""
    __tablename__ = "challenge_progress"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_participant_id = Column(String, ForeignKey("challenge_participants.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # Denormalized for easier queries
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)  # Denormalized for easier queries
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    notes = Column(Text)
    mood_rating = Column(Integer)  # 1-5 scale
    reflection = Column(Text)
    streak_count = Column(Integer, default=0)
    completion_time = Column(Time)  # What time they completed it
    difficulty_rating = Column(Integer)  # How challenging was it today (1-5)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class EventComment(Base):
    """Comments on events"""
    __tablename__ = "event_comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("community_events.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(String, ForeignKey("event_comments.id"))  # For replies
    is_moderator_comment = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    like_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class ChallengeComment(Base):
    """Comments on challenges"""
    __tablename__ = "challenge_comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(String, ForeignKey("challenge_comments.id"))  # For replies
    is_progress_share = Column(Boolean, default=False)  # Is this a progress sharing comment?
    progress_day = Column(Integer)  # Which day of the challenge this relates to
    mood_tag = Column(String)  # Optional mood tag associated with the comment
    is_pinned = Column(Boolean, default=False)
    like_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class EventFeedback(Base):
    """Post-event feedback and ratings"""
    __tablename__ = "event_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String, ForeignKey("community_events.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    participant_id = Column(String, ForeignKey("event_participants.id"), nullable=False)
    overall_rating = Column(Integer, nullable=False)  # 1-5 scale
    content_rating = Column(Integer)  # 1-5 scale for content quality
    organization_rating = Column(Integer)  # 1-5 scale for organization
    engagement_rating = Column(Integer)  # 1-5 scale for engagement level
    feedback_text = Column(Text)
    would_recommend = Column(Boolean)
    would_attend_similar = Column(Boolean)
    improvement_suggestions = Column(Text)
    favorite_aspects = Column(JSON)  # List of things they liked most
    tags = Column(JSON)  # ["helpful", "inspiring", "well-organized", "too-long", etc.]
    is_anonymous = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=utcnow)

class ChallengeReflection(Base):
    """End-of-challenge reflections and achievements"""
    __tablename__ = "challenge_reflections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    challenge_id = Column(String, ForeignKey("challenges.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    participant_id = Column(String, ForeignKey("challenge_participants.id"), nullable=False)
    completion_percentage = Column(Float, nullable=False)  # 0-100
    total_days_completed = Column(Integer, nullable=False)
    longest_streak = Column(Integer, default=0)
    average_mood_rating = Column(Float)
    biggest_challenge = Column(Text)
    biggest_win = Column(Text)
    key_insights = Column(Text)
    would_recommend = Column(Boolean)
    difficulty_rating = Column(Integer)  # 1-5 how challenging overall
    life_impact_rating = Column(Integer)  # 1-5 how much it impacted their life
    favorite_days = Column(JSON)  # List of day numbers they enjoyed most
    challenging_days = Column(JSON)  # List of day numbers that were hardest
    tags = Column(JSON)  # ["life-changing", "harder-than-expected", "motivating", etc.]
    
    created_at = Column(DateTime, default=utcnow)

class CommentLike(Base):
    """Likes on comments (both event and challenge comments)"""
    __tablename__ = "comment_likes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    comment_type = Column(String, nullable=False)  # 'event_comment' or 'challenge_comment'
    comment_id = Column(String, nullable=False)  # ID of the comment
    
    created_at = Column(DateTime, default=utcnow)

class CommunityStats(Base):
    """Daily community statistics for analytics"""
    __tablename__ = "community_stats"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    stat_date = Column(Date, nullable=False)
    active_events = Column(Integer, default=0)
    active_challenges = Column(Integer, default=0)
    total_participants = Column(Integer, default=0)
    new_participants = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    total_progress_updates = Column(Integer, default=0)
    average_event_rating = Column(Float)
    average_challenge_completion = Column(Float)
    top_challenge_categories = Column(JSON)  # Most popular categories
    engagement_metrics = Column(JSON)  # Additional engagement data
    
    created_at = Column(DateTime, default=utcnow)


# Memory Service Models (Sprint 3)

class UserInteraction(Base):
    """
    Stores all user interactions across the platform for memory service
    """
    __tablename__ = "user_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    interaction_type = Column(String(100), nullable=False, index=True)  # mood, journal, chat, community, voice
    interaction_data = Column(JSON, nullable=False)
    cultural_context = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=utcnow, nullable=False, index=True)
    interaction_metadata = Column(JSON, nullable=True)
    
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
    deleted_at = Column(DateTime, nullable=True)

    # Add indexes for performance
    __table_args__ = (
        Index('idx_user_interactions_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_user_interactions_type_timestamp', 'interaction_type', 'timestamp'),
        Index('idx_user_interactions_source_timestamp', 'source_service', 'timestamp'),
        Index('idx_user_interactions_session', 'session_id', 'timestamp'),
    )

class MoodPattern(Base):
    """
    Stores aggregated mood patterns and analysis results
    """
    __tablename__ = "mood_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    pattern_type = Column(String(100), nullable=False, index=True)  # daily, weekly, monthly, seasonal
    pattern_data = Column(JSON, nullable=False)
    
    # Pattern characteristics
    confidence_score = Column(Float, nullable=False, default=0.0)
    frequency = Column(String(50), nullable=True)  # daily, weekly, monthly
    intensity = Column(Float, nullable=True)  # 0.0 to 1.0
    stability = Column(Float, nullable=True)  # how stable the pattern is
    
    # Time range
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=utcnow)
    
    # Cultural and contextual information
    cultural_context = Column(JSON, nullable=True)
    environmental_factors = Column(JSON, nullable=True)
    triggers = Column(JSON, nullable=True)
    
    # Analysis metadata
    analysis_version = Column(String(20), nullable=True)  # track algorithm versions
    sample_size = Column(Integer, nullable=True)  # number of interactions analyzed
    
    # Soft delete support
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Add indexes for performance
    __table_args__ = (
        Index('idx_mood_patterns_user_type', 'user_id', 'pattern_type'),
        Index('idx_mood_patterns_date_range', 'start_date', 'end_date'),
        Index('idx_mood_patterns_confidence', 'confidence_score'),
        Index('idx_mood_patterns_active', 'is_active', 'is_deleted'),
    )

class BehavioralInsight(Base):
    """
    Stores generated behavioral insights and recommendations
    """
    __tablename__ = "behavioral_insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False, index=True)  # recommendation, warning, trend, achievement
    insight_data = Column(JSON, nullable=False)
    
    # Insight characteristics
    accuracy_score = Column(Float, nullable=False, default=0.0)
    relevance_score = Column(Float, nullable=False, default=0.0)
    urgency_level = Column(String(20), nullable=False, default='low')  # low, medium, high, critical
    priority = Column(Integer, nullable=False, default=1)  # 1-10 scale
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    action_items = Column(JSON, nullable=True)
    
    # Timing and context
    generated_at = Column(DateTime, default=utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    delivered_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Cultural and personalization
    cultural_context = Column(JSON, nullable=True)
    personalization_factors = Column(JSON, nullable=True)
    delivery_channels = Column(JSON, nullable=True)  # preferred delivery methods
    
    # Feedback and effectiveness
    user_feedback = Column(JSON, nullable=True)
    effectiveness_score = Column(Float, nullable=True)
    follow_up_required = Column(Boolean, default=False, nullable=False)
    
    # Source tracking
    source_patterns = Column(JSON, nullable=True)  # which patterns led to this insight
    source_interactions = Column(JSON, nullable=True)  # which interactions contributed
    algorithm_version = Column(String(20), nullable=True)
    
    # State management
    status = Column(String(50), nullable=False, default='generated')  # generated, delivered, acknowledged, expired
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Add indexes for performance
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
    """
    __tablename__ = "memory_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Session characteristics
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True, index=True)
    duration_seconds = Column(Integer, nullable=True)
    interaction_count = Column(Integer, default=0, nullable=False)
    
    # Context
    device_type = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    location_data = Column(JSON, nullable=True)
    
    # Session analysis
    mood_trend = Column(JSON, nullable=True)
    activity_summary = Column(JSON, nullable=True)
    engagement_score = Column(Float, nullable=True)
    session_quality = Column(String(20), nullable=True)  # high, medium, low
    
    # Cultural context
    cultural_context = Column(JSON, nullable=True)
    language_preference = Column(String(10), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # State
    is_active = Column(Boolean, default=True, nullable=False)
    closed_reason = Column(String(100), nullable=True)  # timeout, logout, error, etc.

    # Add indexes for performance
    __table_args__ = (
        Index('idx_memory_sessions_user_time', 'user_id', 'start_time'),
        Index('idx_memory_sessions_active', 'is_active', 'end_time'),
        Index('idx_memory_sessions_duration', 'duration_seconds'),
    )

class MemoryAggregation(Base):
    """
    Stores pre-computed aggregations for performance
    """
    __tablename__ = "memory_aggregations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    aggregation_type = Column(String(100), nullable=False, index=True)  # daily, weekly, monthly
    aggregation_key = Column(String(255), nullable=False, index=True)  # specific aggregation identifier
    
    # Aggregated data
    aggregation_data = Column(JSON, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    sum_value = Column(Float, nullable=True)
    avg_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    
    # Time range
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    computed_at = Column(DateTime, default=utcnow, nullable=False)
    
    # Metadata
    computation_version = Column(String(20), nullable=True)
    source_count = Column(Integer, nullable=True)  # number of source records
    confidence_score = Column(Float, nullable=True)
    
    # State
    is_current = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Add indexes for performance
    __table_args__ = (
        Index('idx_memory_aggregations_user_type_key', 'user_id', 'aggregation_type', 'aggregation_key'),
        Index('idx_memory_aggregations_period', 'period_start', 'period_end'),
        Index('idx_memory_aggregations_current', 'is_current', 'is_deleted'),
    )