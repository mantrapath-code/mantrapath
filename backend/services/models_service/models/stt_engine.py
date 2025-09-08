"""
Speech-to-Text Engine
Supports multiple STT engines including Whisper, Vosk, Wav2Vec2
"""

import asyncio
import io
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import numpy as np
import librosa
import torch

logger = logging.getLogger(__name__)

class STTEngine:
    """Speech-to-Text processing engine"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.loaded_models: Dict[str, Any] = {}
        self.default_models: Dict[str, str] = {}
        
        # Language support mapping
        self.supported_languages = {
            "en": ["whisper_medium", "vosk_en_us", "wav2vec2_en"],
            "hi": ["whisper_medium", "vosk_hi", "wav2vec2_hi"],
            "bn": ["whisper_medium", "wav2vec2_bn"],
            "te": ["wav2vec2_te"],
            "ta": ["wav2vec2_ta"],
            "mr": ["vosk_mr"],
            "gu": ["vosk_gu"],
            "kn": ["vosk_kn"],
            "ml": ["vosk_ml"],
            "pa": ["vosk_pa"],
            "or": ["vosk_or"],
            "as": ["vosk_as"],
            "es": ["whisper_medium", "vosk_es"],
            "fr": ["whisper_medium", "vosk_fr"],
            "de": ["whisper_medium", "vosk_de"],
            "ru": ["whisper_medium", "vosk_ru"],
            "zh": ["whisper_medium", "vosk_zh"]
        }
    
    async def load_default_models(self):
        """Load default STT models gracefully"""
        logger.info("🔊 Attempting to load default STT models...")
        
        # Check if we're in minimal mode
        if os.environ.get("MODELS_SERVICE_MODE") == "minimal":
            logger.info("✅ STT Engine initialized in minimal mode (models will load on-demand)")
            return
        
        # Load primary models
        primary_models = [
            "whisper_medium",  # Good quality, multilingual
            "vosk_en_us_small",  # Fast English
            "vosk_hi_small"  # Fast Hindi
        ]
        
        loaded_count = 0
        for model_name in primary_models:
            try:
                success = await self.load_model(model_name)
                if success:
                    loaded_count += 1
                    logger.info(f"✅ Loaded STT model: {model_name}")
                else:
                    logger.warning(f"⚠️ STT model {model_name} not available locally")
            except Exception as e:
                logger.warning(f"⚠️ Could not load STT model {model_name}: {e}")
        
        if loaded_count == 0:
            logger.warning("⚠️ No STT models loaded - service will attempt to load models on-demand")
        else:
            logger.info(f"✅ Loaded {loaded_count}/{len(primary_models)} STT models")
    
    async def load_model(self, model_name: str) -> bool:
        """Load a specific STT model"""
        if model_name in self.loaded_models:
            logger.info(f"STT model {model_name} already loaded")
            return True
        
        if not self.model_manager.is_model_available(model_name):
            logger.error(f"STT model {model_name} not available locally")
            return False
        
        try:
            model_path = self.model_manager.get_model_path(model_name)
            config_file = model_path / "config.json"
            
            if not config_file.exists():
                logger.error(f"Config file not found for {model_name}")
                return False
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            model_type = config.get("model_type")
            
            if model_type == "whisper":
                model = await self._load_whisper_model(model_name, config)
            elif model_type == "vosk":
                model = await self._load_vosk_model(model_name, config, model_path)
            elif model_type == "huggingface":
                model = await self._load_huggingface_model(model_name, config)
            else:
                logger.error(f"Unsupported STT model type: {model_type}")
                return False
            
            if model:
                self.loaded_models[model_name] = {
                    "model": model,
                    "config": config,
                    "type": model_type
                }
                logger.info(f"✅ Successfully loaded STT model: {model_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading STT model {model_name}: {e}")
            return False
    
    async def _load_whisper_model(self, model_name: str, config: Dict) -> Any:
        """Load Whisper model"""
        try:
            import whisper
            
            model_size = config.get("model_size", "medium")
            model = whisper.load_model(model_size)
            
            return model
            
        except ImportError:
            logger.error("Whisper library not installed")
            return None
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            return None
    
    async def _load_vosk_model(self, model_name: str, config: Dict, model_path: Path) -> Any:
        """Load Vosk model"""
        try:
            import vosk
            import json as json_lib
            
            # Find the actual model directory (Vosk extracts to a subdirectory)
            model_dirs = list(model_path.glob("vosk-model-*"))
            if not model_dirs:
                logger.error(f"No Vosk model directory found in {model_path}")
                return None
            
            actual_model_path = model_dirs[0]
            
            # Load model
            vosk_model = vosk.Model(str(actual_model_path))
            
            return vosk_model
            
        except ImportError:
            logger.error("Vosk library not installed")
            return None
        except Exception as e:
            logger.error(f"Error loading Vosk model: {e}")
            return None
    
    async def _load_huggingface_model(self, model_name: str, config: Dict) -> Any:
        """Load Hugging Face model"""
        try:
            from transformers import AutoModel, AutoTokenizer, AutoProcessor
            
            model_id = config.get("model_id")
            model_path = self.model_manager.get_model_path(model_name)
            
            # Load model
            model = AutoModel.from_pretrained(str(model_path))
            
            # Load processor/tokenizer
            try:
                processor = AutoProcessor.from_pretrained(str(model_path))
            except:
                try:
                    processor = AutoTokenizer.from_pretrained(str(model_path))
                except:
                    processor = None
            
            return {
                "model": model,
                "processor": processor
            }
            
        except ImportError:
            logger.error("Transformers library not installed")
            return None
        except Exception as e:
            logger.error(f"Error loading Hugging Face model: {e}")
            return None
    
    async def transcribe(
        self,
        audio_data: Union[bytes, np.ndarray, str, Path],
        language: str = "auto",
        model_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Transcribe audio to text"""
        try:
            # Preprocess audio
            audio_array, sample_rate = await self._preprocess_audio(audio_data)
            
            # Select model
            model_name = await self._select_model(language, model_preference)
            if not model_name:
                return {
                    "success": False,
                    "error": f"No suitable STT model available for language: {language}"
                }
            
            # Load model if not already loaded
            if model_name not in self.loaded_models:
                await self.load_model(model_name)
            
            if model_name not in self.loaded_models:
                return {
                    "success": False,
                    "error": f"Failed to load STT model: {model_name}"
                }
            
            # Perform transcription
            model_info = self.loaded_models[model_name]
            model_type = model_info["type"]
            
            if model_type == "whisper":
                result = await self._transcribe_whisper(
                    audio_array, model_info, language
                )
            elif model_type == "vosk":
                result = await self._transcribe_vosk(
                    audio_array, sample_rate, model_info
                )
            elif model_type == "huggingface":
                result = await self._transcribe_huggingface(
                    audio_array, model_info, language
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported model type: {model_type}"
                }
            
            # Update usage stats
            self.model_manager.update_usage_stats(model_name, "transcribe")
            
            result["model_used"] = model_name
            result["language_detected"] = language
            
            return result
            
        except Exception as e:
            logger.error(f"Error in transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _preprocess_audio(
        self, 
        audio_data: Union[bytes, np.ndarray, str, Path]
    ) -> tuple[np.ndarray, int]:
        """Preprocess audio data"""
        if isinstance(audio_data, (str, Path)):
            # Load from file
            audio_array, sample_rate = librosa.load(str(audio_data), sr=16000)
        elif isinstance(audio_data, bytes):
            # Load from bytes
            audio_array, sample_rate = librosa.load(io.BytesIO(audio_data), sr=16000)
        elif isinstance(audio_data, np.ndarray):
            # Already an array
            audio_array = audio_data
            sample_rate = 16000  # Assume 16kHz
        else:
            raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
        
        # Ensure 16kHz sample rate
        if sample_rate != 16000:
            audio_array = librosa.resample(audio_array, orig_sr=sample_rate, target_sr=16000)
            sample_rate = 16000
        
        return audio_array, sample_rate
    
    async def _select_model(self, language: str, preference: Optional[str]) -> Optional[str]:
        """Select best available model for language"""
        if preference and preference in self.loaded_models:
            return preference
        
        # Auto-detect language if needed
        if language == "auto":
            language = "en"  # Default to English
        
        # Get available models for language
        available_models = self.supported_languages.get(language, [])
        
        # Find first available model
        for model_name in available_models:
            if (self.model_manager.is_model_available(model_name) or 
                model_name in self.loaded_models):
                return model_name
        
        # Fallback to multilingual models
        multilingual_models = ["whisper_medium", "whisper_small", "whisper_base"]
        for model_name in multilingual_models:
            if (self.model_manager.is_model_available(model_name) or 
                model_name in self.loaded_models):
                return model_name
        
        return None
    
    async def _transcribe_whisper(
        self, 
        audio_array: np.ndarray, 
        model_info: Dict, 
        language: str
    ) -> Dict[str, Any]:
        """Transcribe using Whisper"""
        try:
            model = model_info["model"]
            
            # Set language if not auto
            options = {}
            if language != "auto":
                options["language"] = language
            
            # Transcribe
            result = model.transcribe(audio_array, **options)
            
            return {
                "success": True,
                "text": result["text"].strip(),
                "language": result.get("language", language),
                "confidence": 0.9,  # Whisper doesn't provide confidence
                "segments": result.get("segments", [])
            }
            
        except Exception as e:
            logger.error(f"Error in Whisper transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _transcribe_vosk(
        self, 
        audio_array: np.ndarray, 
        sample_rate: int,
        model_info: Dict
    ) -> Dict[str, Any]:
        """Transcribe using Vosk"""
        try:
            import vosk
            import json
            
            model = model_info["model"]
            
            # Create recognizer
            rec = vosk.KaldiRecognizer(model, sample_rate)
            
            # Convert audio to bytes
            audio_bytes = (audio_array * 32767).astype(np.int16).tobytes()
            
            # Process audio
            rec.AcceptWaveform(audio_bytes)
            final_result = json.loads(rec.FinalResult())
            
            return {
                "success": True,
                "text": final_result.get("text", ""),
                "confidence": final_result.get("confidence", 0.8)
            }
            
        except Exception as e:
            logger.error(f"Error in Vosk transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _transcribe_huggingface(
        self, 
        audio_array: np.ndarray, 
        model_info: Dict,
        language: str
    ) -> Dict[str, Any]:
        """Transcribe using Hugging Face models"""
        try:
            model_data = model_info["model"]
            model = model_data["model"]
            processor = model_data["processor"]
            
            if not processor:
                return {
                    "success": False,
                    "error": "No processor available for this model"
                }
            
            # Process audio
            inputs = processor(audio_array, return_tensors="pt", sampling_rate=16000)
            
            # Generate
            with torch.no_grad():
                logits = model(**inputs).logits
            
            # Decode
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = processor.decode(predicted_ids[0])
            
            return {
                "success": True,
                "text": transcription.strip(),
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Error in Hugging Face transcription: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_supported_languages(self) -> Dict[str, List[str]]:
        """Get supported languages and their available models"""
        return self.supported_languages
    
    async def unload_model(self, model_name: str):
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            logger.info(f"Unloaded STT model: {model_name}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up STT Engine...")
        self.loaded_models.clear()
        logger.info("✅ STT Engine cleanup complete")
