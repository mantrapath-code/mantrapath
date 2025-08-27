"""
Database Models for Media Service
"""

from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

Base = declarative_base()


def utc_now():
    """Get current UTC time"""
    return datetime.now(timezone.utc)


class MediaFile(Base):
    """Main media files table"""
    __tablename__ = "media_files"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False, index=True)  # image, video, audio, document
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Storage information
    storage_provider = Column(String(50), nullable=False)  # aws_s3, minio, local
    storage_path = Column(Text, nullable=False)
    cdn_url = Column(Text, nullable=True)
    
    # Processing information
    thumbnail_url = Column(Text, nullable=True)
    processing_status = Column(String(50), default='pending')  # pending, processing, completed, failed
    is_public = Column(Boolean, default=False)
    
    # Metadata
    file_metadata = Column(JSONB, nullable=True)  # File-specific metadata (dimensions, duration, etc.)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    # Relationships
    variants = relationship("MediaVariant", back_populates="media_file", cascade="all, delete-orphan")
    analysis_results = relationship("ContentAnalysis", back_populates="media_file", cascade="all, delete-orphan")


class MediaVariant(Base):
    """Media variants table (resized, compressed versions)"""
    __tablename__ = "media_variants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey('media_files.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Variant information
    variant_type = Column(String(50), nullable=False)  # thumbnail, compressed, resized, converted
    variant_config = Column(JSONB, nullable=False)  # Processing parameters used
    
    # Storage information
    storage_path = Column(Text, nullable=False)
    cdn_url = Column(Text, nullable=True)
    file_size = Column(BigInteger, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    
    # Relationships
    media_file = relationship("MediaFile", back_populates="variants")


class ContentAnalysis(Base):
    """Content analysis results table"""
    __tablename__ = "content_analysis"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey('media_files.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Analysis information
    analysis_type = Column(String(50), nullable=False)  # nsfw, objects, sentiment, faces, text_ocr
    confidence_score = Column(String(10), nullable=True)  # Decimal stored as string for precision
    results = Column(JSONB, nullable=False)  # Analysis results in JSON format
    
    # Timestamps
    analyzed_at = Column(DateTime, default=utc_now)
    
    # Relationships
    media_file = relationship("MediaFile", back_populates="analysis_results")


class MediaAccess(Base):
    """Media access tracking table"""
    __tablename__ = "media_access"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey('media_files.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Null for anonymous access
    
    # Access information
    access_type = Column(String(50), nullable=False)  # view, download, stream
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)
    
    # Timestamps
    accessed_at = Column(DateTime, default=utc_now, index=True)


class MediaProcessingJob(Base):
    """Media processing jobs queue table"""
    __tablename__ = "media_processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey('media_files.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Job information
    job_type = Column(String(50), nullable=False)  # thumbnail, resize, compress, analyze, cdn_sync
    job_config = Column(JSONB, nullable=False)  # Job parameters
    priority = Column(Integer, default=5)  # 1-10, lower is higher priority
    
    # Status tracking
    status = Column(String(50), default='pending')  # pending, processing, completed, failed, retrying
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Worker information
    worker_id = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    
class MediaTag(Base):
    """Media tags table for categorization"""
    __tablename__ = "media_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(String(50), nullable=True)  # user_defined, auto_detected, system
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class MediaFileTag(Base):
    """Many-to-many relationship between media files and tags"""
    __tablename__ = "media_file_tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    media_file_id = Column(UUID(as_uuid=True), ForeignKey('media_files.id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey('media_tags.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Tag assignment information
    assigned_by = Column(String(50), nullable=False)  # user, system, ai
    confidence = Column(String(10), nullable=True)  # For AI-assigned tags
    
    # Timestamps
    created_at = Column(DateTime, default=utc_now)


# Indexes for performance optimization
# These would be created via migration scripts

"""
-- Additional indexes to create via migrations:

-- Media files indexes
CREATE INDEX idx_media_files_user_created ON media_files(user_id, created_at DESC);
CREATE INDEX idx_media_files_type_status ON media_files(file_type, processing_status);
CREATE INDEX idx_media_files_public_created ON media_files(is_public, created_at DESC) WHERE is_public = true;

-- Media variants indexes
CREATE INDEX idx_media_variants_file_type ON media_variants(media_file_id, variant_type);

-- Content analysis indexes  
CREATE INDEX idx_content_analysis_type_confidence ON content_analysis(analysis_type, confidence_score);

-- Media access indexes
CREATE INDEX idx_media_access_file_date ON media_access(media_file_id, accessed_at DESC);
CREATE INDEX idx_media_access_user_date ON media_access(user_id, accessed_at DESC) WHERE user_id IS NOT NULL;

-- Processing jobs indexes
CREATE INDEX idx_processing_jobs_status_priority ON media_processing_jobs(status, priority, created_at);
CREATE INDEX idx_processing_jobs_type_status ON media_processing_jobs(job_type, status);

-- Media tags indexes
CREATE INDEX idx_media_tags_category_usage ON media_tags(category, usage_count DESC);

-- Media file tags indexes
CREATE INDEX idx_media_file_tags_file_assigned ON media_file_tags(media_file_id, assigned_by);
CREATE INDEX idx_media_file_tags_tag_confidence ON media_file_tags(tag_id, confidence DESC);
"""
