import asyncio
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

import structlog
from nats.aio.client import Client as NATS
from nats.js import JetStreamContext
from redis import Redis

from shared.events import get_enhanced_event_bus
from shared.events.ai_events import AIProcessingEvent, AIEventType, ProcessingData, ContextData
from models.ai_models import AIMetrics, EventProcessingStatus

logger = structlog.get_logger(__name__)

class AIEventProcessor:
    """
    Core AI Event Processing Pipeline
    
    Processes all platform events with real-time AI analysis including:
    - Emotion analysis from mood and journal events
    - Cross-service AI context building 
    - Predictive intervention triggers
    - Cultural intelligence processing
    """
    
    def __init__(self):
        self.event_bus = None
        self.redis_client = None
        self.nats = None
        self.js = None
        self.is_running = False
        self.metrics = AIMetrics()
        self.processing_tasks = {}
        
        # Performance tracking
        self.start_time = time.time()
        self.event_count = 0
        self.error_count = 0
        self.processing_times = []
        
    async def start(self):
        """Start the AI event processor"""
        try:
            logger.info("Starting AI Event Processor")
            
            # Initialize event bus
            self.event_bus = get_enhanced_event_bus()
            await self.event_bus.connect()
            
            # Initialize Redis for caching and state
            self.redis_client = Redis.from_url("redis://redis:6379/3", decode_responses=True)
            
            # Subscribe to relevant events
            await self._setup_event_subscriptions()
            
            self.is_running = True
            logger.info("AI Event Processor started successfully")
            
        except Exception as e:
            logger.error("Failed to start AI Event Processor", error=str(e))
            raise
    
    async def stop(self):
        """Stop the AI event processor"""
        try:
            logger.info("Stopping AI Event Processor")
            self.is_running = False
            
            # Cancel all processing tasks
            for task in self.processing_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.processing_tasks:
                await asyncio.gather(*self.processing_tasks.values(), return_exceptions=True)
            
            # Disconnect from services
            if self.event_bus:
                await self.event_bus.disconnect()
            
            logger.info("AI Event Processor stopped")
            
        except Exception as e:
            logger.error("Error stopping AI Event Processor", error=str(e))
    
    async def _setup_event_subscriptions(self):
        """Setup event subscriptions for AI processing"""
        
        # Mood events for emotion analysis
        await self.event_bus.subscribe(
            "mood.entry_created",
            self._handle_mood_event
        )
        
        # Journal events for sentiment analysis
        await self.event_bus.subscribe(
            "journal.entry_created",
            self._handle_journal_event
        )
        
        # Voice events for voice emotion analysis
        await self.event_bus.subscribe(
            "voice.activity_detected",
            self._handle_voice_event
        )
        
        # Chat events for conversation analysis
        await self.event_bus.subscribe(
            "chat.message_sent",
            self._handle_chat_event
        )
        
        # User behavior events
        await self.event_bus.subscribe(
            "user.interaction",
            self._handle_user_interaction
        )
        
        logger.info("AI event subscriptions setup complete")
    
    async def _handle_mood_event(self, event: Dict[str, Any]):
        """Handle mood events for emotion analysis"""
        try:
            start_time = time.time()
            user_id = event.get("user_id")
            
            if not user_id:
                logger.warning("Mood event missing user_id")
                return
            
            # Process mood data
            mood_data = event.get("data", {})
            
            # Analyze emotional patterns
            analysis_result = await self._analyze_mood_patterns(user_id, mood_data)
            
            # Update user context
            await self._update_user_context(user_id, "mood", analysis_result)
            
            # Check for intervention needs
            await self._evaluate_intervention_needs(user_id, analysis_result)
            
            # Publish AI analysis result
            ai_event = AIProcessingEvent(
                event_type=AIEventType.EMOTION_ANALYZED,
                processing_data=ProcessingData(
                    model_name="emotion_analyzer",
                    input_data_hash=str(hash(str(mood_data))),
                    processing_time_ms=100,
                    confidence_scores={"emotion": 0.85}
                ),
                context_data=ContextData(
                    user_context={"user_id": user_id},
                    session_context={"analysis_type": "mood"}
                ),
                source_service="ai_event_processor",
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                response_data_reference=str({
                    "source": "mood",
                    "analysis": analysis_result,
                    "processing_time_ms": (time.time() - start_time) * 1000
                })
            )
            
            await self.event_bus.publish("ai.emotion_analyzed", ai_event.model_dump())
            
            # Update metrics
            self._update_metrics(time.time() - start_time)
            
        except Exception as e:
            logger.error("Error handling mood event", error=str(e), user_id=user_id)
            self.error_count += 1
    
    async def _handle_journal_event(self, event: Dict[str, Any]):
        """Handle journal events for sentiment analysis"""
        try:
            start_time = time.time()
            user_id = event.get("user_id")
            
            if not user_id:
                logger.warning("Journal event missing user_id")
                return
            
            # Process journal content
            journal_data = event.get("data", {})
            content = journal_data.get("content", "")
            
            # Analyze sentiment and themes
            analysis_result = await self._analyze_journal_content(user_id, content)
            
            # Update user context
            await self._update_user_context(user_id, "journal", analysis_result)
            
            # Check for intervention needs
            await self._evaluate_intervention_needs(user_id, analysis_result)
            
            # Publish AI analysis result
            ai_event = AIProcessingEvent(
                event_type=AIEventType.CONTENT_ANALYZED,
                processing_data=ProcessingData(
                    model_name="content_analyzer",
                    input_data_hash=str(hash(str(journal_data))),
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    confidence_scores={"content": 0.85}
                ),
                context_data=ContextData(
                    user_context={"user_id": user_id},
                    session_context={"analysis_type": "journal"}
                ),
                source_service="ai_event_processor",
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                response_data_reference=str({
                    "source": "journal",
                    "analysis": analysis_result,
                    "processing_time_ms": (time.time() - start_time) * 1000
                })
            )
            
            await self.event_bus.publish("ai.content_analyzed", ai_event.model_dump())
            
            # Update metrics
            self._update_metrics(time.time() - start_time)
            
        except Exception as e:
            logger.error("Error handling journal event", error=str(e), user_id=user_id)
            self.error_count += 1
    
    async def _handle_voice_event(self, event: Dict[str, Any]):
        """Handle voice events for voice emotion analysis"""
        try:
            start_time = time.time()
            user_id = event.get("user_id")
            
            if not user_id:
                logger.warning("Voice event missing user_id")
                return
            
            # Process voice data
            voice_data = event.get("data", {})
            
            # Analyze voice emotion
            analysis_result = await self._analyze_voice_emotion(user_id, voice_data)
            
            # Update user context
            await self._update_user_context(user_id, "voice", analysis_result)
            
            # Check for intervention needs (voice has higher urgency)
            await self._evaluate_intervention_needs(user_id, analysis_result, urgent=True)
            
            # Publish AI analysis result
            ai_event = AIProcessingEvent(
                event_type=AIEventType.VOICE_ANALYZED,
                processing_data=ProcessingData(
                    model_name="voice_analyzer",
                    input_data_hash=str(hash(str(voice_data))),
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    confidence_scores={"voice": 0.85}
                ),
                context_data=ContextData(
                    user_context={"user_id": user_id},
                    session_context={"analysis_type": "voice"}
                ),
                source_service="ai_event_processor",
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                response_data_reference=str({
                    "source": "voice",
                    "analysis": analysis_result,
                    "processing_time_ms": (time.time() - start_time) * 1000
                })
            )
            
            await self.event_bus.publish("ai.voice_analyzed", ai_event.model_dump())
            
            # Update metrics
            self._update_metrics(time.time() - start_time)
            
        except Exception as e:
            logger.error("Error handling voice event", error=str(e), user_id=user_id)
            self.error_count += 1
    
    async def _handle_chat_event(self, event: Dict[str, Any]):
        """Handle chat events for conversation analysis"""
        try:
            start_time = time.time()
            user_id = event.get("user_id")
            
            if not user_id:
                logger.warning("Chat event missing user_id")
                return
            
            # Process chat message
            chat_data = event.get("data", {})
            message = chat_data.get("message", "")
            
            # Analyze conversation patterns
            analysis_result = await self._analyze_conversation(user_id, message)
            
            # Update user context
            await self._update_user_context(user_id, "chat", analysis_result)
            
            # Check for intervention needs
            await self._evaluate_intervention_needs(user_id, analysis_result)
            
            # Publish AI analysis result
            ai_event = AIProcessingEvent(
                event_type=AIEventType.CONVERSATION_ANALYZED,
                processing_data=ProcessingData(
                    model_name="conversation_analyzer",
                    input_data_hash=str(hash(str(chat_data))),
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    confidence_scores={"conversation": 0.85}
                ),
                context_data=ContextData(
                    user_context={"user_id": user_id},
                    session_context={"analysis_type": "chat"}
                ),
                source_service="ai_event_processor",
                user_id=user_id,
                session_id=str(uuid.uuid4()),
                response_data_reference=str({
                    "source": "chat",
                    "analysis": analysis_result,
                    "processing_time_ms": (time.time() - start_time) * 1000
                })
            )
            
            await self.event_bus.publish("ai.conversation_analyzed", ai_event.model_dump())
            
            # Update metrics
            self._update_metrics(time.time() - start_time)
            
        except Exception as e:
            logger.error("Error handling chat event", error=str(e), user_id=user_id)
            self.error_count += 1
    
    async def _handle_user_interaction(self, event: Dict[str, Any]):
        """Handle general user interaction events"""
        try:
            start_time = time.time()
            user_id = event.get("user_id")
            
            if not user_id:
                return
            
            # Process user interaction patterns
            interaction_data = event.get("data", {})
            
            # Update behavioral context
            await self._update_behavioral_context(user_id, interaction_data)
            
            # Update metrics
            self._update_metrics(time.time() - start_time)
            
        except Exception as e:
            logger.error("Error handling user interaction", error=str(e), user_id=user_id)
            self.error_count += 1
    
    async def _analyze_mood_patterns(self, user_id: str, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mood patterns for emotional insights"""
        # Placeholder for mood pattern analysis
        # In production, this would use ML models for pattern recognition
        
        mood_score = mood_data.get("mood_score", 5)
        emotions = mood_data.get("emotions", [])
        
        return {
            "mood_trend": "stable" if 4 <= mood_score <= 6 else "declining" if mood_score < 4 else "improving",
            "emotional_state": emotions[0] if emotions else "neutral",
            "risk_level": "low" if mood_score >= 4 else "medium" if mood_score >= 2 else "high",
            "confidence": 0.85
        }
    
    async def _analyze_journal_content(self, user_id: str, content: str) -> Dict[str, Any]:
        """Analyze journal content for sentiment and themes"""
        # Placeholder for sentiment analysis
        # In production, this would use transformer models for sentiment analysis
        
        word_count = len(content.split())
        
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.0,
            "themes": ["reflection"],
            "urgency": "low",
            "word_count": word_count,
            "confidence": 0.80
        }
    
    async def _analyze_voice_emotion(self, user_id: str, voice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze voice data for emotional state"""
        # Placeholder for voice emotion analysis
        # In production, this would use audio ML models
        
        return {
            "emotion": "neutral",
            "confidence": 0.75,
            "stress_level": "low",
            "energy_level": "medium",
            "voice_quality": "clear"
        }
    
    async def _analyze_conversation(self, user_id: str, message: str) -> Dict[str, Any]:
        """Analyze conversation for patterns and sentiment"""
        # Placeholder for conversation analysis
        # In production, this would use conversation AI models
        
        return {
            "sentiment": "neutral",
            "intent": "casual_conversation",
            "engagement_level": "medium",
            "support_needed": False,
            "confidence": 0.82
        }
    
    async def _update_user_context(self, user_id: str, source: str, analysis: Dict[str, Any]):
        """Update user AI context with new analysis"""
        try:
            context_key = f"ai_context:{user_id}"
            
            # Get existing context
            existing_context = self.redis_client.get(context_key)
            if existing_context:
                context = json.loads(existing_context)
            else:
                context = {"user_id": user_id, "sources": {}}
            
            # Update with new analysis
            context["sources"][source] = {
                "analysis": analysis,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "last_updated": time.time()
            }
            
            # Store updated context
            self.redis_client.setex(
                context_key, 
                3600,  # 1 hour TTL
                json.dumps(context)
            )
            
            # Publish context update event
            await self.event_bus.publish("ai.context_updated", {
                "user_id": user_id,
                "source": source,
                "context": context
            })
            
        except Exception as e:
            logger.error("Error updating user context", error=str(e), user_id=user_id)
    
    async def _update_behavioral_context(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update behavioral context from user interactions"""
        try:
            behavior_key = f"behavior_context:{user_id}"
            
            # Simple interaction tracking
            interaction_summary = {
                "action": interaction_data.get("action"),
                "timestamp": time.time(),
                "session_id": interaction_data.get("session_id")
            }
            
            # Store recent interactions (last 100)
            self.redis_client.lpush(behavior_key, json.dumps(interaction_summary))
            self.redis_client.ltrim(behavior_key, 0, 99)
            self.redis_client.expire(behavior_key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error("Error updating behavioral context", error=str(e), user_id=user_id)
    
    async def _evaluate_intervention_needs(self, user_id: str, analysis: Dict[str, Any], urgent: bool = False):
        """Evaluate if user needs proactive intervention"""
        try:
            risk_level = analysis.get("risk_level", "low")
            confidence = analysis.get("confidence", 0.0)
            
            # Simple intervention logic
            if risk_level == "high" and confidence > 0.8:
                await self.event_bus.publish("ai.intervention_needed", {
                    "user_id": user_id,
                    "urgency": "high" if urgent else "medium",
                    "reason": "High risk detected",
                    "analysis": analysis,
                    "timestamp": time.time()
                })
            elif risk_level == "medium" and confidence > 0.9:
                await self.event_bus.publish("ai.intervention_suggested", {
                    "user_id": user_id,
                    "urgency": "low",
                    "reason": "Medium risk detected",
                    "analysis": analysis,
                    "timestamp": time.time()
                })
            
        except Exception as e:
            logger.error("Error evaluating intervention needs", error=str(e), user_id=user_id)
    
    async def update_context(self, user_id: str, context_data: Dict[str, Any], source: str):
        """External API for updating user context"""
        await self._update_user_context(user_id, source, context_data)
    
    def _update_metrics(self, processing_time: float):
        """Update processing metrics"""
        self.event_count += 1
        processing_time_ms = processing_time * 1000
        self.processing_times.append(processing_time_ms)
        
        # Keep only last 1000 measurements
        if len(self.processing_times) > 1000:
            self.processing_times = self.processing_times[-1000:]
        
        # Update metrics
        self.metrics.total_events_processed = self.event_count
        self.metrics.average_processing_time_ms = sum(self.processing_times) / len(self.processing_times)
        self.metrics.error_rate = self.error_count / max(self.event_count, 1)
        
        # Calculate events per minute
        elapsed_time = time.time() - self.start_time
        self.metrics.events_per_minute = (self.event_count / elapsed_time) * 60 if elapsed_time > 0 else 0
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current processing metrics"""
        return self.metrics.model_dump()
    
    def health_check(self) -> bool:
        """Check if the processor is healthy"""
        return self.is_running and self.event_bus is not None
    
    def is_ready(self) -> bool:
        """Check if the processor is ready to handle requests"""
        return self.health_check() and self.redis_client is not None
