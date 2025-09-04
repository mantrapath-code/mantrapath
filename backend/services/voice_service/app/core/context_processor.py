"""
Context Processor
Handles context analysis, cultural adaptation, and response enhancement
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class CulturalContext:
    """Cultural context information"""
    culture: str
    language: str
    region: str
    formality_level: str  # formal, informal, casual
    communication_style: str  # direct, indirect, contextual
    values: List[str]
    taboos: List[str]

@dataclass
class ProcessedContext:
    """Processed context result"""
    original_text: str
    processed_text: str
    cultural_adaptations: List[str]
    sentiment_enhanced: bool
    language_detected: str
    confidence: float
    suggestions: List[str]

class ContextProcessor:
    """Processes context for cultural adaptation and enhancement"""
    
    def __init__(self):
        self.cultural_contexts = self._load_cultural_contexts()
        self.language_patterns = self._load_language_patterns()
        self.emotion_keywords = self._load_emotion_keywords()
    
    def _load_cultural_contexts(self) -> Dict[str, CulturalContext]:
        """Load cultural context configurations"""
        return {
            "indian": CulturalContext(
                culture="indian",
                language="hi",
                region="south_asia",
                formality_level="respectful",
                communication_style="contextual",
                values=["respect", "family", "tradition", "spirituality"],
                taboos=["direct_criticism", "personal_space"]
            ),
            "western": CulturalContext(
                culture="western",
                language="en", 
                region="north_america_europe",
                formality_level="casual",
                communication_style="direct",
                values=["individualism", "efficiency", "innovation"],
                taboos=["personal_questions", "religious_topics"]
            ),
            "neutral": CulturalContext(
                culture="neutral",
                language="en",
                region="global",
                formality_level="formal",
                communication_style="balanced",
                values=["respect", "clarity", "helpfulness"],
                taboos=[]
            )
        }
    
    def _load_language_patterns(self) -> Dict[str, List[str]]:
        """Load language-specific patterns"""
        return {
            "hindi": [
                r"\b(आप|तुम|हम|मैं)\b",
                r"\b(नमस्ते|धन्यवाद|क्षमा)\b",
                r"\b(जी|हां|नहीं)\b"
            ],
            "english": [
                r"\b(you|I|we|they)\b",
                r"\b(hello|thank|please|sorry)\b", 
                r"\b(yes|no|maybe)\b"
            ],
            "mixed": [
                r"\b(yaar|bhai|dude)\b",
                r"\b(sorry|please)\s+\w+\b",
                r"\bhindi\s+english\b"
            ]
        }
    
    def _load_emotion_keywords(self) -> Dict[str, List[str]]:
        """Load emotion keywords for different languages"""
        return {
            "positive_en": ["happy", "joy", "excited", "wonderful", "amazing", "great"],
            "negative_en": ["sad", "angry", "frustrated", "upset", "terrible", "awful"],
            "positive_hi": ["खुश", "प्रसन्न", "उत्साहित", "बहुत अच्छा", "शानदार"],
            "negative_hi": ["दुखी", "गुस्सा", "परेशान", "चिंतित", "बुरा"]
        }
    
    def detect_language_mix(self, text: str) -> Dict[str, Any]:
        """Detect language mixing in text"""
        hindi_score = 0
        english_score = 0
        mixed_score = 0
        
        # Check for Hindi patterns
        for pattern in self.language_patterns["hindi"]:
            hindi_score += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Check for English patterns  
        for pattern in self.language_patterns["english"]:
            english_score += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Check for mixed patterns
        for pattern in self.language_patterns["mixed"]:
            mixed_score += len(re.findall(pattern, text, re.IGNORECASE))
        
        total_score = hindi_score + english_score + mixed_score
        
        if total_score == 0:
            return {"primary": "unknown", "confidence": 0.0, "mixed": False}
        
        primary_language = "hindi" if hindi_score > english_score else "english"
        confidence = max(hindi_score, english_score) / total_score
        is_mixed = mixed_score > 0 or (hindi_score > 0 and english_score > 0)
        
        return {
            "primary": primary_language,
            "confidence": confidence,
            "mixed": is_mixed,
            "scores": {
                "hindi": hindi_score / total_score,
                "english": english_score / total_score,
                "mixed": mixed_score / total_score
            }
        }
    
    def detect_cultural_context(self, text: str, user_profile: Optional[Dict[str, Any]] = None) -> str:
        """Detect cultural context from text and user profile"""
        # Default to neutral
        detected_culture = "neutral"
        
        # Check user profile first
        if user_profile:
            if user_profile.get("region") in ["india", "south_asia"]:
                detected_culture = "indian"
            elif user_profile.get("region") in ["usa", "europe", "north_america"]:
                detected_culture = "western"
        
        # Check text patterns for cultural indicators
        indian_indicators = [
            r"\b(namaste|namaskar|प्रणाम)\b",
            r"\b(ji|haan|acha|theek)\b",
            r"\b(bhai|didi|uncle|aunty)\b",
            r"\b(dharma|karma|ashram)\b"
        ]
        
        western_indicators = [
            r"\b(hey|hi|hello)\b",
            r"\b(dude|buddy|mate)\b",
            r"\b(awesome|cool|amazing)\b"
        ]
        
        indian_matches = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in indian_indicators)
        western_matches = sum(len(re.findall(pattern, text, re.IGNORECASE)) for pattern in western_indicators)
        
        if indian_matches > western_matches:
            detected_culture = "indian"
        elif western_matches > indian_matches:
            detected_culture = "western"
        
        return detected_culture
    
    def enhance_sentiment_awareness(self, text: str, sentiment: str, confidence: float) -> Dict[str, Any]:
        """Enhance response based on sentiment awareness"""
        enhancements = []
        
        if sentiment == "negative" and confidence > 0.7:
            enhancements.append("empathy_boost")
            enhancements.append("supportive_tone")
        elif sentiment == "positive" and confidence > 0.7:
            enhancements.append("enthusiasm_match")
            enhancements.append("positive_reinforcement")
        elif confidence < 0.5:
            enhancements.append("neutral_safe_response")
        
        # Check for emotional keywords
        emotion_detected = []
        for emotion_type, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    emotion_detected.append(emotion_type)
        
        return {
            "enhancements": enhancements,
            "emotions_detected": emotion_detected,
            "response_strategy": self._get_response_strategy(sentiment, confidence)
        }
    
    def _get_response_strategy(self, sentiment: str, confidence: float) -> str:
        """Get response strategy based on sentiment"""
        if sentiment == "negative" and confidence > 0.8:
            return "crisis_support"
        elif sentiment == "negative" and confidence > 0.6:
            return "empathetic_support"
        elif sentiment == "positive" and confidence > 0.7:
            return "enthusiasm_matching"
        else:
            return "neutral_helpful"
    
    def adapt_response_culturally(self, response: str, culture: str, language: str) -> str:
        """Adapt response for cultural context"""
        if culture not in self.cultural_contexts:
            return response
        
        cultural_context = self.cultural_contexts[culture]
        adapted_response = response
        
        # Apply cultural adaptations
        if culture == "indian":
            # Add respectful language
            if language == "hi":
                adapted_response = self._add_hindi_respect_markers(adapted_response)
            else:
                adapted_response = self._add_english_respect_markers(adapted_response)
        
        elif culture == "western":
            # Make more casual and direct
            adapted_response = self._make_casual_tone(adapted_response)
        
        return adapted_response
    
    def _add_hindi_respect_markers(self, text: str) -> str:
        """Add Hindi respect markers"""
        # Simple respect enhancement for Hindi
        if not text.strip().endswith(('।', '.')):
            text += "।"
        
        respectful_additions = [
            ("आप", "आप"),  # Keep formal 'you'
            ("है", "है जी"),  # Add respect marker
            ("हूं", "हूं जी")   # Add respect marker
        ]
        
        for old, new in respectful_additions:
            text = text.replace(old, new)
        
        return text
    
    def _add_english_respect_markers(self, text: str) -> str:
        """Add English respect markers"""
        # Add polite language
        if not text.startswith(("Please", "I would", "May I")):
            if text.startswith(("Can you", "Do you")):
                text = "May I ask: " + text
        
        return text
    
    def _make_casual_tone(self, text: str) -> str:
        """Make response more casual"""
        casual_replacements = [
            ("I would like to", "I'd"),
            ("cannot", "can't"),
            ("will not", "won't"),
            ("do not", "don't")
        ]
        
        for formal, casual in casual_replacements:
            text = text.replace(formal, casual)
        
        return text
    
    def process_context(self, text: str, session_context: Dict[str, Any],
                       sentiment: str, confidence: float,
                       user_profile: Optional[Dict[str, Any]] = None) -> ProcessedContext:
        """Process complete context for enhanced response"""
        # Detect language and cultural context
        language_info = self.detect_language_mix(text)
        detected_culture = self.detect_cultural_context(text, user_profile)
        
        # Enhance sentiment awareness
        sentiment_enhancement = self.enhance_sentiment_awareness(text, sentiment, confidence)
        
        # Adapt culturally
        primary_language = language_info["primary"]
        adapted_text = self.adapt_response_culturally(text, detected_culture, primary_language)
        
        # Generate adaptations list
        adaptations = []
        if detected_culture != "neutral":
            adaptations.append(f"cultural_adaptation_{detected_culture}")
        if language_info["mixed"]:
            adaptations.append("multilingual_support")
        if sentiment_enhancement["enhancements"]:
            adaptations.extend(sentiment_enhancement["enhancements"])
        
        # Generate suggestions
        suggestions = self._generate_suggestions(text, language_info, detected_culture, sentiment)
        
        return ProcessedContext(
            original_text=text,
            processed_text=adapted_text,
            cultural_adaptations=adaptations,
            sentiment_enhanced=bool(sentiment_enhancement["enhancements"]),
            language_detected=primary_language,
            confidence=language_info["confidence"],
            suggestions=suggestions
        )
    
    def _generate_suggestions(self, text: str, language_info: Dict[str, Any],
                            culture: str, sentiment: str) -> List[str]:
        """Generate contextual suggestions"""
        suggestions = []
        
        if language_info["mixed"]:
            suggestions.append("Consider language preference settings")
        
        if sentiment == "negative":
            suggestions.append("Offer emotional support resources")
        
        if culture == "indian" and language_info["primary"] == "english":
            suggestions.append("Offer Hindi language option")
        
        return suggestions
    
    def get_context_summary(self, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of processed context"""
        return {
            "active_cultures": list(self.cultural_contexts.keys()),
            "supported_languages": list(self.language_patterns.keys()),
            "emotion_detection": bool(self.emotion_keywords),
            "processing_features": [
                "cultural_adaptation",
                "sentiment_enhancement", 
                "language_detection",
                "code_switching_support"
            ]
        }
