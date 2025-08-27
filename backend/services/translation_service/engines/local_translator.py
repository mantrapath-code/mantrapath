"""
Local Translation Models
Provides self-hosted translation without external API dependencies
Uses lightweight transformer models for common language pairs
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import pickle
import hashlib

# Simple rule-based translation for common meditation terms
# In production, this would use actual transformer models
from .base_translator import BaseTranslator, TranslationResult
from config.settings import SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)

class LocalTranslator(BaseTranslator):
    """Local translation using pre-trained models and dictionaries"""
    
    def __init__(self, name: str = "local", config: Dict[str, Any] = None):
        super().__init__(name, config or {})
        
        self.models_path = Path("models")
        self.models_path.mkdir(exist_ok=True)
        
        # Simple translation dictionaries for meditation terms
        self.meditation_glossary = self._load_meditation_glossary()
        
        # Language detection patterns
        self.language_patterns = self._load_language_patterns()
        
        # Cache for frequent translations
        self.translation_cache = {}
        
        # Set supported languages based on glossary
        self.supported_languages = set(['en', 'es', 'fr', 'de', 'hi', 'zh'])
        
        logger.info("Local translator initialized")
    
    def _load_meditation_glossary(self) -> Dict[str, Dict[str, str]]:
        """
        Load meditation-specific translation glossary
        Format: {source_lang: {target_lang: {term: translation}}}
        """
        return {
            'en': {
                'es': {
                    'meditation': 'meditación',
                    'mindfulness': 'atención plena',
                    'breathing': 'respiración',
                    'awareness': 'conciencia',
                    'peace': 'paz',
                    'calm': 'calma',
                    'focus': 'enfoque',
                    'present moment': 'momento presente',
                    'inner peace': 'paz interior',
                    'compassion': 'compasión',
                    'gratitude': 'gratitud',
                    'wisdom': 'sabiduría',
                    'enlightenment': 'iluminación',
                    'chakra': 'chakra',
                    'mantra': 'mantra',
                    'yoga': 'yoga',
                    'namaste': 'namaste',
                    'om': 'om'
                },
                'fr': {
                    'meditation': 'méditation',
                    'mindfulness': 'pleine conscience',
                    'breathing': 'respiration',
                    'awareness': 'conscience',
                    'peace': 'paix',
                    'calm': 'calme',
                    'focus': 'concentration',
                    'present moment': 'moment présent',
                    'inner peace': 'paix intérieure',
                    'compassion': 'compassion',
                    'gratitude': 'gratitude',
                    'wisdom': 'sagesse',
                    'enlightenment': 'illumination',
                    'chakra': 'chakra',
                    'mantra': 'mantra',
                    'yoga': 'yoga',
                    'namaste': 'namaste',
                    'om': 'om'
                },
                'de': {
                    'meditation': 'Meditation',
                    'mindfulness': 'Achtsamkeit',
                    'breathing': 'Atmung',
                    'awareness': 'Bewusstsein',
                    'peace': 'Frieden',
                    'calm': 'Ruhe',
                    'focus': 'Fokus',
                    'present moment': 'gegenwärtiger Moment',
                    'inner peace': 'innerer Frieden',
                    'compassion': 'Mitgefühl',
                    'gratitude': 'Dankbarkeit',
                    'wisdom': 'Weisheit',
                    'enlightenment': 'Erleuchtung',
                    'chakra': 'Chakra',
                    'mantra': 'Mantra',
                    'yoga': 'Yoga',
                    'namaste': 'Namaste',
                    'om': 'Om'
                },
                'hi': {
                    'meditation': 'ध्यान',
                    'mindfulness': 'सचेतता',
                    'breathing': 'श्वास',
                    'awareness': 'जागरूकता',
                    'peace': 'शांति',
                    'calm': 'शांत',
                    'focus': 'फोकस',
                    'present moment': 'वर्तमान क्षण',
                    'inner peace': 'आंतरिक शांति',
                    'compassion': 'करुणा',
                    'gratitude': 'कृतज्ञता',
                    'wisdom': 'ज्ञान',
                    'enlightenment': 'बोधि',
                    'chakra': 'चक्र',
                    'mantra': 'मंत्र',
                    'yoga': 'योग',
                    'namaste': 'नमस्ते',
                    'om': 'ॐ'
                },
                'zh': {
                    'meditation': '冥想',
                    'mindfulness': '正念',
                    'breathing': '呼吸',
                    'awareness': '觉知',
                    'peace': '平静',
                    'calm': '冷静',
                    'focus': '专注',
                    'present moment': '当下',
                    'inner peace': '内心平静',
                    'compassion': '慈悲',
                    'gratitude': '感恩',
                    'wisdom': '智慧',
                    'enlightenment': '觉悟',
                    'chakra': '脉轮',
                    'mantra': '咒语',
                    'yoga': '瑜伽',
                    'namaste': '合十礼',
                    'om': '唵'
                }
            }
        }
    
    def _load_language_patterns(self) -> Dict[str, List[str]]:
        """
        Load simple language detection patterns
        """
        return {
            'en': ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with'],
            'es': ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no'],
            'fr': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir'],
            'de': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich'],
            'hi': ['के', 'की', 'का', 'है', 'में', 'से', 'पर', 'को', 'और', 'यह'],
            'zh': ['的', '是', '在', '有', '个', '不', '了', '我', '你', '他']
        }
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate text using local models and dictionaries
        """
        # Create cache key
        cache_key = self._get_cache_key(text, target_language, source_language)
        
        # Check cache first
        if cache_key in self.translation_cache:
            cached_result = self.translation_cache[cache_key]
            cached_result['metadata']['from_cache'] = True
            return cached_result
        
        # Detect source language if not provided
        if not source_language:
            detection = await self.detect_language(text)
            source_language = detection['language']
        
        # Perform translation
        translated_text = await self._translate_text(
            text, source_language, target_language, context
        )
        
        # Calculate confidence
        confidence = self._calculate_local_confidence(
            text, translated_text, source_language, target_language, context
        )
        
        start_time = time.time()
        return TranslationResult(
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            confidence_score=confidence,
            engine="local",
            processing_time_ms=int((time.time() - start_time) * 1000),
            quality_score=confidence,
            cache_hit=False,
            cultural_notes=[],
            custom_terms_used=[],
            metadata={
                "model_type": "dictionary_based",
                "has_cultural_adaptation": bool(context and context.get('domain') == 'meditation'),
                "from_cache": False
            }
        )
        
        # Store the result in cache (as dict for caching)
        cache_entry = {
            "translated_text": translated_text,
            "confidence_score": confidence,
            "timestamp": time.time()
        }
        self.translation_cache[cache_key] = cache_entry
        
        return TranslationResult(
            translated_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            confidence_score=confidence,
            engine="local",
            processing_time_ms=int((time.time() - start_time) * 1000),
            quality_score=confidence,
            cache_hit=False,
            cultural_notes=[],
            custom_terms_used=[],
            metadata={
                "model_type": "dictionary_based",
                "has_cultural_adaptation": bool(context and context.get('domain') == 'meditation'),
                "from_cache": False
            }
        )
    
    async def translate_batch(
        self,
        texts: List[str],
        source_language: str,
        target_language: str,
        domain: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[TranslationResult]:
        """
        Translate multiple texts
        """
        results = []
        
        for text in texts:
            result = await self.translate(text, source_language, target_language, domain, context)
            results.append(result)
        
        return results
    
    async def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Simple language detection using pattern matching
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        if not words:
            return ('unknown', 0.0)
        
        language_scores = {}
        
        # Score each language based on common words
        for lang, patterns in self.language_patterns.items():
            score = 0
            for word in words:
                if word in patterns:
                    score += 1
            
            if len(words) > 0:
                language_scores[lang] = score / len(words)
        
        # Find best match
        if language_scores:
            best_lang = max(language_scores.keys(), key=lambda k: language_scores[k])
            best_score = language_scores[best_lang]
            
            return (best_lang, min(best_score * 2, 1.0))  # Scale to 0-1
        
        return ('en', 0.5)  # Default to English
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        """
        return list(self.supported_languages)
    
    async def _translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Perform the actual translation
        """
        # If same language, return original
        if source_lang == target_lang:
            return text
        
        # Try meditation-specific translation first
        if context and context.get('domain') == 'meditation':
            meditation_translation = self._translate_meditation_terms(
                text, source_lang, target_lang
            )
            if meditation_translation != text:
                return meditation_translation
        
        # For demonstration, perform simple word-by-word translation
        # In production, this would use actual transformer models
        return await self._simple_word_translation(text, source_lang, target_lang)
    
    def _translate_meditation_terms(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Translate using meditation-specific glossary
        """
        if (source_lang not in self.meditation_glossary or 
            target_lang not in self.meditation_glossary[source_lang]):
            return text
        
        glossary = self.meditation_glossary[source_lang][target_lang]
        
        # Simple term replacement
        translated = text
        for term, translation in glossary.items():
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            translated = pattern.sub(translation, translated)
        
        return translated
    
    async def _simple_word_translation(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Simple word-by-word translation for demonstration
        In production, use actual neural translation models
        """
        # For now, just return a simple format indicating translation attempt
        if source_lang == 'en' and target_lang == 'es':
            # Very basic English to Spanish patterns
            basic_translations = {
                'hello': 'hola',
                'goodbye': 'adiós',
                'please': 'por favor',
                'thank you': 'gracias',
                'yes': 'sí',
                'no': 'no',
                'good': 'bueno',
                'bad': 'malo',
                'big': 'grande',
                'small': 'pequeño'
            }
            
            words = text.split()
            translated_words = []
            
            for word in words:
                word_lower = word.lower().strip('.,!?')
                if word_lower in basic_translations:
                    translated_words.append(basic_translations[word_lower])
                else:
                    translated_words.append(word)  # Keep original if no translation
            
            return ' '.join(translated_words)
        
        # For other language pairs, return original with note
        return f"{text} [Local translation from {source_lang} to {target_lang}]"
    
    def _calculate_local_confidence(
        self,
        original: str,
        translated: str,
        source_lang: str,
        target_lang: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence for local translation
        """
        # Base confidence for local translation
        confidence = 0.6
        
        # Higher confidence for meditation terms
        if context and context.get('domain') == 'meditation':
            if any(term in original.lower() for term in ['meditation', 'mindfulness', 'breathing']):
                confidence = 0.85
        
        # Same language
        if source_lang == target_lang:
            confidence = 1.0
        
        # Check if any actual translation occurred
        if translated == original:
            confidence *= 0.7
        
        # Boost confidence for supported language pairs
        supported_pairs = [('en', 'es'), ('en', 'fr'), ('en', 'de'), ('en', 'hi'), ('en', 'zh')]
        if (source_lang, target_lang) in supported_pairs:
            confidence *= 1.1
        
        return min(confidence, 1.0)
    
    def _get_cache_key(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str]
    ) -> str:
        """
        Generate cache key for translation
        """
        key_data = f"{text}:{source_language}:{target_language}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def initialize(self) -> bool:
        """Initialize the local translator"""
        try:
            self.is_initialized = True
            logger.info("Local translator initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize local translator: {e}")
            self.is_initialized = False
            return False
    
    def supports_language_pair(self, source: str, target: str) -> bool:
        """Check if language pair is supported"""
        return source in self.supported_languages and target in self.supported_languages
    
    async def get_quality_score(
        self,
        original_text: str,
        translated_text: str,
        source_language: str,
        target_language: str
    ) -> float:
        """Get quality score for translation"""
        return self._calculate_local_confidence(
            original_text, translated_text, source_language, target_language, None
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for local translator"""
        return {
            "name": self.name,
            "status": "healthy" if self.is_initialized else "not_initialized",
            "supported_languages_count": len(self.supported_languages),
            "timestamp": datetime.utcnow().isoformat(),
            "features": ["meditation_glossary", "offline_mode"]
        }
    
    async def close(self):
        """
        Cleanup resources
        """
        # Save cache if needed
        pass
