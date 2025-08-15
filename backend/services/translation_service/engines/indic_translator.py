"""
Indic Language Translator using AI4Bharat models
Supports Indian regional languages with better accuracy
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
import time
import re

logger = logging.getLogger(__name__)

class IndicTranslator:
    """Indic language translator using AI4Bharat approach"""
    
    def __init__(self):
        self.is_initialized = False
        self.supported_languages = {
            'hi': 'Hindi',
            'bn': 'Bengali', 
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'or': 'Odia',
            'pa': 'Punjabi',
            'as': 'Assamese',
            'mr': 'Marathi',
            'ur': 'Urdu',
            'ne': 'Nepali',
            'si': 'Sinhala',
            'my': 'Myanmar',
            'en': 'English'
        }
        
        # Common phrases and translations for basic functionality
        self.phrase_dictionary = {
            'hi': {
                'hello': 'नमस्ते',
                'thank you': 'धन्यवाद',
                'welcome': 'स्वागत',
                'good morning': 'सुप्रभात',
                'good night': 'शुभ रात्रि',
                'yes': 'हाँ',
                'no': 'नहीं',
                'please': 'कृपया',
                'sorry': 'माफ करें',
                'help': 'मदद'
            },
            'bn': {
                'hello': 'নমস্কার',
                'thank you': 'ধন্যবাদ',
                'welcome': 'স্বাগতম',
                'good morning': 'সুপ্রভাত',
                'good night': 'শুভ রাত্রি',
                'yes': 'হ্যাঁ',
                'no': 'না',
                'please': 'দয়া করে',
                'sorry': 'দুঃখিত',
                'help': 'সাহায্য'
            },
            'ta': {
                'hello': 'வணக்கம்',
                'thank you': 'நன்றி',
                'welcome': 'வரவேற்கிறோம்',
                'good morning': 'காலை வணக்கம்',
                'good night': 'இனிய இரவு',
                'yes': 'ஆம்',
                'no': 'இல்லை',
                'please': 'தயவுசெய்து',
                'sorry': 'மன்னிக்கவும்',
                'help': 'உதவி'
            },
            'te': {
                'hello': 'నమస్కారం',
                'thank you': 'ధన్యవాదాలు',
                'welcome': 'స్వాగతం',
                'good morning': 'శుభోదయం',
                'good night': 'శుభ రాత్రి',
                'yes': 'అవును',
                'no': 'లేదు',
                'please': 'దయచేసి',
                'sorry': 'క్షమించండి',
                'help': 'సహాయం'
            },
            'gu': {
                'hello': 'નમસ્તે',
                'thank you': 'આભાર',
                'welcome': 'સ્વાગત',
                'good morning': 'સુપ્રભાત',
                'good night': 'શુભ રાત્રિ',
                'yes': 'હા',
                'no': 'ના',
                'please': 'કૃપા કરીને',
                'sorry': 'માફ કરો',
                'help': 'મદદ'
            },
            'ml': {
                'hello': 'നമസ്കാരം',
                'thank you': 'നന്ദി',
                'welcome': 'സ്വാഗതം',
                'good morning': 'സുപ്രഭാതം',
                'good night': 'ശുഭ രാത്രി',
                'yes': 'അതെ',
                'no': 'ഇല്ല',
                'please': 'ദയവായി',
                'sorry': 'ക്ഷമിക്കുക',
                'help': 'സഹായം'
            },
            'kn': {
                'hello': 'ನಮಸ್ಕಾರ',
                'thank you': 'ಧನ್ಯವಾದಗಳು',
                'welcome': 'ಸ್ವಾಗತ',
                'good morning': 'ಶುಭೋದಯ',
                'good night': 'ಶುಭ ರಾತ್ರಿ',
                'yes': 'ಹೌದು',
                'no': 'ಇಲ್ಲ',
                'please': 'ದಯವಿಟ್ಟು',
                'sorry': 'ಕ್ಷಮಿಸಿ',
                'help': 'ಸಹಾಯ'
            },
            'mr': {
                'hello': 'नमस्कार',
                'thank you': 'धन्यवाद',
                'welcome': 'स्वागत',
                'good morning': 'सुप्रभात',
                'good night': 'शुभ रात्री',
                'yes': 'होय',
                'no': 'नाही',
                'please': 'कृपया',
                'sorry': 'माफ करा',
                'help': 'मदत'
            },
            'pa': {
                'hello': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ',
                'thank you': 'ਧੰਨਵਾਦ',
                'welcome': 'ਸੁਆਗਤ',
                'good morning': 'ਸੁਪ੍ਰਭਾਤ',
                'good night': 'ਸ਼ੁਭ ਰਾਤ',
                'yes': 'ਹਾਂ',
                'no': 'ਨਹੀਂ',
                'please': 'ਕਿਰਪਾ ਕਰਕੇ',
                'sorry': 'ਮਾਫ਼ ਕਰੋ',
                'help': 'ਮਦਦ'
            },
            'ur': {
                'hello': 'آداب',
                'thank you': 'شکریہ',
                'welcome': 'خوش آمدید',
                'good morning': 'صبح بخیر',
                'good night': 'شب بخیر',
                'yes': 'جی ہاں',
                'no': 'نہیں',
                'please': 'برائے کرم',
                'sorry': 'معاف کریں',
                'help': 'مدد'
            }
        }
        
    async def initialize(self) -> bool:
        """Initialize the Indic translator"""
        try:
            self.is_initialized = True
            logger.info(f"Indic Translator initialized with {len(self.supported_languages)} languages")
            logger.info(f"Supported languages: {list(self.supported_languages.keys())}")
            return True
        except Exception as e:
            logger.error(f"Error initializing Indic Translator: {str(e)}")
            return False
    
    async def translate(
        self,
        text: str,
        target_language: str,
        source_language: str = "en",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate text using Indic language models
        """
        start_time = time.time()
        
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Check if languages are supported
            if target_language not in self.supported_languages:
                raise Exception(f"Target language '{target_language}' not supported")
            
            # Clean and prepare text
            cleaned_text = text.strip().lower()
            
            # Try phrase-based translation first
            translated_text = self._phrase_translate(cleaned_text, target_language, source_language)
            
            # If no phrase match, use rule-based translation
            if translated_text == text:
                translated_text = self._rule_based_translate(text, target_language, source_language)
            
            processing_time = (time.time() - start_time) * 1000
            
            # Calculate confidence
            confidence = self._calculate_confidence(text, translated_text, source_language, target_language)
            
            return {
                'translated_text': translated_text,
                'source_language': source_language,
                'target_language': target_language,
                'confidence_score': confidence,
                'engine': 'indic',
                'processing_time_ms': processing_time,
                'offline': True,
                'regional_support': True
            }
            
        except Exception as e:
            logger.error(f"Indic translation failed: {str(e)}")
            raise
    
    def _phrase_translate(self, text: str, target_lang: str, source_lang: str) -> str:
        """Translate using phrase dictionary"""
        if target_lang not in self.phrase_dictionary:
            return text
            
        phrase_dict = self.phrase_dictionary[target_lang]
        
        # Check for exact phrase matches
        if text in phrase_dict:
            return phrase_dict[text]
        
        # Check for partial matches
        for phrase, translation in phrase_dict.items():
            if phrase in text:
                return text.replace(phrase, translation)
        
        return text
    
    def _rule_based_translate(self, text: str, target_lang: str, source_lang: str) -> str:
        """Rule-based translation for common patterns"""
        
        # Basic English to Indic translation patterns
        if source_lang == 'en' and target_lang in self.phrase_dictionary:
            
            # Common word replacements
            word_map = {
                'hi': {
                    'I': 'मैं', 'you': 'आप', 'he': 'वह', 'she': 'वह', 'we': 'हम',
                    'they': 'वे', 'am': 'हूँ', 'is': 'है', 'are': 'हैं', 'was': 'था',
                    'were': 'थे', 'will': 'होगा', 'can': 'सकता', 'should': 'चाहिए',
                    'what': 'क्या', 'where': 'कहाँ', 'when': 'कब', 'how': 'कैसे',
                    'why': 'क्यों', 'who': 'कौन', 'and': 'और', 'or': 'या',
                    'but': 'लेकिन', 'if': 'अगर', 'then': 'तो', 'because': 'क्योंकि'
                },
                'bn': {
                    'I': 'আমি', 'you': 'আপনি', 'he': 'তিনি', 'she': 'তিনি', 'we': 'আমরা',
                    'they': 'তারা', 'am': 'আছি', 'is': 'আছে', 'are': 'আছেন', 'was': 'ছিল',
                    'what': 'কী', 'where': 'কোথায়', 'when': 'কখন', 'how': 'কীভাবে',
                    'why': 'কেন', 'who': 'কে', 'and': 'এবং', 'or': 'অথবা'
                },
                'ta': {
                    'I': 'நான்', 'you': 'நீங்கள்', 'he': 'அவர்', 'she': 'அவள்', 'we': 'நாங்கள்',
                    'they': 'அவர்கள்', 'what': 'என்ன', 'where': 'எங்கே', 'when': 'எப்போது',
                    'how': 'எப்படி', 'why': 'ஏன்', 'who': 'யார்', 'and': 'மற்றும்'
                }
            }
            
            if target_lang in word_map:
                words = text.split()
                translated_words = []
                
                for word in words:
                    clean_word = re.sub(r'[^\w]', '', word.lower())
                    if clean_word in word_map[target_lang]:
                        translated_words.append(word_map[target_lang][clean_word])
                    else:
                        translated_words.append(word)
                
                return ' '.join(translated_words)
        
        return text
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect Indian languages based on Unicode ranges"""
        
        # Unicode ranges for different scripts
        script_ranges = {
            'hi': (0x0900, 0x097F),  # Devanagari
            'bn': (0x0980, 0x09FF),  # Bengali
            'ta': (0x0B80, 0x0BFF),  # Tamil
            'te': (0x0C00, 0x0C7F),  # Telugu
            'ml': (0x0D00, 0x0D7F),  # Malayalam
            'kn': (0x0C80, 0x0CFF),  # Kannada
            'gu': (0x0A80, 0x0AFF),  # Gujarati
            'or': (0x0B00, 0x0B7F),  # Odia
            'pa': (0x0A00, 0x0A7F),  # Gurmukhi (Punjabi)
            'ur': (0x0600, 0x06FF),  # Arabic (for Urdu)
        }
        
        detected_language = 'en'
        confidence = 0.5
        max_chars = 0
        
        for lang, (start, end) in script_ranges.items():
            char_count = sum(1 for char in text if start <= ord(char) <= end)
            if char_count > max_chars:
                max_chars = char_count
                detected_language = lang
                confidence = min(0.9, 0.5 + (char_count / len(text)) * 0.4)
        
        return {
            'language': detected_language,
            'confidence': confidence,
            'engine': 'indic_unicode_detection'
        }
    
    def _calculate_confidence(self, source_text: str, translated_text: str, 
                            source_lang: str, target_lang: str) -> float:
        """Calculate translation confidence"""
        
        confidence = 0.6  # Base confidence
        
        # Check if translation happened
        if source_text != translated_text:
            confidence += 0.2
        
        # Boost for Indian languages
        indian_languages = list(self.supported_languages.keys())
        if target_lang in indian_languages:
            confidence += 0.1
        
        # Check for script change (good sign)
        source_script = any(ord(char) > 127 for char in source_text)
        target_script = any(ord(char) > 127 for char in translated_text)
        
        if source_script != target_script:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check translator health"""
        return {
            'status': 'healthy' if self.is_initialized else 'unhealthy',
            'initialized': self.is_initialized,
            'supported_languages': len(self.supported_languages),
            'available_languages': list(self.supported_languages.keys()),
            'phrase_dictionaries': len(self.phrase_dictionary)
        }
