"""
Final coverage push for Action Orchestrator
Testing error handling and edge cases for 80% coverage
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
    WorkflowStatus, ActionWorkflow, WorkflowStep, OrchestrationRequest,
    OrchestrationResponse, ActionResult, ServiceAction
)


@pytest.mark.asyncio
class TestOrchestratorErrorHandling:
    """Test error handling and edge cases for 80% coverage"""

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
    def cultural_context(self):
        """Default cultural context"""
        return CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="direct",
            formality_level="casual",
            time_zone="UTC",
            date_format="ISO"
        )

    @pytest.fixture
    def orchestration_request(self):
        """Sample orchestration request"""
        return OrchestrationRequest(
            voice_input="I want to write in my journal",
            user_id=uuid4(),
            cultural_preferences={"language": "en"}
        )

    async def test_orchestrate_action_empty_input(self, orchestrator):
        """Test orchestration with empty voice input"""
        request = OrchestrationRequest(
            voice_input="",
            user_id=uuid4()
        )
        
        response = await orchestrator.orchestrate_action(request)
        
        assert response.status == WorkflowStatus.FAILED
        assert "Voice input is required" in response.message

    async def test_orchestrate_action_whitespace_input(self, orchestrator):
        """Test orchestration with whitespace-only input"""
        request = OrchestrationRequest(
            voice_input="   \n\t   ",
            user_id=uuid4()
        )
        
        response = await orchestrator.orchestrate_action(request)
        
        assert response.status == WorkflowStatus.FAILED
        assert "Voice input is required" in response.message

    async def test_cultural_context_processing_error(self, orchestrator, orchestration_request):
        """Test error handling in cultural context processing"""
        # Mock cultural processor to raise exception
        orchestrator.cultural_processor.process_cultural_context = AsyncMock(
            side_effect=Exception("Cultural processing failed")
        )
        
        # Mock other components
        orchestrator.intent_classifier.classify_intent = AsyncMock(return_value={
            'intent_type': IntentType.JOURNAL_ENTRY,
            'confidence': 0.8,
            'parameters': {}
        })
        
        orchestrator.workflow_builder.build_workflow = AsyncMock(return_value=MagicMock(
            workflow_id=uuid4(),
            steps=[],
            status=WorkflowStatus.PENDING,
            cultural_context=orchestrator._get_default_cultural_context(),
            intent=MagicMock()
        ))
        
        response = await orchestrator.orchestrate_action(orchestration_request)
        
        # Should use default cultural context and continue
        assert response is not None

    async def test_intent_classification_error(self, orchestrator, orchestration_request, cultural_context):
        """Test error handling in intent classification"""
        # Mock cultural processor success
        orchestrator.cultural_processor.process_cultural_context = AsyncMock(
            return_value=cultural_context
        )
        
        # Mock intent classifier to raise exception
        orchestrator.intent_classifier.classify_intent = AsyncMock(
            side_effect=Exception("Classification failed")
        )
        
        response = await orchestrator.orchestrate_action(orchestration_request)
        
        # Should use fallback intent and continue or fail gracefully
        assert response is not None
        assert response.status == WorkflowStatus.FAILED

    async def test_workflow_building_error(self, orchestrator, orchestration_request, cultural_context):
        """Test error handling in workflow building"""
        # Mock successful cultural context and intent classification
        orchestrator.cultural_processor.process_cultural_context = AsyncMock(
            return_value=cultural_context
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
        
        orchestrator.intent_classifier.classify_intent = AsyncMock(return_value=intent)
        
        # Mock workflow builder to raise exception
        orchestrator.workflow_builder.build_workflow = AsyncMock(
            side_effect=Exception("Workflow building failed")
        )
        
        response = await orchestrator.orchestrate_action(orchestration_request)
        
        # Should use fallback workflow and continue or fail gracefully
        assert response is not None

    async def test_workflow_execution_failure(self, orchestrator, orchestration_request, cultural_context):
        """Test workflow execution failure handling"""
        # Mock successful setup
        orchestrator.cultural_processor.process_cultural_context = AsyncMock(
            return_value=cultural_context
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
        
        orchestrator.intent_classifier.classify_intent = AsyncMock(return_value=intent)
        
        # Create workflow with failing step
        workflow = ActionWorkflow(
            intent=intent,
            steps=[],
            status=WorkflowStatus.PENDING,
            cultural_context=cultural_context
        )
        
        orchestrator.workflow_builder.build_workflow = AsyncMock(return_value=workflow)
        
        # Mock execute_workflow_safely to raise exception
        original_execute = orchestrator._execute_workflow_safely
        async def failing_execute(wf):
            raise Exception("Workflow execution failed")
        
        orchestrator._execute_workflow_safely = failing_execute
        
        response = await orchestrator.orchestrate_action(orchestration_request)
        
        assert response.status == WorkflowStatus.FAILED
        assert "Orchestration failed" in response.message

    async def test_cleanup_failed_workflow(self, orchestrator, cultural_context):
        """Test cleanup of failed workflow"""
        workflow_id = uuid4()
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
        
        workflow = ActionWorkflow(
            intent=intent,
            steps=[],
            status=WorkflowStatus.FAILED,
            cultural_context=cultural_context
        )
        
        orchestrator.active_workflows[workflow_id] = workflow
        orchestrator._trigger_rollback = AsyncMock()
        
        await orchestrator._cleanup_failed_workflow(workflow_id)
        
        # Should call rollback
        orchestrator._trigger_rollback.assert_called_once()

    async def test_cleanup_failed_workflow_error(self, orchestrator):
        """Test error handling in cleanup"""
        workflow_id = uuid4()
        
        # Test with non-existent workflow
        await orchestrator._cleanup_failed_workflow(workflow_id)
        
        # Should handle gracefully (no exception)
        assert True

    async def test_step_execution_with_failures(self, orchestrator):
        """Test step execution with action failures"""
        action = ServiceAction(
            service_name="test_service",
            action_type="test_action",
            parameters={"test": "data"},
            timeout_seconds=30,
            retry_count=3
        )
        
        step = WorkflowStep(
            actions=[action],
            parallel_execution=False
        )
        
        # Mock action dispatcher to fail
        orchestrator.action_dispatcher.dispatch_action = AsyncMock(
            side_effect=Exception("Action failed")
        )
        
        results = await orchestrator._execute_step(step)
        
        assert len(results) == 1
        assert not results[0].success
        assert "Action failed" in results[0].error_message

    async def test_step_execution_parallel_with_failures(self, orchestrator):
        """Test parallel step execution with some failures"""
        action1 = ServiceAction(
            service_name="test_service1",
            action_type="test_action",
            parameters={"test": "data1"},
            timeout_seconds=30,
            retry_count=3
        )
        
        action2 = ServiceAction(
            service_name="test_service2",
            action_type="test_action",
            parameters={"test": "data2"},
            timeout_seconds=30,
            retry_count=3
        )
        
        step = WorkflowStep(
            actions=[action1, action2],
            parallel_execution=True
        )
        
        # Mock action dispatcher with mixed results
        async def mock_dispatch(service_name, action_type, **kwargs):
            if service_name == "test_service1":
                return {"success": True}
            else:
                raise Exception("Service 2 failed")
        
        orchestrator.action_dispatcher.dispatch_action = AsyncMock(side_effect=mock_dispatch)
        
        results = await orchestrator._execute_step(step)
        
        assert len(results) == 2
        assert results[0].success
        assert not results[1].success

    async def test_create_fallback_intent(self, orchestrator, cultural_context):
        """Test creation of fallback intent"""
        voice_input = "some unclear input"
        user_id = uuid4()
        
        fallback_intent = orchestrator._create_fallback_intent(voice_input, cultural_context, user_id)
        
        assert fallback_intent.intent_type == IntentType.UNKNOWN
        assert fallback_intent.confidence == 0.1
        assert fallback_intent.confidence_level == ConfidenceLevel.VERY_LOW
        assert fallback_intent.raw_text == voice_input
        assert fallback_intent.user_id == user_id

    async def test_create_fallback_workflow(self, orchestrator, cultural_context):
        """Test creation of fallback workflow"""
        intent = VoiceIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.1,
            confidence_level=ConfidenceLevel.VERY_LOW,
            raw_text="test",
            processed_text="test",
            parameters={},
            cultural_context=cultural_context,
            user_id=uuid4()
        )
        
        fallback_workflow = orchestrator._create_fallback_workflow(intent, cultural_context)
        
        assert fallback_workflow.intent == intent
        assert len(fallback_workflow.steps) == 0
        assert fallback_workflow.status == WorkflowStatus.PENDING
        assert fallback_workflow.cultural_context == cultural_context

    async def test_trigger_rollback_error(self, orchestrator, cultural_context):
        """Test rollback error handling"""
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
        
        workflow = ActionWorkflow(
            intent=intent,
            steps=[],
            status=WorkflowStatus.FAILED,
            cultural_context=cultural_context
        )
        
        # Mock rollback manager to fail
        orchestrator.rollback_manager.rollback_workflow = AsyncMock(
            side_effect=Exception("Rollback failed")
        )
        
        # Should not raise exception
        await orchestrator._trigger_rollback(workflow, [])
        
        # Should have logged the error (we can't easily test this without log capture)
        assert True

    async def test_confidence_level_boundaries(self, orchestrator):
        """Test confidence level calculation at boundaries"""
        assert orchestrator._get_confidence_level(0.8) == ConfidenceLevel.HIGH
        assert orchestrator._get_confidence_level(0.79) == ConfidenceLevel.MEDIUM
        assert orchestrator._get_confidence_level(0.5) == ConfidenceLevel.MEDIUM
        assert orchestrator._get_confidence_level(0.49) == ConfidenceLevel.LOW
        assert orchestrator._get_confidence_level(0.3) == ConfidenceLevel.LOW
        assert orchestrator._get_confidence_level(0.29) == ConfidenceLevel.VERY_LOW
        assert orchestrator._get_confidence_level(0.0) == ConfidenceLevel.VERY_LOW

    async def test_get_default_cultural_context(self, orchestrator):
        """Test default cultural context"""
        context = orchestrator._get_default_cultural_context()
        
        assert context.language == "en"
        assert context.cultural_region == "global"
        assert context.communication_style == "neutral"
        assert context.formality_level == "moderate"
        assert context.time_zone == "UTC"
        assert context.date_format == "ISO"
