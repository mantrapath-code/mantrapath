"""
Proactive Assistance Orchestrator

Main orchestrator for proactive assistance that coordinates existing services
to provide timely, contextually relevant, and culturally sensitive assistance.
"""

import asyncio
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import structlog
import os, sys

# Ensure backend root is on sys.path so `shared` package is importable
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from shared.events import EnhancedEventBus, Event

# Prefer shared models; fallback to local src models to avoid import errors depending on PYTHONPATH
try:
    from shared.models.assistance import (
        AssistanceEvaluation, UserAssistanceNeeds, HealthStatus,
        IntegrationStatus, ServiceMetrics, InterventionAnalysis,
        TimingEvaluation, CulturalEvaluation, AssistanceDecision,
        AssistanceContent
    )
except Exception:
    from src.models.assistance_models import (
        AssistanceEvaluation, UserAssistanceNeeds, HealthStatus,
        IntegrationStatus, ServiceMetrics, InterventionAnalysis,
        TimingEvaluation, CulturalEvaluation, AssistanceDecision,
        AssistanceContent
    )

# Event schema optional typing
try:
    from shared.events.schemas import AssistanceInterventionNeeded
except Exception:
    AssistanceInterventionNeeded = None

# Import shared event bus and event model
from src.integrations.ai_event_processor_client import AIEventProcessorClient
from src.integrations.ai_context_store_client import AIContextStoreClient
from src.integrations.cultural_intelligence_client import CulturalIntelligenceClient
from src.integrations.models_service_client import ProactiveModelsServiceClient  # NEW
from src.core.timing_predictor import ComprehensiveTimingPredictor
from src.core.contextual_help_engine import ContextualHelpEngine
from src.core.cultural_sensitivity_engine import CulturalSensitivityEngine
try:
    from shared.models.assistance import (
        AssistanceEvaluation, UserAssistanceNeeds, HealthStatus,
        IntegrationStatus, ServiceMetrics, InterventionAnalysis,
        TimingEvaluation, CulturalEvaluation, AssistanceDecision,
        AssistanceContent
    )
except Exception:
    from src.models.assistance_models import (
        AssistanceEvaluation, UserAssistanceNeeds, HealthStatus,
        IntegrationStatus, ServiceMetrics, InterventionAnalysis,
        TimingEvaluation, CulturalEvaluation, AssistanceDecision,
        AssistanceContent
    )

logger = structlog.get_logger(__name__)

class ProactiveAssistanceOrchestrator:
    """
    Main orchestrator for proactive assistance that coordinates existing services
    """
    
    def __init__(self):
        self.ai_event_client = None
        self.context_store_client = None
        self.cultural_client = None
        self.models_service_client = None  # NEW - Models Service client
        self.timing_predictor = None
        self.help_engine = None
        self.cultural_sensitivity_engine = None
        self.is_initialized = False
        
        # Assistance configuration
        self.assistance_config = {
            "evaluation_interval_minutes": 30,
            "min_assistance_gap_hours": 2,
            "cultural_sensitivity_threshold": 0.9,
            "timing_confidence_threshold": 0.7
        }
        
        # Performance tracking
        self.metrics = {
            "total_evaluations": 0,
            "successful_evaluations": 0,
            "total_response_time_ms": 0,
            "cultural_adaptations": 0,
            "errors": 0
        }
        
        # Eventing: Enhanced bus (NATS-backed) and debounce map
        self.event_bus: Optional[EnhancedEventBus] = None
        self._last_eval_ts: Dict[str, float] = {}
        self._debounce_seconds: int = 60  # throttle per-user evaluations

    async def initialize(self):
        """Initialize orchestrator with service clients"""
        try:
            # Initialize service clients using environment variables for Docker networking
            import os
            ai_event_url = os.getenv("AI_EVENT_PROCESSOR_URL", "http://localhost:8014")
            context_store_url = os.getenv("AI_CONTEXT_STORE_URL", "http://localhost:8013")
            cultural_url = os.getenv("CULTURAL_INTELLIGENCE_URL", "http://localhost:8017")
            models_url = os.getenv("MODELS_SERVICE_URL", "http://localhost:8080")
            
            self.ai_event_client = AIEventProcessorClient(ai_event_url)
            self.context_store_client = AIContextStoreClient(context_store_url)
            self.cultural_client = CulturalIntelligenceClient(cultural_url)
            self.models_service_client = ProactiveModelsServiceClient(models_url)
            
            # Initialize core engines
            self.timing_predictor = ComprehensiveTimingPredictor()
            self.help_engine = ContextualHelpEngine()
            self.cultural_sensitivity_engine = CulturalSensitivityEngine()
            
            # Initialize event bus and subscriptions (disable NATS for now)
            self.event_bus = EnhancedEventBus(use_nats=False)
            await self.event_bus.initialize()
            await self._subscribe_to_events()
            
            # Test connections
            await self._test_service_connections()
            
            self.is_initialized = True
            logger.info("Proactive Assistance Orchestrator initialized successfully with Models Service")
            
        except Exception as e:
            logger.error("Failed to initialize orchestrator", error=str(e))
            raise

    async def _subscribe_to_events(self) -> None:
        """Subscribe to upstream events and debounce evaluations."""
        async def handler(event: Event):
            try:
                user_id = event.user_id or (event.data or {}).get("user_id")
                if not user_id:
                    return
                await self._debounced_evaluate(user_id)
            except Exception as e:
                logger.error("Event handler error", channel=event.channel, error=str(e))
        
        # Core topics from plan
        for subject in [
            "context.updated",
            "ai.emotion_detected",
            "journal.entry_created",
            "mood.entry_created",
            "voice.activity_detected",
        ]:
            await self.event_bus.subscribe(subject, handler)
            logger.info("Subscribed to event", subject=subject)

    async def _debounced_evaluate(self, user_id: str) -> None:
        """Debounce per-user assistance evaluations to avoid storms."""
        now = datetime.now(timezone.utc).timestamp()
        last = self._last_eval_ts.get(user_id, 0)
        if now - last < self._debounce_seconds:
            return
        self._last_eval_ts[user_id] = now
        
        evaluation = await self.evaluate_user_assistance_needs(user_id)
        # Publish intervention-needed event
        if evaluation.assistance_decision.should_provide_assistance and self.event_bus:
            if AssistanceInterventionNeeded:
                event_model = AssistanceInterventionNeeded(
                    user_id=user_id,
                    risk_level=str(evaluation.intervention_analysis.urgency_level),
                    recommended_actions=evaluation.intervention_analysis.recommended_actions,
                    reason="; ".join(evaluation.assistance_decision.reasoning),
                    ts=evaluation.evaluation_timestamp
                )
                payload = event_model.model_dump(mode="json")
            else:
                payload = {
                    "user_id": user_id,
                    "risk_level": str(evaluation.intervention_analysis.urgency_level),
                    "recommended_actions": evaluation.intervention_analysis.recommended_actions,
                    "reason": "; ".join(evaluation.assistance_decision.reasoning),
                    "ts": evaluation.evaluation_timestamp.isoformat()
                }
            await self.event_bus.publish("assistance.intervention_needed", payload, user_id=user_id)

    async def evaluate_user_assistance_needs(self, user_id: str) -> AssistanceEvaluation:
        """
        Evaluate user's current assistance needs based on AI analysis
        
        Args:
            user_id: User identifier
        
        Returns:
            AssistanceRecommendation with intervention details
        """
        try:
            logger.info("Starting assistance evaluation", user_id=user_id)
            
            # Get user context from AI Context Store
            user_context = await self.context_store_client.get_user_context(user_id)
            logger.info("Retrieved user context", user_id=user_id, context_available=bool(user_context))
            
            # Get intervention analysis from AI Event Processor
            intervention_analysis = await self.ai_event_client.analyze_intervention_needs(user_id)
            logger.info("Retrieved intervention analysis", user_id=user_id, 
                       intervention_needed=intervention_analysis.get("intervention_needed", False))
            
            # Create assistance recommendation based on analysis
            assistance_evaluation = await self._create_assistance_evaluation(
                user_id, user_context, intervention_analysis
            )
            
            logger.info("Assistance evaluation completed", user_id=user_id, 
                       assistance_type=assistance_evaluation.assistance_decision.assistance_type)
            
            return assistance_evaluation
            
        except Exception as e:
            logger.error("Error evaluating assistance needs", user_id=user_id, error=str(e))
            # Return safe fallback assistance
            return self._create_fallback_evaluation(user_id)
    
    async def get_user_assistance_status(self, user_id: str) -> Dict[str, Any]:
        """Get current assistance status for user"""
        try:
            if not self.is_initialized:
                raise RuntimeError("Orchestrator not initialized")
            
            # Get recent assistance history
            user_context = await self.context_store_client.get_user_context(user_id)
            
            return {
                "user_id": user_id,
                "last_assistance_time": user_context.get("last_assistance_time"),
                "assistance_frequency": user_context.get("assistance_frequency", "unknown"),
                "current_needs": user_context.get("current_needs", []),
                "assistance_preferences": user_context.get("assistance_preferences", {}),
                "status": "active" if user_context else "inactive"
            }
            
        except Exception as e:
            logger.error("Failed to get assistance status", error=str(e), user_id=user_id)
            return {
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            }
    
    async def trigger_assistance(self, user_id: str) -> Dict[str, Any]:
        """Manually trigger proactive assistance for user"""
        try:
            if not self.is_initialized:
                raise RuntimeError("Orchestrator not initialized")
            
            logger.info("Manually triggering assistance", user_id=user_id)
            
            # Force assistance evaluation
            evaluation = await self.evaluate_user_assistance_needs(user_id)
            
            # If assistance is needed, provide it immediately
            if evaluation.assistance_decision.should_provide_assistance:
                # Publish triggered event
                if self.event_bus:
                    await self.event_bus.publish(
                        "assistance.triggered",
                        {
                            "user_id": user_id,
                            "assistance_type": str(evaluation.assistance_decision.assistance_type) if evaluation.assistance_decision.assistance_type else None,
                            "ts": evaluation.evaluation_timestamp.isoformat()
                        },
                        user_id=user_id
                    )
                return {
                    "status": "assistance_triggered",
                    "user_id": user_id,
                    "assistance_type": evaluation.assistance_decision.assistance_type,
                    "content": evaluation.assistance_content
                }
            else:
                return {
                    "status": "no_assistance_needed",
                    "user_id": user_id,
                    "reason": "User does not currently need assistance"
                }
                
        except Exception as e:
            logger.error("Failed to trigger assistance", error=str(e), user_id=user_id)
            return {
                "status": "error",
                "user_id": user_id,
                "error": str(e)
            }
    
    async def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        try:
            components = {
                "orchestrator": self.is_initialized,
                "timing_predictor": self.timing_predictor is not None,
                "help_engine": self.help_engine is not None,
                "cultural_sensitivity_engine": self.cultural_sensitivity_engine is not None
            }
            
            integrations = await self.get_integration_status()
            
            return HealthStatus(
                status="healthy" if self.is_initialized else "unhealthy",
                service="proactive-assistance-engine",
                version="1.0.0",
                timestamp=datetime.now(timezone.utc),
                components=components,
                integrations=integrations.model_dump()
            )
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return HealthStatus(
                status="unhealthy",
                service="proactive-assistance-engine",
                version="1.0.0",
                timestamp=datetime.now(timezone.utc),
                components={},
                integrations={}
            )
    
    async def get_integration_status(self) -> IntegrationStatus:
        """Check status of all integrated services"""
        try:
            ai_event_status = await self.ai_event_client.get_health_status()
            context_store_status = await self.context_store_client.get_health_status()
            cultural_status = await self.cultural_client.get_health_status()
            
            # Determine overall status
            all_healthy = all([
                ai_event_status.get("status") == "healthy",
                context_store_status.get("status") == "healthy",
                cultural_status.get("status") == "healthy"
            ])
            
            return IntegrationStatus(
                ai_event_processor=ai_event_status,
                ai_context_store=context_store_status,
                cultural_intelligence=cultural_status,
                overall_status="healthy" if all_healthy else "degraded",
                last_check=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error("Integration status check failed", error=str(e))
            return IntegrationStatus(
                ai_event_processor={"status": "unknown"},
                ai_context_store={"status": "unknown"},
                cultural_intelligence={"status": "unknown"},
                overall_status="unknown",
                last_check=datetime.now(timezone.utc)
            )
    
    async def get_metrics(self) -> ServiceMetrics:
        """Get service performance metrics"""
        try:
            avg_response_time = (
                self.metrics["total_response_time_ms"] / self.metrics["total_evaluations"]
                if self.metrics["total_evaluations"] > 0 else 0
            )
            
            cultural_adaptation_rate = (
                self.metrics["cultural_adaptations"] / self.metrics["total_evaluations"]
                if self.metrics["total_evaluations"] > 0 else 0
            )
            
            error_rate = (
                self.metrics["errors"] / self.metrics["total_evaluations"]
                if self.metrics["total_evaluations"] > 0 else 0
            )
            
            return ServiceMetrics(
                timestamp=datetime.now(timezone.utc),
                service="proactive-assistance-engine",
                total_evaluations=self.metrics["total_evaluations"],
                successful_evaluations=self.metrics["successful_evaluations"],
                average_response_time_ms=avg_response_time,
                cultural_adaptation_rate=cultural_adaptation_rate,
                assistance_acceptance_rate=0.0,  # TODO: Implement user feedback tracking
                error_rate=error_rate,
                performance_indicators={
                    "initialization_status": self.is_initialized,
                    "active_connections": 3 if self.is_initialized else 0
                }
            )
            
        except Exception as e:
            logger.error("Failed to get metrics", error=str(e))
            return ServiceMetrics(
                timestamp=datetime.now(timezone.utc),
                service="proactive-assistance-engine",
                total_evaluations=0,
                successful_evaluations=0,
                average_response_time_ms=0.0,
                cultural_adaptation_rate=0.0,
                assistance_acceptance_rate=0.0,
                error_rate=0.0,
                performance_indicators={}
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.ai_event_client:
                await self.ai_event_client.close()
            if self.context_store_client:
                await self.context_store_client.close()
            if self.cultural_client:
                await self.cultural_client.close()
            if self.event_bus:
                await self.event_bus.close()
            
            logger.info("Proactive Assistance Orchestrator cleanup completed")
            
        except Exception as e:
            logger.error("Cleanup failed", error=str(e))
    
    async def _test_service_connections(self):
        """Test connections to all integrated services"""
        try:
            # Test AI Event Processor
            await self.ai_event_client.get_health_status()
            logger.info("AI Event Processor connection successful")
            
            # Test AI Context Store
            await self.context_store_client.get_health_status()
            logger.info("AI Context Store connection successful")
            
            # Test Cultural Intelligence
            await self.cultural_client.get_health_status()
            logger.info("Cultural Intelligence connection successful")
            
        except Exception as e:
            logger.error("Service connection test failed", error=str(e))
            raise
    
    async def _make_assistance_decision(
        self,
        user_id: str,
        intervention_analysis: InterventionAnalysis,
        timing_evaluation: TimingEvaluation,
        cultural_evaluation: CulturalEvaluation
    ) -> AssistanceDecision:
        """Make final assistance decision based on all evaluations"""
        try:
            # Base decision on intervention analysis
            intervention_needed = intervention_analysis.intervention_needed
            urgency_level = intervention_analysis.urgency_level
            
            # Check timing appropriateness
            timing_appropriate = timing_evaluation.timing_appropriate
            urgency_override = timing_evaluation.urgency_override
            
            # Check cultural appropriateness
            culturally_appropriate = cultural_evaluation.culturally_appropriate
            
            # Decision logic
            should_provide = (
                intervention_needed and
                (timing_appropriate or urgency_override) and
                culturally_appropriate
            )
            
            # Calculate confidence score
            confidence = (
                intervention_analysis.confidence * 0.4 +
                timing_evaluation.timing_confidence * 0.3 +
                cultural_evaluation.appropriateness_score * 0.3
            )
            
            # Determine assistance type
            assistance_type = intervention_analysis.intervention_type
            
            # Generate reasoning
            reasoning = []
            if intervention_needed:
                reasoning.append(f"Intervention needed: {intervention_analysis.intervention_type or 'unknown'}")
            if timing_appropriate or urgency_override:
                reasoning.append("Timing appropriate for assistance")
            if culturally_appropriate:
                reasoning.append("Culturally appropriate")
            
            return AssistanceDecision(
                should_provide_assistance=should_provide,
                confidence=confidence,
                reasoning=reasoning,
                assistance_type=assistance_type,
                priority_score=confidence,
                user_preferences_respected=True  # TODO: Implement user preference checking
            )
            
        except Exception as e:
            logger.error("Failed to make assistance decision", error=str(e))
            return AssistanceDecision(
                should_provide_assistance=False,
                confidence=0.0,
                reasoning=["Error in decision making"],
                assistance_type=None,
                priority_score=0.0,
                user_preferences_respected=False
            )
    
    async def _create_assistance_evaluation(self, user_id: str, user_context: Dict[str, Any], intervention_analysis: Dict[str, Any]) -> AssistanceEvaluation:
        """Create complete assistance evaluation from user context and intervention analysis"""
        try:
            # Extract or create intervention analysis
            if isinstance(intervention_analysis, dict):
                from shared.models.assistance import UrgencyLevel
                intervention = InterventionAnalysis(
                    intervention_needed=intervention_analysis.get("intervention_needed", False),
                    confidence=intervention_analysis.get("confidence", 0.0),
                    intervention_type=intervention_analysis.get("intervention_type"),
                    urgency_level=UrgencyLevel(intervention_analysis.get("urgency_level", "none")),
                    recommended_actions=intervention_analysis.get("recommended_actions", []),
                    risk_factors=intervention_analysis.get("risk_factors", {}),
                    fallback_reason=intervention_analysis.get("fallback_reason")
                )
            else:
                intervention = intervention_analysis

            # Create timing evaluation
            timing = TimingEvaluation(
                timing_appropriate=True,  # Default to appropriate
                timing_confidence=0.7,
                can_proceed=True,
                recommended_delay_minutes=0,
                recent_assistance_check={},
                activity_analysis={},
                cultural_timing={},
                urgency_override=False
            )

            # Create cultural evaluation  
            cultural = CulturalEvaluation(
                culturally_appropriate=True,
                appropriateness_score=0.8,
                content_evaluation={},
                timing_evaluation={},
                adapted_content=None,
                cultural_considerations=[]
            )

            # Create assistance decision
            decision = AssistanceDecision(
                should_provide_assistance=intervention.intervention_needed,
                confidence=intervention.confidence,
                reasoning=["Based on intervention analysis"],
                assistance_type=intervention.intervention_type,
                priority_score=intervention.confidence,
                user_preferences_respected=True
            )

            # Create assistance content if needed
            content = None
            if decision.should_provide_assistance:
                from shared.models.assistance import UrgencyLevel
                content = AssistanceContent(
                    content_id=f"assist_{user_id}_{datetime.now(timezone.utc).timestamp()}",
                    title="Assistance Recommendation",
                    content="We've identified that you might benefit from some support.",
                    actions=intervention.recommended_actions,
                    urgency=intervention.urgency_level,
                    cultural_adaptations={},
                    confidence_score=intervention.confidence
                )

            return AssistanceEvaluation(
                user_id=user_id,
                evaluation_timestamp=datetime.now(timezone.utc),
                intervention_analysis=intervention,
                timing_evaluation=timing,
                cultural_evaluation=cultural,
                assistance_decision=decision,
                assistance_content=content,
                confidence_score=intervention.confidence,
                metadata={"source": "proactive_evaluation"}
            )

        except Exception as e:
            logger.error("Error creating assistance evaluation", error=str(e), user_id=user_id)
            # Return fallback evaluation
            return self._create_fallback_evaluation(user_id)
    
    def _create_fallback_evaluation(self, user_id: str) -> AssistanceEvaluation:
        """Create fallback evaluation with demonstration assistance when services are unavailable"""
        import os
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        if demo_mode:
            # Import enum types
            from shared.models.assistance import AssistanceType, UrgencyLevel
            
            # Provide realistic demonstration data
            fallback_intervention = InterventionAnalysis(
                intervention_needed=True,
                confidence=0.75,
                intervention_type=AssistanceType.GENTLE_CHECK_IN,
                urgency_level=UrgencyLevel.MEDIUM,
                recommended_actions=["provide_meditation_guidance", "offer_breathing_exercise"],
                risk_factors={"user_confusion": 0.6, "session_timeout": 0.4},
                fallback_reason=None
            )
            
            fallback_timing = TimingEvaluation(
                timing_appropriate=True,
                timing_confidence=0.8,
                can_proceed=True,
                recommended_delay_minutes=0,
                recent_assistance_check={"last_assistance": "2025-08-19T19:30:00Z"},
                activity_analysis={"current_activity": "meditation", "engagement_level": "medium"},
                cultural_timing={"time_zone": "UTC", "preferred_time": True},
                urgency_override=False
            )
            
            fallback_cultural = CulturalEvaluation(
                culturally_appropriate=True,
                appropriateness_score=0.85,
                content_evaluation={"style": "gentle", "tone": "supportive"},
                timing_evaluation={"cultural_context": "western", "appropriate": True},
                adapted_content=None,
                cultural_considerations=["gentle_guidance", "mindfulness_focused"]
            )
            
            fallback_decision = AssistanceDecision(
                should_provide_assistance=True,
                confidence=0.8,
                reasoning=["User appears confused during meditation", "Optimal timing for gentle guidance"],
                assistance_type=AssistanceType.PROACTIVE_SUPPORT,
                priority_score=0.75,
                user_preferences_respected=True
            )
            
            # Provide sample assistance content
            sample_content = AssistanceContent(
                content_id="demo_guidance_001",
                title="Meditation Guidance",
                content="I notice you might be having some difficulty with your meditation practice. Would you like a gentle reminder about breathing techniques? Remember, it's completely normal for the mind to wander during meditation. The key is to gently bring your attention back to your breath.",
                actions=[
                    "Take three deep, slow breaths",
                    "Focus on the sensation of breathing",
                    "Try counting breaths from 1 to 10"
                ],
                urgency=UrgencyLevel.MEDIUM,
                cultural_adaptations={"tone": "gentle", "style": "supportive"},
                confidence_score=0.8
            )
            
            return AssistanceEvaluation(
                user_id=user_id,
                evaluation_timestamp=datetime.now(timezone.utc),
                intervention_analysis=fallback_intervention,
                timing_evaluation=fallback_timing,
                cultural_evaluation=fallback_cultural,
                assistance_decision=fallback_decision,
                assistance_content=sample_content,
                confidence_score=fallback_decision.confidence,
                metadata={"demo_mode": True, "reason": "Demonstration with sample assistance content"}
            )
        else:
            # Original fallback behavior
            fallback_intervention = InterventionAnalysis(
                intervention_needed=False,
                confidence=0.0,
                intervention_type=None,
                urgency_level=UrgencyLevel.NONE,
                recommended_actions=[],
                risk_factors={},
                fallback_reason="Service unavailable"
            )
            
            fallback_timing = TimingEvaluation(
                timing_appropriate=False,
                timing_confidence=0.0,
                can_proceed=False,
                recommended_delay_minutes=0,
                recent_assistance_check={},
                activity_analysis={},
                cultural_timing={},
                urgency_override=False
            )
            
            fallback_cultural = CulturalEvaluation(
                culturally_appropriate=False,
                appropriateness_score=0.0,
                content_evaluation={},
                timing_evaluation={},
                adapted_content=None,
                cultural_considerations=[]
            )
            
            fallback_decision = AssistanceDecision(
                should_provide_assistance=False,
                confidence=0.0,
                reasoning=["Fallback mode - services unavailable"],
                assistance_type=None,
                priority_score=0.0,
                user_preferences_respected=False
            )
            
            return AssistanceEvaluation(
                user_id=user_id,
                evaluation_timestamp=datetime.now(timezone.utc),
                intervention_analysis=fallback_intervention,
                timing_evaluation=fallback_timing,
                cultural_evaluation=fallback_cultural,
                assistance_decision=fallback_decision,
                assistance_content=None,
                confidence_score=fallback_decision.confidence,
                metadata={"fallback": True, "reason": "Service unavailable"}
            )
    
    def _update_metrics(self, start_time: datetime, success: bool):
        """Update performance metrics"""
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        self.metrics["total_evaluations"] += 1
        self.metrics["total_response_time_ms"] += response_time
        
        if success:
            self.metrics["successful_evaluations"] += 1
        else:
            self.metrics["errors"] += 1
