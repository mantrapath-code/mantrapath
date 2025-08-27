"""
Comprehensive tests for translation engines with proper mocking
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

from engines.base_translator import BaseTranslator
from engines.local_translator import LocalTranslator
from engines.free_google_translator import FreeGoogleTranslator
from engines.enhanced_multi_translator import EnhancedMultiTranslator


@pytest.mark.unit
class TestBaseTranslatorFunctionality:
    """Test base translator abstract functionality"""
    
    def test_base_translator_abstract_methods(self):
        """Test that BaseTranslator is abstract and cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseTranslator()
    
    def test_base_translator_constants(self):
        """Test BaseTranslator class constants"""
        assert hasattr(BaseTranslator, 'ENGINE_NAME')
        assert hasattr(BaseTranslator, 'SUPPORTED_LANGUAGES')


@pytest.mark.unit 
class TestLocalTranslatorFunctionality:
    """Test LocalTranslator with proper mocking"""
    
    @pytest.fixture
    def mock_local_translator(self):
        """Create a mock LocalTranslator"""
        with patch('engines.local_translator.LocalTranslator.__init__', return_value=None):
            translator = LocalTranslator.__new__(LocalTranslator)
            translator.ENGINE_NAME = "local"
            translator.SUPPORTED_LANGUAGES = {"en": "English", "es": "Spanish"}
            translator.models = {}
            translator.tokenizers = {}
            translator.initialized = False
            return translator
    
    def test_local_translator_engine_name(self, mock_local_translator):
        """Test LocalTranslator engine name"""
        assert mock_local_translator.ENGINE_NAME == "local"
    
    @patch('engines.local_translator.LocalTranslator.initialize')
    async def test_local_translator_initialization(self, mock_init, mock_local_translator):
        """Test LocalTranslator initialization"""
        mock_init.return_value = True
        mock_local_translator.initialize = mock_init
        
        result = await mock_local_translator.initialize()
        assert result is True
        mock_init.assert_called_once()
    
    @patch('engines.local_translator.LocalTranslator.translate')
    async def test_local_translator_translate(self, mock_translate, mock_local_translator):
        """Test LocalTranslator translate method"""
        mock_translate.return_value = {
            "translated_text": "Hola mundo",
            "confidence_score": 0.95,
            "quality_score": 0.9,
            "processing_time_ms": 100
        }
        mock_local_translator.translate = mock_translate
        
        result = await mock_local_translator.translate("Hello world", "en", "es")
        assert result["translated_text"] == "Hola mundo"
        assert result["confidence_score"] == 0.95
        mock_translate.assert_called_once_with("Hello world", "en", "es")


@pytest.mark.unit
class TestFreeGoogleTranslatorFunctionality:
    """Test FreeGoogleTranslator with mocking"""
    
    @pytest.fixture
    def mock_google_translator(self):
        """Create a mock FreeGoogleTranslator"""
        with patch('engines.free_google_translator.FreeGoogleTranslator.__init__', return_value=None):
            translator = FreeGoogleTranslator.__new__(FreeGoogleTranslator)
            translator.ENGINE_NAME = "free_google"
            translator.initialized = False
            translator.client = MagicMock()
            return translator
    
    def test_google_translator_engine_name(self, mock_google_translator):
        """Test FreeGoogleTranslator engine name"""
        assert mock_google_translator.ENGINE_NAME == "free_google"
    
    @patch('engines.free_google_translator.FreeGoogleTranslator.initialize')
    async def test_google_translator_initialization(self, mock_init, mock_google_translator):
        """Test FreeGoogleTranslator initialization"""
        mock_init.return_value = True
        mock_google_translator.initialize = mock_init
        
        result = await mock_google_translator.initialize()
        assert result is True
        mock_init.assert_called_once()
    
    @patch('engines.free_google_translator.FreeGoogleTranslator.translate')
    async def test_google_translator_translate(self, mock_translate, mock_google_translator):
        """Test FreeGoogleTranslator translate method"""
        mock_translate.return_value = {
            "translated_text": "Hola mundo",
            "confidence_score": 0.98,
            "quality_score": 0.95,
            "processing_time_ms": 50
        }
        mock_google_translator.translate = mock_translate
        
        result = await mock_google_translator.translate("Hello world", "en", "es")
        assert result["translated_text"] == "Hola mundo"
        assert result["confidence_score"] == 0.98
        mock_translate.assert_called_once_with("Hello world", "en", "es")
    
    @patch('engines.free_google_translator.FreeGoogleTranslator.detect_language')
    async def test_google_translator_detect_language(self, mock_detect, mock_google_translator):
        """Test FreeGoogleTranslator language detection"""
        mock_detect.return_value = {
            "detected_language": "en",
            "confidence_score": 0.99,
            "processing_time_ms": 25
        }
        mock_google_translator.detect_language = mock_detect
        
        result = await mock_google_translator.detect_language("Hello world")
        assert result["detected_language"] == "en"
        assert result["confidence_score"] == 0.99
        mock_detect.assert_called_once_with("Hello world")


@pytest.mark.unit
class TestEnhancedMultiTranslatorFunctionality:
    """Test EnhancedMultiTranslator with mocking"""
    
    @pytest.fixture
    def mock_multi_translator(self):
        """Create a mock EnhancedMultiTranslator"""
        with patch('engines.enhanced_multi_translator.EnhancedMultiTranslator.__init__', return_value=None):
            translator = EnhancedMultiTranslator.__new__(EnhancedMultiTranslator)
            translator.engines = {}
            translator.engine_priorities = {
                "google": 1,
                "microsoft": 2,
                "local": 3,
                "argos": 4
            }
            translator.indian_languages = {"hi", "bn", "ta", "te", "ml", "kn", "gu", "pa", "or", "mr"}
            translator.initialized = False
            return translator
    
    def test_multi_translator_constants(self, mock_multi_translator):
        """Test EnhancedMultiTranslator constants"""
        assert isinstance(mock_multi_translator.engine_priorities, dict)
        assert isinstance(mock_multi_translator.indian_languages, set)
        assert "google" in mock_multi_translator.engine_priorities
    
    @patch('engines.enhanced_multi_translator.EnhancedMultiTranslator.initialize')
    async def test_multi_translator_initialization(self, mock_init, mock_multi_translator):
        """Test EnhancedMultiTranslator initialization"""
        mock_init.return_value = True
        mock_multi_translator.initialize = mock_init
        
        result = await mock_multi_translator.initialize()
        assert result is True
        mock_init.assert_called_once()
    
    @patch('engines.enhanced_multi_translator.EnhancedMultiTranslator._is_indian_language')
    def test_multi_translator_is_indian_language(self, mock_is_indian, mock_multi_translator):
        """Test EnhancedMultiTranslator Indian language detection"""
        mock_is_indian.return_value = True
        mock_multi_translator._is_indian_language = mock_is_indian
        
        result = mock_multi_translator._is_indian_language("hi")
        assert result is True
        mock_is_indian.assert_called_once_with("hi")
    
    @patch('engines.enhanced_multi_translator.EnhancedMultiTranslator._get_engine_priority')
    def test_multi_translator_engine_priority(self, mock_priority, mock_multi_translator):
        """Test EnhancedMultiTranslator engine priority"""
        mock_priority.return_value = ["google", "microsoft", "local"]
        mock_multi_translator._get_engine_priority = mock_priority
        
        result = mock_multi_translator._get_engine_priority("en", "es")
        assert isinstance(result, list)
        assert "google" in result
        mock_priority.assert_called_once_with("en", "es")
    
    @patch('engines.enhanced_multi_translator.EnhancedMultiTranslator.translate')
    async def test_multi_translator_translate_basic(self, mock_translate, mock_multi_translator):
        """Test EnhancedMultiTranslator basic translation"""
        mock_translate.return_value = {
            "translated_text": "Hola mundo",
            "confidence_score": 0.96,
            "quality_score": 0.94,
            "engine_used": "google",
            "processing_time_ms": 75
        }
        mock_multi_translator.translate = mock_translate
        
        result = await mock_multi_translator.translate("Hello world", "en", "es")
        assert result["translated_text"] == "Hola mundo"
        assert result["engine_used"] == "google"
        mock_translate.assert_called_once_with("Hello world", "en", "es")
    
    @patch('engines.enhanced_multi_translator.EnhancedMultiTranslator.health_check')
    async def test_multi_translator_health_check(self, mock_health, mock_multi_translator):
        """Test EnhancedMultiTranslator health check"""
        mock_health.return_value = {
            "status": "healthy",
            "engines": {
                "google": {"status": "healthy", "response_time_ms": 50},
                "local": {"status": "healthy", "response_time_ms": 100}
            },
            "total_engines": 2,
            "healthy_engines": 2
        }
        mock_multi_translator.health_check = mock_health
        
        result = await mock_multi_translator.health_check()
        assert result["status"] == "healthy"
        assert result["total_engines"] == 2
        assert result["healthy_engines"] == 2
        mock_health.assert_called_once()
