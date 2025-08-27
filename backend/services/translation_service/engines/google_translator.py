"""
Google Translate API integration
High-performance, reliable translation with broad language support
"""
import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlencode

from engines.base_translator import BaseTranslator
from config.settings import GOOGLE_TRANSLATE_API_KEY, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

class GoogleTranslator(BaseTranslator):
    """Google Translate API implementation"""
    
    def __init__(self):
        super().__init__("google", config)
        self.client = None
        self.api_key = config.get("api_key")
        self.rate_limit_delay = config.get("rate_limit_delay", 0.01)  # 10ms between requests
        
    async def initialize(self) -> bool:
        """Initialize Google Translate client"""
        try:
            if not self.api_key:
                logger.error("Google Translate API key not provided")
                return False
                
            # Initialize the client
            self.client = translate.Client(
                api_key=self.api_key,
                target_language="en"  # Default target, will be overridden
            )
            
            # Test connection with a simple translation
            test_result = self.client.translate("hello", target_language="es")
            if test_result and 'translatedText' in test_result:
                self.is_initialized = True
                self.supported_languages = set(SUPPORTED_LANGUAGES.keys())
                logger.info(f"Google Translator initialized successfully with {len(self.supported_languages)} languages")
                return True
            else:
                logger.error("Google Translate test translation failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Google Translator: {e}")
            return False
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TranslationResult:
        """Translate text using Google Translate"""
        start_time = time.time()
        
        if not self.is_initialized:
            raise RuntimeError("Google Translator not initialized")
        
        try:
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            # Prepare translation parameters
            translate_params = {
                "values": text,
                "target_language": target_language,
                "format_": "text"
            }
            
            # Add source language if specified
            if source_language and source_language != "auto":
                translate_params["source_language"] = source_language
            
            # Perform translation
            result = self.client.translate(**translate_params)
            
            # Extract results
            translated_text = result['translatedText']
            detected_source = result.get('detectedSourceLanguage', source_language)
            
            # Calculate confidence score (Google doesn't provide this, so we estimate)
            confidence_score = self._estimate_confidence(text, translated_text, detected_source, target_language)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Prepare metadata
            metadata = {
                "detected_source_language": detected_source,
                "model": "google-translate-v2",
                "format": "text",
                "domain": domain
            }
            
            if context:
                metadata.update(context)
            
            return TranslationResult(
                translated_text=translated_text,
                source_language=detected_source,
                target_language=target_language,
                confidence_score=confidence_score,
                engine_name=self.name,
                processing_time_ms=processing_time,
                metadata=metadata
            )
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Google Translate API error: {e}")
            raise RuntimeError(f"Translation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Google translation: {e}")
            raise RuntimeError(f"Translation failed: {e}")
    
    async def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[TranslationResult]:
        """Translate multiple texts efficiently"""
        start_time = time.time()
        
        if not self.is_initialized:
            raise RuntimeError("Google Translator not initialized")
        
        try:
            # Rate limiting for batch
            await asyncio.sleep(self.rate_limit_delay * len(texts))
            
            # Prepare batch translation
            translate_params = {
                "values": texts,
                "target_language": target_language,
                "format_": "text"
            }
            
            if source_language and source_language != "auto":
                translate_params["source_language"] = source_language
            
            # Perform batch translation
            results = self.client.translate(**translate_params)
            
            # Process results
            translations = []
            processing_time = int((time.time() - start_time) * 1000)
            
            for i, result in enumerate(results):
                translated_text = result['translatedText']
                detected_source = result.get('detectedSourceLanguage', source_language)
                
                confidence_score = self._estimate_confidence(
                    texts[i], translated_text, detected_source, target_language
                )
                
                metadata = {
                    "detected_source_language": detected_source,
                    "model": "google-translate-v2",
                    "format": "text",
                    "domain": domain,
                    "batch_index": i,
                    "batch_size": len(texts)
                }
                
                if context:
                    metadata.update(context)
                
                translations.append(TranslationResult(
                    translated_text=translated_text,
                    source_language=detected_source,
                    target_language=target_language,
                    confidence_score=confidence_score,
                    engine_name=self.name,
                    processing_time_ms=processing_time // len(texts),  # Distribute time
                    metadata=metadata
                ))
            
            return translations
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Google Translate batch API error: {e}")
            raise RuntimeError(f"Batch translation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Google batch translation: {e}")
            raise RuntimeError(f"Batch translation failed: {e}")
    
    async def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language using Google Translate"""
        if not self.is_initialized:
            raise RuntimeError("Google Translator not initialized")
        
        try:
            await asyncio.sleep(self.rate_limit_delay)
            
            result = self.client.detect_language(text)
            
            language = result['language']
            # Google provides confidence as a number, normalize to 0-1
            confidence = min(result.get('confidence', 0.9), 1.0)
            
            return language, confidence
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Google language detection error: {e}")
            raise RuntimeError(f"Language detection failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Google language detection: {e}")
            raise RuntimeError(f"Language detection failed: {e}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes"""
        return list(self.supported_languages)
    
    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if language pair is supported"""
        return (source in self.supported_languages or source == "auto") and \
               target in self.supported_languages
    
    async def get_quality_score(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Calculate quality score for Google translation"""
        # Google Translate generally provides high quality
        # Base score depends on language tier
        lang_info = SUPPORTED_LANGUAGES.get(target_language, {})
        tier = lang_info.get("tier", 3)
        
        base_scores = {1: 0.95, 2: 0.90, 3: 0.85}
        base_score = base_scores.get(tier, 0.80)
        
        # Adjust based on text characteristics
        length_factor = min(len(original_text) / 100, 1.0)  # Longer texts generally translate better
        
        return min(base_score + (length_factor * 0.05), 1.0)
    
    def _estimate_confidence(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Estimate translation confidence score"""
        # Base confidence depends on language pair and text characteristics
        lang_info = SUPPORTED_LANGUAGES.get(target_language, {})
        tier = lang_info.get("tier", 3)
        
        # Tier-based confidence
        base_confidence = {1: 0.92, 2: 0.88, 3: 0.82}.get(tier, 0.75)
        
        # Adjust for text length (longer texts generally more reliable)
        length_factor = min(len(original_text) / 200, 0.1)
        
        # Adjust for language similarity (e.g., Spanish-Portuguese vs English-Chinese)
        similarity_bonus = self._get_language_similarity_bonus(source_language, target_language)
        
        final_confidence = min(base_confidence + length_factor + similarity_bonus, 1.0)
        return max(final_confidence, 0.5)  # Minimum confidence threshold
    
    def _get_language_similarity_bonus(self, source: str, target: str) -> float:
        """Get confidence bonus for similar language pairs"""
        # Language family groupings for similarity bonus
        romance_languages = {"es", "fr", "it", "pt", "ro"}
        germanic_languages = {"en", "de", "nl", "sv", "da", "no"}
        slavic_languages = {"ru", "pl", "cs", "sk", "hr", "sr", "bg"}
        indic_languages = {"hi", "bn", "ta", "te", "gu", "kn", "ml", "mr", "pa", "ur"}
        
        language_families = [
            romance_languages, germanic_languages, slavic_languages, indic_languages
        ]
        
        for family in language_families:
            if source in family and target in family:
                return 0.05  # 5% bonus for same family
        
        return 0.0
    
    def estimate_cost(self, text: str, source_language: str, target_language: str) -> float:
        """Estimate Google Translate API cost"""
        # Google Translate pricing (as of 2024): $20 per 1M characters
        character_count = len(text)
        cost_per_character = 0.00002  # $20 / 1,000,000
        return character_count * cost_per_character
