"""
Intent Classification System
Handles voice intent processing and classification with cultural awareness
"""
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import asyncio

from ..models import IntentType, CulturalContext

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Voice intent classification with cultural context support
    
    Implements intent detection and parameter extraction for voice commands
    with multi-language and cultural awareness
    """
    
    def __init__(self):
        # Intent patterns for different languages and cultural contexts
        self.intent_patterns = self._initialize_intent_patterns()
        self.parameter_extractors = self._initialize_parameter_extractors()
        self.cultural_adaptations = self._initialize_cultural_adaptations()
        
        logger.info("Intent Classifier initialized")
    
    async def classify_intent(
        self, 
        processed_text: str, 
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """
        Classify voice intent with cultural context
        
        Returns:
            Dict containing:
            - intent_type: IntentType
            - confidence: float (0.0-1.0)
            - parameters: Dict[str, Any]
            - cultural_adaptations: Dict[str, Any]
        """
        try:
            # Get language-specific patterns
            language = cultural_context.language
            patterns = self.intent_patterns.get(language, self.intent_patterns["en"])
            
            # Calculate confidence scores for each intent type
            intent_scores = {}
            for intent_type, pattern_list in patterns.items():
                scores = []
                for pattern in pattern_list:
                    score = self._calculate_pattern_match_score(processed_text, pattern)
                    scores.append(score)
                
                # Use best matching pattern
                intent_scores[intent_type] = max(scores) if scores else 0.0
            
            # Get best intent
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent_type_str, confidence = best_intent
            
            # Convert string to IntentType enum
            try:
                intent_type = IntentType(intent_type_str)
            except ValueError:
                intent_type = IntentType.UNKNOWN
                confidence = 0.0
            
            # Extract parameters for the classified intent
            parameters = await self._extract_parameters(
                processed_text, intent_type, cultural_context
            )
            
            # Apply cultural adaptations
            cultural_adaptations = await self._apply_cultural_adaptations(
                intent_type, parameters, cultural_context
            )
            
            result = {
                "intent_type": intent_type,
                "confidence": confidence,
                "parameters": parameters,
                "cultural_adaptations": cultural_adaptations
            }
            
            logger.info(f"Intent classified: {intent_type} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}", exc_info=True)
            return {
                "intent_type": IntentType.UNKNOWN,
                "confidence": 0.0,
                "parameters": {},
                "cultural_adaptations": {}
            }
    
    def _initialize_intent_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize intent patterns for different languages"""
        return {
            "en": {
                IntentType.MOOD_TRACKING.value: [
                    r"(?i)\b(feel|feeling|mood|emotion|emotional)\b",
                    r"(?i)\b(happy|sad|angry|anxious|calm|excited|tired|stressed)\b",
                    r"(?i)\b(track|log|record|note|save).*\b(mood|feeling)\b",
                    r"(?i)\btoday\s+(?:i|i'm|im)\s+(feeling|felt)\b",
                    r"(?i)\bhow.*(?:am|was|feeling|feel)\b"
                ],
                IntentType.JOURNAL_ENTRY.value: [
                    r"(?i)\b(write|journal|diary|entry|note|record)\b",
                    r"(?i)\b(dear\s+diary|today\s+was|what\s+happened)\b",
                    r"(?i)\b(thoughts|reflection|think|remember)\b",
                    r"(?i)\b(happened|experience|story|tell)\b"
                ],
                IntentType.CHAT_CONVERSATION.value: [
                    r"(?i)\b(talk|chat|speak|discuss|conversation)\b",
                    r"(?i)\b(tell\s+me|help|advice|support|listen)\b",
                    r"(?i)\b(question|ask|wondering|curious)\b",
                    r"(?i)\bhello|hi|hey|good\s+(morning|afternoon|evening)\b"
                ],
                IntentType.PROFILE_UPDATE.value: [
                    r"(?i)\b(update|change|modify|edit).*\b(profile|settings|preferences)\b",
                    r"(?i)\b(name|age|location|timezone|language)\b",
                    r"(?i)\bset.*\b(preference|setting|option)\b"
                ],
                IntentType.COMMUNITY_INTERACTION.value: [
                    r"(?i)\b(share|post|forum|community|group)\b",
                    r"(?i)\b(others|people|friends|connect|social)\b",
                    r"(?i)\b(discussion|thread|comment|reply)\b"
                ],
                IntentType.ANALYTICS_QUERY.value: [
                    r"(?i)\b(show|display|view).*\b(stats|analytics|data|trends)\b",
                    r"(?i)\b(how\s+am\s+i|progress|improvement|pattern)\b",
                    r"(?i)\b(summary|overview|report|insights)\b",
                    r"(?i)\b(week|month|year).*\b(data|mood|progress)\b"
                ],
                IntentType.CONTENT_SEARCH.value: [
                    r"(?i)\b(search|find|look|explore).*\b(content|article|resource)\b",
                    r"(?i)\b(help\s+with|about|information)\b",
                    r"(?i)\b(learn|understand|know)\b"
                ],
                IntentType.VOICE_COMMAND.value: [
                    r"(?i)\b(start|stop|pause|resume|cancel)\b",
                    r"(?i)\b(volume|speed|repeat|skip)\b",
                    r"(?i)\b(navigate|go\s+to|open|close)\b"
                ],
                IntentType.CRISIS_INTERVENTION.value: [
                    r"(?i)\b(suicide|kill\s+myself|end\s+it|give\s+up)\b",
                    r"(?i)\b(hurt\s+myself|self\s+harm|cutting)\b",
                    r"(?i)\b(hopeless|worthless|no\s+point|can't\s+go\s+on)\b",
                    r"(?i)\b(crisis|emergency|help\s+me|desperate)\b"
                ]
            },
            "hi": {  # Hindi patterns
                IntentType.MOOD_TRACKING.value: [
                    r"(?i)\b(महसूस|भावना|मूड|भावनात्मक)\b",
                    r"(?i)\b(खुश|उदास|गुस्सा|चिंतित|शांत|उत्साहित|थका|तनावग्रस्त)\b",
                    r"(?i)\b(ट्रैक|लॉग|रिकॉर्ड|नोट|सेव).*\b(मूड|भावना)\b"
                ],
                IntentType.JOURNAL_ENTRY.value: [
                    r"(?i)\b(लिखना|जर्नल|डायरी|एंट्री|नोट|रिकॉर्ड)\b",
                    r"(?i)\b(प्रिय डायरी|आज था|क्या हुआ)\b"
                ],
                IntentType.CHAT_CONVERSATION.value: [
                    r"(?i)\b(बात|चैट|बोलना|चर्चा|बातचीत)\b",
                    r"(?i)\b(मुझे बताओ|मदद|सलाह|समर्थन|सुनो)\b",
                    r"(?i)\bनमस्ते|हाय|नमस्कार|शुभ\s+(सुबह|दोपहर|शाम)\b"
                ]
                # Add more Hindi patterns as needed
            }
            # Add more languages as needed
        }
    
    def _initialize_parameter_extractors(self) -> Dict[str, List[str]]:
        """Initialize parameter extraction patterns"""
        return {
            # Mood-related parameters
            "mood_value": [
                r"(?i)\b(1|2|3|4|5|6|7|8|9|10)\b",
                r"(?i)\b(one|two|three|four|five|six|seven|eight|nine|ten)\b",
                r"(?i)\b(very\s+)?(good|bad|okay|fine|terrible|amazing|awful)\b"
            ],
            "emotion_type": [
                r"(?i)\b(happy|happiness|joy|joyful)\b",
                r"(?i)\b(sad|sadness|depressed|depression)\b",
                r"(?i)\b(angry|anger|frustrated|frustration)\b",
                r"(?i)\b(anxious|anxiety|worried|worry|nervous)\b",
                r"(?i)\b(calm|peaceful|relaxed|serene)\b",
                r"(?i)\b(excited|excitement|enthusiastic)\b",
                r"(?i)\b(tired|exhausted|fatigue)\b",
                r"(?i)\b(stressed|stress|overwhelmed)\b"
            ],
            "time_reference": [
                r"(?i)\b(today|yesterday|tomorrow)\b",
                r"(?i)\b(this\s+(morning|afternoon|evening|night|week|month))\b",
                r"(?i)\b(last\s+(hour|day|week|month))\b",
                r"(?i)\b(now|currently|right\s+now|at\s+the\s+moment)\b"
            ],
            "intensity": [
                r"(?i)\b(very|extremely|really|quite|somewhat|a\s+little|slightly)\b",
                r"(?i)\b(intense|mild|moderate|severe|overwhelming)\b"
            ]
        }
    
    def _initialize_cultural_adaptations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cultural adaptations for different contexts"""
        return {
            "en": {
                "communication_style": "direct",
                "formality_level": "casual",
                "response_patterns": ["I understand", "Let me help", "That makes sense"]
            },
            "hi": {
                "communication_style": "respectful",
                "formality_level": "formal",
                "response_patterns": ["मैं समझता हूँ", "मैं आपकी मदद करूंगा", "यह समझ में आता है"]
            }
        }
    
    def _calculate_pattern_match_score(self, text: str, pattern: str) -> float:
        """Calculate confidence score for pattern match"""
        try:
            import re
            matches = re.finditer(pattern, text)
            match_count = len(list(matches))
            
            if match_count == 0:
                return 0.0
            
            # Base score from match count
            base_score = min(match_count * 0.3, 0.9)
            
            # Bonus for exact matches
            exact_matches = re.findall(pattern, text)
            if exact_matches:
                base_score += 0.1
            
            # Normalize to text length
            text_length = len(text.split())
            if text_length > 0:
                # Longer texts need more matches for same confidence
                length_factor = min(text_length / 10, 1.0)
                base_score *= (2 - length_factor)
            
            return min(base_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Pattern matching error: {str(e)}")
            return 0.0
    
    async def _extract_parameters(
        self, 
        text: str, 
        intent_type: IntentType,
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """Extract parameters specific to the intent type"""
        parameters = {}
        
        try:
            if intent_type == IntentType.MOOD_TRACKING:
                # Extract mood-related parameters
                parameters.update(await self._extract_mood_parameters(text))
            
            elif intent_type == IntentType.JOURNAL_ENTRY:
                # Extract journal-related parameters
                parameters.update(await self._extract_journal_parameters(text))
            
            elif intent_type == IntentType.ANALYTICS_QUERY:
                # Extract analytics query parameters
                parameters.update(await self._extract_analytics_parameters(text))
            
            # Extract common parameters for all intents
            parameters.update(await self._extract_common_parameters(text))
            
            # Apply cultural context to parameters
            parameters["cultural_context"] = {
                "language": cultural_context.language,
                "formality_level": cultural_context.formality_level,
                "communication_style": cultural_context.communication_style
            }
            
        except Exception as e:
            logger.warning(f"Parameter extraction error: {str(e)}")
        
        return parameters
    
    async def _extract_mood_parameters(self, text: str) -> Dict[str, Any]:
        """Extract mood-specific parameters"""
        params = {}
        
        # Extract mood value (1-10 scale)
        mood_patterns = self.parameter_extractors["mood_value"]
        for pattern in mood_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Convert to numeric if possible
                try:
                    if matches[0].isdigit():
                        params["mood_value"] = int(matches[0])
                    else:
                        # Convert word to number
                        word_to_num = {
                            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
                            "terrible": 1, "awful": 2, "bad": 3, "okay": 5,
                            "fine": 6, "good": 7, "very good": 8, "great": 9, "amazing": 10
                        }
                        params["mood_value"] = word_to_num.get(matches[0].lower(), 5)
                except ValueError:
                    params["mood_value"] = 5  # Default neutral
                break
        
        # Extract emotion type
        emotion_patterns = self.parameter_extractors["emotion_type"]
        for pattern in emotion_patterns:
            matches = re.findall(pattern, text)
            if matches:
                params["emotion_type"] = matches[0].lower()
                break
        
        # Extract intensity
        intensity_patterns = self.parameter_extractors["intensity"]
        for pattern in intensity_patterns:
            matches = re.findall(pattern, text)
            if matches:
                params["intensity"] = matches[0].lower()
                break
        
        return params
    
    async def _extract_journal_parameters(self, text: str) -> Dict[str, Any]:
        """Extract journal-specific parameters"""
        params = {}
        
        # Extract the main content (everything after journal keywords)
        journal_keywords = ["write", "journal", "diary", "dear diary"]
        for keyword in journal_keywords:
            if keyword in text.lower():
                # Get text after the keyword
                parts = text.lower().split(keyword, 1)
                if len(parts) > 1:
                    params["content"] = parts[1].strip()
                    break
        
        # If no specific content found, use the whole text
        if "content" not in params:
            params["content"] = text
        
        # Extract privacy level
        if any(word in text.lower() for word in ["private", "personal", "secret"]):
            params["privacy_level"] = "private"
        elif any(word in text.lower() for word in ["public", "share", "open"]):
            params["privacy_level"] = "public"
        else:
            params["privacy_level"] = "private"  # Default
        
        return params
    
    async def _extract_analytics_parameters(self, text: str) -> Dict[str, Any]:
        """Extract analytics query parameters"""
        params = {}
        
        # Extract time range
        time_patterns = self.parameter_extractors["time_reference"]
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            if matches:
                params["time_range"] = matches[0].lower()
                break
        
        # Extract metric type
        if any(word in text.lower() for word in ["mood", "feeling", "emotion"]):
            params["metric_type"] = "mood"
        elif any(word in text.lower() for word in ["journal", "entry", "writing"]):
            params["metric_type"] = "journal"
        elif any(word in text.lower() for word in ["activity", "engagement"]):
            params["metric_type"] = "activity"
        else:
            params["metric_type"] = "overall"
        
        return params
    
    async def _extract_common_parameters(self, text: str) -> Dict[str, Any]:
        """Extract common parameters for all intents"""
        params = {}
        
        # Extract time reference
        time_patterns = self.parameter_extractors["time_reference"]
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            if matches:
                params["time_reference"] = matches[0].lower()
                break
        
        # Extract urgency level
        if any(word in text.lower() for word in ["urgent", "emergency", "now", "immediately"]):
            params["urgency"] = "high"
        elif any(word in text.lower() for word in ["later", "whenever", "no rush"]):
            params["urgency"] = "low"
        else:
            params["urgency"] = "normal"
        
        return params
    
    async def _apply_cultural_adaptations(
        self,
        intent_type: IntentType,
        parameters: Dict[str, Any],
        cultural_context: CulturalContext
    ) -> Dict[str, Any]:
        """Apply cultural adaptations to the intent processing"""
        adaptations = {}
        
        language = cultural_context.language
        cultural_settings = self.cultural_adaptations.get(language, self.cultural_adaptations["en"])
        
        # Communication style adaptations
        adaptations["communication_style"] = cultural_settings["communication_style"]
        adaptations["formality_level"] = cultural_settings["formality_level"]
        
        # Language-specific adaptations
        if language == "hi":
            # Hindi cultural adaptations
            adaptations["respectful_address"] = True
            adaptations["family_context"] = True
            adaptations["formal_responses"] = True
        elif language == "en":
            # English cultural adaptations
            adaptations["direct_communication"] = True
            adaptations["individual_focus"] = True
        
        # Intent-specific cultural adaptations
        if intent_type == IntentType.MOOD_TRACKING:
            if cultural_context.cultural_region in ["south_asia", "india"]:
                adaptations["family_wellness_focus"] = True
                adaptations["holistic_approach"] = True
        
        return adaptations
    
    @property
    def supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return list(self.intent_patterns.keys())
    
    def _match_intent_patterns(self, text: str) -> str:
        """Match text against intent patterns and return best match"""
        try:
            # Use English patterns for basic matching
            patterns = self.intent_patterns.get("en", {})
            best_match = "unknown"
            highest_score = 0.0
            
            for intent_type, pattern_list in patterns.items():
                for pattern in pattern_list:
                    if re.search(pattern, text):
                        score = self._calculate_pattern_match_score(text, pattern)
                        if score > highest_score:
                            highest_score = score
                            best_match = intent_type
            
            return best_match
        except Exception as e:
            logger.error(f"Pattern matching failed: {str(e)}")
            return "unknown"
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text"""
        entities = {}
        
        try:
            # Extract numbers (for mood values, durations, etc.)
            numbers = re.findall(r'\b\d+\b', text)
            if numbers:
                entities["numbers"] = [int(n) for n in numbers]
            
            # Extract time references
            time_patterns = [
                r'\b(morning|afternoon|evening|night)\b',
                r'\b(today|yesterday|tomorrow)\b',
                r'\b(minutes?|hours?|days?)\b'
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    entities["time_references"] = matches
            
            # Extract emotions
            emotion_words = [
                "happy", "sad", "angry", "anxious", "calm", "excited", 
                "tired", "stressed", "peaceful", "frustrated", "worried"
            ]
            found_emotions = [word for word in emotion_words if word in text.lower()]
            if found_emotions:
                entities["emotions"] = found_emotions
            
            # Extract activity references
            activity_patterns = [
                r'\b(meditation|exercise|work|sleep|eat)\w*\b',
                r'\b(running|walking|yoga|reading)\b'
            ]
            
            activities = []
            for pattern in activity_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                activities.extend(matches)
            
            if activities:
                entities["activities"] = activities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
        
        return entities
    
    def _calculate_confidence(self, text: str, intent_type: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence score for intent classification"""
        try:
            base_confidence = 0.5
            
            # Get patterns for the intent type
            patterns = self.intent_patterns.get("en", {}).get(intent_type, [])
            
            # Calculate pattern match score
            pattern_scores = []
            for pattern in patterns:
                score = self._calculate_pattern_match_score(text, pattern)
                pattern_scores.append(score)
            
            if pattern_scores:
                pattern_confidence = max(pattern_scores)
            else:
                pattern_confidence = 0.0
            
            # Boost confidence based on entities
            entity_boost = 0.0
            if entities:
                entity_boost = min(0.3, len(entities) * 0.1)
            
            # Text length factor (longer, more specific text = higher confidence)
            length_factor = min(0.2, len(text.split()) * 0.02)
            
            final_confidence = min(1.0, pattern_confidence + entity_boost + length_factor)
            
            return final_confidence
            
        except Exception as e:
            logger.error(f"Confidence calculation failed: {str(e)}")
            return 0.0
