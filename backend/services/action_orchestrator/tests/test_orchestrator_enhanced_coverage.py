"""
Additional test coverage for orchestrator features
Testing newly added service coordination and workflow management methods
"""
import pytest
import asyncio
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from src.core.orchestrator import ActionOrchestrator
from src.core.intent_classifier import IntentClassifier
from src.core.cultural_processor import CulturalProcessor
from src.core.workflow_builder import WorkflowBuilder
from src.core.action_dispatcher import ActionDispatcher
from src.core.rollback_manager import RollbackManager
from src.models import (
    VoiceIntent, IntentType, ConfidenceLevel, CulturalContext, 
    WorkflowStatus, ActionWorkflow, WorkflowStep
)


@pytest.mark.asyncio
class TestOrchestratorEnhancedFeatures:
    """Test enhanced orchestrator features for 80% coverage"""

    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        intent_classifier = MagicMock(spec=IntentClassifier)
        cultural_processor = MagicMock(spec=CulturalProcessor)
        workflow_builder = MagicMock(spec=WorkflowBuilder)
        action_dispatcher = MagicMock(spec=ActionDispatcher)
        rollback_manager = MagicMock(spec=RollbackManager)
        
        return ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )

    @pytest.fixture
    def sample_intent(self):
        """Create sample intent for testing"""
        cultural_context = CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )
        
        return VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            raw_text="I want to write in my journal",
            processed_text="I want to write in my journal",
            parameters={"action": "create", "content_type": "journal"},
            cultural_context=cultural_context,
            user_id=uuid4()
        )

    async def test_rollback_workflow_success(self, orchestrator, sample_intent):
        """Test successful workflow rollback"""
        workflow_id = uuid4()
        workflow = ActionWorkflow(
            intent=sample_intent,
            steps=[],
            status=WorkflowStatus.COMPLETED,
            cultural_context=sample_intent.cultural_context
        )
        
        orchestrator.active_workflows[workflow_id] = workflow
        orchestrator.rollback_manager.rollback_workflow = AsyncMock()
        
        result = await orchestrator.rollback_workflow(workflow_id)
        
        assert result["workflow_id"] == str(workflow_id)
        assert result["rollback_status"] == "completed"
        assert workflow.status == WorkflowStatus.ROLLED_BACK

    async def test_rollback_workflow_not_found(self, orchestrator):
        """Test rollback for non-existent workflow"""
        workflow_id = uuid4()
        
        result = await orchestrator.rollback_workflow(workflow_id)
        
        assert result["workflow_id"] == str(workflow_id)
        assert result["rollback_status"] == "not_found"

    async def test_rollback_workflow_failure(self, orchestrator, sample_intent):
        """Test workflow rollback failure handling"""
        workflow_id = uuid4()
        workflow = ActionWorkflow(
            intent=sample_intent,
            steps=[],
            status=WorkflowStatus.COMPLETED,
            cultural_context=sample_intent.cultural_context
        )
        
        orchestrator.active_workflows[workflow_id] = workflow
        # Mock the _trigger_rollback method that's actually called
        orchestrator._trigger_rollback = AsyncMock(side_effect=Exception("Rollback failed"))
        
        result = await orchestrator.rollback_workflow(workflow_id)
        
        assert result["workflow_id"] == str(workflow_id)
        assert result["rollback_status"] == "failed"
        assert "error" in result

    async def test_estimate_workflow_duration(self, orchestrator, sample_intent):
        """Test workflow duration estimation"""
        duration = await orchestrator.estimate_workflow_duration(sample_intent)
        
        assert isinstance(duration, int)
        assert duration > 0
        # Journal entry should have 2.0 multiplier -> 2000ms
        assert duration == 2000

    async def test_estimate_workflow_duration_unknown_intent(self, orchestrator):
        """Test duration estimation for unknown intent"""
        cultural_context = CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )
        
        unknown_intent = VoiceIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.5,
            confidence_level=ConfidenceLevel.MEDIUM,
            raw_text="unknown request",
            processed_text="unknown request",
            parameters={},
            cultural_context=cultural_context,
            user_id=uuid4()
        )
        
        duration = await orchestrator.estimate_workflow_duration(unknown_intent)
        assert duration == 1000  # Default multiplier 1.0

    async def test_validate_workflow_feasibility_supported(self, orchestrator, sample_intent):
        """Test workflow feasibility validation for supported intent"""
        result = await orchestrator.validate_workflow_feasibility(sample_intent)
        
        assert result["feasible"] is True
        assert "estimated_duration_ms" in result
        assert "required_services" in result
        assert "confidence_assessment" in result

    async def test_validate_workflow_feasibility_unsupported(self, orchestrator):
        """Test workflow feasibility validation for unsupported intent"""
        cultural_context = CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )
        
        unsupported_intent = VoiceIntent(
            intent_type=IntentType.CRISIS_INTERVENTION,  # Not in supported list
            confidence=0.9,
            confidence_level=ConfidenceLevel.HIGH,
            raw_text="crisis request",
            processed_text="crisis request",
            parameters={},
            cultural_context=cultural_context,
            user_id=uuid4()
        )
        
        result = await orchestrator.validate_workflow_feasibility(unsupported_intent)
        
        assert result["feasible"] is False
        assert "not supported" in result["reason"]

    async def test_validate_workflow_feasibility_low_confidence(self, orchestrator):
        """Test workflow feasibility validation for low confidence intent"""
        cultural_context = CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )
        
        low_confidence_intent = VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence=0.1,
            confidence_level=ConfidenceLevel.VERY_LOW,
            raw_text="maybe journal",
            processed_text="maybe journal",
            parameters={},
            cultural_context=cultural_context,
            user_id=uuid4()
        )
        
        result = await orchestrator.validate_workflow_feasibility(low_confidence_intent)
        
        assert result["feasible"] is False
        assert "confidence too low" in result["reason"]

    async def test_get_required_services(self, orchestrator, sample_intent):
        """Test getting required services for different intents"""
        # Test journal entry
        services = orchestrator._get_required_services(sample_intent)
        assert "journal_service" in services
        assert "analytics_service" in services
        
        # Test unknown intent
        cultural_context = CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )
        
        unknown_intent = VoiceIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.5,
            confidence_level=ConfidenceLevel.MEDIUM,
            raw_text="unknown",
            processed_text="unknown",
            parameters={},
            cultural_context=cultural_context,
            user_id=uuid4()
        )
        
        services = orchestrator._get_required_services(unknown_intent)
        assert services == ["general_service"]

    async def test_get_required_services_all_intents(self, orchestrator):
        """Test required services for all intent types"""
        cultural_context = CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )
        
        test_cases = [
            (IntentType.MOOD_TRACKING, ["mood_service", "analytics_service"]),
            (IntentType.CHAT_CONVERSATION, ["chatbot_service"]),
            (IntentType.COMMUNITY_INTERACTION, ["community_service", "profile_service"]),
            (IntentType.PROFILE_UPDATE, ["profile_service"]),
            (IntentType.ANALYTICS_QUERY, ["analytics_service"]),
            (IntentType.CONTENT_SEARCH, ["search_service", "content_service"]),
            (IntentType.VOICE_COMMAND, ["command_service"])
        ]
        
        for intent_type, expected_services in test_cases:
            intent = VoiceIntent(
                intent_type=intent_type,
                confidence=0.8,
                confidence_level=ConfidenceLevel.HIGH,
                raw_text="test",
                processed_text="test",
                parameters={},
                cultural_context=cultural_context,
                user_id=uuid4()
            )
            
            services = orchestrator._get_required_services(intent)
            assert services == expected_services

    async def test_supported_intents_list(self, orchestrator):
        """Test that supported intents list contains expected intents"""
        intents = await orchestrator.get_supported_intents()
        
        expected_intents = [
            IntentType.JOURNAL_ENTRY,
            IntentType.MOOD_TRACKING,
            IntentType.CHAT_CONVERSATION,
            IntentType.COMMUNITY_INTERACTION,
            IntentType.PROFILE_UPDATE,
            IntentType.ANALYTICS_QUERY,
            IntentType.CONTENT_SEARCH,
            IntentType.VOICE_COMMAND
        ]
        
        assert all(intent in intents for intent in expected_intents)
        assert len(intents) == len(expected_intents)

    async def test_metrics_with_supported_intents(self, orchestrator):
        """Test metrics include supported intents count"""
        metrics = orchestrator.get_metrics()
        
        assert "supported_intents" in metrics
        assert metrics["supported_intents"] == 8  # Number of supported intents

    async def test_feasibility_validation_error_handling(self, orchestrator):
        """Test error handling in feasibility validation"""
        # Mock get_supported_intents to raise an exception
        orchestrator.get_supported_intents = AsyncMock(side_effect=Exception("Service error"))
        
        cultural_context = CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )
        
        intent = VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence=0.8,
            confidence_level=ConfidenceLevel.HIGH,
            raw_text="test",
            processed_text="test",
            parameters={},
            cultural_context=cultural_context,
            user_id=uuid4()
        )
        
        result = await orchestrator.validate_workflow_feasibility(intent)
        
        assert result["feasible"] is False
        assert "Validation error" in result["reason"]

    async def test_duration_estimation_error_handling(self, orchestrator):
        """Test error handling in duration estimation"""
        # Test with None intent_type (which uses default multiplier 1.0)
        intent = MagicMock()
        intent.intent_type = None
        
        duration = await orchestrator.estimate_workflow_duration(intent)
        
        # Should return base duration with default multiplier (1000ms)
        assert duration == 1000
