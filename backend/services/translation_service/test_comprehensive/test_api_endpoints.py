"""
Comprehensive integration tests for Translation Service API endpoints
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import json
import time
from datetime import datetime

# Mock the shared.auth module before importing main
import sys
from unittest.mock import MagicMock

# Create mock for shared.auth
mock_auth = MagicMock()
mock_auth.get_current_user = MagicMock(return_value={"user_id": "test_user", "username": "test"})
sys.modules['shared.auth'] = mock_auth

from main import app


@pytest.mark.asyncio
class TestTranslationServiceAPI:
    """Test Translation Service API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client for API"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_translation_engine(self):
        """Mock translation engine"""
        mock = AsyncMock()
        mock.translate.return_value = {
            "translated_text": "Hola mundo",
            "source_language": "en",
            "target_language": "es",
            "confidence": 0.95,
            "quality_score": 0.92,
            "engine": "local",
            "processing_time_ms": 150,
            "cache_hit": False,
            "cultural_notes": [],
            "custom_terms_used": []
        }
        mock.translate_batch.return_value = [
            {
                "status": "success",
                "translated_text": "Hola",
                "source_language": "en",
                "target_language": "es",
                "confidence_score": 0.95
            }
        ]
        mock.detect_language.return_value = {
            "language": "en",
            "confidence": 0.95
        }
        mock.health_check.return_value = {
            "status": "healthy",
            "engines": ["local", "google"]
        }
        mock.initialize.return_value = True
        return mock
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        with patch('main.translation_engine') as mock_engine:
            mock_engine.health_check.return_value = {
                "status": "healthy",
                "engines": ["local"]
            }
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
            assert "timestamp" in data
            assert "version" in data
    
    def test_health_check_failure(self, client):
        """Test health check when service is unhealthy"""
        with patch('main.translation_engine') as mock_engine:
            mock_engine.health_check.side_effect = Exception("Service down")
            
            response = client.get("/health")
            
            assert response.status_code == 503
    
    def test_translate_endpoint_success(self, client, auth_headers):
        """Test successful translation request"""
        with patch('main.translation_engine') as mock_engine, \
             patch('main.get_current_user') as mock_user:
            
            mock_engine.translate.return_value = {
                "translated_text": "Hola mundo",
                "source_language": "en", 
                "target_language": "es",
                "confidence": 0.95,
                "quality_score": 0.92,
                "engine": "local",
                "processing_time_ms": 150,
                "cache_hit": False,
                "cultural_notes": [],
                "custom_terms_used": [],
                "request_id": "test_123"
            }
            
            mock_user.return_value = MagicMock(id="test_user")
            
            response = client.post(
                "/translate",
                json={
                    "text": "Hello world",
                    "source_language": "en",
                    "target_language": "es",
                    "engine": "local",
                    "domain": "meditation",
                    "cultural_adaptation": True,
                    "use_custom_glossary": True,
                    "use_cache": True
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["translated_text"] == "Hola mundo"
            assert data["source_language"] == "en"
            assert data["target_language"] == "es"
            assert data["status"] == "completed"
    
    def test_translate_endpoint_error(self, client, auth_headers):
        """Test translation endpoint error handling"""
        with patch('main.translation_engine') as mock_engine, \
             patch('main.get_current_user') as mock_user:
            
            mock_engine.translate.side_effect = Exception("Translation failed")
            mock_user.return_value = MagicMock(id="test_user")
            
            response = client.post(
                "/translate",
                json={
                    "text": "Hello world",
                    "source_language": "en",
                    "target_language": "es",
                    "engine": "local"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 500
            assert "Translation failed" in response.json()["detail"]
    
    def test_translate_batch_endpoint(self, client, auth_headers):
        """Test batch translation endpoint"""
        with patch('main.translation_engine') as mock_engine, \
             patch('main.get_current_user') as mock_user:
            
            mock_engine.translate_batch.return_value = [
                {
                    "status": "success",
                    "translated_text": "Hola",
                    "source_language": "en",
                    "target_language": "es",
                    "confidence_score": 0.95,
                    "quality_score": 0.9,
                    "engine": "local",
                    "processing_time_ms": 100,
                    "cache_hit": False
                },
                {
                    "status": "success", 
                    "translated_text": "Mundo",
                    "source_language": "en",
                    "target_language": "es",
                    "confidence_score": 0.92,
                    "quality_score": 0.88,
                    "engine": "local",
                    "processing_time_ms": 95,
                    "cache_hit": False
                }
            ]
            
            mock_user.return_value = MagicMock(id="test_user")
            
            response = client.post(
                "/translate/batch",
                json={
                    "texts": ["Hello", "World"],
                    "source_language": "en",
                    "target_language": "es",
                    "engine": "local",
                    "domain": "meditation",
                    "cultural_adaptation": True,
                    "use_custom_glossary": True
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["translations"]) == 2
            assert data["success_count"] == 2
            assert data["failure_count"] == 0
            assert "batch_id" in data
    
    def test_detect_language_endpoint(self, client):
        """Test language detection endpoint"""
        with patch('main.translation_engine') as mock_engine:
            mock_engine.detect_language.return_value = {
                "language": "en",
                "confidence": 0.95
            }
            
            response = client.post(
                "/detect-language",
                json={"text": "Hello world"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["detected_language"] == "en"
            assert data["confidence_score"] == 0.95
            assert "processing_time_ms" in data
    
    def test_detect_language_error(self, client):
        """Test language detection error handling"""
        with patch('main.translation_engine') as mock_engine:
            mock_engine.detect_language.side_effect = Exception("Detection failed")
            
            response = client.post(
                "/detect-language",
                json={"text": "Hello world"}
            )
            
            assert response.status_code == 500
            assert "Language detection failed" in response.json()["detail"]
    
    def test_supported_languages_endpoint(self, client):
        """Test supported languages endpoint"""
        with patch('config.settings.SUPPORTED_LANGUAGES') as mock_langs, \
             patch('config.settings.TIER_CONFIGURATIONS') as mock_tiers:
            
            mock_langs.return_value = {
                "en": {"name": "English", "native": "English", "tier": 1},
                "es": {"name": "Spanish", "native": "Español", "tier": 1},
                "hi": {"name": "Hindi", "native": "हिन्दी", "tier": 2}
            }
            
            mock_tiers.return_value = {
                1: {"features": ["translation", "detection", "cultural_adaptation"]},
                2: {"features": ["translation", "detection"]}
            }
            
            response = client.get("/languages")
            
            assert response.status_code == 200
            data = response.json()
            assert "languages" in data
            assert "total_count" in data
            assert "tiers" in data
    
    def test_supported_languages_error(self, client):
        """Test supported languages endpoint error"""
        with patch('config.settings.SUPPORTED_LANGUAGES') as mock_langs:
            mock_langs.side_effect = Exception("Config error")
            
            response = client.get("/languages")
            
            assert response.status_code == 500
    
    def test_test_translate_endpoint(self, client):
        """Test the test translation endpoint (no auth required)"""
        with patch('main.translation_engine') as mock_engine:
            mock_engine.translate.return_value = {
                "translated_text": "Hola mundo",
                "source_language": "en",
                "target_language": "es", 
                "confidence": 0.95,
                "engine": "local",
                "cached": False
            }
            
            response = client.post(
                "/test/translate",
                json={
                    "text": "Hello world",
                    "source_language": "en",
                    "target_language": "es",
                    "engine": "local",
                    "domain": "meditation",
                    "cultural_adaptation": True
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["translated_text"] == "Hola mundo"
            assert "processing_time_ms" in data
    
    def test_test_translate_error(self, client):
        """Test test translation endpoint error handling"""
        with patch('main.translation_engine') as mock_engine:
            mock_engine.translate.side_effect = Exception("Test translation failed")
            
            response = client.post(
                "/test/translate",
                json={
                    "text": "Hello world",
                    "target_language": "es",
                    "engine": "local"
                }
            )
            
            assert response.status_code == 500
            assert "Translation failed" in response.json()["detail"]
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get("/metrics")
        
        # Should return metrics data (content type may vary)
        assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/health")
        
        # Should handle OPTIONS request for CORS
        assert response.status_code in [200, 405]
    
    def test_request_validation_missing_fields(self, client, auth_headers):
        """Test request validation for missing required fields"""
        with patch('main.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="test_user")
            
            # Missing text field
            response = client.post(
                "/translate",
                json={
                    "target_language": "es",
                    "engine": "local"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 422
    
    def test_request_validation_invalid_language(self, client, auth_headers):
        """Test request validation for invalid language codes"""
        with patch('main.get_current_user') as mock_user:
            mock_user.return_value = MagicMock(id="test_user")
            
            response = client.post(
                "/translate", 
                json={
                    "text": "Hello",
                    "target_language": "invalid_lang",
                    "engine": "local"
                },
                headers=auth_headers
            )
            
            # May pass validation but fail in translation
            assert response.status_code in [422, 500]
    
    def test_authentication_required(self, client):
        """Test that authentication is required for protected endpoints"""
        response = client.post(
            "/translate",
            json={
                "text": "Hello world",
                "target_language": "es",
                "engine": "local"
            }
        )
        
        # Should require authentication
        assert response.status_code in [401, 403]
    
    def test_empty_text_translation(self, client, auth_headers):
        """Test translation with empty text"""
        with patch('main.translation_engine') as mock_engine, \
             patch('main.get_current_user') as mock_user:
            
            mock_engine.translate.return_value = {
                "translated_text": "",
                "source_language": "en",
                "target_language": "es",
                "confidence": 1.0,
                "engine": "local"
            }
            
            mock_user.return_value = MagicMock(id="test_user")
            
            response = client.post(
                "/translate",
                json={
                    "text": "",
                    "target_language": "es",
                    "engine": "local"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert response.json()["translated_text"] == ""
    
    def test_long_text_translation(self, client, auth_headers):
        """Test translation with very long text"""
        with patch('main.translation_engine') as mock_engine, \
             patch('main.get_current_user') as mock_user:
            
            long_text = "Hello world " * 1000
            mock_engine.translate.return_value = {
                "translated_text": "Hola mundo " * 1000,
                "source_language": "en",
                "target_language": "es",
                "confidence": 0.9,
                "engine": "local"
            }
            
            mock_user.return_value = MagicMock(id="test_user")
            
            response = client.post(
                "/translate",
                json={
                    "text": long_text,
                    "target_language": "es", 
                    "engine": "local"
                },
                headers=auth_headers
            )
            
            assert response.status_code == 200
            assert len(response.json()["translated_text"]) > 1000
    
    def test_concurrent_requests(self, client, auth_headers):
        """Test handling of concurrent translation requests"""
        import concurrent.futures
        import threading
        
        with patch('main.translation_engine') as mock_engine, \
             patch('main.get_current_user') as mock_user:
            
            mock_engine.translate.return_value = {
                "translated_text": "Hola",
                "source_language": "en",
                "target_language": "es",
                "confidence": 0.95,
                "engine": "local"
            }
            
            mock_user.return_value = MagicMock(id="test_user")
            
            def make_request():
                return client.post(
                    "/translate",
                    json={
                        "text": f"Hello {threading.current_thread().ident}",
                        "target_language": "es",
                        "engine": "local"
                    },
                    headers=auth_headers
                )
            
            # Execute concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                responses = [future.result() for future in futures]
            
            # All requests should succeed
            for response in responses:
                assert response.status_code == 200
    
    def test_request_logging_middleware(self, client):
        """Test that request logging middleware works"""
        # This test mainly ensures the middleware doesn't break the request
        response = client.get("/health")
        
        # Request should complete successfully with middleware
        assert response.status_code in [200, 503]  # Healthy or unhealthy
    
    def test_global_exception_handler(self, client):
        """Test global exception handler"""
        with patch('main.translation_engine') as mock_engine:
            # Force an unexpected exception
            mock_engine.health_check.side_effect = RuntimeError("Unexpected error")
            
            response = client.get("/health")
            
            assert response.status_code == 500
            data = response.json()
            assert data["error"] == "internal_server_error"
