"""
Shared Models Service Client
Provides unified access to Models Service capabilities across all services.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List, Union, Type
import structlog
import json
from pathlib import Path
import types

logger = structlog.get_logger(__name__)

class ModelsServiceClient:
    """Client for interacting with Models Service (Port 8085)"""
    
    def __init__(self, base_url: str = "http://models-service:8080"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        
    async def __aenter__(self):
        """Async context manager entry"""
        return self
        
    async def __aexit__(self, exc_type: Optional[Type[BaseException]], 
                       exc_val: Optional[BaseException], 
                       exc_tb: Optional[types.TracebackType]) -> None:
        """Async context manager exit"""
        await self.client.aclose()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    # Health & Status Methods
    async def check_health(self) -> bool:
        """Check if Models Service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning("Models Service health check failed", error=str(e))
            return False

    async def get_service_status(self) -> Dict[str, Any]:
        """Get detailed Models Service status"""
        try:
            response = await self.client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get Models Service status", error=str(e))
            raise

    async def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models for download"""
        try:
            response = await self.client.get(f"{self.base_url}/models/available")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get available models", error=str(e))
            raise

    async def get_loaded_models(self) -> Dict[str, Any]:
        """Get list of currently loaded models"""
        try:
            response = await self.client.get(f"{self.base_url}/models/loaded")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("Failed to get loaded models", error=str(e))
            raise

    # Speech-to-Text Methods
    async def transcribe_audio(
        self,
        audio_data: Union[bytes, str, Path],
        language: str = "auto",
        model: str = "whisper_base",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Models Service STT
        
        Args:
            audio_data: Audio data as bytes, file path, or Path object
            language: Language code (auto for detection)
            model: STT model to use
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Handle different audio input types
            if isinstance(audio_data, (str, Path)):
                with open(audio_data, 'rb') as f:
                    audio_bytes = f.read()
                filename = Path(audio_data).name
            else:
                audio_bytes = audio_data
                filename = kwargs.get('filename', 'audio.wav')
            
            files = {"audio": (filename, audio_bytes, "audio/wav")}
            data = {
                "language": language,
                "model": model,
                **{k: v for k, v in kwargs.items() if k != 'filename'}
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/stt/transcribe",
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info("STT transcription successful", 
                       model=model, language=language, 
                       text_length=len(result.get('text', '')))
            return result
            
        except Exception as e:
            logger.error("STT transcription failed", 
                        model=model, language=language, error=str(e))
            raise

    # Text-to-Speech Methods
    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        voice: str = "default",
        model: str = "espeak",
        format: str = "wav",
        **kwargs
    ) -> bytes:
        """
        Synthesize speech from text using Models Service TTS
        
        Args:
            text: Text to synthesize
            language: Language code
            voice: Voice to use
            model: TTS model to use
            format: Audio format (wav, mp3, etc.)
            **kwargs: Additional parameters
            
        Returns:
            Audio data as bytes
        """
        try:
            data = {
                "text": text,
                "language": language,
                "voice": voice,
                "model": model,
                "format": format,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/tts/synthesize",
                json=data
            )
            response.raise_for_status()
            
            logger.info("TTS synthesis successful",
                       model=model, language=language, 
                       text_length=len(text), 
                       audio_size=len(response.content))
            return response.content
            
        except Exception as e:
            logger.error("TTS synthesis failed",
                        model=model, language=language, error=str(e))
            raise

    # Natural Language Processing Methods
    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        engine: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Translate text using Models Service NLP
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            engine: Translation engine to use
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with translation results
        """
        try:
            data = {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "engine": engine,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/nlp/translate",
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info("Translation successful",
                       source_lang=source_lang, target_lang=target_lang,
                       original_length=len(text),
                       translated_length=len(result.get('translated_text', '')))
            return result
            
        except Exception as e:
            logger.error("Translation failed",
                        source_lang=source_lang, target_lang=target_lang, 
                        error=str(e))
            raise

    async def analyze_sentiment(
        self,
        text: str,
        language: str = "en",
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze sentiment using Models Service NLP
        
        Args:
            text: Text to analyze
            language: Language code
            model: Sentiment analysis model
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            data = {
                "text": text,
                "language": language,
                "model": model,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/nlp/sentiment",
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info("Sentiment analysis successful",
                       language=language, text_length=len(text),
                       sentiment=result.get('sentiment'))
            return result
            
        except Exception as e:
            logger.error("Sentiment analysis failed",
                        language=language, error=str(e))
            raise

    async def get_embeddings(
        self,
        text: str,
        language: str = "en",
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get text embeddings using Models Service NLP
        
        Args:
            text: Text to embed
            language: Language code
            model: Embedding model
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with embeddings
        """
        try:
            data = {
                "text": text,
                "language": language,
                "model": model,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/nlp/embeddings",
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info("Embeddings generation successful",
                       language=language, text_length=len(text),
                       embedding_dim=len(result.get('embeddings', [])))
            return result
            
        except Exception as e:
            logger.error("Embeddings generation failed",
                        language=language, error=str(e))
            raise

    # Model Management Methods
    async def download_model(
        self,
        model_name: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Download a model to Models Service
        
        Args:
            model_name: Name of model to download
            force: Force re-download if model exists
            
        Returns:
            Download status information
        """
        try:
            data = {
                "model_name": model_name,
                "force": force
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/models/download",
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info("Model download initiated",
                       model_name=model_name, status=result.get('status'))
            return result
            
        except Exception as e:
            logger.error("Model download failed",
                        model_name=model_name, error=str(e))
            raise

    async def unload_model(
        self,
        model_name: str
    ) -> Dict[str, Any]:
        """
        Unload a model from Models Service memory
        
        Args:
            model_name: Name of model to unload
            
        Returns:
            Unload status information
        """
        try:
            data = {"model_name": model_name}
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/models/unload",
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info("Model unload successful",
                       model_name=model_name)
            return result
            
        except Exception as e:
            logger.error("Model unload failed",
                        model_name=model_name, error=str(e))
            raise

    # Batch Processing Methods
    async def batch_transcribe(
        self,
        audio_files: List[Union[bytes, str, Path]],
        language: str = "auto",
        model: str = "whisper_base",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Batch transcribe multiple audio files
        
        Args:
            audio_files: List of audio data/files
            language: Language code
            model: STT model to use
            **kwargs: Additional parameters
            
        Returns:
            List of transcription results
        """
        try:
            tasks = [
                self.transcribe_audio(audio, language, model, **kwargs)
                for audio in audio_files
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Separate successful results from exceptions
            success_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch transcription failed for file {i}",
                               error=str(result))
                    success_results.append({
                        "error": str(result),
                        "success": False
                    })
                else:
                    success_results.append(result)
            
            logger.info("Batch transcription completed",
                       total_files=len(audio_files),
                       successful=len([r for r in success_results if r.get('success', True)]))
            
            return success_results
            
        except Exception as e:
            logger.error("Batch transcription failed", error=str(e))
            raise

    async def batch_synthesize(
        self,
        texts: List[str],
        language: str = "en",
        voice: str = "default",
        model: str = "espeak",
        **kwargs
    ) -> List[bytes]:
        """
        Batch synthesize multiple texts
        
        Args:
            texts: List of texts to synthesize
            language: Language code
            voice: Voice to use
            model: TTS model to use
            **kwargs: Additional parameters
            
        Returns:
            List of audio data
        """
        try:
            tasks = [
                self.synthesize_speech(text, language, voice, model, **kwargs)
                for text in texts
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in batch results
            audio_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch synthesis failed for text {i}",
                               error=str(result))
                    audio_results.append(b'')  # Empty audio for failed synthesis
                else:
                    audio_results.append(result)
            
            logger.info("Batch synthesis completed",
                       total_texts=len(texts),
                       successful=len([r for r in audio_results if r]))
            
            return audio_results
            
        except Exception as e:
            logger.error("Batch synthesis failed", error=str(e))
            raise

    # Utility Methods
    async def get_supported_languages(self) -> Dict[str, List[str]]:
        """
        Get supported languages for each capability
        
        Returns:
            Dictionary with supported languages per capability
        """
        try:
            status = await self.get_service_status()
            capabilities = status.get('capabilities', {})
            
            supported_languages = {}
            
            if 'stt' in capabilities:
                supported_languages['stt'] = capabilities['stt'].get('supported_languages', [])
            
            if 'tts' in capabilities:
                supported_languages['tts'] = capabilities['tts'].get('supported_languages', [])
                
            if 'nlp' in capabilities:
                supported_languages['nlp'] = capabilities['nlp'].get('supported_languages', [])
            
            return supported_languages
            
        except Exception as e:
            logger.error("Failed to get supported languages", error=str(e))
            return {
                'stt': ['en', 'hi'],  # Default fallback
                'tts': ['en', 'hi'],
                'nlp': ['en', 'hi']
            }

    def is_language_supported(self, language: str, capability: str) -> bool:
        """
        Check if a language is supported for a specific capability
        
        Args:
            language: Language code to check
            capability: Capability to check (stt, tts, nlp)
            
        Returns:
            True if language is supported
        """
        # This would typically cache the supported languages result
        # For now, return True for common languages
        common_languages = ['en', 'hi', 'te', 'ta', 'bn', 'mr', 'gu', 'kn', 'ml']
        return language in common_languages or language == 'auto'


# Singleton instance for easy imports
models_service_client = ModelsServiceClient()


class ModelsServiceError(Exception):
    """Base exception for Models Service errors"""
    pass


class ModelsServiceUnavailableError(ModelsServiceError):
    """Exception raised when Models Service is unavailable"""
    pass


class ModelNotFoundError(ModelsServiceError):
    """Exception raised when requested model is not found"""
    pass


class LanguageNotSupportedError(ModelsServiceError):
    """Exception raised when language is not supported"""
    pass
