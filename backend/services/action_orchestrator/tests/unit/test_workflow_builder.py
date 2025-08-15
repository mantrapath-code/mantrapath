"""
Unit tests for Workflow Builder
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.core.workflow_builder import WorkflowBuilder
from src.models import CulturalContext, IntentType, ConfidenceLevel


class TestWorkflowBuilder:
    """Test WorkflowBuilder functionality"""
    
    @pytest.fixture
    def workflow_builder(self):
        """Create workflow builder instance"""
        return WorkflowBuilder()
    
    @pytest.fixture
    def sample_intent_result(self):
        """Sample intent classification result"""
        return {
            "intent_type": "journal_creation",
            "confidence": 0.95,
            "entities": {
                "activity": ["meditation"],
                "sentiment": "positive",
                "duration": "30 minutes"
            },
            "suggested_services": ["journal_service", "mood_service", "analytics_service"]
        }
    
    @pytest.fixture
    def sample_cultural_context(self):
        """Sample cultural context"""
        return CulturalContext(
            language="en",
            cultural_region="US",
            communication_style="direct",
            formality_level="casual"
        )
    
    @pytest.mark.asyncio
    async def test_build_workflow_journal_creation(self, workflow_builder, sample_intent_result, sample_cultural_context):
        """Test building workflow for journal creation intent"""
        user_id = uuid4()
        
        workflow = await workflow_builder.build_workflow(
            sample_intent_result,
            user_id,
            sample_cultural_context
        )
        
        assert workflow.user_id == user_id
        assert workflow.cultural_context == sample_cultural_context
        assert len(workflow.steps) > 0
        
        # Check that journal service action is included
        journal_actions = []
        for step in workflow.steps:
            for action in step.actions:
                if action.service_name == "journal_service":
                    journal_actions.append(action)
        
        assert len(journal_actions) > 0
        assert journal_actions[0].action_type == "create_entry"
    
    @pytest.mark.asyncio
    async def test_build_workflow_mood_tracking(self, workflow_builder, sample_cultural_context):
        """Test building workflow for mood tracking intent"""
        intent_result = {
            "intent_type": "mood_tracking",
            "confidence": 0.88,
            "entities": {
                "sentiment": "positive",
                "emotions": ["happy", "peaceful"],
                "context": "after meditation"
            },
            "suggested_services": ["mood_service", "analytics_service"]
        }
        
        user_id = uuid4()
        workflow = await workflow_builder.build_workflow(
            intent_result,
            user_id,
            sample_cultural_context
        )
        
        # Check mood service action
        mood_actions = []
        for step in workflow.steps:
            for action in step.actions:
                if action.service_name == "mood_service":
                    mood_actions.append(action)
        
        assert len(mood_actions) > 0
        assert mood_actions[0].action_type == "create_mood_entry"
        assert mood_actions[0].parameters["sentiment"] == "positive"
    
    @pytest.mark.asyncio
    async def test_build_workflow_community_sharing(self, workflow_builder, sample_cultural_context):
        """Test building workflow for community sharing intent"""
        intent_result = {
            "intent_type": "community_sharing",
            "confidence": 0.92,
            "entities": {
                "activity": ["meditation"],
                "share_type": "progress",
                "visibility": "public"
            },
            "suggested_services": ["community_service", "profile_service"]
        }
        
        user_id = uuid4()
        workflow = await workflow_builder.build_workflow(
            intent_result,
            user_id,
            sample_cultural_context
        )
        
        # Check community service action
        community_actions = []
        for step in workflow.steps:
            for action in step.actions:
                if action.service_name == "community_service":
                    community_actions.append(action)
        
        assert len(community_actions) > 0
        assert community_actions[0].action_type == "share_content"
    
    @pytest.mark.asyncio
    async def test_build_workflow_with_dependencies(self, workflow_builder, sample_cultural_context):
        """Test building workflow with service dependencies"""
        intent_result = {
            "intent_type": "journal_with_mood",  # Custom combined intent
            "confidence": 0.90,
            "entities": {
                "activity": ["meditation"],
                "sentiment": "positive",
                "duration": "20 minutes"
            },
            "suggested_services": ["journal_service", "mood_service", "analytics_service"]
        }
        
        user_id = uuid4()
        workflow = await workflow_builder.build_workflow(
            intent_result,
            user_id,
            sample_cultural_context
        )
        
        # Should have multiple steps with dependencies
        assert len(workflow.steps) >= 2
        
        # Find dependent steps
        dependent_steps = [step for step in workflow.steps if len(step.dependencies) > 0]
        assert len(dependent_steps) > 0
    
    def test_create_journal_action(self, workflow_builder):
        """Test creating journal service action"""
        entities = {
            "activity": ["meditation"],
            "sentiment": "positive",
            "duration": "30 minutes"
        }
        
        action = workflow_builder._create_journal_action(entities, str(uuid4()))
        
        assert action.service_name == "journal_service"
        assert action.action_type == "create_entry"
        assert "meditation" in action.parameters["content"]
        assert action.parameters["tags"] == ["meditation"]
    
    def test_create_mood_action(self, workflow_builder):
        """Test creating mood service action"""
        entities = {
            "sentiment": "positive",
            "emotions": ["happy", "peaceful"],
            "context": "after meditation"
        }
        
        action = workflow_builder._create_mood_action(entities, str(uuid4()))
        
        assert action.service_name == "mood_service"
        assert action.action_type == "create_mood_entry"
        assert action.parameters["sentiment"] == "positive"
        assert action.parameters["emotions"] == ["happy", "peaceful"]
    
    def test_create_community_action(self, workflow_builder):
        """Test creating community service action"""
        entities = {
            "activity": ["meditation"],
            "share_type": "progress",
            "visibility": "public"
        }
        
        action = workflow_builder._create_community_action(entities, str(uuid4()))
        
        assert action.service_name == "community_service"
        assert action.action_type == "share_content"
        assert action.parameters["content_type"] == "progress"
        assert action.parameters["visibility"] == "public"
    
    def test_create_chatbot_action(self, workflow_builder):
        """Test creating chatbot service action"""
        entities = {
            "question": "How to meditate better?",
            "topic": "meditation",
            "context": "beginner"
        }
        
        action = workflow_builder._create_chatbot_action(entities, str(uuid4()))
        
        assert action.service_name == "chatbot_service"
        assert action.action_type == "process_conversation"
        assert action.parameters["message"] == "How to meditate better?"
        assert action.parameters["context"] == "beginner"
    
    def test_create_profile_action(self, workflow_builder):
        """Test creating profile service action"""
        entities = {
            "update_type": "preferences",
            "field": "meditation_goal",
            "value": "30 minutes daily"
        }
        
        action = workflow_builder._create_profile_action(entities, str(uuid4()))
        
        assert action.service_name == "profile_service"
        assert action.action_type == "update_profile"
        assert action.parameters["field"] == "meditation_goal"
        assert action.parameters["value"] == "30 minutes daily"
    
    def test_create_analytics_action(self, workflow_builder):
        """Test creating analytics service action"""
        entities = {
            "request_type": "progress",
            "time_period": "month",
            "activity": ["meditation"]
        }
        
        action = workflow_builder._create_analytics_action(entities, str(uuid4()))
        
        assert action.service_name == "analytics_service"
        assert action.action_type == "generate_report"
        assert action.parameters["report_type"] == "progress"
        assert action.parameters["time_period"] == "month"
    
    def test_determine_step_dependencies_journal_mood(self, workflow_builder):
        """Test determining dependencies for journal and mood actions"""
        actions = [
            MagicMock(service_name="journal_service", action_id=uuid4()),
            MagicMock(service_name="mood_service", action_id=uuid4()),
            MagicMock(service_name="analytics_service", action_id=uuid4())
        ]
        
        dependencies = workflow_builder._determine_step_dependencies(actions)
        
        # Analytics should depend on both journal and mood
        analytics_deps = next(
            (deps for service, deps in dependencies.items() if service == "analytics_service"),
            []
        )
        assert len(analytics_deps) == 2
    
    def test_determine_step_dependencies_community_sharing(self, workflow_builder):
        """Test determining dependencies for community sharing"""
        actions = [
            MagicMock(service_name="journal_service", action_id=uuid4()),
            MagicMock(service_name="community_service", action_id=uuid4())
        ]
        
        dependencies = workflow_builder._determine_step_dependencies(actions)
        
        # Community sharing should depend on journal creation
        community_deps = next(
            (deps for service, deps in dependencies.items() if service == "community_service"),
            []
        )
        assert len(community_deps) == 1
    
    def test_optimize_workflow_parallel_execution(self, workflow_builder):
        """Test workflow optimization for parallel execution"""
        # Create mock workflow with independent actions
        workflow = MagicMock()
        workflow.steps = [
            MagicMock(actions=[MagicMock(service_name="journal_service")]),
            MagicMock(actions=[MagicMock(service_name="mood_service")])
        ]
        
        optimized = workflow_builder._optimize_workflow(workflow)
        
        # Independent actions should be optimized for parallel execution
        assert optimized is not None
    
    def test_validate_workflow_structure_valid(self, workflow_builder):
        """Test validating valid workflow structure"""
        workflow = MagicMock()
        workflow.steps = [
            MagicMock(actions=[MagicMock(service_name="journal_service")]),
            MagicMock(actions=[MagicMock(service_name="mood_service")])
        ]
        
        is_valid = workflow_builder._validate_workflow_structure(workflow)
        assert is_valid is True
    
    def test_validate_workflow_structure_circular_dependency(self, workflow_builder):
        """Test detecting circular dependencies in workflow"""
        # Create workflow with circular dependency
        step1_id = uuid4()
        step2_id = uuid4()
        
        workflow = MagicMock()
        workflow.steps = [
            MagicMock(step_id=step1_id, dependencies=[step2_id]),
            MagicMock(step_id=step2_id, dependencies=[step1_id])
        ]
        
        is_valid = workflow_builder._validate_workflow_structure(workflow)
        assert is_valid is False
    
    def test_estimate_execution_time(self, workflow_builder):
        """Test estimating workflow execution time"""
        workflow = MagicMock()
        workflow.steps = [
            MagicMock(actions=[
                MagicMock(timeout_seconds=30),
                MagicMock(timeout_seconds=20)
            ]),
            MagicMock(actions=[
                MagicMock(timeout_seconds=15)
            ])
        ]
        
        estimated_time = workflow_builder._estimate_execution_time(workflow)
        
        # Should account for sequential vs parallel execution
        assert estimated_time > 0
        assert estimated_time <= 65  # Maximum if all sequential
