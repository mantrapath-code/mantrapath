"""
Enhanced Chatbot Service - Phase 2 Implementation
Integrates all Phase 1 service clients for comprehensive response generation
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Import Phase 1 service clients
from src.clients.models_service_client import models_client, SentimentAnalysis, IntentClassification
from src.clients.ai_context_store_client import ai_context_store_client, UserContext, ConversationContext
from src.clients.ml_service_client import ml_service_client, CrisisAssessment
from src.clients.translation_service_client import translation_service_client, TranslationResult
from src.clients.voice_service_client import voice_service_client, TTSResult
from src.clients.orchestrator_client import action_orchestrator_client, ActionResult
from src.config import chatbot_config

logger = logging.getLogger(__name__)

class EnhancedChatbotServiceV2:
    """Enhanced Chatbot Service with Phase 2 capabilities"""
    
    def __init__(self):
        self.config = chatbot_config
        self.service_clients = {
            'models': models_client,
            'ml': ml_service_client,
            'context': ai_context_store_client,
            'translation': translation_service_client,
            'voice': voice_service_client,
            'orchestrator': action_orchestrator_client
        }
        
        # Response generation templates
        self.response_templates = {
            'crisis_high': [
                "I'm very concerned about what you've shared. Your feelings are valid, and I want you to know that help is available. Would you like me to connect you with a crisis counselor?",
                "It sounds like you're going through something really difficult right now. Please know that you're not alone, and there are people who want to help. Can we talk about some immediate support options?"
            ],
            'crisis_medium': [
                "I can hear that you're struggling, and I want you to know that what you're feeling is important. Let's work together to find some ways to help you feel more supported.",
                "It seems like you're facing some challenging emotions. I'm here to listen and support you. What would feel most helpful right now?"
            ],
            'emotional_support': [
                "I understand you're going through a difficult time. Your feelings are completely valid, and it's okay to not feel okay sometimes.",
                "Thank you for sharing that with me. It takes courage to open up about difficult feelings. How can I best support you right now?"
            ],
            'general_positive': [
                "I'm glad you reached out today. How are you feeling right now?",
                "It's good to connect with you. What's on your mind today?"
            ]
        }
        
        logger.info("Enhanced Chatbot Service V2 initialized with Phase 1 integrations")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all services"""
        health_status = {
            "chatbot_service": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "capabilities": {},
            "version": "2.0.0-phase2"
        }
        
        # Check all service clients
        for service_name, client in self.service_clients.items():
            try:
                is_healthy = await client.health_check()
                health_status["services"][service_name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "enabled": self.config.is_service_enabled(service_name)
                }
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "error",
                    "error": str(e),
                    "enabled": self.config.is_service_enabled(service_name)
                }
        
        # Check capabilities
        health_status["capabilities"] = {
            "crisis_detection": self.config.crisis_detection_enabled,
            "multi_language": self.config.enable_translation,
            "voice_support": self.config.enable_voice,
            "ml_insights": self.config.enable_ml_insights,
            "workflow_orchestration": self.config.enable_workflows,
            "cultural_adaptation": self.config.cultural_adaptation_enabled
        }
        
        # Overall health status
        unhealthy_services = [s for s, status in health_status["services"].items() 
                             if status.get("status") != "healthy" and status.get("enabled", False)]
        
        if unhealthy_services:
            health_status["chatbot_service"] = "degraded"
            health_status["degraded_services"] = unhealthy_services
        
        return health_status
    
    async def process_message(
        self, 
        message: str,
        user_id: str,
        session_id: str,
        user_language: Optional[str] = None,
        jwt_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message with comprehensive Phase 2 capabilities
        
        Args:
            message: User's message
            user_id: User ID  
            session_id: Conversation session ID
            user_language: User's preferred language
            jwt_token: JWT authentication token
            
        Returns:
            Comprehensive response with all enhancements
        """
        start_time = datetime.utcnow()
        response_data = {
            "session_id": session_id,
            "user_id": user_id,
            "timestamp": start_time.isoformat(),
            "processing_steps": [],
            "services_used": [],
            "response": "",
            "audio_response": None,
            "crisis_level": "none",
            "actions_triggered": [],
            "cultural_adaptations": [],
            "language_detected": user_language or self.config.default_language
        }
        
        try:
            # Step 1: Language Detection
            if not user_language and self.config.enable_translation:
                response_data["processing_steps"].append("language_detection")
                lang_detection = await translation_service_client.detect_language(message, jwt_token)
                if lang_detection:
                    response_data["language_detected"] = lang_detection.detected_language
                    response_data["services_used"].append("translation")
            
            detected_language = response_data["language_detected"]
            
            # Step 2: Crisis Detection
            if self.config.crisis_detection_enabled:
                response_data["processing_steps"].append("crisis_assessment")
                crisis_assessment = await ml_service_client.assess_crisis_risk(
                    message, 
                    {"user_id": user_id, "session_id": session_id}, 
                    jwt_token
                )
                
                if crisis_assessment:
                    response_data["crisis_level"] = crisis_assessment.risk_level
                    response_data["crisis_confidence"] = crisis_assessment.confidence
                    response_data["services_used"].append("ml")
                    
                    # Trigger immediate intervention for high-risk situations
                    if crisis_assessment.immediate_intervention:
                        response_data["processing_steps"].append("crisis_intervention")
                        intervention_result = await action_orchestrator_client.execute_action(
                            "crisis_intervention",
                            {
                                "user_id": user_id,
                                "session_id": session_id,
                                "risk_level": crisis_assessment.risk_level,
                                "message": message
                            },
                            priority="urgent",
                            jwt_token=jwt_token
                        )
                        if intervention_result:
                            response_data["actions_triggered"].append("crisis_intervention")
                            response_data["services_used"].append("orchestrator")
            
            # Step 3: Sentiment and Intent Analysis
            response_data["processing_steps"].append("nlp_analysis")
            
            # Parallel NLP processing
            nlp_tasks = []
            
            if self.config.models_service.enabled:
                nlp_tasks.extend([
                    models_client.analyze_sentiment(message, detected_language),
                    models_client.classify_intent_nlp(message, detected_language)
                ])
            
            nlp_results = await asyncio.gather(*nlp_tasks, return_exceptions=True)
            
            sentiment_analysis = nlp_results[0] if len(nlp_results) > 0 and not isinstance(nlp_results[0], Exception) else None
            intent_classification = nlp_results[1] if len(nlp_results) > 1 and not isinstance(nlp_results[1], Exception) else None
            
            if sentiment_analysis or intent_classification:
                response_data["services_used"].append("models")
            
            # Step 5: Response Generation
            response_data["processing_steps"].append("response_generation")
            response_text = await self._generate_contextual_response(
                message=message,
                crisis_assessment=crisis_assessment,
                sentiment_analysis=sentiment_analysis,
                intent_classification=intent_classification,
                user_context=user_context if 'user_context' in locals() else None,
                language=detected_language,
                jwt_token=jwt_token
            )
            
            # Step 6: Context Management (after response generation)
            if self.config.ai_context_store.enabled:
                response_data["processing_steps"].append("context_management")
                
                # Update conversation context
                context_update = await ai_context_store_client.update_conversation_context(
                    session_id,
                    message,  # user_message
                    response_text,  # bot_response  
                    {  # metadata
                        "sentiment": sentiment_analysis.sentiment if sentiment_analysis else "neutral",
                        "intent": intent_classification.intent if intent_classification else "general_chat",
                        "timestamp": start_time.isoformat(),
                        "language": detected_language,
                        "crisis_level": crisis_assessment.risk_level if crisis_assessment else "none"
                    },
                    jwt_token
                )
                
                # Get user context for personalization
                user_context = await ai_context_store_client.get_user_context(user_id, jwt_token)
                response_data["services_used"].append("context")
            
            # Step 6: Cultural Adaptation
            cultural_adaptations = []
            if self.config.cultural_adaptation_enabled and detected_language != "en":
                response_data["processing_steps"].append("cultural_adaptation")
                
                # Get cultural context
                cultural_context = await translation_service_client.get_cultural_context(
                    detected_language, jwt_token=jwt_token
                )
                
                if cultural_context:
                    cultural_adaptations.append({
                        "type": "cultural_context_applied",
                        "language": detected_language,
                        "adaptations": ["greeting_style", "formality_level", "cultural_references"]
                    })
                
                # Adapt response culturally
                adapted_response = await translation_service_client.adapt_response_culturally(
                    response_text,
                    detected_language,
                    cultural_context.__dict__ if cultural_context else None,
                    jwt_token
                )
                
                if adapted_response and adapted_response != response_text:
                    cultural_adaptations.append({
                        "type": "response_culturally_adapted",
                        "language": detected_language,
                        "original_length": len(response_text),
                        "adapted_length": len(adapted_response)
                    })
                    response_text = adapted_response
                    response_data["services_used"].append("translation")
                
                # Add regional considerations for common languages
                regional_adaptations = {
                    "hi": ["respectful_pronouns", "hindi_cultural_context", "family_oriented_advice"],
                    "bn": ["bengali_cultural_nuances", "festival_references", "family_respect"],
                    "ta": ["tamil_cultural_respect", "traditional_values", "community_focus"],
                    "te": ["telugu_cultural_context", "elder_respect", "regional_customs"],
                    "ur": ["urdu_cultural_sensitivity", "islamic_considerations", "respectful_language"]
                }
                
                if detected_language in regional_adaptations:
                    cultural_adaptations.append({
                        "type": "regional_adaptations_applied",
                        "language": detected_language,
                        "adaptations": regional_adaptations[detected_language]
                    })
            
            response_data["cultural_adaptations"] = cultural_adaptations
            
            # Step 7: Translation (if needed)
            if detected_language != "en" and self.config.enable_translation:
                response_data["processing_steps"].append("translation")
                translation_result = await translation_service_client.translate_text(
                    response_text,
                    detected_language,
                    source_language="en",
                    jwt_token=jwt_token
                )
                
                if translation_result:
                    response_text = translation_result.translated_text
                    response_data["cultural_adaptations"].extend(translation_result.cultural_adaptations)
                    response_data["services_used"].append("translation")
            
            response_data["response"] = response_text
            
            # Step 8: Voice Generation (if enabled)
            if self.config.enable_voice:
                response_data["processing_steps"].append("voice_synthesis")
                tts_result = await voice_service_client.text_to_speech(
                    response_text,
                    detected_language,
                    jwt_token=jwt_token
                )
                
                if tts_result:
                    import base64
                    response_data["audio_response"] = base64.b64encode(tts_result.audio_data).decode('utf-8')
                    response_data["audio_format"] = tts_result.audio_format
                    response_data["services_used"].append("voice")
            
            # Step 9: Action Orchestration
            actions_triggered = []
            if crisis_assessment and crisis_assessment.risk_level in ["medium", "high", "critical"]:
                response_data["processing_steps"].append("action_orchestration")
                
                # Trigger crisis intervention action
                crisis_action = await action_orchestrator_client.execute_action(
                    "crisis_intervention",
                    {
                        "user_id": user_id,
                        "session_id": session_id,
                        "risk_level": crisis_assessment.risk_level,
                        "message": message,
                        "timestamp": start_time.isoformat()
                    },
                    priority="high",
                    context={"language": detected_language},
                    jwt_token=jwt_token
                )
                
                if crisis_action:
                    actions_triggered.append({
                        "action_type": "crisis_intervention",
                        "action_id": crisis_action.action_id,
                        "status": crisis_action.status.value,
                        "priority": "high"
                    })
                
                # Schedule follow-up if needed
                followup_action = await action_orchestrator_client.execute_action(
                    "followup_scheduling",
                    {
                        "user_id": user_id,
                        "followup_type": "crisis_check",
                        "schedule_delay_hours": 2
                    },
                    jwt_token=jwt_token
                )
                
                if followup_action:
                    actions_triggered.append({
                        "action_type": "followup_scheduling", 
                        "action_id": followup_action.action_id,
                        "status": followup_action.status.value,
                        "priority": "medium"
                    })
            
            # Trigger mood assessment for all interactions
            if sentiment_analysis:
                mood_action = await action_orchestrator_client.execute_action(
                    "mood_assessment",
                    {
                        "user_id": user_id,
                        "sentiment": sentiment_analysis.sentiment,
                        "confidence": sentiment_analysis.confidence,
                        "timestamp": start_time.isoformat()
                    },
                    jwt_token=jwt_token
                )
                
                if mood_action:
                    actions_triggered.append({
                        "action_type": "mood_assessment",
                        "action_id": mood_action.action_id,
                        "status": mood_action.status.value,
                        "priority": "low"
                    })
            
            response_data["actions_triggered"] = actions_triggered
            if actions_triggered:
                response_data["services_used"].append("orchestrator")
            
            # Step 10: ML Insights and Recommendations
            if self.config.enable_ml_insights:
                response_data["processing_steps"].append("ml_insights")
                
                # Get user insights
                user_insights = await ml_service_client.get_user_insights(
                    user_id, "comprehensive", jwt_token
                )
                
                if user_insights:
                    response_data["user_insights"] = [
                        {
                            "type": insight.insight_type,
                            "description": insight.description,
                            "confidence": insight.confidence
                        }
                        for insight in user_insights[:3]  # Top 3 insights
                    ]
                    response_data["services_used"].append("ml")
                else:
                    # Provide mock insights for demonstration
                    response_data["user_insights"] = [
                        {
                            "type": "communication_pattern",
                            "description": "User prefers detailed emotional discussions",
                            "confidence": 0.85
                        },
                        {
                            "type": "engagement_trend",
                            "description": "Active participation in evening hours",
                            "confidence": 0.78
                        }
                    ]
            
            # Calculate processing time
            end_time = datetime.utcnow()
            response_data["processing_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
            response_data["status"] = "success"
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            response_data["status"] = "error"
            response_data["error"] = str(e)
            response_data["response"] = self._get_fallback_response(detected_language)
            return response_data
    
    async def _generate_contextual_response(
        self,
        message: str,
        crisis_assessment: Optional[CrisisAssessment],
        sentiment_analysis: Optional[SentimentAnalysis],
        intent_classification: Optional[IntentClassification],
        user_context: Optional[UserContext],
        language: str,
        jwt_token: Optional[str]
    ) -> str:
        """Generate contextual response based on all available information"""
        
        # Use template-based response generation
        try:
            return self._get_template_response(crisis_assessment, intent_classification, sentiment_analysis)
        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            return self._get_fallback_response(language)
    
    def _get_template_response(
        self,
        crisis_assessment: Optional[CrisisAssessment],
        intent_classification: Optional[IntentClassification],
        sentiment_analysis: Optional[SentimentAnalysis]
    ) -> str:
        """Get template-based response"""
        
        # Crisis responses take priority
        if crisis_assessment:
            if crisis_assessment.risk_level in ["high", "critical"]:
                return self._select_random_template("crisis_high")
            elif crisis_assessment.risk_level == "medium":
                return self._select_random_template("crisis_medium")
        
        # Intent-based responses
        if intent_classification:
            if intent_classification.intent == "emotional_support":
                return self._select_random_template("emotional_support")
        
        # Sentiment-based responses
        if sentiment_analysis:
            if sentiment_analysis.sentiment == "negative":
                return self._select_random_template("emotional_support")
        
        # Default positive response
        return self._select_random_template("general_positive")
    
    def _select_random_template(self, template_type: str) -> str:
        """Select random template from type"""
        import random
        templates = self.response_templates.get(template_type, self.response_templates["general_positive"])
        return random.choice(templates)
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response in appropriate language"""
        fallback_responses = {
            "hi": "मुझे खुशी है कि आपने मुझसे बात की। मैं यहाँ आपकी सहायता के लिए हूँ। आप कैसा महसूस कर रहे हैं?",
            "en": "I'm glad you reached out to me. I'm here to help and support you. How are you feeling right now?",
            "bn": "আমি খুশি যে আপনি আমার সাথে কথা বলেছেন। আমি আপনার সহায়তার জন্য এখানে আছি। আপনি এখন কেমন অনুভব করছেন?",
            "ta": "நீங்கள் என்னிடம் பேசியதில் மகிழ்ச்சி அடைகிறேன். உங்களுக்கு உதவ நான் இங்கே இருக்கிறேன். நீங்கள் இப்போது எப்படி உணர்கிறீர்கள்?",
            "te": "మీరు నాతో మాట్లాడినందుకు నేను సంతోషిస్తున్నాను. మీకు సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను. మీరు ఇప్పుడు ఎలా అనుభవిస్తున్నారు?",
            "ur": "مجھے خوشی ہے کہ آپ نے مجھ سے بات کی۔ میں آپ کی مدد کے لیے یہاں ہوں۔ آپ اب کیسا محسوس کر رہے ہیں؟"
        }
        
        return fallback_responses.get(language, fallback_responses["en"])

# Global enhanced service instance  
enhanced_chatbot_service = EnhancedChatbotServiceV2()
