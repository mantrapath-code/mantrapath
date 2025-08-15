"""
Base translator interface that all translation engines must implement
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

class TranslationResult:
    """Standard translation result structure"""
    def __init__(
        self,
        translated_text: str,
        source_language: str,
        target_language: str,
        confidence_score: float,
        engine_name: str,
        processing_time_ms: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.translated_text = translated_text
        self.source_language = source_language
        self.target_language = target_language
        self.confidence_score = confidence_score
        self.engine_name = engine_name
        self.processing_time_ms = processing_time_ms
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()

class BaseTranslator(ABC):
    """Abstract base class for all translation engines"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_initialized = False
        self.supported_languages = set()
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the translation engine"""
        pass
    
    @abstractmethod
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TranslationResult:
        """Translate text from source to target language"""
        pass
    
    @abstractmethod
    async def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[TranslationResult]:
        """Translate multiple texts in a batch"""
        pass
    
    @abstractmethod
    async def detect_language(
        self,
        text: str
    ) -> Tuple[str, float]:
        """Detect the language of the given text"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        pass
    
    @abstractmethod
    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if the engine supports the given language pair"""
        pass
    
    @abstractmethod
    async def get_quality_score(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Calculate quality score for a translation"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the translation engine"""
        return {
            "name": self.name,
            "status": "healthy" if self.is_initialized else "not_initialized",
            "supported_languages_count": len(self.supported_languages),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def validate_language_code(self, language_code: str) -> bool:
        """Validate language code format (ISO 639-1)"""
        return len(language_code) == 2 and language_code.islower()
    
    def estimate_cost(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Estimate the cost for translation (if applicable)"""
        return 0.0  # Default implementation for free engines
