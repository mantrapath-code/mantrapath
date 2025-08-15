"""
OpenAI Whisper Speech-to-Text Engine
Enterprise-grade implementation with multilingual support
"""
import asyncio
import logging
import tempfile
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime

from core.base_engine import BaseSTTEngine, voice_engine
from core.models import AudioData, STTResult, WordTiming, AudioFormat
from core.exceptions import STTEngineError, UnsupportedLanguageError
from config.language_config import SUPPORTED_LANGUAGES, get_language_info

logger = logging.getLogger(__name__)

@voice_engine("whisper", "stt")
class WhisperSTTEngine(BaseSTTEngine):
    """OpenAI Whisper Speech-to-Text Engine implementation"""
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.model_size = config.get("model_size", "base")
        self.api_key = config.get("openai_api_key", "")
        self.local_model = None
        
    def initialize(self, **kwargs) -> None:
        """Initialize Whisper engine"""
        try:
            # Try to import and initialize whisper
            if self.api_key:
                # Use OpenAI API
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                self.use_api = True
                logger.info("Whisper engine initialized with OpenAI API")
            else:
                # Use local whisper model
                import whisper
                self.local_model = whisper.load_model(self.model_size)
                self.use_api = False
                logger.info(f"Whisper engine initialized with local model: {self.model_size}")
            
            self.is_initialized = True
            
        except ImportError as e:
            raise STTEngineError(f"Failed to import Whisper dependencies: {e}", "whisper")
        except Exception as e:
            raise STTEngineError(f"Failed to initialize Whisper engine: {e}", "whisper")
    
    def health_check(self) -> Dict[str, Any]:
        """Check Whisper engine health"""
        try:
            if self.use_api and self.client:
                # For API, we can just check if client is configured
                status = "healthy"
                details = {"model": "whisper-1", "api_available": True}
            elif self.local_model:
                # For local model, check if model is loaded
                status = "healthy"
                details = {"model": self.model_size, "local_model_loaded": True}
            else:
                status = "unhealthy"
                details = {"error": "No model available"}
            
            return {
                "engine": "whisper",
                "status": status,
                "details": details,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "engine": "whisper",
                "status": "unhealthy", 
                "details": {"error": str(e)},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get Whisper supported languages"""
        # Whisper supports all our configured languages
        return list(SUPPORTED_LANGUAGES.keys())
    
    async def transcribe_audio(
        self, 
        audio_data: AudioData, 
        language: str = "en",
        **kwargs
    ) -> STTResult:
        """Transcribe audio using Whisper"""
        if not self.is_initialized:
            raise STTEngineError("Whisper engine not initialized", "whisper")
        
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language, self.get_supported_languages())
        
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(suffix=f".{audio_data.format.value}", delete=False) as temp_file:
                temp_file.write(audio_data.data)
                temp_path = temp_file.name
            
            try:
                if self.use_api:
                    result = await self._transcribe_with_api(temp_path, language, **kwargs)
                else:
                    result = await self._transcribe_with_local_model(temp_path, language, **kwargs)
                
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            raise STTEngineError(f"Transcription failed: {str(e)}", "whisper")
    
    async def _transcribe_with_api(
        self, 
        audio_path: str, 
        language: str,
        **kwargs
    ) -> STTResult:
        """Transcribe using OpenAI API"""
        try:
            with open(audio_path, "rb") as audio_file:
                # Prepare API parameters
                api_params = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "language": language,
                    "response_format": "verbose_json",
                    "timestamp_granularities": ["word"]
                }
                
                # Add optional parameters
                if kwargs.get("translate_to_english"):
                    # Use translation endpoint instead
                    transcript = await asyncio.get_event_loop().run_in_executor(
                        None, 
                        lambda: self.client.audio.translations.create(**{
                            k: v for k, v in api_params.items() 
                            if k not in ["language"]  # Translation doesn't need language param
                        })
                    )
                else:
                    transcript = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self.client.audio.transcriptions.create(**api_params)
                    )
                
                # Parse response
                return self._parse_whisper_response(transcript, language)
                
        except Exception as e:
            raise STTEngineError(f"OpenAI API transcription failed: {str(e)}", "whisper")
    
    async def _transcribe_with_local_model(
        self, 
        audio_path: str, 
        language: str,
        **kwargs
    ) -> STTResult:
        """Transcribe using local Whisper model"""
        try:
            # Prepare transcription options
            options = {
                "language": language if language != "auto" else None,
                "task": "translate" if kwargs.get("translate_to_english") else "transcribe",
                "word_timestamps": True
            }
            
            # Run transcription in thread pool
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.local_model.transcribe(audio_path, **options)
            )
            
            return self._parse_local_whisper_response(result, language)
            
        except Exception as e:
            raise STTEngineError(f"Local Whisper transcription failed: {str(e)}", "whisper")
    
    def _parse_whisper_response(self, response, language: str) -> STTResult:
        """Parse OpenAI API response to STTResult"""
        try:
            word_timings = []
            if hasattr(response, 'words') and response.words:
                word_timings = [
                    WordTiming(
                        word=word.word,
                        start_time=word.start,
                        end_time=word.end,
                        confidence=getattr(word, 'confidence', 0.9)
                    )
                    for word in response.words
                ]
            
            return STTResult(
                text=response.text,
                language=response.language if hasattr(response, 'language') else language,
                confidence=0.95,  # Whisper API doesn't provide overall confidence
                duration=response.duration if hasattr(response, 'duration') else 0.0,
                word_timings=word_timings,
                translated_text=response.text if hasattr(response, 'task') and response.task == 'translate' else None
            )
        except Exception as e:
            raise STTEngineError(f"Failed to parse Whisper API response: {str(e)}", "whisper")
    
    def _parse_local_whisper_response(self, result: Dict[str, Any], language: str) -> STTResult:
        """Parse local Whisper response to STTResult"""
        try:
            word_timings = []
            if "segments" in result:
                for segment in result["segments"]:
                    if "words" in segment:
                        for word_info in segment["words"]:
                            word_timings.append(WordTiming(
                                word=word_info["word"],
                                start_time=word_info["start"],
                                end_time=word_info["end"],
                                confidence=word_info.get("probability", 0.9)
                            ))
            
            # Calculate overall confidence from segments
            confidence = 0.9
            if "segments" in result and result["segments"]:
                confidences = [seg.get("avg_logprob", -1.0) for seg in result["segments"]]
                # Convert log probabilities to confidence scores
                confidence = min(1.0, max(0.0, (sum(confidences) / len(confidences) + 1.0) / 2.0))
            
            return STTResult(
                text=result["text"],
                language=result.get("language", language),
                confidence=confidence,
                duration=result.get("duration", 0.0),
                word_timings=word_timings,
                translated_text=result["text"] if result.get("task") == "translate" else None
            )
        except Exception as e:
            raise STTEngineError(f"Failed to parse local Whisper response: {str(e)}", "whisper")
    
    async def transcribe_stream(
        self, 
        audio_stream,
        language: str = "en",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Whisper doesn't support real-time streaming natively
        This implementation buffers audio and processes in chunks
        """
        if not self.is_initialized:
            raise STTEngineError("Whisper engine not initialized", "whisper")
        
        # Note: This is a simplified implementation
        # Real streaming would require more sophisticated buffering
        buffer = b""
        chunk_duration = kwargs.get("chunk_duration", 3.0)  # 3 second chunks
        
        async for audio_chunk in audio_stream:
            buffer += audio_chunk
            
            # Process buffer when it reaches chunk duration
            # (This is a simplified example - real implementation would need proper audio segmentation)
            if len(buffer) >= chunk_duration * 16000 * 2:  # Assuming 16kHz, 16-bit audio
                try:
                    audio_data = AudioData(
                        data=buffer,
                        format=AudioFormat.WAV,
                        sample_rate=16000,
                        channels=1
                    )
                    
                    result = await self.transcribe_audio(audio_data, language, **kwargs)
                    yield result.text
                    buffer = b""
                    
                except Exception as e:
                    logger.warning(f"Streaming transcription chunk failed: {e}")
                    continue
    
    def supports_diarization(self) -> bool:
        """Whisper supports basic speaker identification"""
        return False  # Whisper doesn't have built-in diarization
    
    def supports_streaming(self) -> bool:
        """Whisper supports streaming with buffering"""
        return True
    
    def get_confidence_threshold(self) -> float:
        """Get Whisper confidence threshold"""
        return self.config.get("confidence_threshold", 0.7)
