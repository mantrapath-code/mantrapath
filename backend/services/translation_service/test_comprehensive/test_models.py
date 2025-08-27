"""
Comprehensive tests for Translation Service Models
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from typing import List, Optional

from models.request_models import (
    TranslationEngine, Priority, TranslationStatus,
    LanguageDetectionRequest, LanguageDetectionResponse
)
from models.translation_models import (
    TranslationRequest as DBTranslationRequest,
    TranslationCache, LanguageDetectionResult,
    CustomGlossary, TranslationFeedback
)


@pytest.mark.unit
class TestRequestModels:
    """Test request and response models"""
    
    def test_translation_request_valid(self):
        """Test valid translation request"""
        request = TranslationRequest(
            text="Hello world",
            target_language="es",
            source_language="en",
            engine=TranslationEngine.LOCAL,
            domain="meditation",
            cultural_adaptation=True,
            use_custom_glossary=True,
            use_cache=True
        )
        
        assert request.text == "Hello world"
        assert request.target_language == "es"
        assert request.source_language == "en"
        assert request.engine == TranslationEngine.LOCAL
        assert request.domain == "meditation"
        assert request.cultural_adaptation is True
        assert request.use_custom_glossary is True
        assert request.use_cache is True
    
    def test_translation_engine_enum(self):
        """Test translation engine enum"""
        assert TranslationEngine.GOOGLE == "google"
        assert TranslationEngine.MICROSOFT == "microsoft"
        assert TranslationEngine.LOCAL == "local"
        assert TranslationEngine.AUTO == "auto"
    
    def test_language_detection_request_valid(self):
        """Test valid language detection request"""
        request = LanguageDetectionRequest(
            text="Hello world",
            engines=["langdetect"],
            include_alternatives=True
        )
        
        assert request.text == "Hello world"
        assert request.engines == ["langdetect"]
        assert request.include_alternatives is True
    
    def test_translation_request_minimal(self):
        """Test minimal translation request"""
        request = TranslationRequest(
            text="Hello",
            target_language="es",
            engine=TranslationEngine.LOCAL
        )
        
        assert request.text == "Hello"
        assert request.target_language == "es"
        assert request.source_language is None  # Optional field
        assert request.engine == TranslationEngine.LOCAL
    
    def test_translation_request_empty_text(self):
        """Test translation request with empty text"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(
                text="",
                target_language="es",
                engine=TranslationEngine.LOCAL
            )
        
        assert "ensure this value has at least 1 characters" in str(exc_info.value)
    
    def test_translation_request_invalid_language(self):
        """Test translation request with invalid language code"""
        # This depends on validation rules - if any exist
        request = TranslationRequest(
            text="Hello",
            target_language="invalid_lang",
            engine=TranslationEngine.LOCAL
        )
        
        # Should create successfully (validation may be done elsewhere)
        assert request.target_language == "invalid_lang"
    
    def test_translation_response_complete(self):
        """Test complete translation response"""
        response = TranslationResponse(
            translated_text="Hola mundo",
            source_language="en",
            target_language="es",
            confidence_score=0.95,
            quality_score=0.92,
            engine_used="local",
            processing_time_ms=150,
            cache_hit=False,
            cultural_adaptations_applied=["greeting_formal"],
            custom_terms_used=["mundo"],
            request_id="test_123",
            status="completed"
        )
        
        assert response.translated_text == "Hola mundo"
        assert response.source_language == "en"
        assert response.target_language == "es"
        assert response.confidence_score == 0.95
        assert response.quality_score == 0.92
        assert response.engine_used == "local"
        assert response.processing_time_ms == 150
        assert response.cache_hit is False
        assert response.cultural_adaptations_applied == ["greeting_formal"]
        assert response.custom_terms_used == ["mundo"]
        assert response.request_id == "test_123"
        assert response.status == "completed"
    
    def test_batch_translation_request(self):
        """Test batch translation request"""
        request = BatchTranslationRequest(
            texts=["Hello", "World", "Peace"],
            target_language="es",
            source_language="en",
            engine=TranslationEngine.GOOGLE,
            domain="meditation",
            cultural_adaptation=True,
            use_custom_glossary=False
        )
        
        assert len(request.texts) == 3
        assert request.texts == ["Hello", "World", "Peace"]
        assert request.target_language == "es"
        assert request.engine == TranslationEngine.GOOGLE
    
    def test_batch_translation_empty_list(self):
        """Test batch translation with empty text list"""
        with pytest.raises(ValidationError) as exc_info:
            BatchTranslationRequest(
                texts=[],
                target_language="es",
                engine=TranslationEngine.LOCAL
            )
        
        assert "ensure this value has at least 1 items" in str(exc_info.value)
    
    def test_batch_translation_response(self):
        """Test batch translation response"""
        translations = [
            TranslationResponse(
                translated_text="Hola",
                source_language="en",
                target_language="es",
                confidence_score=0.95,
                quality_score=0.9,
                engine_used="local",
                processing_time_ms=100,
                cache_hit=False,
                cultural_adaptations_applied=[],
                custom_terms_used=[],
                request_id="batch_0",
                status="completed"
            ),
            TranslationResponse(
                translated_text="Mundo",
                source_language="en",
                target_language="es",
                confidence_score=0.93,
                quality_score=0.88,
                engine_used="local",
                processing_time_ms=95,
                cache_hit=False,
                cultural_adaptations_applied=[],
                custom_terms_used=[],
                request_id="batch_1",
                status="completed"
            )
        ]
        
        response = BatchTranslationResponse(
            translations=translations,
            total_processing_time_ms=250,
            success_count=2,
            failure_count=0,
            batch_id="batch_123"
        )
        
        assert len(response.translations) == 2
        assert response.total_processing_time_ms == 250
        assert response.success_count == 2
        assert response.failure_count == 0
        assert response.batch_id == "batch_123"
    
    def test_language_detection_request(self):
        """Test language detection request"""
        request = LanguageDetectionRequest(
            text="Hello world, how are you today?"
        )
        
        assert request.text == "Hello world, how are you today?"
    
    def test_language_detection_response(self):
        """Test language detection response"""
        response = LanguageDetectionResponse(
            detected_language="en",
            confidence_score=0.95,
            alternative_languages=[
                {"language": "es", "confidence": 0.15},
                {"language": "fr", "confidence": 0.10}
            ],
            processing_time_ms=50,
            engine_used="google"
        )
        
        assert response.detected_language == "en"
        assert response.confidence_score == 0.95
        assert len(response.alternative_languages) == 2
        assert response.processing_time_ms == 50
        assert response.engine_used == "google"
    
    def test_voice_translation_request(self):
        """Test voice translation request"""
        request = VoiceTranslationRequest(
            audio_data="base64_encoded_audio_data",
            audio_format="wav",
            target_language="es",
            source_language="en",
            engine=TranslationEngine.GOOGLE,
            domain="meditation"
        )
        
        assert request.audio_data == "base64_encoded_audio_data"
        assert request.audio_format == "wav"
        assert request.target_language == "es"
        assert request.source_language == "en"
        assert request.engine == TranslationEngine.GOOGLE
        assert request.domain == "meditation"
    
    def test_supported_languages_response(self):
        """Test supported languages response"""
        languages = [
            LanguageInfo(
                code="en",
                name="English", 
                native_name="English",
                rtl=False,
                tier=1,
                features=["translation", "detection", "cultural_adaptation"]
            ),
            LanguageInfo(
                code="es",
                name="Spanish",
                native_name="Español",
                rtl=False,
                tier=1, 
                features=["translation", "detection"]
            ),
            LanguageInfo(
                code="hi",
                name="Hindi",
                native_name="हिन्दी",
                rtl=False,
                tier=2,
                features=["translation", "indic_support"]
            )
        ]
        
        response = SupportedLanguagesResponse(
            languages=languages,
            total_count=3,
            tiers={
                1: {"features": ["translation", "detection", "cultural_adaptation"]},
                2: {"features": ["translation", "indic_support"]}
            }
        )
        
        assert len(response.languages) == 3
        assert response.total_count == 3
        assert 1 in response.tiers
        assert 2 in response.tiers
    
    def test_health_check_response(self):
        """Test health check response"""
        response = HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0",
            engines_status={"local": "healthy", "google": "healthy"},
            cache_status="healthy",
            database_status="healthy",
            uptime_seconds=3600
        )
        
        assert response.status == "healthy"
        assert isinstance(response.timestamp, datetime)
        assert response.version == "1.0.0"
        assert response.engines_status["local"] == "healthy"
        assert response.cache_status == "healthy"
        assert response.database_status == "healthy"
        assert response.uptime_seconds == 3600
    
    def test_error_response(self):
        """Test error response model"""
        error = ErrorResponse(
            error="translation_failed",
            message="Translation engine is temporarily unavailable",
            details={"engine": "google", "error_code": "503"}
        )
        
        assert error.error == "translation_failed"
        assert error.message == "Translation engine is temporarily unavailable"
        assert error.details["engine"] == "google"
        assert error.details["error_code"] == "503"
    
    def test_translation_feedback_request(self):
        """Test translation feedback request"""
        request = TranslationFeedbackRequest(
            translation_id="trans_123",
            rating=4,
            feedback="Good translation but could be more natural",
            suggested_translation="Hola, ¿cómo estás?",
            user_id="user_456"
        )
        
        assert request.translation_id == "trans_123"
        assert request.rating == 4
        assert request.feedback == "Good translation but could be more natural"
        assert request.suggested_translation == "Hola, ¿cómo estás?"
        assert request.user_id == "user_456"
    
    def test_custom_glossary_request(self):
        """Test custom glossary request"""
        request = CustomGlossaryRequest(
            user_id="user_123",
            language_pair={"source": "en", "target": "es"},
            terms={
                "meditation": "meditación profunda",
                "mindfulness": "atención plena consciente",
                "chakra": "chakra"
            },
            domain="meditation"
        )
        
        assert request.user_id == "user_123"
        assert request.language_pair["source"] == "en"
        assert request.language_pair["target"] == "es"
        assert len(request.terms) == 3
        assert request.terms["meditation"] == "meditación profunda"
        assert request.domain == "meditation"


@pytest.mark.unit
class TestTranslationModels:
    """Test translation internal models"""
    
    def test_translation_result(self):
        """Test translation result model"""
        metadata = TranslationMetadata(
            processing_time_ms=150,
            engine_used="google",
            cache_hit=False,
            quality_score=0.92,
            confidence_score=0.95
        )
        
        result = TranslationResult(
            translated_text="Hola mundo",
            source_language="en",
            target_language="es",
            original_text="Hello world",
            engine_name="google",
            metadata=metadata,
            cultural_adaptations=[],
            custom_terms_used=[]
        )
        
        assert result.translated_text == "Hola mundo"
        assert result.source_language == "en"
        assert result.target_language == "es"
        assert result.original_text == "Hello world"
        assert result.engine_name == "google"
        assert result.metadata.processing_time_ms == 150
        assert result.metadata.quality_score == 0.92
    
    def test_cultural_adaptation(self):
        """Test cultural adaptation model"""
        adaptation = CulturalAdaptation(
            original_text="Hello",
            adapted_text="Buenos días",
            adaptation_type="formal_greeting",
            cultural_context={"region": "spain", "formality": "high"},
            confidence_score=0.88
        )
        
        assert adaptation.original_text == "Hello"
        assert adaptation.adapted_text == "Buenos días"
        assert adaptation.adaptation_type == "formal_greeting"
        assert adaptation.cultural_context["region"] == "spain"
        assert adaptation.confidence_score == 0.88
    
    def test_quality_metrics(self):
        """Test quality metrics model"""
        metrics = QualityMetrics(
            fluency_score=0.92,
            accuracy_score=0.89,
            cultural_appropriateness=0.95,
            overall_quality=0.92,
            confidence_level="high"
        )
        
        assert metrics.fluency_score == 0.92
        assert metrics.accuracy_score == 0.89
        assert metrics.cultural_appropriateness == 0.95
        assert metrics.overall_quality == 0.92
        assert metrics.confidence_level == "high"
    
    def test_cache_info(self):
        """Test cache info model"""
        cache_info = CacheInfo(
            cache_key="en_es_hello_world",
            cache_hit=True,
            cache_ttl=3600,
            cache_created_at=datetime.now()
        )
        
        assert cache_info.cache_key == "en_es_hello_world"
        assert cache_info.cache_hit is True
        assert cache_info.cache_ttl == 3600
        assert isinstance(cache_info.cache_created_at, datetime)
    
    def test_service_health(self):
        """Test service health model"""
        health = ServiceHealth(
            service_name="translation_service",
            status="healthy",
            last_check=datetime.now(),
            response_time_ms=45,
            error_rate=0.01,
            uptime_percentage=99.9
        )
        
        assert health.service_name == "translation_service"
        assert health.status == "healthy"
        assert isinstance(health.last_check, datetime)
        assert health.response_time_ms == 45
        assert health.error_rate == 0.01
        assert health.uptime_percentage == 99.9
    
    def test_translation_engine_enum(self):
        """Test translation engine enum values"""
        assert TranslationEngine.LOCAL == "local"
        assert TranslationEngine.GOOGLE == "google"
        assert TranslationEngine.MICROSOFT == "microsoft"
        assert TranslationEngine.INDIC == "indic"
        assert TranslationEngine.ARGOS == "argos"
        
        # Test all enum values are valid
        all_engines = [e.value for e in TranslationEngine]
        assert "local" in all_engines
        assert "google" in all_engines
        assert "microsoft" in all_engines
    
    def test_model_validation_edge_cases(self):
        """Test model validation for edge cases"""
        # Test negative confidence score
        with pytest.raises(ValidationError):
            TranslationResponse(
                translated_text="Test",
                source_language="en",
                target_language="es", 
                confidence_score=-0.1,  # Invalid negative score
                quality_score=0.9,
                engine_used="local",
                processing_time_ms=100,
                cache_hit=False,
                cultural_adaptations_applied=[],
                custom_terms_used=[],
                request_id="test",
                status="completed"
            )
        
        # Test confidence score > 1.0
        with pytest.raises(ValidationError):
            TranslationResponse(
                translated_text="Test",
                source_language="en",
                target_language="es",
                confidence_score=1.5,  # Invalid score > 1.0
                quality_score=0.9,
                engine_used="local",
                processing_time_ms=100,
                cache_hit=False,
                cultural_adaptations_applied=[],
                custom_terms_used=[],
                request_id="test",
                status="completed"
            )
    
    def test_model_serialization(self):
        """Test model serialization to dict"""
        request = TranslationRequest(
            text="Hello world",
            target_language="es",
            source_language="en",
            engine=TranslationEngine.LOCAL
        )
        
        # Test dict conversion
        request_dict = request.dict()
        assert request_dict["text"] == "Hello world"
        assert request_dict["target_language"] == "es"
        assert request_dict["source_language"] == "en"
        assert request_dict["engine"] == "local"
    
    def test_model_json_serialization(self):
        """Test model JSON serialization"""
        response = TranslationResponse(
            translated_text="Hola mundo",
            source_language="en",
            target_language="es",
            confidence_score=0.95,
            quality_score=0.92,
            engine_used="local",
            processing_time_ms=150,
            cache_hit=False,
            cultural_adaptations_applied=["greeting_formal"],
            custom_terms_used=["mundo"],
            request_id="test_123",
            status="completed"
        )
        
        # Test JSON conversion
        json_str = response.json()
        assert isinstance(json_str, str)
        assert "Hola mundo" in json_str
        assert "greeting_formal" in json_str
