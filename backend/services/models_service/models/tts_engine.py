"""
Text-to-Speech Engine
Supports multiple TTS engines including Coqui TTS, Festival, eSpeak
"""

import asyncio
import io
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import numpy as np
import soundfile as sf
import torch

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-Speech processing engine"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.loaded_models: Dict[str, Any] = {}
        self.default_models: Dict[str, str] = {}
        
        # Language support mapping
        self.supported_languages = {
            "en": ["coqui_xtts_v2", "festival_en", "espeak_en"],
            "hi": ["coqui_xtts_v2", "coqui_hi", "festival_hi", "espeak_hi"],
            "bn": ["coqui_bn", "espeak_bn"],
            "te": ["coqui_xtts_v2", "espeak_te"],
            "ta": ["coqui_xtts_v2", "espeak_ta"],
            "mr": ["coqui_xtts_v2", "espeak_mr"],
            "gu": ["coqui_xtts_v2", "espeak_gu"],
            "kn": ["coqui_xtts_v2", "espeak_kn"],
            "ml": ["coqui_xtts_v2", "espeak_ml"],
            "pa": ["espeak_pa"],
            "or": ["espeak_or"],
            "as": ["espeak_as"],
            "es": ["coqui_xtts_v2", "espeak_es"],
            "fr": ["coqui_xtts_v2", "espeak_fr"],
            "de": ["coqui_xtts_v2", "espeak_de"],
            "it": ["coqui_xtts_v2", "espeak_it"],
            "pt": ["coqui_xtts_v2", "espeak_pt"],
            "ru": ["coqui_xtts_v2", "espeak_ru"],
            "zh": ["coqui_xtts_v2", "espeak_zh"],
            "ja": ["coqui_xtts_v2", "espeak_ja"],
            "ko": ["coqui_xtts_v2", "espeak_ko"]
        }
    
    async def load_default_models(self):
        """Load default TTS models"""
        logger.info("🔊 Loading default TTS models...")
        
        # Load primary models
        primary_models = [
            "coqui_xtts_v2",  # High quality multilingual
            "espeak_en",      # Fast English fallback
            "espeak_hi"       # Fast Hindi fallback
        ]
        
        for model_name in primary_models:
            try:
                await self.load_model(model_name)
                logger.info(f"✅ Loaded TTS model: {model_name}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load TTS model {model_name}: {e}")
    
    async def load_model(self, model_name: str) -> bool:
        """Load a specific TTS model"""
        if model_name in self.loaded_models:
            logger.info(f"TTS model {model_name} already loaded")
            return True
        
        try:
            # Handle system TTS engines
            if model_name.startswith("espeak_") or model_name.startswith("festival_"):
                return await self._load_system_tts(model_name)
            
            # Handle file-based models
            if not self.model_manager.is_model_available(model_name):
                logger.error(f"TTS model {model_name} not available locally")
                return False
            
            model_path = self.model_manager.get_model_path(model_name)
            config_file = model_path / "config.json"
            
            if not config_file.exists():
                logger.error(f"Config file not found for {model_name}")
                return False
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            model_type = config.get("model_type")
            
            if model_type == "coqui":
                model = await self._load_coqui_model(model_name, config)
            else:
                logger.error(f"Unsupported TTS model type: {model_type}")
                return False
            
            if model:
                self.loaded_models[model_name] = {
                    "model": model,
                    "config": config,
                    "type": model_type
                }
                logger.info(f"✅ Successfully loaded TTS model: {model_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading TTS model {model_name}: {e}")
            return False
    
    async def _load_system_tts(self, model_name: str) -> bool:
        """Load system TTS engines (eSpeak, Festival)"""
        try:
            engine = model_name.split("_")[0]
            language = model_name.split("_")[1] if "_" in model_name else "en"
            
            # Check if system command is available
            if engine == "espeak":
                result = subprocess.run(["which", "espeak"], capture_output=True)
                if result.returncode != 0:
                    logger.error("eSpeak not installed")
                    return False
            elif engine == "festival":
                result = subprocess.run(["which", "festival"], capture_output=True)
                if result.returncode != 0:
                    logger.error("Festival not installed")
                    return False
            
            self.loaded_models[model_name] = {
                "model": None,  # System command
                "config": {
                    "engine": engine,
                    "language": language
                },
                "type": "system"
            }
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading system TTS {model_name}: {e}")
            return False
    
    async def _load_coqui_model(self, model_name: str, config: Dict) -> Any:
        """Load Coqui TTS model"""
        try:
            from TTS.api import TTS
            
            model_name_tts = config.get("model_name")
            if not model_name_tts:
                logger.error(f"No model_name specified for {model_name}")
                return None
            
            # Initialize TTS
            tts = TTS(model_name_tts)
            
            return tts
            
        except ImportError:
            logger.error("Coqui TTS library not installed")
            return None
        except Exception as e:
            logger.error(f"Error loading Coqui model: {e}")
            return None
    
    async def synthesize(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None,
        model_preference: Optional[str] = None,
        speaker_wav: Optional[Union[str, bytes]] = None
    ) -> Dict[str, Any]:
        """Synthesize text to speech"""
        try:
            # Select model
            model_name = await self._select_model(language, model_preference)
            if not model_name:
                return {
                    "success": False,
                    "error": f"No suitable TTS model available for language: {language}"
                }
            
            # Load model if not already loaded
            if model_name not in self.loaded_models:
                await self.load_model(model_name)
            
            if model_name not in self.loaded_models:
                return {
                    "success": False,
                    "error": f"Failed to load TTS model: {model_name}"
                }
            
            # Perform synthesis
            model_info = self.loaded_models[model_name]
            model_type = model_info["type"]
            
            if model_type == "coqui":
                result = await self._synthesize_coqui(
                    text, model_info, language, voice, speaker_wav
                )
            elif model_type == "system":
                result = await self._synthesize_system(
                    text, model_info, language, voice
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported model type: {model_type}"
                }
            
            # Update usage stats
            self.model_manager.update_usage_stats(model_name, "synthesize")
            
            result["model_used"] = model_name
            result["language"] = language
            
            return result
            
        except Exception as e:
            logger.error(f"Error in synthesis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _select_model(self, language: str, preference: Optional[str]) -> Optional[str]:
        """Select best available model for language"""
        if preference and preference in self.loaded_models:
            return preference
        
        # Get available models for language
        available_models = self.supported_languages.get(language, [])
        
        # Find first available model
        for model_name in available_models:
            if (self.model_manager.is_model_available(model_name) or 
                model_name in self.loaded_models or
                model_name.startswith("espeak_") or 
                model_name.startswith("festival_")):
                return model_name
        
        # Fallback to multilingual models
        multilingual_models = ["coqui_xtts_v2", "espeak_en"]
        for model_name in multilingual_models:
            if (self.model_manager.is_model_available(model_name) or 
                model_name in self.loaded_models or
                model_name.startswith("espeak_")):
                return model_name
        
        return None
    
    async def _synthesize_coqui(
        self,
        text: str,
        model_info: Dict,
        language: str,
        voice: Optional[str],
        speaker_wav: Optional[Union[str, bytes]]
    ) -> Dict[str, Any]:
        """Synthesize using Coqui TTS"""
        try:
            tts = model_info["model"]
            
            # Handle voice cloning if speaker_wav provided
            kwargs = {}
            if speaker_wav:
                if isinstance(speaker_wav, bytes):
                    # Save bytes to temporary file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        f.write(speaker_wav)
                        kwargs["speaker_wav"] = f.name
                else:
                    kwargs["speaker_wav"] = speaker_wav
            
            # Set language if model supports it
            if hasattr(tts, 'synthesizer') and hasattr(tts.synthesizer, 'tts_config'):
                if language in getattr(tts.synthesizer.tts_config, 'languages', []):
                    kwargs["language"] = language
            
            # Generate audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
                output_path = output_file.name
            
            tts.tts_to_file(text=text, file_path=output_path, **kwargs)
            
            # Read generated audio
            audio_data, sample_rate = sf.read(output_path)
            
            # Clean up temporary files
            Path(output_path).unlink()
            if "speaker_wav" in kwargs and isinstance(speaker_wav, bytes):
                Path(kwargs["speaker_wav"]).unlink()
            
            # Convert to bytes
            audio_bytes = io.BytesIO()
            sf.write(audio_bytes, audio_data, sample_rate, format="WAV")
            audio_bytes.seek(0)
            
            return {
                "success": True,
                "audio_data": audio_bytes.read(),
                "sample_rate": sample_rate,
                "duration": len(audio_data) / sample_rate,
                "format": "wav"
            }
            
        except Exception as e:
            logger.error(f"Error in Coqui synthesis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _synthesize_system(
        self,
        text: str,
        model_info: Dict,
        language: str,
        voice: Optional[str]
    ) -> Dict[str, Any]:
        """Synthesize using system TTS (eSpeak, Festival)"""
        try:
            config = model_info["config"]
            engine = config["engine"]
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
                output_path = output_file.name
            
            if engine == "espeak":
                cmd = ["espeak", "-w", output_path]
                
                # Set language/voice
                if language == "hi":
                    cmd.extend(["-v", "hi"])
                elif language == "bn":
                    cmd.extend(["-v", "bn"])
                elif language in ["te", "ta", "mr", "gu", "kn", "ml"]:
                    cmd.extend(["-v", language])
                else:
                    cmd.extend(["-v", "en"])
                
                # Set speaking rate and pitch
                cmd.extend(["-s", "150", "-p", "50"])
                cmd.append(text)
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
            elif engine == "festival":
                # Create temporary text file
                with tempfile.NamedTemporaryFile(mode='w', suffix=".txt", delete=False) as text_file:
                    text_file.write(text)
                    text_path = text_file.name
                
                cmd = [
                    "festival", "--tts", text_path,
                    "--otype", "wav", 
                    "--output", output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                Path(text_path).unlink()
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported system engine: {engine}"
                }
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"System TTS failed: {result.stderr}"
                }
            
            # Read generated audio
            if not Path(output_path).exists():
                return {
                    "success": False,
                    "error": "System TTS did not generate audio file"
                }
            
            audio_data, sample_rate = sf.read(output_path)
            
            # Clean up
            Path(output_path).unlink()
            
            # Convert to bytes
            audio_bytes = io.BytesIO()
            sf.write(audio_bytes, audio_data, sample_rate, format="WAV")
            audio_bytes.seek(0)
            
            return {
                "success": True,
                "audio_data": audio_bytes.read(),
                "sample_rate": sample_rate,
                "duration": len(audio_data) / sample_rate,
                "format": "wav"
            }
            
        except Exception as e:
            logger.error(f"Error in system TTS synthesis: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_available_voices(self, language: str = "en") -> Dict[str, List[str]]:
        """Get available voices for a language"""
        voices = {
            "coqui": [],
            "system": []
        }
        
        # Check for loaded Coqui models
        for model_name, model_info in self.loaded_models.items():
            if model_info["type"] == "coqui":
                tts = model_info["model"]
                if hasattr(tts, 'synthesizer'):
                    if hasattr(tts.synthesizer, 'tts_speakers'):
                        voices["coqui"].extend(tts.synthesizer.tts_speakers)
        
        # Check system voices
        if language == "en":
            voices["system"].extend(["default", "male", "female"])
        elif language in ["hi", "bn", "te", "ta", "mr", "gu", "kn", "ml"]:
            voices["system"].append(f"{language}_default")
        
        return voices
    
    async def get_supported_languages(self) -> Dict[str, List[str]]:
        """Get supported languages and their available models"""
        return self.supported_languages
    
    async def clone_voice(
        self,
        reference_audio: Union[str, bytes],
        text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Clone a voice from reference audio"""
        # Use XTTS-v2 for voice cloning if available
        xtts_models = [name for name in self.loaded_models.keys() if "xtts" in name]
        
        if not xtts_models:
            return {
                "success": False,
                "error": "No voice cloning models available"
            }
        
        model_name = xtts_models[0]
        return await self.synthesize(
            text=text,
            language=language,
            model_preference=model_name,
            speaker_wav=reference_audio
        )
    
    async def unload_model(self, model_name: str):
        """Unload a model from memory"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            logger.info(f"Unloaded TTS model: {model_name}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up TTS Engine...")
        self.loaded_models.clear()
        logger.info("✅ TTS Engine cleanup complete")
