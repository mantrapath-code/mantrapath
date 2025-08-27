"""
Fixed Coverage Tests for Models Service
Target: 80% overall coverage, 60% minimum per function
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import numpy as np
import tempfile
import shutil
from pathlib import Path
import json
import asyncio
from fastapi.testclient import TestClient

# Import the actual classes
from models.stt_engine import STTEngine
from models.tts_engine import TTSEngine
from models.nlp_engine import NLPEngine
from models.model_manager import ModelManager
from main import app

class TestFixedSTTEngine:
    """Fixed STT Engine tests using correct method names"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """Mock model manager"""
        manager = Mock()
        manager.is_model_available.return_value = True
        manager.get_model_path.return_value = Path("/tmp/test_model")
        manager.update_usage_stats = Mock()
        return manager
    
    @pytest.fixture
    def stt_engine(self, mock_model_manager):
        """STT engine instance"""
        return STTEngine(mock_model_manager)
    
    @pytest.mark.asyncio
    async def test_transcribe_method_exists(self, stt_engine):
        """Test that transcribe method exists and is callable"""
        assert hasattr(stt_engine, 'transcribe')
        assert callable(stt_engine.transcribe)
    
    @pytest.mark.asyncio
    async def test_transcribe_basic_functionality(self, stt_engine):
        """Test basic transcribe functionality"""
        # Mock the _preprocess_audio method
        with patch.object(stt_engine, '_preprocess_audio') as mock_preprocess:
            mock_preprocess.return_value = (np.array([0.1, 0.2, 0.3]), 16000)
            
            # Mock the _select_model method
            with patch.object(stt_engine, '_select_model') as mock_select:
                mock_select.return_value = "whisper_medium"
                
                # Mock the load_model method
                with patch.object(stt_engine, 'load_model') as mock_load:
                    mock_load.return_value = True
                    
                    # Mock the _transcribe_whisper method
                    with patch.object(stt_engine, '_transcribe_whisper') as mock_transcribe:
                        mock_transcribe.return_value = {
                            "success": True,
                            "text": "Hello world",
                            "confidence": 0.95
                        }
                        
                        # Test the actual transcribe method
                        result = await stt_engine.transcribe(
                            audio_data=b"test_audio_data",
                            language="en"
                        )
                        
                        assert result["success"] is True
                        assert "text" in result
                        assert "model_used" in result
    
    @pytest.mark.asyncio
    async def test_transcribe_no_models_available(self, stt_engine):
        """Test transcribe when no models are available"""
        with patch.object(stt_engine, '_select_model') as mock_select:
            mock_select.return_value = None
            
            result = await stt_engine.transcribe(
                audio_data=b"test_audio_data",
                language="invalid_lang"
            )
            
            assert result["success"] is False
            assert "error" in result
            assert "No suitable STT model available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_transcribe_model_load_failure(self, stt_engine):
        """Test transcribe when model loading fails"""
        with patch.object(stt_engine, '_preprocess_audio') as mock_preprocess:
            mock_preprocess.return_value = (np.array([0.1, 0.2, 0.3]), 16000)
            
            with patch.object(stt_engine, '_select_model') as mock_select:
                mock_select.return_value = "whisper_medium"
                
                with patch.object(stt_engine, 'load_model') as mock_load:
                    mock_load.return_value = False
                    
                    result = await stt_engine.transcribe(
                        audio_data=b"test_audio_data",
                        language="en"
                    )
                    
                    assert result["success"] is False
                    assert "Failed to load STT model" in result["error"]
    
    @pytest.mark.asyncio
    async def test_preprocess_audio_method(self, stt_engine):
        """Test _preprocess_audio method"""
        # Test with numpy array
        audio_array = np.array([0.1, 0.2, 0.3])
        result_array, result_sr = await stt_engine._preprocess_audio(audio_array)
        
        assert isinstance(result_array, np.ndarray)
        assert result_sr == 16000
        
        # Test with bytes
        audio_bytes = b"test_audio_bytes"
        with patch('librosa.load') as mock_load:
            mock_load.return_value = (np.array([0.1, 0.2, 0.3]), 22050)
            
            result_array, result_sr = await stt_engine._preprocess_audio(audio_bytes)
            assert result_sr == 16000
    
    @pytest.mark.asyncio
    async def test_select_model_method(self, stt_engine):
        """Test _select_model method"""
        # Test with preference
        model_name = await stt_engine._select_model("en", "whisper_medium")
        assert model_name == "whisper_medium"
        
        # Test without preference
        with patch.object(stt_engine.model_manager, 'is_model_available') as mock_available:
            mock_available.return_value = True
            model_name = await stt_engine._select_model("en", None)
            assert model_name in stt_engine.supported_languages["en"]

class TestFixedTTSEngine:
    """Fixed TTS Engine tests using correct method names"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """Mock model manager"""
        manager = Mock()
        manager.is_model_available.return_value = True
        manager.get_model_path.return_value = Path("/tmp/test_model")
        manager.update_usage_stats = Mock()
        return manager
    
    @pytest.fixture
    def tts_engine(self, mock_model_manager):
        """TTS engine instance"""
        return TTSEngine(mock_model_manager)
    
    @pytest.mark.asyncio
    async def test_synthesize_method_exists(self, tts_engine):
        """Test that synthesize method exists and is callable"""
        assert hasattr(tts_engine, 'synthesize')
        assert callable(tts_engine.synthesize)
    
    @pytest.mark.asyncio
    async def test_synthesize_basic_functionality(self, tts_engine):
        """Test basic synthesize functionality"""
        # Mock the _select_model method
        with patch.object(tts_engine, '_select_model') as mock_select:
            mock_select.return_value = "coqui_xtts_v2"
            
            # Mock the load_model method
            with patch.object(tts_engine, 'load_model') as mock_load:
                mock_load.return_value = True
                
                # Mock the _synthesize_coqui method
                with patch.object(tts_engine, '_synthesize_coqui') as mock_synthesize:
                    mock_synthesize.return_value = {
                        "success": True,
                        "audio_data": np.array([0.1, 0.2, 0.3]),
                        "sample_rate": 22050
                    }
                    
                    # Test the actual synthesize method
                    result = await tts_engine.synthesize(
                        text="Hello world",
                        language="en"
                    )
                    
                    assert result["success"] is True
                    assert "audio_data" in result
                    assert "model_used" in result
    
    @pytest.mark.asyncio
    async def test_synthesize_no_models_available(self, tts_engine):
        """Test synthesize when no models are available"""
        with patch.object(tts_engine, '_select_model') as mock_select:
            mock_select.return_value = None
            
            result = await tts_engine.synthesize(
                text="Hello world",
                language="invalid_lang"
            )
            
            assert result["success"] is False
            assert "No suitable TTS model available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_synthesize_model_load_failure(self, tts_engine):
        """Test synthesize when model loading fails"""
        with patch.object(tts_engine, '_select_model') as mock_select:
            mock_select.return_value = "coqui_xtts_v2"
            
            with patch.object(tts_engine, 'load_model') as mock_load:
                mock_load.return_value = False
                
                result = await tts_engine.synthesize(
                    text="Hello world",
                    language="en"
                )
                
                assert result["success"] is False
                assert "Failed to load TTS model" in result["error"]
    
    @pytest.mark.asyncio
    async def test_select_model_method(self, tts_engine):
        """Test _select_model method"""
        # Test with preference
        model_name = await tts_engine._select_model("en", "coqui_xtts_v2")
        assert model_name == "coqui_xtts_v2"
        
        # Test without preference
        with patch.object(tts_engine.model_manager, 'is_model_available') as mock_available:
            mock_available.return_value = True
            model_name = await tts_engine._select_model("en", None)
            assert model_name in tts_engine.supported_languages["en"]

class TestFixedNLPEngine:
    """Fixed NLP Engine tests"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """Mock model manager"""
        manager = Mock()
        manager.is_model_available.return_value = True
        manager.get_model_path.return_value = Path("/tmp/test_model")
        manager.update_usage_stats = Mock()
        return manager
    
    @pytest.fixture
    def nlp_engine(self, mock_model_manager):
        """NLP engine instance"""
        return NLPEngine(mock_model_manager)
    
    @pytest.mark.asyncio
    async def test_translate_method_exists(self, nlp_engine):
        """Test that translate method exists"""
        assert hasattr(nlp_engine, 'translate')
        assert callable(nlp_engine.translate)
    
    @pytest.mark.asyncio
    async def test_translate_basic_functionality(self, nlp_engine):
        """Test basic translate functionality"""
        # Mock the _select_model method
        with patch.object(nlp_engine, '_select_model') as mock_select:
            mock_select.return_value = "bert_multilingual"
            
            # Mock the load_model method
            with patch.object(nlp_engine, 'load_model') as mock_load:
                mock_load.return_value = True
                
                # Mock the _translate_with_model method
                with patch.object(nlp_engine, '_translate_with_model') as mock_translate:
                    mock_translate.return_value = {
                        "success": True,
                        "translated_text": "नमस्ते दुनिया",
                        "confidence": 0.92
                    }
                    
                    result = await nlp_engine.translate(
                        text="Hello world",
                        source_lang="en",
                        target_lang="hi"
                    )
                    
                    assert result["success"] is True
                    assert "translated_text" in result
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_method_exists(self, nlp_engine):
        """Test that analyze_sentiment method exists"""
        assert hasattr(nlp_engine, 'analyze_sentiment')
        assert callable(nlp_engine.analyze_sentiment)
    
    @pytest.mark.asyncio
    async def test_get_embeddings_method_exists(self, nlp_engine):
        """Test that get_embeddings method exists"""
        assert hasattr(nlp_engine, 'get_embeddings')
        assert callable(nlp_engine.get_embeddings)

class TestFixedModelManager:
    """Fixed Model Manager tests"""
    
    @pytest.fixture
    def temp_models_dir(self):
        """Create temporary models directory"""
        temp_dir = tempfile.mkdtemp()
        models_dir = Path(temp_dir) / "models"
        models_dir.mkdir(parents=True, exist_ok=True)
        yield models_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def model_manager(self, temp_models_dir):
        """Model manager instance"""
        return ModelManager(temp_models_dir)
    
    @pytest.mark.asyncio
    async def test_initialize_method(self, model_manager):
        """Test initialize method"""
        # Mock the _load_model_configs method
        with patch.object(model_manager, '_load_model_configs') as mock_load_configs:
            with patch.object(model_manager, '_scan_existing_models') as mock_scan:
                with patch.object(model_manager, '_load_usage_stats') as mock_load_stats:
                    await model_manager.initialize()
                    
                    mock_load_configs.assert_called_once()
                    mock_scan.assert_called_once()
                    mock_load_stats.assert_called_once()
    
    def test_is_model_available_method(self, model_manager):
        """Test is_model_available method"""
        # Test with available model
        model_manager.available_models["test_model"] = {"path": Path("/tmp/test")}
        assert model_manager.is_model_available("test_model") is True
        
        # Test with unavailable model
        assert model_manager.is_model_available("nonexistent_model") is False
    
    def test_get_model_path_method(self, model_manager):
        """Test get_model_path method"""
        # Test with available model
        model_path = Path("/tmp/test")
        model_manager.available_models["test_model"] = {"path": model_path}
        
        result = model_manager.get_model_path("test_model")
        assert result == model_path
        
        # Test with unavailable model
        result = model_manager.get_model_path("nonexistent_model")
        assert result is None

class TestFixedAPIRoutes:
    """Fixed API Routes tests"""
    
    @pytest.fixture
    def test_client(self):
        """Test client"""
        return TestClient(app)
    
    def test_health_endpoint(self, test_client):
        """Test health endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "models_service"
    
    def test_status_endpoint(self, test_client):
        """Test status endpoint"""
        response = test_client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "models_service"
        assert data["status"] == "running"
        assert "hardware" in data
        assert "models" in data
    
    def test_models_available_endpoint(self, test_client):
        """Test models available endpoint"""
        # Mock the model_manager global
        with patch('main.model_manager') as mock_manager:
            mock_manager.get_available_models = AsyncMock()
            mock_manager.get_available_models.return_value = {
                "whisper_medium": {"type": "stt", "languages": ["en", "hi"]}
            }
            
            response = test_client.get("/models/available")
            assert response.status_code == 200
    
    def test_models_loaded_endpoint(self, test_client):
        """Test models loaded endpoint"""
        response = test_client.get("/models/loaded")
        assert response.status_code == 200
        
        data = response.json()
        assert "stt" in data
        assert "tts" in data
        assert "nlp" in data

class TestFixedMainApp:
    """Fixed Main App tests"""
    
    @pytest.fixture
    def test_client(self):
        """Test client"""
        return TestClient(app)
    
    def test_startup_event_success(self):
        """Test startup event success"""
        # Mock the global components
        with patch('main.ModelManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.initialize = AsyncMock()
            mock_manager_class.return_value = mock_manager
            
            with patch('main.STTEngine') as mock_stt_class:
                mock_stt = Mock()
                mock_stt.load_default_models = AsyncMock()
                mock_stt_class.return_value = mock_stt
                
                with patch('main.TTSEngine') as mock_tts_class:
                    mock_tts = Mock()
                    mock_tts.load_default_models = AsyncMock()
                    mock_tts_class.return_value = mock_tts
                    
                    with patch('main.NLPEngine') as mock_nlp_class:
                        mock_nlp = Mock()
                        mock_nlp.load_default_models = AsyncMock()
                        mock_nlp_class.return_value = mock_nlp
                        
                        # Test startup event
                        from main import startup_event
                        asyncio.run(startup_event())
                        
                        mock_manager.initialize.assert_called_once()
                        mock_stt.load_default_models.assert_called_once()
                        mock_tts.load_default_models.assert_called_once()
                        mock_nlp.load_default_models.assert_called_once()
    
    def test_shutdown_event(self):
        """Test shutdown event"""
        # Mock the global model_manager
        with patch('main.model_manager') as mock_manager:
            mock_manager.cleanup = AsyncMock()
            
            # Test shutdown event
            from main import shutdown_event
            asyncio.run(shutdown_event())
            
            mock_manager.cleanup.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=.", "--cov-report=term-missing"])
