"""
Comprehensive unit tests for Enhanced Multi Translator
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import time

from engines.enhanced_multi_translator import EnhancedMultiTranslator


@pytest.mark.asyncio
class TestEnhancedMultiTranslator:
    """Test Enhanced Multi Translator functionality"""
    
    @pytest.fixture
    async def translator(self):
        """Create translator instance"""
        translator = EnhancedMultiTranslator()
        return translator
    
    @pytest.fixture
    def mock_engines(self):
        """Mock translation engines"""
        engines = {}
        for name in ['google', 'argos', 'indic', 'local']:
            engine = AsyncMock()
            engine.initialize = AsyncMock(return_value=True)
            engine.translate = AsyncMock(return_value={
                "translated_text": f"Translation from {name}",
                "source_language": "en",
                "target_language": "es",
                "confidence_score": 0.9,
                "engine": name,
                "processing_time_ms": 100
            })
            engine.health_check = AsyncMock(return_value={
                "status": "healthy",
                "engine": name
            })
            engine.get_supported_languages = AsyncMock(return_value=["en", "es", "hi"])
            engines[name] = engine
        return engines
    
    async def test_initialization_success(self, translator, mock_engines):
        """Test successful initialization"""
        with patch.object(translator, '_create_engines', return_value=mock_engines):
            result = await translator.initialize()
            
            assert result is True
            assert translator.is_initialized is True
            assert len(translator.engines) == 4
    
    async def test_initialization_failure(self, translator):
        """Test initialization failure handling"""
        with patch('engines.enhanced_multi_translator.FreeGoogleTranslator') as mock_google:
            mock_google.return_value.initialize.side_effect = Exception("Init failed")
            
            result = await translator.initialize()
            
            assert result is False
            assert translator.is_initialized is False
    
    async def test_translate_english_to_spanish(self, translator, mock_engines):
        """Test basic translation functionality"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        result = await translator.translate(
            text="Hello world",
            target_language="es",
            source_language="en"
        )
        
        assert result is not None
        assert "translated_text" in result
        assert result["source_language"] == "en"
        assert result["target_language"] == "es"
    
    async def test_translate_with_indian_language_priority(self, translator, mock_engines):
        """Test Indic translator priority for Indian languages"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        # Mock Indic translator to return better result
        mock_engines['indic'].translate.return_value = {
            "translated_text": "नमस्ते",
            "source_language": "en",
            "target_language": "hi",
            "confidence_score": 0.95,
            "engine": "indic",
            "processing_time_ms": 80
        }
        
        result = await translator.translate(
            text="Hello",
            target_language="hi",
            source_language="en"
        )
        
        # Should use Indic translator for Hindi
        mock_engines['indic'].translate.assert_called()
        assert result["engine"] == "indic"
    
    async def test_translate_fallback_mechanism(self, translator, mock_engines):
        """Test fallback to other engines when primary fails"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        # Make Google translator fail
        mock_engines['google'].translate.side_effect = Exception("Google failed")
        
        # Should fallback to other engines
        result = await translator.translate(
            text="Hello",
            target_language="es",
            source_language="en"
        )
        
        assert result is not None
        assert result["engine"] in ["argos", "local", "indic"]
    
    async def test_translate_batch(self, translator, mock_engines):
        """Test batch translation functionality"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        batch_requests = [
            {
                'text': 'Hello',
                'target_language': 'es',
                'source_language': 'en'
            },
            {
                'text': 'World',
                'target_language': 'es', 
                'source_language': 'en'
            }
        ]
        
        results = await translator.translate_batch(batch_requests)
        
        assert len(results) == 2
        for result in results:
            assert "translated_text" in result
            assert result["status"] == "success"
    
    async def test_detect_language(self, translator, mock_engines):
        """Test language detection"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        # Mock language detection
        mock_engines['google'].detect_language = AsyncMock(return_value={
            "language": "en",
            "confidence": 0.95
        })
        
        result = await translator.detect_language("Hello world")
        
        assert result["language"] == "en"
        assert result["confidence"] > 0.9
    
    async def test_get_engine_priority(self, translator):
        """Test engine priority determination"""
        # Test Indian language priority
        priority = translator._get_engine_priority("hi", "en")
        assert priority[0] == "indic"
        
        # Test general language priority
        priority = translator._get_engine_priority("es", "en")
        assert "google" in priority[:2]
    
    async def test_select_best_translation(self, translator):
        """Test selection of best translation from multiple results"""
        results = [
            {
                "engine": "google",
                "confidence_score": 0.85,
                "quality_score": 0.8,
                "translated_text": "Hola mundo"
            },
            {
                "engine": "indic",
                "confidence_score": 0.95,
                "quality_score": 0.9,
                "translated_text": "Hola mundo"
            },
            {
                "engine": "local",
                "confidence_score": 0.7,
                "quality_score": 0.6,
                "translated_text": "Hola mundo"
            }
        ]
        
        best = translator._select_best_translation(results, "es")
        
        # Should select Indic translator due to higher scores
        assert best["engine"] == "indic"
        assert best["confidence_score"] == 0.95
    
    async def test_health_check(self, translator, mock_engines):
        """Test health check functionality"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        health = await translator.health_check()
        
        assert health["status"] == "healthy"
        assert "engines" in health
        assert len(health["engines"]) > 0
    
    async def test_get_supported_languages(self, translator, mock_engines):
        """Test getting supported languages"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        languages = await translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "es" in languages
        assert "hi" in languages
    
    async def test_engine_timeout_handling(self, translator, mock_engines):
        """Test timeout handling for slow engines"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        # Make Google translator slow
        async def slow_translate(*args, **kwargs):
            await asyncio.sleep(2)
            return {"translated_text": "Slow result"}
        
        mock_engines['google'].translate = slow_translate
        
        # Should timeout and fallback
        start_time = time.time()
        result = await translator.translate(
            text="Hello",
            target_language="es",
            source_language="en",
            context={"timeout": 1}
        )
        end_time = time.time()
        
        # Should not take more than reasonable time due to timeout
        assert (end_time - start_time) < 3
        assert result is not None
    
    async def test_context_parameter_handling(self, translator, mock_engines):
        """Test context parameter handling"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        context = {
            "user_id": "test_user",
            "domain": "meditation",
            "cultural_adaptation": True,
            "use_cache": True
        }
        
        result = await translator.translate(
            text="Hello",
            target_language="es",
            source_language="en",
            context=context
        )
        
        # Verify context is passed through
        assert result is not None
        # Engine should have been called with context
        args, kwargs = mock_engines['google'].translate.call_args
        assert 'context' in kwargs or len(args) > 3
    
    async def test_error_handling_all_engines_fail(self, translator, mock_engines):
        """Test error handling when all engines fail"""
        translator.engines = mock_engines
        translator.is_initialized = True
        
        # Make all engines fail
        for engine in mock_engines.values():
            engine.translate.side_effect = Exception("Engine failed")
        
        with pytest.raises(Exception):
            await translator.translate(
                text="Hello",
                target_language="es",
                source_language="en"
            )
    
    async def test_uninitialized_translator(self, translator):
        """Test handling of uninitialized translator"""
        # Don't initialize
        translator.is_initialized = False
        
        with pytest.raises(Exception):
            await translator.translate(
                text="Hello",
                target_language="es",
                source_language="en"
            )
    
    async def test_quality_score_calculation(self, translator):
        """Test quality score calculation"""
        result = {
            "confidence_score": 0.9,
            "engine": "google",
            "processing_time_ms": 100,
            "translated_text": "Hola mundo"
        }
        
        quality_score = translator._calculate_quality_score(result, "es")
        
        assert isinstance(quality_score, float)
        assert 0.0 <= quality_score <= 1.0
    
    async def test_indian_language_detection(self, translator):
        """Test Indian language detection"""
        # Test various Indian languages
        indian_langs = ["hi", "bn", "ta", "te", "ml", "kn", "gu", "or", "pa", "as", "mr"]
        
        for lang in indian_langs:
            is_indian = translator._is_indian_language(lang)
            assert is_indian is True
        
        # Test non-Indian languages
        non_indian_langs = ["en", "es", "fr", "de", "zh", "ja"]
        for lang in non_indian_langs:
            is_indian = translator._is_indian_language(lang)
            assert is_indian is False
    
    async def test_engine_availability_check(self, translator, mock_engines):
        """Test engine availability checking"""
        translator.engines = mock_engines
        
        # Test available engine
        available = await translator._is_engine_available("google")
        assert available is True
        
        # Test unavailable engine (make health check fail)
        mock_engines['local'].health_check.side_effect = Exception("Engine down")
        available = await translator._is_engine_available("local")
        assert available is False
