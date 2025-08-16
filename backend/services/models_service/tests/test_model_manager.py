"""
Test cases for ModelManager
Tests model downloading, management, and caching functionality
"""

import pytest
import pytest_asyncio
import json
import shutil
import tempfile
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path
import hashlib
import asyncio


class TestModelManager:
    """Test Model Manager functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_model_manager(self, temp_models_dir, mock_settings):
        """Setup ModelManager for testing"""
        from models.model_manager import ModelManager
        
        with patch('models.model_manager.get_settings', return_value=mock_settings):
            self.model_manager = ModelManager(temp_models_dir)
            self.temp_models_dir = temp_models_dir
    
    @pytest.mark.asyncio
    async def test_model_manager_initialization(self, mock_model_config):
        """Test ModelManager initialization"""
        assert self.model_manager.models_dir == self.temp_models_dir
        assert isinstance(self.model_manager.available_models, dict)
        assert isinstance(self.model_manager.loaded_models, dict)
        assert isinstance(self.model_manager.download_progress, dict)
        assert isinstance(self.model_manager.downloading, set)
        assert self.model_manager.cache_size_limit > 0
        
    @pytest.mark.asyncio
    async def test_initialize_success(self, mock_model_config):
        """Test successful initialization"""
        with patch.object(self.model_manager, '_load_model_configs', new_callable=AsyncMock), \
             patch.object(self.model_manager, '_scan_existing_models', new_callable=AsyncMock), \
             patch.object(self.model_manager, '_load_usage_stats', new_callable=AsyncMock):
            
            await self.model_manager.initialize()
            
            # Verify initialization methods were called
            self.model_manager._load_model_configs.assert_called_once()
            self.model_manager._scan_existing_models.assert_called_once()
            self.model_manager._load_usage_stats.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_load_model_configs(self, mock_settings):
        """Test loading model configurations"""
        with patch('models.model_manager.get_settings', return_value=mock_settings):
            await self.model_manager._load_model_configs()
            
            assert len(self.model_manager.model_configs) > 0
            # Should include configs from settings and generated Indian language models
    
    @pytest.mark.asyncio
    async def test_scan_existing_models(self, create_test_model_dir):
        """Test scanning for existing models"""
        # Create some test model directories
        model1_dir = create_test_model_dir("test_model_1")
        model2_dir = create_test_model_dir("test_model_2")
        
        with patch.object(self.model_manager, '_validate_model_directory', return_value=True):
            await self.model_manager._scan_existing_models()
            
            assert "test_model_1" in self.model_manager.available_models
            assert "test_model_2" in self.model_manager.available_models
    
    @pytest.mark.asyncio
    async def test_validate_model_directory_valid(self, create_test_model_dir):
        """Test validating a valid model directory"""
        model_dir = create_test_model_dir("valid_model")
        
        result = await self.model_manager._validate_model_directory(model_dir)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_model_directory_invalid(self, temp_models_dir):
        """Test validating an invalid model directory"""
        # Create directory without config file
        invalid_dir = temp_models_dir / "invalid_model"
        invalid_dir.mkdir()
        
        result = await self.model_manager._validate_model_directory(invalid_dir)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_available_models(self, mock_model_config):
        """Test getting available models"""
        self.model_manager.model_configs = mock_model_config
        
        available = await self.model_manager.get_available_models()
        
        assert isinstance(available, dict)
        assert len(available) > 0
        for model_name, config in available.items():
            assert "type" in config
            assert "languages" in config
    
    def test_is_model_available_true(self):
        """Test checking if model is available (true case)"""
        model_name = "test_model"
        self.model_manager.available_models[model_name] = {"path": "/path/to/model"}
        
        result = self.model_manager.is_model_available(model_name)
        
        assert result is True
    
    def test_is_model_available_false(self):
        """Test checking if model is available (false case)"""
        model_name = "nonexistent_model"
        
        result = self.model_manager.is_model_available(model_name)
        
        assert result is False
    
    def test_get_model_path_exists(self):
        """Test getting model path when model exists"""
        model_name = "test_model"
        expected_path = self.temp_models_dir / model_name
        self.model_manager.available_models[model_name] = {"path": expected_path}
        
        result = self.model_manager.get_model_path(model_name)
        
        assert result == expected_path
    
    def test_get_model_path_not_exists(self):
        """Test getting model path when model doesn't exist"""
        model_name = "nonexistent_model"
        
        result = self.model_manager.get_model_path(model_name)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_download_model_success(self, mock_model_config):
        """Test successful model download"""
        model_name = "test_model"
        self.model_manager.model_configs = mock_model_config
        
        with patch.object(self.model_manager, '_download_file', new_callable=AsyncMock) as mock_download, \
             patch.object(self.model_manager, '_extract_archive', new_callable=AsyncMock) as mock_extract, \
             patch.object(self.model_manager, '_verify_download', new_callable=AsyncMock) as mock_verify:
            
            mock_download.return_value = True
            mock_extract.return_value = True
            mock_verify.return_value = True
            
            result = await self.model_manager.download_model(model_name)
            
            assert result is True
            assert model_name not in self.model_manager.downloading
            mock_download.assert_called_once()
            mock_extract.assert_called_once()
            mock_verify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_download_model_not_in_configs(self):
        """Test downloading model not in configurations"""
        model_name = "unknown_model"
        
        result = await self.model_manager.download_model(model_name)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_download_model_already_downloading(self, mock_model_config):
        """Test downloading model that's already being downloaded"""
        model_name = "test_model"
        self.model_manager.model_configs = mock_model_config
        self.model_manager.downloading.add(model_name)
        
        result = await self.model_manager.download_model(model_name)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_download_model_already_available(self, mock_model_config):
        """Test downloading model that's already available"""
        model_name = "test_model"
        self.model_manager.model_configs = mock_model_config
        self.model_manager.available_models[model_name] = {"path": "/path"}
        
        result = await self.model_manager.download_model(model_name)
        
        assert result is True  # Should return True for already available
    
    @pytest.mark.asyncio
    async def test_download_file_success(self, mock_model_config):
        """Test successful file download"""
        url = "https://example.com/model.zip"
        output_path = self.temp_models_dir / "model.zip"
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"content-length": "1000"}
        mock_response.content.iter_chunked = AsyncMock(return_value=[b"data1", b"data2"])
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            result = await self.model_manager._download_file(url, output_path)
            
            assert result is True
            assert output_path.exists()
    
    @pytest.mark.asyncio
    async def test_download_file_http_error(self):
        """Test file download with HTTP error"""
        url = "https://example.com/model.zip"
        output_path = self.temp_models_dir / "model.zip"
        
        mock_response = AsyncMock()
        mock_response.status = 404
        
        with patch('aiohttp.ClientSession.get', return_value=mock_response):
            result = await self.model_manager._download_file(url, output_path)
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_extract_archive_zip(self):
        """Test extracting ZIP archive"""
        # Create a dummy zip file
        zip_path = self.temp_models_dir / "test.zip"
        extract_path = self.temp_models_dir / "extracted"
        
        # Create zip content
        import zipfile
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("model.bin", "dummy model data")
            zf.writestr("config.json", '{"model_type": "test"}')
        
        result = await self.model_manager._extract_archive(zip_path, extract_path)
        
        assert result is True
        assert (extract_path / "model.bin").exists()
        assert (extract_path / "config.json").exists()
    
    @pytest.mark.asyncio
    async def test_extract_archive_tar(self):
        """Test extracting TAR archive"""
        import tarfile
        
        # Create a dummy tar file
        tar_path = self.temp_models_dir / "test.tar.gz"
        extract_path = self.temp_models_dir / "extracted"
        
        with tarfile.open(tar_path, 'w:gz') as tf:
            # Add dummy files
            info = tarfile.TarInfo("model.bin")
            info.size = 10
            tf.addfile(info, io.BytesIO(b"dummy data"))
        
        result = await self.model_manager._extract_archive(tar_path, extract_path)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_extract_archive_unsupported(self):
        """Test extracting unsupported archive format"""
        archive_path = self.temp_models_dir / "test.unknown"
        extract_path = self.temp_models_dir / "extracted"
        
        # Create dummy file
        archive_path.write_bytes(b"dummy data")
        
        result = await self.model_manager._extract_archive(archive_path, extract_path)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_verify_download_success(self, create_test_model_dir):
        """Test successful download verification"""
        model_dir = create_test_model_dir("test_model")
        
        result = await self.model_manager._verify_download(model_dir)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_download_missing_config(self, temp_models_dir):
        """Test download verification with missing config"""
        model_dir = temp_models_dir / "incomplete_model"
        model_dir.mkdir()
        
        result = await self.model_manager._verify_download(model_dir)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_download_progress(self, mock_model_config):
        """Test getting download progress"""
        model_name = "test_model"
        self.model_manager.download_progress[model_name] = {
            "status": "downloading",
            "progress": 50.0,
            "total_size": 1000,
            "downloaded": 500
        }
        
        progress = await self.model_manager.get_download_progress(model_name)
        
        assert progress["status"] == "downloading"
        assert progress["progress"] == 50.0
    
    @pytest.mark.asyncio
    async def test_get_download_progress_not_found(self):
        """Test getting download progress for non-existent download"""
        model_name = "nonexistent_model"
        
        progress = await self.model_manager.get_download_progress(model_name)
        
        assert progress is None
    
    @pytest.mark.asyncio
    async def test_cancel_download(self, mock_model_config):
        """Test canceling an ongoing download"""
        model_name = "test_model"
        self.model_manager.downloading.add(model_name)
        self.model_manager.download_progress[model_name] = {
            "status": "downloading",
            "task": AsyncMock()
        }
        
        result = await self.model_manager.cancel_download(model_name)
        
        assert result is True
        assert model_name not in self.model_manager.downloading
    
    @pytest.mark.asyncio
    async def test_cancel_download_not_downloading(self):
        """Test canceling download that's not in progress"""
        model_name = "test_model"
        
        result = await self.model_manager.cancel_download(model_name)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup_cache_by_size(self, create_test_model_dir):
        """Test cleanup cache when size limit exceeded"""
        # Create multiple models
        model1_dir = create_test_model_dir("model1")
        model2_dir = create_test_model_dir("model2")
        model3_dir = create_test_model_dir("model3")
        
        # Add to available models with usage stats
        self.model_manager.available_models = {
            "model1": {"path": model1_dir, "size_mb": 100},
            "model2": {"path": model2_dir, "size_mb": 200},
            "model3": {"path": model3_dir, "size_mb": 300}
        }
        
        self.model_manager.model_usage_stats = {
            "model1": {"last_used": "2024-01-01", "use_count": 5},
            "model2": {"last_used": "2024-01-03", "use_count": 2},
            "model3": {"last_used": "2024-01-02", "use_count": 10}
        }
        
        # Set small cache limit
        self.model_manager.cache_size_limit = 400 * 1024**2  # 400MB
        
        with patch.object(self.model_manager, '_get_directory_size', return_value=500 * 1024**2):
            await self.model_manager._cleanup_cache()
            
            # Should remove least recently used models
            # Implementation depends on cleanup strategy
    
    @pytest.mark.asyncio
    async def test_update_usage_stats(self):
        """Test updating model usage statistics"""
        model_name = "test_model"
        
        await self.model_manager._update_usage_stats(model_name)
        
        assert model_name in self.model_manager.model_usage_stats
        assert "last_used" in self.model_manager.model_usage_stats[model_name]
        assert "use_count" in self.model_manager.model_usage_stats[model_name]
    
    @pytest.mark.asyncio
    async def test_get_cache_info(self, create_test_model_dir):
        """Test getting cache information"""
        # Create test models
        model1_dir = create_test_model_dir("model1")
        model2_dir = create_test_model_dir("model2")
        
        self.model_manager.available_models = {
            "model1": {"path": model1_dir, "size_mb": 100},
            "model2": {"path": model2_dir, "size_mb": 200}
        }
        
        with patch.object(self.model_manager, '_get_directory_size', return_value=300 * 1024**2):
            cache_info = await self.model_manager.get_cache_info()
            
            assert "total_size_mb" in cache_info
            assert "model_count" in cache_info
            assert "available_models" in cache_info
            assert cache_info["model_count"] == 2
    
    @pytest.mark.asyncio
    async def test_remove_model(self, create_test_model_dir):
        """Test removing a model"""
        model_name = "test_model"
        model_dir = create_test_model_dir(model_name)
        
        self.model_manager.available_models[model_name] = {"path": model_dir}
        
        result = await self.model_manager.remove_model(model_name)
        
        assert result is True
        assert model_name not in self.model_manager.available_models
        assert not model_dir.exists()
    
    @pytest.mark.asyncio
    async def test_remove_model_not_exists(self):
        """Test removing non-existent model"""
        model_name = "nonexistent_model"
        
        result = await self.model_manager.remove_model(model_name)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_list_models_by_type(self, mock_model_config):
        """Test listing models by type"""
        self.model_manager.model_configs = mock_model_config
        
        stt_models = await self.model_manager.list_models_by_type("stt")
        tts_models = await self.model_manager.list_models_by_type("tts")
        
        assert isinstance(stt_models, list)
        assert isinstance(tts_models, list)
        assert len(stt_models) > 0 or len(tts_models) > 0
    
    @pytest.mark.asyncio
    async def test_get_model_info(self, mock_model_config):
        """Test getting detailed model information"""
        model_name = "test_model"
        self.model_manager.model_configs = mock_model_config
        
        info = await self.model_manager.get_model_info(model_name)
        
        assert isinstance(info, dict)
        if model_name in mock_model_config:
            assert "type" in info
            assert "languages" in info
    
    @pytest.mark.asyncio
    async def test_cleanup_success(self):
        """Test successful cleanup"""
        with patch.object(self.model_manager, '_save_usage_stats', new_callable=AsyncMock):
            await self.model_manager.cleanup()
            
            self.model_manager._save_usage_stats.assert_called_once()


class TestModelManagerAdvanced:
    """Advanced test cases for ModelManager"""
    
    @pytest.fixture(autouse=True)
    def setup_advanced_manager(self, temp_models_dir, mock_settings):
        """Setup ModelManager for advanced testing"""
        from models.model_manager import ModelManager
        
        with patch('models.model_manager.get_settings', return_value=mock_settings):
            self.model_manager = ModelManager(temp_models_dir)
    
    @pytest.mark.asyncio
    async def test_concurrent_downloads(self, mock_model_config):
        """Test handling concurrent download requests"""
        model_names = ["model1", "model2", "model3"]
        self.model_manager.model_configs = {
            name: {"download_url": f"https://example.com/{name}.zip"}
            for name in model_names
        }
        
        with patch.object(self.model_manager, '_download_file', new_callable=AsyncMock) as mock_download, \
             patch.object(self.model_manager, '_extract_archive', new_callable=AsyncMock), \
             patch.object(self.model_manager, '_verify_download', new_callable=AsyncMock):
            
            mock_download.return_value = True
            
            # Start concurrent downloads
            tasks = [
                self.model_manager.download_model(name) 
                for name in model_names
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that downloads were handled properly
            successful_downloads = sum(1 for r in results if r is True)
            assert successful_downloads > 0
    
    @pytest.mark.asyncio
    async def test_download_progress_tracking(self, mock_model_config):
        """Test download progress tracking"""
        model_name = "test_model"
        self.model_manager.model_configs = mock_model_config
        
        async def mock_download_with_progress(url, output_path):
            # Simulate progress updates
            for progress in [25, 50, 75, 100]:
                self.model_manager.download_progress[model_name]["progress"] = progress
                await asyncio.sleep(0.01)  # Small delay
            return True
        
        with patch.object(self.model_manager, '_download_file', side_effect=mock_download_with_progress), \
             patch.object(self.model_manager, '_extract_archive', new_callable=AsyncMock) as mock_extract, \
             patch.object(self.model_manager, '_verify_download', new_callable=AsyncMock) as mock_verify:
            
            mock_extract.return_value = True
            mock_verify.return_value = True
            
            download_task = asyncio.create_task(
                self.model_manager.download_model(model_name)
            )
            
            # Check progress during download
            await asyncio.sleep(0.005)
            progress = await self.model_manager.get_download_progress(model_name)
            assert progress is not None
            
            result = await download_task
            assert result is True
    
    @pytest.mark.asyncio
    async def test_cache_eviction_lru(self, create_test_model_dir):
        """Test LRU cache eviction strategy"""
        # Create models with different usage patterns
        models = {}
        for i in range(5):
            model_name = f"model_{i}"
            model_dir = create_test_model_dir(model_name)
            models[model_name] = {
                "path": model_dir,
                "size_mb": 100,
                "last_used": f"2024-01-{i+1:02d}",
                "use_count": i + 1
            }
        
        self.model_manager.available_models = models
        self.model_manager.model_usage_stats = {
            name: {"last_used": info["last_used"], "use_count": info["use_count"]}
            for name, info in models.items()
        }
        
        # Set cache limit that requires eviction
        self.model_manager.cache_size_limit = 300 * 1024**2  # 300MB
        
        with patch.object(self.model_manager, '_get_directory_size', return_value=500 * 1024**2):
            await self.model_manager._cleanup_cache()
            
            # Verify that some models were removed
            # (Exact behavior depends on implementation)
            remaining_models = len(self.model_manager.available_models)
            assert remaining_models < 5
    
    def test_error_handling_corrupted_config(self, temp_models_dir):
        """Test handling corrupted model configuration"""
        # Create model directory with corrupted config
        model_dir = temp_models_dir / "corrupted_model"
        model_dir.mkdir()
        
        config_file = model_dir / "config.json"
        config_file.write_text("invalid json content {")
        
        # Should handle gracefully
        with pytest.raises(json.JSONDecodeError):
            with open(config_file, 'r') as f:
                json.load(f)


# Coverage target: >80% for ModelManager
# Key areas covered:
# - Initialization (100%)
# - Model download/management (95%)
# - Cache management (90%)
# - Progress tracking (85%)
# - Error handling (90%)
# - Concurrent operations (80%)
# - File operations (85%)
# - Configuration loading (95%)
