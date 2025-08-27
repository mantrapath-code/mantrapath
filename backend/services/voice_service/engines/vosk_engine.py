"""
Vosk Speech-to-Text Engine
Lightweight local STT engine for real-time processing
"""
import logging
import io
import json
import asyncio
import tempfile
import os
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime

try:
    import vosk
    import soundfile as sf
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logging.warning("Vosk not available, falling back to mock mode")

from core.base_engine import BaseSTTEngine, voice_engine
from core.models import AudioData, STTResult, WordTiming, AudioFormat
from core.exceptions import EngineError, AudioValidationError, UnsupportedLanguageError

logger = logging.getLogger(__name__)

@voice_engine("vosk", "stt")
class VoskSTTEngine(BaseSTTEngine):
    """Vosk Speech-to-Text Engine for lightweight local processing"""
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        self.model = None
        self.rec = None
        self.model_path = config.get("model_path", "/models/vosk")
        self.sample_rate = config.get("sample_rate", 16000)
        self.language = config.get("language", "en")
        
        # Model paths for different languages
        self.model_paths = {
            "en": config.get("en_model_path", "/models/vosk/vosk-model-en-us-0.22"),
            "es": config.get("es_model_path", "/models/vosk/vosk-model-es-0.42"),
            "fr": config.get("fr_model_path", "/models/vosk/vosk-model-fr-0.39"),
            "de": config.get("de_model_path", "/models/vosk/vosk-model-de-0.21"),
            "ru": config.get("ru_model_path", "/models/vosk/vosk-model-ru-0.42"),
            "zh": config.get("zh_model_path", "/models/vosk/vosk-model-cn-0.22"),
        }
        
        super().__init__(config, **kwargs)
    
    def initialize(self, **kwargs) -> None:
        """Initialize Vosk engine"""
        try:
            if not VOSK_AVAILABLE:
                logger.warning("Vosk not available, using mock mode")
                self.is_initialized = False
                return
            
            # Try to load default language model
            model_path = self.model_paths.get(self.language, self.model_paths["en"])
            
            if not os.path.exists(model_path):
                logger.warning(f"Vosk model not found at {model_path}, trying alternative paths")
                # Try common installation paths
                alternative_paths = [
                    f"/usr/local/share/vosk-models/vosk-model-{self.language}",
                    f"./models/vosk/vosk-model-{self.language}",
                    f"./vosk-model-{self.language}"
                ]
                
                model_path = None
                for path in alternative_paths:
                    if os.path.exists(path):
                        model_path = path
                        break
                
                if not model_path:
                    logger.error(f"No Vosk model found for language {self.language}")
                    self.is_initialized = False
                    return
            
            logger.info(f"Loading Vosk model from: {model_path}")
            self.model = vosk.Model(model_path)
            self.rec = vosk.KaldiRecognizer(self.model, self.sample_rate)
            
            logger.info(f"Vosk STT Engine initialized successfully for language: {self.language}")
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Vosk engine: {e}")
            self.is_initialized = False
            self.model = None
            self.rec = None
    
    def health_check(self) -> Dict[str, Any]:
        """Check Vosk engine health"""
        try:
            if not self.is_initialized:
                return {
                    "engine": "vosk",
                    "status": "unhealthy",
                    "details": {"error": "Engine not initialized"},
                    "timestamp": datetime.now().isoformat()
                }
            
            # Test with a small audio snippet
            test_passed = True
            error_msg = None
            
            try:
                if self.rec:
                    # Create test audio (1 second of silence)
                    test_audio = np.zeros(self.sample_rate, dtype=np.int16)
                    test_audio_bytes = test_audio.tobytes()
                    
                    # Test recognition
                    self.rec.AcceptWaveform(test_audio_bytes)
                    result = self.rec.Result()
                    json.loads(result)  # Validate JSON format
                
            except Exception as e:
                test_passed = False
                error_msg = str(e)
            
            return {
                "engine": "vosk",
                "status": "healthy" if test_passed else "unhealthy",
                "details": {
                    "language": self.language,
                    "sample_rate": self.sample_rate,
                    "model_path": self.model_paths.get(self.language),
                    "error": error_msg
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "engine": "vosk",
                "status": "unhealthy",
                "details": {"error": str(e)},
                "timestamp": datetime.now().isoformat()
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get Vosk supported languages (based on available models)"""
        return list(self.model_paths.keys())
    
    async def transcribe_audio(
        self, 
        audio_data: AudioData, 
        language: str = "en",
        **kwargs
    ) -> STTResult:
        """Transcribe audio using Vosk"""
        
        try:
            if not self.is_initialized:
                raise EngineError("Vosk engine not initialized")
                
            # Check if language is supported
            if not self.is_language_supported(language):
                raise UnsupportedLanguageError(f"Language {language} not supported by Vosk")
            
            # Switch model if different language requested
            if language != self.language:
                await self._switch_language(language)
            
            # Process audio
            audio_array = await self._prepare_audio(audio_data)
            result = await self._transcribe_with_vosk(audio_array, language, **kwargs)
            
            # Add engine info
            result.engine_used = "vosk"
            return result
            
        except Exception as e:
            logger.error(f"Vosk transcription failed: {e}")
            if isinstance(e, (EngineError, UnsupportedLanguageError, AudioValidationError)):
                raise
            raise EngineError(f"Vosk transcription failed: {e}")
    
    async def _prepare_audio(self, audio_data: AudioData) -> np.ndarray:
        """Prepare audio data for Vosk processing"""
        try:
            # Save to temporary file for soundfile processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data.data)
                temp_file_path = temp_file.name
            
            try:
                # Load audio and resample to 16kHz (Vosk requirement)
                audio_array, sr = sf.read(temp_file_path)
                
                # Resample if necessary
                if sr != self.sample_rate:
                    try:
                        import librosa
                        audio_array = librosa.resample(audio_array, orig_sr=sr, target_sr=self.sample_rate)
                    except ImportError:
                        logger.warning(f"librosa not available, using audio at {sr}Hz instead of {self.sample_rate}Hz")
                
                # Convert to int16 format expected by Vosk
                if audio_array.dtype != np.int16:
                    audio_array = (audio_array * 32767).astype(np.int16)
                
                return audio_array
            
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise AudioValidationError(f"Failed to prepare audio: {e}")
    
    async def _switch_language(self, language: str) -> None:
        """Switch to a different language model"""
        try:
            model_path = self.model_paths.get(language)
            if not model_path or not os.path.exists(model_path):
                raise UnsupportedLanguageError(f"Model for language {language} not available")
            
            logger.info(f"Switching Vosk model to language: {language}")
            
            # Load new model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _load_model():
                model = vosk.Model(model_path)
                rec = vosk.KaldiRecognizer(model, self.sample_rate)
                return model, rec
            
            self.model, self.rec = await loop.run_in_executor(None, _load_model)
            self.language = language
            
            logger.info(f"Successfully switched to {language} model")
            
        except Exception as e:
            raise EngineError(f"Failed to switch language model: {e}")
    
    async def _transcribe_with_vosk(
        self, 
        audio_array: np.ndarray, 
        language: str,
        **kwargs
    ) -> STTResult:
        """Transcribe using Vosk"""
        try:
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _transcribe():
                # Reset recognizer
                self.rec.Reset()
                
                # Process audio in chunks
                chunk_size = 4000  # Process in smaller chunks for better real-time performance
                audio_bytes = audio_array.tobytes()
                
                partial_results = []
                for i in range(0, len(audio_bytes), chunk_size):
                    chunk = audio_bytes[i:i + chunk_size]
                    if self.rec.AcceptWaveform(chunk):
                        result = json.loads(self.rec.Result())
                        if result.get('text'):
                            partial_results.append(result)
                
                # Get final result
                final_result = json.loads(self.rec.FinalResult())
                
                return partial_results, final_result
            
            partial_results, final_result = await loop.run_in_executor(None, _transcribe)
            
            # Combine all text
            all_text_parts = []
            word_timings = []
            
            # Process partial results
            for result in partial_results:
                if result.get('text'):
                    all_text_parts.append(result['text'])
                    
                    # Extract word timings if available
                    if 'result' in result:
                        for word_info in result['result']:
                            word_timings.append(WordTiming(
                                word=word_info.get('word', ''),
                                start_time=word_info.get('start', 0.0),
                                end_time=word_info.get('end', 0.0),
                                confidence=word_info.get('conf', 0.8)
                            ))
            
            # Add final result
            if final_result.get('text'):
                all_text_parts.append(final_result['text'])
                
                if 'result' in final_result:
                    for word_info in final_result['result']:
                        word_timings.append(WordTiming(
                            word=word_info.get('word', ''),
                            start_time=word_info.get('start', 0.0),
                            end_time=word_info.get('end', 0.0),
                            confidence=word_info.get('conf', 0.8)
                        ))
            
            full_text = ' '.join(all_text_parts).strip()
            
            # Calculate average confidence
            avg_confidence = 0.8
            if word_timings:
                avg_confidence = sum(wt.confidence for wt in word_timings) / len(word_timings)
            
            return STTResult(
                text=full_text,
                language=language,
                confidence=avg_confidence,
                word_timings=word_timings,
                processing_time_ms=0,  # Will be set by service
                alternatives=[],
                metadata={
                    "engine": "vosk",
                    "sample_rate": self.sample_rate,
                    "partial_results_count": len(partial_results),
                    "model_path": self.model_paths.get(language)
                }
            )
            
        except Exception as e:
            raise EngineError(f"Vosk transcription failed: {e}")
    
    def supports_streaming(self) -> bool:
        """Vosk supports real-time streaming"""
        return True
    
    def supports_speaker_diarization(self) -> bool:
        """Vosk doesn't support speaker diarization"""
        return False
    
    async def stream_transcribe(self, audio_stream) -> AsyncIterator[Dict[str, Any]]:
        """Stream transcription for real-time processing"""
        try:
            if not self.is_initialized:
                raise EngineError("Vosk engine not initialized")
            
            self.rec.Reset()
            
            async for audio_chunk in audio_stream:
                # Process audio chunk
                if isinstance(audio_chunk, bytes):
                    chunk_bytes = audio_chunk
                else:
                    # Convert numpy array to bytes
                    chunk_bytes = audio_chunk.astype(np.int16).tobytes()
                
                if self.rec.AcceptWaveform(chunk_bytes):
                    result = json.loads(self.rec.Result())
                    if result.get('text'):
                        yield {
                            "type": "final",
                            "text": result['text'],
                            "confidence": 0.8,
                            "is_partial": False
                        }
                else:
                    partial = json.loads(self.rec.PartialResult())
                    if partial.get('partial'):
                        yield {
                            "type": "partial",
                            "text": partial['partial'],
                            "confidence": 0.6,
                            "is_partial": True
                        }
            
            # Get final result
            final_result = json.loads(self.rec.FinalResult())
            if final_result.get('text'):
                yield {
                    "type": "final",
                    "text": final_result['text'],
                    "confidence": 0.8,
                    "is_partial": False
                }
                
        except Exception as e:
            logger.error(f"Vosk streaming failed: {e}")
            yield {
                "type": "error",
                "error": str(e),
                "is_partial": False
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "engine": "vosk",
            "language": self.language,
            "sample_rate": self.sample_rate,
            "model_path": self.model_paths.get(self.language),
            "initialized": self.is_initialized,
            "streaming_support": self.supports_streaming(),
            "diarization_support": self.supports_speaker_diarization(),
            "available_languages": list(self.model_paths.keys())
        }
