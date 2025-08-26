"""
Memory Service Test Configuration
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from shared.database import get_db, Base
from shared.auth import get_current_user
from shared.models import User

# Test database URL (SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_memory.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    """Override user dependency for testing"""
    return User(
        id="test_user_123",
        email="test@example.com",
        username="testuser",
        is_active=True
    )

# Override dependencies
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = TestingSessionLocal()
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client() -> Generator:
    """Create a test client"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user():
    """Create a test user"""
    return User(
        id="test_user_123",
        email="test@example.com",
        username="testuser",
        is_active=True
    )

@pytest.fixture
def sample_interaction_data():
    """Sample interaction data for testing"""
    return {
        "interaction_type": "mood",
        "interaction_data": {
            "mood_score": 0.8,
            "mood_label": "happy",
            "energy_level": 0.7,
            "notes": "Feeling great today!"
        },
        "source_service": "mood_service",
        "session_id": "test_session_123",
        "cultural_context": {
            "language": "en",
            "cultural_background": "western"
        },
        "metadata": {
            "platform": "web",
            "device_type": "desktop"
        }
    }
