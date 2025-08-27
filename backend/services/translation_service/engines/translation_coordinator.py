"""
Optimized Translation Coordinator with Caching
Manages translation using Bhashini and IndicTrans2 engines with Redis caching
"""
import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any
import redis.asyncio as redis

from .base_translator import BaseTranslator, TranslationResult
from .bhashini_translator import BhashiniTranslator
from .indictrans2_translator import IndicTrans2Translator

logger = logging.getLogger(__name__)

class TranslationCoordinator:
    """Optimized coordinator with lazy loading and caching for translation engines"""
    
    def __init__(self):
        self.engines: Dict[str, BaseTranslator] = {}
        self.engine_initialized: Dict[str, bool] = {}
        self.is_initialized = False
        
        # Caching
        self.redis_client = None
        self.cache_enabled = True
        self.cache_ttl = 86400  # 24 hours
        self.cache_stats = {"hits": 0, "misses": 0}
        
        # Indian language codes
        self.indian_languages = {
            'hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 'as', 'mr', 'ur',
            'ne', 'sd', 'kok', 'mai', 'sat', 'doi', 'mni', 'brx', 'bh'
        }
        
        # Engine priority for fast response
        self.engine_priority = {
            'bhashini': 1,      # Fast, government service (real data)
            'indictrans2': 2    # Slower but comprehensive (large model)
        }
        
    async def initialize(self) -> bool:
        """Fast initialization with cache setup - only initialize Bhashini for quick start"""
        try:
            # Setup Redis cache (optional)
            await self._setup_cache()
            
            # Only initialize Bhashini for fast startup (real data, no model download)
            logger.info("Fast initialization: Starting with Bhashini only...")
            
            self.engines['bhashini'] = BhashiniTranslator()
            self.engine_initialized['bhashini'] = False
            self.engine_initialized['indictrans2'] = False
            
            # Quick initialization of Bhashini (uses real data, no model download)
            bhashini_result = await self.engines['bhashini'].initialize()
            
            if bhashini_result:
                self.engine_initialized['bhashini'] = True
                logger.info("Bhashini initialized successfully - Service ready!")
                self.is_initialized = True
                
                # Initialize IndicTrans2 in background (don't wait)
                asyncio.create_task(self._initialize_indictrans2_background())
                
                return True
            else:
                logger.warning("Bhashini initialization failed, trying IndicTrans2...")
                # If Bhashini fails, initialize IndicTrans2 synchronously
                return await self._initialize_indictrans2_sync()
                
        except Exception as e:
            logger.error(f"Error in fast initialization: {e}")
            # Fallback to IndicTrans2
            return await self._initialize_indictrans2_sync()
    
    async def _setup_cache(self):
        """Setup Redis cache connection"""
        try:
            self.redis_client = redis.from_url("redis://localhost:6379/3")
            await self.redis_client.ping()
            logger.info("✅ Redis cache connected successfully")
            self.cache_enabled = True
        except Exception as e:
            logger.warning(f"Redis cache not available: {e}. Continuing without cache.")
            self.cache_enabled = False
    
    async def _initialize_indictrans2_background(self):
        """Initialize IndicTrans2 in background (non-blocking)"""
        try:
            logger.info("Initializing IndicTrans2 in background...")
            self.engines['indictrans2'] = IndicTrans2Translator()
            result = await self.engines['indictrans2'].initialize()
            
            if result:
                self.engine_initialized['indictrans2'] = True
                logger.info("IndicTrans2 initialized successfully in background")
            else:
                logger.warning("IndicTrans2 background initialization failed")
        except Exception as e:
            logger.error(f"IndicTrans2 background initialization error: {e}")
    
    async def _initialize_indictrans2_sync(self) -> bool:
        """Initialize IndicTrans2 synchronously (fallback)"""
        try:
            logger.info("Initializing IndicTrans2 synchronously...")
            self.engines['indictrans2'] = IndicTrans2Translator()
            result = await self.engines['indictrans2'].initialize()
            
            if result:
                self.engine_initialized['indictrans2'] = True
                self.is_initialized = True
                logger.info("IndicTrans2 initialized successfully")
                return True
            else:
                logger.error("IndicTrans2 initialization failed")
                return False
        except Exception as e:
            logger.error(f"IndicTrans2 initialization error: {e}")
            return False
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> TranslationResult:
        """Fast translation with caching using the best available engine"""
        
        if not self.is_initialized:
            await self.initialize()
        
        # Detect source language if needed (use fast method)
        if source_language == "auto":
            source_language = await self._fast_detect_language(text)
        
        # Check cache first
        cached_result = await self._get_cached_translation(text, source_language, target_language)
        if cached_result:
            self.cache_stats["hits"] += 1
            logger.info(f"🚀 Cache HIT: {source_language}->{target_language}")
            return cached_result
        
        self.cache_stats["misses"] += 1
        logger.info(f"🔍 Cache MISS: {source_language}->{target_language}")
        
        # Get engine priority for this language pair
        engine_priority = self._get_fast_engine_priority(source_language, target_language)
        
        # Try engines in priority order (fastest first)
        for engine_name in engine_priority:
            try:
                # Check if engine is available and initialized
                if engine_name not in self.engines:
                    continue
                    
                if not self.engine_initialized.get(engine_name, False):
                    # Try to initialize the engine if not ready
                    if engine_name == 'indictrans2' and 'indictrans2' not in self.engines:
                        logger.info(f"Lazy loading {engine_name} for translation...")
                        self.engines['indictrans2'] = IndicTrans2Translator()
                        init_result = await self.engines['indictrans2'].initialize()
                        self.engine_initialized['indictrans2'] = init_result
                        if not init_result:
                            continue
                    elif not self.engine_initialized.get(engine_name, False):
                        continue
                
                engine = self.engines[engine_name]
                result = await engine.translate(text, source_language, target_language, domain, context)
                
                # Cache the result if it's good
                if result.confidence_score >= 0.5:
                    await self._cache_translation(text, source_language, target_language, result)
                
                # Return immediately if we get a good result (fast response)
                if result.confidence_score >= 0.7:
                    logger.info(f"⚡ Fast translation successful with {engine_name}")
                    return result
                    
                # If result is not great but acceptable, still return for speed
                elif result.confidence_score >= 0.5:
                    logger.info(f"✅ Acceptable translation with {engine_name}")
                    return result
                    
            except Exception as e:
                logger.error(f"Error with {engine_name} engine: {e}")
                continue
        
        # Fallback - return original text with low confidence
        logger.warning("All engines failed, returning fallback")
        fallback_result = TranslationResult(
            translated_text=text,
            source_language=source_language,
            target_language=target_language,
            confidence_score=0.1,
            engine="fallback"
        )
        
        # Don't cache fallback results
        return fallback_result
    
    def _get_fast_engine_priority(self, source_language: str, target_language: str) -> List[str]:
        """Get engine priority optimized for speed"""
        
        # For Indian languages, use Bhashini first (fast, real data)
        if (source_language in self.indian_languages or 
            target_language in self.indian_languages):
            return ['bhashini', 'indictrans2']
        else:
            # For non-Indian languages, try Bhashini first (fast), then IndicTrans2
            return ['bhashini', 'indictrans2']
    
    async def _fast_detect_language(self, text: str) -> str:
        """Fast language detection - simple heuristics first"""
        
        # Simple character-based detection for common Indian languages
        if any(char in text for char in 'नमस्तेधन्यवादकैसेहैं'):
            return 'hi'  # Hindi (Devanagari)
        elif any(char in text for char in 'বাংলাধন্যবাদকেমনআছেন'):
            return 'bn'  # Bengali
        elif any(char in text for char in 'தமிழ்நன்றிஎப்படிஇருக்கிறீர்கள்'):
            return 'ta'  # Tamil
        elif any(char in text for char in 'తెలుగుధన్యవాదాలుఎలాఉన్నారు'):
            return 'te'  # Telugu
        elif any(char in text for char in 'മലയാളംനന്ദിഎങ്ങനെയുണ്ട്'):
            return 'ml'  # Malayalam
        elif any(char in text for char in 'ಕನ್ನಡಧನ್ಯವಾದಹೇಗಿದ್ದೀರಿ'):
            return 'kn'  # Kannada
        elif any(char in text for char in 'ગુજરાતીઆભારકેમછો'):
            return 'gu'  # Gujarati
        elif any(char in text for char in 'اردوشکریہکیسےہیں'):
            return 'ur'  # Urdu
        
        # If no Indian script detected, assume English for speed
        return 'en'
    
    async def detect_language(self, text: str) -> str:
        """Detect language of text"""
        
        # Try Bhashini first for Indian language detection
        if 'bhashini' in self.engines:
            try:
                result = await self.engines['bhashini'].detect_language(text)
                if result:
                    # Handle tuple result (language, confidence)
                    if isinstance(result, tuple):
                        return result[0]
                    return str(result)
            except Exception as e:
                logger.error(f"Bhashini language detection error: {e}")
        
        # Try IndicTrans2
        if 'indictrans2' in self.engines:
            try:
                result = await self.engines['indictrans2'].detect_language(text)
                if result:
                    # Handle tuple result (language, confidence)
                    if isinstance(result, tuple):
                        return result[0]
                    return str(result)
            except Exception as e:
                logger.error(f"IndicTrans2 language detection error: {e}")
        
        # Fallback to English
        return "en"
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages"""
        
        all_languages = set()
        
        # Collect languages from all engines
        for engine in self.engines.values():
            if hasattr(engine, 'supported_languages'):
                all_languages.update(engine.supported_languages)
        
        # Add Indian languages explicitly
        all_languages.update(self.indian_languages)
        
        # Add common international languages
        all_languages.update(['en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'ru', 'ar', 'pt'])
        
        return sorted(list(all_languages))
    
    async def health_check(self) -> bool:
        """Check health of translation service"""
        
        if not self.is_initialized:
            return False
        
        # Check if at least one engine is working
        for engine_name, engine in self.engines.items():
            try:
                health = await engine.health_check()
                if health:
                    return True
            except Exception as e:
                logger.error(f"Health check failed for {engine_name}: {e}")
                continue
        
        return False
    
    def _is_indian_language(self, language_code: str) -> bool:
        """Check if language is an Indian language"""
        return language_code in self.indian_languages
    
    # Cache Management Methods
    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        cache_data = f"{text}:{source_lang}:{target_lang}"
        return f"translation:{hashlib.md5(cache_data.encode()).hexdigest()}"
    
    async def _get_cached_translation(self, text: str, source_lang: str, target_lang: str) -> Optional[TranslationResult]:
        """Get translation from cache"""
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(text, source_lang, target_lang)
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return TranslationResult(
                    translated_text=data['translated_text'],
                    source_language=data['source_language'],
                    target_language=data['target_language'],
                    confidence_score=data['confidence_score'],
                    engine=data['engine'] + "_cached"
                )
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        
        return None
    
    async def _cache_translation(self, text: str, source_lang: str, target_lang: str, result: TranslationResult):
        """Cache translation result"""
        if not self.cache_enabled or not self.redis_client or result.confidence_score < 0.5:
            return
        
        try:
            cache_key = self._generate_cache_key(text, source_lang, target_lang)
            cache_data = {
                'translated_text': result.translated_text,
                'source_language': result.source_language,
                'target_language': result.target_language,
                'confidence_score': result.confidence_score,
                'engine': result.engine
            }
            
            await self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_data))
            logger.debug(f"💾 Cached translation: {source_lang}->{target_lang}")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_enabled": self.cache_enabled,
            "total_requests": total_requests,
            "cache_hits": self.cache_stats["hits"],
            "cache_misses": self.cache_stats["misses"],
            "hit_rate_percent": round(hit_rate, 2)
        }
