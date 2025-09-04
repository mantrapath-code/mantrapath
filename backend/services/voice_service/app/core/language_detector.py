"""
Language Detector
Detects and handles multiple languages with Indian language support
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LanguageDetectionResult:
    """Language detection result"""
    primary_language: str
    confidence: float
    is_mixed: bool
    language_scores: Dict[str, float]
    script_detected: Optional[str] = None
    regions_detected: List[str] = None

class LanguageDetector:
    """Detects languages with focus on Indian languages"""
    
    def __init__(self):
        self.supported_languages = {
            "hi": "Hindi",
            "en": "English", 
            "bn": "Bengali",
            "ta": "Tamil",
            "te": "Telugu",
            "gu": "Gujarati",
            "mr": "Marathi",
            "pa": "Punjabi",
            "ur": "Urdu",
            "ml": "Malayalam",
            "kn": "Kannada",
            "as": "Assamese",
            "or": "Odia",
            "ne": "Nepali",
            "si": "Sinhala"
        }
        
        self.language_patterns = self._load_language_patterns()
        self.script_patterns = self._load_script_patterns()
        self.common_words = self._load_common_words()
        
    def _load_language_patterns(self) -> Dict[str, List[str]]:
        """Load language-specific regex patterns"""
        return {
            "hi": [
                r"\b(है|हैं|था|थे|को|की|का|के|में|पर|से|तक|और|या|क्या|कैसे|कहाँ|कब|क्यों)\b",
                r"[अ-ह]",  # Devanagari script
                r"\b(आप|हम|मैं|तुम|वह|यह|जो|कौन)\b"
            ],
            "en": [
                r"\b(the|and|or|but|is|are|was|were|have|has|had|do|does|did|will|would|can|could|should|must)\b",
                r"\b(I|you|he|she|it|we|they|this|that|what|where|when|why|how)\b",
                r"[a-zA-Z]+"
            ],
            "bn": [
                r"[অ-হ]",  # Bengali script
                r"\b(আছে|আছি|আছেন|ছিল|ছিলেন|হয়|হয়েছে|করে|করেছে|বলে|বলেছে)\b",
                r"\b(আমি|তুমি|তিনি|আমরা|তোমরা|তারা|এই|সেই|যে|কী|কোথায়|কখন|কেন)\b"
            ],
            "ta": [
                r"[அ-ஹ]",  # Tamil script
                r"\b(இருக்கிறது|இருந்தது|செய்கிறது|செய்தது|சொல்கிறது|சொன்னது)\b",
                r"\b(நான்|நீ|அவன்|அவள்|நாம்|நீங்கள்|அவர்கள்|இது|அது|என்ன|எங்கே|எப்போது|ஏன்)\b"
            ],
            "te": [
                r"[అ-హ]",  # Telugu script
                r"\b(ఉంది|ఉన్నది|చేస్తుంది|చేసింది|అంటుంది|అన్నది)\b",
                r"\b(నేను|నువ్వు|అతను|ఆమె|మేము|మీరు|వారు|ఇది|అది|ఏమిటి|ఎక్కడ|ఎప్పుడు|ఎందుకు)\b"
            ],
            "gu": [
                r"[અ-હ]",  # Gujarati script
                r"\b(છે|હતું|કરે|કર્યું|કહે|કહ્યું)\b",
                r"\b(હું|તું|તે|અમે|તમે|તેઓ|આ|તે|શું|ક્યાં|ક્યારે|શા માટે)\b"
            ],
            "mr": [
                r"[अ-ह]",  # Devanagari (same as Hindi but different words)
                r"\b(आहे|होते|करतो|केले|म्हणतो|म्हणाले)\b",
                r"\b(मी|तू|तो|ती|आम्ही|तुम्ही|ते|हे|ते|काय|कुठे|कधी|का)\b"
            ],
            "pa": [
                r"[ਅ-ਹ]",  # Gurmukhi script
                r"\b(ਹੈ|ਸੀ|ਕਰਦਾ|ਕੀਤਾ|ਕਹਿੰਦਾ|ਕਿਹਾ)\b",
                r"\b(ਮੈਂ|ਤੂੰ|ਉਹ|ਅਸੀਂ|ਤੁਸੀਂ|ਉਹ|ਇਹ|ਉਹ|ਕੀ|ਕਿੱਥੇ|ਕਦੋਂ|ਕਿਉਂ)\b"
            ],
            "ur": [
                r"[آ-ی]",  # Arabic script
                r"\b(ہے|تھا|کرتا|کیا|کہتا|کہا)\b",
                r"\b(میں|تم|وہ|ہم|آپ|وہ|یہ|وہ|کیا|کہاں|کب|کیوں)\b"
            ]
        }
    
    def _load_script_patterns(self) -> Dict[str, str]:
        """Load script detection patterns"""
        return {
            "devanagari": r"[अ-ह]",
            "bengali": r"[অ-হ]", 
            "tamil": r"[அ-ஹ]",
            "telugu": r"[అ-హ]",
            "gujarati": r"[અ-હ]",
            "gurmukhi": r"[ਅ-ਹ]",
            "arabic": r"[آ-ی]",
            "latin": r"[a-zA-Z]"
        }
    
    def _load_common_words(self) -> Dict[str, List[str]]:
        """Load common words for each language"""
        return {
            "hi": ["और", "है", "में", "को", "का", "की", "के", "से", "पर", "हैं", "था", "थे", "हो", "तो", "ही", "भी", "जो", "कि", "यह", "वह"],
            "en": ["the", "and", "to", "of", "a", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "as", "with", "his", "they", "i"],
            "bn": ["এবং", "হয়", "মধ্যে", "কে", "এর", "দিয়ে", "উপর", "আছে", "ছিল", "তাহলে", "শুধু", "এছাড়াও", "যারা", "যে", "এই", "সেই"],
            "ta": ["மற்றும்", "உள்ளது", "இல்", "க்கு", "இன்", "கொண்டு", "மீது", "உள்ளன", "இருந்தது", "பின்னர்", "மட்டும்", "கூட", "யார்", "என்று", "இந்த", "அந்த"],
            "te": ["మరియు", "ఉంది", "లో", "కు", "యొక్క", "తో", "మీద", "ఉన్నాయి", "ఉండేది", "అప్పుడు", "మాత్రమే", "కూడా", "ఎవరు", "అని", "ఈ", "ఆ"],
            "gu": ["અને", "છે", "માં", "ને", "ના", "સાથે", "પર", "છે", "હતું", "તો", "માત્ર", "પણ", "જે", "કે", "આ", "તે"],
            "mr": ["आणि", "आहे", "मध्ये", "ला", "चा", "सह", "वर", "आहेत", "होते", "तर", "फक्त", "सुद्धा", "जे", "की", "हे", "ते"],
            "pa": ["ਅਤੇ", "ਹੈ", "ਵਿੱਚ", "ਨੂੰ", "ਦਾ", "ਨਾਲ", "ਤੇ", "ਹਨ", "ਸੀ", "ਤਾਂ", "ਸਿਰਫ", "ਵੀ", "ਜੋ", "ਕਿ", "ਇਹ", "ਉਹ"],
            "ur": ["اور", "ہے", "میں", "کو", "کا", "کے", "ساتھ", "پر", "ہیں", "تھا", "تو", "صرف", "بھی", "جو", "کہ", "یہ", "وہ"]
        }
    
    def detect_language(self, text: str) -> LanguageDetectionResult:
        """Detect language(s) in text"""
        if not text.strip():
            return LanguageDetectionResult(
                primary_language="en",
                confidence=0.0,
                is_mixed=False,
                language_scores={},
                script_detected="latin"
            )
        
        # Calculate scores for each language
        language_scores = {}
        script_detected = self._detect_script(text)
        
        for lang_code, patterns in self.language_patterns.items():
            score = self._calculate_language_score(text, lang_code, patterns)
            if score > 0:
                language_scores[lang_code] = score
        
        # If no pattern matches, fallback to common words
        if not language_scores:
            language_scores = self._fallback_word_detection(text)
        
        # Determine primary language and confidence
        if language_scores:
            primary_language = max(language_scores, key=language_scores.get)
            confidence = language_scores[primary_language]
            
            # Normalize confidence (0-1 scale)
            max_possible_score = len(text.split()) * 2  # Rough estimate
            confidence = min(confidence / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
        else:
            primary_language = "en"  # Default fallback
            confidence = 0.1
        
        # Check for mixed languages
        is_mixed = len([score for score in language_scores.values() if score > 0.1]) > 1
        
        return LanguageDetectionResult(
            primary_language=primary_language,
            confidence=confidence,
            is_mixed=is_mixed,
            language_scores=language_scores,
            script_detected=script_detected,
            regions_detected=self._detect_regions(language_scores)
        )
    
    def _detect_script(self, text: str) -> Optional[str]:
        """Detect the writing script used"""
        script_counts = {}
        
        for script_name, pattern in self.script_patterns.items():
            matches = len(re.findall(pattern, text))
            if matches > 0:
                script_counts[script_name] = matches
        
        if script_counts:
            return max(script_counts, key=script_counts.get)
        
        return "latin"  # Default
    
    def _calculate_language_score(self, text: str, lang_code: str, patterns: List[str]) -> float:
        """Calculate language score based on patterns"""
        total_score = 0.0
        text_lower = text.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            total_score += len(matches)
        
        # Bonus for common words
        if lang_code in self.common_words:
            for word in self.common_words[lang_code]:
                if word.lower() in text_lower:
                    total_score += 2  # Higher weight for common words
        
        return total_score
    
    def _fallback_word_detection(self, text: str) -> Dict[str, float]:
        """Fallback detection using common words only"""
        scores = {}
        text_words = set(text.lower().split())
        
        for lang_code, common_words in self.common_words.items():
            matches = sum(1 for word in common_words if word.lower() in text_words)
            if matches > 0:
                scores[lang_code] = matches
        
        return scores
    
    def _detect_regions(self, language_scores: Dict[str, float]) -> List[str]:
        """Detect geographical regions based on detected languages"""
        regions = []
        
        # Indian subcontinent languages
        indian_languages = {"hi", "bn", "ta", "te", "gu", "mr", "pa", "ur", "ml", "kn", "as", "or"}
        if any(lang in language_scores for lang in indian_languages):
            regions.append("south_asia")
        
        # English-speaking regions
        if "en" in language_scores:
            regions.append("global")
        
        return regions
    
    def get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        return self.supported_languages.get(lang_code, lang_code.upper())
    
    def is_supported(self, lang_code: str) -> bool:
        """Check if language is supported"""
        return lang_code in self.supported_languages
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return self.supported_languages.copy()
    
    def detect_code_switching(self, text: str) -> Dict[str, Any]:
        """Detect code-switching (language mixing) patterns"""
        sentences = re.split(r'[.!?।]', text)
        sentence_languages = []
        
        for sentence in sentences:
            if sentence.strip():
                detection = self.detect_language(sentence.strip())
                sentence_languages.append({
                    "text": sentence.strip(),
                    "language": detection.primary_language,
                    "confidence": detection.confidence
                })
        
        # Analyze patterns
        languages_used = set(s["language"] for s in sentence_languages)
        is_code_switching = len(languages_used) > 1
        
        # Common code-switching patterns for Indian context
        switching_patterns = []
        if "hi" in languages_used and "en" in languages_used:
            switching_patterns.append("hinglish")
        
        return {
            "is_code_switching": is_code_switching,
            "languages_used": list(languages_used),
            "sentence_breakdown": sentence_languages,
            "switching_patterns": switching_patterns,
            "primary_languages": list(languages_used)[:2]  # Top 2 languages
        }
    
    def suggest_response_language(self, detection_result: LanguageDetectionResult, 
                                user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Suggest the best language for response"""
        # Check user preferences first
        if user_preferences and user_preferences.get("preferred_language"):
            preferred = user_preferences["preferred_language"]
            if self.is_supported(preferred):
                return preferred
        
        # Use detected primary language if confidence is high
        if detection_result.confidence > 0.7:
            return detection_result.primary_language
        
        # For mixed languages, prefer Hindi over English in Indian context
        if detection_result.is_mixed:
            indian_langs = {"hi", "bn", "ta", "te", "gu", "mr", "pa", "ur", "ml", "kn"}
            detected_indian = [lang for lang in detection_result.language_scores.keys() 
                             if lang in indian_langs]
            if detected_indian:
                return detected_indian[0]  # First detected Indian language
        
        # Default to English
        return "en"
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for language detector"""
        return {
            "status": "healthy",
            "supported_languages": len(self.supported_languages),
            "language_patterns_loaded": len(self.language_patterns),
            "script_patterns_loaded": len(self.script_patterns),
            "features": [
                "multi_language_detection",
                "script_detection", 
                "code_switching_detection",
                "indian_language_support",
                "confidence_scoring"
            ]
        }
