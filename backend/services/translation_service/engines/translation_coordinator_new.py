"""
Simplified Translation Coordinator with Lightweight Engines
Manages translation using Bhashini and lightweight API-based engines
"""
import logging
import os
from typing import Dict, List, Optional, Any
import redis.asyncio as redis

from .base_translator import BaseTranslator, TranslationResult
from .bhashini_translator import BhashiniTranslator
from .lightweight_translator import LightweightTranslator

logger = logging.getLogger(__name__)

class TranslationCoordinator:
    """Simplified coordinator with lightweight engines for resource-constrained environments"""
    
    def __init__(self):
        self.engines: Dict[str, BaseTranslator] = {}
        self.engine_initialized: Dict[str, bool] = {}
        self.is_initialized = False
        
        # Caching
        self.redis_client = None
        self.cache_enabled = True
        self.cache_ttl = 86400  # 24 hours
        
        # Indian language codes
        self.indian_languages = {
            'hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 'as', 'mr', 'ur',
            'ne', 'sd', 'kok', 'mai', 'sat', 'doi', 'mni', 'brx', 'bh'
        }
        
        # Engine priority for fast response
        self.engine_priority = {
            'bhashini': 1,      # Fast, government service (real data)
            'lightweight': 2    # API-based fallback translator
        }
        
    async def initialize(self) -> bool:
        """Fast initialization with lightweight engines"""
        try:
            # Setup Redis cache (optional)
            await self._setup_cache()
            
            logger.info("Initializing translation service with lightweight engines...")
            
            # Initialize engines with configuration
            bhashini_config = {
                "api_key": os.getenv("BHASHINI_API_KEY"),
                "user_id": os.getenv("BHASHINI_USER_ID"),
                "base_url": os.getenv("BHASHINI_BASE_URL", "https://meity-auth.ulcacontrib.org"),
                "compute_url": os.getenv("BHASHINI_COMPUTE_URL", "https://dhruva-api.bhashini.gov.in/services/inference"),
                "api_version": os.getenv("BHASHINI_API_VERSION", "v1")
            }
            
            self.engines['bhashini'] = BhashiniTranslator(config=bhashini_config)
            self.engines['lightweight'] = LightweightTranslator()
            self.engine_initialized['bhashini'] = False
            self.engine_initialized['lightweight'] = False
            
            # Try to initialize Bhashini first (fast, no model download)
            try:
                bhashini_result = await self.engines['bhashini'].initialize()
                if bhashini_result:
                    self.engine_initialized['bhashini'] = True
                    logger.info("✅ Bhashini translator initialized successfully")
            except Exception as e:
                logger.warning(f"Bhashini initialization failed: {e}")
            
            # Initialize lightweight translator (fast, API-based)
            try:
                lightweight_result = await self.engines['lightweight'].initialize()
                if lightweight_result:
                    self.engine_initialized['lightweight'] = True
                    logger.info("✅ Lightweight translator initialized successfully")
            except Exception as e:
                logger.warning(f"Lightweight translator initialization failed: {e}")
            
            # Service is ready if at least one engine is available
            if any(self.engine_initialized.values()):
                self.is_initialized = True
                initialized_engines = [name for name, status in self.engine_initialized.items() if status]
                logger.info(f"🚀 Translation service ready with engines: {initialized_engines}")
                return True
            else:
                logger.error("❌ No translation engines available - service initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"Error in translation service initialization: {e}")
            return False
    
    async def _setup_cache(self):
        """Setup Redis cache connection"""
        try:
            self.redis_client = redis.from_url("redis://redis:6379/3")
            await self.redis_client.ping()
            logger.info("✅ Redis cache connected successfully")
            self.cache_enabled = True
        except Exception as e:
            logger.warning(f"Redis cache not available: {e}. Continuing without cache.")
            self.cache_enabled = False
    
    async def translate(self, text: str, source_language: str = "auto", target_language: str = "en", domain: str = None) -> TranslationResult:
        """Translate text using available engines in priority order"""
        if not self.is_initialized:
            raise RuntimeError("Translation coordinator not initialized")
        
        # Try engines in priority order
        for engine_name in sorted(self.engine_priority.keys(), key=lambda x: self.engine_priority[x]):
            if self.engine_initialized.get(engine_name, False):
                try:
                    engine = self.engines[engine_name]
                    result = await engine.translate(text, source_language, target_language, domain)
                    
                    # Check if translation was successful
                    if result.translated_text and result.translated_text.strip():
                        logger.debug(f"Translation successful using {engine_name}")
                        return result
                    else:
                        logger.warning(f"Empty translation result from {engine_name}")
                        
                except Exception as e:
                    logger.warning(f"Translation failed with {engine_name}: {e}")
                    continue
        
        # If all engines fail, return original text with error
        logger.error("All translation engines failed")
        return TranslationResult(
            translated_text=text,
            source_language=source_language,
            target_language=target_language,
            confidence_score=0.0,
            engine="fallback",
            metadata={"error": "All translation engines failed", "original_text": text}
        )
    
    async def get_supported_languages(self) -> List[str]:
        """Get all supported languages from all engines"""
        all_languages = set()
        
        # Collect languages from all initialized engines
        for engine_name, engine in self.engines.items():
            if self.engine_initialized.get(engine_name, False):
                try:
                    languages = engine.get_supported_languages()
                    all_languages.update(languages)
                except Exception as e:
                    logger.warning(f"Failed to get languages from {engine_name}: {e}")
        
        # Add Indian languages and common international languages
        all_languages.update(self.indian_languages)
        all_languages.update(['en', 'es', 'fr', 'de', 'zh', 'ja', 'ko', 'ru', 'ar', 'pt'])
        
        return sorted(list(all_languages))
    
    async def detect_language(self, text: str) -> tuple[str, float]:
        """Detect language using available engines"""
        for engine_name in sorted(self.engine_priority.keys(), key=lambda x: self.engine_priority[x]):
            if self.engine_initialized.get(engine_name, False):
                try:
                    engine = self.engines[engine_name]
                    if hasattr(engine, 'detect_language'):
                        detected_lang, confidence = await engine.detect_language(text)
                        if detected_lang != 'unknown':
                            return detected_lang, confidence
                except Exception as e:
                    logger.warning(f"Language detection failed with {engine_name}: {e}")
                    continue
        
        return 'unknown', 0.0
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all engines"""
        status = {
            'is_initialized': self.is_initialized,
            'engines': {},
            'cache_enabled': self.cache_enabled
        }
        
        for engine_name, engine in self.engines.items():
            status['engines'][engine_name] = {
                'initialized': self.engine_initialized.get(engine_name, False),
                'priority': self.engine_priority.get(engine_name, 999)
            }
        
        return status
