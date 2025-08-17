"""
Redis Manager for Voice Event Processor
"""

import logging
import redis.asyncio as redis
from typing import Optional, Any

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis connection manager"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.redis: Optional[redis.Redis] = None
        
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=False  # Keep as bytes for audio data
            )
            # Test connection
            await self.redis.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}/{self.db}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    async def ping(self) -> bool:
        """Check if Redis is connected"""
        try:
            if self.redis:
                await self.redis.ping()
                return True
        except Exception:
            pass
        return False
    
    # Delegate Redis operations
    async def get(self, key: str) -> Optional[bytes]:
        """Get value from Redis"""
        if self.redis:
            return await self.redis.get(key)
        return None
    
    async def set(self, key: str, value: Any) -> bool:
        """Set value in Redis"""
        if self.redis:
            return await self.redis.set(key, value)
        return False
    
    async def setex(self, key: str, time: int, value: Any) -> bool:
        """Set value with expiration"""
        if self.redis:
            return await self.redis.setex(key, time, value)
        return False
    
    async def lpush(self, key: str, *values) -> int:
        """Left push to list"""
        if self.redis:
            return await self.redis.lpush(key, *values)
        return 0
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get range from list"""
        if self.redis:
            return await self.redis.lrange(key, start, end)
        return []
    
    async def expire(self, key: str, time: int) -> bool:
        """Set key expiration"""
        if self.redis:
            return await self.redis.expire(key, time)
        return False
