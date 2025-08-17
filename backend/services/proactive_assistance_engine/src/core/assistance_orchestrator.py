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

from src.integrations.ai_event_processor_client import AIEventProcessorClient
from src.integrations.ai_context_store_client import AIContextStoreClient
from src.integrations.cultural_intelligence_client import CulturalIntelligenceClient
from src.integrations.models_service_client import ProactiveModelsServiceClient  # NEW
from src.core.timing_predictor import ComprehensiveTimingPredictor
from src.core.contextual_help_engine import ContextualHelpEngine
from src.core.cultural_sensitivity_engine import CulturalSensitivityEngine
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
    
    async def initialize(self):
        """Initialize orchestrator with service clients"""
        try:
            # Initialize service clients
            self.ai_event_client = AIEventProcessorClient("http://localhost:8014")
            self.context_store_client = AIContextStoreClient("http://localhost:8013")
            self.cultural_client = CulturalIntelligenceClient("http://localhost:8017")
            self.models_service_client = ProactiveModelsServiceClient("http://models-service:8080")  # NEW
            
            # Initialize core engines
            self.timing_predictor = ComprehensiveTimingPredictor()
            self.help_engine = ContextualHelpEngine()
            self.cultural_sensitivity_engine = CulturalSensitivityEngine()
            
            # Test connections
            await self._test_service_connections()
            
            self.is_initialized = True
            logger.info("Proactive Assistance Orchestrator initialized successfully with Models Service")
            
        except Exception as e:
            logger.error("Failed to initialize orchestrator", error=str(e))
            raise
    
    async def evaluate_user_assistance_needs(self, user_id: str) -> AssistanceEvaluation:
        """
        Main method: Evaluate if user needs proactive assistance
        """
        start_time = datetime.now()
        
        try:
            if not self.is_initialized:
                raise RuntimeError("Orchestrator not initialized")
            
            logger.info("Evaluating assistance needs", user_id=user_id)
            
            # Step 1: Get user context from AI Context Store
            user_context = await self.context_store_client.get_user_context(user_id)
            
            # Step 2: Get intervention analysis from AI Event Processor
            intervention_analysis_data = await self.ai_event_client.analyze_intervention_needs(user_id)
            intervention_analysis = InterventionAnalysis(**intervention_analysis_data)
            
            # Step 3: Evaluate timing appropriateness
            timing_evaluation_data = await self.timing_predictor.evaluate_optimal_timing(
                user_id, user_context, intervention_analysis_data
            )
            timing_evaluation = TimingEvaluation(**timing_evaluation_data["timing_evaluation"])
            
            # Step 4: Get cultural considerations
            cultural_evaluation_data = await self.cultural_sensitivity_engine.evaluate_cultural_appropriateness(
                user_context.get("cultural_profile", {}), intervention_analysis_data
            )
            cultural_evaluation = CulturalEvaluation(**cultural_evaluation_data)
            
            # Step 5: Make final assistance decision
            assistance_decision = await self._make_assistance_decision(
                user_id, intervention_analysis, timing_evaluation, cultural_evaluation
            )
            
            # Step 6: If assistance needed, prepare assistance content
            assistance_content = None
            if assistance_decision.should_provide_assistance:
                assistance_content_data = await self.help_engine.find_contextual_help(
                    user_context, intervention_analysis_data, cultural_evaluation_data
                )
                if assistance_content_data:
                    assistance_content = AssistanceContent(**assistance_content_data[0]) if assistance_content_data else None
            
            # Create comprehensive evaluation result
            evaluation = AssistanceEvaluation(
                user_id=user_id,
                evaluation_timestamp=datetime.now(timezone.utc),
                intervention_analysis=intervention_analysis,
                timing_evaluation=timing_evaluation,
                cultural_evaluation=cultural_evaluation,
                assistance_decision=assistance_decision,
                assistance_content=assistance_content,
                confidence_score=assistance_decision.confidence
            )
            
            # Update metrics
            self._update_metrics(start_time, True)
            
            logger.info(
                "Assistance evaluation completed",
                user_id=user_id,
                assistance_needed=assistance_decision.should_provide_assistance,
                confidence=assistance_decision.confidence
            )
            
            return evaluation
            
        except RuntimeError:
            # Re-raise RuntimeError (e.g., "Orchestrator not initialized")
            raise
        except Exception as e:
            self._update_metrics(start_time, False)
            logger.error("Assistance evaluation failed", error=str(e), user_id=user_id)
            # Return safe fallback evaluation
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
            if evaluation.assistance_decision["should_provide_assistance"]:
                return {
                    "status": "assistance_triggered",
                    "user_id": user_id,
                    "assistance_type": evaluation.assistance_decision["assistance_type"],
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
    
    def _create_fallback_evaluation(self, user_id: str) -> AssistanceEvaluation:
        """Create safe fallback evaluation when services are unavailable"""
        fallback_intervention = InterventionAnalysis(
            intervention_needed=False,
            confidence=0.0,
            intervention_type=None,
            urgency_level="none",
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
            confidence_score=0.0,
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
