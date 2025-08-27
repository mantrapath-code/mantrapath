"""
Model Manager - Central component for managing all AI models
"""

import asyncio
import aiohttp
import zipfile
import tarfile
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
import hashlib
import torch

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages downloading, loading, and caching of AI models"""
    
    def __init__(self, models_dir: Path):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model registry
        self.available_models: Dict[str, Dict] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.model_configs: Dict[str, Dict] = {}
        
        # Download tracking
        self.download_progress: Dict[str, Dict] = {}
        self.downloading: set = set()
        
        # Cache management
        self.cache_size_limit = 10 * 1024**3  # 10GB default
        self.model_usage_stats: Dict[str, Dict] = {}
    
    async def initialize(self):
        """Initialize model manager"""
        logger.info("🔧 Initializing Model Manager...")
        
        # Load model configurations
        await self._load_model_configs()
        
        # Scan existing models
        await self._scan_existing_models()
        
        # Load usage statistics
        await self._load_usage_stats()
        
        logger.info(f"✅ Model Manager initialized. {len(self.available_models)} models available")
    
    async def _load_model_configs(self):
        """Load model configurations from settings"""
        from config.settings import get_settings
        settings = get_settings()
        
        self.model_configs = settings.MODEL_CONFIGS
        
        # Add Indian language models from configuration
        for lang_code, lang_info in settings.INDIAN_LANGUAGES.items():
            # Add STT models for this language
            for stt_model in lang_info.get("stt_models", []):
                model_key = f"{stt_model}_{lang_code}"
                if model_key not in self.model_configs:
                    self.model_configs[model_key] = {
                        "type": "stt",
                        "engine": stt_model.split("-")[0],
                        "languages": [lang_code],
                        "quality": "good",
                        "device": ["cpu"]
                    }
            
            # Add TTS models for this language  
            for tts_model in lang_info.get("tts_models", []):
                model_key = f"{tts_model}_{lang_code}"
                if model_key not in self.model_configs:
                    self.model_configs[model_key] = {
                        "type": "tts", 
                        "engine": tts_model.split("-")[0],
                        "languages": [lang_code],
                        "quality": "good",
                        "device": ["cpu"]
                    }
    
    async def _scan_existing_models(self):
        """Scan for existing downloaded models"""
        if not self.models_dir.exists():
            return
        
        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                model_name = model_dir.name
                
                # Check if this is a valid model directory
                if await self._validate_model_directory(model_dir):
                    self.available_models[model_name] = {
                        "path": model_dir,
                        "status": "available",
                        "size": await self._calculate_directory_size(model_dir),
                        "downloaded_at": datetime.fromtimestamp(model_dir.stat().st_mtime).isoformat()
                    }
                    logger.info(f"Found existing model: {model_name}")
    
    async def _validate_model_directory(self, model_dir: Path) -> bool:
        """Validate if directory contains a valid model"""
        # Check for common model files
        model_files = [
            "pytorch_model.bin",
            "model.bin", 
            "model.pt",
            "config.json",
            "vocab.json",
            "final.mdl",  # Vosk
            "graph",      # Vosk
            "model.tflite"
        ]
        
        return any((model_dir / file).exists() for file in model_files)
    
    async def _calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory"""
        total_size = 0
        for file_path in directory.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    async def _load_usage_stats(self):
        """Load model usage statistics"""
        stats_file = self.models_dir / "usage_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    self.model_usage_stats = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load usage stats: {e}")
                self.model_usage_stats = {}
    
    async def _save_usage_stats(self):
        """Save model usage statistics"""
        stats_file = self.models_dir / "usage_stats.json"
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.model_usage_stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save usage stats: {e}")
    
    async def download_model(self, model_name: str, force: bool = False) -> bool:
        """Download a model"""
        if model_name in self.downloading:
            logger.info(f"Model {model_name} is already being downloaded")
            return False
        
        if model_name in self.available_models and not force:
            logger.info(f"Model {model_name} already available")
            return True
        
        if model_name not in self.model_configs:
            logger.error(f"Unknown model: {model_name}")
            return False
        
        model_config = self.model_configs[model_name]
        
        try:
            self.downloading.add(model_name)
            logger.info(f"📥 Starting download of {model_name}")
            
            # Initialize progress tracking
            self.download_progress[model_name] = {
                "status": "downloading",
                "progress": 0,
                "started_at": datetime.utcnow().isoformat()
            }
            
            # Handle different engines
            engine = model_config.get("engine", "unknown")
            
            if engine == "whisper":
                success = await self._download_whisper_model(model_name, model_config)
            elif engine == "vosk":
                success = await self._download_vosk_model(model_name, model_config)
            elif engine == "wav2vec2":
                success = await self._download_huggingface_model(model_name, model_config)
            elif engine == "coqui":
                success = await self._download_coqui_model(model_name, model_config)
            else:
                logger.error(f"Unsupported engine: {engine}")
                success = False
            
            if success:
                self.download_progress[model_name]["status"] = "completed"
                self.download_progress[model_name]["progress"] = 100
                self.available_models[model_name] = {
                    "path": self.models_dir / model_name,
                    "status": "available",
                    "downloaded_at": datetime.utcnow().isoformat()
                }
                logger.info(f"✅ Successfully downloaded {model_name}")
            else:
                self.download_progress[model_name]["status"] = "failed"
                logger.error(f"❌ Failed to download {model_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error downloading {model_name}: {e}")
            self.download_progress[model_name]["status"] = "failed" 
            return False
        finally:
            self.downloading.discard(model_name)
    
    async def _download_whisper_model(self, model_name: str, config: Dict) -> bool:
        """Download Whisper model using whisper library"""
        try:
            import whisper
            
            # Extract model size from name
            size = model_name.replace("whisper_", "")
            
            # This will download and cache the model
            model = whisper.load_model(size)
            
            # Models are cached by whisper library in ~/.cache/whisper
            # We create a symlink in our models directory
            cache_dir = Path.home() / ".cache" / "whisper"
            model_file = None
            
            for file in cache_dir.glob(f"*{size}*"):
                if file.is_file():
                    model_file = file
                    break
            
            if model_file:
                model_dir = self.models_dir / model_name
                model_dir.mkdir(parents=True, exist_ok=True)
                
                # Create symlink
                symlink_path = model_dir / model_file.name
                if not symlink_path.exists():
                    symlink_path.symlink_to(model_file)
                
                # Create config file
                config_data = {
                    "model_type": "whisper",
                    "model_size": size,
                    "model_file": str(model_file),
                    "config": config
                }
                
                with open(model_dir / "config.json", 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                return True
            
            return False
            
        except ImportError:
            logger.error("Whisper library not installed")
            return False
        except Exception as e:
            logger.error(f"Error downloading Whisper model: {e}")
            return False
    
    async def _download_vosk_model(self, model_name: str, config: Dict) -> bool:
        """Download Vosk model"""
        try:
            url = config.get("url")
            if not url:
                logger.error(f"No URL specified for Vosk model {model_name}")
                return False
            
            # Download archive
            archive_path = self.models_dir / f"{model_name}.zip"
            success = await self._download_file(url, archive_path, model_name)
            
            if not success:
                return False
            
            # Extract archive
            model_dir = self.models_dir / model_name
            model_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(model_dir)
            
            # Clean up archive
            archive_path.unlink()
            
            # Create config file
            config_data = {
                "model_type": "vosk",
                "model_url": url,
                "config": config
            }
            
            with open(model_dir / "config.json", 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error downloading Vosk model: {e}")
            return False
    
    async def _download_huggingface_model(self, model_name: str, config: Dict) -> bool:
        """Download model from Hugging Face"""
        try:
            from transformers import AutoModel, AutoTokenizer, AutoProcessor
            
            model_id = config.get("model_id")
            if not model_id:
                logger.error(f"No model_id specified for {model_name}")
                return False
            
            model_dir = self.models_dir / model_name
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Download model
            model = AutoModel.from_pretrained(model_id, cache_dir=str(model_dir))
            
            # Try to download tokenizer/processor
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=str(model_dir))
            except:
                try:
                    processor = AutoProcessor.from_pretrained(model_id, cache_dir=str(model_dir))
                except:
                    pass  # Some models don't have tokenizers
            
            # Create config file
            config_data = {
                "model_type": "huggingface",
                "model_id": model_id,
                "config": config
            }
            
            with open(model_dir / "config.json", 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
            
        except ImportError:
            logger.error("Transformers library not installed")
            return False
        except Exception as e:
            logger.error(f"Error downloading Hugging Face model: {e}")
            return False
    
    async def _download_coqui_model(self, model_name: str, config: Dict) -> bool:
        """Download Coqui TTS model"""
        try:
            from TTS.api import TTS
            
            model_name_tts = config.get("model_name")
            if not model_name_tts:
                logger.error(f"No model_name specified for Coqui model {model_name}")
                return False
            
            # Initialize TTS (this will download the model)
            tts = TTS(model_name_tts)
            
            # Models are cached by TTS library
            # Create our own reference
            model_dir = self.models_dir / model_name
            model_dir.mkdir(parents=True, exist_ok=True)
            
            config_data = {
                "model_type": "coqui",
                "model_name": model_name_tts,
                "config": config
            }
            
            with open(model_dir / "config.json", 'w') as f:
                json.dump(config_data, f, indent=2)
            
            return True
            
        except ImportError:
            logger.error("Coqui TTS library not installed")
            return False
        except Exception as e:
            logger.error(f"Error downloading Coqui model: {e}")
            return False
    
    async def _download_file(self, url: str, destination: Path, model_name: str) -> bool:
        """Download file with progress tracking"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download {url}: HTTP {response.status}")
                        return False
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    with open(destination, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                self.download_progress[model_name]["progress"] = progress
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return False
    
    def get_model_path(self, model_name: str) -> Optional[Path]:
        """Get path to a model"""
        if model_name in self.available_models:
            return self.available_models[model_name]["path"]
        return None
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if model is available locally"""
        return model_name in self.available_models
    
    def get_download_progress(self, model_name: str) -> Optional[Dict]:
        """Get download progress for a model"""
        return self.download_progress.get(model_name)
    
    async def get_available_models(self) -> Dict:
        """Get list of all available models"""
        return {
            "local_models": self.available_models,
            "downloadable_models": self.model_configs,
            "download_progress": self.download_progress
        }
    
    def update_usage_stats(self, model_name: str, operation: str):
        """Update usage statistics for a model"""
        if model_name not in self.model_usage_stats:
            self.model_usage_stats[model_name] = {
                "usage_count": 0,
                "last_used": None,
                "operations": {}
            }
        
        stats = self.model_usage_stats[model_name]
        stats["usage_count"] += 1
        stats["last_used"] = datetime.utcnow().isoformat()
        
        if operation not in stats["operations"]:
            stats["operations"][operation] = 0
        stats["operations"][operation] += 1
        
        # Save stats periodically
        asyncio.create_task(self._save_usage_stats())
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up Model Manager...")
        await self._save_usage_stats()
        logger.info("✅ Model Manager cleanup complete")
