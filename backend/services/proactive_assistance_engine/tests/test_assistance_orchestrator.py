"""
Test suite for Proactive Assistance Orchestrator

Comprehensive testing of the main orchestration engine that coordinates
all proactive assistance functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone

from src.core.assistance_orchestrator import ProactiveAssistanceOrchestrator

class TestProactiveAssistanceOrchestrator:
    """
    Test suite for the main assistance orchestrator
    """
    

    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test orchestrator initialization"""
        orchestrator = ProactiveAssistanceOrchestrator()
        
        with patch('src.core.assistance_orchestrator.AIEventProcessorClient') as mock_ai_client, \
             patch('src.core.assistance_orchestrator.AIContextStoreClient') as mock_context_client, \
             patch('src.core.assistance_orchestrator.CulturalIntelligenceClient') as mock_cultural_client:
            
            # Mock client instances
            mock_ai_client_instance = AsyncMock()
            mock_context_client_instance = AsyncMock()
            mock_cultural_client_instance = AsyncMock()
            
            mock_ai_client.return_value = mock_ai_client_instance
            mock_context_client.return_value = mock_context_client_instance
            mock_cultural_client.return_value = mock_cultural_client_instance
            
            # Mock health checks
            mock_ai_client_instance.get_health_status.return_value = {"status": "healthy"}
            mock_context_client_instance.get_health_status.return_value = {"status": "healthy"}
            mock_cultural_client_instance.get_health_status.return_value = {"status": "healthy"}
            
            await orchestrator.initialize()
            
            assert orchestrator.is_initialized is True
            assert orchestrator.ai_event_client is not None
            assert orchestrator.context_store_client is not None
            assert orchestrator.cultural_client is not None
    
    @pytest.mark.asyncio
    async def test_initialization_failure(self):
        """Test orchestrator initialization failure handling"""
        orchestrator = ProactiveAssistanceOrchestrator()
        
        with patch('src.core.assistance_orchestrator.AIEventProcessorClient') as mock_ai_client:
            mock_ai_client.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception, match="Connection failed"):
                await orchestrator.initialize()
            
            assert orchestrator.is_initialized is False
    
    @pytest.mark.asyncio
    async def test_complete_assistance_evaluation_flow(self, assistance_orchestrator):
        """Test complete assistance evaluation from start to finish"""
        
        # Setup mock responses
        user_id = "test_user_123"
        
        # Mock AI Context Store response
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "mood_context": {"current_mood_score": 3.0, "mood_trend": "declining"},
            "cultural_profile": {"primary_culture": "collectivist", "communication_style": "indirect"},
            "recent_interactions": [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "service": "mood", "type": "entry"}
            ]
        }
        
        # Mock AI Event Processor response
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.return_value = {
            "intervention_needed": True,
            "confidence": 0.85,
            "intervention_type": "proactive_support",
            "urgency_level": "medium",
            "recommended_actions": ["Gentle check-in", "Mood support resources"],
            "risk_factors": {"mood_decline": {"score": 0.7}}
        }
        
        # Mock timing evaluation
        assistance_orchestrator.timing_predictor.evaluate_optimal_timing.return_value = {
            "timing_evaluation": {
                "timing_appropriate": True,
                "timing_confidence": 0.8,
                "can_proceed": True,
                "recommended_delay_minutes": 0,
                "recent_assistance_check": {},
                "activity_analysis": {},
                "cultural_timing": {},
                "urgency_override": False
            },
            "timing_score": 0.8
        }
        
        # Mock cultural evaluation
        assistance_orchestrator.cultural_sensitivity_engine.evaluate_cultural_appropriateness.return_value = {
            "culturally_appropriate": True,
            "appropriateness_score": 0.85,
            "content_evaluation": {"appropriateness_score": 0.9},
            "timing_evaluation": {"appropriateness_score": 0.8},
            "adapted_content": None,
            "cultural_considerations": ["Cultural consideration 1", "Cultural consideration 2"]
        }
        
        # Mock help engine
        assistance_orchestrator.help_engine.find_contextual_help.return_value = [
            {
                "content_id": "mood_boost_001",
                "title": "Gentle Mood Support",
                "content": "Support content",
                "actions": ["Action 1", "Action 2"],
                "urgency": "low",
                "cultural_adaptations": {},
                "confidence_score": 0.8
            }
        ]
        
        # Execute assistance evaluation
        evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        
        # Verify evaluation structure
        assert evaluation is not None
        assert evaluation.user_id == user_id
        assert evaluation.intervention_analysis.intervention_needed is True
        assert evaluation.confidence_score > 0.0
        
        # Verify service interactions
        assistance_orchestrator.context_store_client.get_user_context.assert_called_once_with(user_id)
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.assert_called_once_with(user_id)
        assistance_orchestrator.timing_predictor.evaluate_optimal_timing.assert_called_once()
        assistance_orchestrator.cultural_sensitivity_engine.evaluate_cultural_appropriateness.assert_called_once()
        assistance_orchestrator.help_engine.find_contextual_help.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_assistance_evaluation_without_initialization(self):
        """Test that evaluation fails when orchestrator is not initialized"""
        orchestrator = ProactiveAssistanceOrchestrator()
        orchestrator.is_initialized = False
        
        with pytest.raises(RuntimeError, match="Orchestrator not initialized"):
            await orchestrator.evaluate_user_assistance_needs("test_user")
    
    @pytest.mark.asyncio
    async def test_assistance_evaluation_service_failure(self, assistance_orchestrator):
        """Test assistance evaluation when services fail"""
        user_id = "test_user_123"
        
        # Mock service failure
        assistance_orchestrator.context_store_client.get_user_context.side_effect = Exception("Service unavailable")
        
        # Should return fallback evaluation
        evaluation = await assistance_orchestrator.evaluate_user_assistance_needs(user_id)
        
        assert evaluation is not None
        assert evaluation.user_id == user_id
        assert evaluation.confidence_score == 0.0
        assert evaluation.metadata["fallback"] is True
    
    @pytest.mark.asyncio
    async def test_get_user_assistance_status(self, assistance_orchestrator):
        """Test getting user assistance status"""
        user_id = "test_user_123"
        
        # Mock context store response
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "last_assistance_time": "2025-01-01T10:00:00Z",
            "assistance_frequency": "moderate",
            "current_needs": ["mood_support"],
            "assistance_preferences": {"style": "gentle"}
        }
        
        status = await assistance_orchestrator.get_user_assistance_status(user_id)
        
        assert status["user_id"] == user_id
        assert status["status"] == "active"
        assert status["assistance_frequency"] == "moderate"
        assert "mood_support" in status["current_needs"]
    
    @pytest.mark.asyncio
    async def test_get_user_assistance_status_error(self, assistance_orchestrator):
        """Test getting user assistance status when service fails"""
        user_id = "test_user_123"
        
        # Mock service failure
        assistance_orchestrator.context_store_client.get_user_context.side_effect = Exception("Service error")
        
        status = await assistance_orchestrator.get_user_assistance_status(user_id)
        
        assert status["user_id"] == user_id
        assert status["status"] == "error"
        assert "error" in status
    
    @pytest.mark.asyncio
    async def test_trigger_assistance(self, assistance_orchestrator):
        """Test manually triggering assistance"""
        user_id = "test_user_123"
        
        # Mock the internal engines to return successful evaluation
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "mood_context": {"current_mood_score": 3.0, "mood_trend": "declining"},
            "cultural_profile": {"primary_culture": "collectivist", "communication_style": "indirect"},
            "recent_interactions": [{"timestamp": "2025-01-01T10:00:00Z", "service": "mood"}]
        }
        
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.return_value = {
            "intervention_needed": True,
            "confidence": 0.85,
            "intervention_type": "proactive_support",
            "urgency_level": "medium",
            "recommended_actions": ["Gentle check-in"],
            "risk_factors": {"mood_decline": {"score": 0.7}}
        }
        
        assistance_orchestrator.timing_predictor.evaluate_optimal_timing.return_value = {
            "timing_evaluation": {
                "timing_appropriate": True,
                "timing_confidence": 0.8,
                "can_proceed": True,
                "recommended_delay_minutes": 0,
                "recent_assistance_check": {},
                "activity_analysis": {},
                "cultural_timing": {},
                "urgency_override": False
            },
            "timing_score": 0.8
        }
        
        assistance_orchestrator.cultural_sensitivity_engine.evaluate_cultural_appropriateness.return_value = {
            "culturally_appropriate": True,
            "appropriateness_score": 0.85,
            "content_evaluation": {"appropriateness_score": 0.9},
            "timing_evaluation": {"appropriateness_score": 0.8},
            "adapted_content": None,
            "cultural_considerations": ["Cultural consideration 1"]
        }
        
        assistance_orchestrator.help_engine.find_contextual_help.return_value = [
            {
                "content_id": "mood_boost_001",
                "title": "Gentle Mood Support",
                "content": "Support content",
                "actions": ["Action 1", "Action 2"],
                "urgency": "low",
                "cultural_adaptations": {},
                "confidence_score": 0.8
            }
        ]
        
        result = await assistance_orchestrator.trigger_assistance(user_id)
        
        assert result["status"] == "assistance_triggered"
        assert result["user_id"] == user_id
        assert result["assistance_type"] == "proactive_support"
    
    @pytest.mark.asyncio
    async def test_trigger_assistance_no_need(self, assistance_orchestrator):
        """Test triggering assistance when user doesn't need it"""
        user_id = "test_user_123"
        
        # Mock the internal engines to return no assistance needed
        assistance_orchestrator.context_store_client.get_user_context.return_value = {
            "user_id": user_id,
            "mood_context": {"current_mood_score": 7.0, "mood_trend": "stable"},
            "cultural_profile": {"primary_culture": "individualist", "communication_style": "direct"},
            "recent_interactions": [{"timestamp": "2025-01-01T10:00:00Z", "service": "mood"}]
        }
        
        assistance_orchestrator.ai_event_client.analyze_intervention_needs.return_value = {
            "intervention_needed": False,
            "confidence": 0.9,
            "intervention_type": None,
            "urgency_level": "none",
            "recommended_actions": [],
            "risk_factors": {}
        }
        
        result = await assistance_orchestrator.trigger_assistance(user_id)
        
        assert result["status"] == "no_assistance_needed"
        assert result["user_id"] == user_id
    
    @pytest.mark.asyncio
    async def test_trigger_assistance_error(self, assistance_orchestrator):
        """Test triggering assistance when service fails"""
        user_id = "test_user_123"
        
        # Mock service failure
        assistance_orchestrator.context_store_client.get_user_context.side_effect = Exception("Service error")
        
        result = await assistance_orchestrator.trigger_assistance(user_id)
        
        assert result["status"] == "error"
        assert result["user_id"] == user_id
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_get_health_status(self, assistance_orchestrator):
        """Test getting comprehensive health status"""
        # Mock integration status
        assistance_orchestrator.get_integration_status = AsyncMock()
        assistance_orchestrator.get_integration_status.return_value = {
            "ai_event_processor": {"status": "healthy"},
            "ai_context_store": {"status": "healthy"},
            "cultural_intelligence": {"status": "healthy"},
            "overall_status": "healthy",
            "last_check": datetime.now(timezone.utc)
        }
        
        health_status = await assistance_orchestrator.get_health_status()
        
        assert health_status.status == "healthy"
        assert health_status.service == "proactive-assistance-engine"
        assert health_status.version == "1.0.0"
        assert "components" in health_status
        assert "integrations" in health_status
    
    @pytest.mark.asyncio
    async def test_get_health_status_failure(self, assistance_orchestrator):
        """Test getting health status when service fails"""
        # Mock integration status failure
        assistance_orchestrator.get_integration_status = AsyncMock()
        assistance_orchestrator.get_integration_status.side_effect = Exception("Health check failed")
        
        health_status = await assistance_orchestrator.get_health_status()
        
        assert health_status.status == "unhealthy"
        assert health_status.service == "proactive-assistance-engine"
    
    @pytest.mark.asyncio
    async def test_get_integration_status(self, assistance_orchestrator):
        """Test getting integration service status"""
        # Mock client health responses
        assistance_orchestrator.ai_event_client.get_health_status.return_value = {"status": "healthy"}
        assistance_orchestrator.context_store_client.get_health_status.return_value = {"status": "healthy"}
        assistance_orchestrator.cultural_client.get_health_status.return_value = {"status": "healthy"}
        
        integration_status = await assistance_orchestrator.get_integration_status()
        
        assert integration_status.overall_status == "healthy"
        assert integration_status.ai_event_processor["status"] == "healthy"
        assert integration_status.ai_context_store["status"] == "healthy"
        assert integration_status.cultural_intelligence["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_get_integration_status_degraded(self, assistance_orchestrator):
        """Test getting integration status when some services are unhealthy"""
        # Mock mixed health responses
        assistance_orchestrator.ai_event_client.get_health_status.return_value = {"status": "healthy"}
        assistance_orchestrator.context_store_client.get_health_status.return_value = {"status": "unhealthy"}
        assistance_orchestrator.cultural_client.get_health_status.return_value = {"status": "healthy"}
        
        integration_status = await assistance_orchestrator.get_integration_status()
        
        assert integration_status.overall_status == "degraded"
        assert integration_status.ai_event_processor["status"] == "healthy"
        assert integration_status.ai_context_store["status"] == "unhealthy"
        assert integration_status.cultural_intelligence["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_get_integration_status_failure(self, assistance_orchestrator):
        """Test getting integration status when service calls fail"""
        # Mock service failures
        assistance_orchestrator.ai_event_client.get_health_status.side_effect = Exception("Service error")
        assistance_orchestrator.context_store_client.get_health_status.side_effect = Exception("Service error")
        assistance_orchestrator.cultural_client.get_health_status.side_effect = Exception("Service error")
        
        integration_status = await assistance_orchestrator.get_integration_status()
        
        assert integration_status.overall_status == "unknown"
        assert integration_status.ai_event_processor["status"] == "unknown"
        assert integration_status.ai_context_store["status"] == "unknown"
        assert integration_status.cultural_intelligence["status"] == "unknown"
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, assistance_orchestrator):
        """Test getting service performance metrics"""
        # Set up some metrics
        assistance_orchestrator.metrics = {
            "total_evaluations": 100,
            "successful_evaluations": 95,
            "total_response_time_ms": 50000,
            "cultural_adaptations": 80,
            "errors": 5
        }
        
        metrics = await assistance_orchestrator.get_metrics()
        
        assert metrics.total_evaluations == 100
        assert metrics.successful_evaluations == 95
        assert metrics.average_response_time_ms == 500.0
        assert metrics.cultural_adaptation_rate == 0.8
        assert metrics.error_rate == 0.05
        assert metrics.performance_indicators["initialization_status"] is True
    
    @pytest.mark.asyncio
    async def test_get_metrics_no_evaluations(self, assistance_orchestrator):
        """Test getting metrics when no evaluations have been performed"""
        # Reset metrics
        assistance_orchestrator.metrics = {
            "total_evaluations": 0,
            "successful_evaluations": 0,
            "total_response_time_ms": 0,
            "cultural_adaptations": 0,
            "errors": 0
        }
        
        metrics = await assistance_orchestrator.get_metrics()
        
        assert metrics.total_evaluations == 0
        assert metrics.average_response_time_ms == 0.0
        assert metrics.cultural_adaptation_rate == 0.0
        assert metrics.error_rate == 0.0
    
    @pytest.mark.asyncio
    async def test_get_metrics_failure(self, assistance_orchestrator):
        """Test getting metrics when calculation fails"""
        # Mock metrics calculation failure
        assistance_orchestrator.metrics = None
        
        metrics = await assistance_orchestrator.get_metrics()
        
        assert metrics.total_evaluations == 0
        assert metrics.average_response_time_ms == 0.0
        assert metrics.error_rate == 0.0
    
    @pytest.mark.asyncio
    async def test_cleanup(self, assistance_orchestrator):
        """Test orchestrator cleanup"""
        # Mock client close methods
        assistance_orchestrator.ai_event_client.close = AsyncMock()
        assistance_orchestrator.context_store_client.close = AsyncMock()
        assistance_orchestrator.cultural_client.close = AsyncMock()
        
        await assistance_orchestrator.cleanup()
        
        assistance_orchestrator.ai_event_client.close.assert_called_once()
        assistance_orchestrator.context_store_client.close.assert_called_once()
        assistance_orchestrator.cultural_client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cleanup_failure(self, assistance_orchestrator):
        """Test cleanup when some clients fail to close"""
        # Mock client close failures
        assistance_orchestrator.ai_event_client.close = AsyncMock()
        assistance_orchestrator.context_store_client.close = AsyncMock(side_effect=Exception("Close failed"))
        assistance_orchestrator.cultural_client.close = AsyncMock()
        
        # Should not raise exception, should continue cleanup
        await assistance_orchestrator.cleanup()
        
        assistance_orchestrator.ai_event_client.close.assert_called_once()
        assistance_orchestrator.context_store_client.close.assert_called_once()
        assistance_orchestrator.cultural_client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_assistance_decision_making(self, assistance_orchestrator):
        """Test assistance decision making logic"""
        from src.models.assistance_models import InterventionAnalysis, TimingEvaluation, CulturalEvaluation
        
        # Test data as Pydantic models
        intervention_analysis = InterventionAnalysis(
            intervention_needed=True,
            confidence=0.8,
            intervention_type="proactive_support",
            urgency_level="medium",
            recommended_actions=["Action 1"],
            risk_factors={"test": {"score": 0.5}}
        )
    
        timing_evaluation = TimingEvaluation(
            timing_appropriate=True,
            timing_confidence=0.7,
            can_proceed=True,
            recommended_delay_minutes=0,
            recent_assistance_check={},
            activity_analysis={},
            cultural_timing={},
            urgency_override=False
        )
    
        cultural_evaluation = CulturalEvaluation(
            culturally_appropriate=True,
            appropriateness_score=0.9,
            content_evaluation={},
            timing_evaluation={},
            adapted_content=None,
            cultural_considerations=["Consideration 1"]
        )
    
        # Call private method through public interface
        decision = await assistance_orchestrator._make_assistance_decision(
            "test_user", intervention_analysis, timing_evaluation, cultural_evaluation
        )
    
        assert decision.should_provide_assistance is True
        assert decision.confidence > 0.0
        assert len(decision.reasoning) > 0
        assert decision.assistance_type == "proactive_support"
    
    @pytest.mark.asyncio
    async def test_assistance_decision_urgency_override(self, assistance_orchestrator):
        """Test assistance decision with urgency override"""
        from src.models.assistance_models import InterventionAnalysis, TimingEvaluation, CulturalEvaluation
        
        # Test data with urgency override as Pydantic models
        intervention_analysis = InterventionAnalysis(
            intervention_needed=True,
            confidence=0.9,
            intervention_type="crisis_intervention",
            urgency_level="critical",
            recommended_actions=["Action 1"],
            risk_factors={"test": {"score": 0.8}}
        )
    
        timing_evaluation = TimingEvaluation(
            timing_appropriate=False,
            timing_confidence=0.3,
            can_proceed=True,
            recommended_delay_minutes=0,
            recent_assistance_check={},
            activity_analysis={},
            cultural_timing={},
            urgency_override=True
        )
    
        cultural_evaluation = CulturalEvaluation(
            culturally_appropriate=True,
            appropriateness_score=0.8,
            content_evaluation={},
            timing_evaluation={},
            adapted_content=None,
            cultural_considerations=["Consideration 1"]
        )
    
        decision = await assistance_orchestrator._make_assistance_decision(
            "test_user", intervention_analysis, timing_evaluation, cultural_evaluation
        )
    
        assert decision.should_provide_assistance is True
        assert "Timing appropriate for assistance" in decision.reasoning
    
    @pytest.mark.asyncio
    async def test_assistance_decision_failure(self, assistance_orchestrator):
        """Test assistance decision making when analysis fails"""
        # Test data with missing fields
        intervention_analysis = {}
        timing_evaluation = {}
        cultural_evaluation = {}
        
        decision = await assistance_orchestrator._make_assistance_decision(
            "test_user", intervention_analysis, timing_evaluation, cultural_evaluation
        )
        
        assert decision.should_provide_assistance is False
        assert decision.confidence == 0.0
        assert "Error in decision making" in decision.reasoning
    
    @pytest.mark.asyncio
    async def test_fallback_evaluation_creation(self, assistance_orchestrator):
        """Test fallback evaluation creation"""
        user_id = "test_user_123"
        
        fallback_evaluation = assistance_orchestrator._create_fallback_evaluation(user_id)
        
        assert fallback_evaluation.user_id == user_id
        assert fallback_evaluation.confidence_score == 0.0
        assert fallback_evaluation.metadata["fallback"] is True
        assert fallback_evaluation.metadata["reason"] == "Service unavailable"
        assert fallback_evaluation.intervention_analysis.intervention_needed is False
        assert fallback_evaluation.timing_evaluation.timing_appropriate is False
        assert fallback_evaluation.cultural_evaluation.culturally_appropriate is False
    
    @pytest.mark.asyncio
    async def test_metrics_update(self, assistance_orchestrator):
        """Test metrics update functionality"""
        # Reset metrics
        assistance_orchestrator.metrics = {
            "total_evaluations": 0,
            "successful_evaluations": 0,
            "total_response_time_ms": 0,
            "cultural_adaptations": 0,
            "errors": 0
        }
        
        start_time = datetime.now()
        
        # Update metrics for successful evaluation
        assistance_orchestrator._update_metrics(start_time, True)
        
        assert assistance_orchestrator.metrics["total_evaluations"] == 1
        assert assistance_orchestrator.metrics["successful_evaluations"] == 1
        assert assistance_orchestrator.metrics["errors"] == 0
        assert assistance_orchestrator.metrics["total_response_time_ms"] > 0
        
        # Update metrics for failed evaluation
        start_time = datetime.now()
        assistance_orchestrator._update_metrics(start_time, False)
        
        assert assistance_orchestrator.metrics["total_evaluations"] == 2
        assert assistance_orchestrator.metrics["successful_evaluations"] == 1
        assert assistance_orchestrator.metrics["errors"] == 1
