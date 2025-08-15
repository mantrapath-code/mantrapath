"""
Comprehensive tests for SQLAlchemy database models
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import uuid
import sys
from pathlib import Path

# Add proper paths for imports
current_dir = Path(__file__).parent
service_dir = current_dir.parent
sys.path.insert(0, str(service_dir))

from models.translation_models import (
    TranslationRequest, TranslationCache, LanguageDetectionResult,
    CustomGlossary, TranslationFeedback, OfflineTranslationCache
)


@pytest.mark.unit
class TestTranslationRequestModel:
    """Test TranslationRequest database model"""
    
    def test_translation_request_creation(self):
        """Test TranslationRequest model creation"""
        request = TranslationRequest(
            source_text="Hello world",
            source_language="en",
            target_language="es",
            translation_engine="google"
        )
        
        assert request.source_text == "Hello world"
        assert request.source_language == "en"
        assert request.target_language == "es"
        assert request.translation_engine == "google"
        assert request.status == "pending"
        assert request.cache_hit is False
        assert request.cultural_adaptation is False
        assert request.voice_translation is False
    
    def test_translation_request_with_optional_fields(self):
        """Test TranslationRequest with optional fields"""
        request = TranslationRequest(
            source_text="Namaste",
            source_language="hi",
            target_language="en",
            translation_engine="local",
            domain="mindfulness",
            context_type="meditation",
            cultural_adaptation=True,
            voice_translation=True,
            user_id="user123",
            session_id="session456"
        )
        
        assert request.domain == "mindfulness"
        assert request.context_type == "meditation"
        assert request.cultural_adaptation is True
        assert request.voice_translation is True
        assert request.user_id == "user123"
        assert request.session_id == "session456"
    
    def test_translation_request_table_name(self):
        """Test TranslationRequest table name"""
        assert TranslationRequest.__tablename__ == "translation_requests"
    
    def test_translation_request_defaults(self):
        """Test TranslationRequest default values"""
        request = TranslationRequest()
        assert request.status == "pending"
        assert request.cache_hit is False
        assert request.cultural_adaptation is False
        assert request.voice_translation is False


@pytest.mark.unit
class TestTranslationCacheModel:
    """Test TranslationCache database model"""
    
    def test_translation_cache_creation(self):
        """Test TranslationCache model creation"""
        expires_at = datetime.now(timezone.utc)
        cache = TranslationCache(
            source_text_hash="abc123",
            source_language="en",
            target_language="es",
            translated_text="Hola mundo",
            confidence_score=0.95,
            quality_score=0.92,
            translation_engine="google",
            expires_at=expires_at
        )
        
        assert cache.source_text_hash == "abc123"
        assert cache.source_language == "en"
        assert cache.target_language == "es"
        assert cache.translated_text == "Hola mundo"
        assert cache.confidence_score == 0.95
        assert cache.quality_score == 0.92
        assert cache.translation_engine == "google"
        assert cache.expires_at == expires_at
        assert cache.hit_count == 1
        assert cache.priority == "normal"
        assert cache.error_reports == 0
    
    def test_translation_cache_table_name(self):
        """Test TranslationCache table name"""
        assert TranslationCache.__tablename__ == "translation_cache"
    
    def test_translation_cache_with_domain(self):
        """Test TranslationCache with domain"""
        cache = TranslationCache(
            domain="meditation",
            priority="high"
        )
        
        assert cache.domain == "meditation"
        assert cache.priority == "high"


@pytest.mark.unit
class TestLanguageDetectionResultModel:
    """Test LanguageDetectionResult database model"""
    
    def test_language_detection_result_creation(self):
        """Test LanguageDetectionResult model creation"""
        result = LanguageDetectionResult(
            text_sample="Hello world",
            detected_language="en",
            confidence_score=0.98,
            detection_engine="langdetect"
        )
        
        assert result.text_sample == "Hello world"
        assert result.detected_language == "en"
        assert result.confidence_score == 0.98
        assert result.detection_engine == "langdetect"
        assert result.correction_needed is False
    
    def test_language_detection_result_with_alternatives(self):
        """Test LanguageDetectionResult with alternative languages"""
        alternatives = [{"lang": "es", "confidence": 0.15}, {"lang": "fr", "confidence": 0.10}]
        result = LanguageDetectionResult(
            alternative_languages=alternatives,
            user_confirmed_language="en",
            correction_needed=True
        )
        
        assert result.alternative_languages == alternatives
        assert result.user_confirmed_language == "en"
        assert result.correction_needed is True
    
    def test_language_detection_result_table_name(self):
        """Test LanguageDetectionResult table name"""
        assert LanguageDetectionResult.__tablename__ == "language_detection_results"


@pytest.mark.unit
class TestCustomGlossaryModel:
    """Test CustomGlossary database model"""
    
    def test_custom_glossary_creation(self):
        """Test CustomGlossary model creation"""
        glossary = CustomGlossary(
            scope="global",
            domain="buddhist",
            source_term="dharma",
            source_language="en",
            target_term="धर्म",
            target_language="hi"
        )
        
        assert glossary.scope == "global"
        assert glossary.domain == "buddhist"
        assert glossary.source_term == "dharma"
        assert glossary.source_language == "en"
        assert glossary.target_term == "धर्म"
        assert glossary.target_language == "hi"
        assert glossary.confidence_score == 1.0
        assert glossary.usage_frequency == 0
        assert glossary.user_verified is False
        assert glossary.expert_reviewed is False
    
    def test_custom_glossary_with_metadata(self):
        """Test CustomGlossary with metadata"""
        usage_examples = ["Example 1", "Example 2"]
        glossary = CustomGlossary(
            definition="A fundamental concept in Buddhism",
            cultural_context="Buddhist philosophy",
            usage_examples=usage_examples,
            pronunciation="ˈdɑrmə",
            user_verified=True,
            expert_reviewed=True,
            created_by="expert123",
            reviewed_by="reviewer456"
        )
        
        assert glossary.definition == "A fundamental concept in Buddhism"
        assert glossary.cultural_context == "Buddhist philosophy"
        assert glossary.usage_examples == usage_examples
        assert glossary.pronunciation == "ˈdɑrmə"
        assert glossary.user_verified is True
        assert glossary.expert_reviewed is True
        assert glossary.created_by == "expert123"
        assert glossary.reviewed_by == "reviewer456"
    
    def test_custom_glossary_table_name(self):
        """Test CustomGlossary table name"""
        assert CustomGlossary.__tablename__ == "custom_glossaries"


@pytest.mark.unit
class TestTranslationFeedbackModel:
    """Test TranslationFeedback database model"""
    
    def test_translation_feedback_creation(self):
        """Test TranslationFeedback model creation"""
        feedback = TranslationFeedback(
            translation_request_id="req123",
            user_id="user456",
            rating=4
        )
        
        assert feedback.translation_request_id == "req123"
        assert feedback.user_id == "user456"
        assert feedback.rating == 4
        assert feedback.feedback_type == "rating"
    
    def test_translation_feedback_with_details(self):
        """Test TranslationFeedback with detailed feedback"""
        issues = ["grammar", "cultural_context"]
        feedback = TranslationFeedback(
            accuracy_rating=3,
            cultural_appropriateness=4,
            naturalness_rating=5,
            suggested_translation="Better translation",
            comments="Good overall but needs improvement",
            reported_issues=issues,
            feedback_type="correction"
        )
        
        assert feedback.accuracy_rating == 3
        assert feedback.cultural_appropriateness == 4
        assert feedback.naturalness_rating == 5
        assert feedback.suggested_translation == "Better translation"
        assert feedback.comments == "Good overall but needs improvement"
        assert feedback.reported_issues == issues
        assert feedback.feedback_type == "correction"
    
    def test_translation_feedback_table_name(self):
        """Test TranslationFeedback table name"""
        assert TranslationFeedback.__tablename__ == "translation_feedback"


@pytest.mark.unit
class TestOfflineTranslationCacheModel:
    """Test OfflineTranslationCache database model"""
    
    def test_offline_translation_cache_creation(self):
        """Test OfflineTranslationCache model creation"""
        cache = OfflineTranslationCache(
            source_text_hash="xyz789",
            source_language="en",
            target_language="hi",
            domain="meditation",
            translated_text="ध्यान",
            confidence_score=0.90,
            quality_score=0.88,
            size_bytes=1024
        )
        
        assert cache.source_text_hash == "xyz789"
        assert cache.source_language == "en"
        assert cache.target_language == "hi"
        assert cache.domain == "meditation"
        assert cache.translated_text == "ध्यान"
        assert cache.confidence_score == 0.90
        assert cache.quality_score == 0.88
        assert cache.size_bytes == 1024
        assert cache.priority_level == "medium"
        assert cache.download_count == 0
        assert cache.auto_renewable is True
    
    def test_offline_translation_cache_priority(self):
        """Test OfflineTranslationCache priority levels"""
        cache = OfflineTranslationCache(
            priority_level="critical",
            auto_renewable=False
        )
        
        assert cache.priority_level == "critical"
        assert cache.auto_renewable is False
    
    def test_offline_translation_cache_table_name(self):
        """Test OfflineTranslationCache table name"""
        assert OfflineTranslationCache.__tablename__ == "offline_translation_cache"
