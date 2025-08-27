"""
Base Voice Engine Classes
Abstract base classes for voice processing engines following translation service patterns
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncGenerator
from .models import AudioData, STTResult, EmotionAnalysis, VoiceProfile

class BaseVoiceEngine(ABC):
    """Abstract base class for all voice processing engines"""
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        self.config = config
        self.engine_name = self.__class__.__name__
        self.is_initialized = False
        self.supported_languages = []
        self.initialize(**kwargs)
    
    @abstractmethod
    def initialize(self, **kwargs) -> None:
        """Initialize the engine with configuration"""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Check engine health status"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        pass
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported by this engine"""
        return language_code in self.get_supported_languages()

class BaseSTTEngine(BaseVoiceEngine):
    """Abstract base class for Speech-to-Text engines"""
    
    @abstractmethod
    async def transcribe_audio(
        self, 
        audio_data: AudioData, 
        language: str = "en",
        **kwargs
    ) -> STTResult:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio data to transcribe
            language: Expected language code
            **kwargs: Engine-specific parameters
            
        Returns:
            STTResult with transcription and metadata
        """
        pass
    
    @abstractmethod
    async def transcribe_stream(
        self, 
        audio_stream,
        language: str = "en",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Transcribe audio stream in real-time
        
        Args:
            audio_stream: Stream of audio data
            language: Expected language code
            **kwargs: Engine-specific parameters
            
        Yields:
            Partial transcription results
        """
        pass
    
    def supports_diarization(self) -> bool:
        """Check if engine supports speaker diarization"""
        return False
    
    def supports_streaming(self) -> bool:
        """Check if engine supports real-time streaming"""
        return False
    
    def get_confidence_threshold(self) -> float:
        """Get minimum confidence threshold for this engine"""
        return self.config.get("confidence_threshold", 0.7)

class BaseTTSEngine(BaseVoiceEngine):
    """Abstract base class for Text-to-Speech engines"""
    
    @abstractmethod
    async def synthesize_speech(
        self, 
        text: str, 
        language: str = "en",
        voice_id: Optional[str] = None,
        **kwargs
    ) -> AudioData:
        """
        Synthesize speech from text
        
        Args:
            text: Text to convert to speech
            language: Language code
            voice_id: Specific voice identifier
            **kwargs: Engine-specific parameters (speed, pitch, etc.)
            
        Returns:
            AudioData with synthesized speech
        """
        pass
    
    @abstractmethod
    def get_available_voices(self, language: str = "en") -> List[Dict[str, Any]]:
        """
        Get available voices for a language
        
        Args:
            language: Language code
            
        Returns:
            List of voice information dictionaries
        """
        pass
    
    def supports_voice_cloning(self) -> bool:
        """Check if engine supports voice cloning"""
        return False
    
    def supports_custom_voices(self) -> bool:
        """Check if engine supports custom voice profiles"""
        return False
    
    async def create_voice_profile(
        self, 
        audio_samples: List[AudioData], 
        profile_name: str,
        **kwargs
    ) -> VoiceProfile:
        """
        Create custom voice profile from audio samples
        
        Args:
            audio_samples: List of audio samples for training
            profile_name: Name for the voice profile
            **kwargs: Engine-specific parameters
            
        Returns:
            Created voice profile
            
        Raises:
            NotImplementedError: If engine doesn't support voice cloning
        """
        raise NotImplementedError("Voice cloning not supported by this engine")

class BaseEmotionEngine(BaseVoiceEngine):
    """Abstract base class for Voice Emotion Analysis engines"""
    
    @abstractmethod
    async def analyze_emotion(
        self, 
        audio_data: AudioData,
        **kwargs
    ) -> EmotionAnalysis:
        """
        Analyze emotion from voice audio
        
        Args:
            audio_data: Audio data to analyze
            **kwargs: Engine-specific parameters
            
        Returns:
            EmotionAnalysis with detected emotions and scores
        """
        pass
    
    @abstractmethod
    def get_supported_emotions(self) -> List[str]:
        """Get list of emotions this engine can detect"""
        pass
    
    def supports_realtime_analysis(self) -> bool:
        """Check if engine supports real-time emotion analysis"""
        return False
    
    def get_minimum_audio_duration(self) -> float:
        """Get minimum audio duration required for analysis (in seconds)"""
        return 1.0

class VoiceEngineFactory:
    """Factory for creating voice engine instances"""
    
    _engine_registry: Dict[str, type] = {}
    
    @classmethod
    def register_engine(cls, engine_name: str, engine_class: type):
        """Register a voice engine class"""
        cls._engine_registry[engine_name] = engine_class
    
    @classmethod
    def create_engine(
        cls, 
        engine_name: str, 
        engine_type: str,
        config: Dict[str, Any],
        **kwargs
    ) -> BaseVoiceEngine:
        """
        Create voice engine instance
        
        Args:
            engine_name: Name of the engine (e.g., 'whisper', 'elevenlabs')
            engine_type: Type of engine ('stt', 'tts', 'emotion')
            config: Engine configuration
            **kwargs: Additional parameters
            
        Returns:
            Initialized engine instance
            
        Raises:
            ValueError: If engine not found or invalid type
        """
        full_engine_name = f"{engine_name}_{engine_type}"
        
        if full_engine_name not in cls._engine_registry:
            raise ValueError(f"Engine '{full_engine_name}' not registered")
        
        engine_class = cls._engine_registry[full_engine_name]
        return engine_class(config, **kwargs)
    
    @classmethod
    def get_available_engines(cls, engine_type: Optional[str] = None) -> List[str]:
        """Get list of available engine names"""
        engines = list(cls._engine_registry.keys())
        
        if engine_type:
            engines = [e for e in engines if e.endswith(f"_{engine_type}")]
        
        return engines
    
    @classmethod
    def is_engine_available(cls, engine_name: str, engine_type: str) -> bool:
        """Check if specific engine is available"""
        full_engine_name = f"{engine_name}_{engine_type}"
        return full_engine_name in cls._engine_registry

# Engine decorator for automatic registration
def voice_engine(engine_name: str, engine_type: str):
    """Decorator for automatic engine registration"""
    def decorator(engine_class):
        VoiceEngineFactory.register_engine(f"{engine_name}_{engine_type}", engine_class)
        return engine_class
    return decorator
