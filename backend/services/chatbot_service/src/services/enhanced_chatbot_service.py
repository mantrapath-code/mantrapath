"""
Enhanced Chatbot Service with Action Orchestrator Integration
Provides intelligent conversation handling with cross-service coordination
"""
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ..clients.action_orchestrator_client import (
    action_orchestrator_client, 
    OrchestrationRequest, 
    VoiceIntent,
    OrchestrationResponse
)

logger = logging.getLogger(__name__)

@dataclass
class ChatContext:
    """Enhanced chat context with orchestration support"""
    user_id: str
    session_id: str
    language: str = "en"
    cultural_preferences: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None
    mood_context: Optional[Dict[str, Any]] = None
    recent_actions: Optional[List[str]] = None

@dataclass
class EnhancedChatResponse:
    """Enhanced chat response with orchestration metadata"""
    response: str
    message_type: str = "text"
    intent: Optional[VoiceIntent] = None
    orchestration_metadata: Optional[Dict[str, Any]] = None
    suggested_actions: Optional[List[Dict[str, Any]]] = None
    mood_insights: Optional[Dict[str, Any]] = None
    cultural_adaptations: Optional[Dict[str, Any]] = None

class EnhancedChatbotService:
    """Enhanced chatbot service with Action Orchestrator integration"""
    
    def __init__(self, base_chatbot_service=None):
        """
        Initialize enhanced chatbot service
        
        Args:
            base_chatbot_service: Existing chatbot service instance to wrap
        """
        self.base_service = base_chatbot_service
        self.orchestrator_enabled = os.getenv("ACTION_ORCHESTRATOR_INTEGRATION", "true").lower() == "true"
        self.fallback_to_base = os.getenv("CHATBOT_FALLBACK_TO_BASE", "true").lower() == "true"
        
        # Intent thresholds for different actions
        self.mood_intent_threshold = float(os.getenv("MOOD_INTENT_THRESHOLD", "0.7"))
        self.translation_intent_threshold = float(os.getenv("TRANSLATION_INTENT_THRESHOLD", "0.6"))
        self.cross_service_threshold = float(os.getenv("CROSS_SERVICE_THRESHOLD", "0.8"))
        
        logger.info(f"Enhanced Chatbot Service initialized - Orchestrator: {self.orchestrator_enabled}")
    
    async def process_message(
        self, 
        message: str, 
        context: ChatContext,
        jwt_token: Optional[str] = None
    ) -> EnhancedChatResponse:
        """
        Process chat message with intelligent orchestration
        
        Args:
            message: User message
            context: Chat context
            jwt_token: JWT token for authentication
            
        Returns:
            Enhanced chat response with orchestration data
        """
        try:
            # Step 1: Try Action Orchestrator for intelligent processing
            if self.orchestrator_enabled:
                orchestration_response = await self._orchestrate_conversation(
                    message, context, jwt_token
                )
                
                if orchestration_response:
                    return await self._build_enhanced_response(
                        message, orchestration_response, context
                    )
            
            # Step 2: Fallback to base chatbot service
            if self.fallback_to_base and self.base_service:
                base_response = await self._get_base_response(message, context, jwt_token)
                return self._wrap_base_response(base_response, context)
            
            # Step 3: Minimal fallback response
            return self._create_fallback_response(message, context)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._create_error_response(str(e))
    
    async def _orchestrate_conversation(
        self, 
        message: str, 
        context: ChatContext,
        jwt_token: Optional[str] = None
    ) -> Optional[OrchestrationResponse]:
        """Orchestrate conversation through Action Orchestrator"""
        try:
            logger.info(f"Starting orchestration for user_id: {context.user_id}, session_id: {context.session_id}, message: {message}")
            
            # Build orchestration request
            orchestration_context: Dict[str, Any] = {
                "conversation_history": context.conversation_history or [],
                "mood_context": context.mood_context,
                "recent_actions": context.recent_actions or [],
                "session_type": "chat",
                "interaction_type": "conversation"
            }
            
            request = OrchestrationRequest(
                voice_input=message,
                user_id=context.user_id,
                language=context.language,
                cultural_preferences=context.cultural_preferences,
                session_id=context.session_id,
                context=orchestration_context
            )
            
            logger.info(f"Sending orchestration request: user_id={request.user_id}, session_id={request.session_id}")
            result = await action_orchestrator_client.orchestrate_action(request, jwt_token)
            
            if result:
                logger.info(f"Orchestration successful: intent={result.intent.intent_type}, confidence={result.intent.confidence}")
            else:
                logger.warning("Orchestration returned None - will fallback")
                
            return result
            
        except Exception as e:
            logger.error(f"Conversation orchestration failed: {e}", exc_info=True)
            return None
    
    async def _build_enhanced_response(
        self, 
        original_message: str,
        orchestration: OrchestrationResponse,
        context: ChatContext
    ) -> EnhancedChatResponse:
        """Build enhanced response from orchestration results"""
        
        # Extract chatbot response from orchestration results
        chatbot_response = None
        mood_insights = None
        suggested_actions = []
        cultural_adaptations = orchestration.cultural_context
        
        for result in orchestration.results:
            if result.service_name == "chatbot_service" and result.success:
                chatbot_response = result.result_data.get("response") if result.result_data else None
            elif result.service_name == "mood_service" and result.success:
                mood_insights = result.result_data
            elif result.service_name == "translation_service" and result.success:
                # Handle translation results
                pass
        
        # Generate suggested actions based on intent
        if orchestration.intent:
            suggested_actions = self._generate_suggested_actions(orchestration.intent, context)
        
        # Use chatbot response or generate one based on intent
        final_response = chatbot_response or self._generate_response_from_intent(
            orchestration.intent, context
        )
        
        return EnhancedChatResponse(
            response=final_response,
            message_type="enhanced_chat",
            intent=orchestration.intent,
            orchestration_metadata={
                "workflow_id": orchestration.workflow_id,
                "execution_time_ms": orchestration.total_execution_time_ms,
                "services_involved": [r.service_name for r in orchestration.results],
                "success_rate": len([r for r in orchestration.results if r.success]) / len(orchestration.results) if orchestration.results else 0
            },
            suggested_actions=suggested_actions,
            mood_insights=mood_insights,
            cultural_adaptations=cultural_adaptations
        )
    
    def _generate_suggested_actions(
        self, 
        intent: VoiceIntent, 
        context: ChatContext
    ) -> List[Dict[str, Any]]:
        """Generate suggested actions based on intent"""
        suggestions = []
        
        if intent.intent_type == "mood_tracking" and intent.confidence >= self.mood_intent_threshold:
            suggestions.append({
                "action": "track_mood",
                "label": "Track Current Mood",
                "description": "Record how you're feeling right now",
                "confidence": intent.confidence
            })
        
        if intent.intent_type == "journal_entry":
            suggestions.append({
                "action": "create_journal",
                "label": "Create Journal Entry",
                "description": "Write about your thoughts and experiences",
                "confidence": intent.confidence
            })
        
        if intent.intent_type == "breathing_exercise":
            suggestions.append({
                "action": "start_breathing",
                "label": "Start Breathing Exercise",
                "description": "Begin a guided breathing session",
                "confidence": intent.confidence
            })
        
        # Language-specific suggestions
        if context.language != "en" and intent.confidence >= self.translation_intent_threshold:
            suggestions.append({
                "action": "translate_conversation",
                "label": f"Switch to {context.language.upper()}",
                "description": "Continue conversation in your preferred language",
                "confidence": intent.confidence
            })
        
        return suggestions
    
    def _generate_response_from_intent(
        self, 
        intent: VoiceIntent, 
        context: ChatContext
    ) -> str:
        """Generate contextual response based on intent"""
        
        if intent.intent_type == "mood_tracking":
            if context.language == "hi":
                return "मैं समझ गया कि आप अपने मूड के बारे में बात करना चाहते हैं। क्या आप बताना चाहेंगे कि आप कैसा महसूस कर रहे हैं?"
            else:
                return "I understand you'd like to talk about how you're feeling. Would you like to share what's on your mind?"
        
        elif intent.intent_type == "journal_entry":
            if context.language == "hi":
                return "यह बहुत अच्छा है कि आप अपने विचारों को लिखना चाहते हैं। मैं आपकी जर्नल लिखने में मदद कर सकता हूं।"
            else:
                return "It's wonderful that you want to journal your thoughts. I can help you organize and reflect on your experiences."
        
        elif intent.intent_type == "breathing_exercise":
            if context.language == "hi":
                return "सांस की एक्सरसाइज एक बेहतरीन विचार है। क्या आप गाइडेड ब्रीदिंग सेशन शुरू करना चाहेंगे?"
            else:
                return "A breathing exercise is a great idea. Would you like to start a guided breathing session?"
        
        elif intent.intent_type == "chat_conversation":
            if context.cultural_preferences and context.cultural_preferences.get("communication_style") == "formal":
                return "I'm here to assist you. How may I help you today?"
            else:
                return "I'm here to chat! What's on your mind?"
        
        else:
            # Generic response based on cultural context
            if context.language == "hi":
                return "मैं आपकी बात समझने की कोशिश कर रहा हूं। क्या आप और विस्तार से बता सकते हैं?"
            else:
                return "I'm trying to understand what you need. Could you tell me a bit more?"
    
    async def _get_base_response(
        self, 
        message: str, 
        context: ChatContext,
        jwt_token: Optional[str] = None
    ) -> Optional[str]:
        """Get response from base chatbot service"""
        if not self.base_service:
            return None
        
        try:
            # Call base service (this would depend on your existing chatbot service interface)
            # This is a placeholder - you'll need to adapt to your actual service
            response = await self.base_service.chat_with_bot(
                message=message,
                session_id=context.session_id,
                user_id=context.user_id,
                language=context.language
            )
            return response.get("response") if isinstance(response, dict) else str(response)
        except Exception as e:
            logger.error(f"Base chatbot service failed: {e}")
            return None
    
    def _wrap_base_response(
        self, 
        base_response: Optional[str], 
        context: ChatContext
    ) -> EnhancedChatResponse:
        """Wrap base service response in enhanced format"""
        return EnhancedChatResponse(
            response=base_response or "I'm having trouble processing your message right now.",
            message_type="base_chat",
            orchestration_metadata={"source": "base_service"},
            cultural_adaptations={"language": context.language}
        )
    
    def _create_fallback_response(
        self, 
        message: str, 
        context: ChatContext
    ) -> EnhancedChatResponse:
        """Create minimal fallback response"""
        if context.language == "hi":
            response = "माफ़ करें, मुझे अभी थोड़ी तकनीकी समस्या हो रही है। कृपया थोड़ी देर बाद कोशिश करें।"
        else:
            response = "I'm experiencing some technical difficulties right now. Please try again in a moment."
        
        return EnhancedChatResponse(
            response=response,
            message_type="fallback",
            orchestration_metadata={"source": "fallback"},
            cultural_adaptations={"language": context.language}
        )
    
    def _create_error_response(self, error_message: str) -> EnhancedChatResponse:
        """Create error response"""
        return EnhancedChatResponse(
            response="I'm sorry, I encountered an error while processing your message.",
            message_type="error",
            orchestration_metadata={"error": error_message, "source": "error_handler"}
        )
    
    async def get_conversation_insights(
        self, 
        session_id: str,
        jwt_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get conversation insights from Action Orchestrator"""
        try:
            # This could be extended to get insights about the conversation
            # from the Action Orchestrator's analytics capabilities
            return {
                "session_id": session_id,
                "insights_available": self.orchestrator_enabled,
                "message": "Conversation insights feature coming soon"
            }
        except Exception as e:
            logger.error(f"Failed to get conversation insights: {e}")
            return None
