"""
Storage Provider Configuration
"""

import os
from typing import Dict, Any, List
from .settings import settings


class StorageConfig:
    """Storage provider configuration management"""
    
    @staticmethod
    def get_storage_config() -> Dict[str, Dict[str, Any]]:
        """Get storage provider configurations"""
        
        return {
            "aws_s3": {
                "bucket_name": settings.aws_s3_bucket,
                "region": settings.aws_region,
                "access_key": settings.aws_access_key,
                "secret_key": settings.aws_secret_key,
                "endpoint_url": None  # Default AWS endpoints
            },
            "minio": {
                "bucket_name": settings.minio_bucket,
                "endpoint_url": settings.minio_endpoint,
                "access_key": settings.minio_access_key,
                "secret_key": settings.minio_secret_key,
                "secure": settings.minio_secure
            },
            "local": {
                "base_path": settings.local_storage_path,
                "url_prefix": settings.local_url_prefix
            }
        }
    
    @staticmethod
    def get_active_storage_config() -> Dict[str, Any]:
        """Get configuration for the active storage provider"""
        configs = StorageConfig.get_storage_config()
        return configs.get(settings.primary_storage_provider, configs["local"])
    
    @staticmethod
    def validate_storage_config() -> bool:
        """Validate current storage configuration"""
        config = StorageConfig.get_active_storage_config()
        provider = settings.primary_storage_provider
        
        if provider == "aws_s3":
            required_fields = ["bucket_name", "access_key", "secret_key"]
            return all(config.get(field) for field in required_fields)
        
        elif provider == "minio":
            required_fields = ["bucket_name", "endpoint_url", "access_key", "secret_key"]
            return all(config.get(field) for field in required_fields)
        
        elif provider == "local":
            return bool(config.get("base_path"))
        
        return False


# CDN Configuration
class CDNConfig:
    """CDN provider configuration management"""
    
    @staticmethod
    def get_cdn_config() -> Dict[str, Any]:
        """Get CDN configuration"""
        
        if settings.cdn_provider == "cloudflare":
            return {
                "provider": "cloudflare",
                "base_url": settings.cdn_base_url,
                "zone_id": settings.cloudflare_zone_id,
                "api_token": settings.cloudflare_api_token
            }
        
        elif settings.cdn_provider == "aws_cloudfront":
            return {
                "provider": "aws_cloudfront",
                "base_url": settings.cdn_base_url,
                "distribution_id": os.getenv("AWS_CLOUDFRONT_DISTRIBUTION_ID", ""),
                "access_key": settings.aws_access_key,
                "secret_key": settings.aws_secret_key
            }
        
        return {"provider": "none"}
    
    @staticmethod
    def is_cdn_enabled() -> bool:
        """Check if CDN is enabled and configured"""
        config = CDNConfig.get_cdn_config()
        return config.get("provider") != "none" and bool(config.get("base_url"))


# Processing Configuration
class ProcessingConfig:
    """Media processing configuration"""
    
    @staticmethod
    def get_image_config() -> Dict[str, Any]:
        """Get image processing configuration"""
        return {
            "quality": settings.image_quality_default,
            "thumbnail_size": settings.thumbnail_size,
            "allowed_formats": ["JPEG", "PNG", "GIF", "WEBP"],
            "max_dimensions": (4096, 4096),  # Max 4K resolution
            "compression_enabled": True
        }
    
    @staticmethod
    def get_video_config() -> Dict[str, Any]:
        """Get video processing configuration"""
        return {
            "compression_preset": settings.video_compression_preset,
            "allowed_formats": ["mp4", "webm", "avi", "mov"],
            "max_duration": 3600,  # Max 1 hour
            "max_resolution": "1920x1080",  # Max Full HD
            "thumbnail_at_seconds": 5  # Generate thumbnail at 5 seconds
        }
    
    @staticmethod
    def get_audio_config() -> Dict[str, Any]:
        """Get audio processing configuration"""
        return {
            "default_bitrate": settings.audio_bitrate_default,
            "allowed_formats": ["mp3", "wav", "ogg", "m4a", "flac"],
            "max_duration": 7200,  # Max 2 hours
            "normalize_audio": True,
            "generate_waveform": True
        }


# Security Configuration
class SecurityConfig:
    """Security configuration management"""
    
    @staticmethod
    def get_upload_limits() -> Dict[str, int]:
        """Get upload size limits by file type"""
        from .settings import MAX_FILE_SIZES
        return MAX_FILE_SIZES
    
    @staticmethod
    def get_allowed_mime_types() -> Dict[str, List[str]]:
        """Get allowed MIME types by category"""
        from .settings import MIME_TYPE_MAPPING
        
        categories: Dict[str, List[str]] = {}
        for mime_type, category in MIME_TYPE_MAPPING.items():
            if category not in categories:
                categories[category] = []
            categories[category].append(mime_type)
        
        return categories
    
    @staticmethod
    def is_virus_scanning_enabled() -> bool:
        """Check if virus scanning is enabled"""
        return settings.upload_virus_scanning
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers for file responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'"
        }
