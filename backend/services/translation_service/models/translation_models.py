"""
Database models for Translation Service
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, Float, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from shared.database import Base

class TranslationRequest(Base):
    """Translation request tracking for analytics and caching"""
    __tablename__ = "translation_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)  # nullable for anonymous requests
    session_id = Column(String, nullable=True, index=True)  # for anonymous tracking
    
    # Request details
    source_text = Column(Text, nullable=False)
    source_language = Column(String, nullable=False)  # ISO 639-1
    target_language = Column(String, nullable=False)  # ISO 639-1
    translation_engine = Column(String, nullable=False)  # google, microsoft, openai, local
    
    # Response details
    translated_text = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Context and metadata
    domain = Column(String, nullable=True)  # mindfulness, buddhist, etc.
    context_type = Column(String, nullable=True)  # meditation, journal, chat, etc.
    cultural_adaptation = Column(Boolean, default=False)
    voice_translation = Column(Boolean, default=False)
    
    # Status tracking
    status = Column(String, default="pending")  # pending, completed, failed, cached
    error_message = Column(Text, nullable=True)
    cache_hit = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_translation_user_lang', 'user_id', 'source_language', 'target_language'),
        Index('idx_translation_cache_lookup', 'source_text', 'source_language', 'target_language'),
        Index('idx_translation_performance', 'created_at', 'processing_time_ms'),
    )

class TranslationCache(Base):
    """High-performance translation cache with TTL and quality tracking"""
    __tablename__ = "translation_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Cache key components
    source_text_hash = Column(String, nullable=False, index=True)  # SHA-256 of source text
    source_language = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    domain = Column(String, nullable=True)  # domain-specific caching
    
    # Cached data
    translated_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    translation_engine = Column(String, nullable=False)
    
    # Cache metadata
    hit_count = Column(Integer, default=1)
    last_accessed = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    priority = Column(String, default="normal")  # critical, high, normal, low
    
    # Quality tracking
    user_feedback_score = Column(Float, nullable=True)  # 1-5 user rating
    error_reports = Column(Integer, default=0)
    improvement_suggestions = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_cache_lookup', 'source_text_hash', 'source_language', 'target_language', 'domain'),
        Index('idx_cache_expiry', 'expires_at'),
        Index('idx_cache_quality', 'quality_score', 'hit_count'),
    )

class LanguageDetectionResult(Base):
    """Language detection results for analytics and improvement"""
    __tablename__ = "language_detection_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    session_id = Column(String, nullable=True, index=True)
    
    # Input
    text_sample = Column(Text, nullable=False)
    
    # Detection results
    detected_language = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    alternative_languages = Column(JSON, nullable=True)  # [{lang: str, confidence: float}]
    detection_engine = Column(String, nullable=False)  # langdetect, fasttext, google, etc.
    
    # Verification
    user_confirmed_language = Column(String, nullable=True)
    correction_needed = Column(Boolean, default=False)
    
    # Performance
    processing_time_ms = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_lang_detection_performance', 'detected_language', 'confidence_score'),
        Index('idx_lang_detection_accuracy', 'detected_language', 'user_confirmed_language'),
    )

class CustomGlossary(Base):
    """Custom meditation terminology and user-specific translations"""
    __tablename__ = "custom_glossaries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Scope
    scope = Column(String, nullable=False)  # global, user, organization
    scope_id = Column(String, nullable=True)  # user_id for user scope
    domain = Column(String, nullable=False)  # mindfulness, buddhist, etc.
    
    # Term data
    source_term = Column(String, nullable=False)
    source_language = Column(String, nullable=False)
    target_term = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    
    # Metadata
    definition = Column(Text, nullable=True)
    cultural_context = Column(Text, nullable=True)
    usage_examples = Column(JSON, nullable=True)
    pronunciation = Column(String, nullable=True)  # IPA or phonetic
    
    # Quality and usage
    confidence_score = Column(Float, default=1.0)
    usage_frequency = Column(Integer, default=0)
    user_verified = Column(Boolean, default=False)
    expert_reviewed = Column(Boolean, default=False)
    
    # Relationships
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_glossary_lookup', 'source_term', 'source_language', 'target_language', 'domain'),
        Index('idx_glossary_scope', 'scope', 'scope_id', 'domain'),
        Index('idx_glossary_quality', 'confidence_score', 'expert_reviewed'),
    )

class TranslationFeedback(Base):
    """User feedback on translation quality for continuous improvement"""
    __tablename__ = "translation_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    translation_request_id = Column(String, ForeignKey("translation_requests.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Feedback details
    rating = Column(Integer, nullable=False)  # 1-5 scale
    accuracy_rating = Column(Integer, nullable=True)  # 1-5 scale
    cultural_appropriateness = Column(Integer, nullable=True)  # 1-5 scale
    naturalness_rating = Column(Integer, nullable=True)  # 1-5 scale
    
    # Detailed feedback
    suggested_translation = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    reported_issues = Column(JSON, nullable=True)  # [issue_type, ...]
    
    # Context
    feedback_type = Column(String, default="rating")  # rating, correction, report
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    translation_request = relationship("TranslationRequest")
    
    __table_args__ = (
        Index('idx_feedback_quality', 'translation_request_id', 'rating'),
        Index('idx_feedback_user', 'user_id', 'created_at'),
    )

class OfflineTranslationCache(Base):
    """High-priority translations cached for offline access"""
    __tablename__ = "offline_translation_cache"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Cache identification
    source_text_hash = Column(String, nullable=False, index=True)
    source_language = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    
    # Translation data
    translated_text = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    
    # Offline-specific metadata
    priority_level = Column(String, default="medium")  # critical, high, medium, low
    download_count = Column(Integer, default=0)
    last_synced = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    size_bytes = Column(Integer, nullable=False)
    
    # Expiry and maintenance
    expires_at = Column(DateTime, nullable=True)  # None for permanent cache
    auto_renewable = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index('idx_offline_cache_lookup', 'source_text_hash', 'source_language', 'target_language'),
        Index('idx_offline_cache_priority', 'priority_level', 'expires_at'),
        Index('idx_offline_cache_size', 'size_bytes', 'created_at'),
    )
