"""
Response Generator Module

This module coordinates all intelligent engine components to generate
contextually appropriate, mood-aware responses for the MantraPath chatbot.

Key Features:
    - Orchestrates mood-aware response generation
    - Integrates context analysis and service data
    - Provides fallback mechanisms
    - Tracks response effectiveness
    
Author: MantraPath Development Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .mood_aware_responder import MoodAwareResponder, MoodAwareResponse
from .service_integrator import ServiceIntegrator, ServiceContext
from .context_analyzer import ContextAnalyzer, ConversationContext

# Initialize logger first
logger = logging.getLogger(__name__)

@dataclass
class IntelligentResponse:
    """
    Complete intelligent response with all contextual information
    
    Attributes:
        response_text (str): The main response text
        tone (str): Response tone and style
        intervention_type (str): Type of intervention provided
        breathing_exercise (Optional[Dict]): Breathing exercise if applicable
        follow_up_suggestions (List[str]): Suggested follow-up actions
        crisis_detected (bool): Whether crisis situation was detected
        confidence_score (float): Confidence in response appropriateness
        context_used (Dict): Summary of context used for generation
        generation_metadata (Dict): Metadata about response generation
    """
    response_text: str
    tone: str
    intervention_type: str
    breathing_exercise: Optional[Dict[str, Any]] = None
    follow_up_suggestions: List[str] = None
    crisis_detected: bool = False
    confidence_score: float = 0.0
    context_used: Dict[str, Any] = None
    generation_metadata: Dict[str, Any] = None

class ResponseGenerator:
    """
    Central response generation engine that orchestrates all intelligent components
    
    This class coordinates the mood-aware responder, service integrator, and context
    analyzer to generate comprehensive, intelligent responses for users.
    """
    
    def __init__(self):
        """Initialize response generator with all intelligent engine components"""
        self.mood_responder = MoodAwareResponder()
        self.service_integrator = ServiceIntegrator()
        self.context_analyzer = ContextAnalyzer()
        
        # Response tracking for improvement
        self.response_history: Dict[str, List[Dict]] = {}
        
        logger.info("ResponseGenerator initialized with all intelligent components")

    async def generate_intelligent_response(
        self, 
        user_id: str,
        user_message: str, 
        session_id: str,
        conversation_history: List[Dict[str, Any]] = None
    ) -> IntelligentResponse:
        """
        Generate comprehensive intelligent response using all available context
        
        Args:
            user_id (str): User identifier
            user_message (str): User's current message
            session_id (str): Current conversation session ID
            conversation_history (List[Dict]): Previous conversation messages
            
        Returns:
            IntelligentResponse: Complete intelligent response with context
        """
        try:
            start_time = datetime.utcnow()
            logger.info(f"Generating intelligent response for user {user_id}")
            
            # Step 1: Gather comprehensive user context from all services
            service_context = await self.service_integrator.get_comprehensive_context(user_id)
            
            # Step 2: Analyze conversation context and user intent
            conversation_context = await self.context_analyzer.analyze_conversation_context(
                user_message, conversation_history
            )
            
            # Step 3: Generate mood-aware response
            mood_response = await self.mood_responder.generate_mood_aware_response(
                user_message, 
                service_context.mood_context, 
                conversation_history
            )
            
            # Step 4: Enhance response with conversation context
            enhanced_response = await self._enhance_with_context(
                mood_response, conversation_context, service_context
            )
            
            # Step 5: Personalize based on user profile
            personalized_response = await self._personalize_response(
                enhanced_response, service_context.user_profile
            )
            
            # Step 6: Create comprehensive intelligent response
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            intelligent_response = IntelligentResponse(
                response_text=personalized_response.response_text,
                tone=personalized_response.tone,
                intervention_type=personalized_response.intervention_type,
                breathing_exercise=personalized_response.breathing_exercise,
                follow_up_suggestions=personalized_response.follow_up_suggestions,
                crisis_detected=personalized_response.crisis_detected,
                confidence_score=personalized_response.confidence_score,
                context_used={
                    "mood_score": service_context.mood_context.current_mood_score,
                    "mood_trend": service_context.mood_context.mood_trend,
                    "user_intent": conversation_context.user_intent.value,
                    "emotional_intensity": conversation_context.emotional_intensity,
                    "urgency_level": conversation_context.urgency_level
                },
                generation_metadata={
                    "generation_time_seconds": generation_time,
                    "services_used": ["mood", "profile", "context_analysis"],
                    "response_strategy": personalized_response.intervention_type,
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Track response for improvement
            await self._track_response(user_id, user_message, intelligent_response)
            
            logger.info(
                f"Generated intelligent response for user {user_id} in {generation_time:.2f}s "
                f"with confidence {intelligent_response.confidence_score:.2f}"
            )
            
            return intelligent_response
            
        except Exception as e:
            logger.error(f"Error generating intelligent response for user {user_id}: {str(e)}")
            # Do not fabricate responses; surface the error to the caller
            raise

    async def _enhance_with_context(
        self, 
        mood_response: MoodAwareResponse, 
        conversation_context: ConversationContext,
        service_context: ServiceContext
    ) -> MoodAwareResponse:
        """
        Enhance mood-aware response with conversation context
        
        Args:
            mood_response (MoodAwareResponse): Base mood-aware response
            conversation_context (ConversationContext): Conversation analysis
            service_context (ServiceContext): Complete service context
            
        Returns:
            MoodAwareResponse: Enhanced response with conversation context
        """
        # Adjust response based on conversation stage
        if conversation_context.conversation_stage == "opening":
            # Add welcoming elements for new conversations
            if not mood_response.response_text.startswith(("Hi", "Hello", "Welcome")):
                greeting = f"Hi {service_context.user_profile.display_name}, "
                mood_response.response_text = greeting + mood_response.response_text.lower()
        
        # Adjust urgency based on conversation context
        if conversation_context.urgency_level >= 4:
            # Add urgency indicators to follow-up suggestions
            if mood_response.follow_up_suggestions:
                mood_response.follow_up_suggestions.insert(
                    0, "Consider reaching out to a trusted person right away"
                )
        
        # Enhance confidence based on context alignment
        context_confidence_boost = 0.0
        if conversation_context.user_intent.value in mood_response.intervention_type:
            context_confidence_boost += 0.1
        
        mood_response.confidence_score = min(1.0, mood_response.confidence_score + context_confidence_boost)
        
        return mood_response

    async def _personalize_response(
        self, 
        response: MoodAwareResponse, 
        user_profile
    ) -> MoodAwareResponse:
        """
        Personalize response based on user profile and preferences
        
        Args:
            response (MoodAwareResponse): Base response
            user_profile: User profile information
            
        Returns:
            MoodAwareResponse: Personalized response
        """
        # Adjust response length based on preferences
        comm_prefs = user_profile.communication_preferences
        preferred_length = comm_prefs.get('preferred_response_length', 'medium')
        
        if preferred_length == 'brief' and len(response.response_text) > 200:
            # Shorten response for users who prefer brief communication
            sentences = response.response_text.split('. ')
            if len(sentences) > 2:
                response.response_text = '. '.join(sentences[:2]) + '.'
        
        # Adjust tone based on preferences
        preferred_tone = comm_prefs.get('preferred_tone', 'supportive')
        if preferred_tone == 'professional' and response.tone == 'enthusiastic_positive':
            response.tone = 'balanced_supportive'
        
        # Consider mental health info for sensitivity
        mental_health_info = user_profile.mental_health_info
        if mental_health_info.get('conditions'):
            # Be more sensitive with users who have diagnosed conditions
            if 'anxiety' in mental_health_info.get('conditions', []):
                response.response_text = response.response_text.replace(
                    'quickly', 'at your own pace'
                ).replace('immediately', 'when you feel ready')
        
        return response

    async def _track_response(
        self, 
        user_id: str, 
        user_message: str, 
        response: IntelligentResponse
    ):
        """
        Track response for improvement and analytics
        
        Args:
            user_id (str): User identifier
            user_message (str): Original user message
            response (IntelligentResponse): Generated response
        """
        try:
            if user_id not in self.response_history:
                self.response_history[user_id] = []
            
            response_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_message": user_message,
                "response_text": response.response_text,
                "intervention_type": response.intervention_type,
                "confidence_score": response.confidence_score,
                "crisis_detected": response.crisis_detected,
                "context_used": response.context_used
            }
            
            self.response_history[user_id].append(response_record)
            
            # Keep only last 50 responses per user to manage memory
            if len(self.response_history[user_id]) > 50:
                self.response_history[user_id] = self.response_history[user_id][-50:]
            
        except Exception as e:
            logger.error(f"Error tracking response for user {user_id}: {str(e)}")

    # Fallback generation removed to avoid mock-like responses

    async def get_response_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get response analytics for a specific user
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Dict: Response analytics and insights
        """
        if user_id not in self.response_history:
            return {"error": "No response history found for user"}
        
        history = self.response_history[user_id]
        
        # Calculate basic analytics
        total_responses = len(history)
        avg_confidence = sum(r["confidence_score"] for r in history) / total_responses
        crisis_count = sum(1 for r in history if r["crisis_detected"])
        
        intervention_types = [r["intervention_type"] for r in history]
        most_common_intervention = max(set(intervention_types), key=intervention_types.count)
        
        return {
            "total_responses": total_responses,
            "average_confidence": round(avg_confidence, 2),
            "crisis_responses": crisis_count,
            "most_common_intervention": most_common_intervention,
            "response_history_days": (
                datetime.utcnow() - 
                datetime.fromisoformat(history[0]["timestamp"])
            ).days if history else 0
        }

    def get_engine_status(self) -> Dict[str, Any]:
        """
        Get status of all intelligent engine components
        
        Returns:
            Dict: Engine status information
        """
        return {
            "mood_responder": "active",
            "service_integrator": {
                "status": "active",
                "cache_stats": self.service_integrator.get_cache_stats()
            },
            "context_analyzer": "active",
            "response_generator": "active",
            "tracked_users": len(self.response_history),
            "total_responses_tracked": sum(
                len(history) for history in self.response_history.values()
            )
        }
