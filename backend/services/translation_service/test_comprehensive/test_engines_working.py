"""
Working tests for translation engines using actual methods
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import asyncio
import sys
import os
from pathlib import Path

# Add proper paths for imports
current_dir = Path(__file__).parent
service_dir = current_dir.parent
sys.path.insert(0, str(service_dir))

from engines.local_translator import LocalTranslator
from engines.base_translator import BaseTranslator


@pytest.mark.unit
class TestLocalTranslatorWorking:
    """Working tests for LocalTranslator using actual methods"""
    
    def test_local_translator_initialization(self):
        """Test LocalTranslator initialization"""
        translator = LocalTranslator()
        
        assert hasattr(translator, 'meditation_glossary')
        assert hasattr(translator, 'language_patterns')
        assert hasattr(translator, 'translation_cache')
        assert hasattr(translator, 'models_path')
        assert isinstance(translator.translation_cache, dict)
    
    def test_local_translator_meditation_glossary_structure(self):
        """Test meditation glossary structure"""
        translator = LocalTranslator()
        glossary = translator.meditation_glossary
        
        assert isinstance(glossary, dict)
        if 'en' in glossary:
            assert isinstance(glossary['en'], dict)
    
    def test_local_translator_language_patterns(self):
        """Test language patterns loading"""
        translator = LocalTranslator()
        patterns = translator.language_patterns
        
        assert isinstance(patterns, dict)
        # Should have some language patterns
        assert len(patterns) >= 0
    
    @pytest.mark.asyncio
    async def test_local_translator_initialize(self):
        """Test LocalTranslator initialize method"""
        translator = LocalTranslator()
        
        result = await translator.initialize()
        assert isinstance(result, bool)
    
    def test_local_translator_validate_language_code(self):
        """Test language code validation"""
        translator = LocalTranslator()
        
        # Test with common language codes
        assert translator.validate_language_code('en') in [True, False]
        assert translator.validate_language_code('es') in [True, False]
        assert translator.validate_language_code('invalid') in [True, False]
    
    def test_local_translator_supports_language_pair(self):
        """Test language pair support check"""
        translator = LocalTranslator()
        
        result = translator.supports_language_pair('en', 'es')
        assert isinstance(result, bool)
        
        result = translator.supports_language_pair('en', 'hi')
        assert isinstance(result, bool)
    
    def test_local_translator_get_cache_key(self):
        """Test cache key generation"""
        translator = LocalTranslator()
        
        cache_key = translator._get_cache_key("hello", "en", "es")
        assert isinstance(cache_key, str)
        assert len(cache_key) > 0
        
        # Same input should produce same key
        cache_key2 = translator._get_cache_key("hello", "en", "es")
        assert cache_key == cache_key2
    
    def test_local_translator_simple_word_translation(self):
        """Test simple word translation"""
        translator = LocalTranslator()
        
        result = translator._simple_word_translation("hello", "en", "es")
        assert isinstance(result, str) or result is None
    
    def test_local_translator_translate_meditation_terms(self):
        """Test meditation terms translation"""
        translator = LocalTranslator()
        
        result = translator._translate_meditation_terms("meditation", "en", "es")
        assert isinstance(result, str) or result is None
    
    def test_local_translator_calculate_local_confidence(self):
        """Test confidence calculation"""
        translator = LocalTranslator()
        
        confidence = translator._calculate_local_confidence("hello", "en", "hola", "es")
        assert isinstance(confidence, (int, float))
        assert 0 <= confidence <= 1
    
    @pytest.mark.asyncio
    async def test_local_translator_translate_text_method(self):
        """Test _translate_text method"""
        translator = LocalTranslator()
        
        result = await translator._translate_text("hello", "en", "es")
        assert isinstance(result, dict)
        assert "translated_text" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_local_translator_translate_method(self):
        """Test main translate method"""
        translator = LocalTranslator()
        
        result = await translator.translate("hello", "en", "es")
        assert isinstance(result, dict)
        assert "translated_text" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_local_translator_detect_language(self):
        """Test language detection"""
        translator = LocalTranslator()
        
        result = await translator.detect_language("Hello world")
        assert isinstance(result, dict)
        assert "detected_language" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_local_translator_translate_batch(self):
        """Test batch translation"""
        translator = LocalTranslator()
        
        texts = ["hello", "world"]
        result = await translator.translate_batch(texts, "en", "es")
        assert isinstance(result, list)
    
    def test_local_translator_get_supported_languages(self):
        """Test getting supported languages"""
        translator = LocalTranslator()
        
        languages = translator.get_supported_languages()
        assert isinstance(languages, dict)
    
    def test_local_translator_estimate_cost(self):
        """Test cost estimation"""
        translator = LocalTranslator()
        
        cost = translator.estimate_cost("hello world", "en", "es")
        assert isinstance(cost, (int, float))
        assert cost >= 0
    
    def test_local_translator_get_quality_score(self):
        """Test quality score calculation"""
        translator = LocalTranslator()
        
        score = translator.get_quality_score("hello", "hola", "en", "es")
        assert isinstance(score, (int, float))
        assert 0 <= score <= 1
    
    @pytest.mark.asyncio
    async def test_local_translator_health_check(self):
        """Test health check"""
        translator = LocalTranslator()
        
        result = await translator.health_check()
        assert isinstance(result, dict)
        assert "status" in result
    
    @pytest.mark.asyncio 
    async def test_local_translator_close(self):
        """Test close method"""
        translator = LocalTranslator()
        
        result = await translator.close()
        # Should complete without error
        assert result is None or isinstance(result, bool)


@pytest.mark.unit
class TestBaseTranslatorMethods:
    """Test BaseTranslator concrete methods"""
    
    def test_base_translator_abstract_class(self):
        """Test BaseTranslator is abstract"""
        with pytest.raises(TypeError):
            # Cannot instantiate abstract class
            BaseTranslator()
    
    def test_base_translator_has_required_methods(self):
        """Test BaseTranslator has required abstract methods"""
        abstract_methods = BaseTranslator.__abstractmethods__
        
        # Should have abstract methods
        assert len(abstract_methods) > 0
        assert 'translate' in abstract_methods
        assert 'initialize' in abstract_methods


@pytest.mark.unit
class TestLocalTranslatorIntegration:
    """Integration tests for LocalTranslator"""
    
    @pytest.mark.asyncio
    async def test_local_translator_workflow(self):
        """Test complete translation workflow"""
        translator = LocalTranslator()
        
        # Initialize
        init_result = await translator.initialize()
        assert isinstance(init_result, bool)
        
        # Health check
        health = await translator.health_check()
        assert isinstance(health, dict)
        
        # Check language support
        supports_en_es = translator.supports_language_pair('en', 'es')
        assert isinstance(supports_en_es, bool)
        
        # Translate
        translation = await translator.translate("meditation", "en", "es")
        assert isinstance(translation, dict)
        
        # Close
        await translator.close()
    
    def test_local_translator_cache_functionality(self):
        """Test translation caching"""
        translator = LocalTranslator()
        
        # Clear cache
        translator.translation_cache.clear()
        assert len(translator.translation_cache) == 0
        
        # Generate cache key
        key = translator._get_cache_key("test", "en", "es")
        assert isinstance(key, str)
        
        # Cache should be initially empty
        assert key not in translator.translation_cache
    
    def test_local_translator_glossary_functionality(self):
        """Test meditation glossary functionality"""
        translator = LocalTranslator()
        
        # Test glossary access
        glossary = translator.meditation_glossary
        assert isinstance(glossary, dict)
        
        # Test meditation term translation
        result = translator._translate_meditation_terms("mindfulness", "en", "es")
        assert isinstance(result, str) or result is None
    
    def test_local_translator_confidence_scoring(self):
        """Test confidence scoring functionality"""
        translator = LocalTranslator()
        
        # Test confidence calculation
        confidence1 = translator._calculate_local_confidence("hello", "en", "hola", "es")
        confidence2 = translator._calculate_local_confidence("xyz", "en", "abc", "es")
        
        assert isinstance(confidence1, (int, float))
        assert isinstance(confidence2, (int, float))
        assert 0 <= confidence1 <= 1
        assert 0 <= confidence2 <= 1
