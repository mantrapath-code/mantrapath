"""
Focused tests to boost engines coverage from 41% to 60%+
Target specific uncovered lines in LocalTranslator, EnhancedMultiTranslator, FreeGoogleTranslator
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import sys
import os
import json
from datetime import datetime

# Mock all external dependencies first
mock_modules = {
    'shared.auth': MagicMock(),
    'shared.database': MagicMock(), 
    'shared.events': MagicMock(),
    'shared.redis_client': MagicMock(),
    'redis.asyncio': MagicMock(),
    'googletrans': MagicMock(),
    'transformers': MagicMock(),
    'torch': MagicMock(),
    'argostranslate': MagicMock(),
    'azure.cognitiveservices.language.translator': MagicMock(),
    'azure.core.credentials': MagicMock()
}

for module_name, mock_module in mock_modules.items():
    sys.modules[module_name] = mock_module

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from engines.base_translator import TranslationResult
from engines.local_translator import LocalTranslator
from engines.free_google_translator import FreeGoogleTranslator
from engines.enhanced_multi_translator import EnhancedMultiTranslator

@pytest.mark.asyncio
class TestFocusedEnginesBoost:
    """Focused tests targeting specific uncovered lines"""
    
    async def test_local_translator_initialization_flow(self):
        """Test LocalTranslator initialization covering more paths"""
        translator = LocalTranslator()
        
        # Test initialize method
        success = await translator.initialize()
        assert isinstance(success, bool)
        
        # Test close method if it exists
        if hasattr(translator, 'close'):
            await translator.close()
        
        # Test estimate_cost
        cost = translator.estimate_cost("test text", "en", "es")
        assert isinstance(cost, float)
        assert cost >= 0.0
    
    async def test_local_translator_edge_cases(self):
        """Test LocalTranslator edge cases for coverage"""
        translator = LocalTranslator()
        
        # Test empty text translation
        result = await translator.translate("", "en", "es")
        assert isinstance(result, TranslationResult)
        
        # Test same language translation
        result = await translator.translate("hello", "en", "en")
        assert isinstance(result, TranslationResult)
        assert result.source_language == "en"
        assert result.target_language == "en"
        
        # Test unsupported language validation
        assert translator.validate_language_code("") == False
        assert translator.validate_language_code("xyz") == False
        assert translator.validate_language_code("123") == False
        
        # Test valid language validation
        assert translator.validate_language_code("en") == True
        assert translator.validate_language_code("es") == True
    
    async def test_local_translator_batch_translation(self):
        """Test LocalTranslator batch translation"""
        translator = LocalTranslator()
        
        texts = ["hello", "world", "test"]
        results = await translator.translate_batch(texts, "en", "es")
        
        assert isinstance(results, list)
        assert len(results) == len(texts)
        
        for result in results:
            assert isinstance(result, TranslationResult)
    
    async def test_local_translator_glossary_handling(self):
        """Test LocalTranslator meditation glossary functionality"""
        translator = LocalTranslator()
        
        # Test meditation term translation
        meditation_terms = ["peace", "meditation", "mindfulness", "compassion"]
        
        for term in meditation_terms:
            result = await translator.translate(term, "en", "hi")
            assert isinstance(result, TranslationResult)
            assert result.translated_text is not None
    
    async def test_enhanced_multi_translator_initialization(self):
        """Test EnhancedMultiTranslator initialization paths"""
        translator = EnhancedMultiTranslator()
        
        # Test with custom config
        custom_translator = EnhancedMultiTranslator(
            name="custom_multi",
            config={"max_engines": 3, "timeout": 10}
        )
        
        assert custom_translator.name == "custom_multi"
        assert custom_translator.config["max_engines"] == 3
        
        # Test initialize
        success = await translator.initialize()
        assert isinstance(success, bool)
    
    async def test_enhanced_multi_translator_engine_selection(self):
        """Test EnhancedMultiTranslator engine selection logic"""
        translator = EnhancedMultiTranslator()
        
        # Test Indian language detection
        assert translator.is_indian_language("hi") == True
        assert translator.is_indian_language("en") == False
        assert translator.is_indian_language("ta") == True
        
        # Test engine priority
        google_priority = translator.get_engine_priority("google")
        unknown_priority = translator.get_engine_priority("unknown")
        assert google_priority < unknown_priority
        
        # Test language pair support
        assert translator.supports_language_pair("en", "es") == True
        assert translator.supports_language_pair("invalid", "invalid") == False
    
    async def test_enhanced_multi_translator_quality_scoring(self):
        """Test EnhancedMultiTranslator quality scoring logic"""
        translator = EnhancedMultiTranslator()
        
        # Test quality score calculation
        score1 = await translator.get_quality_score("hello", "hola", "en", "es")
        assert isinstance(score1, float)
        assert 0.0 <= score1 <= 1.0
        
        # Test with Indian languages (should get bonus)
        score2 = await translator.get_quality_score("hello", "नमस्ते", "en", "hi")
        assert isinstance(score2, float)
        assert 0.0 <= score2 <= 1.0
        
        # Test with empty translation
        score3 = await translator.get_quality_score("hello", "", "en", "es")
        assert isinstance(score3, float)
        assert score3 == 0.5
        
        # Test with same text
        score4 = await translator.get_quality_score("hello", "hello", "en", "es")
        assert isinstance(score4, float)
        assert score4 == 0.5
    
    async def test_enhanced_multi_translator_health_check(self):
        """Test EnhancedMultiTranslator health check functionality"""
        translator = EnhancedMultiTranslator()
        
        # Initialize first
        await translator.initialize()
        
        # Test health check
        health = await translator.health_check()
        assert isinstance(health, dict)
        assert "status" in health
        assert "engines" in health
        assert "initialized" in health
        assert "supported_engines" in health
        
        assert health["initialized"] == translator.is_initialized
        assert health["status"] in ["healthy", "degraded"]
    
    async def test_free_google_translator_with_googletrans(self):
        """Test FreeGoogleTranslator with mocked googletrans"""
        
        # Mock googletrans module
        with patch('engines.free_google_translator.Translator') as MockTranslator:
            mock_instance = MagicMock()
            MockTranslator.return_value = mock_instance
            
            # Mock translation response
            mock_result = MagicMock()
            mock_result.text = "Hola"
            mock_result.src = "en"
            mock_result.dest = "es"
            mock_instance.translate.return_value = mock_result
            
            # Mock detection response
            mock_detection = MagicMock()
            mock_detection.lang = "en"
            mock_detection.confidence = 0.95
            mock_instance.detect.return_value = mock_detection
            
            translator = FreeGoogleTranslator()
            
            # Test initialization
            success = await translator.initialize()
            assert isinstance(success, bool)
            
            # Test translation
            result = await translator.translate("Hello", "en", "es")
            assert isinstance(result, TranslationResult)
            assert result.translated_text == "Hola"
            
            # Test detection
            lang, confidence = await translator.detect_language("Hello")
            assert lang == "en"
            assert confidence == 0.95
            
            # Test health check
            health = await translator.health_check()
            assert isinstance(health, dict)
            assert "status" in health
    
    async def test_free_google_translator_fallback_behavior(self):
        """Test FreeGoogleTranslator fallback when googletrans fails"""
        
        # Test without googletrans (should use fallback)
        with patch('engines.free_google_translator.Translator', side_effect=ImportError):
            translator = FreeGoogleTranslator()
            
            # Should still initialize
            success = await translator.initialize()
            assert isinstance(success, bool)
            
            # Should use fallback translation
            result = await translator.translate("Hello", "en", "es")
            assert isinstance(result, TranslationResult)
            assert result.engine == "free_google"
            
            # Should provide fallback detection
            lang, confidence = await translator.detect_language("Hello")
            assert isinstance(lang, str)
            assert isinstance(confidence, float)
    
    async def test_free_google_translator_error_handling(self):
        """Test FreeGoogleTranslator error handling"""
        
        with patch('engines.free_google_translator.Translator') as MockTranslator:
            mock_instance = MagicMock()
            MockTranslator.return_value = mock_instance
            
            # Test translation exception handling
            mock_instance.translate.side_effect = Exception("Translation failed")
            
            translator = FreeGoogleTranslator()
            await translator.initialize()
            
            # Should handle exception gracefully
            result = await translator.translate("Hello", "en", "es")
            assert isinstance(result, TranslationResult)
            
            # Test detection exception handling
            mock_instance.detect.side_effect = Exception("Detection failed")
            
            lang, confidence = await translator.detect_language("Hello")
            assert isinstance(lang, str)
            assert isinstance(confidence, float)
    
    def test_translation_result_comprehensive(self):
        """Test TranslationResult with all parameters and edge cases"""
        
        # Test minimal creation
        result1 = TranslationResult(
            translated_text="Hola",
            source_language="en",
            target_language="es",
            confidence_score=0.9
        )
        assert result1.engine == "unknown"  # Default
        assert result1.quality_score == 0.9  # Should default to confidence
        
        # Test full creation
        result2 = TranslationResult(
            translated_text="Bonjour",
            source_language="en", 
            target_language="fr",
            confidence_score=0.8,
            engine="test_engine",
            processing_time_ms=1500,
            quality_score=0.85,
            cache_hit=True,
            cultural_notes=["formal"],
            custom_terms_used=["greeting"],
            metadata={"domain": "general", "context": "formal"}
        )
        
        assert result2.engine == "test_engine"
        assert result2.quality_score == 0.85
        assert result2.cache_hit == True
        assert result2.cultural_notes == ["formal"]
        assert result2.custom_terms_used == ["greeting"]
        assert result2.metadata["domain"] == "general"
        assert isinstance(result2.timestamp, datetime)
    
    async def test_batch_translation_comprehensive(self):
        """Test comprehensive batch translation scenarios"""
        
        # Test with LocalTranslator
        local = LocalTranslator()
        texts = ["hello", "world", "peace", "love"]
        results = await local.translate_batch(texts, "en", "hi")
        
        assert len(results) == len(texts)
        for result in results:
            assert isinstance(result, TranslationResult)
            assert result.source_language == "en"
            assert result.target_language == "hi"
        
        # Test with EnhancedMultiTranslator
        multi = EnhancedMultiTranslator()
        results2 = await multi.translate_batch(texts, "en", "es")
        
        assert len(results2) == len(texts)
        for result in results2:
            assert isinstance(result, TranslationResult)
    
    async def test_language_detection_comprehensive(self):
        """Test comprehensive language detection scenarios"""
        
        # Test LocalTranslator detection
        local = LocalTranslator()
        
        test_texts = [
            "Hello world",
            "Hola mundo", 
            "Bonjour monde",
            "Hallo Welt",
            "नमस्ते दुनिया"
        ]
        
        for text in test_texts:
            lang, confidence = await local.detect_language(text)
            assert isinstance(lang, str)
            assert isinstance(confidence, float)
            assert 0.0 <= confidence <= 1.0
        
        # Test EnhancedMultiTranslator detection
        multi = EnhancedMultiTranslator()
        
        for text in test_texts:
            lang, confidence = await multi.detect_language(text)
            assert isinstance(lang, str)
            assert isinstance(confidence, float)
            assert 0.0 <= confidence <= 1.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
