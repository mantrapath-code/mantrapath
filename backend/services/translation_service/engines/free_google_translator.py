"""
Free Google Translate integration using googletrans library
No API key required - uses the free web interface
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from engines.base_translator import BaseTranslator, TranslationResult

try:
    from googletrans import Translator, LANGUAGES
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    LANGUAGES = {}

logger = logging.getLogger(__name__)

class FreeGoogleTranslator(BaseTranslator):
    """Free Google Translate using googletrans library"""
    
    def __init__(self, name: str = "free_google", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        self.translator = Translator() if GOOGLETRANS_AVAILABLE else None
        self.supported_languages = set(LANGUAGES.keys()) if GOOGLETRANS_AVAILABLE else set()
        self.base_url = "https://translate.googleapis.com"
        
    async def initialize(self) -> bool:
        """Initialize the Google Translator"""
        if not GOOGLETRANS_AVAILABLE:
            logger.error("googletrans library not available")
            return False
        
        try:
            # Test if translator works
            test_result = self.translator.translate("hello", dest="es")
            if test_result and test_result.text:
                self.is_initialized = True
                logger.info("Free Google Translator initialized successfully")
                return True
            else:
                logger.error("Google Translator test failed")
                self.is_initialized = False
                return False
        except Exception as e:
            logger.error(f"Failed to initialize Google Translator: {str(e)}")
            self.is_initialized = False
            return False
        
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TranslationResult:
        """
        Translate text using free Google Translate
        """
        if not GOOGLETRANS_AVAILABLE:
            logger.warning("googletrans library not available")
            return await self._fallback_translation(text, target_language, source_language)
        
        try:
            # Perform translation
            if source_language == "auto" or not source_language:
                source_language = None
                
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.translator.translate(
                    text, 
                    dest=target_language, 
                    src=source_language
                )
            )
            
            return TranslationResult(
                translated_text=result.text,
                source_language=result.src,
                target_language=target_language,
                confidence_score=0.85,  # Free Google Translate is generally reliable
                engine_name=self.name,
                processing_time_ms=0,
                metadata={
                    'detected_language': result.src != source_language,
                    'quality_score': 0.8
                }
            )
            
        except Exception as e:
            logger.error(f"Free Google Translate error: {str(e)}")
            return await self._fallback_translation(text, target_language, source_language)
    
    async def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language using free Google Translate"""
        if not GOOGLETRANS_AVAILABLE:
            return ("en", 0.5)
            
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.translator.detect(text)
            )
            
            return (result.lang, result.confidence if hasattr(result, 'confidence') else 0.8)
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return ("en", 0.5)
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages"""
        return list(self.supported_languages)
    
    async def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[TranslationResult]:
        """Translate multiple texts in a batch"""
        results = []
        for text in texts:
            result = await self.translate(text, source_language, target_language, domain, context)
            results.append(result)
        return results
    
    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if the engine supports the given language pair"""
        return source in self.supported_languages and target in self.supported_languages
    
    async def get_quality_score(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Calculate quality score for a translation"""
        if not translated_text or translated_text == original_text:
            return 0.5
        return 0.85  # Free Google Translate generally provides good quality
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the translation engine"""
        return {
            "name": self.name,
            "status": "healthy" if self.is_initialized else "not_initialized",
            "supported_languages_count": len(self.supported_languages),
            "timestamp": datetime.utcnow().isoformat(),
            "available": GOOGLETRANS_AVAILABLE
        }

    async def _fallback_translation(
        self, 
        text: str, 
        target_language: str, 
        source_language: Optional[str]
    ) -> TranslationResult:
        """Fallback when free translation fails"""
        return TranslationResult(
            translated_text=text,  # Return original text
            source_language=source_language or 'unknown',
            target_language=target_language,
            confidence_score=0.0,
            engine_name='fallback',
            processing_time_ms=0,
            metadata={'fallback': True, 'quality_score': 0.0}
        )
