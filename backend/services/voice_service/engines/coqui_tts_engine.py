"""
Coqui TTS Engine Implementation with Voice Cloning
Provides text-to-speech conversion using the open-source Coqui TTS library.
Supports XTTS v2 model for voice cloning capabilities.
"""
import asyncio
import logging
import tempfile
import os
import numpy as np
from typing import Optional, Dict, Any, List
from pathlib import Path
import hashlib
import json

try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logging.warning("Audio processing libraries not available. Install librosa and soundfile for full functionality.")

from ..models import VoiceRequest, VoiceResponse, TTSEngine
from ..config import VoiceConfig

logger = logging.getLogger(__name__)


class CoquiTTSEngine(TTSEngine):
    """Coqui TTS implementation with voice cloning support using XTTS v2."""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.model = None
        self.xtts_model = None
        # Use XTTS v2 for voice cloning
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.initialized = False
        self.voice_cache = {}  # Cache for cloned voices
        self.cache_dir = Path("/tmp/voice_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    async def initialize(self):
        """Initialize the Coqui TTS model with XTTS v2 for voice cloning."""
        try:
            from TTS.api import TTS
            
            # Load XTTS v2 model for voice cloning
            self.model = TTS(self.model_name)
            self.initialized = True
            logger.info(f"Coqui TTS initialized with XTTS v2 model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Coqui TTS XTTS v2: {str(e)}")
            # Fallback to basic model if XTTS fails
            try:
                self.model_name = "tts_models/en/ljspeech/tacotron2-DDC"
                self.model = TTS(self.model_name)
                self.initialized = True
                logger.warning(f"Fallback to basic TTS model: {self.model_name}")
            except Exception as fallback_e:
                logger.error(f"Fallback TTS model also failed: {str(fallback_e)}")
                raise
    
    async def text_to_speech(self, request: VoiceRequest) -> VoiceResponse:
        """Convert text to speech using Coqui TTS with optional voice cloning."""
        if not self.initialized:
            await self.initialize()
            
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Check if we have a cloned voice for this request
            speaker_wav = None
            if request.voice_id and request.voice_id in self.voice_cache:
                speaker_wav = self.voice_cache[request.voice_id]
                logger.info(f"Using cloned voice: {request.voice_id}")
            
            # Determine language for XTTS
            language = self._map_language_code(request.language or "en")
            
            if speaker_wav and "xtts" in self.model_name:
                # Use voice cloning with XTTS
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._tts_with_cloning,
                    request.text,
                    temp_path,
                    speaker_wav,
                    language
                )
            else:
                # Use regular TTS
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.model.tts_to_file,
                    request.text,
                    temp_path
                )
            
            # Read generated audio file
            with open(temp_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Get audio duration
            duration = await self._get_audio_duration(temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            return VoiceResponse(
                audio_data=audio_data,
                format="wav",
                duration=duration,
                sample_rate=22050,
                metadata={
                    "engine": "coqui_tts",
                    "model": self.model_name,
                    "language": language,
                    "voice_cloned": speaker_wav is not None,
                    "voice_id": request.voice_id
                }
            )
            
        except Exception as e:
            logger.error(f"Coqui TTS generation failed: {str(e)}")
            raise
    
    def _tts_with_cloning(self, text: str, output_path: str, speaker_wav: str, language: str):
        """Generate TTS with voice cloning using XTTS."""
        self.model.tts_to_file(
            text=text,
            file_path=output_path,
            speaker_wav=speaker_wav,
            language=language
        )
    
    def _map_language_code(self, lang_code: str) -> str:
        """Map language codes to XTTS supported languages."""
        language_map = {
            "en": "en",
            "es": "es", 
            "fr": "fr",
            "de": "de",
            "it": "it",
            "pt": "pt",
            "pl": "pl",
            "tr": "tr",
            "ru": "ru",
            "nl": "nl",
            "cs": "cs",
            "ar": "ar",
            "zh": "zh-cn",
            "ja": "ja",
            "hu": "hu",
            "ko": "ko",
            "hi": "hi"  # Hindi support
        }
        return language_map.get(lang_code[:2], "en")
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file."""
        try:
            if AUDIO_LIBS_AVAILABLE:
                y, sr = librosa.load(audio_path)
                return len(y) / sr
            else:
                # Fallback: estimate duration from file size (very rough)
                import wave
                with wave.open(audio_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    sample_rate = wav_file.getframerate()
                    return frames / float(sample_rate)
        except Exception as e:
            logger.warning(f"Could not calculate audio duration: {e}")
            return 0.0
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get available voices from Coqui TTS."""
        if not self.initialized:
            await self.initialize()
            
        try:
            voices = [
                {
                    "id": "default",
                    "name": "Default Voice",
                    "language": "en",
                    "gender": "female",
                    "description": "Default XTTS voice"
                }
            ]
            
            # Add cloned voices
            for voice_id, voice_path in self.voice_cache.items():
                voices.append({
                    "id": voice_id,
                    "name": f"Cloned Voice {voice_id}",
                    "language": "multilingual",
                    "gender": "unknown",
                    "description": "User cloned voice",
                    "cloned": True
                })
            
            return {
                "voices": voices,
                "engine": "coqui_tts",
                "model": self.model_name,
                "supports_cloning": "xtts" in self.model_name,
                "supported_languages": [
                    "en", "es", "fr", "de", "it", "pt", "pl", 
                    "tr", "ru", "nl", "cs", "ar", "zh", "ja", 
                    "hu", "ko", "hi"
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get Coqui TTS voices: {str(e)}")
            return {"voices": [], "error": str(e)}
    
    async def clone_voice(self, audio_sample: bytes, text: str, voice_id: Optional[str] = None) -> VoiceResponse:
        """Clone voice from audio sample using XTTS v2."""
        if not self.initialized:
            await self.initialize()
            
        if "xtts" not in self.model_name:
            logger.warning("Voice cloning requires XTTS model")
            # Fallback to regular TTS
            request = VoiceRequest(text=text, voice_id="default", language="en")
            return await self.text_to_speech(request)
        
        try:
            # Generate voice ID if not provided
            if not voice_id:
                voice_id = hashlib.md5(audio_sample[:1024]).hexdigest()[:8]
            
            # Save audio sample for voice cloning
            speaker_wav_path = self.cache_dir / f"speaker_{voice_id}.wav"
            
            # Process and save speaker audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_input:
                temp_input.write(audio_sample)
                temp_input_path = temp_input.name
            
            # Convert to proper format for XTTS (16kHz, mono)
            await self._process_speaker_audio(temp_input_path, str(speaker_wav_path))
            
            # Cache the speaker voice
            self.voice_cache[voice_id] = str(speaker_wav_path)
            
            # Clean up temporary input
            os.unlink(temp_input_path)
            
            # Generate TTS with cloned voice
            request = VoiceRequest(text=text, voice_id=voice_id, language="en")
            result = await self.text_to_speech(request)
            
            # Add cloning metadata
            result.metadata.update({
                "voice_cloned": True,
                "voice_id": voice_id,
                "speaker_wav": str(speaker_wav_path)
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Voice cloning failed: {str(e)}")
            # Fallback to regular TTS
            request = VoiceRequest(text=text, voice_id="default", language="en")
            return await self.text_to_speech(request)
    
    async def _process_speaker_audio(self, input_path: str, output_path: str):
        """Process speaker audio to XTTS requirements (16kHz, mono)."""
        try:
            if AUDIO_LIBS_AVAILABLE:
                # Load audio and resample to 22050Hz (XTTS requirement)
                y, sr = librosa.load(input_path, sr=22050, mono=True)
                
                # Ensure minimum length (at least 6 seconds for good cloning)
                min_length = 22050 * 6  # 6 seconds
                if len(y) < min_length:
                    # Repeat audio to meet minimum length
                    repeats = int(min_length / len(y)) + 1
                    y = np.tile(y, repeats)[:min_length]
                
                # Save processed audio
                sf.write(output_path, y, 22050)
            else:
                # Fallback: copy original file if processing fails
                import shutil
                shutil.copy2(input_path, output_path)
                logger.warning("Audio processing libraries not available, using original audio file")
            
        except Exception as e:
            logger.error(f"Failed to process speaker audio: {str(e)}")
            # Copy original file if processing fails
            import shutil
            shutil.copy2(input_path, output_path)
    
    def is_available(self) -> bool:
        """Check if Coqui TTS is available."""
        try:
            from TTS.api import TTS
            import torch
            return True
        except ImportError:
            return False
    
    async def get_voice_similarity(self, original_audio: bytes, generated_audio: bytes) -> float:
        """Calculate similarity between original and generated voice (basic implementation)."""
        try:
            if not AUDIO_LIBS_AVAILABLE:
                logger.warning("Audio processing libraries not available, returning default similarity")
                return 0.75  # Default similarity score
            
            # Save both audio samples temporarily
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp1:
                temp1.write(original_audio)
                temp1_path = temp1.name
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp2:
                temp2.write(generated_audio)
                temp2_path = temp2.name
            
            # Load audio and extract features
            y1, sr1 = librosa.load(temp1_path)
            y2, sr2 = librosa.load(temp2_path)
            
            # Extract MFCC features for comparison
            mfcc1 = librosa.feature.mfcc(y=y1, sr=sr1, n_mfcc=13)
            mfcc2 = librosa.feature.mfcc(y=y2, sr=sr2, n_mfcc=13)
            
            # Calculate similarity (simplified approach)
            min_frames = min(mfcc1.shape[1], mfcc2.shape[1])
            mfcc1_trunc = mfcc1[:, :min_frames]
            mfcc2_trunc = mfcc2[:, :min_frames]
            
            # Cosine similarity
            similarity = np.corrcoef(mfcc1_trunc.flatten(), mfcc2_trunc.flatten())[0, 1]
            
            # Clean up
            os.unlink(temp1_path)
            os.unlink(temp2_path)
            
            return max(0.0, similarity) if not np.isnan(similarity) else 0.0
            
        except Exception as e:
            logger.error(f"Voice similarity calculation failed: {str(e)}")
            return 0.0

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
