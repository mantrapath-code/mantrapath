"""
Enhanced Multilingual Voice Support for API Gateway V3
Real language detection and processing with proper NLP integration
"""

import logging
import asyncio
import httpx
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from .models import VoiceLanguageCode, LanguageSupport

logger = logging.getLogger(__name__)


@dataclass
class LanguageDetectionResult:
    """Result of language detection with confidence"""
    language: str
    confidence: float
    script: Optional[str] = None
    regional_variant: Optional[str] = None
    

@dataclass
class CulturalRegion:
    """Cultural region configuration"""
    name: str
    countries: List[str]
    primary_languages: List[str]
    cultural_values: Dict[str, Any]
    communication_style: str
    time_orientation: str
    script_systems: List[str]


class EnhancedLanguageDetector:
    """Enhanced language detection using multiple methods"""
    
    def __init__(self):
        self.translation_service_url = "http://localhost:8005"  # Translation service
        self.fallback_patterns = self._initialize_fallback_patterns()
    
    def _initialize_fallback_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize fallback patterns for when services are unavailable"""
        return {
            # Devanagari script languages
            "hi": {
                "script_range": (0x0900, 0x097F),
                "common_words": ["है", "हूँ", "आज", "मैं", "का", "की", "के", "में", "से"],
                "patterns": [r"[\u0900-\u097F]+"]
            },
            "mr": {
                "script_range": (0x0900, 0x097F),
                "common_words": ["आहे", "आज", "मी", "माझा", "तुमचा"],
                "patterns": [r"[\u0900-\u097F]+"]
            },
            "gu": {
                "script_range": (0x0A80, 0x0AFF),
                "common_words": ["છે", "હું", "આજે", "મારા"],
                "patterns": [r"[\u0A80-\u0AFF]+"]
            },
            
            # Tamil
            "ta": {
                "script_range": (0x0B80, 0x0BFF),
                "common_words": ["இருக்கிறேன்", "நான்", "இன்று", "என்"],
                "patterns": [r"[\u0B80-\u0BFF]+"]
            },
            
            # Telugu
            "te": {
                "script_range": (0x0C00, 0x0C7F),
                "common_words": ["ఉన్నాను", "నేను", "ఈరోజు", "నా"],
                "patterns": [r"[\u0C00-\u0C7F]+"]
            },
            
            # Bengali
            "bn": {
                "script_range": (0x0980, 0x09FF),
                "common_words": ["আছি", "আমি", "আজ", "আমার"],
                "patterns": [r"[\u0980-\u09FF]+"]
            },
            
            # Malayalam
            "ml": {
                "script_range": (0x0D00, 0x0D7F),
                "common_words": ["ഞാൻ", "ഇന്ന്", "എന്റെ"],
                "patterns": [r"[\u0D00-\u0D7F]+"]
            },
            
            # Kannada
            "kn": {
                "script_range": (0x0C80, 0x0CFF),
                "common_words": ["ನಾನು", "ಇಂದು", "ನನ್ನ"],
                "patterns": [r"[\u0C80-\u0CFF]+"]
            },
            
            # Punjabi
            "pa": {
                "script_range": (0x0A00, 0x0A7F),
                "common_words": ["ਮੈਂ", "ਅੱਜ", "ਮੇਰਾ"],
                "patterns": [r"[\u0A00-\u0A7F]+"]
            },
            
            # Urdu (Arabic script)
            "ur": {
                "script_range": (0x0600, 0x06FF),
                "common_words": ["ہوں", "میں", "آج", "میرا"],
                "patterns": [r"[\u0600-\u06FF]+"]
            },
            
            # English
            "en": {
                "script_range": (0x0000, 0x007F),
                "common_words": ["the", "and", "is", "am", "my", "today", "feeling", "mood"],
                "patterns": [r"[a-zA-Z]+"]
            }
        }
    
    async def detect_language_advanced(self, text: str) -> LanguageDetectionResult:
        """Advanced language detection using translation service"""
        try:
            # First try the translation service for proper detection
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.post(
                    f"{self.translation_service_url}/detect-language",
                    json={"text": text}
                )
                if response.status_code == 200:
                    data = response.json()
                    return LanguageDetectionResult(
                        language=data.get("language", "en"),
                        confidence=data.get("confidence", 0.8),
                        script=data.get("script"),
                        regional_variant=data.get("regional_variant")
                    )
        except Exception as e:
            logger.warning(f"Translation service unavailable, using fallback: {e}")
        
        # Fallback to local detection
        return self._detect_language_fallback(text)
    
    def _detect_language_fallback(self, text: str) -> LanguageDetectionResult:
        """Fallback language detection using script and pattern analysis"""
        text_lower = text.lower().strip()
        
        # Script-based detection for Indian languages
        for lang_code, lang_info in self.fallback_patterns.items():
            script_start, script_end = lang_info["script_range"]
            
            # Check if text contains characters from this script
            script_chars = sum(1 for char in text if script_start <= ord(char) <= script_end)
            total_chars = len([c for c in text if not c.isspace()])
            
            if total_chars > 0:
                script_ratio = script_chars / total_chars
                
                if script_ratio > 0.7:  # 70% of characters match script
                    # Additional word-based verification
                    word_matches = sum(1 for word in lang_info["common_words"] if word in text)
                    confidence = min(0.95, script_ratio + (word_matches * 0.1))
                    
                    return LanguageDetectionResult(
                        language=lang_code,
                        confidence=confidence,
                        script=f"script_{script_start:04x}_{script_end:04x}"
                    )
        
        # Default to English with low confidence
        return LanguageDetectionResult(
            language="en",
            confidence=0.3,
            script="latin"
        )


class MultilingualVoiceSupport:
    """Enhanced multilingual voice support with real language processing"""
    
    def __init__(self):
        self.supported_languages: Dict[str, LanguageSupport] = {}
        self.cultural_regions: Dict[str, CulturalRegion] = {}
        self.language_detector = EnhancedLanguageDetector()
        self._initialize_comprehensive_language_support()
        self._initialize_enhanced_cultural_regions()
    
    def _initialize_comprehensive_language_support(self):
        """Initialize comprehensive language support including all Indian regional languages"""
        languages = [
            # Primary languages
            LanguageSupport(
                code=VoiceLanguageCode.ENGLISH,
                name="English",
                support_level="primary",
                cultural_context="global",
                regional_variants=["US", "UK", "AU", "CA", "IN", "SG"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.HINDI,
                name="Hindi (हिन्दी)",
                support_level="primary",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-DL", "IN-UP", "IN-MP", "IN-RJ", "IN-HR"]
            ),
            
            # Indian Regional Languages - Primary Support
            LanguageSupport(
                code=VoiceLanguageCode.BENGALI,
                name="Bengali (বাংলা)",
                support_level="primary",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-WB", "BD", "IN-AS"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.TAMIL,
                name="Tamil (தமிழ்)",
                support_level="primary",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-TN", "LK", "MY", "SG"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.TELUGU,
                name="Telugu (తెలుగు)",
                support_level="primary",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-AP", "IN-TG"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.MARATHI,
                name="Marathi (मराठी)",
                support_level="primary",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-MH", "IN-GO"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.GUJARATI,
                name="Gujarati (ગુજરાતી)",
                support_level="primary",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-GJ", "IN-DN", "IN-DD"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.PUNJABI,
                name="Punjabi (ਪੰਜਾਬੀ)",
                support_level="regional",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-PB", "PK", "IN-CH"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.KANNADA,
                name="Kannada (ಕನ್ನಡ)",
                support_level="regional",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-KA"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.MALAYALAM,
                name="Malayalam (മലയാളം)",
                support_level="regional",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-KL", "IN-LD"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.URDU,
                name="Urdu (اردو)",
                support_level="regional",
                cultural_context="indian_subcontinent",
                regional_variants=["PK", "IN-UP", "IN-JK", "IN-BR"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.ASSAMESE,
                name="Assamese (অসমীয়া)",
                support_level="regional",
                cultural_context="indian_subcontinent",
                regional_variants=["IN-AS"]
            ),
            
            # International languages
            LanguageSupport(
                code=VoiceLanguageCode.SPANISH,
                name="Spanish (Español)",
                support_level="secondary",
                cultural_context="latin_america",
                regional_variants=["ES", "MX", "AR", "CO", "PE", "CL"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.FRENCH,
                name="French (Français)",
                support_level="secondary",
                cultural_context="western_europe",
                regional_variants=["FR", "CA", "BE", "CH", "LU"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.GERMAN,
                name="German (Deutsch)",
                support_level="secondary",
                cultural_context="western_europe",
                regional_variants=["DE", "AT", "CH", "LI"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.CHINESE,
                name="Chinese (中文)",
                support_level="secondary",
                cultural_context="east_asia",
                regional_variants=["CN", "TW", "HK", "SG", "MO"]
            ),
            LanguageSupport(
                code=VoiceLanguageCode.ARABIC,
                name="Arabic (العربية)",
                support_level="secondary",
                cultural_context="middle_east",
                regional_variants=["SA", "AE", "EG", "MA", "JO", "LB"]
            )
        ]
        
        for lang in languages:
            self.supported_languages[lang.code.value] = lang
        
        logger.info(f"Initialized {len(languages)} comprehensive supported languages")
    
    def _initialize_enhanced_cultural_regions(self):
        """Initialize enhanced cultural regions with script information"""
        regions = [
            CulturalRegion(
                name="indian_subcontinent",
                countries=["IN", "PK", "BD", "LK", "NP", "BT", "MV"],
                primary_languages=["hi", "bn", "ta", "te", "mr", "gu", "kn", "ml", "pa", "ur", "as"],
                cultural_values={
                    "family_importance": "very_high",
                    "elder_respect": "very_high",
                    "spiritual_practices": "integral",
                    "collective_orientation": "high",
                    "hierarchy_acceptance": "high",
                    "hospitality": "central",
                    "festival_significance": "high"
                },
                communication_style="high-context",
                time_orientation="polychronic",
                script_systems=["Devanagari", "Bengali", "Tamil", "Telugu", "Gujarati", "Gurmukhi", "Kannada", "Malayalam", "Arabic"]
            ),
            CulturalRegion(
                name="western_europe",
                countries=["DE", "FR", "IT", "ES", "UK", "NL", "BE", "CH", "AT", "PT", "IE"],
                primary_languages=["en", "de", "fr", "it", "es", "pt"],
                cultural_values={
                    "individual_autonomy": "very_high",
                    "privacy_emphasis": "high",
                    "work_life_balance": "important",
                    "direct_communication": "preferred",
                    "punctuality": "valued",
                    "innovation": "encouraged"
                },
                communication_style="direct",
                time_orientation="monochronic",
                script_systems=["Latin"]
            ),
            CulturalRegion(
                name="east_asia",
                countries=["JP", "KR", "CN", "TW", "HK", "SG", "MO"],
                primary_languages=["ja", "ko", "zh"],
                cultural_values={
                    "harmony_focus": "very_high",
                    "respect_hierarchy": "important",
                    "face_saving": "critical",
                    "group_consensus": "preferred",
                    "education_value": "high",
                    "technology_adoption": "high"
                },
                communication_style="indirect",
                time_orientation="monochronic",
                script_systems=["Hanzi", "Hiragana", "Katakana", "Kanji", "Hangul"]
            )
        ]
        
        for region in regions:
            self.cultural_regions[region.name] = region
        
        logger.info(f"Initialized {len(regions)} enhanced cultural regions")
    
    async def detect_language(self, text: str, hint: Optional[str] = None) -> str:
        """Enhanced language detection using AI services"""
        if hint and hint in self.supported_languages:
            return hint
        
        detection_result = await self.language_detector.detect_language_advanced(text)
        
        # Validate detected language is supported
        if detection_result.language in self.supported_languages:
            logger.info(f"Detected language: {detection_result.language} (confidence: {detection_result.confidence:.2f})")
            return detection_result.language
        
        # Fallback to English
        logger.warning(f"Unsupported language detected: {detection_result.language}, falling back to English")
        return "en"
    
    def get_cultural_context(self, language: str, country: Optional[str] = None) -> Optional[str]:
        """Get cultural context for a language with country consideration"""
        lang_support = self.supported_languages.get(language)
        if not lang_support:
            return None
        
        # If country is provided, check for specific regional variants
        if country and lang_support.regional_variants:
            for variant in lang_support.regional_variants:
                if variant.startswith(country):
                    return lang_support.cultural_context
        
        return lang_support.cultural_context
    
    def get_supported_languages_by_level(self, level: str) -> List[LanguageSupport]:
        """Get languages by support level with enhanced Indian regional support"""
        return [lang for lang in self.supported_languages.values() 
                if lang.support_level == level]
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported with full feature set"""
        return language in self.supported_languages
    
    def get_language_info(self, language: str) -> Optional[LanguageSupport]:
        """Get detailed information about a language including script info"""
        return self.supported_languages.get(language)
    
    def get_regional_adaptations(self, cultural_context: str) -> Optional[CulturalRegion]:
        """Get enhanced regional adaptations for a cultural context"""
        return self.cultural_regions.get(cultural_context)
    
    def suggest_fallback_language(self, original_language: str) -> str:
        """Intelligent fallback language suggestion based on script and region"""
        lang_info = self.supported_languages.get(original_language)
        
        if not lang_info:
            return "en"  # Global fallback
        
        # For Indian regional languages, suggest Hindi as primary fallback
        if lang_info.cultural_context == "indian_subcontinent":
            if original_language != "hi":
                return "hi"  # Hindi as primary Indian language
            else:
                return "en"  # English if Hindi itself needs fallback
        
        # For other regions, suggest English
        return "en"
    
    async def get_voice_examples_for_language(self, language: str) -> List[Dict[str, str]]:
        """Get dynamic voice command examples from translation service"""
        try:
            # Try to get examples from translation service
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(
                    f"{self.language_detector.translation_service_url}/voice-examples/{language}"
                )
                if response.status_code == 200:
                    return response.json().get("examples", [])
        except Exception as e:
            logger.warning(f"Could not fetch dynamic examples: {e}")
        
        # Fallback to static examples
        return self._get_static_voice_examples(language)
    
    def _get_static_voice_examples(self, language: str) -> List[Dict[str, str]]:
        """Static voice command examples as fallback"""
        examples = {
            "en": [
                {"intent": "mood_tracking", "text": "I'm feeling happy today"},
                {"intent": "journal_entry", "text": "Start a new journal entry"},
                {"intent": "chatbot_query", "text": "Ask the chatbot about meditation"},
                {"intent": "content_request", "text": "Show me mindfulness content"}
            ],
            "hi": [
                {"intent": "mood_tracking", "text": "मैं आज खुश हूँ"},
                {"intent": "journal_entry", "text": "नई डायरी शुरू करें"},
                {"intent": "chatbot_query", "text": "चैटबॉट से मेडिटेशन के बारे में पूछें"},
                {"intent": "content_request", "text": "मानसिक शांति की सामग्री दिखाएं"}
            ],
            "bn": [
                {"intent": "mood_tracking", "text": "আমি আজ খুশি অনুভব করছি"},
                {"intent": "journal_entry", "text": "নতুন জার্নাল এন্ট্রি শুরু করুন"},
                {"intent": "chatbot_query", "text": "চ্যাটবট এর কাছে ধ্যান সম্পর্কে জিজ্ঞাসা করুন"}
            ],
            "ta": [
                {"intent": "mood_tracking", "text": "நான் இன்று மகிழ்ச்சியாக உணர்கிறேன்"},
                {"intent": "journal_entry", "text": "புதிய பொறிவெழுதார் நுזैन்"},
                {"intent": "chatbot_query", "text": "சாட்பாட்டிடம் தியானம் பற்றி கேளுங்கள்"}
            ],
            "te": [
                {"intent": "mood_tracking", "text": "నేను ఈరోజు సంతోషంగా ఉన్నాను"},
                {"intent": "journal_entry", "text": "కొత్త జర్నల్ ఎంట్రీ ప్రారంభించండి"},
                {"intent": "chatbot_query", "text": "చాట్‌బాట్‌ను ధ్యానం గురించి అడగండి"}
            ],
            "gu": [
                {"intent": "mood_tracking", "text": "હું આજે ખુશ છું"},
                {"intent": "journal_entry", "text": "નવી જર્નલ એન્ટ્રી શરૂ કરો"},
                {"intent": "chatbot_query", "text": "ચેટબોટને ધ્યાન વિશે પૂછો"}
            ],
            "mr": [
                {"intent": "mood_tracking", "text": "मी आज आनंदी आहे"},
                {"intent": "journal_entry", "text": "नवीन जर्नल एंट्री सुरू करा"},
                {"intent": "chatbot_query", "text": "चॅटबॉटला ध्यान बद्दल विचारा"}
            ],
            "pa": [
                {"intent": "mood_tracking", "text": "ਮੈਂ ਅੱਜ ਖੁਸ਼ ਹਾਂ"},
                {"intent": "journal_entry", "text": "ਨਵੀਂ ਜਰਨਲ ਐਂਟਰੀ ਸ਼ੁਰੂ ਕਰੋ"},
                {"intent": "chatbot_query", "text": "ਚੈਟਬਾਟ ਨੂੰ ਮੈਡੀਟੇਸ਼ਨ ਬਾਰੇ ਪੁੱਛੋ"}
            ],
            "kn": [
                {"intent": "mood_tracking", "text": "ನಾನು ಇಂದು ಸಂತೋಷವಾಗಿದ್ದೇನೆ"},
                {"intent": "journal_entry", "text": "ಹೊಸ ಜರ್ನಲ್ ಎಂಟ್ರಿ ಪ್ರಾರಂಭಿಸಿ"},
                {"intent": "chatbot_query", "text": "ಚಾಟ್‌ಬಾಟ್‌ಗೆ ಧ್ಯಾನದ ಬಗ್ಗೆ ಕೇಳಿ"}
            ],
            "ml": [
                {"intent": "mood_tracking", "text": "ഞാൻ ഇന്ന് സന്തോഷവാനാണ്"},
                {"intent": "journal_entry", "text": "പുതിയ ജേണൽ എൻട്രി ആരംഭിക്കുക"},
                {"intent": "chatbot_query", "text": "ചാറ്റ്ബോട്ടിനോട് ധ്യാനത്തെക്കുറിച്ച് ചോദിക്കുക"}
            ],
            "ur": [
                {"intent": "mood_tracking", "text": "میں آج خوش ہوں"},
                {"intent": "journal_entry", "text": "نیا جرنل انٹری شروع کریں"},
                {"intent": "chatbot_query", "text": "چیٹ بوٹ سے مراقبہ کے بارے میں پوچھیں"}
            ]
        }
        
        return examples.get(language, examples["en"])
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about language support"""
        by_level = {}
        for level in ["primary", "secondary", "regional"]:
            by_level[level] = len(self.get_supported_languages_by_level(level))
        
        by_region = {}
        indian_languages = 0
        for region_name in self.cultural_regions.keys():
            languages = [lang for lang in self.supported_languages.values() 
                        if lang.cultural_context == region_name]
            by_region[region_name] = len(languages)
            if region_name == "indian_subcontinent":
                indian_languages = len(languages)
        
        by_script = {}
        for lang in self.supported_languages.values():
            # Determine script system from language code
            script = self._get_script_for_language(lang.code.value)
            by_script[script] = by_script.get(script, 0) + 1
        
        return {
            "total_languages": len(self.supported_languages),
            "indian_regional_languages": indian_languages,
            "by_support_level": by_level,
            "by_cultural_region": by_region,
            "by_script_system": by_script,
            "total_cultural_regions": len(self.cultural_regions),
            "voice_enabled": True,
            "real_time_translation": True
        }
    
    def _get_script_for_language(self, language: str) -> str:
        """Get script system for a language"""
        script_mapping = {
            "hi": "Devanagari", "mr": "Devanagari", "ne": "Devanagari",
            "bn": "Bengali", "as": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "gu": "Gujarati",
            "pa": "Gurmukhi",
            "kn": "Kannada",
            "ml": "Malayalam",
            "ur": "Arabic", "ar": "Arabic",
            "zh": "Hanzi", "ja": "Kanji/Hiragana", "ko": "Hangul",
            "en": "Latin", "es": "Latin", "fr": "Latin", "de": "Latin", "it": "Latin", "pt": "Latin"
        }
        return script_mapping.get(language, "Latin")
    
    async def validate_voice_input(self, text: str, expected_language: Optional[str] = None) -> Dict[str, Any]:
        """Validate voice input quality and language consistency"""
        detection_result = await self.language_detector.detect_language_advanced(text)
        
        validation_result = {
            "is_valid": True,
            "detected_language": detection_result.language,
            "confidence": detection_result.confidence,
            "issues": []
        }
        
        # Check language consistency
        if expected_language and detection_result.language != expected_language:
            if detection_result.confidence > 0.7:
                validation_result["issues"].append(f"Language mismatch: expected {expected_language}, detected {detection_result.language}")
            else:
                validation_result["issues"].append("Low confidence language detection")
        
        # Check text quality
        if len(text.strip()) < 3:
            validation_result["is_valid"] = False
            validation_result["issues"].append("Text too short for reliable processing")
        
        # Check for supported language
        if detection_result.language not in self.supported_languages:
            validation_result["issues"].append(f"Unsupported language: {detection_result.language}")
            validation_result["suggested_fallback"] = self.suggest_fallback_language(detection_result.language)
        
        return validation_result
    
    def get_cultural_context(self, language: str, country: Optional[str] = None) -> Optional[str]:
        """Get cultural context for a language"""
        lang_support = self.supported_languages.get(language)
        if not lang_support:
            return None
        
        return lang_support.cultural_context
    
    def get_supported_languages_by_level(self, level: str) -> List[LanguageSupport]:
        """Get languages by support level (primary, secondary, regional)"""
        return [lang for lang in self.supported_languages.values() 
                if lang.support_level == level]
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a language is supported"""
        return language in self.supported_languages
    
    def get_language_info(self, language: str) -> Optional[LanguageSupport]:
        """Get detailed information about a language"""
        return self.supported_languages.get(language)
    
    def get_regional_adaptations(self, cultural_context: str) -> Optional[CulturalRegion]:
        """Get regional adaptations for a cultural context"""
        return self.cultural_regions.get(cultural_context)
    
    def suggest_fallback_language(self, original_language: str) -> str:
        """Suggest a fallback language if the original is not supported"""
        lang_info = self.supported_languages.get(original_language)
        
        if not lang_info:
            # Language not supported, return English as fallback
            return "en"
        
        # If language is supported but maybe regional, suggest primary alternative
        if lang_info.support_level == "regional":
            # For Indian regional languages, suggest Hindi or English
            if lang_info.cultural_context == "indian_subcontinent":
                return "hi"  # Hindi as primary Indian language
            else:
                return "en"  # English as global fallback
        
        return original_language  # Language is supported
    
    def get_voice_examples_for_language(self, language: str) -> List[Dict[str, str]]:
        """Get voice command examples for a specific language"""
        examples = {
            "en": [
                {"intent": "mood_tracking", "text": "I'm feeling happy today"},
                {"intent": "journal_entry", "text": "Start a new journal entry"},
                {"intent": "chatbot_query", "text": "Ask the chatbot about meditation"}
            ],
            "hi": [
                {"intent": "mood_tracking", "text": "मैं आज खुश हूँ"},
                {"intent": "journal_entry", "text": "नई डायरी शुरू करें"},
                {"intent": "chatbot_query", "text": "चैटबॉट से मेडिटेशन के बारे में पूछें"}
            ],
            "es": [
                {"intent": "mood_tracking", "text": "Me siento feliz hoy"},
                {"intent": "journal_entry", "text": "Empezar nueva entrada de diario"},
                {"intent": "chatbot_query", "text": "Pregunta al chatbot sobre meditación"}
            ],
            "fr": [
                {"intent": "mood_tracking", "text": "Je me sens heureux aujourd'hui"},
                {"intent": "journal_entry", "text": "Commencer une nouvelle entrée de journal"},
                {"intent": "chatbot_query", "text": "Demander au chatbot à propos de la méditation"}
            ]
        }
        
        return examples.get(language, examples["en"])
    
    def get_language_statistics(self) -> Dict[str, Any]:
        """Get statistics about language support"""
        by_level = {}
        for level in ["primary", "secondary", "regional"]:
            by_level[level] = len(self.get_supported_languages_by_level(level))
        
        by_region = {}
        for region_name in self.cultural_regions.keys():
            languages = [lang for lang in self.supported_languages.values() 
                        if lang.cultural_context == region_name]
            by_region[region_name] = len(languages)
        
        return {
            "total_languages": len(self.supported_languages),
            "by_support_level": by_level,
            "by_cultural_region": by_region,
            "total_cultural_regions": len(self.cultural_regions)
        }
