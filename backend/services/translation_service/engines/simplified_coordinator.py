"""
Simplified Translation Coordinator - Real Data + Bhashini Only
Fast startup without heavy AI model dependencies
"""
import asyncio
import hashlib
import json
import time
import os
from typing import Dict, List, Optional, Any, Union
import logging
import redis.asyncio as redis

from .base_translator import BaseTranslator, TranslationResult
from .anuvadini_translator import AnuvadiniTranslator

logger = logging.getLogger(__name__)

class SimplifiedTranslationCoordinator:
    """Simplified coordinator using only Bhashini and real data"""
    
    def __init__(self):
        self.engines = {}
        self.engine_initialized = {}
        self.is_initialized = False
        
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
            "sa",   # Sanskrit (classical)
            "kok",  # Konkani
            "mai",  # Maithili
            "sat",  # Santali
            "doi",  # Dogri
            "mni",  # Manipuri (Meitei)
            "brx",  # Bodo
            "bh",   # Bhojpuri
            "gom",  # Goan Konkani
            
            # Regional variants and dialects
            "raj",  # Rajasthani
            "bhb",  # Bhili
            "mag",  # Magahi
            "hne",  # Chhattisgarhi
            "grt",  # Garo
            "lus",  # Mizo
        ]
        
        # International languages with good translation support
        self.international_languages = [
            "en",   # English - Primary international language
            "es",   # Spanish
            "fr",   # French
            "de",   # German
            "it",   # Italian
            "pt",   # Portuguese
            "ru",   # Russian
            "ja",   # Japanese
            "ko",   # Korean
            "zh",   # Chinese (Simplified)
            "ar",   # Arabic
        ]
        
        # Language groups for intelligent routing
        self.language_groups = {
            "north_indian": ["hi", "ur", "pa", "ne", "sd", "kok", "mai", "doi", "raj", "bhb", "mag", "hne"],
            "south_indian": ["te", "ta", "kn", "ml"],
            "east_indian": ["bn", "as", "or", "sat", "grt", "lus"],
            "west_indian": ["mr", "gu", "gom"],
            "northeast": ["as", "mni", "brx", "grt", "lus"],
            "classical": ["sa", "ur"]
        }
        
        # High-quality language pairs (known to work well)
        self.optimized_pairs = {
            ("hi", "en"), ("en", "hi"),  # Hindi-English (most common)
            ("bn", "en"), ("en", "bn"),  # Bengali-English
            ("te", "en"), ("en", "te"),  # Telugu-English
            ("ta", "en"), ("en", "ta"),  # Tamil-English
            ("mr", "en"), ("en", "mr"),  # Marathi-English
            ("gu", "en"), ("en", "gu"),  # Gujarati-English
            ("ur", "en"), ("en", "ur"),  # Urdu-English
            ("kn", "en"), ("en", "kn"),  # Kannada-English
            ("ml", "en"), ("en", "ml"),  # Malayalam-English
            ("pa", "en"), ("en", "pa"),  # Punjabi-English
            ("or", "en"), ("en", "or"),  # Odia-English
            ("as", "en"), ("en", "as"),  # Assamese-English
            
            # Inter-Indian language pairs
            ("hi", "bn"), ("bn", "hi"),  # Hindi-Bengali
            ("hi", "ta"), ("ta", "hi"),  # Hindi-Tamil
            ("hi", "te"), ("te", "hi"),  # Hindi-Telugu
            ("hi", "mr"), ("mr", "hi"),  # Hindi-Marathi
        }
        
        self.all_languages = self.indian_languages + self.international_languages
        
        logger.info("Simplified Translation Coordinator initialized")

    async def initialize(self) -> bool:
        """Initialize the coordinator with fast startup"""
        start_time = time.time()
        logger.info("🚀 Starting fast initialization...")
        
        try:
            # Setup cache first
            await self._setup_cache()
            
            # Initialize only Anuvadini (Bhashini) translator with credentials
            logger.info("Initializing Anuvadini (Bhashini) translator...")
            
            # Create configuration for Bhashini API
            bhashini_config = {
                "api_key": os.getenv("BHASHINI_API_KEY"),
                "user_id": os.getenv("BHASHINI_USER_ID"),
                "base_url": os.getenv("BHASHINI_BASE_URL", "https://meity-auth.ulcacontrib.org"),
                "compute_url": os.getenv("BHASHINI_COMPUTE_URL", "https://dhruva-api.bhashini.gov.in/services/inference"),
                "api_version": os.getenv("BHASHINI_API_VERSION", "v1")
            }
            
            self.engines['bhashini'] = AnuvadiniTranslator(config=bhashini_config)
            
            # Anuvadini initialization is fast (uses real API)
            bhashini_result = await self.engines['bhashini'].initialize()
            
            if bhashini_result:
                self.engine_initialized['bhashini'] = True
                self.is_initialized = True
                
                elapsed_time = time.time() - start_time
                logger.info(f"✅ Simplified coordinator initialized in {elapsed_time:.3f}s")
                logger.info("🌐 Translation engines ready: Bhashini (Indian languages)")
                return True
            else:
                logger.error("❌ Bhashini initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Initialization error: {e}")
            return False
    
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

    async def translate(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        domain: Optional[str] = None
    ) -> TranslationResult:
        """Translate text using available engines with intelligent routing for Indian languages"""
        
        if not self.is_initialized:
            raise Exception("Translation coordinator not initialized")
        
        # Language pair detection and optimization
        if source_language == "auto":
            source_language = await self.detect_language(text)
        
        # Check if it's a high-quality pair
        is_optimized_pair = (source_language, target_language) in self.optimized_pairs
        
        # Check cache first - prioritize for optimized pairs
        if self.cache_enabled:
            cached_result = await self._get_cached_translation(text, source_language, target_language)
            if cached_result:
                self.cache_stats["hits"] += 1
                logger.debug(f"🚀 Cache hit for {source_language}->{target_language}")
                return cached_result
            
            self.cache_stats["misses"] += 1
        
        start_time = time.time()
        
        try:
            # Intelligent routing based on language pair
            if self._is_indian_to_indian_pair(source_language, target_language):
                # For Indian-to-Indian translations, use specific optimizations
                result = await self._translate_indian_pair(text, source_language, target_language, domain)
            elif self._is_indian_language(source_language) or self._is_indian_language(target_language):
                # For Indian-English pairs, use Bhashini (optimized for these)
                result = await self._translate_with_bhashini(text, source_language, target_language, domain)
            else:
                # For international pairs, use Bhashini with fallback
                result = await self._translate_international_pair(text, source_language, target_language, domain)
            
            # Add processing time
            processing_time = int((time.time() - start_time) * 1000)
            result.processing_time_ms = processing_time
            
            # Cache high-quality results and optimized pairs more aggressively
            cache_threshold = 0.3 if is_optimized_pair else 0.5
            if self.cache_enabled and result.confidence_score >= cache_threshold:
                await self._cache_translation(text, source_language, target_language, result)
            
            logger.info(f"✅ Translation: {source_language}->{target_language} via {result.engine} ({processing_time}ms)")
            return result
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise Exception(f"Translation failed: {str(e)}")

    async def _translate_indian_pair(self, text: str, source_lang: str, target_lang: str, domain: Optional[str]) -> TranslationResult:
        """Optimized translation for Indian language pairs"""
        # Use Bhashini for Indian languages (it has better Indian language support)
        return await self.engines['bhashini'].translate(
            text=text,
            source_language=source_lang,
            target_language=target_lang,
            domain=domain
        )
    
    async def _translate_with_bhashini(self, text: str, source_lang: str, target_lang: str, domain: Optional[str]) -> TranslationResult:
        """Use Bhashini translator for Indian-English pairs"""
        return await self.engines['bhashini'].translate(
            text=text,
            source_language=source_lang,
            target_language=target_lang,
            domain=domain
        )
    
    async def _translate_international_pair(self, text: str, source_lang: str, target_lang: str, domain: Optional[str]) -> TranslationResult:
        """Handle international language pairs"""
        # Try Bhashini first, which may have some international support
        return await self.engines['bhashini'].translate(
            text=text,
            source_language=source_lang,
            target_language=target_lang,
            domain=domain
        )
    
    def _is_indian_to_indian_pair(self, source_lang: str, target_lang: str) -> bool:
        """Check if both languages are Indian languages"""
        return (self._is_indian_language(source_lang) and 
                self._is_indian_language(target_lang) and 
                source_lang != target_lang)
    
    def _get_language_group(self, language_code: str) -> Optional[str]:
        """Get the language group for intelligent routing"""
        for group, languages in self.language_groups.items():
            if language_code in languages:
                return group
        return None

    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages"""
        return self.all_languages

    def get_indian_languages(self) -> List[str]:
        """Get list of supported Indian languages"""
        return self.indian_languages

    def get_international_languages(self) -> List[str]:
        """Get list of supported international languages"""
        return self.international_languages

    async def detect_language(self, text: str) -> str:
        """Detect language of given text (simplified version)"""
        # Simple language detection using word patterns
        text_lower = text.lower()
        
        # Simple heuristics for common Indian languages
        if any(char in text for char in "हिंदी"):
            return "hi"  # Hindi
        elif any(char in text for char in "বাংলা"):
            return "bn"  # Bengali
        elif any(char in text for char in "தமிழ்"):
            return "ta"  # Tamil
        elif any(char in text for char in "తెలుగు"):
            return "te"  # Telugu
        elif any(char in text for char in "ಕನ್ನಡ"):
            return "kn"  # Kannada
        elif any(char in text for char in "മലയാളം"):
            return "ml"  # Malayalam
        elif any(char in text for char in "ગુજરાતી"):
            return "gu"  # Gujarati
        elif any(char in text for char in "मराठी"):
            return "mr"  # Marathi
        
        # Default to English for ASCII text
        if text.isascii():
            return "en"
        
        # Default fallback
        return "auto"

    async def health_check(self) -> bool:
        """Check if the coordinator is healthy"""
        if not self.is_initialized:
            return False
        
        # Check if at least one engine is working
        healthy_engines = 0
        for engine_name, engine in self.engines.items():
            if self.engine_initialized.get(engine_name, False):
                try:
                    # Simple health check
                    health = await engine.health_check()
                    if health:
                        healthy_engines += 1
                except:
                    logger.warning(f"Engine {engine_name} health check failed")
        
        return healthy_engines > 0

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
