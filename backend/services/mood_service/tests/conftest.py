"""
Test configuration for Mood Service
"""

import pytest
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Add the backend directory to the path for shared modules
backend_path = project_root.parent.parent
sys.path.insert(0, str(backend_path))

# Set test environment
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")  # Use test database
os.environ.setdefault("MOOD_SERVICE_PORT", "8003")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Any global test setup can go here
    yield
    # Cleanup after tests