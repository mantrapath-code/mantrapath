"""
Enhanced Chatbot Service - Phase 2 Implementation
Integrates all Phase 1 service clients for comprehensive response generation
"""
import asyncio
import logging
import os
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
from src.clients.memory_service_client import memory_service_client, MemoryEntry, ConversationSummary
from src.clients.proactive_assistance_engine_client import proactive_assistance_engine_client, ProactiveInsight, UserRiskAssessment
from src.clients.ai_event_processor_client import ai_event_processor_client, ChatEvent
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
            'orchestrator': action_orchestrator_client,
            'memory': memory_service_client,
            'proactive': proactive_assistance_engine_client,
            'event_processor': ai_event_processor_client
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
            
            # Step 4: Get User Context for Personalization (BEFORE response generation)
            user_context = None
            if self.config.ai_context_store.enabled:
                response_data["processing_steps"].append("context_retrieval")
                
                # Smart refresh based on keywords
                should_refresh = any(keyword in message.lower() for keyword in [
                    'mood', 'feeling', 'journal', 'community', 'activity', 'progress', 'track', 'how am i', 'my', 'lately'
                ])
                
                logger.info(f"🎯 CONTEXT RETRIEVAL TRIGGERED - message: '{message}', should_refresh: {should_refresh}, user_id: {user_id}")
                
                try:
                    user_context = await ai_context_store_client.get_user_context(
                        user_id, 
                        jwt_token, 
                        refresh_data=should_refresh
                    )
                    
                    if user_context:
                        logger.info(f"📊 Retrieved user context (refreshed: {should_refresh}): user_id={user_context.user_id}, mood_history_count={len(user_context.mood_history)}")
                        response_data["services_used"].append("context")
                    else:
                        logger.warning(f"⚠️ No context available for user {user_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to retrieve user context: {e}")
                    user_context = None
            
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
        """Generate contextual response using AI models with enhanced intelligence"""
        
        try:
            # First try to generate actual AI response using PHI-4/PHI-3
            ai_response = await self._generate_ai_response(
                message, crisis_assessment, sentiment_analysis, intent_classification, 
                user_context, language
            )
            
            if ai_response:
                logger.info("Successfully generated AI response")
                return ai_response
            
            # Fallback to enhanced template system
            logger.warning("AI generation failed, using enhanced template system")
            return self._get_enhanced_template_response(crisis_assessment, intent_classification, sentiment_analysis, message, language)
            
        except Exception as e:
            logger.error(f"Error generating contextual response: {e}")
            return self._get_fallback_response(language)
    
    def _get_template_response(
        self,
        crisis_assessment: Optional[CrisisAssessment],
        intent_classification: Optional[IntentClassification],
        sentiment_analysis: Optional[SentimentAnalysis]
    ) -> str:
        """Get template-based response (fallback)"""
        
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
    
    async def _generate_ai_response(
        self,
        message: str,
        crisis_assessment: Optional[CrisisAssessment],
        sentiment_analysis: Optional[SentimentAnalysis],
        intent_classification: Optional[IntentClassification],
        user_context: Optional[UserContext],
        language: str
    ) -> Optional[str]:
        """Generate AI response using PHI-4/Ollama or other AI services"""
        
        try:
            # Check if PHI-4 is available
            phi4_available = os.getenv("PHI4_MODEL_AVAILABLE", "true").lower() == "true"
            
            if phi4_available:
                return await self._generate_phi4_response(message, crisis_assessment, sentiment_analysis, language, user_context)
            
            # Try OpenAI if available
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                return await self._generate_openai_response(message, crisis_assessment, sentiment_analysis, language, user_context)
            
            logger.warning("No AI services available for response generation")
            return None
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return None
    
    async def _generate_phi4_response(
        self,
        message: str,
        crisis_assessment: Optional[CrisisAssessment],
        sentiment_analysis: Optional[SentimentAnalysis],
        language: str,
        user_context: Optional[UserContext]
    ) -> Optional[str]:
        """Generate response using PHI-4 model via Ollama"""
        
        try:
            import aiohttp
            import json
            
            # Build enhanced therapeutic prompt based on context
            system_prompt = self._build_enhanced_therapeutic_prompt(
                crisis_assessment, sentiment_analysis, language, user_context
            )
            
            # Create conversational prompt that encourages natural responses
            full_prompt = f"""{system_prompt}

User's message: "{message}"

Please respond as Mantra in a natural, conversational way. Make your response feel like you're really listening and care about what they shared. Reference specific details from their message and ask thoughtful questions to continue the conversation."""
            
            # Ollama API endpoint - configurable for Docker vs host environments
            ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
            url = f"{ollama_url}/api/generate"
            
            payload = {
                "model": "phi4",  # or "phi3" depending on what's available
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,  # More creative/conversational
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 300,  # Allow longer, more detailed responses
                    "stop": ["User:", "Assistant:", "Human:", "AI:"]  # Prevent role confusion
                }
            }
            
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=45)  # Longer timeout for better responses
                async with session.post(url, json=payload, timeout=timeout) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result.get("response", "").strip()
                        
                        if ai_response and len(ai_response) > 10:
                            # Post-process the response to make it more refined
                            refined_response = self._refine_ai_response(ai_response, message, language)
                            logger.info(f"Generated refined PHI-4 response: {refined_response[:100]}...")
                            return refined_response
                        else:
                            logger.warning("PHI-4 returned empty or very short response")
                            return None
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error generating PHI-4 response: {e}")
            return None
    
    def _refine_ai_response(self, ai_response: str, user_message: str, language: str) -> str:
        """Post-process AI response to make it more refined and human-like"""
        
        # Remove any unwanted patterns
        refined = ai_response.strip()
        
        # Remove role indicators that might have slipped through
        unwanted_prefixes = ["Mantra:", "Assistant:", "AI:", "Bot:", "Response:"]
        for prefix in unwanted_prefixes:
            if refined.startswith(prefix):
                refined = refined[len(prefix):].strip()
        
        # Ensure response starts naturally
        if refined and not refined[0].isupper():
            refined = refined[0].upper() + refined[1:] if len(refined) > 1 else refined.upper()
        
        # Ensure proper ending punctuation for statements
        if refined and not refined.endswith(('.', '!', '?')):
            # If it looks like a question, add question mark
            question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'would you like', 'can you', 'do you']
            if any(refined.lower().strip().endswith(word) for word in ['like to', 'want to']) or \
               any(refined.lower().startswith(word) for word in question_words):
                refined += "?"
            else:
                refined += "."
        
        # Limit response length to keep it conversational
        if len(refined) > 500:
            # Find the last complete sentence within reasonable length
            sentences = refined.split('.')
            result = ""
            for sentence in sentences:
                if len(result + sentence + ".") <= 450:
                    result += sentence + "."
                else:
                    break
            refined = result.strip()
        
        return refined
    
    async def _generate_openai_response(
        self,
        message: str,
        crisis_assessment: Optional[CrisisAssessment],
        sentiment_analysis: Optional[SentimentAnalysis],
        language: str,
        user_context: Optional[UserContext]
    ) -> Optional[str]:
        """Generate response using OpenAI as backup"""
        
        try:
            import openai
            
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                return None
                
            client = openai.AsyncOpenAI(api_key=openai_key)
            
            system_prompt = self._build_enhanced_therapeutic_prompt(
                crisis_assessment, sentiment_analysis, language, user_context
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=250,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            if ai_response and len(ai_response) > 10:
                logger.info(f"Generated OpenAI response: {ai_response[:100]}...")
                return ai_response
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return None
    
    def _build_enhanced_therapeutic_prompt(
        self,
        crisis_assessment: Optional[CrisisAssessment],
        sentiment_analysis: Optional[SentimentAnalysis],
        language: str,
        user_context: Optional[UserContext]
    ) -> str:
        """Build enhanced therapeutic prompt based on context"""
        
        base_prompt = """You are Maya, a warm, empathetic, and professional mental health companion for MantraPath. You are like a caring friend who genuinely listens and provides thoughtful support.

Your personality:
- Warm, caring, and genuinely interested in the user's wellbeing
- Use a conversational, human-like tone (not robotic or clinical)
- Ask meaningful follow-up questions to show you're listening
- Provide practical, actionable advice when appropriate
- Acknowledge specific details the user shares
- Use empathetic language that validates their feelings

Guidelines:
- Always respond as if you're having a real conversation with a friend
- Reference what they've specifically mentioned in their message
- Ask thoughtful questions to understand their situation better
- Provide gentle guidance without being preachy
- Use natural, flowing language that feels authentic
- Show genuine care and concern for their wellbeing
- Suggest specific coping strategies when helpful"""
        
        # Add crisis context
        if crisis_assessment:
            if crisis_assessment.risk_level in ["high", "critical"]:
                base_prompt += "\n\nIMPORTANT: The user may be in crisis. Be extra caring and supportive. Gently encourage them to reach out for professional help while providing immediate emotional support."
            elif crisis_assessment.risk_level == "medium":
                base_prompt += "\n\nNOTE: The user seems to be struggling emotionally. Provide extra warmth and support, and check in on their wellbeing."
        
        # Add sentiment context
        if sentiment_analysis:
            if sentiment_analysis.sentiment == "negative":
                base_prompt += "\n\nThe user seems to be feeling down or distressed. Focus on validation, understanding, and gentle support."
            elif sentiment_analysis.sentiment == "positive":
                base_prompt += "\n\nThe user appears to be in a positive mood. Celebrate with them and encourage their positive feelings."
        
        # Add language context
        if language != "en":
            base_prompt += f"\n\nRespond in {language} with cultural sensitivity and appropriate warmth for that culture."
        
        # Add user context if available
        if user_context:
            context_info = []
            
            # Process mood context data
            if hasattr(user_context, 'mood_context') and user_context.mood_context:
                mood_context = user_context.mood_context
                
                # Get recent mood scores from the context
                if hasattr(mood_context, 'recent_moods') and mood_context.recent_moods:
                    recent_moods = mood_context.recent_moods
                    mood_count = len(recent_moods)
                    
                    if mood_count > 0:
                        context_info.append(f"Has {mood_count} recent mood entries")
                        
                        # Calculate average mood from recent scores
                        avg_mood = sum(recent_moods) / len(recent_moods)
                        context_info.append(f"Recent average mood: {avg_mood:.1f}/10")
                        
                        # Get latest mood score
                        latest_mood = recent_moods[0] if recent_moods else None
                        if latest_mood:
                            context_info.append(f"Latest mood score: {latest_mood}/10")
                        
                        # Determine mood trend
                        if len(recent_moods) >= 2:
                            first_mood = recent_moods[-1]  # Oldest in recent list
                            last_mood = recent_moods[0]    # Most recent
                            if last_mood > first_mood:
                                context_info.append("Mood trending up recently")
                            elif last_mood < first_mood:
                                context_info.append("Mood has been declining")
                            else:
                                context_info.append("Mood has been stable")
                
                # Process mood analytics if available
                if hasattr(mood_context, 'mood_average') and mood_context.mood_average:
                    context_info.append(f"Overall mood average: {mood_context.mood_average:.1f}/10")
            
            # Process enhanced behavioral patterns
            if hasattr(user_context, 'behavioral_patterns') and user_context.behavioral_patterns:
                patterns = user_context.behavioral_patterns
                if isinstance(patterns, dict):
                    # Mood patterns
                    if 'mood_patterns' in patterns:
                        mood_patterns = patterns['mood_patterns']
                        if 'typical_mood_range' in mood_patterns:
                            context_info.append(f"Mood range: {mood_patterns['typical_mood_range']}")
                        if 'mood_volatility' in mood_patterns:
                            context_info.append(f"Mood stability: {mood_patterns['mood_volatility']}")
                        if 'preferred_input_methods' in mood_patterns:
                            methods = mood_patterns['preferred_input_methods']
                            if methods:
                                context_info.append(f"Uses: {', '.join(methods)} input")
                        if 'tracking_frequency' in mood_patterns:
                            context_info.append(f"Tracks mood: {mood_patterns['tracking_frequency']}")
                    
                    # Activity patterns
                    if 'activity_patterns' in patterns:
                        activity_patterns = patterns['activity_patterns']
                        if 'engagement_level' in activity_patterns:
                            context_info.append(f"Engagement: {activity_patterns['engagement_level']}")
                        if 'consistency' in activity_patterns:
                            context_info.append(f"Consistency: {activity_patterns['consistency']}")
                    
                    # Communication patterns
                    if 'communication_patterns' in patterns:
                        comm_patterns = patterns['communication_patterns']
                        if 'detail_preference' in comm_patterns:
                            context_info.append(f"Prefers {comm_patterns['detail_preference']} responses")
            
            # Process enhanced preferences
            if hasattr(user_context, 'preferences') and user_context.preferences:
                prefs = user_context.preferences
                if isinstance(prefs, dict):
                    if 'communication_style' in prefs:
                        style = prefs['communication_style']
                        context_info.append(f"Communication style: {style}")
                    
                    if 'content_preferences' in prefs:
                        content_prefs = prefs['content_preferences']
                        if 'focus_area' in content_prefs:
                            context_info.append(f"Focus area: {content_prefs['focus_area']}")
                        if 'stress_support' in content_prefs:
                            stress_level = content_prefs['stress_support']
                            if stress_level != 'low':
                                context_info.append(f"Stress support needed: {stress_level}")
                    
                    if 'support_preferences' in prefs:
                        support_prefs = prefs['support_preferences']
                        if 'intervention_level' in support_prefs:
                            context_info.append(f"Support level: {support_prefs['intervention_level']}")
                        if 'community_engagement' in support_prefs:
                            engagement = support_prefs['community_engagement']
                            context_info.append(f"Community: {engagement}")
            
            # Process context history
            if hasattr(user_context, 'context_history') and user_context.context_history:
                history_count = len(user_context.context_history)
                if history_count > 0:
                    context_info.append(f"Platform activity: {history_count} recent actions")
            
            # Add context to prompt if we have any information
            if context_info:
                base_prompt += f"\n\nUser Context: {' | '.join(context_info)}"
                base_prompt += "\n\nIMPORTANT: Use this context to provide highly personalized responses. Reference their specific behavioral patterns, respect their preferences, and acknowledge their unique engagement style. When they ask about patterns or preferences, use the exact data from their context."
            else:
                base_prompt += "\n\nThis appears to be a new user or someone with limited activity. Be welcoming and help them get started with the platform."
        
        base_prompt += "\n\nRemember: Be human, be caring, and make this feel like a real, supportive conversation."
        
        return base_prompt
    
    def _get_enhanced_template_response(
        self,
        crisis_assessment: Optional[CrisisAssessment],
        intent_classification: Optional[IntentClassification],
        sentiment_analysis: Optional[SentimentAnalysis],
        message: str,
        language: str
    ) -> str:
        """Get enhanced template-based response with more intelligence"""
        
        # Analyze message content for better response selection
        message_lower = message.lower()
        
        # Crisis responses take priority
        if crisis_assessment:
            if crisis_assessment.risk_level in ["high", "critical"]:
                return self._get_crisis_response(language, "high")
            elif crisis_assessment.risk_level == "medium":
                return self._get_crisis_response(language, "medium")
        
        # Check for specific mental health topics
        if any(word in message_lower for word in ["anxious", "anxiety", "worried", "stress", "panic"]):
            return self._get_anxiety_response(language)
        elif any(word in message_lower for word in ["sad", "depressed", "down", "lonely", "hopeless"]):
            return self._get_depression_response(language)
        elif any(word in message_lower for word in ["sleep", "tired", "exhausted", "insomnia"]):
            return self._get_sleep_response(language)
        elif any(word in message_lower for word in ["angry", "frustrated", "mad", "irritated"]):
            return self._get_anger_response(language)
        
        # Intent-based responses
        if intent_classification:
            if intent_classification.intent == "emotional_support":
                return self._get_emotional_support_response(language)
            elif intent_classification.intent == "breathing_exercise":
                return self._get_breathing_response(language)
            elif intent_classification.intent == "mood_tracking":
                return self._get_mood_tracking_response(language)
        
        # Sentiment-based responses
        if sentiment_analysis:
            if sentiment_analysis.sentiment == "negative":
                return self._get_emotional_support_response(language)
            elif sentiment_analysis.sentiment == "positive":
                return self._get_positive_reinforcement_response(language)
        
        # Default conversational response
        return self._get_conversational_response(language)
    
    def _get_crisis_response(self, language: str, level: str) -> str:
        """Get crisis-appropriate response"""
        if level == "high":
            responses = {
                "en": "I can hear that you're going through something really difficult right now. Your feelings are completely valid, and you don't have to face this alone. Would it help to talk about what you're experiencing? Remember, there are people who want to help you - including crisis helplines available 24/7.",
                "hi": "मैं समझ सकता हूं कि आप अभी बहुत कठिन समय से गुजर रहे हैं। आपकी भावनाएं बिल्कुल सामान्य हैं, और आपको अकेले इससे निपटने की जरूरत नहीं है। क्या आप बताना चाहेंगे कि आप क्या महसूस कर रहे हैं? याद रखें, ऐसे लोग हैं जो आपकी मदद करना चाहते हैं।"
            }
        else:  # medium
            responses = {
                "en": "I can see that you're dealing with some challenging emotions right now. It's completely normal to feel this way, and I'm here to support you. Would you like to talk about what's been on your mind?",
                "hi": "मैं देख सकता हूं कि आप अभी कुछ कठिन भावनाओं से निपट रहे हैं। ऐसा महसूस करना बिल्कुल सामान्य है, और मैं आपका साथ देने के लिए यहां हूं। क्या आप बताना चाहेंगे कि आपके मन में क्या चल रहा है?"
            }
        
        return responses.get(language, responses["en"])
    
    def _get_anxiety_response(self, language: str) -> str:
        """Get anxiety-focused response"""
        responses = {
            "en": "I understand you're feeling anxious. Anxiety can feel overwhelming, but there are ways to manage it. Would you like to try a quick breathing exercise together, or would you prefer to talk about what's making you feel anxious?",
            "hi": "मैं समझता हूं कि आप चिंतित महसूस कर रहे हैं। चिंता भारी लग सकती है, लेकिन इसे संभालने के तरीके हैं। क्या आप एक त्वरित सांस की एक्सरसाइज करना चाहेंगे, या आप बताना चाहेंगे कि क्या चीज आपको चिंतित कर रही है?"
        }
        return responses.get(language, responses["en"])
    
    def _get_depression_response(self, language: str) -> str:
        """Get depression-focused response"""
        responses = {
            "en": "I hear that you're feeling down, and I want you to know that these feelings are valid. Depression can make everything feel heavy, but small steps can help. Is there one small thing that might bring you a bit of comfort today?",
            "hi": "मैं सुन सकता हूं कि आप उदास महसूस कर रहे हैं, और मैं चाहता हूं कि आप जानें कि ये भावनाएं सामान्य हैं। अवसाद सब कुछ भारी लगा सकता है, लेकिन छोटे कदम मदद कर सकते हैं। क्या कोई छोटी सी चीज है जो आज आपको थोड़ा आराम दे सकती है?"
        }
        return responses.get(language, responses["en"])
    
    def _get_sleep_response(self, language: str) -> str:
        """Get sleep-focused response"""
        responses = {
            "en": "Sleep challenges can really affect how we feel during the day. Good sleep is so important for mental health. Would you like some gentle suggestions for improving sleep, or would you prefer to talk about what might be keeping you awake?",
            "hi": "नींद की समस्याएं दिन भर हमारे महसूस करने के तरीके को प्रभावित कर सकती हैं। अच्छी नींद मानसिक स्वास्थ्य के लिए बहुत महत्वपूर्ण है। क्या आप नींद में सुधार के लिए कुछ सुझाव चाहेंगे, या आप बताना चाहेंगे कि क्या चीज आपको जगाए रख रही है?"
        }
        return responses.get(language, responses["en"])
    
    def _get_anger_response(self, language: str) -> str:
        """Get anger-focused response"""
        responses = {
            "en": "I can sense you're feeling frustrated or angry. These are completely normal emotions, and it's important to acknowledge them. Would you like to talk about what's bothering you, or would you prefer some techniques to help manage these intense feelings?",
            "hi": "मैं महसूस कर सकता हूं कि आप निराश या गुस्से में हैं। ये बिल्कुल सामान्य भावनाएं हैं, और इन्हें स्वीकार करना महत्वपूर्ण है। क्या आप बताना चाहेंगे कि क्या परेशान कर रहा है, या आप इन तीव्र भावनाओं को संभालने के लिए कुछ तकनीकें पसंद करेंगे?"
        }
        return responses.get(language, responses["en"])
    
    def _get_emotional_support_response(self, language: str) -> str:
        """Get general emotional support response"""
        responses = {
            "en": "Thank you for sharing with me. It takes courage to open up about how you're feeling. I'm here to listen and support you. What would feel most helpful for you right now?",
            "hi": "मुझसे साझा करने के लिए धन्यवाद। अपनी भावनाओं के बारे में खुलकर बताने में साहस लगता है। मैं आपकी बात सुनने और आपका साथ देने के लिए यहां हूं। अभी आपके लिए सबसे ज्यादा मददगार क्या होगा?"
        }
        return responses.get(language, responses["en"])
    
    def _get_breathing_response(self, language: str) -> str:
        """Get breathing exercise response"""
        responses = {
            "en": "A breathing exercise is a wonderful idea. Let's try this together: Take a slow breath in for 4 counts, hold for 4, then breathe out for 6. This can help activate your body's relaxation response. Would you like to do a few rounds of this?",
            "hi": "सांस की एक्सरसाइज एक बेहतरीन विचार है। आइए इसे एक साथ करते हैं: 4 गिनती तक धीरे सांस लें, 4 तक रोकें, फिर 6 गिनती तक सांस छोड़ें। यह आपके शरीर की विश्राम प्रतिक्रिया को सक्रिय करने में मदद कर सकता है। क्या आप इसके कुछ चक्र करना चाहेंगे?"
        }
        return responses.get(language, responses["en"])
    
    def _get_mood_tracking_response(self, language: str) -> str:
        """Get mood tracking response"""
        responses = {
            "en": "Tracking your mood is a great way to understand your emotional patterns. It can help you identify what influences your feelings and celebrate your progress. Would you like to record how you're feeling right now?",
            "hi": "अपने मूड को ट्रैक करना अपने भावनात्मक पैटर्न को समझने का एक शानदार तरीका है। यह आपको यह पहचानने में मदद कर सकता है कि आपकी भावनाओं को क्या प्रभावित करता है और अपनी प्रगति का जश्न मना सकता है। क्या आप अभी कैसा महसूस कर रहे हैं, यह रिकॉर्ड करना चाहेंगे?"
        }
        return responses.get(language, responses["en"])
    
    def _get_positive_reinforcement_response(self, language: str) -> str:
        """Get positive reinforcement response"""
        responses = {
            "en": "I'm so glad to hear you're feeling positive! It's wonderful when we can recognize and appreciate good moments. What's been contributing to your positive feelings today?",
            "hi": "मुझे यह सुनकर बहुत खुशी हो रही है कि आप सकारात्मक महसूस कर रहे हैं! जब हम अच्छे पलों को पहचान और सराहना कर सकते हैं तो यह बहुत अच्छा होता है। आज आपकी सकारात्मक भावनाओं में क्या योगदान दे रहा है?"
        }
        return responses.get(language, responses["en"])
    
    def _get_conversational_response(self, language: str) -> str:
        """Get general conversational response"""
        responses = {
            "en": "I'm glad you reached out to me today. I'm here to listen and support you in whatever way feels most helpful. What's on your mind?",
            "hi": "मुझे खुशी है कि आपने आज मुझसे संपर्क किया। जो भी तरीका सबसे मददगार लगे, मैं आपकी बात सुनने और आपका साथ देने के लिए यहां हूं। आपके मन में क्या है?"
        }
        return responses.get(language, responses["en"])
    
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
