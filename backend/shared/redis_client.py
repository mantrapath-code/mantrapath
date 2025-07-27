"""
Shared Redis configuration and utilities
"""
import redis
import json
import os
from typing import Any, Optional

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Redis connection
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class RedisCache:
    """Redis caching utility"""
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from Redis"""
        try:
            value = redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in Redis with TTL in seconds"""
        try:
            redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete key from Redis"""
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    @staticmethod
    def publish(channel: str, message: Any) -> bool:
        """Publish message to Redis channel"""
        try:
            redis_client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            print(f"Redis publish error: {e}")
            return False

# Export Redis client for direct use
__all__ = ['redis_client', 'RedisCache']