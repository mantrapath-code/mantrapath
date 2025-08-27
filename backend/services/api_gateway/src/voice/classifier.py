"""
Voice Intent Classifier for Enhanced API Gateway V3
Classifies voice commands into intents with confidence scoring
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from .models import VoiceIntentType, VoiceCommand, VoiceLanguageCode

logger = logging.getLogger(__name__)


@dataclass
class IntentPattern:
    """Pattern for intent classification"""
    intent: VoiceIntentType
    patterns: List[str]  # Regex patterns
    keywords: List[str]  # Keywords for additional matching
    language: VoiceLanguageCode
    confidence_weight: float = 1.0


class VoiceIntentClassifier:
    """Classifies voice commands into structured intents"""
    
    def __init__(self):
        self.intent_patterns: Dict[str, List[IntentPattern]] = {}
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize intent classification patterns for all supported languages"""
        # English patterns
        self._add_patterns("en", [
            IntentPattern(
                intent=VoiceIntentType.MOOD_TRACKING,
                patterns=[
                    r"i(?:'m| am) feeling (\w+)",
                r"my mood is (\w+)",
                r"track my mood as (\w+)",
                r"mood (\d+) out of (\d+)",
                r"feeling (\w+) today",
                r"i(?:'m| am) (\w+)",
                r"mood is (\w+)"
                ],
                keywords=["mood", "feeling", "emotional", "track", "log"],
                language=VoiceLanguageCode.ENGLISH,
                confidence_weight=1.0
            ),
            IntentPattern(
                intent=VoiceIntentType.JOURNAL_ENTRY,
                patterns=[
                    r"start (?:a )?new journal (?:entry)?",
                    r"add to my journal",
                    r"write (?:about|in) my (?:journal|diary)",
                    r"journal entry about (.+)",
                    r"record (?:in )?my journal",
                    r"write about my (.+)",
                    r"start writing"
                ],
                keywords=["journal", "diary", "write", "record", "entry", "writing"],
                language=VoiceLanguageCode.ENGLISH,
                confidence_weight=1.0
            ),
            IntentPattern(
                intent=VoiceIntentType.CHATBOT_QUERY,
                patterns=[
                    r"ask (?:the )?chatbot (.+)",
                    r"question (?:for|to) (?:the )?bot",
                    r"chat with (?:the )?bot",
                    r"talk to (?:the )?assistant",
                    r"help me with (.+)"
                ],
                keywords=["chatbot", "assistant", "help", "question", "ask", "bot"],
                language=VoiceLanguageCode.ENGLISH,
                confidence_weight=1.0
            ),
            IntentPattern(
                intent=VoiceIntentType.CONTENT_REQUEST,
                patterns=[
                    r"show me (.+) content",
                    r"find (.+) for me",
                    r"search for (.+)",
                    r"get (?:me )?(.+) recommendations",
                    r"what (.+) do you have"
                ],
                keywords=["show", "find", "search", "content", "recommendations"],
                language=VoiceLanguageCode.ENGLISH,
                confidence_weight=1.0
            ),
            IntentPattern(
                intent=VoiceIntentType.PROFILE_UPDATE,
                patterns=[
                    r"update my profile",
                    r"change my (.+)",
                    r"set my (.+) to (.+)",
                    r"modify my settings",
                    r"edit my (.+)"
                ],
                keywords=["update", "change", "set", "modify", "edit", "profile"],
                language=VoiceLanguageCode.ENGLISH,
                confidence_weight=1.0
            )
        ])
        
        # Hindi patterns
        self._add_patterns("hi", [
            IntentPattern(
                intent=VoiceIntentType.MOOD_TRACKING,
                patterns=[
                    r"मैं आज [\u0900-\u097F]+ हूँ",  # I am ... today
                    r"मेरा मूड [\u0900-\u097F]+ है",  # My mood is ...
                    r"मूड ट्रैक करें",      # Track mood
                    r"आज मैं [\u0900-\u097F]+ महसूस कर रहा हूँ",  # Today I feel ...
                    r"मैं [\u0900-\u097F]+ हूँ",       # I am ...
                    r"मेरा मूड अच्छा है",    # My mood is good
                    r"मैं खुश हूँ",          # I am happy
                    r"मैं.*खुश.*हूँ",        # I am happy (flexible)
                    r"मैं.*अच्छा.*महसूस",    # I feel good (flexible)
                    r".*खुश.*",            # Contains happy
                    r".*अच्छा.*"            # Contains good
                ],
                keywords=["मूड", "महसूस", "भावना", "ट्रैक", "खुश", "अच्छा"],
                language=VoiceLanguageCode.HINDI,
                confidence_weight=1.0
            ),
            IntentPattern(
                intent=VoiceIntentType.JOURNAL_ENTRY,
                patterns=[
                    r"नई डायरी शुरू करें",     # Start new diary
                    r"डायरी में लिखें",        # Write in diary
                    r"आज के बारे में लिखें"    # Write about today
                ],
                keywords=["डायरी", "लिखना", "जर्नल"],
                language=VoiceLanguageCode.HINDI,
                confidence_weight=1.0
            )
        ])
        
        # Spanish patterns
        self._add_patterns("es", [
            IntentPattern(
                intent=VoiceIntentType.MOOD_TRACKING,
                patterns=[
                    r"me siento (\w+)",
                    r"mi estado de ánimo es (\w+)",
                    r"estoy (\w+) hoy"
                ],
                keywords=["ánimo", "sentir", "estado", "emocional"],
                language=VoiceLanguageCode.SPANISH,
                confidence_weight=1.0
            ),
            IntentPattern(
                intent=VoiceIntentType.JOURNAL_ENTRY,
                patterns=[
                    r"empezar nueva entrada de diario",
                    r"escribir (?:en )?mi diario",
                    r"agregar al diario"
                ],
                keywords=["diario", "escribir", "entrada"],
                language=VoiceLanguageCode.SPANISH,
                confidence_weight=1.0
            )
        ])
    
    def _add_patterns(self, language: str, patterns: List[IntentPattern]):
        """Add patterns for a specific language"""
        if language not in self.intent_patterns:
            self.intent_patterns[language] = []
        self.intent_patterns[language].extend(patterns)
    
    def classify_intent(self, text: str, language: str, user_id: Optional[str] = None) -> VoiceCommand:
        """
        Classify voice text into intent with confidence scoring
        
        Args:
            text: Voice command text
            language: Language code
            user_id: Optional user ID for personalization
            
        Returns:
            VoiceCommand with classified intent and parameters
        """
        text_lower = text.lower().strip()
        
        # Get patterns for the language, fallback to English
        patterns = self.intent_patterns.get(language, self.intent_patterns.get("en", []))
        
        best_match = None
        best_confidence = 0.0
        best_parameters = {}
        
        for pattern in patterns:
            confidence, parameters = self._match_pattern(text_lower, pattern)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = pattern.intent
                best_parameters = parameters
        
        # If no good match found, classify as UNKNOWN
        if best_confidence < 0.3 or best_match is None:
            best_match = VoiceIntentType.UNKNOWN
            best_confidence = 0.1
            best_parameters = {"raw_text": text}
        
        # Create voice command
        command = VoiceCommand(
            intent=best_match,
            confidence=best_confidence,
            language=language,
            parameters=best_parameters,
            raw_text=text,
            user_id=user_id
        )
        
        logger.info(f"Classified intent: {best_match.value} with confidence {best_confidence:.2f}")
        
        return command
    
    def _match_pattern(self, text: str, pattern: IntentPattern) -> Tuple[float, Dict[str, Any]]:
        """
        Match text against an intent pattern
        
        Returns:
            Tuple of (confidence_score, extracted_parameters)
        """
        confidence = 0.0
        parameters = {}
        
        # Check regex patterns
        for regex_pattern in pattern.patterns:
            match = re.search(regex_pattern, text, re.IGNORECASE)
            if match:
                confidence += 0.7 * pattern.confidence_weight
                
                # Extract parameters from regex groups
                if match.groups():
                    for i, group in enumerate(match.groups()):
                        if group:
                            parameters[f"param_{i+1}"] = group.strip()
                
                break  # Only one pattern match per intent
        
        # Check keyword matching
        keyword_matches = sum(1 for keyword in pattern.keywords if keyword.lower() in text)
        if keyword_matches > 0:
            keyword_confidence = min(0.3, keyword_matches * 0.1)
            confidence += keyword_confidence
        
        # Extract common parameters based on intent type
        if pattern.intent == VoiceIntentType.MOOD_TRACKING:
            parameters.update(self._extract_mood_parameters(text))
        elif pattern.intent == VoiceIntentType.JOURNAL_ENTRY:
            parameters.update(self._extract_journal_parameters(text))
        
        return confidence, parameters
    
    def _extract_mood_parameters(self, text: str) -> Dict[str, Any]:
        """Extract mood-specific parameters"""
        parameters = {}
        
        # Extract mood value if it's a number
        mood_match = re.search(r'(\d+)(?:\s*out\s*of\s*(\d+))?', text)
        if mood_match:
            mood_value = int(mood_match.group(1))
            max_value = int(mood_match.group(2)) if mood_match.group(2) else 10
            parameters["mood_value"] = mood_value
            parameters["mood_scale"] = max_value
            parameters["mood_normalized"] = mood_value / max_value
        
        # Extract mood descriptors
        mood_words = ["happy", "sad", "angry", "excited", "calm", "anxious", "stressed", "relaxed"]
        for word in mood_words:
            if word in text.lower():
                parameters["mood_descriptor"] = word
                break
        
        return parameters
    
    def _extract_journal_parameters(self, text: str) -> Dict[str, Any]:
        """Extract journal-specific parameters"""
        parameters = {}
        
        # Extract topic if mentioned
        topic_match = re.search(r'about\s+(.+)', text, re.IGNORECASE)
        if topic_match:
            parameters["topic"] = topic_match.group(1).strip()
        
        return parameters
    
    def add_custom_pattern(self, language: str, pattern: IntentPattern):
        """Add a custom intent pattern for specific use cases"""
        if language not in self.intent_patterns:
            self.intent_patterns[language] = []
        
        self.intent_patterns[language].append(pattern)
        logger.info(f"Added custom pattern for {pattern.intent.value} in {language}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.intent_patterns.keys())
    
    def get_patterns_for_language(self, language: str) -> List[IntentPattern]:
        """Get all patterns for a specific language"""
        return self.intent_patterns.get(language, [])
