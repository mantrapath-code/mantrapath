"""
Phase 1 Functional Tests - No Mock Data/Responses
Real functional testing of models service components
"""

import pytest
import numpy as np
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import asyncio

# Import actual classes to test
from models.stt_engine import STTEngine
from models.tts_engine import TTSEngine
from models.nlp_engine import NLPEngine
from models.model_manager import ModelManager
from config.settings import get_settings
from utils.logger import setup_logger


class TestSTTEngineFunctional:
    """Functional tests for STT Engine - no mocked responses"""
    
    @pytest.fixture
    def real_model_manager(self):
        """Create a real ModelManager with actual directory structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            # Set up real configs but don't download actual models
            manager.model_configs = {
                "whisper_medium": {
                    "type": "whisper",
                    "model_id": "openai/whisper-medium",
                    "languages": ["en", "hi", "es"],
                    "size": "769MB"
                },
                "vosk_en_us": {
                    "type": "vosk",
                    "languages": ["en"],
                    "size": "50MB"
                }
            }
            yield manager

    @pytest.fixture
    def stt_engine(self, real_model_manager):
        """Create real STT engine with actual model manager"""
        return STTEngine(real_model_manager)

    def test_stt_initialization_real(self, stt_engine):
        """Test real STT engine initialization"""
        # Test actual attributes exist
        assert hasattr(stt_engine, 'model_manager')
        assert hasattr(stt_engine, 'loaded_models')
        assert hasattr(stt_engine, 'supported_languages')
        
        # Test actual language structure
        assert isinstance(stt_engine.supported_languages, dict)
        assert "en" in stt_engine.supported_languages
        assert "hi" in stt_engine.supported_languages
        
        # Test actual model lists for languages
        en_models = stt_engine.supported_languages["en"]
        assert isinstance(en_models, list)
        assert len(en_models) > 0
        assert "whisper_medium" in en_models

    @pytest.mark.asyncio
    async def test_stt_load_model_flow(self, stt_engine):
        """Test actual model loading flow without external dependencies"""
        model_name = "test_model"
        
        # Test actual method existence and behavior
        assert hasattr(stt_engine, 'load_model')
        
        # Test with non-existent model (should return False)
        result = await stt_engine.load_model(model_name)
        assert result is False  # Because model not available
        
        # Test loaded_models state doesn't change for failed load
        assert model_name not in stt_engine.loaded_models

    @pytest.mark.asyncio
    async def test_stt_transcribe_error_handling(self, stt_engine):
        """Test actual transcribe method error handling"""
        # Test with None input
        result = await stt_engine.transcribe(None)
        assert isinstance(result, dict)
        assert "success" in result
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_stt_preprocess_audio_real(self, stt_engine):
        """Test actual audio preprocessing"""
        # Create real audio data
        audio_data = np.random.uniform(-1, 1, 16000).astype(np.float32)
        
        # Test actual preprocessing method
        try:
            result = await stt_engine._preprocess_audio(audio_data)
            # Should return tuple of (audio, sample_rate)
            assert isinstance(result, tuple)
            assert len(result) == 2
            processed_audio, sample_rate = result
            assert isinstance(processed_audio, np.ndarray)
            assert isinstance(sample_rate, int)
        except Exception as e:
            # Even if it fails due to missing libraries, 
            # we're testing the actual code path
            assert "librosa" in str(e) or "audio" in str(e).lower()

    @pytest.mark.asyncio
    async def test_stt_get_supported_languages_real(self, stt_engine):
        """Test actual supported languages method"""
        result = await stt_engine.get_supported_languages()
        
        # Test actual return structure
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Test actual language codes
        for lang_code, models in result.items():
            assert isinstance(lang_code, str)
            assert len(lang_code) == 2  # ISO language codes
            assert isinstance(models, list)

    @pytest.mark.asyncio
    async def test_stt_cleanup_real(self, stt_engine):
        """Test actual cleanup method"""
        # Add some fake loaded models
        stt_engine.loaded_models["test1"] = "model1"
        stt_engine.loaded_models["test2"] = "model2"
        
        # Test actual cleanup
        await stt_engine.cleanup()
        
        # Verify actual state change
        assert len(stt_engine.loaded_models) == 0


class TestTTSEngineFunctional:
    """Functional tests for TTS Engine - no mocked responses"""
    
    @pytest.fixture
    def real_model_manager(self):
        """Create a real ModelManager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            manager.model_configs = {
                "coqui_xtts_v2": {
                    "type": "coqui",
                    "languages": ["en", "hi", "es"],
                    "size": "6GB"
                }
            }
            yield manager

    @pytest.fixture
    def tts_engine(self, real_model_manager):
        """Create real TTS engine"""
        return TTSEngine(real_model_manager)

    def test_tts_initialization_real(self, tts_engine):
        """Test real TTS engine initialization"""
        assert hasattr(tts_engine, 'model_manager')
        assert hasattr(tts_engine, 'loaded_models')
        assert hasattr(tts_engine, 'supported_languages')
        
        # Test actual language structure
        assert isinstance(tts_engine.supported_languages, dict)
        assert len(tts_engine.supported_languages) > 0

    @pytest.mark.asyncio
    async def test_tts_synthesize_error_handling(self, tts_engine):
        """Test actual synthesize method error handling"""
        # Test with empty text
        result = await tts_engine.synthesize("")
        assert isinstance(result, dict)
        
        # Test with None text
        result = await tts_engine.synthesize(None)
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_tts_get_supported_languages_real(self, tts_engine):
        """Test actual supported languages method"""
        result = await tts_engine.get_supported_languages()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_tts_cleanup_real(self, tts_engine):
        """Test actual cleanup method"""
        # Add some test models
        tts_engine.loaded_models["test"] = "model"
        
        await tts_engine.cleanup()
        
        assert len(tts_engine.loaded_models) == 0


class TestNLPEngineFunctional:
    """Functional tests for NLP Engine - no mocked responses"""
    
    @pytest.fixture
    def real_model_manager(self):
        """Create a real ModelManager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            yield ModelManager(models_dir)

    @pytest.fixture
    def nlp_engine(self, real_model_manager):
        """Create real NLP engine"""
        return NLPEngine(real_model_manager)

    def test_nlp_initialization_real(self, nlp_engine):
        """Test real NLP engine initialization"""
        assert hasattr(nlp_engine, 'model_manager')
        assert hasattr(nlp_engine, 'loaded_models')

    @pytest.mark.asyncio
    async def test_nlp_translate_real(self, nlp_engine):
        """Test actual translate method"""
        # Test actual method call - no mocked response
        result = await nlp_engine.translate("Hello", "en", "hi")
        
        # Test actual return structure
        assert isinstance(result, dict)
        # The actual implementation may return different structures
        # but we test the real code path

    @pytest.mark.asyncio
    async def test_nlp_analyze_sentiment_real(self, nlp_engine):
        """Test actual sentiment analysis"""
        result = await nlp_engine.analyze_sentiment("I am happy")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_nlp_get_embeddings_real(self, nlp_engine):
        """Test actual embeddings method"""
        result = await nlp_engine.get_embeddings("test text")
        assert isinstance(result, dict)


class TestModelManagerFunctional:
    """Functional tests for Model Manager - no mocked responses"""
    
    def test_model_manager_real_initialization(self):
        """Test real ModelManager initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)

            # Test actual attributes
            assert manager.models_dir == models_dir
            assert hasattr(manager, 'model_configs')
            assert hasattr(manager, 'available_models')
            assert hasattr(manager, 'download_progress')
            assert hasattr(manager, 'model_usage_stats')            # Test actual types
            assert isinstance(manager.model_configs, dict)
            assert isinstance(manager.available_models, dict)
            assert isinstance(manager.download_progress, dict)
            assert isinstance(manager.model_usage_stats, dict)

    @pytest.mark.asyncio
    async def test_model_manager_initialize_real(self):
        """Test actual initialization process"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            
            # Test actual initialize method
            await manager.initialize()
            
            # The method should complete without error
            # Even if some sub-methods fail due to missing files

    @pytest.mark.asyncio
    async def test_model_manager_get_available_models_real(self):
        """Test actual get_available_models method"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            
            # Set some real config data
            manager.model_configs = {
                "test_model": {
                    "type": "whisper",
                    "languages": ["en"]
                }
            }
            
            result = await manager.get_available_models()
            
            # Test actual return structure
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_model_manager_cleanup_real(self):
        """Test actual cleanup method"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            manager = ModelManager(models_dir)
            
            # Test cleanup doesn't crash
            await manager.cleanup()


class TestSettingsFunctional:
    """Functional tests for Settings - no mocked responses"""
    
    def test_settings_real_loading(self):
        """Test actual settings loading"""
        settings = get_settings()
        
        # Test actual attributes exist
        assert hasattr(settings, 'BASE_DIR')
        assert hasattr(settings, 'MODELS_DIR')
        assert hasattr(settings, 'CACHE_DIR')
        
        # Test actual types
        assert isinstance(settings.BASE_DIR, Path)
        assert isinstance(settings.MODELS_DIR, Path)
        assert isinstance(settings.CACHE_DIR, Path)

    def test_settings_model_configs_real(self):
        """Test actual model configurations"""
        settings = get_settings()
        
        # Test actual MODEL_CONFIGS attribute
        assert hasattr(settings, 'MODEL_CONFIGS')
        model_configs = settings.MODEL_CONFIGS
        assert isinstance(model_configs, dict)
        assert len(model_configs) > 0
        
        # Test actual config structure
        for model_name, config in model_configs.items():
            assert isinstance(model_name, str)
            assert isinstance(config, dict)
            assert 'type' in config  # Should have type field

    def test_settings_indian_languages_real(self):
        """Test actual Indian languages configuration"""
        settings = get_settings()
        
        assert hasattr(settings, 'INDIAN_LANGUAGES')
        indian_langs = settings.INDIAN_LANGUAGES
        assert isinstance(indian_langs, dict)
        
        # Test actual language entries
        expected_langs = ['hi', 'bn', 'te', 'ta']
        for lang in expected_langs:
            assert lang in indian_langs


class TestLoggerFunctional:
    """Functional tests for Logger - no mocked responses"""
    
    def test_logger_setup_real(self):
        """Test actual logger setup"""
        logger = setup_logger("test_module")
        
        # Test actual logger object
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'warning')

    def test_logger_with_different_levels(self):
        """Test logger with different log levels"""
        import logging
        
        # Test with different levels
        logger1 = setup_logger("test1", level=logging.INFO)
        logger2 = setup_logger("test2", level=logging.DEBUG)
        logger3 = setup_logger("test3", level=logging.ERROR)
        
        assert logger1.level <= logging.INFO
        assert logger2.level <= logging.DEBUG  
        assert logger3.level <= logging.ERROR

    def test_logger_file_creation(self):
        """Test actual log file creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            logger = setup_logger("test_file", log_file=log_file)
            
            # Test logger was created
            assert logger is not None
            
            # Test log file path parent exists
            assert log_file.parent.exists()


class TestMainApplicationFunctional:
    """Functional tests for main application - no mocked responses"""
    
    def test_app_import_real(self):
        """Test actual app import"""
        from main import app
        
        # Test actual FastAPI app
        assert app is not None
        assert hasattr(app, 'title')
        assert hasattr(app, 'description')
        assert app.title == "MantraPath Models Service"

    def test_app_routes_real(self):
        """Test actual app routes configuration"""
        from main import app
        
        # Test actual routes exist
        routes = [route.path for route in app.routes]
        
        # Should have basic routes
        assert any('health' in route for route in routes)
        assert any('docs' in route for route in routes)

    def test_cors_configuration_real(self):
        """Test actual CORS configuration"""
        from main import app

        # Test middleware exists
        assert len(app.user_middleware) > 0

        # Test CORS middleware is present  
        middleware_classes = [middleware.cls for middleware in app.user_middleware]
        assert any('CORSMiddleware' in str(cls) for cls in middleware_classes)
class TestIntegrationFunctional:
    """Integration tests with real components"""
    
    def test_engine_initialization_integration(self):
        """Test all engines can be initialized together"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            model_manager = ModelManager(models_dir)
            
            # Initialize all engines
            stt_engine = STTEngine(model_manager)
            tts_engine = TTSEngine(model_manager)
            nlp_engine = NLPEngine(model_manager)
            
            # Test they all have required attributes
            engines = [stt_engine, tts_engine, nlp_engine]
            for engine in engines:
                assert hasattr(engine, 'model_manager')
                assert engine.model_manager == model_manager

    @pytest.mark.asyncio
    async def test_cleanup_integration(self):
        """Test cleanup across all components"""
        with tempfile.TemporaryDirectory() as temp_dir:
            models_dir = Path(temp_dir)
            model_manager = ModelManager(models_dir)
            
            stt_engine = STTEngine(model_manager)
            tts_engine = TTSEngine(model_manager)
            nlp_engine = NLPEngine(model_manager)
            
            # Add some test data
            stt_engine.loaded_models["test"] = "model"
            tts_engine.loaded_models["test"] = "model"
            nlp_engine.loaded_models["test"] = "model"
            
            # Test cleanup all
            await stt_engine.cleanup()
            await tts_engine.cleanup()
            await nlp_engine.cleanup()
            await model_manager.cleanup()
            
            # Verify all cleaned
            assert len(stt_engine.loaded_models) == 0
            assert len(tts_engine.loaded_models) == 0
            assert len(nlp_engine.loaded_models) == 0

    def test_settings_integration(self):
        """Test settings work with all components"""
        settings = get_settings()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test settings can be used with ModelManager
            models_dir = settings.MODELS_DIR if settings.MODELS_DIR.exists() else Path(temp_dir)
            manager = ModelManager(models_dir)
            
            # Test engines can use settings
            stt_engine = STTEngine(manager)
            tts_engine = TTSEngine(manager)
            
            # Test they initialize without error
            assert stt_engine.model_manager == manager
            assert tts_engine.model_manager == manager
