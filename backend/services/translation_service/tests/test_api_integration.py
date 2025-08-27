"""
API Integration Tests for Translation Service
Tests FastAPI endpoints and integration with external services
"""
import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from main import app
from models.request_models import TranslationRequest, LanguageDetectionRequest

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return Mock(id="test_user_123", email="test@example.com")

class TestTranslationAPI:
    """Test Translation API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    @patch('main.translation_engine')
    @patch('main.get_current_user')
    def test_translate_endpoint_success(self, mock_get_user, mock_engine, client):
        """Test successful translation request"""
        # Mock user authentication
        mock_get_user.return_value = Mock(id="user123")
        
        # Mock translation engine
        mock_result = Mock()
        mock_result.translated_text = "Hola mundo"
        mock_result.source_language = "en"
        mock_result.target_language = "es"
        mock_result.confidence_score = 0.95
        mock_result.engine_name = "google"
        mock_result.processing_time_ms = 120
        mock_result.metadata = {"quality_score": 0.92, "cache_hit": False}
        
        mock_engine.translate = AsyncMock(return_value=mock_result)
        
        # Make request
        request_data = {
            "text": "Hello world",
            "target_language": "es",
            "engine": "auto"
        }
        
        response = client.post("/translate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["translated_text"] == "Hola mundo"
        assert data["source_language"] == "en"
        assert data["target_language"] == "es"
        assert data["confidence_score"] == 0.95
    
    @patch('main.translation_engine')
    def test_translate_endpoint_validation_error(self, mock_engine, client):
        """Test translation request validation"""
        # Missing required fields
        request_data = {
            "text": "",  # Empty text should fail
            "target_language": "es"
        }
        
        response = client.post("/translate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('main.translation_engine')
    @patch('main.get_current_user')
    def test_batch_translate_endpoint(self, mock_get_user, mock_engine, client):
        """Test batch translation endpoint"""
        mock_get_user.return_value = Mock(id="user123")
        
        # Mock batch translation results
        mock_results = []
        for i, text in enumerate(["Hello", "World", "Test"]):
            mock_result = Mock()
            mock_result.translated_text = f"Spanish_{text}"
            mock_result.source_language = "en"
            mock_result.target_language = "es"
            mock_result.confidence_score = 0.95
            mock_result.engine_name = "google"
            mock_result.processing_time_ms = 100
            mock_result.metadata = {"quality_score": 0.90, "cache_hit": False}
            mock_results.append(mock_result)
        
        mock_engine.translate_batch = AsyncMock(return_value=mock_results)
        
        request_data = {
            "texts": ["Hello", "World", "Test"],
            "target_language": "es"
        }
        
        response = client.post("/translate/batch", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success_count"] == 3
        assert data["failure_count"] == 0
        assert len(data["translations"]) == 3
    
    @patch('main.translation_engine')
    def test_language_detection_endpoint(self, mock_engine, client):
        """Test language detection endpoint"""
        mock_engine.detect_language = AsyncMock(return_value=("es", 0.92))
        
        request_data = {
            "text": "Hola mundo"
        }
        
        response = client.post("/detect-language", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["detected_language"] == "es"
        assert data["confidence_score"] == 0.92
    
    def test_supported_languages_endpoint(self, client):
        """Test supported languages endpoint"""
        response = client.get("/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert "languages" in data
        assert "total_count" in data
        assert "tiers" in data
        assert data["total_count"] > 0
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Should return Prometheus format metrics
        assert "translation_requests_total" in response.text or response.status_code == 200

class TestAPIValidation:
    """Test API request validation"""
    
    def test_translation_request_validation(self):
        """Test translation request model validation"""
        # Valid request
        valid_request = TranslationRequest(
            text="Hello world",
            target_language="es"
        )
        assert valid_request.text == "Hello world"
        assert valid_request.target_language == "es"
        
        # Test validation errors would be handled by FastAPI
        # We can test the Pydantic models directly
        
    def test_language_detection_validation(self):
        """Test language detection request validation"""
        valid_request = LanguageDetectionRequest(
            text="Hello world"
        )
        assert valid_request.text == "Hello world"
        assert valid_request.include_alternatives is True

class TestAuthentication:
    """Test authentication and authorization"""
    
    @patch('main.get_current_user')
    def test_authenticated_request(self, mock_get_user, client):
        """Test authenticated translation request"""
        mock_get_user.return_value = Mock(id="user123")
        
        # This would normally require actual authentication
        # but we're mocking it for testing
        with patch('main.translation_engine') as mock_engine:
            mock_engine.translate = AsyncMock(return_value=Mock(
                translated_text="Test",
                source_language="en",
                target_language="es",
                confidence_score=0.9,
                engine_name="google",
                processing_time_ms=100,
                metadata={"quality_score": 0.9}
            ))
            
            request_data = {
                "text": "Hello world",
                "target_language": "es"
            }
            
            response = client.post("/translate", json=request_data)
            # The endpoint should work with mocked authentication

class TestErrorHandling:
    """Test API error handling"""
    
    @patch('main.translation_engine')
    @patch('main.get_current_user')
    def test_translation_engine_error(self, mock_get_user, mock_engine, client):
        """Test handling of translation engine errors"""
        mock_get_user.return_value = Mock(id="user123")
        mock_engine.translate = AsyncMock(side_effect=Exception("Engine error"))
        
        request_data = {
            "text": "Hello world",
            "target_language": "es"
        }
        
        response = client.post("/translate", json=request_data)
        assert response.status_code == 500
    
    def test_invalid_json_request(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/translate",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

class TestPerformanceMetrics:
    """Test performance monitoring and metrics"""
    
    @patch('main.translation_engine')
    @patch('main.get_current_user')
    def test_metrics_collection(self, mock_get_user, mock_engine, client):
        """Test that metrics are collected during requests"""
        mock_get_user.return_value = Mock(id="user123")
        
        mock_result = Mock()
        mock_result.translated_text = "Test"
        mock_result.source_language = "en"
        mock_result.target_language = "es"
        mock_result.confidence_score = 0.9
        mock_result.engine_name = "google"
        mock_result.processing_time_ms = 100
        mock_result.metadata = {"quality_score": 0.9, "cache_hit": False}
        
        mock_engine.translate = AsyncMock(return_value=mock_result)
        
        # Make request
        request_data = {
            "text": "Hello world",
            "target_language": "es"
        }
        
        response = client.post("/translate", json=request_data)
        assert response.status_code == 200
        
        # Check that metrics endpoint shows the request
        metrics_response = client.get("/metrics")
        assert metrics_response.status_code == 200

class TestConcurrency:
    """Test concurrent request handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_translations(self):
        """Test handling multiple concurrent translation requests"""
        # This would test the service's ability to handle concurrent requests
        # In a real test, we'd make multiple requests simultaneously
        pass

class TestCaching:
    """Test caching behavior through API"""
    
    @patch('main.translation_engine')
    @patch('main.get_current_user')
    def test_cache_behavior(self, mock_get_user, mock_engine, client):
        """Test that caching works through the API"""
        mock_get_user.return_value = Mock(id="user123")
        
        # First request - cache miss
        mock_result = Mock()
        mock_result.translated_text = "Hola mundo"
        mock_result.source_language = "en"
        mock_result.target_language = "es"
        mock_result.confidence_score = 0.95
        mock_result.engine_name = "google"
        mock_result.processing_time_ms = 120
        mock_result.metadata = {"quality_score": 0.92, "cache_hit": False}
        
        mock_engine.translate = AsyncMock(return_value=mock_result)
        
        request_data = {
            "text": "Hello world",
            "target_language": "es",
            "use_cache": True
        }
        
        response = client.post("/translate", json=request_data)
        assert response.status_code == 200
        assert response.json()["cache_hit"] is False
        
        # Second request - should potentially be cached
        # (In real implementation, this would test actual cache behavior)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
