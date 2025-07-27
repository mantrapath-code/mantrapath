"""
Shared database models across all microservices
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    moods = relationship("MoodEntry", back_populates="user")
    journal_entries = relationship("JournalEntry", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    first_name = Column(String)
    last_name = Column(String)
    avatar_url = Column(String)
    bio = Column(Text)
    timezone = Column(String, default="UTC")
    preferences = Column(JSON, default={})
    
    user = relationship("User", back_populates="profile")

class MoodEntry(Base, TimestampMixin):
    __tablename__ = "mood_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    mood_score = Column(Integer, nullable=False)  # 1-10 scale
    energy_level = Column(Integer)  # 1-10 scale
    stress_level = Column(Integer)  # 1-10 scale
    sleep_quality = Column(Integer)  # 1-10 scale
    notes = Column(Text)
    context_tags = Column(JSON, default=[])
    location = Column(String)
    weather = Column(String)
    
    user = relationship("User", back_populates="moods")

class JournalEntry(Base, TimestampMixin):
    __tablename__ = "journal_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String)
    content = Column(Text, nullable=False)
    mood_before = Column(Integer)
    mood_after = Column(Integer)
    sentiment_score = Column(Float)
    sentiment_label = Column(String)
    themes = Column(JSON, default=[])
    is_private = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="journal_entries")

class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String)
    session_type = Column(String, default="general")  # general, crisis, breathing, etc.
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base, TimestampMixin):
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"))
    sender = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, breathing_exercise, etc.
    metadata = Column(JSON, default={})
    
    session = relationship("ChatSession", back_populates="messages")

class Forum(Base, TimestampMixin):
    __tablename__ = "forums"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    is_private = Column(Boolean, default=False)
    member_count = Column(Integer, default=0)
    
    threads = relationship("ForumThread", back_populates="forum")
    memberships = relationship("ForumMembership", back_populates="forum")

class ForumMembership(Base, TimestampMixin):
    __tablename__ = "forum_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    forum_id = Column(UUID(as_uuid=True), ForeignKey("forums.id"))
    role = Column(String, default="member")  # member, moderator, admin
    
    forum = relationship("Forum", back_populates="memberships")

class ForumThread(Base, TimestampMixin):
    __tablename__ = "forum_threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forum_id = Column(UUID(as_uuid=True), ForeignKey("forums.id"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(Text)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    forum = relationship("Forum", back_populates="threads")
    replies = relationship("ForumReply", back_populates="thread")

class ForumReply(Base, TimestampMixin):
    __tablename__ = "forum_replies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("forum_threads.id"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("forum_replies.id"))
    
    thread = relationship("ForumThread", back_populates="replies")
    parent = relationship("ForumReply", remote_side="ForumReply.id")

class Content(Base, TimestampMixin):
    __tablename__ = "content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text)
    content_type = Column(String)  # article, meditation, exercise, affirmation
    category = Column(String)
    tags = Column(JSON, default=[])
    is_premium = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    
class Like(Base, TimestampMixin):
    __tablename__ = "likes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content_type = Column(String)  # thread, reply, content
    content_id = Column(UUID(as_uuid=True))
    
class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String)  # mood_pattern, community, system
    is_read = Column(Boolean, default=False)
    metadata = Column(JSON, default={})

class Media(Base, TimestampMixin):
    __tablename__ = "media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    original_filename = Column(String)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    media_type = Column(String)  # image, video, audio
    status = Column(String, default="pending")  # pending, approved, rejected
    moderation_reason = Column(Text)