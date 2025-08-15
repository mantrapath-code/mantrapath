"""
Pytest configuration and fixtures for comprehensive testing
"""
import pytest
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any
import sys
import os
from pathlib import Path
import json
import tempfile

# Add the translation service directory and backend directory to Python path
current_dir = Path(__file__).parent
service_dir = current_dir.parent
backend_dir = service_dir.parent.parent
sys.path.insert(0, str(service_dir))
sys.path.insert(0, str(backend_dir))

# Test configuration
TEST_CONFIG = {
    "REDIS_URL": "redis://localhost:6379",
    "DATABASE_URL": "sqlite:///test.db",
    "JWT_SECRET_KEY": "test_secret_key",
    "DEBUG": "true",
    "HOST": "localhost",
    "PORT": "8010"
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    mock = AsyncMock()
    mock.ping = AsyncMock(return_value=True)
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    mock.close = AsyncMock()
    return mock

@pytest.fixture
def mock_event_bus():
    """Mock event bus"""
    mock = AsyncMock()
    mock.publish = AsyncMock()
    return mock

@pytest.fixture
def sample_translation_request():
    """Sample translation request data"""
    return {
        "text": "Hello, welcome to our meditation app",
        "source_language": "en",
        "target_language": "es",
        "engine": "local",
        "domain": "meditation",
        "cultural_adaptation": True,
        "use_custom_glossary": True,
        "use_cache": True
    }

@pytest.fixture
def sample_translation_response():
    """Sample translation response data"""
    return {
        "translated_text": "Hola, bienvenido a nuestra aplicación de meditación",
        "source_language": "en",
        "target_language": "es",
        "confidence_score": 0.95,
        "quality_score": 0.92,
        "engine_used": "local",
        "processing_time_ms": 150,
        "cache_hit": False,
        "cultural_adaptations_applied": ["greeting_formal"],
        "custom_terms_used": ["meditation_app"],
        "request_id": "test_123",
        "status": "completed"
    }

@pytest.fixture
def mock_translation_engine():
    """Mock translation engine"""
    mock = AsyncMock()
    
    # Mock translation method
    mock.translate = AsyncMock(return_value={
        "translated_text": "Hola, bienvenido",
        "source_language": "en",
        "target_language": "es",
        "confidence": 0.95,
        "quality_score": 0.92,
        "engine": "local",
        "processing_time_ms": 150,
        "cache_hit": False,
        "cultural_notes": ["greeting_formal"],
        "custom_terms_used": ["meditation"]
    })
    
    # Mock batch translation
    mock.translate_batch = AsyncMock(return_value=[
        {
            "status": "success",
            "translated_text": "Hola",
            "source_language": "en",
            "target_language": "es",
            "confidence_score": 0.95,
            "quality_score": 0.92,
            "engine": "local",
            "processing_time_ms": 100,
            "cache_hit": False
        }
    ])
    
    # Mock language detection
    mock.detect_language = AsyncMock(return_value={
        "language": "en",
        "confidence": 0.95
    })
    
    # Mock health check
    mock.health_check = AsyncMock(return_value={
        "status": "healthy",
        "engines": ["local", "google", "indic"],
        "supported_languages": ["en", "es", "hi", "fr", "de"]
    })
    
    # Mock initialization
    mock.initialize = AsyncMock(return_value=True)
    
    return mock

@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    user = MagicMock()
    user.id = "test_user_123"
    user.email = "test@example.com"
    return user

@pytest.fixture
def auth_headers():
    """Authentication headers for requests"""
    return {"Authorization": "Bearer test_token"}

@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write('{"test": "data"}')
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass

@pytest.fixture
def mock_settings():
    """Mock settings configuration"""
    settings = MagicMock()
    settings.redis_url = "redis://localhost:6379"
    settings.database_url = "sqlite:///test.db"
    settings.host = "localhost"
    settings.port = 8010
    settings.debug = True
    settings.service_version = "1.0.0"
    return settings

@pytest.fixture
def translation_test_cases():
    """Test cases for different language pairs"""
    return [
        {
            "text": "peace and love",
            "source": "en",
            "target": "es",
            "expected_contains": ["paz", "amor"]
        },
        {
            "text": "meditation and mindfulness",
            "source": "en",
            "target": "hi",
            "expected_contains": ["ध्यान", "सचेतन"]
        },
        {
            "text": "inner wisdom",
            "source": "en", 
            "target": "zh",
            "expected_contains": ["智慧"]
        },
        {
            "text": "breathe deeply",
            "source": "en",
            "target": "fr",
            "expected_contains": ["respirer", "profond"]
        }
    ]

@pytest.fixture
def cultural_adaptation_cases():
    """Test cases for cultural adaptation"""
    return [
        {
            "text": "Good morning",
            "source": "en",
            "target": "es",
            "region": "spain",
            "expected_adaptation": "formal_greeting"
        },
        {
            "text": "Namaste",
            "source": "en",
            "target": "hi", 
            "region": "india",
            "expected_adaptation": "spiritual_greeting"
        }
    ]

@pytest.fixture
def error_test_cases():
    """Test cases for error scenarios"""
    return [
        {
            "case": "empty_text",
            "text": "",
            "expected_error": "EmptyTextError"
        },
        {
            "case": "unsupported_language",
            "text": "Hello",
            "target": "xyz",
            "expected_error": "UnsupportedLanguageError"
        },
        {
            "case": "invalid_text_type",
            "text": None,
            "expected_error": "InvalidTextError"
        }
    ]

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set environment variables for testing
    os.environ.update(TEST_CONFIG)
    
    yield
    
    # Cleanup after test
    for key in TEST_CONFIG.keys():
        if key in os.environ:
            del os.environ[key]
