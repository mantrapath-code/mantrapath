"""
Working tests for actual translation service models
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models.request_models import (
    TranslationRequest, TranslationResponse, BatchTranslationRequest,
    LanguageDetectionRequest, TranslationEngine
)


@pytest.mark.unit
class TestWorkingRequestModels:
    """Test actual request models"""
    
    def test_translation_request_creation(self):
        """Test creating a translation request"""
        request = TranslationRequest(
            text="Hello world",
            target_language="es",
            engine=TranslationEngine.LOCAL
        )
        
        assert request.text == "Hello world"
        assert request.target_language == "es"
        assert request.engine == TranslationEngine.LOCAL
    
    def test_translation_response_creation(self):
        """Test creating a translation response"""
        response = TranslationResponse(
            translated_text="Hola mundo",
            source_language="en",
            target_language="es",
            confidence_score=0.95,
            quality_score=0.92,
            engine_used="local",
            processing_time_ms=150,
            cache_hit=False,
            cultural_adaptations_applied=[],
            custom_terms_used=[],
            request_id="test_123",
            status="completed"
        )
        
        assert response.translated_text == "Hola mundo"
        assert response.confidence_score == 0.95
    
    def test_batch_translation_request(self):
        """Test batch translation request"""
        request = BatchTranslationRequest(
            texts=["Hello", "World"],
            target_language="es",
            engine=TranslationEngine.LOCAL
        )
        
        assert len(request.texts) == 2
        assert request.target_language == "es"
    
    def test_language_detection_request(self):
        """Test language detection request"""
        request = LanguageDetectionRequest(text="Hello world")
        assert request.text == "Hello world"
    
    def test_translation_engine_enum(self):
        """Test translation engine enum"""
        assert TranslationEngine.LOCAL == "local"
        assert TranslationEngine.GOOGLE == "google"
