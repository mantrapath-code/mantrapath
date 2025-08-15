"""
API Request and Response Models for Media Service
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uuid


class MediaUploadRequest(BaseModel):
    """Request model for media upload"""
    alt_text: Optional[str] = Field(None, max_length=255, description="Alternative text for accessibility")
    caption: Optional[str] = Field(None, max_length=1000, description="Media caption") 
    tags: Optional[List[str]] = Field(None, description="Media tags")
    is_public: Optional[bool] = Field(False, description="Whether media is publicly accessible")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            # Filter empty tags and limit length
            return [tag.strip()[:50] for tag in v if tag.strip()][:20]
        return v


class MediaUploadResponse(BaseModel):
    """Response model for successful media upload"""
    id: uuid.UUID
    filename: str
    file_size: int
    content_type: str
    file_type: str  # image, video, audio, document
    upload_url: str
    thumbnail_url: Optional[str] = None
    status: str
    processing_job_id: Optional[uuid.UUID] = None
    
    model_config = {"from_attributes": True}


class MediaFileResponse(BaseModel):
    """Response model for media file details"""
    id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mime_type: str
    storage_provider: str
    cdn_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    processing_status: str
    is_public: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class MediaListResponse(BaseModel):
    """Response model for media file list"""
    items: List[MediaFileResponse]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class MediaVariantResponse(BaseModel):
    """Response model for media variant"""
    id: uuid.UUID
    variant_type: str
    variant_config: Dict[str, Any]
    storage_path: str
    cdn_url: Optional[str] = None
    file_size: int
    created_at: datetime
    
    model_config = {"from_attributes": True}


class MediaProcessingRequest(BaseModel):
    """Request model for media processing operations"""
    operation: str = Field(..., description="Processing operation type")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    priority: Optional[int] = Field(5, ge=1, le=10, description="Processing priority (1-10)")


class MediaProcessingResponse(BaseModel):
    """Response model for media processing job"""
    job_id: uuid.UUID
    media_id: uuid.UUID
    operation: str
    status: str
    estimated_completion: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class ImageProcessingRequest(MediaProcessingRequest):
    """Request model for image processing"""
    operation: str = Field(..., description="resize, compress, convert, enhance, or thumbnail")


class VideoProcessingRequest(MediaProcessingRequest):
    """Request model for video processing"""
    operation: str = Field(..., description="compress, convert, thumbnail, or extract_audio")


class AudioProcessingRequest(MediaProcessingRequest):
    """Request model for audio processing"""
    operation: str = Field(..., description="compress, convert, normalize, or extract_waveform")


class ContentAnalysisResponse(BaseModel):
    """Response model for content analysis results"""
    id: uuid.UUID
    media_file_id: uuid.UUID
    analysis_type: str
    confidence_score: Optional[str] = None
    results: Dict[str, Any]
    analyzed_at: datetime
    
    model_config = {"from_attributes": True}


class MediaAnalyticsResponse(BaseModel):
    """Response model for media analytics"""
    media_id: uuid.UUID
    view_count: int
    download_count: int
    stream_count: int
    last_accessed: Optional[datetime] = None
    access_by_country: Dict[str, int]
    access_by_device: Dict[str, int]
    bandwidth_usage: int  # bytes
    
    model_config = {"from_attributes": True}


class MediaUpdateRequest(BaseModel):
    """Request model for updating media metadata"""
    alt_text: Optional[str] = Field(None, max_length=255)
    caption: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            return [tag.strip()[:50] for tag in v if tag.strip()][:20]
        return v


class MediaSearchRequest(BaseModel):
    """Request model for media search"""
    query: Optional[str] = Field(None, max_length=200, description="Search query")
    file_type: Optional[str] = Field(None, description="image, video, audio, or document")
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_size: Optional[int] = Field(None, ge=0)
    max_size: Optional[int] = Field(None, ge=0)
    is_public: Optional[bool] = None
    processing_status: Optional[str] = Field(None, description="pending, processing, completed, or failed")
    
    # Pagination
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    
    # Sorting
    sort_by: str = Field("created_at", description="created_at, file_size, or filename")
    sort_order: str = Field("desc", description="asc or desc")


class MediaModerationRequest(BaseModel):
    """Request model for media moderation"""
    action: str = Field(..., description="approve, reject, or flag")
    reason: Optional[str] = Field(None, max_length=500)
    moderator_notes: Optional[str] = Field(None, max_length=1000)


class MediaModerationResponse(BaseModel):
    """Response model for media moderation action"""
    media_id: uuid.UUID
    action: str
    reason: Optional[str] = None
    moderator_id: uuid.UUID
    moderated_at: datetime
    
    model_config = {"from_attributes": True}


class MediaBulkActionRequest(BaseModel):
    """Request model for bulk media actions"""
    media_ids: List[uuid.UUID] = Field(..., description="List of media IDs (max 100)")
    action: str = Field(..., description="delete, approve, reject, make_public, or make_private")
    reason: Optional[str] = Field(None, max_length=500)


class MediaBulkActionResponse(BaseModel):
    """Response model for bulk media actions"""
    succeeded: List[uuid.UUID]
    failed: List[Dict[str, Union[uuid.UUID, str]]]
    total_processed: int


class HealthCheckResponse(BaseModel):
    """Response model for service health check"""
    status: str
    service: str
    timestamp: datetime
    storage_providers: Dict[str, str]
    processing_queues: Dict[str, int]
    database: str
    disk_space: Dict[str, float]


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime


# Constants for consistent values
class FileType:
    IMAGE = "image"
    VIDEO = "video" 
    AUDIO = "audio"
    DOCUMENT = "document"


class ProcessingStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VariantType:
    THUMBNAIL = "thumbnail"
    COMPRESSED = "compressed"
    RESIZED = "resized"
    CONVERTED = "converted"


class AnalysisType:
    NSFW = "nsfw"
    OBJECTS = "objects"
    SENTIMENT = "sentiment"
    FACES = "faces"
    TEXT_OCR = "text_ocr"
