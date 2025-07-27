"""
Shared database configuration and utilities
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from typing import Generator
import redis
from contextlib import contextmanager

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mantrapath:mantrapath123@localhost:5432/mantrapath")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

def get_database() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    return redis_client

class CacheService:
    """Redis caching service"""
    
    def __init__(self):
        self.redis = get_redis()
    
    async def get(self, key: str):
        """Get value from cache"""
        return self.redis.get(key)
    
    async def set(self, key: str, value: str, expiration: int = 3600):
        """Set value in cache with expiration"""
        return self.redis.setex(key, expiration, value)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        return self.redis.delete(key)
    
    async def exists(self, key: str):
        """Check if key exists in cache"""
        return self.redis.exists(key)

cache_service = CacheService()