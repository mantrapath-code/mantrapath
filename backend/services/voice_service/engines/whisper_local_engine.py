"""
Local Whisper Speech-to-Text Engine
Self-hosted implementation using local Whisper models
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
    import whisper
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logging.warning("Whisper not available, falling back to mock mode")

from core.base_engine import BaseSTTEngine, voice_engine
from core.models import AudioData, STTResult, WordTiming, AudioFormat, EmotionType
from core.exceptions import EngineError, AudioValidationError, UnsupportedLanguageError
from config.language_config import is_language_supported, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

@voice_engine("whisper_local", "stt")
class LocalWhisperEngine(BaseSTTEngine):
    """Local Whisper Speech-to-Text Engine"""
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        self.model = None
        self.fast_model = None
        self.model_size = config.get("model_size", "medium")  # tiny, base, small, medium, large, large-v2, large-v3
        self.device = config.get("device", "auto")  # auto, cpu, cuda
        self.compute_type = config.get("compute_type", "float16")  # float16, float32, int8
        self.use_faster_whisper = config.get("use_faster_whisper", True)
        self.beam_size = config.get("beam_size", 5)
        self.temperature = config.get("temperature", 0.0)
        
        super().__init__(config, **kwargs)
    
    def initialize(self, **kwargs) -> None:
        """Initialize Local Whisper engine"""
        try:
            if not WHISPER_AVAILABLE:
                logger.warning("Whisper not available, using mock mode")
                self.is_initialized = False
                return
            
            # Auto-detect device
            if self.device == "auto":
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Auto-detected device: {self.device}")
            
            if self.use_faster_whisper:
                # Use faster-whisper for better performance
                logger.info(f"Loading faster-whisper model: {self.model_size}")
                self.fast_model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                logger.info(f"Faster-Whisper model loaded successfully on {self.device}")
            else:
                # Use original OpenAI Whisper
                logger.info(f"Loading OpenAI Whisper model: {self.model_size}")
                self.model = whisper.load_model(self.model_size, device=self.device)
                logger.info(f"OpenAI Whisper model loaded successfully on {self.device}")
            
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Local Whisper engine: {e}")
            self.is_initialized = False
            self.model = None
            self.fast_model = None
    
    def health_check(self) -> Dict[str, Any]:
        """Check Local Whisper engine health"""
        try:
            if not self.is_initialized:
                return {
                    "engine": "whisper_local",
                    "status": "unhealthy",
                    "details": {"error": "Engine not initialized"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test with a small audio snippet
            test_passed = True
            error_msg = None
            
            try:
                # Create a simple test (1 second of silence)
                import numpy as np
                test_audio = np.zeros(16000, dtype=np.float32)  # 1 second at 16kHz
                
                if self.use_faster_whisper and self.fast_model:
                    segments, _ = self.fast_model.transcribe(test_audio, beam_size=1)
                    list(segments)  # Force computation
                elif self.model:
                    self.model.transcribe(test_audio)
                
            except Exception as e:
                test_passed = False
                error_msg = str(e)
            
            return {
                "engine": "whisper_local",
                "status": "healthy" if test_passed else "unhealthy",
                "details": {
                    "model_size": self.model_size,
                    "device": self.device,
                    "use_faster_whisper": self.use_faster_whisper,
                    "error": error_msg
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "engine": "whisper_local",
                "status": "unhealthy",
                "details": {"error": str(e)},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get Local Whisper supported languages"""
        return list(SUPPORTED_LANGUAGES.keys())
    
    async def transcribe_audio(
        self, 
        audio_data: AudioData, 
        language: str = "en",
        **kwargs
    ) -> STTResult:
        """Transcribe audio using Local Whisper"""
        
        try:
            if not self.is_initialized:
                raise EngineError("Local Whisper engine not initialized")
                
            # Check if language is supported
            if not self.is_language_supported(language):
                raise UnsupportedLanguageError(f"Language {language} not supported by Local Whisper")
            
            # Convert audio data to numpy array
            audio_array = await self._prepare_audio(audio_data)
            
            # Transcribe with appropriate engine
            if self.use_faster_whisper and self.fast_model:
                result = await self._transcribe_with_faster_whisper(audio_array, language, **kwargs)
            elif self.model:
                result = await self._transcribe_with_openai_whisper(audio_array, language, **kwargs)
            else:
                raise EngineError("No Whisper model available")
            
            # Add engine info
            result.engine_used = "whisper_local"
            return result
            
        except Exception as e:
            logger.error(f"Local Whisper transcription failed: {e}")
            if isinstance(e, (EngineError, UnsupportedLanguageError, AudioValidationError)):
                raise
            raise EngineError(f"Local Whisper transcription failed: {e}")
    
    async def _prepare_audio(self, audio_data: AudioData) -> np.ndarray:
        """Prepare audio data for Whisper processing"""
        try:
            # Save to temporary file for librosa processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data.data)
                temp_file_path = temp_file.name
            
            try:
                import librosa
                # Load audio and resample to 16kHz (Whisper requirement)
                audio_array, sr = librosa.load(temp_file_path, sr=16000, mono=True)
                return audio_array.astype(np.float32)
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise AudioValidationError(f"Failed to prepare audio: {e}")
    
    async def _transcribe_with_faster_whisper(
        self, 
        audio_array: np.ndarray, 
        language: str,
        **kwargs
    ) -> STTResult:
        """Transcribe using faster-whisper"""
        try:
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _transcribe():
                segments, info = self.fast_model.transcribe(
                    audio_array,
                    language=language if language != "auto" else None,
                    beam_size=self.beam_size,
                    temperature=self.temperature,
                    word_timestamps=True,
                    vad_filter=True  # Voice Activity Detection
                )
                return segments, info
            
            segments, info = await loop.run_in_executor(None, _transcribe)
            
            # Process segments
            full_text = ""
            word_timings = []
            
            for segment in segments:
                full_text += segment.text
                
                # Add word timings if available
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        word_timings.append(WordTiming(
                            word=word.word,
                            start_time=word.start,
                            end_time=word.end,
                            confidence=getattr(word, 'probability', 0.9)
                        ))
            
            return STTResult(
                text=full_text.strip(),
                language=info.language,
                confidence=getattr(info, 'language_probability', 0.9),
                word_timings=word_timings,
                processing_time_ms=0,  # Will be set by service
                alternatives=[],
                metadata={
                    "model": self.model_size,
                    "device": self.device,
                    "duration": info.duration,
                    "language_probability": getattr(info, 'language_probability', 0.9)
                }
            )
            
        except Exception as e:
            raise EngineError(f"Faster-Whisper transcription failed: {e}")
    
    async def _transcribe_with_openai_whisper(
        self, 
        audio_array: np.ndarray, 
        language: str,
        **kwargs
    ) -> STTResult:
        """Transcribe using original OpenAI Whisper"""
        try:
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _transcribe():
                return self.model.transcribe(
                    audio_array,
                    language=language if language != "auto" else None,
                    temperature=self.temperature,
                    word_timestamps=True
                )
            
            result = await loop.run_in_executor(None, _transcribe)
            
            # Process word timings
            word_timings = []
            if 'segments' in result:
                for segment in result['segments']:
                    if 'words' in segment:
                        for word in segment['words']:
                            word_timings.append(WordTiming(
                                word=word['word'],
                                start_time=word['start'],
                                end_time=word['end'],
                                confidence=getattr(word, 'probability', 0.9)
                            ))
            
            return STTResult(
                text=result['text'].strip(),
                language=result.get('language', language),
                confidence=0.9,  # OpenAI Whisper doesn't provide confidence
                word_timings=word_timings,
                processing_time_ms=0,  # Will be set by service
                alternatives=[],
                metadata={
                    "model": self.model_size,
                    "device": self.device,
                    "segments_count": len(result.get('segments', []))
                }
            )
            
        except Exception as e:
            raise EngineError(f"OpenAI Whisper transcription failed: {e}")
    
    def supports_streaming(self) -> bool:
        """Local Whisper supports streaming with faster-whisper"""
        return self.use_faster_whisper and self.fast_model is not None
    
    def supports_speaker_diarization(self) -> bool:
        """Local Whisper doesn't support speaker diarization natively"""
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "use_faster_whisper": self.use_faster_whisper,
            "initialized": self.is_initialized,
            "streaming_support": self.supports_streaming(),
            "diarization_support": self.supports_speaker_diarization()
        }
