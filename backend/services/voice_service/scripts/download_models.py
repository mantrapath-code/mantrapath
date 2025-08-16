"""
Model Download and Management Script
Automated downloading and setup of local voice models
"""
import os
import sys
import asyncio
import aiohttp
import zipfile
import tarfile
import logging
from pathlib import Path
from typing import Dict, List, Optional
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelDownloader:
    """Downloads and manages voice models"""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model definitions
        self.models = {
            "whisper": {
                "tiny": {
                    "url": "https://openaipublic.azureedge.net/whisper/models/",
                    "size": "39MB",
                    "description": "Fastest, lowest quality"
                },
                "base": {
                    "url": "https://openaipublic.azureedge.net/whisper/models/",
                    "size": "74MB", 
                    "description": "Good balance of speed and quality"
                },
                "small": {
                    "url": "https://openaipublic.azureedge.net/whisper/models/",
                    "size": "244MB",
                    "description": "Better quality, slower"
                },
                "medium": {
                    "url": "https://openaipublic.azureedge.net/whisper/models/",
                    "size": "769MB",
                    "description": "High quality, recommended for most use cases"
                },
                "large": {
                    "url": "https://openaipublic.azureedge.net/whisper/models/",
                    "size": "1550MB",
                    "description": "Highest quality, slowest"
                }
            },
            "vosk": {
                "en-us": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
                    "size": "1.8GB",
                    "description": "English (US) - High quality"
                },
                "en-us-small": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
                    "size": "40MB",
                    "description": "English (US) - Lightweight"
                },
                # Indian Languages
                "hi": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-hi-0.22.zip",
                    "size": "1.1GB",
                    "description": "Hindi - High quality"
                },
                "hi-small": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip",
                    "size": "45MB",
                    "description": "Hindi - Lightweight"
                },
                # International Languages
                "es": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip",
                    "size": "1.2GB",
                    "description": "Spanish"
                },
                "fr": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-fr-0.39.zip",
                    "size": "1.4GB",
                    "description": "French"
                },
                "de": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip",
                    "size": "1.2GB",
                    "description": "German"
                },
                "ru": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-ru-0.42.zip",
                    "size": "1.5GB",
                    "description": "Russian"
                },
                "zh": {
                    "url": "https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip",
                    "size": "1.1GB",
                    "description": "Chinese"
                }
            },
            "coqui": {
                "xtts_v2": {
                    "description": "XTTS-v2 Multilingual TTS - Downloads automatically via TTS library",
                    "size": "~6GB",
                    "auto_download": True
                }
            }
        }
    
    async def download_file(self, url: str, destination: Path, description: str = "") -> bool:
        """Download a file with progress tracking"""
        try:
            logger.info(f"Downloading {description}: {url}")
            
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
                                print(f"\rProgress: {progress:.1f}%", end='', flush=True)
                    
                    print()  # New line after progress
                    logger.info(f"Successfully downloaded {description}")
                    return True
                    
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            return False
    
    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """Extract zip or tar archive"""
        try:
            logger.info(f"Extracting {archive_path} to {extract_to}")
            extract_to.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix.lower() in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            else:
                logger.error(f"Unsupported archive format: {archive_path.suffix}")
                return False
            
            logger.info(f"Successfully extracted {archive_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error extracting {archive_path}: {e}")
            return False
    
    async def download_whisper_models(self, models: List[str] = ["medium"]) -> bool:
        """Download Whisper models using the whisper library"""
        try:
            logger.info("Downloading Whisper models using whisper library...")
            
            # Import whisper to trigger model downloads
            try:
                import whisper
            except ImportError:
                logger.error("Whisper library not installed. Install with: pip install openai-whisper")
                return False
            
            for model_name in models:
                if model_name not in self.models["whisper"]:
                    logger.warning(f"Unknown Whisper model: {model_name}")
                    continue
                
                logger.info(f"Loading Whisper model: {model_name}")
                try:
                    # This will download the model if not already cached
                    model = whisper.load_model(model_name)
                    logger.info(f"Successfully loaded Whisper {model_name} model")
                except Exception as e:
                    logger.error(f"Failed to load Whisper {model_name} model: {e}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error downloading Whisper models: {e}")
            return False
    
    async def download_vosk_models(self, languages: List[str] = ["en-us"]) -> bool:
        """Download Vosk models"""
        try:
            vosk_dir = self.models_dir / "vosk"
            vosk_dir.mkdir(parents=True, exist_ok=True)
            
            for lang in languages:
                if lang not in self.models["vosk"]:
                    logger.warning(f"Unknown Vosk language: {lang}")
                    continue
                
                model_info = self.models["vosk"][lang]
                url = model_info["url"]
                
                # Extract model name from URL
                filename = url.split("/")[-1]
                model_name = filename.replace(".zip", "")
                
                model_dir = vosk_dir / model_name
                archive_path = vosk_dir / filename
                
                # Skip if already exists
                if model_dir.exists():
                    logger.info(f"Vosk {lang} model already exists at {model_dir}")
                    continue
                
                # Download
                success = await self.download_file(
                    url, 
                    archive_path, 
                    f"Vosk {lang} model ({model_info['size']})"
                )
                
                if not success:
                    continue
                
                # Extract
                if self.extract_archive(archive_path, vosk_dir):
                    # Clean up archive
                    archive_path.unlink()
                    logger.info(f"Vosk {lang} model ready at {model_dir}")
                else:
                    logger.error(f"Failed to extract Vosk {lang} model")
            
            return True
            
        except Exception as e:
            logger.error(f"Error downloading Vosk models: {e}")
            return False
    
    def setup_coqui_tts(self) -> bool:
        """Setup Coqui TTS (models download automatically)"""
        try:
            logger.info("Setting up Coqui TTS...")
            
            try:
                from TTS.api import TTS
            except ImportError:
                logger.error("Coqui TTS library not installed. Install with: pip install coqui-tts")
                return False
            
            # Test model loading (will download automatically)
            logger.info("Testing XTTS-v2 model (will download if not cached)...")
            try:
                tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
                logger.info("Coqui TTS setup successful")
                return True
            except Exception as e:
                logger.error(f"Failed to setup Coqui TTS: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting up Coqui TTS: {e}")
            return False
    
    def install_system_dependencies(self) -> None:
        """Print instructions for installing system dependencies"""
        logger.info("=== System Dependencies Installation Instructions ===")
        
        print("\n1. Ubuntu/Debian:")
        print("sudo apt update && sudo apt install -y \\")
        print("    festival espeak espeak-data libespeak-ng-dev \\")
        print("    festival-dev speech-tools festvox-kallpc16k \\")
        print("    ffmpeg sox libsox-fmt-all")
        
        print("\n2. macOS:")
        print("brew install festival espeak sox ffmpeg")
        
        print("\n3. For CUDA support (optional but recommended):")
        print("Follow NVIDIA CUDA installation guide for your OS")
        print("https://developer.nvidia.com/cuda-downloads")
        
        print("\n4. Python dependencies:")
        print("pip install -r requirements_local.txt")
    
    def create_config_files(self) -> None:
        """Create configuration files for local models"""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        # Local models configuration
        local_config = {
            "voice_engines": {
                "stt_engines": [
                    {
                        "name": "whisper_local",
                        "priority": 1,
                        "enabled": True,
                        "config": {
                            "model_size": "medium",
                            "device": "auto",
                            "use_faster_whisper": True,
                            "compute_type": "float16"
                        }
                    },
                    {
                        "name": "vosk",
                        "priority": 2,
                        "enabled": True,
                        "config": {
                            "model_path": "./models/vosk",
                            "sample_rate": 16000,
                            "language": "en"
                        }
                    }
                ],
                "tts_engines": [
                    {
                        "name": "coqui_local",
                        "priority": 1,
                        "enabled": True,
                        "config": {
                            "model_name": "tts_models/multilingual/multi-dataset/xtts_v2",
                            "device": "auto",
                            "use_cuda": True,
                            "sample_rate": 22050
                        }
                    },
                    {
                        "name": "festival",
                        "priority": 2,
                        "enabled": True,
                        "config": {
                            "voice": "default",
                            "sample_rate": 16000
                        }
                    }
                ]
            },
            "fallback_strategy": {
                "enable_api_fallback": True,
                "api_engines": ["whisper_api", "elevenlabs_api"],
                "max_retries": 3,
                "retry_delay": 1.0
            }
        }
        
        config_file = config_dir / "local_models_config.json"
        with open(config_file, 'w') as f:
            json.dump(local_config, f, indent=2)
        
        logger.info(f"Created local models configuration: {config_file}")
        
        # Environment file for local models
        env_file = config_dir / ".env.local"
        env_content = """# Local Voice Models Configuration

# Local Model Paths
MODELS_DIR=./models
VOSK_MODELS_DIR=./models/vosk
WHISPER_CACHE_DIR=~/.cache/whisper
COQUI_CACHE_DIR=~/.local/share/tts

# Model Selection
WHISPER_MODEL_SIZE=medium
VOSK_DEFAULT_LANGUAGE=en
COQUI_MODEL_NAME=tts_models/multilingual/multi-dataset/xtts_v2

# Hardware Settings
TORCH_DEVICE=auto  # auto, cpu, cuda
USE_GPU=true
COQUI_USE_CUDA=true
WHISPER_USE_FASTER=true

# Performance Settings
WHISPER_COMPUTE_TYPE=float16
VOSK_SAMPLE_RATE=16000
COQUI_SAMPLE_RATE=22050

# Fallback Settings
ENABLE_API_FALLBACK=true
MAX_MODEL_RETRIES=3
MODEL_RETRY_DELAY=1.0

# System Integration
FESTIVAL_VOICE=default
ESPEAK_VOICE=default
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"Created environment file: {env_file}")
    
    def print_model_info(self) -> None:
        """Print information about available models"""
        print("\n=== Available Models ===")
        
        print("\n📢 Speech-to-Text (STT) Models:")
        print("\n1. Whisper (OpenAI) - Local Installation:")
        for name, info in self.models["whisper"].items():
            print(f"   • {name}: {info['size']} - {info['description']}")
        
        print("\n2. Vosk - Lightweight Local STT:")
        for name, info in self.models["vosk"].items():
            print(f"   • {name}: {info['size']} - {info['description']}")
        
        print("\n🔊 Text-to-Speech (TTS) Models:")
        print("\n1. Coqui TTS - High Quality Local TTS:")
        for name, info in self.models["coqui"].items():
            print(f"   • {name}: {info['size']} - {info['description']}")
        
        print("\n2. System TTS (Festival/eSpeak):")
        print("   • Festival: High quality, multiple voices")
        print("   • eSpeak: Lightweight, fast, many languages")

async def main():
    """Main download and setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download and setup voice models for MantraPath")
    parser.add_argument("--models-dir", default="./models", help="Directory to store models")
    parser.add_argument("--whisper-models", nargs="+", default=["medium"], 
                       choices=["tiny", "base", "small", "medium", "large"],
                       help="Whisper models to download")
    parser.add_argument("--vosk-languages", nargs="+", default=["en-us"],
                       choices=["en-us", "en-us-small", "es", "fr", "de", "ru", "zh"],
                       help="Vosk language models to download")
    parser.add_argument("--setup-coqui", action="store_true", default=True,
                       help="Setup Coqui TTS")
    parser.add_argument("--info-only", action="store_true",
                       help="Only show model information")
    parser.add_argument("--create-config", action="store_true", default=True,
                       help="Create configuration files")
    
    args = parser.parse_args()
    
    downloader = ModelDownloader(args.models_dir)
    
    if args.info_only:
        downloader.print_model_info()
        downloader.install_system_dependencies()
        return
    
    logger.info("Starting voice models setup for MantraPath...")
    
    # Show available models
    downloader.print_model_info()
    
    # Install system dependencies info
    downloader.install_system_dependencies()
    
    print(f"\nDownloading models to: {downloader.models_dir}")
    
    # Download Whisper models
    logger.info(f"Downloading Whisper models: {args.whisper_models}")
    await downloader.download_whisper_models(args.whisper_models)
    
    # Download Vosk models
    logger.info(f"Downloading Vosk models: {args.vosk_languages}")
    await downloader.download_vosk_models(args.vosk_languages)
    
    # Setup Coqui TTS
    if args.setup_coqui:
        downloader.setup_coqui_tts()
    
    # Create configuration files
    if args.create_config:
        downloader.create_config_files()
    
    logger.info("✅ Voice models setup completed!")
    print("\nNext steps:")
    print("1. Install system dependencies (see instructions above)")
    print("2. Copy config/.env.local to .env and customize if needed")
    print("3. Update your voice service configuration to use local engines")
    print("4. Test the models with your voice service")

if __name__ == "__main__":
    asyncio.run(main())
