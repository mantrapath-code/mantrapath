"""
Coqui TTS (Text-to-Speech) Engine
Self-hosted implementation using Coqui TTS models
"""
import logging
import io
import tempfile
import os
import asyncio
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

try:
    from TTS.api import TTS
    from TTS.utils.manage import ModelManager
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    logging.warning("Coqui TTS not available, falling back to mock mode")

from core.base_engine import BaseTTSEngine, voice_engine
from core.models import AudioData, AudioFormat
from core.exceptions import EngineError, AudioProcessingError, UnsupportedLanguageError

logger = logging.getLogger(__name__)

@voice_engine("coqui_local", "tts")
class CoquiTTSEngine(BaseTTSEngine):
    """Coqui TTS Engine for local text-to-speech synthesis"""
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        self.tts = None
        self.model_name = config.get("model_name", "tts_models/multilingual/multi-dataset/xtts_v2")
        self.device = config.get("device", "auto")  # auto, cpu, cuda
        self.vocoder_path = config.get("vocoder_path", None)
        self.use_cuda = config.get("use_cuda", True)
        
        # Voice settings
        self.default_speaker = config.get("default_speaker", "Claribel Dervla")
        self.speaker_wav_path = config.get("speaker_wav_path", None)  # For voice cloning
        
        # Audio settings
        self.sample_rate = config.get("sample_rate", 22050)
        self.emotion = config.get("emotion", "neutral")
        self.speed = config.get("speed", 1.0)
        
        super().__init__(config, **kwargs)
    
    def initialize(self, **kwargs) -> None:
        """Initialize Coqui TTS engine"""
        try:
            if not COQUI_AVAILABLE:
                logger.warning("Coqui TTS not available, using mock mode")
                self.is_initialized = False
                return
            
            # Auto-detect device
            if self.device == "auto":
                try:
                    import torch
                    self.device = "cuda" if torch.cuda.is_available() and self.use_cuda else "cpu"
                except ImportError:
                    self.device = "cpu"
                logger.info(f"Auto-detected device: {self.device}")
            
            # Initialize TTS model
            logger.info(f"Loading Coqui TTS model: {self.model_name}")
            
            gpu = self.device == "cuda"
            self.tts = TTS(
                model_name=self.model_name,
                vocoder_path=self.vocoder_path,
                gpu=gpu
            )
            
            logger.info(f"Coqui TTS model loaded successfully on {self.device}")
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Coqui TTS engine: {e}")
            self.is_initialized = False
            self.tts = None
    
    def health_check(self) -> Dict[str, Any]:
        """Check Coqui TTS engine health"""
        try:
            if not self.is_initialized:
                return {
                    "engine": "coqui_local",
                    "status": "unhealthy",
                    "details": {"error": "Engine not initialized"},
                    "timestamp": datetime.now().isoformat()
                }
            
            # Test with a simple synthesis
            test_passed = True
            error_msg = None
            
            try:
                test_text = "Hello world"
                if self.tts:
                    # Create a small test synthesis
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_file:
                        self.tts.tts_to_file(
                            text=test_text,
                            file_path=temp_file.name,
                            speaker=self.default_speaker
                        )
                
            except Exception as e:
                test_passed = False
                error_msg = str(e)
            
            return {
                "engine": "coqui_local",
                "status": "healthy" if test_passed else "unhealthy",
                "details": {
                    "model_name": self.model_name,
                    "device": self.device,
                    "sample_rate": self.sample_rate,
                    "error": error_msg
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "engine": "coqui_local",
                "status": "unhealthy",
                "details": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get Coqui TTS supported languages"""
        # XTTS-v2 supports these languages natively
        return [
            "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", 
            "nl", "cs", "ar", "zh", "ja", "hu", "ko", "hi"
        ]
    
    async def synthesize_speech(
        self, 
        text: str, 
        language: str = "en",
        voice_id: Optional[str] = None,
        **kwargs
    ) -> AudioData:
        """Synthesize speech using Coqui TTS"""
        
        try:
            if not self.is_initialized:
                raise EngineError("Coqui TTS engine not initialized")
                
            # Check if language is supported
            if not self.is_language_supported(language):
                raise UnsupportedLanguageError(f"Language {language} not supported by Coqui TTS")
            
            # Validate text
            if not text or len(text.strip()) == 0:
                raise AudioProcessingError("Text cannot be empty")
            
            if len(text) > 5000:  # Reasonable limit for TTS
                raise AudioProcessingError("Text too long for synthesis")
            
            # Use provided voice or default
            speaker = voice_id or self.default_speaker
            
            # Get additional parameters
            speed = kwargs.get("speed", self.speed)
            emotion = kwargs.get("emotion", self.emotion)
            
            # Run synthesis in thread pool to avoid blocking
            audio_data = await self._synthesize_audio(text, language, speaker, speed, emotion)
            
            # Add engine info
            audio_data.engine_used = "coqui_local"
            return audio_data
            
        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}")
            if isinstance(e, (EngineError, UnsupportedLanguageError, AudioProcessingError)):
                raise
            raise EngineError(f"Coqui TTS synthesis failed: {e}")
    
    async def _synthesize_audio(
        self, 
        text: str, 
        language: str, 
        speaker: str, 
        speed: float, 
        emotion: str
    ) -> AudioData:
        """Perform the actual TTS synthesis"""
        try:
            loop = asyncio.get_event_loop()
            
            def _synthesize():
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                try:
                    if self.speaker_wav_path:
                        # Voice cloning mode
                        self.tts.tts_to_file(
                            text=text,
                            file_path=temp_path,
                            speaker_wav=self.speaker_wav_path,
                            language=language,
                            speed=speed
                        )
                    else:
                        # Standard synthesis with predefined voices
                        self.tts.tts_to_file(
                            text=text,
                            file_path=temp_path,
                            speaker=speaker,
                            language=language,
                            speed=speed
                        )
                    
                    # Read the generated audio file
                    with open(temp_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    return audio_bytes
                
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
            
            # Execute synthesis in thread pool
            audio_bytes = await loop.run_in_executor(None, _synthesize)
            
            # Calculate duration (approximate)
            duration = self._estimate_duration(text, speed)
            
            return AudioData(
                data=audio_bytes,
                format=AudioFormat.WAV,
                sample_rate=self.sample_rate,
                channels=1,
                duration=duration,
                file_size=len(audio_bytes),
                metadata={
                    "text_length": len(text),
                    "speaker": speaker,
                    "language": language,
                    "speed": speed,
                    "emotion": emotion,
                    "model": self.model_name
                }
            )
            
        except Exception as e:
            raise EngineError(f"Audio synthesis failed: {e}")
    
    def _estimate_duration(self, text: str, speed: float) -> float:
        """Estimate audio duration based on text length and speed"""
        # Rough estimation: ~150 words per minute at normal speed
        words = len(text.split())
        base_duration = (words / 150) * 60  # seconds
        return base_duration / speed
    
    async def get_available_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        """Get available voices for a language"""
        try:
            if not self.is_initialized:
                return []
            
            # XTTS-v2 has predefined speakers
            speakers = [
                "Claribel Dervla", "Daisy Studious", "Gracie Wise", "Tammie Ema",
                "Alison Dietlinde", "Ana Florence", "Annmarie Nele", "Asya Anara",
                "Brenda Stern", "Gitta Nikolina", "Henriette Usha", "Sofia Hellen",
                "Tammy Grit", "Tanja Adelina", "Vjollca Johnnie", "Andrew Chipper",
                "Badr Odhiambo", "Dionisio Schuyler", "Royston Min", "Viktor Eka",
                "Abrahan Mack", "Adde Michal", "Baldur Sanjin", "Craig Gutsy",
                "Damien Black", "Gilberto Mathias", "Ilkin Urbano", "Kazuhiko Atallah",
                "Ludvig Milivoj", "Suad Qasim", "Torcull Diarmuid", "Viktor Menelaos",
                "Zacharie Aimilios"
            ]
            
            voices = []
            for speaker in speakers:
                voices.append({
                    "id": speaker,
                    "name": speaker,
                    "language": language,
                    "gender": "unknown",  # Would need gender detection
                    "sample_rate": self.sample_rate,
                    "supports_emotions": True,
                    "supports_speed_control": True
                })
            
            return voices
            
        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            return []
    
    def supports_voice_cloning(self) -> bool:
        """Coqui TTS supports voice cloning"""
        return True
    
    def supports_custom_voices(self) -> bool:
        """Coqui TTS supports custom voice training"""
        return True
    
    def supports_emotions(self) -> bool:
        """Coqui TTS supports emotional expression"""
        return True
    
    def supports_streaming(self) -> bool:
        """Coqui TTS doesn't support streaming by default"""
        return False
    
    async def clone_voice(self, speaker_audio_path: str, voice_name: str) -> bool:
        """Clone a voice from audio sample"""
        try:
            if not os.path.exists(speaker_audio_path):
                raise FileNotFoundError(f"Speaker audio file not found: {speaker_audio_path}")
            
            # For XTTS-v2, we just need to store the speaker audio path
            # The actual cloning happens during synthesis
            self.speaker_wav_path = speaker_audio_path
            
            logger.info(f"Voice cloning set up for {voice_name} using {speaker_audio_path}")
            return True
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "sample_rate": self.sample_rate,
            "initialized": self.is_initialized,
            "voice_cloning_support": self.supports_voice_cloning(),
            "streaming_support": self.supports_streaming(),
            "emotions_support": self.supports_emotions(),
            "supported_languages": self.get_supported_languages()
        }
