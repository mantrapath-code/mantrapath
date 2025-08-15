"""
ElevenLabs Text-to-Speech Engine
Premium voice synthesis with voice cloning capabilities
"""
import asyncio
import logging
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.base_engine import BaseTTSEngine, voice_engine
from core.models import AudioData, VoiceProfile, AudioFormat
from core.exceptions import TTSEngineError, UnsupportedLanguageError, VoiceProfileCreationError
from config.language_config import SUPPORTED_LANGUAGES, get_language_info

logger = logging.getLogger(__name__)

@voice_engine("elevenlabs", "tts")
class ElevenLabsTTSEngine(BaseTTSEngine):
    """ElevenLabs Text-to-Speech Engine implementation"""
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        super().__init__(config, **kwargs)
        self.api_key = config.get("elevenlabs_api_key", "")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.client = None
        self.available_voices = {}
        
    def initialize(self, **kwargs) -> None:
        """Initialize ElevenLabs engine"""
        if not self.api_key:
            raise TTSEngineError("ElevenLabs API key not provided", "elevenlabs")
        
        try:
            self.client = httpx.AsyncClient(
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            self.is_initialized = True
            logger.info("ElevenLabs TTS engine initialized")
            
        except Exception as e:
            raise TTSEngineError(f"Failed to initialize ElevenLabs engine: {e}", "elevenlabs")
    
    def health_check(self) -> Dict[str, Any]:
        """Check ElevenLabs engine health"""
        try:
            if not self.client:
                return {
                    "engine": "elevenlabs",
                    "status": "unhealthy",
                    "details": {"error": "Client not initialized"},
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            return {
                "engine": "elevenlabs",
                "status": "healthy",
                "details": {"api_connected": True, "voices_cached": len(self.available_voices)},
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "engine": "elevenlabs",
                "status": "unhealthy",
                "details": {"error": str(e)},
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_supported_languages(self) -> List[str]:
        """Get ElevenLabs supported languages (Tier 1 languages with premium support)"""
        return [
            code for code, info in SUPPORTED_LANGUAGES.items() 
            if info.get("tier") == 1 and "elevenlabs" in info.get("tts_engines", [])
        ]
    
    async def synthesize_speech(
        self, 
        text: str, 
        language: str = "en",
        voice_id: Optional[str] = None,
        **kwargs
    ) -> AudioData:
        """Synthesize speech using ElevenLabs"""
        if not self.is_initialized:
            raise TTSEngineError("ElevenLabs engine not initialized", "elevenlabs")
        
        if not self.is_language_supported(language):
            raise UnsupportedLanguageError(language, self.get_supported_languages())
        
        try:
            # Get default voice if none specified
            if not voice_id:
                voices = await self.get_available_voices(language)
                if not voices:
                    raise TTSEngineError(f"No voices available for language: {language}", "elevenlabs")
                voice_id = voices[0]["voice_id"]
            
            # Prepare synthesis parameters
            voice_settings = {
                "stability": kwargs.get("stability", 0.75),
                "similarity_boost": kwargs.get("similarity_boost", 0.75),
                "style": kwargs.get("style", 0.0),
                "use_speaker_boost": kwargs.get("use_speaker_boost", True)
            }
            
            # Make API request
            url = f"{self.base_url}/text-to-speech/{voice_id}"
            payload = {
                "text": text,
                "model_id": kwargs.get("model_id", "eleven_multilingual_v2"),
                "voice_settings": voice_settings
            }
            
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            
            # Return audio data
            audio_bytes = response.content
            
            return AudioData(
                data=audio_bytes,
                format=AudioFormat.MP3,  # ElevenLabs returns MP3 by default
                sample_rate=kwargs.get("sample_rate", 22050),
                channels=1,
                file_size=len(audio_bytes)
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs API error: {e.response.status_code} - {e.response.text}")
            raise TTSEngineError(f"ElevenLabs API error: {e.response.status_code}", "elevenlabs")
        except Exception as e:
            logger.error(f"ElevenLabs synthesis error: {e}")
            raise TTSEngineError(f"Speech synthesis failed: {str(e)}", "elevenlabs")
    
    async def get_available_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        """Get available voices for a language"""
        if not self.is_initialized:
            raise TTSEngineError("ElevenLabs engine not initialized", "elevenlabs")
        
        try:
            # Check cache first
            if language in self.available_voices:
                return self.available_voices[language]
            
            # Fetch voices from API
            url = f"{self.base_url}/voices"
            response = await self.client.get(url)
            response.raise_for_status()
            
            voices_data = response.json()
            voices = []
            
            for voice in voices_data.get("voices", []):
                # Filter voices that support the requested language
                voice_info = {
                    "voice_id": voice["voice_id"],
                    "name": voice["name"],
                    "category": voice.get("category", "generated"),
                    "description": voice.get("description", ""),
                    "labels": voice.get("labels", {}),
                    "preview_url": voice.get("preview_url"),
                    "available_for_tiers": voice.get("available_for_tiers", []),
                    "settings": voice.get("settings")
                }
                
                # Check if voice supports the language (simplified logic)
                if self._voice_supports_language(voice, language):
                    voices.append(voice_info)
            
            # Cache the results
            self.available_voices[language] = voices
            return voices
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs voices API error: {e.response.status_code}")
            raise TTSEngineError(f"Failed to fetch voices: {e.response.status_code}", "elevenlabs")
        except Exception as e:
            logger.error(f"ElevenLabs get voices error: {e}")
            raise TTSEngineError(f"Failed to get available voices: {str(e)}", "elevenlabs")
    
    def _voice_supports_language(self, voice: Dict[str, Any], language: str) -> bool:
        """Check if voice supports the specified language"""
        # ElevenLabs v2 multilingual model supports most languages
        # For now, we'll assume all voices support all our tier 1 languages
        return language in self.get_supported_languages()
    
    def supports_voice_cloning(self) -> bool:
        """ElevenLabs supports voice cloning"""
        return True
    
    def supports_custom_voices(self) -> bool:
        """ElevenLabs supports custom voice profiles"""
        return True
    
    async def create_voice_profile(
        self, 
        audio_samples: List[AudioData], 
        profile_name: str,
        **kwargs
    ) -> VoiceProfile:
        """Create custom voice profile using ElevenLabs voice cloning"""
        if not self.is_initialized:
            raise TTSEngineError("ElevenLabs engine not initialized", "elevenlabs")
        
        if len(audio_samples) < 3:
            raise VoiceProfileCreationError("At least 3 audio samples required for voice cloning")
        
        try:
            # Prepare voice cloning request
            url = f"{self.base_url}/voices/add"
            
            # Create multipart form data
            files = []
            for i, sample in enumerate(audio_samples[:10]):  # Limit to 10 samples
                files.append(("files", (f"sample_{i}.wav", sample.data, "audio/wav")))
            
            data = {
                "name": profile_name,
                "description": kwargs.get("description", f"Custom voice profile: {profile_name}"),
                "labels": kwargs.get("labels", "{}")
            }
            
            # Make voice cloning request
            response = await self.client.post(
                url,
                files=files,
                data=data
            )
            response.raise_for_status()
            
            voice_data = response.json()
            
            # Create voice profile object
            voice_profile = VoiceProfile(
                user_id=kwargs.get("user_id", "unknown"),
                voice_id=voice_data["voice_id"],
                name=profile_name,
                description=data["description"],
                voice_settings={
                    "engine": "elevenlabs",
                    "voice_id": voice_data["voice_id"],
                    "model_id": "eleven_multilingual_v2"
                },
                sample_count=len(audio_samples),
                quality_score=0.85  # ElevenLabs typically produces good quality
            )
            
            logger.info(f"Created ElevenLabs voice profile: {voice_data['voice_id']}")
            return voice_profile
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs voice cloning API error: {e.response.status_code} - {e.response.text}")
            raise VoiceProfileCreationError(f"Voice cloning failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"ElevenLabs voice cloning error: {e}")
            raise VoiceProfileCreationError(f"Voice profile creation failed: {str(e)}")
    
    async def delete_voice_profile(self, voice_id: str) -> bool:
        """Delete a custom voice profile"""
        if not self.is_initialized:
            raise TTSEngineError("ElevenLabs engine not initialized", "elevenlabs")
        
        try:
            url = f"{self.base_url}/voices/{voice_id}"
            response = await self.client.delete(url)
            response.raise_for_status()
            
            logger.info(f"Deleted ElevenLabs voice profile: {voice_id}")
            return True
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Voice profile not found: {voice_id}")
                return False
            logger.error(f"ElevenLabs delete voice error: {e.response.status_code}")
            raise TTSEngineError(f"Failed to delete voice profile: {e.response.status_code}", "elevenlabs")
        except Exception as e:
            logger.error(f"ElevenLabs delete voice error: {e}")
            raise TTSEngineError(f"Failed to delete voice profile: {str(e)}", "elevenlabs")
    
    async def get_voice_info(self, voice_id: str) -> Dict[str, Any]:
        """Get detailed information about a voice"""
        if not self.is_initialized:
            raise TTSEngineError("ElevenLabs engine not initialized", "elevenlabs")
        
        try:
            url = f"{self.base_url}/voices/{voice_id}"
            response = await self.client.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs voice info error: {e.response.status_code}")
            raise TTSEngineError(f"Failed to get voice info: {e.response.status_code}", "elevenlabs")
        except Exception as e:
            logger.error(f"ElevenLabs voice info error: {e}")
            raise TTSEngineError(f"Failed to get voice info: {str(e)}", "elevenlabs")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.client:
            await self.client.aclose()
