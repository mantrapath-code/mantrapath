"""
Lightweight Translation Engine for Resource-Constrained Environments
Uses smaller models and external APIs for translation
"""
import logging
from typing import Dict, List, Any, Tuple, Optional
import httpx
from .base_translator import BaseTranslator, TranslationResult

logger = logging.getLogger(__name__)

class LightweightTranslator(BaseTranslator):
    """Lightweight translator using external APIs and smaller models"""
    
    def __init__(self, name: str = "lightweight", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config or {})
        self.supported_languages = {
            'en', 'hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 
            'as', 'mr', 'ur', 'ne', 'sd', 'es', 'fr', 'de', 'zh', 'ja', 'ko'
        }
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize HTTP client for API calls"""
        try:
            self.client = httpx.AsyncClient(timeout=30.0)
            self.is_initialized = True
            logger.info("Lightweight translator initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize lightweight translator: {e}")
            return False
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TranslationResult:
        """Translate using multiple fallback APIs"""
        try:
            # Try Google Translate API (free tier)
            result = await self._try_google_translate(text, source_language, target_language)
            if result.translated_text:
                return result
                
            # Fallback to LibreTranslate (open source)
            result = await self._try_libretranslate(text, source_language, target_language)
            if result.translated_text:
                return result
                
            # Last fallback: return original text with warning
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.1,
                engine=self.name,
                metadata={"warning": "Translation services unavailable, returned original text"}
            )
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.0,
                engine=self.name,
                metadata={"error": str(e)}
            )
    
    async def _try_google_translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Try Google Translate (free tier, limited)"""
        try:
            # Using Google Translate's free web interface (not official API)
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang if source_lang != 'auto' else 'auto',
                'tl': target_lang,
                'dt': 't',
                'q': text
            }
            
            if self.client:
                response = await self.client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    translated_text = ''.join([item[0] for item in data[0] if item[0]])
                    detected_lang = data[2] if len(data) > 2 else source_lang
                    
                    return TranslationResult(
                        translated_text=translated_text,
                        source_language=detected_lang,
                        target_language=target_lang,
                        confidence_score=0.8,
                        engine=f"{self.name}_google",
                        metadata={"api": "google_web"}
                    )
        except Exception as e:
            logger.warning(f"Google Translate failed: {e}")
        
        return TranslationResult("", source_lang, target_lang, 0.0, self.name)
    
    async def _try_libretranslate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Try LibreTranslate (open source, self-hostable)"""
        try:
            # Using public LibreTranslate instance
            url = "https://libretranslate.pussthecat.org/translate"
            data = {
                'q': text,
                'source': source_lang if source_lang != 'auto' else 'auto',
                'target': target_lang
            }
            
            if self.client:
                response = await self.client.post(url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    
                    return TranslationResult(
                        translated_text=result.get('translatedText', ''),
                        source_language=result.get('detectedLanguage', {}).get('language', source_lang),
                        target_language=target_lang,
                        confidence_score=result.get('detectedLanguage', {}).get('confidence', 0.7),
                        engine=f"{self.name}_libre",
                        metadata={"api": "libretranslate"}
                    )
        except Exception as e:
            logger.warning(f"LibreTranslate failed: {e}")
        
        return TranslationResult("", source_lang, target_lang, 0.0, self.name)
    
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
    
    def get_supported_languages(self) -> List[str]:
        """Return supported language codes"""
        return sorted(list(self.supported_languages))
    
    async def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language using Google's detection"""
        try:
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'auto',
                'tl': 'en',
                'dt': 't',
                'q': text[:100]  # Limit text for detection
            }
            
            if self.client:
                response = await self.client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    detected_lang = data[2] if len(data) > 2 else 'unknown'
                    return detected_lang, 0.8
                    
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
        
        return 'unknown', 0.0
    
    def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """Check if the engine supports a language pair"""
        return (source_lang in self.supported_languages or source_lang == 'auto') and target_lang in self.supported_languages
    
    def get_quality_score(self, source_lang: str, target_lang: str) -> float:
        """Get quality score for a language pair"""
        if not self.supports_language_pair(source_lang, target_lang):
            return 0.0
        
        # Higher quality for Indian languages
        if source_lang in {'hi', 'bn', 'ta', 'te', 'ml'} or target_lang in {'hi', 'bn', 'ta', 'te', 'ml'}:
            return 0.7
        
        # Standard quality for other supported languages
        return 0.6
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.aclose()
