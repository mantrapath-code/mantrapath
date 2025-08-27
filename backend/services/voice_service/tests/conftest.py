"""
Test Configuration and Fixtures
"""
import pytest
import asyncio
import tempfile
import os
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Generator
import httpx
from fastapi.testclient import TestClient
from faker import Faker

# Import voice service components
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from core.models import AudioData, AudioFormat, VoiceResponse, VoiceCommand, CommandType
from core.exceptions import VoiceServiceError
from engines.engine_manager import VoiceEngineManager
from services.voice_service import VoiceProcessingService
from services.command_processor import VoiceCommandProcessor
from services.profile_service import VoiceProfileService
from services.integration_service import ServiceIntegrationManager

fake = Faker()

@pytest.fixture
def test_client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def mock_auth_token():
    """Mock authentication token"""
    return "test_jwt_token_123"

@pytest.fixture
def mock_user_data():
    """Mock user authentication data"""
    return {
        "user_id": "test_user_123",
        "username": "testuser",
        "email": "test@example.com",
        "is_admin": False,
        "token": "test_jwt_token_123"
    }

@pytest.fixture
def mock_admin_data():
    """Mock admin authentication data"""
    return {
        "user_id": "admin_user_123", 
        "username": "admin",
        "email": "admin@example.com",
        "is_admin": True,
        "token": "admin_jwt_token_123"
    }

@pytest.fixture
def sample_audio_data():
    """Create sample audio data for testing"""
    # Create a simple WAV file content (mock)
    audio_content = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xAC\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    
    return AudioData(
        data=audio_content,
        format=AudioFormat.WAV,
        file_size=len(audio_content),
        duration=1.5,
        filename="test_audio.wav"
    )

@pytest.fixture
def sample_voice_command():
    """Create sample voice command"""
    return VoiceCommand(
        text="start meditation",
        command_type=CommandType.START_MEDITATION,
        language="en",
        confidence=0.9,
        parameters={},
        context={"source": "test"}
    )

@pytest.fixture
def mock_engine_manager():
    """Mock voice engine manager"""
    manager = AsyncMock(spec=VoiceEngineManager)
    
    # Mock successful initialization
    manager.initialize_engines.return_value = None
    manager.cleanup.return_value = None
    
    # Mock health status
    manager.get_health_status.return_value = {
        "status": "healthy",
        "stt_engines": ["whisper"],
        "tts_engines": ["elevenlabs"],
        "emotion_engines": []
    }
    
    # Mock transcription
    manager.transcribe_audio.return_value = MagicMock(
        text="Hello world",
        language="en",
        confidence=0.95,
        processing_time_ms=150.0,
        engine_used="whisper"
    )
    
    # Mock speech synthesis
    manager.synthesize_speech.return_value = AudioData(
        data=b"mock_audio_data",
        format=AudioFormat.WAV,
        file_size=1000,
        duration=2.0
    )
    
    # Mock emotion analysis
    manager.analyze_emotion.return_value = MagicMock(
        primary_emotion="neutral",
        emotions={"neutral": 0.8, "happy": 0.2},
        confidence=0.8,
        processing_time_ms=100.0
    )
    
    return manager

@pytest.fixture
def mock_integration_manager():
    """Mock service integration manager"""
    manager = AsyncMock(spec=ServiceIntegrationManager)
    
    # Mock authentication
    manager.verify_user_authentication.return_value = {
        "user_id": "test_user_123",
        "username": "testuser", 
        "is_admin": False,
        "token": "test_jwt_token_123"
    }
    
    # Mock other service calls
    manager.get_user_profile.return_value = {"name": "Test User", "preferences": {}}
    manager.translate_text.return_value = {"translated_text": "translated"}
    manager.send_notification.return_value = True
    manager.log_user_activity.return_value = True
    manager.update_mood_tracking.return_value = True
    manager.register_with_api_gateway.return_value = True
    
    manager.get_integration_stats.return_value = {
        "total_requests": 100,
        "successful_requests": 95,
        "failed_requests": 5,
        "success_rate": 0.95
    }
    
    return manager

@pytest.fixture
def mock_voice_processing():
    """Mock voice processing service"""
    service = AsyncMock(spec=VoiceProcessingService)
    
    service.process_speech_to_text.return_value = VoiceResponse(
        success=True,
        message="Speech converted to text successfully",
        data={
            "transcription": {
                "text": "Hello world",
                "language": "en",
                "confidence": 0.95
            },
            "processing_time_ms": 150.0
        }
    )
    
    service.process_text_to_speech.return_value = AudioData(
        data=b"mock_audio_data",
        format=AudioFormat.WAV,
        file_size=1000,
        duration=2.0
    )
    
    service.analyze_voice_emotion.return_value = VoiceResponse(
        success=True,
        message="Emotion analysis completed",
        data={
            "emotion_analysis": {
                "primary_emotion": "neutral",
                "confidence": 0.8
            }
        }
    )
    
    service.get_supported_features.return_value = {
        "supported_languages": ["en", "hi", "es"],
        "features": {
            "speech_to_text": True,
            "text_to_speech": True,
            "emotion_analysis": True
        }
    }
    
    service.get_processing_stats.return_value = {
        "total_requests": 50,
        "successful_requests": 48,
        "success_rate": 0.96
    }
    
    return service

@pytest.fixture
def mock_command_processor():
    """Mock command processor"""
    processor = AsyncMock(spec=VoiceCommandProcessor)
    
    processor.process_voice_command.return_value = VoiceResponse(
        success=True,
        message="Command processed successfully",
        data={
            "action": "start_meditation",
            "command_type": "START_MEDITATION"
        }
    )
    
    processor.get_supported_commands.return_value = [
        {
            "pattern": "start.*meditation",
            "command_type": "START_MEDITATION",
            "language": "en"
        }
    ]
    
    processor.get_command_stats.return_value = {
        "total_commands": 20,
        "successful_commands": 19,
        "success_rate": 0.95
    }
    
    return processor

@pytest.fixture
def mock_profile_service():
    """Mock profile service"""
    service = AsyncMock(spec=VoiceProfileService)
    
    service.create_voice_profile.return_value = VoiceResponse(
        success=True,
        message="Voice profile created successfully",
        data={"profile_id": "test_profile_123"}
    )
    
    service.get_user_profiles.return_value = [
        MagicMock(
            profile_id="test_profile_123",
            profile_name="Test Profile",
            language="en",
            is_active=True
        )
    ]
    
    service.get_training_status.return_value = VoiceResponse(
        success=True,
        message="Training status retrieved",
        data={
            "training_status": "completed",
            "training_progress": 1.0
        }
    )
    
    service.get_service_stats.return_value = {
        "total_profiles": 5,
        "active_profiles": 4
    }
    
    return service

@pytest.fixture
async def setup_test_environment():
    """Set up test environment with mocked services"""
    with patch('main.engine_manager') as mock_engine, \
         patch('main.voice_processing') as mock_voice, \
         patch('main.command_processor') as mock_command, \
         patch('main.profile_service') as mock_profile, \
         patch('main.integration_manager') as mock_integration:
        
        # Configure mocks
        mock_engine.get_health_status.return_value = {"status": "healthy"}
        mock_integration.get_integration_stats.return_value = {"success_rate": 1.0}
        mock_voice.get_processing_stats.return_value = {"uptime_seconds": 3600}
        
        yield {
            "engine_manager": mock_engine,
            "voice_processing": mock_voice, 
            "command_processor": mock_command,
            "profile_service": mock_profile,
            "integration_manager": mock_integration
        }

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Test utilities

def create_test_audio_file() -> bytes:
    """Create a minimal valid WAV file for testing"""
    # Minimal WAV header + 1 second of silence
    wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00D\xac\x00\x00\x10\xb1\x02\x00\x04\x00\x10\x00data\x00\x00\x00\x00'
    silence_data = b'\x00' * 8000  # 1 second of silence at 8kHz
    return wav_header + silence_data

async def mock_auth_response(token: str) -> Dict[str, Any]:
    """Mock authentication response"""
    if token == "admin_jwt_token_123":
        return {
            "user_id": "admin_user_123",
            "username": "admin", 
            "is_admin": True,
            "token": token
        }
    else:
        return {
            "user_id": "test_user_123",
            "username": "testuser",
            "is_admin": False, 
            "token": token
        }

# Test data generators

def generate_test_commands(language: str = "en", count: int = 5) -> list:
    """Generate test voice commands"""
    commands = []
    command_types = [
        CommandType.START_MEDITATION,
        CommandType.STOP_MEDITATION,
        CommandType.PLAY_MUSIC,
        CommandType.NAVIGATE_HOME,
        CommandType.HELP
    ]
    
    for i in range(count):
        commands.append(VoiceCommand(
            text=fake.sentence(),
            command_type=fake.random_element(command_types),
            language=language,
            confidence=fake.random.uniform(0.7, 1.0),
            parameters={},
            context={"test": True, "index": i}
        ))
    
    return commands
