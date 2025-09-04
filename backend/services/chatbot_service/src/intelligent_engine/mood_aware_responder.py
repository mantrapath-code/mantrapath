"""
Mood-Aware Responder Module

This module provides intelligent, mood-aware response generation for the MantraPath chatbot.
It integrates with the mood service to understand user's current emotional state and generates
contextually appropriate responses based on mood patterns and emotional context.

Key Features:
    - Real-time mood state analysis
    - Contextual response adaptation
    - Emotional intelligence in conversations
    - Integration with mood service data
    
Author: MantraPath Development Team
Version: 1.0.0
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class MoodState(Enum):
    """Enumeration of different mood states for response tailoring"""
    VERY_LOW = "very_low"      # Severe depression, crisis risk
    LOW = "low"                # Mild depression, sadness
    NEUTRAL = "neutral"        # Balanced emotional state
    GOOD = "good"              # Positive mood, content
    EXCELLENT = "excellent"    # Very positive, energetic

class EmotionalContext(Enum):
    """Enumeration of emotional contexts for response adaptation"""
    CRISIS = "crisis"          # Emergency situation requiring immediate attention
    DISTRESS = "distress"      # High emotional distress
    SEEKING_SUPPORT = "seeking_support"  # User actively seeking help
    MAINTENANCE = "maintenance"  # Regular check-in, maintaining wellness
    CELEBRATION = "celebration"  # Sharing positive experiences

@dataclass
class MoodContext:
    """
    Data class representing comprehensive mood context for response generation
    
    Attributes:
        current_mood_score (float): Current mood rating (1-10 scale)
        mood_trend (str): Recent mood trend (improving/declining/stable)
        stress_level (int): Current stress level (1-10 scale)
        energy_level (int): Current energy level (1-10 scale)
        emotional_context (EmotionalContext): Current emotional context
        risk_factors (List[str]): Identified risk factors
        protective_factors (List[str]): Identified protective factors
        last_mood_entry (datetime): Timestamp of last mood entry
        mood_pattern_insights (Dict): ML-generated mood pattern insights
    """
    current_mood_score: float
    mood_trend: str
    stress_level: int
    energy_level: int
    emotional_context: EmotionalContext
    risk_factors: List[str]
    protective_factors: List[str]
    last_mood_entry: datetime
    mood_pattern_insights: Dict[str, Any]

@dataclass
class MoodAwareResponse:
    """
    Data class representing a mood-aware response with contextual information
    
    Attributes:
        response_text (str): The main response text
        tone (str): Response tone (supportive, encouraging, etc.)
        intervention_type (str): Type of intervention suggested
        breathing_exercise (Optional[Dict]): Breathing exercise if applicable
        follow_up_suggestions (List[str]): Suggested follow-up actions
        crisis_detected (bool): Whether crisis situation was detected
        confidence_score (float): Confidence in response appropriateness (0-1)
    """
    response_text: str
    tone: str
    intervention_type: str
    breathing_exercise: Optional[Dict[str, Any]] = None
    follow_up_suggestions: List[str] = None
    crisis_detected: bool = False
    confidence_score: float = 0.0

class MoodAwareResponder:
    """
    Core mood-aware response generation engine
    
    This class analyzes user mood context and generates intelligent, contextually
    appropriate responses that adapt to the user's current emotional state.
    """
    
    def __init__(self):
        """Initialize the mood-aware responder with response templates and configurations"""
        self.response_templates = self._load_response_templates()
        self.crisis_keywords = self._load_crisis_keywords()
        self.therapeutic_responses = self._load_therapeutic_responses()
        
        # Configuration settings
        self.crisis_threshold = 3.0  # Mood score threshold for crisis detection
        self.distress_threshold = 5.0  # Mood score threshold for distress detection
        
        logger.info("MoodAwareResponder initialized successfully")

    async def generate_mood_aware_response(
        self, 
        user_message: str, 
        mood_context: MoodContext,
        conversation_history: List[Dict[str, Any]] = None
    ) -> MoodAwareResponse:
        """
        Generate a mood-aware response based on user message and mood context
        
        Args:
            user_message (str): The user's message
            mood_context (MoodContext): Current mood context
            conversation_history (List[Dict]): Previous conversation messages
            
        Returns:
            MoodAwareResponse: Intelligent response tailored to mood context
        """
        try:
            # Step 1: Analyze crisis risk
            crisis_detected = await self._detect_crisis_situation(user_message, mood_context)
            
            if crisis_detected:
                return await self._generate_crisis_response(user_message, mood_context)
            
            # Step 2: Determine emotional context
            emotional_context = await self._analyze_emotional_context(user_message, mood_context)
            
            # Step 3: Select appropriate response strategy
            response_strategy = await self._select_response_strategy(
                emotional_context, mood_context
            )
            
            # Step 4: Generate contextual response
            response = await self._generate_contextual_response(
                user_message, mood_context, response_strategy, conversation_history
            )
            
            # Step 5: Add therapeutic interventions if needed
            response = await self._add_therapeutic_interventions(response, mood_context)
            
            logger.info(f"Generated mood-aware response with strategy: {response_strategy}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating mood-aware response: {str(e)}")
            return await self._generate_fallback_response(user_message)

    async def _detect_crisis_situation(
        self, 
        user_message: str, 
        mood_context: MoodContext
    ) -> bool:
        """
        Detect potential crisis situations requiring immediate intervention
        
        Args:
            user_message (str): User's message
            mood_context (MoodContext): Current mood context
            
        Returns:
            bool: True if crisis situation detected
        """
        # Check mood score threshold
        if mood_context.current_mood_score <= self.crisis_threshold:
            return True
        
        # Check for crisis keywords in message
        message_lower = user_message.lower()
        crisis_indicators = [
            "kill myself", "end it all", "not worth living", "suicide",
            "hurt myself", "can't go on", "give up", "hopeless"
        ]
        
        for indicator in crisis_indicators:
            if indicator in message_lower:
                logger.warning(f"Crisis keyword detected: {indicator}")
                return True
        
        # Check risk factors
        high_risk_factors = ["isolation", "substance_abuse", "recent_loss"]
        if any(factor in mood_context.risk_factors for factor in high_risk_factors):
            return True
        
        return False

    async def _generate_crisis_response(
        self, 
        user_message: str, 
        mood_context: MoodContext
    ) -> MoodAwareResponse:
        """
        Generate appropriate crisis intervention response
        
        Args:
            user_message (str): User's message
            mood_context (MoodContext): Current mood context
            
        Returns:
            MoodAwareResponse: Crisis intervention response
        """
        crisis_response_text = """I'm deeply concerned about what you're sharing with me. Your feelings are important, and I want you to know that you're not alone. 

🆘 **If you're having thoughts of self-harm, please reach out for immediate help:**
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911

I care about your safety and wellbeing. Would you like me to help you connect with professional support right now? You deserve care and support through this difficult time."""

        return MoodAwareResponse(
            response_text=crisis_response_text,
            tone="compassionate_urgent",
            intervention_type="crisis_intervention",
            crisis_detected=True,
            confidence_score=0.95,
            follow_up_suggestions=[
                "Contact crisis helpline immediately",
                "Reach out to trusted friend or family member",
                "Contact healthcare provider",
                "Go to nearest emergency room if in immediate danger"
            ]
        )

    async def _analyze_emotional_context(
        self, 
        user_message: str, 
        mood_context: MoodContext
    ) -> EmotionalContext:
        """
        Analyze the emotional context of the user's message and mood state
        
        Args:
            user_message (str): User's message
            mood_context (MoodContext): Current mood context
            
        Returns:
            EmotionalContext: Identified emotional context
        """
        message_lower = user_message.lower()
        
        # Check for distress indicators
        distress_keywords = [
            "anxious", "panic", "overwhelmed", "stressed", "worried",
            "scared", "afraid", "nervous", "tense"
        ]
        
        if any(keyword in message_lower for keyword in distress_keywords):
            return EmotionalContext.DISTRESS
        
        # Check for support-seeking behavior
        support_keywords = [
            "help", "advice", "don't know what to do", "struggling",
            "need support", "talk to someone", "guidance"
        ]
        
        if any(keyword in message_lower for keyword in support_keywords):
            return EmotionalContext.SEEKING_SUPPORT
        
        # Check for positive sharing
        positive_keywords = [
            "better", "good", "happy", "excited", "accomplished",
            "proud", "grateful", "thankful", "celebrate"
        ]
        
        if any(keyword in message_lower for keyword in positive_keywords):
            return EmotionalContext.CELEBRATION
        
        # Default based on mood score
        if mood_context.current_mood_score <= self.distress_threshold:
            return EmotionalContext.DISTRESS
        
        return EmotionalContext.MAINTENANCE

    async def _select_response_strategy(
        self, 
        emotional_context: EmotionalContext, 
        mood_context: MoodContext
    ) -> str:
        """
        Select appropriate response strategy based on emotional context and mood
        
        Args:
            emotional_context (EmotionalContext): Current emotional context
            mood_context (MoodContext): Current mood context
            
        Returns:
            str: Selected response strategy
        """
        if emotional_context == EmotionalContext.CRISIS:
            return "crisis_intervention"
        elif emotional_context == EmotionalContext.DISTRESS:
            return "supportive_intervention"
        elif emotional_context == EmotionalContext.SEEKING_SUPPORT:
            return "guidance_focused"
        elif emotional_context == EmotionalContext.CELEBRATION:
            return "positive_reinforcement"
        else:
            return "maintenance_support"

    async def _generate_contextual_response(
        self, 
        user_message: str, 
        mood_context: MoodContext, 
        strategy: str,
        conversation_history: List[Dict[str, Any]] = None
    ) -> MoodAwareResponse:
        """
        Generate contextually appropriate response based on strategy and mood context
        
        Args:
            user_message (str): User's message
            mood_context (MoodContext): Current mood context
            strategy (str): Selected response strategy
            conversation_history (List[Dict]): Previous conversation messages
            
        Returns:
            MoodAwareResponse: Generated response
        """
        response_templates = self.response_templates.get(strategy, {})
        
        # Select appropriate template based on mood score
        if mood_context.current_mood_score <= 3:
            template_key = "very_low_mood"
        elif mood_context.current_mood_score <= 5:
            template_key = "low_mood"
        elif mood_context.current_mood_score <= 7:
            template_key = "neutral_mood"
        else:
            template_key = "good_mood"
        
        template = response_templates.get(template_key, response_templates.get("default", ""))
        
        # Personalize response based on context
        personalized_response = await self._personalize_response(
            template, user_message, mood_context
        )
        
        return MoodAwareResponse(
            response_text=personalized_response,
            tone=self._determine_response_tone(mood_context),
            intervention_type=strategy,
            confidence_score=0.85
        )

    async def _add_therapeutic_interventions(
        self, 
        response: MoodAwareResponse, 
        mood_context: MoodContext
    ) -> MoodAwareResponse:
        """
        Add appropriate therapeutic interventions based on mood context
        
        Args:
            response (MoodAwareResponse): Base response
            mood_context (MoodContext): Current mood context
            
        Returns:
            MoodAwareResponse: Enhanced response with therapeutic interventions
        """
        # Add breathing exercise for high stress
        if mood_context.stress_level >= 7:
            response.breathing_exercise = {
                "name": "4-7-8 Calming Breath",
                "description": "A powerful technique to reduce anxiety and stress",
                "steps": [
                    {"action": "inhale", "duration": 4, "instruction": "Breathe in slowly through your nose"},
                    {"action": "hold", "duration": 7, "instruction": "Hold your breath gently"},
                    {"action": "exhale", "duration": 8, "instruction": "Exhale completely through your mouth"}
                ],
                "cycles": 4
            }
        
        # Add follow-up suggestions based on mood
        suggestions = []
        
        if mood_context.current_mood_score <= 5:
            suggestions.extend([
                "Consider taking a short walk outside",
                "Try journaling your thoughts and feelings",
                "Reach out to a supportive friend or family member"
            ])
        
        if mood_context.energy_level <= 4:
            suggestions.extend([
                "Engage in gentle movement or stretching",
                "Listen to uplifting music",
                "Practice a mindfulness exercise"
            ])
        
        response.follow_up_suggestions = suggestions
        
        return response

    def _determine_response_tone(self, mood_context: MoodContext) -> str:
        """
        Determine appropriate response tone based on mood context
        
        Args:
            mood_context (MoodContext): Current mood context
            
        Returns:
            str: Appropriate response tone
        """
        if mood_context.current_mood_score <= 3:
            return "gentle_supportive"
        elif mood_context.current_mood_score <= 5:
            return "encouraging_supportive"
        elif mood_context.current_mood_score <= 7:
            return "balanced_friendly"
        else:
            return "enthusiastic_positive"

    async def _personalize_response(
        self, 
        template: str, 
        user_message: str, 
        mood_context: MoodContext
    ) -> str:
        """
        Personalize response template based on user context
        
        Args:
            template (str): Response template
            user_message (str): User's message
            mood_context (MoodContext): Current mood context
            
        Returns:
            str: Personalized response text
        """
        # Replace placeholders with contextual information
        personalized = template.replace(
            "{mood_acknowledgment}", 
            await self._get_mood_acknowledgment(mood_context)
        )
        
        personalized = personalized.replace(
            "{trend_comment}",
            await self._get_trend_comment(mood_context)
        )
        
        return personalized

    async def _get_mood_acknowledgment(self, mood_context: MoodContext) -> str:
        """Get appropriate mood acknowledgment phrase"""
        if mood_context.current_mood_score <= 3:
            return "I can sense you're going through a really difficult time right now"
        elif mood_context.current_mood_score <= 5:
            return "I notice you're having some challenges today"
        elif mood_context.current_mood_score <= 7:
            return "It sounds like you're managing things reasonably well"
        else:
            return "I'm glad to hear you're doing well"

    async def _get_trend_comment(self, mood_context: MoodContext) -> str:
        """Get appropriate trend comment based on mood pattern"""
        if mood_context.mood_trend == "improving":
            return "I'm encouraged to see your mood has been improving recently."
        elif mood_context.mood_trend == "declining":
            return "I've noticed your mood has been challenging lately, and I want you to know that's okay."
        else:
            return "Your mood seems to be staying relatively stable."

    async def _generate_fallback_response(self, user_message: str) -> MoodAwareResponse:
        """Generate fallback response when errors occur"""
        return MoodAwareResponse(
            response_text="I'm here to listen and support you. Could you tell me a bit more about how you're feeling right now?",
            tone="supportive",
            intervention_type="general_support",
            confidence_score=0.5
        )

    def _load_response_templates(self) -> Dict[str, Dict[str, str]]:
        """Load response templates for different strategies and mood states"""
        return {
            "supportive_intervention": {
                "very_low_mood": "{mood_acknowledgment}, and I want you to know that your feelings are completely valid. {trend_comment} You don't have to face this alone - I'm here with you.",
                "low_mood": "{mood_acknowledgment}. {trend_comment} Sometimes it helps to take things one moment at a time. What feels most manageable for you right now?",
                "neutral_mood": "{mood_acknowledgment}. {trend_comment} How would you like to focus our conversation today?",
                "good_mood": "{mood_acknowledgment}. {trend_comment} What's been helping you maintain this positive state?"
            },
            "guidance_focused": {
                "default": "I'm here to help and support you. {mood_acknowledgment}. {trend_comment} What specific area would you like guidance with?"
            },
            "positive_reinforcement": {
                "default": "That's wonderful to hear! {mood_acknowledgment}. {trend_comment} I'd love to hear more about what's going well for you."
            },
            "maintenance_support": {
                "default": "{mood_acknowledgment}. {trend_comment} How can I best support you today?"
            }
        }

    def _load_crisis_keywords(self) -> List[str]:
        """Load keywords that indicate potential crisis situations"""
        return [
            "suicide", "kill myself", "end it all", "not worth living",
            "hurt myself", "self-harm", "can't go on", "give up entirely",
            "no point in living", "better off dead", "hopeless situation"
        ]

    def _load_therapeutic_responses(self) -> Dict[str, str]:
        """Load therapeutic response patterns"""
        return {
            "validation": "Your feelings are completely valid and understandable.",
            "normalization": "What you're experiencing is more common than you might think.",
            "hope_instillation": "While things feel difficult now, there are paths forward.",
            "strength_identification": "I can see the strength it takes to reach out and share this."
        }
