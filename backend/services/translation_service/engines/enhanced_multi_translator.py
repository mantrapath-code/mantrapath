"""
Enhanced Multi-Translator Engine
Combines Google Translate, Argos Translate, and Indic Translator for best translation quality
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
import time
from statistics import mean

logger = logging.getLogger(__name__)

from .free_google_translator import FreeGoogleTranslator
from .argos_translator import ArgosTranslator
from .indic_translator import IndicTranslator
from .local_translator import LocalTranslator
from .cultural_adaptation import CulturalAdaptationService

class EnhancedMultiTranslator:
    """Enhanced multi-translator engine combining multiple translation services"""
    
    def __init__(self):
        self.engines = {}
        self.engine_priorities = {
            'indic': 1,      # Highest priority for Indian languages
            'google': 2,     # Good general quality
            'argos': 3,      # Offline backup
            'local': 4       # Fallback
        }
        self.is_initialized = False
        
        # Indian language codes for specialized routing
        self.indian_languages = {
            'hi', 'bn', 'ta', 'te', 'ml', 'kn', 'gu', 'or', 'pa', 'as', 'mr', 'ur'
        }
        
    async def initialize(self) -> bool:
        """Initialize all translation engines"""
        try:
            # Initialize all engines
            self.engines['google'] = FreeGoogleTranslator()
            self.engines['argos'] = ArgosTranslator()
            self.engines['indic'] = IndicTranslator()
            self.engines['local'] = LocalTranslator()
            
            # Initialize engines concurrently
            init_results = await asyncio.gather(
                self.engines['google'].initialize(),
                self.engines['argos'].initialize(),
                self.engines['indic'].initialize(),
                self.engines['local'].initialize(),
                return_exceptions=True
            )
            
            # Log initialization results
            engine_names = ['google', 'argos', 'indic', 'local']
            for i, result in enumerate(init_results):
                engine_name = engine_names[i]
                if isinstance(result, Exception):
                    logger.error(f"Failed to initialize {engine_name}: {result}")
                else:
                    logger.info(f"Initialized {engine_name}: {result}")
            
            self.is_initialized = True
            logger.info("Enhanced Multi-Translator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Enhanced Multi-Translator: {str(e)}")
            return False
    
    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate text using multiple engines and select best result
        """
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        translation_results = []
        
        # Determine which engines to use based on language pair
        selected_engines = self._select_engines(source_language, target_language)
        
        # Run translations concurrently
        tasks = []
        for engine_name in selected_engines:
            engine = self.engines.get(engine_name)
            if engine:
                tasks.append(self._safe_translate(engine, engine_name, text, target_language, source_language, context))
        
        # Wait for all translations
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        for i, result in enumerate(results):
            if not isinstance(result, Exception) and result:
                translation_results.append(result)
            else:
                logger.warning(f"Translation failed for engine {selected_engines[i]}: {result}")
        
        # Select best translation
        if not translation_results:
            raise Exception("All translation engines failed")
        
        best_result = self._select_best_translation(translation_results, source_language, target_language)
        
        # Add metadata
        processing_time = (time.time() - start_time) * 1000
        best_result['processing_time_ms'] = processing_time
        best_result['engines_used'] = [r['engine'] for r in translation_results]
        best_result['total_candidates'] = len(translation_results)
        
        return best_result
    
    def _select_engines(self, source_lang: str, target_lang: str) -> List[str]:
        """Select appropriate engines based on language pair"""
        engines = []
        
        # For Indian languages, prioritize Indic translator
        if source_lang in self.indian_languages or target_lang in self.indian_languages:
            engines.extend(['indic', 'google', 'argos'])
        else:
            engines.extend(['google', 'argos', 'indic'])
        
        # Always include local as fallback
        engines.append('local')
        
        return engines[:3]  # Limit to 3 engines for performance
    
    async def _safe_translate(
        self, 
        engine: Any, 
        engine_name: str, 
        text: str, 
        target_language: str, 
        source_language: str, 
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Safely translate with timeout and error handling"""
        try:
            # Set a timeout for each translation
            result = await asyncio.wait_for(
                engine.translate(text, target_language, source_language, context),
                timeout=10.0  # 10 second timeout
            )
            result['engine'] = engine_name
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Translation timeout for engine {engine_name}")
            return None
        except Exception as e:
            logger.warning(f"Translation error for engine {engine_name}: {str(e)}")
            return None
    
    def _select_best_translation(
        self, 
        results: List[Dict[str, Any]], 
        source_lang: str, 
        target_lang: str
    ) -> Dict[str, Any]:
        """Select the best translation from multiple results"""
        
        # If only one result, return it
        if len(results) == 1:
            return results[0]
        
        # Score each result
        scored_results = []
        for result in results:
            score = self._calculate_result_score(result, source_lang, target_lang)
            scored_results.append((score, result))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        best_result = scored_results[0][1]
        
        # Add comparison metadata
        best_result['selection_score'] = scored_results[0][0]
        best_result['alternatives'] = [
            {
                'engine': r[1]['engine'],
                'score': r[0],
                'confidence': r[1].get('confidence_score', 0.5)
            }
            for r in scored_results[1:]
        ]
        
        return best_result
    
    def _calculate_result_score(
        self, 
        result: Dict[str, Any], 
        source_lang: str, 
        target_lang: str
    ) -> float:
        """Calculate a score for translation result quality"""
        
        base_score = result.get('confidence_score', 0.5)
        engine = result.get('engine', 'unknown')
        
        # Engine-specific scoring
        engine_bonus = {
            'indic': 0.2 if (source_lang in self.indian_languages or target_lang in self.indian_languages) else 0.0,
            'google': 0.15,
            'argos': 0.1,
            'local': 0.0
        }.get(engine, 0.0)
        
        # Quality indicators
        translated_text = result.get('translated_text', '')
        
        # Penalize if translation is same as source (likely failed)
        if 'source_text' in result and translated_text == result.get('source_text', ''):
            base_score *= 0.3
        
        # Penalize very short translations for longer source
        if len(translated_text) < 3 and 'source_text' in result and len(result.get('source_text', '')) > 10:
            base_score *= 0.5
        
        # Bonus for reasonable length ratio
        if 'source_text' in result:
            source_len = len(result.get('source_text', ''))
            if source_len > 0:
                length_ratio = len(translated_text) / source_len
                if 0.5 <= length_ratio <= 2.0:  # Reasonable length ratio
                    base_score += 0.1
        
        total_score = base_score + engine_bonus
        return min(total_score, 1.0)
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect language using the best available engine"""
        
        if not self.is_initialized:
            await self.initialize()
        
        # Try engines in order of detection quality
        engines_to_try = ['google', 'indic', 'argos', 'local']
        
        for engine_name in engines_to_try:
            engine = self.engines.get(engine_name)
            if engine:
                try:
                    result = await asyncio.wait_for(
                        engine.detect_language(text),
                        timeout=5.0
                    )
                    result['primary_engine'] = engine_name
                    return result
                except Exception as e:
                    logger.warning(f"Language detection failed for {engine_name}: {str(e)}")
                    continue
        
        # Fallback detection
        return {
            'language': 'en',
            'confidence': 0.3,
            'primary_engine': 'fallback'
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all translation engines"""
        
        if not self.is_initialized:
            await self.initialize()
        
        health_results = {}
        overall_healthy = True
        
        # Check each engine
        for engine_name, engine in self.engines.items():
            try:
                health = await asyncio.wait_for(
                    engine.health_check(),
                    timeout=5.0
                )
                health_results[engine_name] = health
                
                if health.get('status') != 'healthy':
                    overall_healthy = False
                    
            except Exception as e:
                health_results[engine_name] = {
                    'status': 'error',
                    'error': str(e)
                }
                overall_healthy = False
        
        return {
            'status': 'healthy' if overall_healthy else 'degraded',
            'engines': health_results,
            'initialized': self.is_initialized,
            'supported_engines': list(self.engines.keys())
        }
    
    async def get_supported_languages(self) -> Dict[str, List[str]]:
        """Get supported languages for each engine"""
        
        if not self.is_initialized:
            await self.initialize()
        
        languages_by_engine = {}
        
        for engine_name, engine in self.engines.items():
            try:
                if hasattr(engine, 'get_supported_languages'):
                    languages = await engine.get_supported_languages()
                    languages_by_engine[engine_name] = languages
                elif hasattr(engine, 'supported_languages'):
                    languages_by_engine[engine_name] = list(engine.supported_languages.keys())
                else:
                    languages_by_engine[engine_name] = ['en']  # Default
                    
            except Exception as e:
                logger.warning(f"Could not get languages for {engine_name}: {str(e)}")
                languages_by_engine[engine_name] = []
        
        # Combine all unique languages
        all_languages = set()
        for langs in languages_by_engine.values():
            all_languages.update(langs)
        
        return {
            'all_supported': sorted(list(all_languages)),
            'by_engine': languages_by_engine,
            'indian_languages': sorted(list(self.indian_languages))
        }
    
    async def translate_batch(
        self,
        requests: List[Dict[str, Any]],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Translate multiple texts concurrently"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def translate_single(request):
            async with semaphore:
                return await self.translate(
                    text=request.get('text', ''),
                    target_language=request.get('target_language', 'en'),
                    source_language=request.get('source_language', 'en'),
                    context=request.get('context')
                )
        
        tasks = [translate_single(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error dictionaries
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'error': str(result),
                    'request_index': i,
                    'status': 'failed'
                })
            else:
                result['request_index'] = i
                result['status'] = 'success'
                processed_results.append(result)
        
        return processed_results
