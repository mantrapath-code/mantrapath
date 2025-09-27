"""
Test configuration and fixtures for Action Orchestrator Service
"""
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List, Optional

# Test configuration
TEST_CONFIG: Dict[str, Any] = {
    "database_url": "sqlite:///test.db",
    "redis_url": os.getenv("REDIS_TEST_URL", "redis://redis:6379/15"),  # Test database
    "nats_url": os.getenv("NATS_TEST_URL", "nats://nats-server:4222"),
    "service_urls": {
        "mood_service": os.getenv("MOOD_SERVICE_TEST_URL", "http://mood-service:8003"),
        "journal_service": os.getenv("JOURNAL_SERVICE_TEST_URL", "http://content-service:8005"), 
        "chatbot_service": os.getenv("CHATBOT_SERVICE_TEST_URL", "http://chatbot-service:8004"),
        "profile_service": os.getenv("PROFILE_SERVICE_TEST_URL", "http://profile-service:8002"),
        "community_service": os.getenv("COMMUNITY_SERVICE_TEST_URL", "http://community-service:8006"),
        "analytics_service": os.getenv("ANALYTICS_SERVICE_TEST_URL", "http://ml-service:8008"),
        "notification_service": os.getenv("NOTIFICATION_SERVICE_TEST_URL", "http://notification-service:8007")
    },
    "jwt_secret": "test-secret-key",
    "max_workflow_steps": 5,
    "default_timeout": 10,
    "max_retries": 2,
    "circuit_breaker_threshold": 3
}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_httpx_client():
    """Mock HTTPX client for testing service calls"""
    client = AsyncMock()
    client.post = AsyncMock()
    client.get = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def mock_nats_client():
    """Mock NATS client for testing event publishing"""
    client = AsyncMock()
    client.publish = AsyncMock()
    client.subscribe = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def sample_voice_intent() -> Dict[str, Any]:
    """Sample voice intent for testing"""
    return {
        "text": "I want to journal about my meditation today",
        "language": "en",
        "confidence": 0.95,
        "metadata": {
            "duration": 3.2,
            "audio_quality": "good"
        }
    }


@pytest.fixture
def sample_cultural_context() -> Dict[str, Any]:
    """Sample cultural context for testing"""
    return {
        "country": "US",
        "timezone": "America/New_York",
        "language": "en",
        "cultural_preferences": {
            "communication_style": "direct",
            "formality_level": "casual"
        }
    }


@pytest.fixture
def sample_workflow_steps() -> list[Dict[str, Any]]:
    """Sample workflow steps for testing"""
    return [
        {
            "step_id": "step_1",
            "service": "mood_service",
            "action": "create_mood_entry",
            "parameters": {
                "user_id": "user123",
                "mood_level": 8,
                "notes": "Feeling great after meditation"
            },
            "dependencies": [],
            "timeout": 30
        },
        {
            "step_id": "step_2", 
            "service": "journal_service",
            "action": "create_entry",
            "parameters": {
                "user_id": "user123",
                "title": "Today's Meditation",
                "content": "Had a wonderful meditation session",
                "tags": ["meditation", "wellness"]
            },
            "dependencies": ["step_1"],
            "timeout": 30
        }
    ]


@pytest.fixture
def mock_service_response():
    """Mock service response for testing"""
    def _create_response(status_code: int = 200, data: Dict[str, Any] | None = None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = data or {"success": True, "id": "test_id"}
        response.text = str(data or {"success": True})
        return response
    return _create_response


@pytest.fixture
def mock_intent_classifier():
    """Mock intent classifier for testing"""
    classifier = AsyncMock()
    classifier.classify_intent = AsyncMock(return_value={
        "intent_type": "journal_creation",
        "confidence": 0.95,
        "entities": {
            "activity": "meditation",
            "sentiment": "positive"
        },
        "suggested_services": ["journal_service", "mood_service"]
    })
    return classifier


@pytest.fixture
def mock_cultural_processor():
    """Mock cultural processor for testing"""
    processor = AsyncMock()
    processor.adapt_workflow = AsyncMock()
    processor.localize_content = AsyncMock()
    return processor


@pytest.fixture
def mock_workflow_builder():
    """Mock workflow builder for testing"""
    builder = AsyncMock()
    builder.build_workflow = AsyncMock()
    return builder


@pytest.fixture
def mock_action_dispatcher():
    """Mock action dispatcher for testing"""
    dispatcher = AsyncMock()
    dispatcher.execute_action = AsyncMock()
    return dispatcher


@pytest.fixture
def mock_rollback_manager():
    """Mock rollback manager for testing"""
    manager = AsyncMock()
    manager.rollback_workflow = AsyncMock()
    manager.register_rollback_action = AsyncMock()
    return manager
