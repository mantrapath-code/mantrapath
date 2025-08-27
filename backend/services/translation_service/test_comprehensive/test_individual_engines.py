"""
Comprehensive unit tests for individual translation engines
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import asyncio

from engines.free_google_translator import FreeGoogleTranslator
from engines.argos_translator import ArgosTranslator
from engines.indic_translator import IndicTranslator
from engines.local_translator import LocalTranslator


@pytest.mark.asyncio
class TestFreeGoogleTranslator:
    """Test Free Google Translator"""
    
    @pytest.fixture
    async def translator(self):
        translator = FreeGoogleTranslator()
        await translator.initialize()
        return translator
    
    async def test_initialization(self):
        """Test Google translator initialization"""
        translator = FreeGoogleTranslator()
        result = await translator.initialize()
        
        assert result is True
        assert translator.is_initialized is True
    
    @patch('httpx.AsyncClient.get')
    async def test_translate_success(self, mock_get, translator):
        """Test successful translation"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "translations": [{
                    "translatedText": "Hola mundo"
                }]
            }
        }
        mock_get.return_value = mock_response
        
        result = await translator.translate(
            text="Hello world",
            target_language="es",
            source_language="en"
        )
        
        assert result["translated_text"] == "Hola mundo"
        assert result["source_language"] == "en"
        assert result["target_language"] == "es"
        assert result["engine"] == "google"
    
    @patch('httpx.AsyncClient.get')
    async def test_translate_http_error(self, mock_get, translator):
        """Test translation with HTTP error"""
        mock_get.side_effect = httpx.HTTPError("Network error")
        
        with pytest.raises(Exception):
            await translator.translate(
                text="Hello world",
                target_language="es",
                source_language="en"
            )
    
    @patch('httpx.AsyncClient.get')
    async def test_detect_language(self, mock_get, translator):
        """Test language detection"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "detections": [[{
                    "language": "en",
                    "confidence": 0.95
                }]]
            }
        }
        mock_get.return_value = mock_response
        
        result = await translator.detect_language("Hello world")
        
        assert result["language"] == "en"
        assert result["confidence"] == 0.95
    
    async def test_get_supported_languages(self, translator):
        """Test getting supported languages"""
        languages = await translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "es" in languages
    
    async def test_health_check(self, translator):
        """Test health check"""
        health = await translator.health_check()
        
        assert health["status"] == "healthy"
        assert health["engine"] == "google"


@pytest.mark.asyncio
class TestArgosTranslator:
    """Test Argos Translator"""
    
    @pytest.fixture
    async def translator(self):
        translator = ArgosTranslator()
        return translator
    
    async def test_initialization_success(self, translator):
        """Test successful initialization"""
        with patch('engines.argos_translator.argostranslate.package') as mock_package:
            mock_package.get_available_packages.return_value = []
            mock_package.get_installed_packages.return_value = []
            
            result = await translator.initialize()
            
            assert result is True
            assert translator.is_initialized is True
    
    async def test_initialization_no_argos(self):
        """Test initialization when argostranslate is not available"""
        with patch('engines.argos_translator.argostranslate', None):
            translator = ArgosTranslator()
            result = await translator.initialize()
            
            assert result is False
            assert translator.is_initialized is False
    
    async def test_translate_with_installed_package(self, translator):
        """Test translation with installed language package"""
        translator.is_initialized = True
        
        with patch('engines.argos_translator.argostranslate.translate') as mock_translate:
            mock_translate.translate.return_value = "Hola mundo"
            
            result = await translator.translate(
                text="Hello world",
                target_language="es",
                source_language="en"
            )
            
            assert result["translated_text"] == "Hola mundo"
            assert result["engine"] == "argos"
    
    async def test_translate_no_package(self, translator):
        """Test translation when no package is available"""
        translator.is_initialized = True
        translator.installed_packages = {}
        
        with pytest.raises(Exception):
            await translator.translate(
                text="Hello world",
                target_language="xyz",  # Unsupported language
                source_language="en"
            )
    
    async def test_get_supported_languages(self, translator):
        """Test getting supported languages"""
        translator.is_initialized = True
        translator.installed_packages = {
            ("en", "es"): True,
            ("en", "fr"): True
        }
        
        languages = await translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert len(languages) > 0


@pytest.mark.asyncio 
class TestIndicTranslator:
    """Test Indic Translator"""
    
    @pytest.fixture
    async def translator(self):
        translator = IndicTranslator()
        return translator
    
    async def test_initialization_success(self, translator):
        """Test successful initialization"""
        with patch('engines.indic_translator.IndicTrans2') as mock_indictrans:
            mock_indictrans.return_value = MagicMock()
            
            result = await translator.initialize()
            
            assert result is True
            assert translator.is_initialized is True
    
    async def test_initialization_no_indictrans(self):
        """Test initialization when IndicTrans2 is not available"""
        with patch('engines.indic_translator.IndicTrans2', side_effect=ImportError):
            translator = IndicTranslator()
            result = await translator.initialize()
            
            assert result is False
    
    async def test_translate_english_to_hindi(self, translator):
        """Test English to Hindi translation"""
        translator.is_initialized = True
        translator.model = MagicMock()
        translator.model.translate.return_value = ["नमस्ते"]
        
        result = await translator.translate(
            text="Hello",
            target_language="hi",
            source_language="en"
        )
        
        assert result["translated_text"] == "नमस्ते"
        assert result["source_language"] == "en"
        assert result["target_language"] == "hi"
        assert result["engine"] == "indic"
    
    async def test_translate_hindi_to_english(self, translator):
        """Test Hindi to English translation"""
        translator.is_initialized = True
        translator.model = MagicMock()
        translator.model.translate.return_value = ["Hello"]
        
        result = await translator.translate(
            text="नमस्ते",
            target_language="en",
            source_language="hi"
        )
        
        assert result["translated_text"] == "Hello"
        assert result["engine"] == "indic"
    
    async def test_translate_unsupported_language_pair(self, translator):
        """Test translation with unsupported language pair"""
        translator.is_initialized = True
        
        with pytest.raises(Exception):
            await translator.translate(
                text="Hello",
                target_language="xyz",
                source_language="en"
            )
    
    async def test_get_supported_languages(self, translator):
        """Test getting supported Indian languages"""
        languages = await translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "hi" in languages
        assert "bn" in languages
        assert "ta" in languages
    
    async def test_is_supported_language_pair(self, translator):
        """Test language pair support check"""
        # Test supported pair
        assert translator._is_supported_language_pair("en", "hi") is True
        assert translator._is_supported_language_pair("hi", "en") is True
        
        # Test unsupported pair
        assert translator._is_supported_language_pair("en", "xyz") is False
        assert translator._is_supported_language_pair("fr", "de") is False


@pytest.mark.asyncio
class TestLocalTranslator:
    """Test Local Translator"""
    
    @pytest.fixture
    async def translator(self):
        translator = LocalTranslator()
        await translator.initialize()
        return translator
    
    async def test_initialization(self):
        """Test local translator initialization"""
        translator = LocalTranslator()
        result = await translator.initialize()
        
        assert result is True
        assert translator.is_initialized is True
        assert translator.glossary is not None
        assert translator.patterns is not None
    
    async def test_translate_meditation_terms(self, translator):
        """Test translation of meditation-specific terms"""
        result = await translator.translate(
            text="meditation and mindfulness",
            target_language="es",
            source_language="en",
            domain="meditation"
        )
        
        assert result["translated_text"] is not None
        assert result["engine"] == "local"
        assert result["source_language"] == "en"
        assert result["target_language"] == "es"
    
    async def test_translate_with_custom_glossary(self, translator):
        """Test translation using custom glossary"""
        # Add custom term to glossary
        translator.glossary[("en", "es")]["chakra"] = "chakra"
        
        result = await translator.translate(
            text="chakra energy",
            target_language="es",
            source_language="en",
            use_custom_glossary=True
        )
        
        assert "chakra" in result["translated_text"]
        assert result["custom_terms_used"] == ["chakra"]
    
    async def test_translate_same_language(self, translator):
        """Test translation when source and target are the same"""
        result = await translator.translate(
            text="Hello world",
            target_language="en",
            source_language="en"
        )
        
        assert result["translated_text"] == "Hello world"
        assert result["confidence_score"] == 1.0
        assert result["processing_time_ms"] > 0
    
    async def test_detect_language(self, translator):
        """Test language detection using patterns"""
        # Test English detection
        result = await translator.detect_language("Hello world, how are you?")
        assert result["language"] == "en"
        assert result["confidence"] > 0.5
        
        # Test Spanish detection
        result = await translator.detect_language("Hola mundo, como estas?")
        assert result["language"] == "es"
        assert result["confidence"] > 0.5
    
    async def test_translate_batch(self, translator):
        """Test batch translation"""
        texts = ["Hello", "World", "Peace"]
        
        results = await translator.translate_batch(
            texts=texts,
            target_language="es",
            source_language="en"
        )
        
        assert len(results) == 3
        for result in results:
            assert "translated_text" in result
            assert result["engine"] == "local"
    
    async def test_translate_empty_text(self, translator):
        """Test translation of empty text"""
        result = await translator.translate(
            text="",
            target_language="es",
            source_language="en"
        )
        
        assert result["translated_text"] == ""
        assert result["confidence_score"] == 1.0
    
    async def test_translate_long_text(self, translator):
        """Test translation of long text"""
        long_text = " ".join(["meditation"] * 100)
        
        result = await translator.translate(
            text=long_text,
            target_language="es",
            source_language="en"
        )
        
        assert len(result["translated_text"]) > 0
        assert result["processing_time_ms"] > 0
    
    async def test_get_supported_languages(self, translator):
        """Test getting supported languages"""
        languages = await translator.get_supported_languages()
        
        assert isinstance(languages, list)
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert "hi" in languages
    
    async def test_health_check(self, translator):
        """Test health check"""
        health = await translator.health_check()
        
        assert health["status"] == "healthy"
        assert health["engine"] == "local"
        assert "features" in health
        assert "supported_languages" in health
    
    async def test_pattern_based_translation(self, translator):
        """Test pattern-based translation for common phrases"""
        # Test greeting patterns
        result = await translator.translate(
            text="Good morning",
            target_language="es",
            source_language="en"
        )
        
        assert result["translated_text"] is not None
        assert result["confidence_score"] > 0.7
    
    async def test_cultural_adaptation_patterns(self, translator):
        """Test cultural adaptation in local translation"""
        result = await translator.translate(
            text="How are you?",
            target_language="es",
            source_language="en",
            cultural_adaptation=True
        )
        
        assert result["translated_text"] is not None
        if "cultural_notes" in result:
            assert isinstance(result["cultural_notes"], list)
    
    async def test_domain_specific_translation(self, translator):
        """Test domain-specific translation"""
        result = await translator.translate(
            text="breathing exercise",
            target_language="es",
            source_language="en",
            domain="meditation"
        )
        
        assert result["translated_text"] is not None
        assert result["domain"] == "meditation"
    
    async def test_confidence_score_calculation(self, translator):
        """Test confidence score calculation"""
        # High confidence - exact match
        result = await translator.translate(
            text="meditation",
            target_language="es",
            source_language="en"
        )
        
        assert 0.0 <= result["confidence_score"] <= 1.0
        
        # Lower confidence - no exact match
        result = await translator.translate(
            text="abcdefghijklmnop",  # Nonsense word
            target_language="es",
            source_language="en"
        )
        
        assert 0.0 <= result["confidence_score"] <= 1.0
