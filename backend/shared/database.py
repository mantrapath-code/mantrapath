"""
Shared database configuration and utilities
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import AsyncGenerator, Generator
from .models import Base

class DatabaseConfig:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://mantrapath:password@localhost:5432/mantrapath")
        self.async_database_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        # Create engines
        self.engine = create_engine(
            self.database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        self.async_engine = create_async_engine(
            self.async_database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Create session factories
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        self.AsyncSessionLocal = sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
        )
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get synchronous database session"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get asynchronous database session"""
        async with self.AsyncSessionLocal() as session:
            yield session

# Global database instance
db_config = DatabaseConfig()

# Dependency functions for FastAPI
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for synchronous database sessions"""
    yield from db_config.get_session()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for asynchronous database sessions"""
    async for session in db_config.get_async_session():
        yield session