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
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

# HTTP client for MantraPath services
import httpx

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
    follow_up_suggestions: Optional[List[str]] = None
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
        
        # MantraPath service URLs from environment
        self.models_service_url = os.getenv('MODELS_SERVICE_URL', 'http://localhost:8081')
        # Remove deprecated phi4 agent URL attribute
        # self.phi4_agent_url = os.getenv('PHI4_AGENT_URL', 'http://localhost:8016')
        self.ai_context_store_url = os.getenv('AI_CONTEXT_STORE_URL', 'http://localhost:8006')
        self.memory_service_url = os.getenv('MEMORY_SERVICE_URL', 'http://localhost:8017')
        
        # Prioritize models service only
        self.use_models_service_first = True
        
        logger.info("MoodAwareResponder initialized with centralized models service priority")

    async def generate_mood_aware_response(
        self, 
        user_message: str, 
        mood_context: MoodContext,
        conversation_history: Optional[List[Dict[str, Any]]] = None
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
        conversation_history: Optional[List[Dict[str, Any]]] = None
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
        # Primary: Lightweight embeddings-based template selection (no large models)
        try:
            embeddings_response = await self._generate_via_embeddings_templates(
                user_message, mood_context, strategy, conversation_history
            )
            if embeddings_response:
                return embeddings_response
        except Exception as e:
            logger.error(f"Embeddings-based generation failed: {e}")
        
        # No mock/template fallback. Fail fast so the caller can handle properly.
        logger.error("No AI response available from embeddings pipeline")
        raise RuntimeError("No AI response available")
    
    def _build_system_prompt(self, mood_context: MoodContext, strategy: str) -> str:
        """
        Build system prompt for OpenAI based on mood context and strategy
        
        Args:
            mood_context (MoodContext): Current mood context
            strategy (str): Response strategy
            
        Returns:
            str: System prompt for AI
        """
        base_prompt = f"""You are Mantra-Mitra, the AI wellness companion for MantraPath - a comprehensive mental health platform. You have access to the user's mood tracking data, journal entries, and wellness journey.

Platform Context:
- MantraPath tracks mood scores (1-10 scale), energy levels, stress levels, and sleep quality
- Users can journal, join community forums, and participate in wellness challenges
- The platform provides emotional weather forecasts and personalized insights
- Current user mood score: {mood_context.current_mood_score}/10
- Recent mood trend: {mood_context.mood_trend}
- Stress level: {mood_context.stress_level}/10
- Energy level: {mood_context.energy_level}/10

Response Guidelines:
- Reference their actual mood data when relevant ("I see your mood score is {mood_context.current_mood_score}/10...")
- Be aware of their wellness journey on MantraPath
- Suggest platform features when appropriate (mood tracking, journaling, community)
- Keep responses warm, personal, and actionable (2-3 sentences)
- Never diagnose - focus on wellness support and professional referrals when needed
"""
        
        # Add mood-specific context
        mood_info = f"\nCurrent user context:\n- Mood score: {mood_context.current_mood_score}/10\n- Mood trend: {mood_context.mood_trend}\n- Stress level: {mood_context.stress_level}/10\n- Energy level: {mood_context.energy_level}/10"
        
        # Add strategy-specific guidance
        strategy_guidance = {
            "crisis_intervention": "\nIMPORTANT: User may be in crisis. Provide immediate support and encourage professional help.",
            "supportive_intervention": "\nFocus on validation and gentle support. Offer coping strategies.",
            "guidance_focused": "\nUser is seeking guidance. Provide practical advice and resources.",
            "positive_reinforcement": "\nUser is sharing positive experiences. Celebrate and encourage continued wellness.",
            "maintenance_support": "\nProvide general wellness support and check-in."
        }
        
        return base_prompt + mood_info + strategy_guidance.get(strategy, "")
    
    def _generate_follow_up_suggestions(self, mood_context: MoodContext) -> List[str]:
        """
        Generate follow-up suggestions based on mood context
        
        Args:
            mood_context (MoodContext): Current mood context
            
        Returns:
            List[str]: Follow-up suggestions
        """
        suggestions = []
        
        if mood_context.current_mood_score <= 5:
            suggestions.extend([
                "Consider taking a short walk outside",
                "Try journaling your thoughts and feelings",
                "Reach out to a supportive friend or family member"
            ])
        
        if mood_context.stress_level >= 7:
            suggestions.extend([
                "Practice deep breathing exercises",
                "Try a brief meditation or mindfulness exercise"
            ])
        
        if mood_context.energy_level <= 4:
            suggestions.extend([
                "Engage in gentle movement or stretching",
                "Listen to uplifting music"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    async def _generate_via_models_service_ollama(
        self,
        user_message: str,
        mood_context: MoodContext,
        strategy: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[MoodAwareResponse]:
        """
        Deprecated: Ollama/Phi routes removed.
        """
        return None
        try:
            # Get enhanced user context from AI Context Store and Memory Service
            enhanced_context = await self._get_enhanced_user_context(mood_context)
            
            # Build context for AI with enhanced user insights
            system_prompt = self._build_enhanced_system_prompt(mood_context, strategy, enhanced_context)
            
            # Build conversation context
            conversation_context = ""
            if conversation_history:
                for msg in conversation_history[-3:]:  # Last 3 messages for context
                    role = "User" if msg.get("sender") == "user" else "Assistant"
                    conversation_context += f"{role}: {msg.get('content', '')}\n"
            
            # Create complete prompt for centralized models service
            complete_prompt = f"""{system_prompt}

Previous conversation:
{conversation_context}

Current user message: {user_message}

Please provide a thoughtful, empathetic response that addresses the user's needs based on their mood context and the conversation strategy."""

            # Use centralized text generation endpoint
            request_data = {
                "prompt": complete_prompt,
                "max_tokens": 250,
                "temperature": 0.7
            }
            
            # Make request to centralized models service
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.models_service_url}/api/v1/nlp/generate",  # Centralized endpoint
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_text = result.get("generated_text", "").strip()
                    
                    if ai_text:
                        # Clean up response
                        if ai_text.startswith("System:") or ai_text.startswith("Assistant:"):
                            lines = ai_text.split("\n")
                            ai_text = "\n".join([line for line in lines if not line.strip().startswith(("System:", "Assistant:", "User:"))])
                            ai_text = ai_text.strip()
                        
                        # Determine if breathing exercise should be suggested
                        breathing_exercise = None
                        if mood_context.stress_level >= 7 or "anxious" in user_message.lower() or "stress" in user_message.lower():
                            breathing_exercise = {
                                "name": "4-7-8 Calming Breath",
                                "description": "A powerful technique to reduce anxiety and stress",
                                "steps": [
                                    {"action": "inhale", "duration": 4, "instruction": "Breathe in slowly through your nose"},
                                    {"action": "hold", "duration": 7, "instruction": "Hold your breath gently"},
                                    {"action": "exhale", "duration": 8, "instruction": "Exhale completely through your mouth"}
                                ],
                                "cycles": 4
                            }
                        
                        return MoodAwareResponse(
                            response_text=ai_text,
                            tone=self._determine_response_tone(mood_context),
                            intervention_type=strategy,
                            breathing_exercise=breathing_exercise,
                            confidence_score=0.88,  # High confidence for centralized models service
                            follow_up_suggestions=self._generate_follow_up_suggestions(mood_context)
                        )
                    else:
                        logger.warning(f"Centralized Models Service returned empty response")
                        return None
                else:
                    logger.error(f"Centralized Models Service request failed with status {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Centralized Models Service request failed: {e}")
            return None
    
    async def _generate_phi4_agent_response(
        self,
        user_message: str,
        mood_context: MoodContext,
        strategy: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[MoodAwareResponse]:
        """Deprecated: Phi-4 agent fallback removed."""
        return None
    
    async def _generate_models_service_response(
        self,
        user_message: str,
        mood_context: MoodContext,
        strategy: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[MoodAwareResponse]:
        """Deprecated: legacy models-service text generation removed."""
        return None

    async def _generate_via_embeddings_templates(
        self,
        user_message: str,
        mood_context: MoodContext,
        strategy: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[MoodAwareResponse]:
        """
        Generate a response by leveraging TEI embeddings from the Models Service
        to select and personalize a high-quality template. This avoids large
        transformer models while producing meaningful, contextual replies.
        """
        try:
            # Build candidate templates tailored to strategy
            templates_map: Dict[str, List[str]] = self._load_template_candidates()
            candidates: List[str] = templates_map.get(strategy, templates_map.get("maintenance_support", []))
            if not candidates:
                return None

            # Create embeddings for user message and templates
            from ..clients.models_service_client import models_client

            message_embedding = await models_client.get_text_embeddings(user_message)
            if not message_embedding or not message_embedding.embedding:
                return None

            # Score templates by cosine similarity
            import math
            def cosine(a: List[float], b: List[float]) -> float:
                dot = sum(x*y for x, y in zip(a, b))
                na = math.sqrt(sum(x*x for x in a))
                nb = math.sqrt(sum(x*x for x in b))
                return (dot / (na * nb)) if na and nb else 0.0

            best_template: Optional[str] = None
            best_score: float = -1.0

            for template in candidates:
                emb = await models_client.get_text_embeddings(template)
                if emb and emb.embedding:
                    score = cosine(message_embedding.embedding, emb.embedding)
                    if score > best_score:
                        best_score = score
                        best_template = template

            if not best_template:
                return None

            # Personalize and return
            personalized = await self._personalize_response(best_template, user_message, mood_context)
            return MoodAwareResponse(
                response_text=personalized,
                tone=self._determine_response_tone(mood_context),
                intervention_type=strategy,
                confidence_score=min(0.9, max(0.5, best_score)),
                follow_up_suggestions=self._generate_follow_up_suggestions(mood_context)
            )
        except Exception:
            return None

    async def _get_enhanced_user_context(self, mood_context: MoodContext) -> Dict[str, Any]:
        """
        Get enhanced user context from AI Context Store and Memory Service
        
        Args:
            mood_context (MoodContext): Current mood context
            
        Returns:
            Dict[str, Any]: Enhanced user context data
        """
        enhanced_context = {
            "ai_insights": {},
            "behavioral_patterns": {},
            "memory_insights": {}
        }
        
        try:
            # Try to get AI insights from AI Context Store
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Note: In a real implementation, we'd need user_id from the request context
                # For now, we'll use a placeholder approach
                ai_context_response = await client.get(
                    f"{self.ai_context_store_url}/api/v1/intelligence/insights/user_placeholder",
                    timeout=5.0
                )
                if ai_context_response.status_code == 200:
                    enhanced_context["ai_insights"] = ai_context_response.json()
        except Exception as e:
            logger.warning(f"Could not get AI Context Store insights: {e}")
        
        try:
            # Try to get behavioral insights from Memory Service
            async with httpx.AsyncClient(timeout=10.0) as client:
                memory_response = await client.get(
                    f"{self.memory_service_url}/api/v1/insights/user_placeholder",
                    timeout=5.0
                )
                if memory_response.status_code == 200:
                    enhanced_context["memory_insights"] = memory_response.json()
        except Exception as e:
            logger.warning(f"Could not get Memory Service insights: {e}")
        
        return enhanced_context
    
    def _build_enhanced_system_prompt(self, mood_context: MoodContext, strategy: str, enhanced_context: Dict[str, Any]) -> str:
        """
        Build enhanced system prompt with AI Context Store and Memory Service insights
        
        Args:
            mood_context (MoodContext): Current mood context
            strategy (str): Response strategy
            enhanced_context (Dict): Enhanced user context from other services
            
        Returns:
            str: Enhanced system prompt for AI
        """
        base_prompt = self._build_system_prompt(mood_context, strategy)
        
        # Add enhanced context insights if available
        if enhanced_context.get("ai_insights"):
            ai_insights = enhanced_context["ai_insights"]
            base_prompt += f"\n\nAI-Generated User Insights:\n{ai_insights}"
        
        if enhanced_context.get("memory_insights"):
            memory_insights = enhanced_context["memory_insights"]
            base_prompt += f"\n\nBehavioral Memory Insights:\n{memory_insights}"
        
        return base_prompt
    
    async def _generate_template_response(
        self,
        user_message: str,
        mood_context: MoodContext,
        strategy: str
    ) -> MoodAwareResponse:
        """
        Generate template-based response as fallback
        
        Args:
            user_message (str): User's message
            mood_context (MoodContext): Current mood context
            strategy (str): Selected response strategy
            
        Returns:
            MoodAwareResponse: Template-based response
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
            confidence_score=0.65  # Lower confidence for template responses
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

    def _load_template_candidates(self) -> Dict[str, List[str]]:
        """Lightweight templates for embeddings-based selection."""
        base = self._load_response_templates()
        return {
            "crisis_intervention": [
                base["supportive_intervention"]["very_low_mood"],
                "I hear how overwhelming this feels. You're not alone. Let's focus on one small step together right now.",
            ],
            "supportive_intervention": [
                base["supportive_intervention"]["low_mood"],
                base["maintenance_support"]["default"],
            ],
            "guidance_focused": [
                base["guidance_focused"]["default"],
            ],
            "positive_reinforcement": [
                base["positive_reinforcement"]["default"],
            ],
            "maintenance_support": [
                base["maintenance_support"]["default"],
            ],
        }
