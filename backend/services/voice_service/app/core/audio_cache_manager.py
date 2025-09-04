"""
Audio Cache Manager
Manages audio caching for performance optimization
"""
import logging
import hashlib
import os
import json
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import redis

logger = logging.getLogger(__name__)

@dataclass
class CachedAudio:
    """Cached audio data structure"""
    cache_key: str
    audio_data: bytes
    content_type: str
    sample_rate: int
    duration: float
    model_used: str
    created_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class AudioCacheManager:
    """Manages audio caching for TTS and processed audio"""
    
    def __init__(self, redis_url: Optional[str] = None, cache_dir: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.cache_dir = cache_dir or os.getenv("AUDIO_CACHE_DIR", "/tmp/voice_cache")
        self.redis_client = None
        self.cache_ttl_hours = 24
        self.max_cache_size_mb = 500
        self.key_prefix = "audio_cache:"
        self.metadata_prefix = "audio_meta:"
        
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize cache storage (Redis + file system)"""
        # Initialize Redis for metadata
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=False)
            self.redis_client.ping()
            logger.info("Connected to Redis for audio cache metadata")
        except Exception as e:
            logger.warning(f"Redis not available for audio cache: {e}")
            self.redis_client = None
        
        # Initialize file system cache
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Audio cache directory: {self.cache_dir}")
        except Exception as e:
            logger.error(f"Failed to create cache directory: {e}")
            self.cache_dir = "/tmp"
    
    def _generate_cache_key(self, text: str, language: str, voice: Optional[str] = None,
                          model: Optional[str] = None) -> str:
        """Generate cache key for audio content"""
        content = f"{text}|{language}|{voice or 'default'}|{model or 'default'}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_file_path(self, cache_key: str) -> str:
        """Get file path for cached audio"""
        return os.path.join(self.cache_dir, f"{cache_key}.wav")
    
    def _get_metadata_key(self, cache_key: str) -> str:
        """Get Redis key for audio metadata"""
        return f"{self.metadata_prefix}{cache_key}"
    
    def cache_audio(self, text: str, language: str, audio_data: bytes,
                   content_type: str, sample_rate: int, duration: float,
                   model_used: str, voice: Optional[str] = None) -> str:
        """Cache audio data"""
        cache_key = self._generate_cache_key(text, language, voice, model_used)
        
        try:
            # Store audio file
            file_path = self._get_file_path(cache_key)
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            
            # Store metadata
            cached_audio = CachedAudio(
                cache_key=cache_key,
                audio_data=b"",  # Don't store in memory, use file
                content_type=content_type,
                sample_rate=sample_rate,
                duration=duration,
                model_used=model_used,
                created_at=datetime.now()
            )
            
            self._store_metadata(cached_audio)
            logger.debug(f"Cached audio: {cache_key}")
            return cache_key
            
        except Exception as e:
            logger.error(f"Failed to cache audio: {e}")
            return ""
    
    def get_cached_audio(self, text: str, language: str, voice: Optional[str] = None,
                        model: Optional[str] = None) -> Optional[CachedAudio]:
        """Retrieve cached audio"""
        cache_key = self._generate_cache_key(text, language, voice, model)
        
        try:
            # Check if file exists
            file_path = self._get_file_path(cache_key)
            if not os.path.exists(file_path):
                return None
            
            # Get metadata
            metadata = self._get_metadata(cache_key)
            if not metadata:
                return None
            
            # Read audio data
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            
            # Update access statistics
            metadata.access_count += 1
            metadata.last_accessed = datetime.now()
            metadata.audio_data = audio_data
            
            self._store_metadata(metadata)
            
            logger.debug(f"Retrieved cached audio: {cache_key}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to retrieve cached audio: {e}")
            return None
    
    def is_cached(self, text: str, language: str, voice: Optional[str] = None,
                 model: Optional[str] = None) -> bool:
        """Check if audio is cached"""
        cache_key = self._generate_cache_key(text, language, voice, model)
        file_path = self._get_file_path(cache_key)
        
        # Check file exists and metadata exists
        if not os.path.exists(file_path):
            return False
        
        if self.redis_client:
            metadata_key = self._get_metadata_key(cache_key)
            return self.redis_client.exists(metadata_key)
        
        return True
    
    def invalidate_cache(self, cache_key: str) -> bool:
        """Remove item from cache"""
        try:
            # Remove file
            file_path = self._get_file_path(cache_key)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Remove metadata
            if self.redis_client:
                metadata_key = self._get_metadata_key(cache_key)
                self.redis_client.delete(metadata_key)
            
            logger.debug(f"Invalidated cache: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return False
    
    def cleanup_expired_cache(self) -> int:
        """Clean up expired cache entries"""
        cleaned_count = 0
        cutoff_time = datetime.now() - timedelta(hours=self.cache_ttl_hours)
        
        try:
            if self.redis_client:
                # Find expired entries using Redis metadata
                pattern = f"{self.metadata_prefix}*"
                keys = self.redis_client.scan_iter(match=pattern)
                
                for key in keys:
                    try:
                        metadata_json = self.redis_client.get(key)
                        if metadata_json:
                            metadata_dict = json.loads(metadata_json.decode())
                            created_at = datetime.fromisoformat(metadata_dict["created_at"])
                            
                            if created_at < cutoff_time:
                                cache_key = metadata_dict["cache_key"]
                                if self.invalidate_cache(cache_key):
                                    cleaned_count += 1
                    except Exception as e:
                        logger.error(f"Error cleaning cache entry: {e}")
            else:
                # Fallback: check file system
                if os.path.exists(self.cache_dir):
                    for filename in os.listdir(self.cache_dir):
                        if filename.endswith('.wav'):
                            file_path = os.path.join(self.cache_dir, filename)
                            try:
                                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                                if file_time < cutoff_time:
                                    os.remove(file_path)
                                    cleaned_count += 1
                            except Exception as e:
                                logger.error(f"Error cleaning file {filename}: {e}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired cache entries")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
        
        return cleaned_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            "total_entries": 0,
            "total_size_mb": 0.0,
            "storage_type": "redis+file" if self.redis_client else "file_only",
            "cache_directory": self.cache_dir
        }
        
        try:
            if os.path.exists(self.cache_dir):
                total_size = 0
                file_count = 0
                
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.wav'):
                        file_path = os.path.join(self.cache_dir, filename)
                        try:
                            file_size = os.path.getsize(file_path)
                            total_size += file_size
                            file_count += 1
                        except Exception:
                            pass
                
                stats["total_entries"] = file_count
                stats["total_size_mb"] = total_size / (1024 * 1024)
            
            # Add Redis metadata stats
            if self.redis_client:
                pattern = f"{self.metadata_prefix}*"
                metadata_keys = list(self.redis_client.scan_iter(match=pattern))
                stats["metadata_entries"] = len(metadata_keys)
                
                # Calculate access statistics
                total_access_count = 0
                for key in metadata_keys[:100]:  # Sample first 100 for performance
                    try:
                        metadata_json = self.redis_client.get(key)
                        if metadata_json:
                            metadata_dict = json.loads(metadata_json.decode())
                            total_access_count += metadata_dict.get("access_count", 0)
                    except Exception:
                        pass
                
                stats["average_access_count"] = total_access_count / len(metadata_keys) if metadata_keys else 0
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            stats["error"] = str(e)
        
        return stats
    
    def _store_metadata(self, cached_audio: CachedAudio):
        """Store audio metadata"""
        if not self.redis_client:
            return
        
        try:
            metadata_dict = {
                "cache_key": cached_audio.cache_key,
                "content_type": cached_audio.content_type,
                "sample_rate": cached_audio.sample_rate,
                "duration": cached_audio.duration,
                "model_used": cached_audio.model_used,
                "created_at": cached_audio.created_at.isoformat(),
                "access_count": cached_audio.access_count,
                "last_accessed": cached_audio.last_accessed.isoformat() if cached_audio.last_accessed else None
            }
            
            metadata_key = self._get_metadata_key(cached_audio.cache_key)
            metadata_json = json.dumps(metadata_dict)
            
            # Set with TTL
            self.redis_client.setex(
                metadata_key,
                timedelta(hours=self.cache_ttl_hours),
                metadata_json
            )
            
        except Exception as e:
            logger.error(f"Failed to store metadata: {e}")
    
    def _get_metadata(self, cache_key: str) -> Optional[CachedAudio]:
        """Get audio metadata"""
        if not self.redis_client:
            return None
        
        try:
            metadata_key = self._get_metadata_key(cache_key)
            metadata_json = self.redis_client.get(metadata_key)
            
            if not metadata_json:
                return None
            
            metadata_dict = json.loads(metadata_json.decode())
            
            return CachedAudio(
                cache_key=metadata_dict["cache_key"],
                audio_data=b"",  # Will be loaded from file
                content_type=metadata_dict["content_type"],
                sample_rate=metadata_dict["sample_rate"],
                duration=metadata_dict["duration"],
                model_used=metadata_dict["model_used"],
                created_at=datetime.fromisoformat(metadata_dict["created_at"]),
                access_count=metadata_dict["access_count"],
                last_accessed=datetime.fromisoformat(metadata_dict["last_accessed"]) if metadata_dict["last_accessed"] else None
            )
            
        except Exception as e:
            logger.error(f"Failed to get metadata: {e}")
            return None
    
    def health_check(self) -> Dict[str, Any]:
        """Check cache health"""
        health = {
            "status": "healthy",
            "redis_connection": "active" if self.redis_client else "unavailable",
            "cache_directory": self.cache_dir,
            "directory_writable": os.access(self.cache_dir, os.W_OK) if os.path.exists(self.cache_dir) else False
        }
        
        if self.redis_client:
            try:
                self.redis_client.ping()
                health["redis_ping"] = "success"
            except Exception as e:
                health["status"] = "degraded"
                health["redis_ping"] = "failed"
                health["redis_error"] = str(e)
        
        # Add cache stats to health check
        health.update(self.get_cache_stats())
        
        return health
