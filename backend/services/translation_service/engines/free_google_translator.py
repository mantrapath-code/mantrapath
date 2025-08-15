"""
Free Google Translate integration using googletrans library
No API key required - uses the free web interface
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple

try:
    from googletrans import Translator, LANGUAGES
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    LANGUAGES = {}

logger = logging.getLogger(__name__)

class FreeGoogleTranslator:
    """Free Google Translate using googletrans library"""
    
    def __init__(self):
        self.translator = Translator() if GOOGLETRANS_AVAILABLE else None
        self.supported_languages = list(LANGUAGES.keys()) if GOOGLETRANS_AVAILABLE else []
        self.is_initialized = False
        
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
                return False
        except Exception as e:
            logger.error(f"Failed to initialize Google Translator: {str(e)}")
            return False
        
    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
            
            return {
                'translated_text': result.text,
                'source_language': result.src,
                'target_language': target_language,
                'confidence_score': 0.85,  # Free Google Translate is generally reliable
                'engine': 'free_google',
                'metadata': {
                    'detected_language': result.src != source_language,
                    'quality_score': 0.8
                },
                'processing_time_ms': 0
            }
            
        except Exception as e:
            logger.error(f"Free Google Translate error: {str(e)}")
            return await self._fallback_translation(text, target_language, source_language)
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language using free Google Translate"""
        if not GOOGLETRANS_AVAILABLE:
            return {"language": "en", "confidence": 0.5}
            
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.translator.detect(text)
            )
            
            return {
                "language": result.lang,
                "confidence": result.confidence if hasattr(result, 'confidence') else 0.8
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {"language": "en", "confidence": 0.5}
    
    async def get_supported_languages(self) -> List[str]:
        """Get supported languages"""
        return self.supported_languages
    
    async def _fallback_translation(
        self, 
        text: str, 
        target_language: str, 
        source_language: Optional[str]
    ) -> Dict[str, Any]:
        """Fallback when free translation fails"""
        return {
            'translated_text': text,  # Return original text
            'source_language': source_language or 'unknown',
            'target_language': target_language,
            'confidence_score': 0.0,
            'engine': 'fallback',
            'metadata': {'fallback': True, 'quality_score': 0.0},
            'processing_time_ms': 0
        }
