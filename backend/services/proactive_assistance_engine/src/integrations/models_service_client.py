"""
Models Service Client for Proactive Assistance Engine
Extended client with proactive assistance specific workflows.
"""

import asyncio
from typing import Dict, Any, List, Optional
import structlog
import httpx

logger = structlog.get_logger(__name__)

class ModelsServiceError(Exception):
    """Exception for Models Service errors"""
    pass

class ProactiveModelsServiceClient:
    """Models Service client for Proactive Assistance Engine workflows"""
    
    def __init__(self, base_url: str = "http://models-service:8080"):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
        self.logger = logger.bind(service="proactive_assistance_models_client")
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def check_health(self) -> bool:
        """Check if Models Service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            self.logger.warning("Models Service health check failed", error=str(e))
            return False

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "auto",
        model: str = "whisper_base"
    ) -> Dict[str, Any]:
        """Transcribe audio to text using Models Service STT"""
        try:
            files = {"audio": ("audio.wav", audio_data, "audio/wav")}
            data = {"language": language, "model": model}
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/stt/transcribe",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error("STT transcription failed", error=str(e))
            raise ModelsServiceError(f"STT failed: {e}")

    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        voice: str = "default",
        model: str = "espeak"
    ) -> bytes:
        """Synthesize speech from text using Models Service TTS"""
        try:
            data = {
                "text": text,
                "language": language,
                "voice": voice,
                "model": model
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/tts/synthesize",
                json=data
            )
            response.raise_for_status()
            return response.content
            
        except Exception as e:
            self.logger.error("TTS synthesis failed", error=str(e))
            raise ModelsServiceError(f"TTS failed: {e}")

    async def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        engine: str = "default"
    ) -> Dict[str, Any]:
        """Translate text using Models Service NLP"""
        try:
            data = {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "engine": engine
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/nlp/translate",
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error("Translation failed", error=str(e))
            raise ModelsServiceError(f"Translation failed: {e}")

    async def analyze_sentiment(
        self,
        text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Analyze sentiment using Models Service NLP"""
        try:
            data = {"text": text, "language": language}
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/nlp/sentiment",
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error("Sentiment analysis failed", error=str(e))
            raise ModelsServiceError(f"Sentiment analysis failed: {e}")

    async def get_embeddings(
        self,
        text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Get text embeddings using Models Service NLP"""
        try:
            data = {"text": text, "language": language}
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/nlp/embeddings",
                json=data
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            self.logger.error("Embeddings generation failed", error=str(e))
            raise ModelsServiceError(f"Embeddings failed: {e}")
        
    async def process_voice_assistance_request(
        self,
        audio_data: bytes,
        user_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process voice assistance request with full AI pipeline
        
        Args:
            audio_data: Audio data from user
            user_id: User identifier
            context: User context (language preferences, cultural profile, etc.)
            
        Returns:
            Comprehensive analysis including transcription, sentiment, and recommendations
        """
        try:
            self.logger.info("Processing voice assistance request", user_id=user_id)
            
            # Get user preferences
            preferred_language = context.get("preferred_language", "auto")
            cultural_profile = context.get("cultural_profile", "neutral")
            
            # Step 1: Transcribe audio to text
            self.logger.debug("Starting STT transcription", 
                            language=preferred_language, user_id=user_id)
            
            transcription = await self.transcribe_audio(
                audio_data, 
                language=preferred_language,
                model="whisper_base"
            )
            
            transcribed_text = transcription.get("text", "")
            detected_language = transcription.get("detected_language", preferred_language)
            
            self.logger.info("STT transcription completed",
                           text_length=len(transcribed_text),
                           detected_language=detected_language,
                           user_id=user_id)
            
            # Step 2: Analyze sentiment of the request
            self.logger.debug("Starting sentiment analysis", user_id=user_id)
            
            try:
                sentiment = await self.analyze_sentiment(
                    transcribed_text,
                    language=detected_language
                )
                self.logger.info("Sentiment analysis completed",
                               sentiment=sentiment.get("sentiment"),
                               confidence=sentiment.get("confidence"),
                               user_id=user_id)
            except Exception as e:
                self.logger.warning("Sentiment analysis failed, using default",
                                  error=str(e), user_id=user_id)
                sentiment = {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "error": str(e)
                }
            
            # Step 3: Generate embeddings for contextual matching (if needed)
            embeddings = None
            if len(transcribed_text) > 10:  # Only for meaningful text
                try:
                    embeddings_result = await self.get_embeddings(
                        transcribed_text,
                        language=detected_language
                    )
                    embeddings = embeddings_result.get("embeddings")
                    self.logger.debug("Embeddings generated",
                                    embedding_dim=len(embeddings) if embeddings else 0,
                                    user_id=user_id)
                except Exception as e:
                    self.logger.warning("Embeddings generation failed",
                                      error=str(e), user_id=user_id)
            
            # Compile comprehensive result
            result = {
                "user_id": user_id,
                "request_analysis": {
                    "transcription": {
                        "text": transcribed_text,
                        "confidence": transcription.get("confidence", 0.0),
                        "detected_language": detected_language,
                        "processing_time": transcription.get("processing_time", 0.0)
                    },
                    "sentiment": sentiment,
                    "embeddings": embeddings,
                    "context": context
                },
                "assistance_needs": self._analyze_assistance_needs(
                    transcribed_text, sentiment, context
                ),
                "recommendations": self._generate_response_recommendations(
                    transcribed_text, sentiment, context, detected_language
                )
            }
            
            self.logger.info("Voice assistance request processing completed",
                           user_id=user_id,
                           has_transcription=bool(transcribed_text),
                           sentiment=sentiment.get("sentiment"),
                           needs_assistance=result["assistance_needs"]["requires_intervention"])
            
            return result
            
        except Exception as e:
            self.logger.error("Voice assistance request processing failed",
                            user_id=user_id, error=str(e))
            raise ModelsServiceError(f"Voice assistance processing failed: {e}")

    async def generate_multilingual_response(
        self,
        response_text: str,
        target_language: str,
        user_context: Dict[str, Any],
        voice_enabled: bool = True,
        cultural_adaptation: bool = True
    ) -> Dict[str, Any]:
        """
        Generate culturally appropriate multilingual assistance response
        
        Args:
            response_text: Base response text (usually in English)
            target_language: User's preferred language
            user_context: Cultural and personal context
            voice_enabled: Whether to generate audio response
            cultural_adaptation: Whether to apply cultural adaptations
            
        Returns:
            Complete response package (text, translated text, audio)
        """
        try:
            self.logger.info("Generating multilingual response",
                           target_language=target_language,
                           voice_enabled=voice_enabled,
                           cultural_adaptation=cultural_adaptation)
            
            result = {
                "original_text": response_text,
                "target_language": target_language,
                "cultural_adaptation": cultural_adaptation
            }
            
            # Step 1: Apply cultural adaptations to the text if needed
            adapted_text = response_text
            if cultural_adaptation:
                adapted_text = self._apply_cultural_adaptations(
                    response_text, user_context
                )
                result["culturally_adapted_text"] = adapted_text
            
            # Step 2: Translate if target language is not English
            if target_language != "en" and target_language != "auto":
                self.logger.debug("Starting translation",
                                target_language=target_language)
                
                try:
                    translation = await self.translate_text(
                        adapted_text,
                        source_lang="en",
                        target_lang=target_language
                    )
                    
                    translated_text = translation.get("translated_text", adapted_text)
                    result["translated_text"] = translated_text
                    result["translation_confidence"] = translation.get("confidence", 0.0)
                    
                    self.logger.info("Translation completed",
                                   target_language=target_language,
                                   confidence=result["translation_confidence"])
                    
                except Exception as e:
                    self.logger.warning("Translation failed, using original text",
                                      target_language=target_language, error=str(e))
                    result["translated_text"] = adapted_text
                    result["translation_error"] = str(e)
            else:
                result["translated_text"] = adapted_text
            
            # Use translated text for final response
            final_text = result["translated_text"]
            result["final_text"] = final_text
            
            # Step 3: Generate voice response if requested
            if voice_enabled and final_text:
                self.logger.debug("Starting TTS synthesis",
                                target_language=target_language)
                
                try:
                    audio_data = await self.synthesize_speech(
                        final_text,
                        language=target_language,
                        model="espeak"  # Using espeak for reliability
                    )
                    
                    result["audio_data"] = audio_data
                    result["audio_format"] = "wav"
                    result["audio_size"] = len(audio_data)
                    
                    self.logger.info("TTS synthesis completed",
                                   target_language=target_language,
                                   audio_size=len(audio_data))
                    
                except Exception as e:
                    self.logger.warning("TTS synthesis failed",
                                      target_language=target_language, error=str(e))
                    result["tts_error"] = str(e)
            
            self.logger.info("Multilingual response generation completed",
                           target_language=target_language,
                           has_translation=("translated_text" in result),
                           has_audio=(voice_enabled and "audio_data" in result))
            
            return result
            
        except Exception as e:
            self.logger.error("Multilingual response generation failed",
                            target_language=target_language, error=str(e))
            raise ModelsServiceError(f"Multilingual response generation failed: {e}")

    async def analyze_user_content_sentiment(
        self,
        content_history: List[str],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze sentiment trends from user's recent content (journal entries, mood logs, etc.)
        
        Args:
            content_history: List of recent user content (texts)
            user_context: User context for interpretation
            
        Returns:
            Sentiment trend analysis and intervention recommendations
        """
        try:
            self.logger.info("Analyzing user content sentiment",
                           content_count=len(content_history))
            
            if not content_history:
                return {
                    "sentiment_trend": "insufficient_data",
                    "requires_intervention": False,
                    "confidence": 0.0
                }
            
            # Analyze each piece of content
            sentiment_results = []
            for i, content in enumerate(content_history):
                if not content or len(content.strip()) < 3:
                    continue
                    
                try:
                    sentiment = await self.analyze_sentiment(
                        content,
                        language=user_context.get("preferred_language", "en")
                    )
                    sentiment_results.append({
                        "content_index": i,
                        "sentiment": sentiment.get("sentiment", "neutral"),
                        "confidence": sentiment.get("confidence", 0.0),
                        "scores": sentiment.get("scores", {})
                    })
                except Exception as e:
                    self.logger.warning(f"Sentiment analysis failed for content {i}",
                                      error=str(e))
            
            if not sentiment_results:
                return {
                    "sentiment_trend": "analysis_failed",
                    "requires_intervention": False,
                    "confidence": 0.0
                }
            
            # Analyze trends
            trend_analysis = self._analyze_sentiment_trends(sentiment_results)
            
            self.logger.info("User content sentiment analysis completed",
                           analyzed_items=len(sentiment_results),
                           trend=trend_analysis["sentiment_trend"],
                           requires_intervention=trend_analysis["requires_intervention"])
            
            return trend_analysis
            
        except Exception as e:
            self.logger.error("User content sentiment analysis failed", error=str(e))
            raise ModelsServiceError(f"Content sentiment analysis failed: {e}")

    def _analyze_assistance_needs(
        self, 
        text: str, 
        sentiment: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze what kind of assistance the user might need"""
        
        # Keywords that might indicate specific needs
        crisis_keywords = ["help", "emergency", "urgent", "crisis", "danger", "hurt", "harm"]
        mood_keywords = ["sad", "depressed", "anxious", "worried", "stressed", "angry"]
        support_keywords = ["lonely", "alone", "support", "talk", "listen", "friend"]
        
        text_lower = text.lower()
        
        # Check for crisis indicators
        has_crisis_indicators = any(keyword in text_lower for keyword in crisis_keywords)
        
        # Check sentiment severity
        sentiment_score = sentiment.get("confidence", 0.0)
        sentiment_type = sentiment.get("sentiment", "neutral")
        
        # Determine intervention level
        requires_immediate_intervention = (
            has_crisis_indicators or 
            (sentiment_type in ["very_negative", "negative"] and sentiment_score > 0.8)
        )
        
        requires_gentle_intervention = (
            any(keyword in text_lower for keyword in mood_keywords + support_keywords) or
            (sentiment_type == "negative" and sentiment_score > 0.6)
        )
        
        return {
            "requires_intervention": requires_immediate_intervention or requires_gentle_intervention,
            "intervention_level": (
                "immediate" if requires_immediate_intervention
                else "gentle" if requires_gentle_intervention
                else "none"
            ),
            "detected_needs": {
                "crisis_support": has_crisis_indicators,
                "mood_support": any(keyword in text_lower for keyword in mood_keywords),
                "social_support": any(keyword in text_lower for keyword in support_keywords),
                "general_assistance": len(text.strip()) > 0
            },
            "confidence": max(sentiment_score, 0.5) if requires_immediate_intervention else sentiment_score
        }

    def _generate_response_recommendations(
        self,
        text: str,
        sentiment: Dict[str, Any],
        context: Dict[str, Any],
        language: str
    ) -> Dict[str, Any]:
        """Generate recommendations for response type and content"""
        
        assistance_needs = self._analyze_assistance_needs(text, sentiment, context)
        
        recommendations = {
            "response_type": "acknowledgment",
            "tone": "supportive",
            "urgency": "normal",
            "suggested_actions": []
        }
        
        if assistance_needs["intervention_level"] == "immediate":
            recommendations.update({
                "response_type": "crisis_intervention",
                "tone": "calm_supportive",
                "urgency": "high",
                "suggested_actions": ["connect_with_counselor", "provide_emergency_resources"]
            })
        elif assistance_needs["intervention_level"] == "gentle":
            recommendations.update({
                "response_type": "supportive_guidance",
                "tone": "empathetic",
                "urgency": "medium",
                "suggested_actions": ["mood_check_in", "suggest_coping_strategies"]
            })
        
        # Add cultural considerations
        cultural_profile = context.get("cultural_profile", "neutral")
        if cultural_profile == "collectivist":
            recommendations["cultural_notes"] = "Consider family/community support"
        elif cultural_profile == "individualist":
            recommendations["cultural_notes"] = "Focus on personal coping strategies"
        
        return recommendations

    def _apply_cultural_adaptations(
        self, 
        text: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Apply cultural adaptations to response text"""
        
        cultural_profile = user_context.get("cultural_profile", "neutral")
        
        # Simple cultural adaptations (in a real system, this would be more sophisticated)
        if cultural_profile == "collectivist":
            # Add community/family oriented language
            if "you should" in text.lower():
                text = text.replace("you should", "you and your loved ones might consider")
        elif cultural_profile == "high_context":
            # Use more indirect language
            text = text.replace("You need to", "It might be helpful to")
            text = text.replace("You must", "Perhaps you could")
        
        return text

    def _analyze_sentiment_trends(
        self, 
        sentiment_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze sentiment trends from multiple content pieces"""
        
        if not sentiment_results:
            return {
                "sentiment_trend": "no_data",
                "requires_intervention": False,
                "confidence": 0.0
            }
        
        # Calculate average sentiment scores
        negative_count = len([s for s in sentiment_results if s["sentiment"] in ["negative", "very_negative"]])
        positive_count = len([s for s in sentiment_results if s["sentiment"] in ["positive", "very_positive"]])
        neutral_count = len(sentiment_results) - negative_count - positive_count
        
        total_count = len(sentiment_results)
        negative_ratio = negative_count / total_count
        positive_ratio = positive_count / total_count
        
        # Determine trend
        if negative_ratio > 0.7:
            trend = "concerning_negative"
            requires_intervention = True
        elif negative_ratio > 0.5:
            trend = "moderately_negative"
            requires_intervention = True
        elif positive_ratio > 0.6:
            trend = "positive"
            requires_intervention = False
        else:
            trend = "mixed_neutral"
            requires_intervention = False
        
        # Calculate confidence based on consistency
        dominant_sentiment_ratio = max(negative_ratio, positive_ratio, neutral_count / total_count)
        confidence = dominant_sentiment_ratio
        
        return {
            "sentiment_trend": trend,
            "requires_intervention": requires_intervention,
            "confidence": confidence,
            "statistics": {
                "negative_ratio": negative_ratio,
                "positive_ratio": positive_ratio,
                "neutral_ratio": neutral_count / total_count,
                "total_analyzed": total_count
            },
            "recent_sentiments": [s["sentiment"] for s in sentiment_results[-5:]]  # Last 5
        }
