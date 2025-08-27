"""
Voice Engine Manager
Centralized management and coordination of voice processing engines
"""
import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from core.base_engine import BaseVoiceEngine, BaseSTTEngine, BaseTTSEngine, BaseEmotionEngine, VoiceEngineFactory
from core.models import AudioData, STTResult, VoiceProfile, EmotionAnalysis
from core.exceptions import EngineError, UnsupportedLanguageError, ConfigurationError
from config.language_config import SUPPORTED_LANGUAGES, get_supported_engines, ENGINE_PRIORITIES

logger = logging.getLogger(__name__)

class VoiceEngineManager:
    """Manages voice processing engines with fallback and load balancing"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.stt_engines: Dict[str, BaseSTTEngine] = {}
        self.tts_engines: Dict[str, BaseTTSEngine] = {}
        self.emotion_engines: Dict[str, BaseEmotionEngine] = {}
        self.engine_health: Dict[str, Dict[str, Any]] = {}
        self.is_initialized = False
        
    async def initialize_engines(self) -> None:
        """Initialize all configured engines - alias for initialize()"""
        await self.initialize()
        
    async def cleanup(self) -> None:
        """Cleanup all engines"""
        try:
            # Cleanup STT engines
            for engine in self.stt_engines.values():
                if hasattr(engine, 'cleanup'):
                    await engine.cleanup()
            
            # Cleanup TTS engines
            for engine in self.tts_engines.values():
                if hasattr(engine, 'cleanup'):
                    await engine.cleanup()
            
            # Cleanup emotion engines
            for engine in self.emotion_engines.values():
                if hasattr(engine, 'cleanup'):
                    await engine.cleanup()
                    
            logger.info("All engines cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during engine cleanup: {e}")
    
    async def initialize(self) -> None:
        """Initialize all configured engines"""
        try:
            await self._initialize_stt_engines()
            await self._initialize_tts_engines()
            await self._initialize_emotion_engines()
            
            self.is_initialized = True
            logger.info("Voice Engine Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Voice Engine Manager: {e}")
            raise ConfigurationError(f"Engine initialization failed: {str(e)}")
    
    async def _initialize_stt_engines(self) -> None:
        """Initialize STT engines"""
        stt_config = self.config.get("stt_engines", {})
        
        for engine_name, engine_config in stt_config.items():
            if not engine_config.get("enabled", True):
                continue
                
            try:
                engine = VoiceEngineFactory.create_engine(
                    engine_name, 
                    "stt", 
                    engine_config
                )
                self.stt_engines[engine_name] = engine
                logger.info(f"Initialized STT engine: {engine_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize STT engine {engine_name}: {e}")
                if engine_config.get("required", False):
                    raise ConfigurationError(f"Required STT engine {engine_name} failed to initialize")
    
    async def _initialize_tts_engines(self) -> None:
        """Initialize TTS engines"""
        tts_config = self.config.get("tts_engines", {})
        
        for engine_name, engine_config in tts_config.items():
            if not engine_config.get("enabled", True):
                continue
                
            try:
                engine = VoiceEngineFactory.create_engine(
                    engine_name,
                    "tts", 
                    engine_config
                )
                self.tts_engines[engine_name] = engine
                logger.info(f"Initialized TTS engine: {engine_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize TTS engine {engine_name}: {e}")
                if engine_config.get("required", False):
                    raise ConfigurationError(f"Required TTS engine {engine_name} failed to initialize")
    
    async def _initialize_emotion_engines(self) -> None:
        """Initialize emotion analysis engines"""
        emotion_config = self.config.get("emotion_engines", {})
        
        for engine_name, engine_config in emotion_config.items():
            if not engine_config.get("enabled", True):
                continue
                
            try:
                engine = VoiceEngineFactory.create_engine(
                    engine_name,
                    "emotion",
                    engine_config
                )
                self.emotion_engines[engine_name] = engine
                logger.info(f"Initialized emotion engine: {engine_name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize emotion engine {engine_name}: {e}")
    
    async def transcribe_audio(
        self, 
        audio_data: AudioData, 
        language: str = "en",
        preferred_engine: Optional[str] = None,
        **kwargs
    ) -> STTResult:
        """Transcribe audio with engine selection and fallback"""
        if not self.is_initialized:
            raise EngineError("Engine manager not initialized")
        
        if not self.stt_engines:
            raise EngineError("No STT engines available")
        
        # Get engine priority list for language
        available_engines = self._get_available_stt_engines(language)
        if not available_engines:
            raise UnsupportedLanguageError(language)
        
        # Try preferred engine first
        if preferred_engine and preferred_engine in available_engines:
            available_engines = [preferred_engine] + [e for e in available_engines if e != preferred_engine]
        
        # Try engines in priority order
        last_error = None
        for engine_name in available_engines:
            try:
                engine = self.stt_engines[engine_name]
                
                # Check engine health
                if not await self._is_engine_healthy(engine_name, "stt"):
                    logger.warning(f"STT engine {engine_name} is unhealthy, trying next")
                    continue
                
                result = await engine.transcribe_audio(audio_data, language, **kwargs)
                
                # Add engine info to result
                result.engine_used = engine_name
                
                logger.info(f"STT completed successfully with engine: {engine_name}")
                return result
                
            except Exception as e:
                logger.warning(f"STT engine {engine_name} failed: {e}")
                last_error = e
                continue
        
        # All engines failed
        raise EngineError(f"All STT engines failed. Last error: {str(last_error)}")
    
    async def synthesize_speech(
        self, 
        text: str, 
        language: str = "en",
        voice_id: Optional[str] = None,
        preferred_engine: Optional[str] = None,
        **kwargs
    ) -> AudioData:
        """Synthesize speech with engine selection and fallback"""
        if not self.is_initialized:
            raise EngineError("Engine manager not initialized")
        
        if not self.tts_engines:
            raise EngineError("No TTS engines available")
        
        # Get engine priority list for language
        available_engines = self._get_available_tts_engines(language)
        if not available_engines:
            raise UnsupportedLanguageError(language)
        
        # Try preferred engine first
        if preferred_engine and preferred_engine in available_engines:
            available_engines = [preferred_engine] + [e for e in available_engines if e != preferred_engine]
        
        # Try engines in priority order
        last_error = None
        for engine_name in available_engines:
            try:
                engine = self.tts_engines[engine_name]
                
                # Check engine health
                if not await self._is_engine_healthy(engine_name, "tts"):
                    logger.warning(f"TTS engine {engine_name} is unhealthy, trying next")
                    continue
                
                result = await engine.synthesize_speech(text, language, voice_id, **kwargs)
                
                # Add engine info to result
                result.engine_used = engine_name
                
                logger.info(f"TTS completed successfully with engine: {engine_name}")
                return result
                
            except Exception as e:
                logger.warning(f"TTS engine {engine_name} failed: {e}")
                last_error = e
                continue
        
        # All engines failed
        raise EngineError(f"All TTS engines failed. Last error: {str(last_error)}")
    
    async def analyze_emotion(
        self, 
        audio_data: AudioData,
        preferred_engine: Optional[str] = None,
        **kwargs
    ) -> Optional[EmotionAnalysis]:
        """Analyze emotion with engine selection"""
        if not self.emotion_engines:
            logger.warning("No emotion analysis engines available")
            return None
        
        # Get available emotion engines
        available_engines = list(self.emotion_engines.keys())
        
        # Try preferred engine first
        if preferred_engine and preferred_engine in available_engines:
            available_engines = [preferred_engine] + [e for e in available_engines if e != preferred_engine]
        
        # Try engines in order
        for engine_name in available_engines:
            try:
                engine = self.emotion_engines[engine_name]
                
                # Check engine health
                if not await self._is_engine_healthy(engine_name, "emotion"):
                    continue
                
                result = await engine.analyze_emotion(audio_data, **kwargs)
                
                logger.info(f"Emotion analysis completed with engine: {engine_name}")
                return result
                
            except Exception as e:
                logger.warning(f"Emotion engine {engine_name} failed: {e}")
                continue
        
        logger.warning("All emotion analysis engines failed")
        return None
    
    def _get_available_stt_engines(self, language: str) -> List[str]:
        """Get available STT engines for a language in priority order"""
        supported_engines = get_supported_engines(language, "stt")
        
        # Filter by available engines
        available = [
            engine for engine in supported_engines 
            if engine in self.stt_engines
        ]
        
        # Sort by priority
        lang_info = SUPPORTED_LANGUAGES.get(language, {})
        tier = lang_info.get("tier", 2)
        priorities = ENGINE_PRIORITIES["stt"].get(f"tier_{tier}", ENGINE_PRIORITIES["stt"]["tier_2"])
        
        # Sort available engines by priority
        sorted_engines = []
        for priority_engine in priorities:
            if priority_engine in available:
                sorted_engines.append(priority_engine)
        
        # Add any remaining engines
        for engine in available:
            if engine not in sorted_engines:
                sorted_engines.append(engine)
        
        return sorted_engines
    
    def _get_available_tts_engines(self, language: str) -> List[str]:
        """Get available TTS engines for a language in priority order"""
        supported_engines = get_supported_engines(language, "tts")
        
        # Filter by available engines
        available = [
            engine for engine in supported_engines 
            if engine in self.tts_engines
        ]
        
        # Sort by priority
        lang_info = SUPPORTED_LANGUAGES.get(language, {})
        tier = lang_info.get("tier", 2)
        priorities = ENGINE_PRIORITIES["tts"].get(f"tier_{tier}", ENGINE_PRIORITIES["tts"]["tier_2"])
        
        # Sort available engines by priority
        sorted_engines = []
        for priority_engine in priorities:
            if priority_engine in available:
                sorted_engines.append(priority_engine)
        
        # Add any remaining engines
        for engine in available:
            if engine not in sorted_engines:
                sorted_engines.append(engine)
        
        return sorted_engines
    
    async def _is_engine_healthy(self, engine_name: str, engine_type: str) -> bool:
        """Check if engine is healthy"""
        try:
            engine_dict = getattr(self, f"{engine_type}_engines")
            engine = engine_dict.get(engine_name)
            
            if not engine:
                return False
            
            health = engine.health_check()
            return health.get("status") == "healthy"
            
        except Exception as e:
            logger.error(f"Health check failed for {engine_type} engine {engine_name}: {e}")
            return False
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all engines"""
        health_status = {
            "manager_status": "healthy" if self.is_initialized else "unhealthy",
            "engines": {
                "stt": {},
                "tts": {},
                "emotion": {}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check STT engines
        for name, engine in self.stt_engines.items():
            try:
                health_status["engines"]["stt"][name] = engine.health_check()
            except Exception as e:
                health_status["engines"]["stt"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check TTS engines
        for name, engine in self.tts_engines.items():
            try:
                health_status["engines"]["tts"][name] = engine.health_check()
            except Exception as e:
                health_status["engines"]["tts"][name] = {
                    "status": "unhealthy", 
                    "error": str(e)
                }
        
        # Check emotion engines
        for name, engine in self.emotion_engines.items():
            try:
                health_status["engines"]["emotion"][name] = engine.health_check()
            except Exception as e:
                health_status["engines"]["emotion"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status
    
    def get_supported_languages(self, engine_type: Optional[str] = None) -> Dict[str, List[str]]:
        """Get supported languages by engine type"""
        if engine_type == "stt":
            return {name: engine.get_supported_languages() for name, engine in self.stt_engines.items()}
        elif engine_type == "tts":
            return {name: engine.get_supported_languages() for name, engine in self.tts_engines.items()}
        elif engine_type == "emotion":
            return {name: engine.get_supported_languages() for name, engine in self.emotion_engines.items()}
        else:
            return {
                "stt": {name: engine.get_supported_languages() for name, engine in self.stt_engines.items()},
                "tts": {name: engine.get_supported_languages() for name, engine in self.tts_engines.items()},
                "emotion": {name: engine.get_supported_languages() for name, engine in self.emotion_engines.items()}
            }
    
    def get_available_engines(self) -> Dict[str, List[str]]:
        """Get list of available engines by type"""
        return {
            "stt": list(self.stt_engines.keys()),
            "tts": list(self.tts_engines.keys()),
            "emotion": list(self.emotion_engines.keys())
        }
    
    async def shutdown(self) -> None:
        """Shutdown all engines gracefully"""
        logger.info("Shutting down Voice Engine Manager...")
        
        # Close all engines
        for engine in self.stt_engines.values():
            try:
                if hasattr(engine, 'shutdown'):
                    await engine.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down STT engine: {e}")
        
        for engine in self.tts_engines.values():
            try:
                if hasattr(engine, 'shutdown'):
                    await engine.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down TTS engine: {e}")
        
        for engine in self.emotion_engines.values():
            try:
                if hasattr(engine, 'shutdown'):
                    await engine.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down emotion engine: {e}")
        
        self.is_initialized = False
        logger.info("Voice Engine Manager shutdown complete")
