"""Unified Insights Cache Abstraction (E2)

Redis-based TTL cache with in-memory fallback for enhanced scalability.
Supports both Redis and in-memory implementations.
"""
from __future__ import annotations
import time
import json
import os
from typing import Any, Optional, Tuple, Dict
import logging

# Redis imports with fallback
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

from __future__ import annotations
"""Unified Insights Cache Abstraction (E2)

Redis-based TTL cache with in-memory fallback for enhanced scalability.
Supports both Redis and in-memory implementations.
"""
import time
import json
import os
from typing import Any, Optional, Tuple, Dict, List
import logging

# Redis imports with fallback
try:
    import redis
    redis_available = True
except ImportError:
    redis_available = False

logger = logging.getLogger(__name__)

class CacheInterface:
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        raise NotImplementedError
    def invalidate(self, key: str) -> None:
        raise NotImplementedError
    def clear(self) -> None:
        raise NotImplementedError

class RedisTTLCache(CacheInterface):
    """Redis-based TTL cache implementation"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.connected = False
        
        if not redis_available:
            logger.warning("Redis not available, cache operations will be no-op")
            return
            
        # Try multiple Redis URLs
        redis_urls: List[str] = []
        if redis_url:
            redis_urls.append(redis_url)
        
        # Add environment variable URLs
        env_redis_url = os.getenv('REDIS_URL')
        if env_redis_url:
            redis_urls.append(env_redis_url)
            
        # Add default URLs
        redis_urls.extend([
            "redis://redis:6379",
            "redis://localhost:6379"
        ])
        
        # Try to connect to Redis
        for url in redis_urls:
            try:
                self.redis_client = redis.from_url(url, decode_responses=True, socket_timeout=5)  # type: ignore
                # Test the connection
                self.redis_client.ping()  # type: ignore
                self.connected = True
                logger.info(f"Connected to Redis at {url}")
                break
            except Exception as e:
                logger.debug(f"Failed to connect to Redis at {url}: {e}")
                continue
        
        if not self.connected:
            logger.warning("Failed to connect to Redis, cache operations will be no-op")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self.connected or not self.redis_client:
            return None
            
        try:
            data = self.redis_client.get(key)  # type: ignore
            if data is None:
                return None
            return json.loads(data)
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Set value in Redis cache with TTL"""
        if not self.connected or not self.redis_client:
            return
            
        try:
            data = json.dumps(value)
            self.redis_client.setex(key, ttl_seconds, data)  # type: ignore
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
    
    def invalidate(self, key: str) -> None:
        """Remove key from Redis cache"""
        if not self.connected or not self.redis_client:
            return
            
        try:
            self.redis_client.delete(key)  # type: ignore
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
    
    def clear(self) -> None:
        """Clear all cache entries (for testing)"""
        if not self.connected or not self.redis_client:
            return
            
        try:
            # Clear only keys with our pattern
            pattern = "unified_insights:*"
            keys = self.redis_client.keys(pattern)  # type: ignore
            if keys:
                self.redis_client.delete(*keys)  # type: ignore
        except Exception as e:
            logger.error(f"Redis clear error: {e}")

class InMemoryTTLCache(CacheInterface):
    """In-memory TTL cache implementation (fallback)"""
    
    def __init__(self):
        self._store: Dict[str, Tuple[float, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        expires, value = item
        if time.time() > expires:
            self._store.pop(key, None)
            return None
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + ttl_seconds, value)
    
    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries (for testing)"""
        self._store.clear()

def get_cache() -> CacheInterface:
    """Get cache implementation - Redis if available, in-memory fallback"""
    # Try Redis first
    redis_cache = RedisTTLCache()
    if redis_cache.connected:
        logger.info("Using Redis cache for unified insights")
        return redis_cache
    
    # Fallback to in-memory cache
    logger.info("Using in-memory cache for unified insights (Redis not available)")
    return InMemoryTTLCache()
