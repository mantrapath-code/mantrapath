"""
Media Service Configuration Management
"""

import os
from typing import Dict, Any, List, Tuple
from pydantic_settings import BaseSettings


class MediaServiceSettings(BaseSettings):
    """Media Service Configuration Settings"""
    
    # Service Configuration
    service_name: str = "media_service"
    service_port: int = 8009
    service_host: str = "0.0.0.0"
    
    # Database Configuration
    database_url: str = ""
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    celery_broker_url: str = "redis://localhost:6379"
    celery_result_backend: str = "redis://localhost:6379"
    
    # Storage Configuration
    primary_storage_provider: str = "local"
    local_storage_path: str = "./uploads"
    local_url_prefix: str = "/static/uploads"
    
    # AWS S3 Configuration
    aws_s3_bucket: str = ""
    aws_region: str = "us-east-1"
    aws_access_key: str = ""
    aws_secret_key: str = ""
    
    # MinIO Configuration
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "mantrapath-media-dev"
    minio_secure: bool = False
    
    # CDN Configuration
    cdn_provider: str = ""
    cdn_base_url: str = ""
    cloudflare_zone_id: str = ""
    cloudflare_api_token: str = ""
    
    # Security Configuration
    upload_virus_scanning: bool = False
    clamav_host: str = "localhost"
    clamav_port: int = 3310
    max_upload_size: str = "500MB"
    allowed_domains: List[str] = ["localhost"]
    
    # Processing Configuration
    image_quality_default: int = 85
    thumbnail_size: str = "300x300"
    video_compression_preset: str = "medium"
    audio_bitrate_default: str = "128k"
    
    # Monitoring Configuration
    sentry_dsn: str = ""
    metrics_enabled: bool = True
    log_level: str = "INFO"
    
    # JWT Configuration (inherited from shared auth)
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "env_prefix": "",
        "extra": "ignore"
    }


# Global settings instance
settings = MediaServiceSettings()


def get_max_file_size() -> int:
    """Parse and return max file size in bytes"""
    size_str = settings.max_upload_size.upper()
    
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        # Assume bytes
        return int(size_str)


def get_thumbnail_size() -> Tuple[int, int]:
    """Parse and return thumbnail size as tuple"""
    size_str = settings.thumbnail_size
    width, height = map(int, size_str.split('x'))
    return (width, height)


# File type configurations
ALLOWED_FILE_TYPES = {
    "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
    "audio": ["mp3", "wav", "ogg", "m4a", "flac"],
    "video": ["mp4", "avi", "mov", "wmv", "flv", "webm"],
    "document": ["pdf", "doc", "docx", "txt", "md"]
}

# MIME type mapping
MIME_TYPE_MAPPING = {
    # Images
    "image/jpeg": "image",
    "image/jpg": "image",
    "image/png": "image",
    "image/gif": "image",
    "image/webp": "image",
    "image/svg+xml": "image",
    
    # Audio
    "audio/mpeg": "audio",
    "audio/mp3": "audio",
    "audio/wav": "audio",
    "audio/ogg": "audio",
    "audio/mp4": "audio",
    "audio/flac": "audio",
    
    # Video
    "video/mp4": "video",
    "video/avi": "video",
    "video/quicktime": "video",
    "video/x-ms-wmv": "video",
    "video/x-flv": "video",
    "video/webm": "video",
    
    # Documents
    "application/pdf": "document",
    "application/msword": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "text/plain": "document",
    "text/markdown": "document"
}

# File size limits by type (in bytes)
MAX_FILE_SIZES = {
    "image": 10 * 1024 * 1024,      # 10MB
    "audio": 100 * 1024 * 1024,     # 100MB
    "video": 500 * 1024 * 1024,     # 500MB
    "document": 5 * 1024 * 1024      # 5MB
}


def get_file_category(mime_type: str) -> str:
    """Get file category from MIME type"""
    return MIME_TYPE_MAPPING.get(mime_type, "other")


def is_allowed_mime_type(mime_type: str) -> bool:
    """Check if MIME type is allowed"""
    return mime_type in MIME_TYPE_MAPPING


def get_max_size_for_type(file_category: str) -> int:
    """Get maximum file size for file category"""
    return MAX_FILE_SIZES.get(file_category, get_max_file_size())
