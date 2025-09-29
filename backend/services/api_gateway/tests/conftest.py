"""
Test configuration and fixtures
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from typing import AsyncGenerator
import httpx
from fastapi.testclient import TestClient

from main import app
from registry import ServiceRegistry
from core.models import ServiceInstance, ServiceStatus

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)

@pytest.fixture
async def mock_service_registry():
    """Create a mock service registry with test services"""
    registry = ServiceRegistry()
    
    # Add mock services
    # Use environment variables for test URLs or internal DNS defaults
    auth_url = os.getenv("AUTH_SERVICE_TEST_URL", "http://auth-service:8001")
    mood_url = os.getenv("MOOD_SERVICE_TEST_URL", "http://mood-service:8003")
    
    test_services = [
        ServiceInstance(
            id="auth-test-1",
            name="auth",
            url=auth_url,
            health_path="/health",
            status=ServiceStatus.HEALTHY
        ),
        ServiceInstance(
            id="mood-test-1", 
            name="mood",
            url=mood_url,
            health_path="/health",
            status=ServiceStatus.HEALTHY
        )
    ]
    
    for service in test_services:
        await registry.register_service(service)
    
    return registry

@pytest.fixture
async def mock_backend_server():
    """Mock backend server for testing proxying"""
    # This would typically be implemented with a test server
    # For now, we'll use httpx mock or similar
    pass
