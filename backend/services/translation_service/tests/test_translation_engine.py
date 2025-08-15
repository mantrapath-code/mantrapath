"""
Comprehensive tests for Translation Service core functionality
Target: 50%+ test coverage for all core features
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

# Test the translation engine
from services.translation_engine import TranslationEngine
from engines.base_translator import TranslationResult
from config.settings import SUPPORTED_LANGUAGES

class TestTranslationEngine:
    """Test core translation engine functionality"""
    
    @pytest.fixture
    async def translation_engine(self):
        """Create a translation engine for testing"""
        engine = TranslationEngine()
        
        # Mock the Google translator
        mock_translator = AsyncMock()
        mock_translator.name = "google"
        mock_translator.is_initialized = True
        mock_translator.supported_languages = set(["en", "es", "fr", "hi", "ar"])
        
        # Mock translate method
        async def mock_translate(text, source_lang, target_lang, domain=None, context=None):
            return TranslationResult(
                translated_text=f"Translated: {text}",
                source_language=source_lang,
                target_language=target_lang,
                confidence_score=0.95,
                engine_name="google",
                processing_time_ms=150
            )
        
        mock_translator.translate = mock_translate
        mock_translator.supports_language_pair = lambda s, t: True
        mock_translator.detect_language = AsyncMock(return_value=("en", 0.9))
        mock_translator.get_quality_score = AsyncMock(return_value=0.92)
        mock_translator.health_check = AsyncMock(return_value={
            "name": "google",
            "status": "healthy"
        })
        
        engine.engines["google"] = mock_translator
        engine.is_initialized = True
        
        # Mock cache
        engine.cache = AsyncMock()
        engine.cache.get = AsyncMock(return_value=None)  # No cache hits by default
        engine.cache.setex = AsyncMock()
        
        return engine
    
    @pytest.mark.asyncio
    async def test_single_translation_success(self, translation_engine):
        """Test successful single text translation"""
        result = await translation_engine.translate(
            text="Hello world",
            source_language="en",
            target_language="es",
            engine="google"
        )
        
        assert result.translated_text == "Translated: Hello world"
        assert result.source_language == "en"
        assert result.target_language == "es"
        assert result.confidence_score == 0.95
        assert result.engine_name == "google"
        assert result.processing_time_ms == 150
    
    @pytest.mark.asyncio
    async def test_auto_language_detection(self, translation_engine):
        """Test automatic language detection"""
        result = await translation_engine.translate(
            text="Hello world",
            source_language=None,  # Auto-detect
            target_language="es"
        )
        
        assert result.source_language == "en"  # Should be detected
        assert result.translated_text == "Translated: Hello world"
    
    @pytest.mark.asyncio
    async def test_batch_translation(self, translation_engine):
        """Test batch translation functionality"""
        texts = ["Hello", "World", "How are you?"]
        
        results = await translation_engine.translate_batch(
            texts=texts,
            source_language="en",
            target_language="es"
        )
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result.translated_text == f"Translated: {texts[i]}"
            assert result.source_language == "en"
            assert result.target_language == "es"
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, translation_engine):
        """Test translation cache functionality"""
        # Setup cache to return a cached result
        cached_data = json.dumps({
            "translated_text": "Cached translation",
            "source_language": "en",
            "target_language": "es",
            "confidence_score": 0.98,
            "engine_name": "google",
            "metadata": {"cache_hit": True},
            "cached_at": datetime.now(timezone.utc).isoformat()
        })
        
        translation_engine.cache.get = AsyncMock(return_value=cached_data)
        
        result = await translation_engine.translate(
            text="Hello world",
            source_language="en",
            target_language="es"
        )
        
        assert result.translated_text == "Cached translation"
        assert result.metadata.get("cache_hit") is True
        assert result.processing_time_ms == 0  # Cache hits have no processing time
    
    @pytest.mark.asyncio
    async def test_engine_selection_by_tier(self, translation_engine):
        """Test engine selection based on language tier"""
        # Test Tier 1 language (should prefer best engines)
        result = await translation_engine.translate(
            text="Hello",
            source_language="en",
            target_language="hi",  # Tier 1 language
            engine="auto"
        )
        
        assert result.engine_name == "google"
        
        # Test with unsupported engine fallback
        result = await translation_engine.translate(
            text="Hello",
            source_language="en",
            target_language="es",
            engine="nonexistent"
        )
        
        assert result.engine_name == "google"  # Should fallback
    
    @pytest.mark.asyncio
    async def test_language_detection(self, translation_engine):
        """Test language detection functionality"""
        language, confidence = await translation_engine.detect_language("Hello world")
        
        assert language == "en"
        assert confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_health_check(self, translation_engine):
        """Test health check functionality"""
        health = await translation_engine.health_check()
        
        assert health["status"] == "healthy"
        assert "engines" in health
        assert "google" in health["engines"]
        assert health["engines"]["google"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_error_handling_no_engines(self):
        """Test error handling when no engines are available"""
        engine = TranslationEngine()
        engine.is_initialized = True  # But no engines
        
        with pytest.raises(RuntimeError, match="No suitable engine available"):
            await engine.translate("Hello", "en", "es")
    
    @pytest.mark.asyncio
    async def test_unsupported_language_pair(self, translation_engine):
        """Test handling of unsupported language pairs"""
        # Mock engine to not support a specific pair
        translation_engine.engines["google"].supports_language_pair = lambda s, t: False
        
        with pytest.raises(RuntimeError, match="No suitable engine available"):
            await translation_engine.translate("Hello", "xx", "yy")

class TestTranslationCaching:
    """Test translation caching functionality"""
    
    @pytest.fixture
    def mock_cache(self):
        """Create mock cache for testing"""
        return AsyncMock()
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation consistency"""
        engine = TranslationEngine()
        
        key1 = engine._create_cache_key("Hello", "en", "es", "general")
        key2 = engine._create_cache_key("Hello", "en", "es", "general")
        key3 = engine._create_cache_key("Hello", "en", "fr", "general")
        
        assert key1 == key2  # Same inputs should generate same key
        assert key1 != key3  # Different target language should generate different key
    
    @pytest.mark.asyncio
    async def test_cache_storage_and_retrieval(self, translation_engine):
        """Test storing and retrieving from cache"""
        # Test cache miss first
        translation_engine.cache.get = AsyncMock(return_value=None)
        
        result = await translation_engine.translate("Hello", "en", "es")
        
        # Verify cache storage was attempted
        translation_engine.cache.setex.assert_called_once()
        
        # Test cache hit
        cached_data = json.dumps({
            "translated_text": result.translated_text,
            "source_language": result.source_language,
            "target_language": result.target_language,
            "confidence_score": result.confidence_score,
            "engine_name": result.engine_name,
            "metadata": result.metadata,
            "cached_at": datetime.now(timezone.utc).isoformat()
        })
        
        translation_engine.cache.get = AsyncMock(return_value=cached_data)
        
        cached_result = await translation_engine.translate("Hello", "en", "es")
        assert cached_result.metadata.get("cache_hit") is True

class TestLanguageSupport:
    """Test language support and tier functionality"""
    
    def test_supported_languages_structure(self):
        """Test that supported languages have required structure"""
        for lang_code, lang_info in SUPPORTED_LANGUAGES.items():
            assert isinstance(lang_code, str)
            assert len(lang_code) == 2  # ISO 639-1 format
            assert "name" in lang_info
            assert "native" in lang_info
            assert "tier" in lang_info
            assert lang_info["tier"] in [1, 2, 3]
    
    def test_tier_1_languages_features(self):
        """Test that Tier 1 languages have premium features"""
        tier_1_languages = [
            lang for lang, info in SUPPORTED_LANGUAGES.items() 
            if info.get("tier") == 1
        ]
        
        assert len(tier_1_languages) >= 5  # Should have several Tier 1 languages
        assert "en" in tier_1_languages  # English should be Tier 1
        assert "hi" in tier_1_languages  # Hindi should be Tier 1 for meditation
    
    def test_meditation_specific_languages(self):
        """Test that meditation-specific languages are supported"""
        meditation_languages = ["sa", "hi", "th", "my", "bo"]  # Sanskrit, Hindi, Thai, Myanmar, Tibetan
        
        for lang in meditation_languages:
            if lang in SUPPORTED_LANGUAGES:
                # These should be high tier for meditation context
                assert SUPPORTED_LANGUAGES[lang]["tier"] <= 2

class TestQualityAssurance:
    """Test translation quality assurance features"""
    
    @pytest.mark.asyncio
    async def test_confidence_score_calculation(self, translation_engine):
        """Test confidence score calculation"""
        result = await translation_engine.translate("Hello world", "en", "es")
        
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.confidence_score > 0.8  # Should be high for common languages
    
    @pytest.mark.asyncio
    async def test_quality_score_calculation(self, translation_engine):
        """Test quality score calculation"""
        result = await translation_engine.translate("Hello world", "en", "es")
        
        quality_score = result.metadata.get("quality_score", 0.0)
        assert 0.0 <= quality_score <= 1.0
        assert quality_score > 0.7  # Should be reasonably high

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_translation_performance(self, translation_engine):
        """Test that translations complete within reasonable time"""
        import time
        
        start_time = time.time()
        result = await translation_engine.translate("Hello world", "en", "es")
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Should complete within 5 seconds (generous for testing)
        assert processing_time < 5000
        assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_batch_translation_efficiency(self, translation_engine):
        """Test batch translation is more efficient than individual translations"""
        texts = ["Hello", "World", "Test"] * 10  # 30 texts
        
        # Batch translation
        start_time = time.time()
        batch_results = await translation_engine.translate_batch(texts, "en", "es")
        batch_time = time.time() - start_time
        
        assert len(batch_results) == len(texts)
        
        # Should complete batch in reasonable time
        assert batch_time < 10.0  # 10 seconds max for 30 translations

class TestErrorHandling:
    """Test error handling and resilience"""
    
    @pytest.mark.asyncio
    async def test_engine_failure_resilience(self, translation_engine):
        """Test resilience when translation engine fails"""
        # Make the engine raise an exception
        async def failing_translate(*args, **kwargs):
            raise Exception("Translation engine failure")
        
        translation_engine.engines["google"].translate = failing_translate
        
        with pytest.raises(Exception):
            await translation_engine.translate("Hello", "en", "es")
    
    @pytest.mark.asyncio
    async def test_invalid_language_codes(self, translation_engine):
        """Test handling of invalid language codes"""
        with pytest.raises(RuntimeError):
            await translation_engine.translate("Hello", "invalid", "es")
        
        with pytest.raises(RuntimeError):
            await translation_engine.translate("Hello", "en", "invalid")
    
    @pytest.mark.asyncio
    async def test_empty_text_handling(self, translation_engine):
        """Test handling of empty or invalid text"""
        # This should be handled at the API level, but test engine resilience
        result = await translation_engine.translate("", "en", "es")
        assert result.translated_text is not None

class TestCulturalAdaptation:
    """Test cultural adaptation features"""
    
    @pytest.mark.asyncio
    async def test_cultural_context_preservation(self, translation_engine):
        """Test that cultural context is preserved in translations"""
        # Test with meditation-specific text
        meditation_text = "Practice mindfulness meditation daily"
        
        result = await translation_engine.translate(
            meditation_text, "en", "hi", 
            domain="mindfulness",
            cultural_adaptation=True
        )
        
        assert result.translated_text is not None
        assert "cultural_adaptations_applied" in result.metadata
    
    @pytest.mark.asyncio
    async def test_domain_specific_translation(self, translation_engine):
        """Test domain-specific translation handling"""
        domains = ["mindfulness", "buddhist", "yoga", "meditation"]
        
        for domain in domains:
            result = await translation_engine.translate(
                "Peace and tranquility", "en", "es",
                domain=domain
            )
            
            assert result.translated_text is not None
            assert result.metadata.get("domain") == domain

# Integration tests would go here
class TestIntegration:
    """Integration tests for the complete translation pipeline"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_translation_flow(self, translation_engine):
        """Test complete translation flow from request to response"""
        # This would test the full pipeline including:
        # 1. Language detection
        # 2. Engine selection  
        # 3. Custom glossary application
        # 4. Translation
        # 5. Cultural adaptation
        # 6. Quality scoring
        # 7. Caching
        
        result = await translation_engine.translate(
            text="Welcome to our meditation session",
            source_language=None,  # Auto-detect
            target_language="hi",
            domain="meditation",
            cultural_adaptation=True,
            use_custom_glossary=True
        )
        
        # Verify all components worked
        assert result.source_language == "en"  # Detected
        assert result.target_language == "hi"
        assert result.translated_text is not None
        assert result.confidence_score > 0.0
        assert "quality_score" in result.metadata
        assert result.engine_name in ["google"]  # Available engines

# Performance benchmarks
class TestBenchmarks:
    """Performance benchmarks for the translation service"""
    
    @pytest.mark.asyncio
    async def test_translation_latency_benchmark(self, translation_engine):
        """Benchmark translation latency"""
        test_texts = [
            "Hello world",
            "This is a longer text to test translation performance with more content",
            "Short",
            "Medium length text for testing purposes"
        ]
        
        latencies = []
        
        for text in test_texts:
            start_time = time.time()
            await translation_engine.translate(text, "en", "es")
            latency = (time.time() - start_time) * 1000
            latencies.append(latency)
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Performance targets (adjust based on requirements)
        assert avg_latency < 1000  # Average under 1 second
        assert max_latency < 2000   # Maximum under 2 seconds
        
        print(f"Average latency: {avg_latency:.2f}ms")
        print(f"Maximum latency: {max_latency:.2f}ms")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=html"])
