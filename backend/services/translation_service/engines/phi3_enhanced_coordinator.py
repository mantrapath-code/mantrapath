"""
Enhanced Translation Coordinator with Phi-3 Integration
Combines Bhashini API for Indian languages with Phi-3 for enhanced context awareness
"""
import asyncio
import hashlib
import json
import time
import os
from typing import Dict, List, Optional, Any, Union
import logging
import redis.asyncio as redis
import httpx

from .base_translator import BaseTranslator, TranslationResult
from .anuvadini_translator import AnuvadiniTranslator

logger = logging.getLogger(__name__)

class Phi3EnhancedTranslationCoordinator:
    """Enhanced coordinator using both Bhashini and Phi-3 for superior translation"""
    
    def __init__(self):
        self.engines = {}
        self.engine_initialized = {}
        self.is_initialized = False
        
        # Models Service client for Phi-3
        self.models_service_url = os.getenv('MODELS_SERVICE_URL', 'http://models-service:8080')
        self.models_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0)
        )
        
        # Caching
        self.redis_client = None
        self.cache_enabled = False
        self.cache_ttl = 86400  # 24 hours
        self.cache_stats = {"hits": 0, "misses": 0}
        
        # Enhanced Indian languages support (22 official + regional variants)
        self.indian_languages = [
            # Constitutional languages (official)
            "hi",   # Hindi - Most widely spoken
            "bn",   # Bengali - 2nd most spoken
            "te",   # Telugu - Large South Indian population
            "ta",   # Tamil - Significant South Indian language
            "mr",   # Marathi - Western India
            "gu",   # Gujarati - Business language of West India
            "ur",   # Urdu - Significant Muslim population
            "kn",   # Kannada - Karnataka state
            "ml",   # Malayalam - Kerala state
            "pa",   # Punjabi - Punjab region
            "or",   # Odia - Odisha state
            "as",   # Assamese - Assam state
            
            # Additional supported languages
            "ne",   # Nepali
            "sd",   # Sindhi
            "kok",  # Konkani
            "mai",  # Maithili
            "sat",  # Santali
            "doi",  # Dogri
            "mni",  # Manipuri
            "brx",  # Bodo
            "bh"    # Bhojpuri
        ]
        
        # Global languages supported by Phi-3
        self.global_languages = [
            "en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar"
        ]
        
        # All supported languages
        self.all_supported_languages = list(set(self.indian_languages + self.global_languages))
    
    async def initialize(self):
        """Initialize both Bhashini and Phi-3 engines"""
        try:
            logger.info("🚀 Initializing Enhanced Translation Coordinator...")
            
            # Initialize Redis cache if available
            await self._init_cache()
            
            # Initialize Bhashini engine for Indian languages
            await self._initialize_bhashini()
            
            # Check Models Service availability for Phi-3
            await self._check_models_service()
            
            self.is_initialized = True
            logger.info("✅ Enhanced Translation Coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize coordinator: {e}")
            raise
    
    async def _init_cache(self):
        """Initialize Redis cache if available"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379/2")
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            self.cache_enabled = True
            logger.info("✅ Redis cache enabled")
        except Exception as e:
            logger.warning(f"⚠️ Redis cache not available: {e}")
            self.cache_enabled = False
    
    async def _initialize_bhashini(self):
        """Initialize Bhashini engine for Indian languages"""
        try:
            # Create configuration for Bhashini API
            bhashini_config = {
                "api_key": os.getenv("BHASHINI_API_KEY"),
                "user_id": os.getenv("BHASHINI_USER_ID", "demo-user"),
                "ulca_api_key": os.getenv("ULCA_API_KEY"),
                "compute_url": os.getenv("BHASHINI_COMPUTE_URL", "https://dhruva-api.bhashini.gov.in/services/inference"),
                "api_version": os.getenv("BHASHINI_API_VERSION", "v1")
            }
            
            # Initialize Anuvadini translator
            anuvadini = AnuvadiniTranslator(config=bhashini_config)
            # Anuvadini initialization is fast (uses real API)
            if await anuvadini.initialize():
                self.engines["anuvadini"] = anuvadini
                self.engine_initialized["anuvadini"] = True
                logger.info("✅ Bhashini/Anuvadini engine initialized")
            else:
                logger.warning("⚠️ Bhashini/Anuvadini engine failed to initialize")
                
        except Exception as e:
            logger.error(f"❌ Bhashini initialization failed: {e}")
    
    async def _check_models_service(self):
        """Check if Models Service with Phi-3 is available"""
        try:
            response = await self.models_client.get(f"{self.models_service_url}/health")
            if response.status_code == 200:
                logger.info("✅ Models Service (Phi-3) is available")
                return True
            else:
                logger.warning("⚠️ Models Service not responding properly")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Models Service not available: {e}")
            return False
    
    async def translate(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        domain: Optional[str] = None,
        context: Optional[str] = None
    ) -> TranslationResult:
        """Enhanced translation using both Bhashini and Phi-3"""
        
        if not self.is_initialized:
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.0,
                engine="none"
            )
        
        start_time = time.time()
        
        try:
            # Auto-detect language if needed
            if source_language == "auto":
                source_language = await self.detect_language(text)
            
            # Check cache first
            cache_key = self._get_cache_key(text, source_language, target_language, domain)
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return cached_result
            
            # Choose translation strategy based on language pair
            result = await self._choose_translation_strategy(
                text, source_language, target_language, domain, context
            )
            
            # Add processing time
            result.processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Cache the result
            await self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return TranslationResult(
                translated_text=text,
                source_language=source_language,
                target_language=target_language,
                confidence_score=0.0,
                engine="error"
            )
    
    async def _choose_translation_strategy(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str],
        context: Optional[str]
    ) -> TranslationResult:
        """Choose the best translation strategy based on language pair and context"""
        
        # Strategy 1: Use Phi-3 for context-aware translation (preferred for complex text)
        if len(text.split()) > 5 or context:  # Complex text or has context
            phi3_result = await self._translate_with_phi3(
                text, source_language, target_language, context
            )
            if phi3_result and phi3_result.confidence_score > 0.7:
                logger.info(f"Used Phi-3 for context-aware translation: {source_language} -> {target_language}")
                return phi3_result
        
        # Strategy 2: Use Bhashini for Indian language pairs (high accuracy)
        if (source_language in self.indian_languages or target_language in self.indian_languages):
            if "anuvadini" in self.engines:
                try:
                    bhashini_result = await self.engines["anuvadini"].translate(
                        text, source_language, target_language, domain
                    )
                    if bhashini_result.confidence_score > 0.6:
                        logger.info(f"Used Bhashini for Indian languages: {source_language} -> {target_language}")
                        return bhashini_result
                except Exception as e:
                    logger.warning(f"Bhashini translation failed: {e}")
        
        # Strategy 3: Fallback to Phi-3 for all other cases
        phi3_result = await self._translate_with_phi3(
            text, source_language, target_language, context
        )
        if phi3_result:
            logger.info(f"Used Phi-3 as fallback: {source_language} -> {target_language}")
            return phi3_result
        
        # Strategy 4: Final fallback - return original text
        logger.warning(f"All translation strategies failed for: {source_language} -> {target_language}")
        return TranslationResult(
            translated_text=text,
            source_language=source_language,
            target_language=target_language,
            confidence_score=0.0,
            engine="fallback"
        )
    
    async def _translate_with_phi3(
        self,
        text: str,
        source_language: str,
        target_language: str,
        context: Optional[str] = None
    ) -> Optional[TranslationResult]:
        """Translate using Phi-3 via Models Service"""
        try:
            payload = {
                "text": text,
                "source_language": source_language,
                "target_language": target_language
            }
            if context:
                payload["context"] = context
            
            response = await self.models_client.post(
                f"{self.models_service_url}/api/v1/translation/translate",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return TranslationResult(
                        translated_text=data["translated_text"],
                        source_language=data["source_language"],
                        target_language=data["target_language"],
                        confidence_score=data["confidence_score"],
                        engine="phi3",
                        processing_time_ms=data.get("processing_time_ms", 0)
                    )
            else:
                logger.warning(f"Phi-3 translation failed with status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Phi-3 translation error: {e}")
        
        return None
    
    async def detect_language(self, text: str) -> str:
        """Enhanced language detection using both Phi-3 and fallbacks"""
        try:
            # Try Phi-3 first for better accuracy
            response = await self.models_client.post(
                f"{self.models_service_url}/api/v1/translation/detect-language",
                json={"text": text},
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_lang = data.get("language", "en")
                if detected_lang in self.all_supported_languages:
                    return detected_lang
                    
        except Exception as e:
            logger.warning(f"Phi-3 language detection failed: {e}")
        
        # Fallback: Simple heuristic detection
        return self._simple_language_detection(text)
    
    def _simple_language_detection(self, text: str) -> str:
        """Simple fallback language detection"""
        # Check for common Indian language patterns
        if any(ord(char) in range(0x0900, 0x097F) for char in text):  # Devanagari
            return "hi"
        elif any(ord(char) in range(0x0980, 0x09FF) for char in text):  # Bengali
            return "bn"
        elif any(ord(char) in range(0x0B80, 0x0BFF) for char in text):  # Tamil
            return "ta"
        elif any(ord(char) in range(0x0C00, 0x0C7F) for char in text):  # Telugu
            return "te"
        else:
            return "en"  # Default to English
    
    def _get_cache_key(self, text: str, source: str, target: str, domain: Optional[str]) -> str:
        """Generate cache key for translation"""
        key_string = f"{text}:{source}:{target}:{domain or 'none'}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_from_cache(self, cache_key: str) -> Optional[TranslationResult]:
        """Get translation from cache"""
        if not self.cache_enabled:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                self.cache_stats["hits"] += 1
                return TranslationResult(**data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        self.cache_stats["misses"] += 1
        return None
    
    async def _save_to_cache(self, cache_key: str, result: TranslationResult):
        """Save translation to cache"""
        if not self.cache_enabled:
            return
        
        try:
            data = {
                "translated_text": result.translated_text,
                "source_language": result.source_language,
                "target_language": result.target_language,
                "confidence_score": result.confidence_score,
                "engine": result.engine,
                "processing_time_ms": result.processing_time_ms,
                "cache_hit": False
            }
            await self.redis_client.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(data)
            )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages"""
        return self.all_supported_languages
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get translation statistics"""
        return {
            "engines_initialized": list(self.engine_initialized.keys()),
            "cache_enabled": self.cache_enabled,
            "cache_stats": self.cache_stats,
            "supported_languages_count": len(self.all_supported_languages),
            "indian_languages_count": len(self.indian_languages),
            "models_service_url": self.models_service_url
        }
    
    async def close(self):
        """Clean up resources"""
        if self.models_client:
            await self.models_client.aclose()
        if self.redis_client:
            await self.redis_client.aclose()
