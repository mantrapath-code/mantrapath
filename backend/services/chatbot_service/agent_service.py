"""
MantraPath Phi-3 Mini Agent Service

Production-ready local AI agent service using Microsoft's Phi-3 Mini model
via vLLM for enhanced conversational capabilities with ML-driven learning.

Key Features:
- OpenAI-compatible API integration with vLLM
- ML-driven conversation learning and optimization
- Secure, robust error handling and fallback mechanisms
- Real-time performance monitoring and analytics
- Context-aware therapeutic response generation

Author: MantraPath Development Team
Version: 3.0.0 (Phi-3 Mini Production)
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import httpx
import redis.asyncio as redis
from pydantic import BaseModel, Field

from .ml_learning import ConversationAnalytics, ResponseOptimizer, PatternRecognizer
from .security_manager import SecurityManager, InputValidator

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """
    Production-ready agent response with comprehensive metadata
    """
    response_text: str
    confidence_score: float
    therapeutic_alignment: float
    conversation_continuity: float
    emotional_intelligence: float
    ml_insights: Dict[str, Any]
    processing_metrics: Dict[str, float]
    security_validation: Dict[str, bool]
    learning_updates: List[Dict[str, Any]]
    timestamp: str

class Phi3AgentService:
    """
    Production Phi-3 Mini agent service with ML-driven learning
    
    Integrates Microsoft's Phi-3 Mini model via vLLM with comprehensive
    ML analytics, security validation, and therapeutic optimization.
    """
    
    def __init__(self):
        # Core configuration
        self.agent_url = "http://localhost:8000/v1/chat/completions"
        self.model_name = "phi3-mini"
        self.redis_url = "redis://localhost:6380"
        
        # ML Learning Components
        self.conversation_analytics = ConversationAnalytics()
        self.response_optimizer = ResponseOptimizer()
        self.pattern_recognizer = PatternRecognizer()
        
        # Security and Validation
        self.security_manager = SecurityManager()
        self.input_validator = InputValidator()
        
        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_responses": 0,
            "average_response_time": 0.0,
            "ml_learning_events": 0,
            "security_validations": 0
        }
        
        # Service state
        self.is_healthy = False
        self.redis_client = None
        
        logger.info("Phi3AgentService initialized with ML learning capabilities")
    
    async def initialize(self):
        """
        Initialize agent service with health checks and ML model loading
        """
        try:
            # Initialize Redis connection for ML data and caching
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis connection established for ML learning")
            
            # Perform agent health check
            await self._health_check()
            
            # Initialize ML learning components
            await self.conversation_analytics.initialize(self.redis_client)
            await self.response_optimizer.initialize(self.redis_client)
            await self.pattern_recognizer.initialize(self.redis_client)
            
            # Load existing ML models and patterns
            await self._load_ml_insights()
            
            self.is_healthy = True
            logger.info("Phi3AgentService initialized successfully with ML capabilities")
            
        except Exception as e:
            logger.error(f"Failed to initialize Phi3AgentService: {str(e)}")
            self.is_healthy = False
            raise
    
    async def generate_response(
        self,
        user_input: str,
        conversation_context: Dict[str, Any],
        mood_context: Dict[str, Any],
        user_profile: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> AgentResponse:
        """
        Generate enhanced response using Phi-3 Mini with ML-driven optimization
        
        Args:
            user_input: User's current message
            conversation_context: Analyzed conversation context
            mood_context: Current mood state and trends
            user_profile: User preferences and mental health context
            conversation_history: Recent conversation messages
            
        Returns:
            AgentResponse with ML-optimized content and learning insights
        """
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1
        
        try:
            # Step 1: Security validation and input sanitization
            security_validation = await self.security_manager.validate_input(
                user_input, user_profile
            )
            
            if not security_validation["is_safe"]:
                return await self._generate_safety_response(security_validation)
            
            # Step 2: ML-driven conversation analysis
            ml_insights = await self.conversation_analytics.analyze_conversation(
                user_input, conversation_context, mood_context, conversation_history
            )
            
            # Step 3: Pattern recognition for therapeutic optimization
            recognized_patterns = await self.pattern_recognizer.identify_patterns(
                user_input, conversation_history, user_profile
            )
            
            # Step 4: Build optimized prompt using ML insights
            optimized_prompt = await self._build_ml_optimized_prompt(
                user_input, conversation_context, mood_context, 
                user_profile, ml_insights, recognized_patterns
            )
            
            # Step 5: Generate response via Phi-3 Mini
            raw_response = await self._call_phi3_agent(optimized_prompt)
            
            # Step 6: ML-driven response optimization
            optimized_response = await self.response_optimizer.optimize_response(
                raw_response, ml_insights, recognized_patterns, user_profile
            )
            
            # Step 7: Generate learning updates for continuous improvement
            learning_updates = await self._generate_learning_updates(
                user_input, optimized_response, ml_insights, recognized_patterns
            )
            
            # Step 8: Cache insights for future optimization
            await self._cache_ml_insights(user_profile["user_id"], ml_insights, learning_updates)
            
            # Calculate processing metrics
            processing_time = time.time() - start_time
            processing_metrics = {
                "total_processing_time": processing_time,
                "ml_analysis_time": ml_insights.get("analysis_time", 0.0),
                "pattern_recognition_time": recognized_patterns.get("recognition_time", 0.0),
                "response_generation_time": raw_response.get("generation_time", 0.0),
                "optimization_time": optimized_response.get("optimization_time", 0.0)
            }
            
            # Create comprehensive agent response
            agent_response = AgentResponse(
                response_text=optimized_response["text"],
                confidence_score=optimized_response["confidence"],
                therapeutic_alignment=optimized_response["therapeutic_score"],
                conversation_continuity=ml_insights["continuity_score"],
                emotional_intelligence=ml_insights["emotional_intelligence"],
                ml_insights=ml_insights,
                processing_metrics=processing_metrics,
                security_validation=security_validation,
                learning_updates=learning_updates,
                timestamp=datetime.utcnow().isoformat()
            )
            
            # Update performance metrics
            self.performance_metrics["successful_responses"] += 1
            self.performance_metrics["average_response_time"] = (
                (self.performance_metrics["average_response_time"] * 
                 (self.performance_metrics["successful_responses"] - 1) + processing_time) /
                self.performance_metrics["successful_responses"]
            )
            self.performance_metrics["ml_learning_events"] += len(learning_updates)
            
            logger.info(
                f"Generated ML-optimized response with confidence {agent_response.confidence_score:.2f} "
                f"in {processing_time:.2f}s"
            )
            
            return agent_response
            
        except Exception as e:
            logger.error(f"Error in Phi-3 response generation: {str(e)}")
            return await self._generate_fallback_response(user_input, mood_context)
    
    async def _build_ml_optimized_prompt(
        self,
        user_input: str,
        conversation_context: Dict,
        mood_context: Dict,
        user_profile: Dict,
        ml_insights: Dict,
        recognized_patterns: Dict
    ) -> List[Dict[str, str]]:
        """
        Build ML-optimized prompt for Phi-3 Mini using conversation insights
        """
        
        # Extract key insights for prompt optimization
        user_communication_style = ml_insights.get("preferred_communication_style", "supportive")
        therapeutic_approach = recognized_patterns.get("optimal_therapeutic_approach", "general_support")
        emotional_state = ml_insights.get("emotional_state_analysis", {})
        conversation_stage = conversation_context.get("conversation_stage", "middle")
        
        # Build system message with ML-driven therapeutic context
        system_message = f"""You are an empathetic, professional mental health support AI assistant specializing in therapeutic conversation.

LEARNED USER PREFERENCES (from ML analysis):
- Preferred Communication Style: {user_communication_style}
- Optimal Therapeutic Approach: {therapeutic_approach}
- Emotional Processing Pattern: {ml_insights.get('emotional_processing_pattern', 'standard')}
- Crisis Response Sensitivity: {ml_insights.get('crisis_sensitivity_level', 'standard')}

CURRENT EMOTIONAL STATE (ML Analysis):
- Primary Emotion: {emotional_state.get('primary_emotion', 'neutral')}
- Emotional Intensity: {emotional_state.get('intensity', 0.5)}/1.0
- Emotional Trajectory: {emotional_state.get('trajectory', 'stable')}
- Stress Indicators: {emotional_state.get('stress_level', 'normal')}

THERAPEUTIC CONTEXT:
- Conversation Stage: {conversation_stage}
- Identified Patterns: {', '.join(recognized_patterns.get('pattern_types', []))}
- Recommended Interventions: {', '.join(recognized_patterns.get('recommended_interventions', []))}

RESPONSE GUIDELINES:
1. Use the learned communication style: {user_communication_style}
2. Apply therapeutic approach: {therapeutic_approach}
3. Address emotional state: {emotional_state.get('primary_emotion', 'neutral')}
4. Maintain conversation continuity based on stage: {conversation_stage}
5. Provide specific, actionable support

Respond with empathy, professionalism, and therapeutic insight. Keep responses conversational but meaningful."""
        
        # Build user message with context
        user_message = f"Current message: {user_input}"
        
        # Add conversation history context if available
        if conversation_context.get("recent_topics"):
            user_message += f"\n\nRecent conversation topics: {', '.join(conversation_context['recent_topics'])}"
        
        if mood_context.get("current_mood_score"):
            user_message += f"\nCurrent mood level: {mood_context['current_mood_score']}/5"
        
        return [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    
    async def _call_phi3_agent(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Call Phi-3 Mini via vLLM OpenAI-compatible API
        """
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.agent_url,
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "max_tokens": 512,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "frequency_penalty": 0.1,
                        "presence_penalty": 0.1,
                        "stop": None
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                generation_time = time.time() - start_time
                
                return {
                    "text": result["choices"][0]["message"]["content"].strip(),
                    "usage": result.get("usage", {}),
                    "generation_time": generation_time,
                    "model": result.get("model", self.model_name)
                }
                
        except Exception as e:
            logger.error(f"Error calling Phi-3 agent: {str(e)}")
            raise
    
    async def _generate_learning_updates(
        self,
        user_input: str,
        response: Dict[str, Any],
        ml_insights: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate learning updates for ML improvement
        """
        learning_updates = []
        
        # User communication pattern learning
        if ml_insights.get("new_communication_pattern"):
            learning_updates.append({
                "type": "communication_pattern",
                "pattern": ml_insights["new_communication_pattern"],
                "confidence": ml_insights["pattern_confidence"],
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Therapeutic approach effectiveness
        if response.get("therapeutic_score", 0) > 0.8:
            learning_updates.append({
                "type": "therapeutic_success",
                "approach": patterns.get("optimal_therapeutic_approach"),
                "effectiveness_score": response["therapeutic_score"],
                "context": ml_insights.get("emotional_state_analysis", {}),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Response quality learning
        learning_updates.append({
            "type": "response_quality",
            "confidence": response.get("confidence", 0.0),
            "therapeutic_alignment": response.get("therapeutic_score", 0.0),
            "user_input_complexity": len(user_input.split()),
            "response_length": len(response.get("text", "").split()),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return learning_updates
    
    async def _cache_ml_insights(
        self, 
        user_id: str, 
        ml_insights: Dict[str, Any], 
        learning_updates: List[Dict[str, Any]]
    ):
        """
        Cache ML insights and learning updates for future optimization
        """
        try:
            if self.redis_client:
                # Cache user-specific insights
                await self.redis_client.setex(
                    f"ml_insights:{user_id}",
                    timedelta(hours=24).total_seconds(),
                    json.dumps(ml_insights)
                )
                
                # Store learning updates for batch processing
                for update in learning_updates:
                    await self.redis_client.lpush(
                        "ml_learning_queue",
                        json.dumps(update)
                    )
                
                # Update global ML statistics
                await self.redis_client.hincrby("ml_stats", "total_insights", 1)
                await self.redis_client.hincrby("ml_stats", "learning_updates", len(learning_updates))
                
        except Exception as e:
            logger.error(f"Error caching ML insights: {str(e)}")
    
    async def _load_ml_insights(self):
        """
        Load existing ML insights and patterns from cache
        """
        try:
            if self.redis_client:
                # Load global ML statistics
                ml_stats = await self.redis_client.hgetall("ml_stats")
                logger.info(f"Loaded ML statistics: {ml_stats}")
                
                # Load recent learning patterns
                recent_patterns = await self.redis_client.lrange("ml_learning_queue", 0, 100)
                logger.info(f"Loaded {len(recent_patterns)} recent learning patterns")
                
        except Exception as e:
            logger.error(f"Error loading ML insights: {str(e)}")
    
    async def _generate_safety_response(self, security_validation: Dict) -> AgentResponse:
        """
        Generate safety response when security validation fails
        """
        safety_response = (
            "I want to ensure our conversation remains supportive and safe. "
            "Let's focus on how I can best help you with your mental health and wellbeing. "
            "What's been on your mind lately that I can support you with?"
        )
        
        return AgentResponse(
            response_text=safety_response,
            confidence_score=0.9,
            therapeutic_alignment=0.95,
            conversation_continuity=0.7,
            emotional_intelligence=0.8,
            ml_insights={"safety_intervention": True},
            processing_metrics={"processing_time": 0.05},
            security_validation=security_validation,
            learning_updates=[{
                "type": "security_intervention",
                "reason": security_validation.get("violation_type", "general"),
                "timestamp": datetime.utcnow().isoformat()
            }],
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _generate_fallback_response(self, user_input: str, mood_context: Dict) -> AgentResponse:
        """
        Generate fallback response when Phi-3 agent is unavailable
        """
        fallback_text = (
            "I'm here to support you, though I'm experiencing some technical challenges right now. "
            "Your wellbeing is important to me. Can you tell me what's most important for you "
            "to talk about today?"
        )
        
        return AgentResponse(
            response_text=fallback_text,
            confidence_score=0.6,
            therapeutic_alignment=0.75,
            conversation_continuity=0.5,
            emotional_intelligence=0.7,
            ml_insights={"fallback_mode": True},
            processing_metrics={"processing_time": 0.1},
            security_validation={"is_safe": True, "validation_level": "basic"},
            learning_updates=[{
                "type": "fallback_activation",
                "reason": "agent_unavailable",
                "timestamp": datetime.utcnow().isoformat()
            }],
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def _health_check(self) -> bool:
        """
        Perform comprehensive health check on Phi-3 agent
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test model availability
                response = await client.get("http://localhost:8000/v1/models")
                if response.status_code != 200:
                    return False
                
                models = response.json()
                available_models = [model["id"] for model in models.get("data", [])]
                
                if self.model_name not in available_models:
                    logger.warning(f"Model {self.model_name} not found in available models: {available_models}")
                    return False
                
                # Test basic generation
                test_response = await client.post(
                    self.agent_url,
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "max_tokens": 10
                    }
                )
                
                return test_response.status_code == 200
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive service status including ML metrics
        """
        return {
            "is_healthy": self.is_healthy,
            "model_name": self.model_name,
            "agent_url": self.agent_url,
            "performance_metrics": self.performance_metrics,
            "ml_capabilities": {
                "conversation_analytics": self.conversation_analytics.is_initialized,
                "response_optimizer": self.response_optimizer.is_initialized,
                "pattern_recognizer": self.pattern_recognizer.is_initialized
            },
            "redis_connected": self.redis_client is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
