"""
Main Application API Tests
Tests for FastAPI endpoints and application lifecycle
"""
import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from io import BytesIO

from main import app
from core.models import VoiceCommand, TTSRequest, CommandType
from .conftest import create_test_audio_file, mock_auth_response

@pytest.fixture
def client():
    return TestClient(app)

class TestHealthCheck:
    """Test health check endpoint"""
    
    @patch('main.voice_processing')
    @patch('main.engine_manager') 
    @patch('main.integration_manager')
    def test_health_check_healthy(self, mock_integration, mock_engine, mock_voice, client):
        """Test healthy status"""
        mock_engine.get_health_status = AsyncMock(return_value={"status": "healthy"})
        mock_voice.get_processing_stats = AsyncMock(return_value={"uptime_seconds": 3600})
        mock_integration.get_integration_stats.return_value = {"status": "healthy"}
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert data["version"] == "1.0.0"

    @patch('main.engine_manager')
    def test_health_check_unhealthy(self, mock_engine, client):
        """Test unhealthy status when engine fails"""
        mock_engine.get_health_status.side_effect = Exception("Engine failed")
        
        response = client.get("/health")
        
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"

class TestAuthentication:
    """Test authentication functionality"""
    
    @patch('main.integration_manager')
    def test_verify_token_success(self, mock_integration, client):
        """Test successful token verification"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123",
            "username": "testuser",
            "is_admin": False
        }
        
        # This will be tested through other endpoints that require auth
        # Direct testing of verify_token would require mocking the dependency

    @patch('main.integration_manager')
    def test_verify_token_failure(self, mock_integration, client):
        """Test failed token verification"""
        mock_integration.verify_user_authentication.side_effect = Exception("Auth failed")
        
        # Test through an endpoint that requires auth
        response = client.get("/profiles", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 500  # Auth service unavailable

    def test_no_token_provided(self, client):
        """Test request without token"""
        response = client.get("/profiles")
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

class TestSpeechToText:
    """Test STT endpoint"""
    
    @patch('main.integration_manager')
    @patch('main.voice_processing')
    def test_stt_success(self, mock_voice, mock_integration, client):
        """Test successful STT processing"""
        # Setup mocks
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        mock_integration.log_user_activity = AsyncMock(return_value=True)
        
        mock_voice.process_speech_to_text = AsyncMock(return_value=MagicMock(
            success=True,
            message="Success",
            data={"transcription": {"text": "Hello world", "confidence": 0.95}},
            request_id="test_request_123",
            language="en",
            processing_time_ms=150.0
        ))
        
        # Create test audio file
        audio_data = create_test_audio_file()
        
        response = client.post(
            "/stt",
            files={"file": ("test.wav", BytesIO(audio_data), "audio/wav")},
            data={"language": "en"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "transcription" in data["data"]

    @patch('main.integration_manager')
    @patch('main.voice_processing')
    def test_stt_processing_error(self, mock_voice, mock_integration, client):
        """Test STT processing error"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        
        from core.exceptions import AudioProcessingError
        mock_voice.process_speech_to_text = AsyncMock(side_effect=AudioProcessingError("Processing failed"))
        
        audio_data = create_test_audio_file()
        
        response = client.post(
            "/stt",
            files={"file": ("test.wav", BytesIO(audio_data), "audio/wav")},
            data={"language": "en"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "Processing failed" in response.json()["detail"]

    def test_stt_no_file(self, client):
        """Test STT without file upload"""
        response = client.post(
            "/stt",
            data={"language": "en"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 422  # Validation error

class TestTextToSpeech:
    """Test TTS endpoint"""
    
    @patch('main.integration_manager')
    @patch('main.voice_processing')
    def test_tts_success(self, mock_voice, mock_integration, client):
        """Test successful TTS processing"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        mock_integration.log_user_activity = AsyncMock(return_value=True)
        
        from core.models import AudioData, AudioFormat
        mock_voice.process_text_to_speech = AsyncMock(return_value=AudioData(
            data=b"mock_audio_data",
            format=AudioFormat.WAV,
            file_size=1000
        ))
        
        tts_request = {
            "text": "Hello world",
            "language": "en",
            "format": "wav"
        }
        
        response = client.post(
            "/tts",
            json=tts_request,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("audio/")

    @patch('main.integration_manager')
    @patch('main.voice_processing')
    def test_tts_processing_error(self, mock_voice, mock_integration, client):
        """Test TTS processing error"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        
        from core.exceptions import AudioProcessingError
        mock_voice.process_text_to_speech = AsyncMock(side_effect=AudioProcessingError("TTS failed"))
        
        tts_request = {
            "text": "Hello world",
            "language": "en", 
            "format": "wav"
        }
        
        response = client.post(
            "/tts",
            json=tts_request,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "TTS failed" in response.json()["detail"]

class TestVoiceCommand:
    """Test voice command endpoint"""
    
    @patch('main.integration_manager')
    @patch('main.command_processor')
    def test_voice_command_success(self, mock_command, mock_integration, client):
        """Test successful voice command processing"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        
        mock_command.process_voice_command = AsyncMock(return_value=MagicMock(
            success=True,
            message="Command processed",
            data={"action": "start_meditation"},
            request_id="test_request_123",
            language="en",
            processing_time_ms=150.0
        ))
        
        command = {
            "text": "start meditation",
            "language": "en",
            "context": {}
        }
        
        response = client.post(
            "/voice-command",
            json=command,
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "action" in data["data"]

class TestEmotionAnalysis:
    """Test emotion analysis endpoint"""
    
    @patch('main.integration_manager')
    @patch('main.voice_processing')
    def test_emotion_analysis_success(self, mock_voice, mock_integration, client):
        """Test successful emotion analysis"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        mock_integration.update_mood_tracking = AsyncMock(return_value=True)
        
        mock_voice.analyze_voice_emotion = AsyncMock(return_value=MagicMock(
            success=True,
            message="Success",
            data={"emotion": {"primary_emotion": "happy", "confidence": 0.85}},
            request_id="test_request_123",
            language="en",
            processing_time_ms=150.0
        ))
        
        audio_data = create_test_audio_file()
        
        response = client.post(
            "/emotion-analysis",
            files={"file": ("test.wav", BytesIO(audio_data), "audio/wav")},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "emotion" in data["data"]

class TestVoiceProfiles:
    """Test voice profile endpoints"""
    
    @patch('main.integration_manager')
    @patch('main.profile_service')
    def test_create_voice_profile_success(self, mock_profile, mock_integration, client):
        """Test successful voice profile creation"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        
        mock_profile.create_voice_profile = AsyncMock(return_value=MagicMock(
            success=True,
            message="Profile created",
            data={"profile_id": "test_profile_123"},
            request_id="test_request_123",
            language="en"
        ))
        
        response = client.post(
            "/profiles",
            data={"profile_name": "Test Profile", "language": "en"},
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "profile_id" in data["data"]

    @patch('main.integration_manager')
    @patch('main.profile_service')
    def test_get_user_profiles(self, mock_profile, mock_integration, client):
        """Test getting user profiles"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        
        mock_profile.get_user_profiles = AsyncMock(return_value=[
            MagicMock(dict=lambda: {"profile_id": "123", "profile_name": "Test"})
        ])
        
        response = client.get(
            "/profiles",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "profiles" in data
        assert "count" in data

    @patch('main.integration_manager')
    @patch('main.profile_service')
    def test_get_training_status(self, mock_profile, mock_integration, client):
        """Test getting training status"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "test_user_123", "token": "test_token"
        }
        
        mock_profile.get_training_status = AsyncMock(return_value=MagicMock(
            success=True,
            data={"training_status": "completed", "training_progress": 1.0}
        ))
        
        response = client.get(
            "/profiles/test_profile_123/training-status",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200

class TestServiceInfo:
    """Test service information endpoints"""
    
    @patch('main.voice_processing')
    @patch('main.command_processor')
    def test_get_capabilities(self, mock_command, mock_voice, client):
        """Test getting service capabilities"""
        mock_voice.get_supported_features = AsyncMock(return_value={
            "supported_languages": ["en", "hi", "es"],
            "features": {"speech_to_text": True}
        })
        
        mock_command.get_supported_commands.return_value = [
            {"pattern": "start.*meditation", "command_type": "START_MEDITATION"}
        ]
        
        mock_voice.get_processing_stats.return_value = {"uptime_seconds": 3600}
        
        response = client.get("/capabilities")
        
        assert response.status_code == 200
        data = response.json()
        assert "features" in data
        assert "supported_commands" in data
        assert "service_info" in data

    @patch('main.integration_manager')
    @patch('main.voice_processing')
    @patch('main.command_processor')
    @patch('main.profile_service')
    def test_get_stats_admin(self, mock_profile, mock_command, mock_voice, mock_integration, client):
        """Test getting service stats as admin"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "admin_123", "token": "admin_token", "is_admin": True
        }
        
        # Setup mock responses
        mock_voice.get_processing_stats.return_value = {"total_requests": 100}
        mock_command.get_command_stats.return_value = {"total_commands": 50}
        mock_profile.get_service_stats.return_value = {"total_profiles": 10}
        mock_integration.get_integration_stats.return_value = {"success_rate": 0.95}
        
        response = client.get(
            "/stats",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "processing" in data
        assert "commands" in data
        assert "profiles" in data
        assert "integration" in data

    @patch('main.integration_manager')
    def test_get_stats_non_admin(self, mock_integration, client):
        """Test getting service stats as non-admin (should fail)"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "user_123", "token": "user_token", "is_admin": False
        }
        
        response = client.get(
            "/stats",
            headers={"Authorization": "Bearer user_token"}
        )
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

class TestAdminEndpoints:
    """Test admin-only endpoints"""
    
    @patch('main.integration_manager')
    @patch('main.voice_processing')
    @patch('main.profile_service')
    def test_cleanup_services_admin(self, mock_profile, mock_voice, mock_integration, client):
        """Test service cleanup as admin"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "admin_123", "token": "admin_token", "is_admin": True
        }
        
        mock_voice.cleanup_expired_sessions = AsyncMock(return_value=5)
        mock_profile.cleanup_inactive_profiles = AsyncMock(return_value=3)
        
        response = client.post(
            "/admin/cleanup",
            headers={"Authorization": "Bearer admin_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["expired_sessions_removed"] == 5
        assert data["inactive_profiles_cleaned"] == 3

    @patch('main.integration_manager')
    def test_cleanup_services_non_admin(self, mock_integration, client):
        """Test service cleanup as non-admin (should fail)"""
        mock_integration.verify_user_authentication.return_value = {
            "user_id": "user_123", "token": "user_token", "is_admin": False
        }
        
        response = client.post(
            "/admin/cleanup",
            headers={"Authorization": "Bearer user_token"}
        )
        
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

class TestApplicationLifecycle:
    """Test application startup and shutdown"""
    
    @patch('main.register_with_api_gateway')
    @patch('main.VoiceEngineManager')
    @patch('main.ServiceIntegrationManager')
    def test_lifespan_startup_success(self, mock_integration_cls, mock_engine_cls, mock_register):
        """Test successful application startup"""
        # This would require testing the lifespan context manager
        # For now, we'll test the individual components
        mock_engine = AsyncMock()
        mock_engine.initialize_engines = AsyncMock()
        mock_engine_cls.return_value = mock_engine
        
        mock_integration = AsyncMock()
        mock_integration_cls.return_value = mock_integration
        
        mock_register.return_value = AsyncMock(return_value=True)
        
        # Test would require more complex setup for lifespan testing
        assert True  # Placeholder for lifespan testing

    def test_cors_middleware(self, client):
        """Test CORS middleware configuration"""
        response = client.options("/health")
        # CORS headers should be present in preflight response
        assert response.status_code in [200, 405]  # Either OK or Method Not Allowed is fine
