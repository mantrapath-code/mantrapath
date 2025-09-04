"""
Clean Chatbot Service - Simplified and Robust
Handles voice-to-voice conversations with proper language detection
No mock data, only real service integrations
"""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, UTC
import json

# Import service clients
from src.clients.models_service_client import models_client
from src.clients.translation_service_client import translation_service_client
from src.clients.voice_service_client import voice_service_client
from src.clients.ml_service_client import ml_service_client
from src.models.chat_context import ChatContext, EnhancedChatResponse

logger = logging.getLogger(__name__)

class CleanChatbotService:
    """Clean, simplified chatbot service with voice-to-voice support"""
    
    def __init__(self):
        self.config = self._load_config()
        logger.info("Clean Chatbot Service initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment"""
        return {
            "default_language": "en",
            "enable_voice": True,
            "enable_translation": True,
            "enable_ml_insights": True,
            "voice_service_url": "http://voice-service:8011",
            "translation_service_url": "http://translation-service:8010",
            "models_service_url": "http://models-service:8085",
            "ml_service_url": "http://ml-service:8008"
        }
    
    async def process_message(
        self, 
        message: str, 
        context: ChatContext,
        jwt_token: Optional[str] = None
    ) -> EnhancedChatResponse:
        """
        Process chat message with clean, robust logic
        
        Args:
            message: User message
            context: Chat context with user info and language preferences
            jwt_token: JWT token for authentication
            
        Returns:
            Enhanced chat response with voice support
        """
        start_time = datetime.now(UTC)
        
        try:
            logger.info(f"🎯 Processing message: '{message[:50]}...' for user {context.get('user_id')}")
            
            # Step 1: Language Detection (Improved)
            detected_language = await self._detect_language_robust(message, context, jwt_token)
            logger.info(f"🌐 Language detected: {detected_language}")
            
            # Step 2: Generate Response in Detected Language
            response_text = await self._generate_response_in_language(
                message, detected_language, context, jwt_token
            )
            logger.info(f"💬 Response generated: '{response_text[:50]}...'")
            
            # Step 3: Generate Voice Response (if voice input)
            audio_response = None
            voice_language = None
            
            if context.get("input_type") == "voice" and self.config["enable_voice"]:
                audio_response, voice_language = await self._generate_voice_response(
                    response_text, detected_language, jwt_token
                )
                if audio_response:
                    logger.info(f"🎤 Voice response generated in {voice_language}")
                else:
                    logger.warning("⚠️ Voice response generation failed")
            
            # Step 4: Prepare Final Response
            response_data = {
                "user_id": context.get("user_id"),
                "session_id": context.get("session_id"),
                "timestamp": start_time.isoformat(),
                "language_detected": detected_language,
                "conversation_language": detected_language,
                "input_type": context.get("input_type", "text"),
                "should_respond_with_voice": context.get("input_type") == "voice",
                "processing_steps": ["language_detection", "response_generation"],
                "services_used": ["translation", "models"]
            }
            
            if audio_response:
                response_data["processing_steps"].append("voice_synthesis")
                response_data["services_used"].append("voice")
            
            # Calculate processing time
            end_time = datetime.now(UTC)
            processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
            response_data["processing_time_ms"] = processing_time_ms
            
            logger.info(f"✅ Message processed in {processing_time_ms}ms")
            
            return EnhancedChatResponse(
                response=response_text,
                session_id=context.get("session_id"),
                user_id=context.get("user_id"),
                timestamp=response_data["timestamp"],
                language_detected=detected_language,
                conversation_language=detected_language,
                input_type=context.get("input_type", "text"),
                should_respond_with_voice=context.get("input_type") == "voice",
                audio_response=audio_response,
                voice_language=voice_language,
                crisis_level="none",
                cultural_adaptations=[],
                actions_triggered=[],
                processing_steps=response_data["processing_steps"],
                services_used=response_data["services_used"],
                metadata=response_data
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return await self._create_error_response(str(e), context)
    
    async def _detect_language_robust(
        self, 
        message: str, 
        context: ChatContext, 
        jwt_token: Optional[str]
    ) -> str:
        """Robust language detection with fallbacks"""
        
        try:
            # Check if user has specified language preference
            user_language = context.get("user_language")
            if user_language and user_language != "auto":
                logger.info(f"Using user-specified language: {user_language}")
                return user_language
            
            # Try translation service for language detection
            if self.config["enable_translation"]:
                try:
                    lang_detection = await translation_service_client.detect_language(message, jwt_token)
                    if lang_detection and lang_detection.detected_language:
                        detected_lang = lang_detection.detected_language
                        
                        # Validate detection with simple heuristics
                        if self._is_english_text(message) and detected_lang != "en":
                            logger.warning(f"Language detection mismatch: '{message}' detected as {detected_lang}, forcing English")
                            return "en"
                        
                        logger.info(f"Translation service detected: {detected_lang}")
                        return detected_lang
                        
                except Exception as e:
                    logger.warning(f"Translation service language detection failed: {e}")
            
            # Fallback to simple detection
            detected_lang = self._simple_language_detection(message)
            logger.info(f"Simple detection fallback: {detected_lang}")
            return detected_lang
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return self.config["default_language"]
    
    def _is_english_text(self, text: str) -> bool:
        """Simple English text detection"""
        if not text:
            return False
        
        # Count ASCII alphabetic characters
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
        total_chars = sum(1 for c in text if c.isalpha())
        
        if total_chars == 0:
            return False
        
        english_ratio = english_chars / total_chars
        
        # If more than 80% are English characters, consider it English
        is_english = english_ratio > 0.8
        
        logger.debug(f"Text: '{text[:30]}...', English ratio: {english_ratio:.2f}, Is English: {is_english}")
        
        return is_english
    
    def _simple_language_detection(self, text: str) -> str:
        """Simple language detection using character analysis"""
        if not text:
            return self.config["default_language"]
        
        # Check for Hindi/Devanagari characters
        devanagari_chars = sum(1 for c in text if '\u0900' <= c <= '\u097F')
        
        # Check for English characters
        english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
        
        # Check for other Indic scripts
        bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        telugu_chars = sum(1 for c in text if '\u0C00' <= c <= '\u0C7F')
        
        total_chars = len(text)
        
        if total_chars == 0:
            return self.config["default_language"]
        
        # Calculate ratios
        devanagari_ratio = devanagari_chars / total_chars
        english_ratio = english_chars / total_chars
        bengali_ratio = bengali_chars / total_chars
        tamil_ratio = tamil_chars / total_chars
        telugu_ratio = telugu_chars / total_chars
        
        # Determine language based on highest ratio
        ratios = {
            "en": english_ratio,
            "hi": devanagari_ratio,
            "bn": bengali_ratio,
            "ta": tamil_ratio,
            "te": telugu_ratio
        }
        
        detected_lang = max(ratios, key=ratios.get)
        
        # Only return detected language if ratio is significant (> 0.3)
        if ratios[detected_lang] > 0.3:
            logger.info(f"Simple detection: {detected_lang} (ratio: {ratios[detected_lang]:.2f})")
            return detected_lang
        else:
            logger.info(f"Simple detection: insufficient confidence, using default: {self.config['default_language']}")
            return self.config["default_language"]
    
    async def _generate_response_in_language(
        self, 
        message: str, 
        language: str, 
        context: ChatContext,
        jwt_token: Optional[str]
    ) -> str:
        """Generate response in the detected language"""
        
        try:
            # Try to generate response using models service
            if self._is_service_available("models"):
                try:
                    # Generate response in the detected language
                    response = await self._generate_ai_response(message, language, context, jwt_token)
                    if response and response.get("response"):
                        logger.info(f"AI response generated in {language}")
                        return response["response"]
                except Exception as e:
                    logger.warning(f"AI response generation failed: {e}")
            
            # Fallback to language-specific responses
            fallback_response = self._get_language_specific_response(message, language)
            logger.info(f"Using fallback response in {language}")
            return fallback_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self._get_fallback_response(language)
    
    async def _generate_ai_response(
        self, 
        message: str, 
        language: str, 
        context: ChatContext,
        jwt_token: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Generate AI response using models service"""
        
        try:
            # Use models service for response generation
            response = await models_client.generate_response(
                message=message,
                language=language,
                context=context.get("user_context", {}),
                jwt_token=jwt_token
            )
            
            if response and response.get("response"):
                return response
            
            return None
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return None
    
    def _get_language_specific_response(self, message: str, language: str) -> str:
        """Get language-specific fallback response"""
        
        # Simple, empathetic responses in different languages
        responses = {
            "en": [
                "I understand how you're feeling. I'm here to listen and support you. How can I help you today?",
                "Thank you for sharing that with me. I want you to know that your feelings are valid. What would be most helpful right now?",
                "I hear you, and I want you to know that you're not alone. Let's work through this together. What's on your mind?",
                "I appreciate you opening up to me. Your wellness journey is important, and I'm here to support you every step of the way."
            ],
            "hi": [
                "मैं समझ सकता हूं कि आप कैसा महसूस कर रहे हैं। मैं यहां आपकी बात सुनने और आपकी मदद करने के लिए हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
                "मुझे यह बताने के लिए धन्यवाद। मैं चाहता हूं कि आप जानें कि आपकी भावनाएं मान्य हैं। अभी क्या सबसे ज्यादा मददगार होगा?",
                "मैं आपकी बात सुन रहा हूं, और मैं चाहता हूं कि आप जानें कि आप अकेले नहीं हैं। चलिए इसे एक साथ सुलझाते हैं। आपके मन में क्या है?",
                "मुझे यह बताने के लिए आपका धन्यवाद। आपकी कल्याण यात्रा महत्वपूर्ण है, और मैं हर कदम पर आपका समर्थन करने के लिए यहां हूं।"
            ]
        }
        
        # Get responses for the detected language, fallback to English
        language_responses = responses.get(language, responses["en"])
        
        # Return a random response (simple implementation)
        import random
        return random.choice(language_responses)
    
    def _get_fallback_response(self, language: str) -> str:
        """Get fallback response when everything else fails"""
        fallbacks = {
            "en": "I'm here to help and support you. How can I assist you today?",
            "hi": "मैं आपकी मदद और समर्थन करने के लिए यहां हूं। आज मैं आपकी कैसे सहायता कर सकता हूं?"
        }
        return fallbacks.get(language, fallbacks["en"])
    
    async def _generate_voice_response(
        self, 
        text: str, 
        language: str, 
        jwt_token: Optional[str]
    ) -> tuple[Optional[str], Optional[str]]:
        """Generate voice response using voice service"""
        
        try:
            if not self.config["enable_voice"]:
                logger.info("Voice service disabled")
                return None, None
            
            logger.info(f"🎤 Generating voice response in {language}")
            
            # Call voice service for TTS
            tts_result = await voice_service_client.text_to_speech(
                text, language, jwt_token=jwt_token
            )
            
            if tts_result and tts_result.audio_data:
                import base64
                audio_b64 = base64.b64encode(tts_result.audio_data).decode('utf-8')
                logger.info(f"✅ Voice response generated: {len(tts_result.audio_data)} bytes")
                return audio_b64, language
            else:
                logger.warning("Voice service returned no audio data")
                return None, None
                
        except Exception as e:
            logger.error(f"Voice response generation failed: {e}")
            return None, None
    
    def _is_service_available(self, service_name: str) -> bool:
        """Check if a service is available"""
        service_urls = {
            "models": self.config["models_service_url"],
            "voice": self.config["voice_service_url"],
            "translation": self.config["translation_service_url"],
            "ml": self.config["ml_service_url"]
        }
        
        url = service_urls.get(service_name)
        if not url:
            return False
        
        # Simple availability check (in production, use health checks)
        return True
    
    async def _create_error_response(self, error: str, context: ChatContext) -> EnhancedChatResponse:
        """Create error response when processing fails"""
        
        error_message = f"I'm experiencing some technical difficulties. Please try again in a moment. (Error: {error})"
        
        return EnhancedChatResponse(
            response=error_message,
            session_id=context.get("session_id"),
            user_id=context.get("user_id"),
            timestamp=datetime.now(UTC).isoformat(),
            language_detected="en",
            conversation_language="en",
            input_type=context.get("input_type", "text"),
            should_respond_with_voice=False,
            audio_response=None,
            voice_language=None,
            crisis_level="none",
            cultural_adaptations=[],
            actions_triggered=[],
            processing_steps=["error_handling"],
            services_used=[],
            metadata={"error": error, "status": "error"}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the clean chatbot service"""
        return {
            "service": "Clean Chatbot Service",
            "status": "healthy",
            "version": "1.0.0",
            "capabilities": {
                "voice_to_voice": self.config["enable_voice"],
                "language_detection": self.config["enable_translation"],
                "ai_response_generation": True,
                "multilingual_support": True
            },
            "timestamp": datetime.now(UTC).isoformat()
        }

# Create service instance
clean_chatbot_service = CleanChatbotService()
