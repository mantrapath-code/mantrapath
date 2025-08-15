"""
Working tests for translation engines
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.mark.asyncio
class TestLocalTranslator:
    """Test Local Translator with mocked dependencies"""
    
    @pytest.fixture
    async def translator(self):
        """Create local translator"""
        from engines.local_translator import LocalTranslator
        translator = LocalTranslator()
        return translator
    
    async def test_initialization(self, translator):
        """Test translator initialization"""
        result = await translator.initialize()
        assert result is True
        assert translator.is_initialized is True
    
    async def test_translate_same_language(self, translator):
        """Test translation when source and target are same"""
        await translator.initialize()
        
        result = await translator.translate(
            text="Hello world",
            target_language="en", 
            source_language="en"
        )
        
        assert result["translated_text"] == "Hello world"
        assert result["confidence_score"] == 1.0
    
    async def test_translate_empty_text(self, translator):
        """Test translation of empty text"""
        await translator.initialize()
        
        result = await translator.translate(
            text="",
            target_language="es",
            source_language="en"
        )
        
        assert result["translated_text"] == ""
    
    async def test_detect_language_english(self, translator):
        """Test language detection for English"""
        await translator.initialize()
        
        result = await translator.detect_language("Hello world, how are you?")
        
        assert result["language"] == "en"
        assert result["confidence"] > 0.0
    
    async def test_detect_language_spanish(self, translator):
        """Test language detection for Spanish"""
        await translator.initialize()
        
        result = await translator.detect_language("Hola mundo, como estas?")
        
        assert result["language"] == "es"
        assert result["confidence"] > 0.0
    
    async def test_get_supported_languages(self, translator):
        """Test getting supported languages"""
        await translator.initialize()
        
        languages = await translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "es" in languages
    
    async def test_health_check(self, translator):
        """Test health check"""
        await translator.initialize()
        
        health = await translator.health_check()
        
        assert health["status"] == "healthy"
        assert health["engine"] == "local"


@pytest.mark.asyncio 
class TestBaseTranslator:
    """Test Base Translator functionality"""
    
    @pytest.fixture
    def base_translator(self):
        """Create base translator"""
        from engines.base_translator import BaseTranslator
        return BaseTranslator()
    
    def test_initialization_default(self, base_translator):
        """Test base translator initialization"""
        assert base_translator.is_initialized is False
        assert base_translator.name == "base"
    
    async def test_translate_not_implemented(self, base_translator):
        """Test that translate method raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            await base_translator.translate("test", "es", "en")
    
    async def test_detect_language_not_implemented(self, base_translator):
        """Test that detect_language raises NotImplementedError"""
        with pytest.raises(NotImplementedError):
            await base_translator.detect_language("test")
    
    async def test_get_supported_languages_not_implemented(self, base_translator):
        """Test that get_supported_languages raises NotImplementedError"""  
        with pytest.raises(NotImplementedError):
            await base_translator.get_supported_languages()
    
    async def test_health_check_basic(self, base_translator):
        """Test basic health check"""
        health = await base_translator.health_check()
        
        assert "status" in health
        assert "engine" in health


@pytest.mark.asyncio
class TestFreeGoogleTranslator:
    """Test Free Google Translator with mocked HTTP calls"""
    
    @pytest.fixture
    async def translator(self):
        """Create Google translator"""
        from engines.free_google_translator import FreeGoogleTranslator
        translator = FreeGoogleTranslator()
        await translator.initialize()
        return translator
    
    async def test_initialization(self):
        """Test Google translator initialization"""
        from engines.free_google_translator import FreeGoogleTranslator
        translator = FreeGoogleTranslator()
        result = await translator.initialize()
        
        assert result is True
        assert translator.is_initialized is True
    
    @patch('httpx.AsyncClient.get')
    async def test_translate_success(self, mock_get, translator):
        """Test successful translation with mocked response"""
        # Mock successful HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'window.TRANSLATION_DATA = {"translated_text": "Hola mundo"};'
        mock_get.return_value = mock_response
        
        result = await translator.translate(
            text="Hello world",
            target_language="es",
            source_language="en"
        )
        
        assert result["source_language"] == "en"
        assert result["target_language"] == "es"
        assert result["engine"] == "google"
    
    @patch('httpx.AsyncClient.get') 
    async def test_detect_language_success(self, mock_get, translator):
        """Test successful language detection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'window.DETECTION_DATA = {"language": "en", "confidence": 0.95};'
        mock_get.return_value = mock_response
        
        result = await translator.detect_language("Hello world")
        
        assert "language" in result
        assert "confidence" in result
    
    async def test_get_supported_languages(self, translator):
        """Test getting supported languages"""
        languages = await translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) > 0
    
    async def test_health_check(self, translator):
        """Test health check"""
        health = await translator.health_check()
        
        assert health["status"] == "healthy"
        assert health["engine"] == "google"


@pytest.mark.asyncio
class TestEnhancedMultiTranslator:
    """Test Enhanced Multi Translator with mocked engines"""
    
    @pytest.fixture
    async def translator(self):
        """Create multi translator with mocked engines"""
        from engines.enhanced_multi_translator import EnhancedMultiTranslator
        translator = EnhancedMultiTranslator()
        
        # Mock the engines
        translator.engines = {
            'local': AsyncMock(),
            'google': AsyncMock(),
            'indic': AsyncMock(),
            'argos': AsyncMock()
        }
        
        # Set up mock responses
        for engine in translator.engines.values():
            engine.translate.return_value = {
                "translated_text": "Test translation",
                "source_language": "en",
                "target_language": "es",
                "confidence_score": 0.9,
                "engine": "mock"
            }
            engine.health_check.return_value = {"status": "healthy"}
        
        translator.is_initialized = True
        return translator
    
    async def test_translate_basic(self, translator):
        """Test basic translation"""
        result = await translator.translate(
            text="Hello",
            target_language="es",
            source_language="en"
        )
        
        assert result is not None
        assert "translated_text" in result
    
    async def test_translate_indian_language(self, translator):
        """Test translation to Indian language prioritizes Indic translator"""
        # Mock Indic translator to return better result
        translator.engines['indic'].translate.return_value = {
            "translated_text": "नमस्ते",
            "source_language": "en",
            "target_language": "hi", 
            "confidence_score": 0.95,
            "engine": "indic"
        }
        
        result = await translator.translate(
            text="Hello",
            target_language="hi",
            source_language="en"
        )
        
        # Should use Indic translator
        translator.engines['indic'].translate.assert_called()
    
    async def test_get_engine_priority(self, translator):
        """Test engine priority logic"""
        # Indian language should prioritize Indic translator
        priority = translator._get_engine_priority("hi", "en")
        assert priority[0] == "indic"
        
        # Non-Indian language should prioritize Google
        priority = translator._get_engine_priority("es", "en")
        assert "google" in priority[:2]
    
    def test_is_indian_language(self, translator):
        """Test Indian language detection"""
        assert translator._is_indian_language("hi") is True
        assert translator._is_indian_language("bn") is True
        assert translator._is_indian_language("ta") is True
        assert translator._is_indian_language("en") is False
        assert translator._is_indian_language("es") is False
    
    async def test_health_check(self, translator):
        """Test health check"""
        health = await translator.health_check()
        
        assert health["status"] == "healthy"
        assert "engines" in health


@pytest.mark.asyncio
class TestCulturalAdaptationService:
    """Test Cultural Adaptation Service"""
    
    @pytest.fixture
    async def service(self):
        """Create cultural adaptation service"""
        from engines.cultural_adaptation import CulturalAdaptationService
        service = CulturalAdaptationService()
        await service.initialize()
        return service
    
    async def test_initialization(self):
        """Test service initialization"""
        from engines.cultural_adaptation import CulturalAdaptationService
        service = CulturalAdaptationService()
        result = await service.initialize()
        
        assert result is True
        assert service.is_initialized is True
    
    async def test_adapt_translation_basic(self, service):
        """Test basic translation adaptation"""
        result = await service.adapt_translation(
            original_text="Hello",
            translated_text="Hola",
            source_language="en",
            target_language="es",
            cultural_context={}
        )
        
        assert result is not None
        assert "adapted_text" in result
    
    async def test_detect_cultural_context(self, service):
        """Test cultural context detection"""
        context = await service.detect_cultural_context(
            "I practice meditation daily",
            "en"
        )
        
        assert context is not None
        assert isinstance(context, dict)
    
    async def test_get_cultural_preferences(self, service):
        """Test getting cultural preferences"""
        prefs = await service.get_cultural_preferences("es", "spain")
        
        assert prefs is not None
        assert isinstance(prefs, dict)
    
    async def test_health_check(self, service):
        """Test health check"""
        health = await service.health_check()
        
        assert health["status"] == "healthy"
        assert health["service"] == "cultural_adaptation"
