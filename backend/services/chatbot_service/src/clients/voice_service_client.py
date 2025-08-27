"""
Voice Service Client for Chatbot Service  
Provides Text-to-Speech (TTS) and Speech-to-Text (STT) capabilities
"""
import logging
from typing import Dict, Any, Optional, List, Union
import httpx
from dataclasses import dataclass
import base64

logger = logging.getLogger(__name__)

@dataclass
class TTSResult:
    """Text-to-Speech result"""
    audio_data: bytes
    audio_format: str
    language: str
    voice_id: str
    duration: float
    sample_rate: int

@dataclass
class STTResult:
    """Speech-to-Text result"""
    transcribed_text: str
    confidence: float
    language: str
    words: List[Dict[str, Any]]
    duration: float

@dataclass
class VoiceProfile:
    """Voice profile information"""
    voice_id: str
    name: str
    language: str
    gender: str
    age_group: str
    style: str
    supported_emotions: List[str]

class VoiceServiceClient:
    """Client for communicating with Voice Service"""
    
    def __init__(self):
        import os
        self.voice_service_url = os.getenv("VOICE_SERVICE_URL", "http://voice-service:8003")
        self.timeout = int(os.getenv("VOICE_SERVICE_TIMEOUT", "60"))  # Longer timeout for audio processing
        self.max_retries = int(os.getenv("VOICE_SERVICE_MAX_RETRIES", "3"))
        self.default_voice = os.getenv("VOICE_DEFAULT_VOICE", "hi_female_1")
        self.default_language = os.getenv("VOICE_DEFAULT_LANGUAGE", "hi")
        self.audio_format = os.getenv("VOICE_AUDIO_FORMAT", "wav")
        self.sample_rate = int(os.getenv("VOICE_SAMPLE_RATE", "22050"))
        self.is_enabled = os.getenv("VOICE_SERVICE_ENABLED", "true").lower() == "true"
        
        # Supported languages from MantraPath voice configuration
        self.supported_languages = {
            "hi": "Hindi",
            "en": "English", 
            "bn": "Bengali",
            "te": "Telugu",
            "ta": "Tamil",
            "ur": "Urdu",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "mr": "Marathi",
            "pa": "Punjabi",
            "or": "Odia"
        }
        
        logger.info(f"Voice Service Client initialized - URL: {self.voice_service_url}, Enabled: {self.is_enabled}")
    
    async def health_check(self) -> bool:
        """Check if Voice Service is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.voice_service_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Voice Service health check failed: {e}")
            return False
    
    async def text_to_speech(
        self, 
        text: str, 
        language: str = None,
        voice_id: str = None,
        emotion: str = "neutral",
        speed: float = 1.0,
        jwt_token: Optional[str] = None
    ) -> Optional[TTSResult]:
        """
        Convert text to speech using Voice Service
        
        Args:
            text: Text to convert to speech
            language: Language code (defaults to default_language)
            voice_id: Voice ID to use (defaults to default_voice)
            emotion: Emotion for voice synthesis
            speed: Speech speed multiplier
            jwt_token: JWT token for authentication
            
        Returns:
            TTSResult object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Voice Service is disabled, TTS not available")
            return None
            
        language = language or self.default_language
        voice_id = voice_id or self.default_voice
        
        if language not in self.supported_languages:
            logger.warning(f"Unsupported language for TTS: {language}")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "text": text,
                "language": language,
                "voice_id": voice_id,
                "emotion": emotion,
                "speed": speed,
                "format": self.audio_format,
                "sample_rate": self.sample_rate
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.voice_service_url}/api/tts/synthesize",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_tts_result(data)
                else:
                    logger.error(f"TTS synthesis failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in TTS synthesis: {e}")
            return None
    
    async def speech_to_text(
        self, 
        audio_data: bytes, 
        language: str = None,
        audio_format: str = None,
        jwt_token: Optional[str] = None
    ) -> Optional[STTResult]:
        """
        Convert speech to text using Voice Service
        
        Args:
            audio_data: Audio data bytes
            language: Language code for STT
            audio_format: Audio format (wav, mp3, etc.)
            jwt_token: JWT token for authentication
            
        Returns:
            STTResult object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Voice Service is disabled, STT not available")
            return None
            
        language = language or self.default_language
        audio_format = audio_format or self.audio_format
        
        try:
            headers = {}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            # Convert audio to base64 for JSON payload
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            payload = {
                "audio_data": audio_base64,
                "language": language,
                "format": audio_format
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.voice_service_url}/api/stt/transcribe",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_stt_result(data)
                else:
                    logger.error(f"STT transcription failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in STT transcription: {e}")
            return None
    
    async def get_available_voices(
        self, 
        language: str = None,
        jwt_token: Optional[str] = None
    ) -> List[VoiceProfile]:
        """
        Get available voice profiles from Voice Service
        
        Args:
            language: Filter by language (optional)
            jwt_token: JWT token for authentication
            
        Returns:
            List of VoiceProfile objects
        """
        if not self.is_enabled:
            logger.debug("Voice Service is disabled, returning basic voice profiles")
            return self._get_basic_voice_profiles(language)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            params = {}
            if language:
                params["language"] = language
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.voice_service_url}/api/voices",
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_voice_profiles(data.get("voices", []))
                else:
                    logger.error(f"Get voices failed: {response.status_code} - {response.text}")
                    return self._get_basic_voice_profiles(language)
                    
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return self._get_basic_voice_profiles(language)
    
    async def synthesize_with_emotion(
        self, 
        text: str, 
        emotion: str,
        intensity: float = 0.5,
        language: str = None,
        voice_id: str = None,
        jwt_token: Optional[str] = None
    ) -> Optional[TTSResult]:
        """
        Synthesize speech with specific emotion
        
        Args:
            text: Text to synthesize
            emotion: Emotion to convey (happy, sad, angry, etc.)
            intensity: Emotion intensity (0.0 to 1.0)
            language: Language code
            voice_id: Voice ID to use
            jwt_token: JWT token for authentication
            
        Returns:
            TTSResult object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Voice Service is disabled, emotional TTS not available")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "text": text,
                "emotion": emotion,
                "intensity": intensity,
                "language": language or self.default_language,
                "voice_id": voice_id or self.default_voice,
                "format": self.audio_format,
                "sample_rate": self.sample_rate
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.voice_service_url}/api/tts/emotional-synthesis",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_tts_result(data)
                else:
                    logger.error(f"Emotional TTS failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error in emotional TTS: {e}")
            return None
    
    async def batch_synthesize(
        self, 
        texts: List[str], 
        language: str = None,
        voice_id: str = None,
        jwt_token: Optional[str] = None
    ) -> List[Optional[TTSResult]]:
        """
        Synthesize multiple texts in batch
        
        Args:
            texts: List of texts to synthesize
            language: Language code
            voice_id: Voice ID to use
            jwt_token: JWT token for authentication
            
        Returns:
            List of TTSResult objects
        """
        if not self.is_enabled:
            logger.debug("Voice Service is disabled, batch TTS not available")
            return [None] * len(texts)
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "texts": texts,
                "language": language or self.default_language,
                "voice_id": voice_id or self.default_voice,
                "format": self.audio_format,
                "sample_rate": self.sample_rate
            }
            
            async with httpx.AsyncClient(timeout=self.timeout * 2) as client:  # Longer timeout for batch
                response = await client.post(
                    f"{self.voice_service_url}/api/tts/batch-synthesize",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return [self._parse_tts_result(result) for result in data.get("results", [])]
                else:
                    logger.error(f"Batch TTS failed: {response.status_code} - {response.text}")
                    return [None] * len(texts)
                    
        except Exception as e:
            logger.error(f"Error in batch TTS: {e}")
            return [None] * len(texts)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages for voice services"""
        return self.supported_languages.copy()
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported for voice services"""
        return language_code in self.supported_languages
    
    def _get_basic_voice_profiles(self, language: str = None) -> List[VoiceProfile]:
        """Get basic voice profiles as fallback"""
        basic_profiles = [
            VoiceProfile(
                voice_id="hi_female_1",
                name="Hindi Female Voice 1",
                language="hi",
                gender="female",
                age_group="adult",
                style="neutral",
                supported_emotions=["neutral", "happy", "sad"]
            ),
            VoiceProfile(
                voice_id="hi_male_1",
                name="Hindi Male Voice 1", 
                language="hi",
                gender="male",
                age_group="adult",
                style="neutral",
                supported_emotions=["neutral", "happy", "sad"]
            ),
            VoiceProfile(
                voice_id="en_female_1",
                name="English Female Voice 1",
                language="en",
                gender="female",
                age_group="adult",
                style="neutral",
                supported_emotions=["neutral", "happy", "sad"]
            ),
            VoiceProfile(
                voice_id="en_male_1",
                name="English Male Voice 1",
                language="en",
                gender="male",
                age_group="adult",
                style="neutral",
                supported_emotions=["neutral", "happy", "sad"]
            )
        ]
        
        if language:
            return [profile for profile in basic_profiles if profile.language == language]
        return basic_profiles
    
    def _parse_tts_result(self, data: Dict[str, Any]) -> TTSResult:
        """Parse TTS result from API response"""
        # Decode base64 audio data
        audio_base64 = data.get("audio_data", "")
        audio_data = base64.b64decode(audio_base64) if audio_base64 else b""
        
        return TTSResult(
            audio_data=audio_data,
            audio_format=data.get("format", self.audio_format),
            language=data.get("language", self.default_language),
            voice_id=data.get("voice_id", self.default_voice),
            duration=data.get("duration", 0.0),
            sample_rate=data.get("sample_rate", self.sample_rate)
        )
    
    def _parse_stt_result(self, data: Dict[str, Any]) -> STTResult:
        """Parse STT result from API response"""
        return STTResult(
            transcribed_text=data.get("text", ""),
            confidence=data.get("confidence", 0.0),
            language=data.get("language", self.default_language),
            words=data.get("words", []),
            duration=data.get("duration", 0.0)
        )
    
    def _parse_voice_profiles(self, voices_data: List[Dict[str, Any]]) -> List[VoiceProfile]:
        """Parse voice profiles from API response"""
        profiles = []
        for voice_data in voices_data:
            try:
                profile = VoiceProfile(
                    voice_id=voice_data.get("voice_id", ""),
                    name=voice_data.get("name", ""),
                    language=voice_data.get("language", ""),
                    gender=voice_data.get("gender", ""),
                    age_group=voice_data.get("age_group", ""),
                    style=voice_data.get("style", ""),
                    supported_emotions=voice_data.get("supported_emotions", [])
                )
                profiles.append(profile)
            except Exception as e:
                logger.error(f"Error parsing voice profile: {e}")
                continue
        
        return profiles

# Global client instance
voice_service_client = VoiceServiceClient()
