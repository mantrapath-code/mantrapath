"""
Unit tests for Action Orchestrator models
"""
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.models import (
    VoiceIntent, ActionWorkflow, WorkflowStep, ServiceAction,
    ActionResult, CulturalContext, OrchestrationRequest, OrchestrationResponse
)


class TestVoiceIntent:
    """Test VoiceIntent model"""
    
    def test_voice_intent_creation(self):
        """Test creating a valid voice intent"""
        intent = VoiceIntent(
            text="I want to journal about my day",
            language="en",
            confidence=0.95
        )
        assert intent.text == "I want to journal about my day"
        assert intent.language == "en"
        assert intent.confidence == 0.95
        assert intent.metadata == {}
    
    def test_voice_intent_with_metadata(self):
        """Test creating voice intent with metadata"""
        metadata = {"duration": 3.2, "audio_quality": "good"}
        intent = VoiceIntent(
            text="Schedule meditation",
            language="es",
            confidence=0.88,
            metadata=metadata
        )
        assert intent.metadata == metadata
    
    def test_voice_intent_validation_errors(self):
        """Test voice intent validation errors"""
        # Test invalid confidence
        with pytest.raises(ValidationError):
            VoiceIntent(
                text="test",
                language="en",
                confidence=1.5  # Invalid - must be <= 1.0
            )
        
        # Test invalid language
        with pytest.raises(ValidationError):
            VoiceIntent(
                text="test",
                language="",  # Invalid - must be non-empty
                confidence=0.9
            )
    
    def test_voice_intent_confidence_range(self):
        """Test confidence value range validation"""
        # Valid confidence values
        VoiceIntent(text="test", language="en", confidence=0.0)
        VoiceIntent(text="test", language="en", confidence=1.0)
        
        # Invalid confidence values
        with pytest.raises(ValidationError):
            VoiceIntent(text="test", language="en", confidence=-0.1)


class TestCulturalContext:
    """Test CulturalContext model"""
    
    def test_cultural_context_creation(self):
        """Test creating cultural context"""
        context = CulturalContext(
            country="US",
            timezone="America/New_York",
            language="en"
        )
        assert context.country == "US"
        assert context.timezone == "America/New_York"
        assert context.language == "en"
        assert context.cultural_preferences == {}
    
    def test_cultural_context_with_preferences(self):
        """Test cultural context with preferences"""
        preferences = {
            "communication_style": "direct",
            "formality_level": "casual"
        }
        context = CulturalContext(
            country="JP",
            timezone="Asia/Tokyo",
            language="ja",
            cultural_preferences=preferences
        )
        assert context.cultural_preferences == preferences
    
    def test_cultural_context_validation(self):
        """Test cultural context validation"""
        # Test invalid timezone
        with pytest.raises(ValidationError):
            CulturalContext(
                country="US",
                timezone="Invalid/Timezone",
                language="en"
            )


class TestServiceAction:
    """Test ServiceAction model"""
    
    def test_service_action_creation(self):
        """Test creating service action"""
        action = ServiceAction(
            service="journal_service",
            action="create_entry",
            parameters={"title": "Test", "content": "Test content"}
        )
        assert action.service == "journal_service"
        assert action.action == "create_entry"
        assert action.parameters["title"] == "Test"
        assert action.timeout == 30  # Default value
    
    def test_service_action_with_timeout(self):
        """Test service action with custom timeout"""
        action = ServiceAction(
            service="mood_service",
            action="create_mood",
            parameters={"mood": "happy"},
            timeout=60
        )
        assert action.timeout == 60
    
    def test_service_action_validation(self):
        """Test service action validation"""
        # Test invalid timeout
        with pytest.raises(ValidationError):
            ServiceAction(
                service="test_service",
                action="test_action",
                parameters={},
                timeout=0  # Invalid - must be positive
            )


class TestWorkflowStep:
    """Test WorkflowStep model"""
    
    def test_workflow_step_creation(self):
        """Test creating workflow step"""
        step = WorkflowStep(
            step_id="step_1",
            service="journal_service",
            action="create_entry",
            parameters={"title": "Test"},
            dependencies=[]
        )
        assert step.step_id == "step_1"
        assert step.service == "journal_service"
        assert step.dependencies == []
        assert step.timeout == 30  # Default
    
    def test_workflow_step_with_dependencies(self):
        """Test workflow step with dependencies"""
        step = WorkflowStep(
            step_id="step_2",
            service="analytics_service",
            action="track_event",
            parameters={"event": "journal_created"},
            dependencies=["step_1"],
            timeout=15
        )
        assert step.dependencies == ["step_1"]
        assert step.timeout == 15
    
    def test_workflow_step_validation(self):
        """Test workflow step validation"""
        # Test empty step_id
        with pytest.raises(ValidationError):
            WorkflowStep(
                step_id="",
                service="test_service",
                action="test_action",
                parameters={},
                dependencies=[]
            )


class TestActionResult:
    """Test ActionResult model"""
    
    def test_action_result_success(self):
        """Test successful action result"""
        result = ActionResult(
            step_id="step_1",
            success=True,
            data={"id": "123", "status": "created"},
            execution_time=1.5
        )
        assert result.step_id == "step_1"
        assert result.success is True
        assert result.data["id"] == "123"
        assert result.error_message is None
        assert result.execution_time == 1.5
    
    def test_action_result_failure(self):
        """Test failed action result"""
        result = ActionResult(
            step_id="step_2",
            success=False,
            error_message="Service unavailable",
            execution_time=0.8
        )
        assert result.step_id == "step_2"
        assert result.success is False
        assert result.error_message == "Service unavailable"
        assert result.data == {}
    
    def test_action_result_validation(self):
        """Test action result validation"""
        # Test negative execution time
        with pytest.raises(ValidationError):
            ActionResult(
                step_id="step_1",
                success=True,
                execution_time=-1.0  # Invalid
            )


class TestActionWorkflow:
    """Test ActionWorkflow model"""
    
    def test_action_workflow_creation(self):
        """Test creating action workflow"""
        steps = [
            WorkflowStep(
                step_id="step_1",
                service="journal_service",
                action="create_entry",
                parameters={"title": "Test"},
                dependencies=[]
            )
        ]
        
        workflow = ActionWorkflow(
            workflow_id="wf_123",
            user_id="user123",
            intent_type="journal_creation",
            steps=steps
        )
        assert workflow.workflow_id == "wf_123"
        assert workflow.user_id == "user123"
        assert workflow.intent_type == "journal_creation"
        assert len(workflow.steps) == 1
        assert workflow.status == "pending"  # Default
    
    def test_action_workflow_with_cultural_context(self):
        """Test workflow with cultural context"""
        cultural_context = CulturalContext(
            country="FR",
            timezone="Europe/Paris",
            language="fr"
        )
        
        workflow = ActionWorkflow(
            workflow_id="wf_456",
            user_id="user456",
            intent_type="mood_tracking",
            steps=[],
            cultural_context=cultural_context
        )
        assert workflow.cultural_context.country == "FR"
        assert workflow.cultural_context.language == "fr"
    
    def test_action_workflow_validation(self):
        """Test workflow validation"""
        # Test empty steps
        with pytest.raises(ValidationError):
            ActionWorkflow(
                workflow_id="wf_123",
                user_id="user123",
                intent_type="test",
                steps=[]  # Invalid - must have at least one step
            )


class TestOrchestrationRequest:
    """Test OrchestrationRequest model"""
    
    def test_orchestration_request_creation(self):
        """Test creating orchestration request"""
        voice_intent = VoiceIntent(
            text="I want to meditate",
            language="en",
            confidence=0.9
        )
        
        request = OrchestrationRequest(
            voice_intent=voice_intent,
            user_id="user123"
        )
        assert request.voice_intent.text == "I want to meditate"
        assert request.user_id == "user123"
        assert request.cultural_context is None
    
    def test_orchestration_request_with_cultural_context(self):
        """Test request with cultural context"""
        voice_intent = VoiceIntent(
            text="Quiero meditar",
            language="es",
            confidence=0.85
        )
        
        cultural_context = CulturalContext(
            country="ES",
            timezone="Europe/Madrid",
            language="es"
        )
        
        request = OrchestrationRequest(
            voice_intent=voice_intent,
            user_id="user456",
            cultural_context=cultural_context
        )
        assert request.cultural_context.country == "ES"
        assert request.voice_intent.language == "es"


class TestOrchestrationResponse:
    """Test OrchestrationResponse model"""
    
    def test_orchestration_response_success(self):
        """Test successful orchestration response"""
        results = [
            ActionResult(
                step_id="step_1",
                success=True,
                data={"id": "123"},
                execution_time=1.0
            )
        ]
        
        response = OrchestrationResponse(
            workflow_id="wf_123",
            status="completed",
            results=results,
            execution_time=2.5
        )
        assert response.workflow_id == "wf_123"
        assert response.status == "completed"
        assert len(response.results) == 1
        assert response.execution_time == 2.5
        assert response.error_message is None
    
    def test_orchestration_response_failure(self):
        """Test failed orchestration response"""
        response = OrchestrationResponse(
            workflow_id="wf_456",
            status="failed",
            results=[],
            execution_time=0.5,
            error_message="Service timeout"
        )
        assert response.status == "failed"
        assert response.error_message == "Service timeout"
        assert response.results == []
    
    def test_orchestration_response_validation(self):
        """Test response validation"""
        # Test invalid status
        with pytest.raises(ValidationError):
            OrchestrationResponse(
                workflow_id="wf_123",
                status="invalid_status",
                results=[],
                execution_time=1.0
            )
