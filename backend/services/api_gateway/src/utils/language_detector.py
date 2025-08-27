"""
Language Detection Utility for API Gateway V3 Enhanced
Detects language from text input for voice commands and content
"""

import time
import re
from typing import Dict, List, Optional, Tuple, Any
import structlog

# Import language detection libraries
try:
    from langdetect import detect, detect_langs, DetectorFactory
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

logger = structlog.get_logger(__name__)

# Set seed for consistent results
if LANGDETECT_AVAILABLE:
    DetectorFactory.seed = 0


class LanguageDetector:
    """Language detection utility with multiple backends"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'zh': 'Chinese (Simplified)',
            'zh-tw': 'Chinese (Traditional)',
            'ko': 'Korean',
            'ar': 'Arabic',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'gu': 'Gujarati',
            'mr': 'Marathi',
            'pa': 'Punjabi',
            'ur': 'Urdu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'as': 'Assamese'
        }
        
        # Language patterns for keyword-based detection
        self.language_patterns = {
            'hi': [
                r'[\u0900-\u097F]',  # Devanagari script
                r'\b(मैं|आप|यह|वह|है|हैं|था|थे|करना|होना)\b'
            ],
            'ta': [
                r'[\u0B80-\u0BFF]',  # Tamil script
                r'\b(நான்|நீங்கள்|இது|அது|உள்ளது)\b'
            ],
            'te': [
                r'[\u0C00-\u0C7F]',  # Telugu script
                r'\b(నేను|మీరు|ఇది|అది|ఉంది)\b'
            ],
            'gu': [
                r'[\u0A80-\u0AFF]',  # Gujarati script
                r'\b(હું|તમે|આ|તે|છે)\b'
            ],
            'mr': [
                r'[\u0900-\u097F]',  # Devanagari script (shared with Hindi)
                r'\b(मी|तुम्ही|हे|ते|आहे)\b'
            ],
            'bn': [
                r'[\u0980-\u09FF]',  # Bengali script
                r'\b(আমি|আপনি|এটি|সেটি|আছে)\b'
            ],
            'ar': [
                r'[\u0600-\u06FF]',  # Arabic script
                r'\b(أنا|أنت|هذا|ذلك|هو)\b'
            ],
            'ja': [
                r'[\u3040-\u309F]',  # Hiragana
                r'[\u30A0-\u30FF]',  # Katakana
                r'[\u4E00-\u9FAF]'   # CJK Unified Ideographs
            ],
            'zh': [
                r'[\u4E00-\u9FAF]',  # CJK Unified Ideographs
                r'\b(我|你|他|她|它|是|的|在)\b'
            ],
            'ko': [
                r'[\uAC00-\uD7AF]',  # Hangul syllables
                r'[\u1100-\u11FF]',  # Hangul jamo
                r'\b(나|너|이|그|있다)\b'
            ]
        }
        
        # Common English words for fallback detection
        self.english_keywords = {
            'feel', 'mood', 'happy', 'sad', 'meditation', 'breathe', 'peace',
            'stress', 'calm', 'journal', 'write', 'today', 'help', 'start',
            'stop', 'find', 'show', 'community', 'profile', 'settings'
        }
        
        self.detection_stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'fallback_detections': 0,
            'errors': 0
        }
    
    async def detect(self, text: str, fallback_language: str = 'en') -> str:
        """Detect language from text"""
        if not text or not text.strip():
            return fallback_language
        
        self.detection_stats['total_detections'] += 1
        
        try:
            # Method 1: Pattern-based detection for Indian languages
            pattern_result = self._detect_by_patterns(text)
            if pattern_result:
                self.detection_stats['successful_detections'] += 1
                logger.debug("Language detected by patterns", language=pattern_result, text=text[:50])
                return pattern_result
            
            # Method 2: Library-based detection
            if LANGDETECT_AVAILABLE:
                library_result = await self._detect_by_library(text)
                if library_result and library_result in self.supported_languages:
                    self.detection_stats['successful_detections'] += 1
                    logger.debug("Language detected by library", language=library_result, text=text[:50])
                    return library_result
            
            # Method 3: Keyword-based detection for English
            if self._is_likely_english(text):
                self.detection_stats['successful_detections'] += 1
                logger.debug("Language detected as English by keywords", text=text[:50])
                return 'en'
            
            # Fallback
            self.detection_stats['fallback_detections'] += 1
            logger.debug("Using fallback language", language=fallback_language, text=text[:50])
            return fallback_language
            
        except Exception as e:
            self.detection_stats['errors'] += 1
            logger.exception("Language detection failed", error=str(e), text=text[:50])
            return fallback_language
    
    def _detect_by_patterns(self, text: str) -> Optional[str]:
        """Detect language using script patterns"""
        for language, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return language
        return None
    
    async def _detect_by_library(self, text: str) -> Optional[str]:
        """Detect language using langdetect library"""
        try:
            # Use langdetect for better accuracy
            detected = detect(text)
            
            # Map some common variations
            language_mapping = {
                'zh-cn': 'zh',
                'zh-tw': 'zh-tw',
                'pt-br': 'pt',
                'en-us': 'en',
                'en-gb': 'en'
            }
            
            return language_mapping.get(detected, detected)
            
        except Exception as e:
            logger.debug("Library-based detection failed", error=str(e))
            return None
    
    def _is_likely_english(self, text: str) -> bool:
        """Check if text is likely English based on keywords"""
        words = set(text.lower().split())
        english_matches = len(words & self.english_keywords)
        return english_matches >= min(2, len(words) * 0.3)
    
    async def detect_with_confidence(self, text: str) -> Tuple[str, float]:
        """Detect language with confidence score"""
        if not text or not text.strip():
            return ('en', 0.0)
        
        try:
            # Pattern-based detection has high confidence
            pattern_result = self._detect_by_patterns(text)
            if pattern_result:
                return (pattern_result, 0.9)
            
            # Library-based detection with confidence
            if LANGDETECT_AVAILABLE:
                try:
                    detections = detect_langs(text)
                    if detections:
                        best_detection = detections[0]
                        language = best_detection.lang
                        confidence = best_detection.prob
                        
                        # Map language if needed
                        language_mapping = {
                            'zh-cn': 'zh',
                            'zh-tw': 'zh-tw',
                            'pt-br': 'pt'
                        }
                        language = language_mapping.get(language, language)
                        
                        if language in self.supported_languages:
                            return (language, confidence)
                
                except Exception as e:
                    logger.debug("Confidence-based detection failed", error=str(e))
            
            # English keyword detection
            if self._is_likely_english(text):
                return ('en', 0.7)
            
            # Fallback with low confidence
            return ('en', 0.1)
            
        except Exception as e:
            logger.exception("Language detection with confidence failed", error=str(e))
            return ('en', 0.0)
    
    async def detect_multiple(self, texts: List[str]) -> List[Tuple[str, str]]:
        """Detect languages for multiple texts"""
        results = []
        for text in texts:
            language = await self.detect(text)
            results.append((text, language))
        return results
    
    def is_supported_language(self, language_code: str) -> bool:
        """Check if a language is supported"""
        return language_code in self.supported_languages
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        return self.supported_languages.get(language_code, language_code)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return self.supported_languages.copy()
    
    def normalize_language_code(self, language_code: str) -> str:
        """Normalize language code to supported format"""
        # Handle common variations
        normalization_map = {
            'en-us': 'en',
            'en-gb': 'en',
            'en-au': 'en',
            'es-es': 'es',
            'es-mx': 'es',
            'pt-br': 'pt',
            'pt-pt': 'pt',
            'zh-cn': 'zh',
            'zh-hans': 'zh',
            'zh-hant': 'zh-tw',
            'fr-fr': 'fr',
            'fr-ca': 'fr',
            'de-de': 'de',
            'de-at': 'de',
            'it-it': 'it',
            'ja-jp': 'ja',
            'ko-kr': 'ko',
            'ar-sa': 'ar',
            'hi-in': 'hi'
        }
        
        language_lower = language_code.lower()
        
        # Check direct mapping
        if language_lower in normalization_map:
            return normalization_map[language_lower]
        
        # Extract primary language code
        primary = language_lower.split('-')[0]
        if primary in self.supported_languages:
            return primary
        
        return language_code
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for language detector"""
        try:
            # Test detection on sample texts
            test_cases = [
                ("Hello, how are you?", "en"),
                ("Bonjour, comment allez-vous?", "fr"),
                ("नमस्ते, आप कैसे हैं?", "hi"),
                ("Hola, ¿cómo estás?", "es")
            ]
            
            successful_tests = 0
            for text, expected_lang in test_cases:
                try:
                    detected = await self.detect(text)
                    if detected == expected_lang:
                        successful_tests += 1
                except Exception:
                    pass
            
            success_rate = successful_tests / len(test_cases)
            overall_success_rate = (
                self.detection_stats['successful_detections'] / 
                max(self.detection_stats['total_detections'], 1)
            )
            
            healthy = (
                success_rate >= 0.75 and  # At least 75% test success
                overall_success_rate >= 0.8 and  # At least 80% overall success
                LANGDETECT_AVAILABLE  # Required library available
            )
            
            return {
                "status": "healthy" if healthy else "degraded",
                "test_success_rate": round(success_rate, 2),
                "overall_success_rate": round(overall_success_rate, 2),
                "total_detections": self.detection_stats['total_detections'],
                "libraries_available": {
                    "langdetect": LANGDETECT_AVAILABLE,
                    "textblob": TEXTBLOB_AVAILABLE
                },
                "supported_languages_count": len(self.supported_languages),
                "detection_methods": [
                    "pattern_based",
                    "library_based" if LANGDETECT_AVAILABLE else None,
                    "keyword_based"
                ],
                "timestamp": time.time()
            }
        
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""
        total = max(self.detection_stats['total_detections'], 1)
        
        return {
            **self.detection_stats,
            "success_rate": round(
                self.detection_stats['successful_detections'] / total, 3
            ),
            "fallback_rate": round(
                self.detection_stats['fallback_detections'] / total, 3
            ),
            "error_rate": round(
                self.detection_stats['errors'] / total, 3
            )
        }
    
    def reset_stats(self):
        """Reset detection statistics"""
        self.detection_stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'fallback_detections': 0,
            'errors': 0
        }
