"""
Comprehensive Action Orchestrator Functionality Tests
Tests complete workflow orchestration, service coordination, and error handling
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from src.core.orchestrator import ActionOrchestrator
from src.core.intent_classifier import IntentClassifier
from src.core.cultural_processor import CulturalProcessor
from src.core.workflow_builder import WorkflowBuilder
from src.core.action_dispatcher import ActionDispatcher
from src.core.rollback_manager import RollbackManager
from src.models import (
    VoiceIntent, IntentType, ConfidenceLevel, CulturalContext,
    ActionWorkflow, WorkflowStep, ServiceAction, WorkflowResult, WorkflowStatus
)


@pytest.mark.asyncio
class TestActionOrchestratorFunctionality:
    """Test comprehensive action orchestrator functionality"""
    
    async def test_complete_journal_workflow_english(self):
        """Test complete journal creation workflow in English"""
        # Mock dependencies
        intent_classifier = MagicMock()
        cultural_processor = MagicMock()
        workflow_builder = MagicMock()
        action_dispatcher = MagicMock()
        rollback_manager = MagicMock()
        
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Mock responses
        voice_intent = VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence_level=ConfidenceLevel.HIGH,
            entities={"activities": ["journal"], "content": ["thoughts", "daily reflection"]},
            original_text="I want to create a journal entry about my day"
        )
        intent_classifier.classify_intent.return_value = voice_intent
        
        cultural_context = CulturalContext(
            language="en",
            cultural_region="north_america",
            communication_style="direct",
            formality_level="medium",
            cultural_sensitivities=["privacy"],
            time_zone="UTC",
            date_format="MM/DD/YYYY"
        )
        cultural_processor.process_cultural_context.return_value = cultural_context
        
        # Mock workflow creation
        workflow_steps = [
            WorkflowStep(
                step_id="step_1",
                service_action=ServiceAction(
                    service_name="journal_service",
                    action_type="create_entry",
                    parameters={"content": "Daily reflection", "mood": "reflective"},
                    timeout_seconds=30
                ),
                dependencies=[],
                rollback_action=ServiceAction(
                    service_name="journal_service",
                    action_type="delete_entry",
                    parameters={"entry_id": "placeholder"},
                    timeout_seconds=15
                )
            )
        ]
        
        workflow = ActionWorkflow(
            workflow_id="test_workflow_123",
            intent=voice_intent,
            cultural_context=cultural_context,
            steps=workflow_steps,
            created_at=datetime.utcnow()
        )
        workflow_builder.build_workflow.return_value = workflow
        
        # Mock successful action execution
        action_dispatcher.execute_action.return_value = {
            "success": True,
            "entry_id": "journal_123",
            "message": "Journal entry created successfully"
        }
        
        # Execute orchestration
        result = await orchestrator.orchestrate_voice_workflow(
            voice_input="I want to create a journal entry about my day",
            user_id="user_123",
            cultural_preferences={"language": "en"}
        )
        
        # Verify results
        assert result.status == WorkflowStatus.COMPLETED
        assert result.successful_actions == 1
        assert result.failed_actions == 0
        assert len(result.action_results) == 1
        assert result.action_results[0]["success"] is True
        
        # Verify method calls
        intent_classifier.classify_intent.assert_called_once()
        cultural_processor.process_cultural_context.assert_called_once()
        workflow_builder.build_workflow.assert_called_once()
        action_dispatcher.execute_action.assert_called_once()
    
    async def test_complete_mood_tracking_workflow_hindi(self):
        """Test complete mood tracking workflow in Hindi"""
        # Setup similar to English test but with Hindi context
        intent_classifier = MagicMock()
        cultural_processor = MagicMock()
        workflow_builder = MagicMock()
        action_dispatcher = MagicMock()
        rollback_manager = MagicMock()
        
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Hindi mood tracking intent
        voice_intent = VoiceIntent(
            intent_type=IntentType.MOOD_TRACKING,
            confidence_level=ConfidenceLevel.HIGH,
            entities={"emotions": ["खुश"], "activities": ["mood"], "numbers": []},
            original_text="मैं आज बहुत खुश हूं"
        )
        intent_classifier.classify_intent.return_value = voice_intent
        
        # Hindi cultural context
        cultural_context = CulturalContext(
            language="hi",
            cultural_region="india_north",
            communication_style="respectful",
            formality_level="high",
            cultural_sensitivities=["family_values", "religious_respect"],
            time_zone="Asia/Kolkata",
            date_format="DD/MM/YYYY"
        )
        cultural_processor.process_cultural_context.return_value = cultural_context
        
        # Mock workflow for mood tracking
        workflow_steps = [
            WorkflowStep(
                step_id="mood_step_1",
                service_action=ServiceAction(
                    service_name="mood_service",
                    action_type="track_mood",
                    parameters={"mood": "happy", "intensity": "high", "language": "hi"},
                    timeout_seconds=20
                ),
                dependencies=[],
                rollback_action=None
            )
        ]
        
        workflow = ActionWorkflow(
            workflow_id="mood_workflow_456",
            intent=voice_intent,
            cultural_context=cultural_context,
            steps=workflow_steps,
            created_at=datetime.utcnow()
        )
        workflow_builder.build_workflow.return_value = workflow
        
        # Mock successful mood tracking
        action_dispatcher.execute_action.return_value = {
            "success": True,
            "mood_id": "mood_789",
            "message": "मूड सफलतापूर्वक ट्रैक किया गया"
        }
        
        # Execute orchestration
        result = await orchestrator.orchestrate_voice_workflow(
            voice_input="मैं आज बहुत खुश हूं",
            user_id="user_456",
            cultural_preferences={"language": "hi", "cultural_region": "india_north"}
        )
        
        # Verify Hindi-specific results
        assert result.status == WorkflowStatus.COMPLETED
        assert result.cultural_context.language == "hi"
        assert result.cultural_context.cultural_region == "india_north"
        assert result.successful_actions == 1
    
    async def test_complex_multi_service_workflow(self):
        """Test complex workflow involving multiple services"""
        intent_classifier = MagicMock()
        cultural_processor = MagicMock()
        workflow_builder = MagicMock()
        action_dispatcher = MagicMock()
        rollback_manager = MagicMock()
        
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Complex intent involving multiple services
        voice_intent = VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence_level=ConfidenceLevel.HIGH,
            entities={
                "activities": ["journal", "mood", "community"],
                "emotions": ["accomplished", "grateful"],
                "content": ["meditation session", "progress"]
            },
            original_text="I want to journal about my meditation session, track my mood as accomplished, and share my progress with the community"
        )
        intent_classifier.classify_intent.return_value = voice_intent
        
        cultural_context = CulturalContext(
            language="en",
            cultural_region="north_america",
            communication_style="direct",
            formality_level="medium",
            cultural_sensitivities=[],
            time_zone="UTC",
            date_format="MM/DD/YYYY"
        )
        cultural_processor.process_cultural_context.return_value = cultural_context
        
        # Multi-step workflow
        workflow_steps = [
            # Step 1: Create journal entry
            WorkflowStep(
                step_id="journal_step",
                service_action=ServiceAction(
                    service_name="journal_service",
                    action_type="create_entry",
                    parameters={"content": "Meditation session progress", "tags": ["meditation", "progress"]},
                    timeout_seconds=30
                ),
                dependencies=[],
                rollback_action=ServiceAction(
                    service_name="journal_service",
                    action_type="delete_entry",
                    parameters={"entry_id": "{{journal_step.entry_id}}"},
                    timeout_seconds=15
                )
            ),
            # Step 2: Track mood (depends on journal)
            WorkflowStep(
                step_id="mood_step", 
                service_action=ServiceAction(
                    service_name="mood_service",
                    action_type="track_mood",
                    parameters={"mood": "accomplished", "intensity": "high", "related_entry": "{{journal_step.entry_id}}"},
                    timeout_seconds=20
                ),
                dependencies=["journal_step"],
                rollback_action=None
            ),
            # Step 3: Share with community (depends on both)
            WorkflowStep(
                step_id="community_step",
                service_action=ServiceAction(
                    service_name="community_service", 
                    action_type="share_progress",
                    parameters={
                        "content": "Shared my meditation progress",
                        "journal_id": "{{journal_step.entry_id}}",
                        "mood_id": "{{mood_step.mood_id}}"
                    },
                    timeout_seconds=25
                ),
                dependencies=["journal_step", "mood_step"],
                rollback_action=ServiceAction(
                    service_name="community_service",
                    action_type="delete_post", 
                    parameters={"post_id": "{{community_step.post_id}}"},
                    timeout_seconds=15
                )
            )
        ]
        
        workflow = ActionWorkflow(
            workflow_id="complex_workflow_789",
            intent=voice_intent,
            cultural_context=cultural_context,
            steps=workflow_steps,
            created_at=datetime.utcnow()
        )
        workflow_builder.build_workflow.return_value = workflow
        
        # Mock successful execution of all steps
        action_results = [
            {"success": True, "entry_id": "journal_456", "message": "Journal created"},
            {"success": True, "mood_id": "mood_789", "message": "Mood tracked"},
            {"success": True, "post_id": "post_123", "message": "Progress shared"}
        ]
        action_dispatcher.execute_action.side_effect = action_results
        
        # Execute complex orchestration
        result = await orchestrator.orchestrate_voice_workflow(
            voice_input="I want to journal about my meditation session, track my mood as accomplished, and share my progress with the community",
            user_id="user_complex",
            cultural_preferences={}
        )
        
        # Verify complex workflow execution
        assert result.status == WorkflowStatus.COMPLETED
        assert result.successful_actions == 3
        assert result.failed_actions == 0
        assert len(result.action_results) == 3
        
        # Verify all services were called
        assert action_dispatcher.execute_action.call_count == 3
    
    async def test_workflow_failure_and_rollback(self):
        """Test workflow failure handling and rollback mechanism"""
        intent_classifier = MagicMock()
        cultural_processor = MagicMock()
        workflow_builder = MagicMock()
        action_dispatcher = MagicMock()
        rollback_manager = MagicMock()
        
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Setup intent and context
        voice_intent = VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence_level=ConfidenceLevel.MEDIUM,
            entities={"activities": ["journal"]},
            original_text="Create journal entry"
        )
        intent_classifier.classify_intent.return_value = voice_intent
        
        cultural_context = CulturalContext(
            language="en",
            cultural_region="north_america", 
            communication_style="direct",
            formality_level="medium",
            cultural_sensitivities=[],
            time_zone="UTC",
            date_format="MM/DD/YYYY"
        )
        cultural_processor.process_cultural_context.return_value = cultural_context
        
        # Workflow with rollback action
        workflow_steps = [
            WorkflowStep(
                step_id="failing_step",
                service_action=ServiceAction(
                    service_name="journal_service",
                    action_type="create_entry",
                    parameters={"content": "Test entry"},
                    timeout_seconds=30
                ),
                dependencies=[],
                rollback_action=ServiceAction(
                    service_name="journal_service",
                    action_type="cleanup",
                    parameters={},
                    timeout_seconds=15
                )
            )
        ]
        
        workflow = ActionWorkflow(
            workflow_id="failing_workflow",
            intent=voice_intent,
            cultural_context=cultural_context,
            steps=workflow_steps,
            created_at=datetime.utcnow()
        )
        workflow_builder.build_workflow.return_value = workflow
        
        # Mock action failure
        action_dispatcher.execute_action.side_effect = Exception("Service temporarily unavailable")
        
        # Mock rollback success
        rollback_manager.rollback_workflow.return_value = True
        
        # Execute workflow (should fail and rollback)
        result = await orchestrator.orchestrate_voice_workflow(
            voice_input="Create journal entry",
            user_id="user_fail",
            cultural_preferences={}
        )
        
        # Verify failure handling
        assert result.status in [WorkflowStatus.FAILED, WorkflowStatus.ROLLED_BACK]
        assert result.successful_actions == 0
        assert result.failed_actions >= 1
        
        # Verify rollback was called
        rollback_manager.rollback_workflow.assert_called_once()
    
    async def test_low_confidence_intent_handling(self):
        """Test handling of low confidence intents"""
        intent_classifier = MagicMock()
        cultural_processor = MagicMock()
        workflow_builder = MagicMock()
        action_dispatcher = MagicMock()
        rollback_manager = MagicMock()
        
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Low confidence intent
        voice_intent = VoiceIntent(
            intent_type=IntentType.CHATBOT_CONVERSATION,
            confidence_level=ConfidenceLevel.LOW,
            entities={"activities": ["unclear"]},
            original_text="Um, maybe something?"
        )
        intent_classifier.classify_intent.return_value = voice_intent
        
        cultural_context = CulturalContext(
            language="en",
            cultural_region="north_america",
            communication_style="direct", 
            formality_level="medium",
            cultural_sensitivities=[],
            time_zone="UTC",
            date_format="MM/DD/YYYY"
        )
        cultural_processor.process_cultural_context.return_value = cultural_context
        
        # Execute with low confidence
        result = await orchestrator.orchestrate_voice_workflow(
            voice_input="Um, maybe something?",
            user_id="user_unclear",
            cultural_preferences={}
        )
        
        # Should still process but might have different handling
        assert result is not None
        assert result.intent.confidence_level == ConfidenceLevel.LOW
    
    async def test_cultural_adaptation_in_workflow(self):
        """Test cultural adaptation throughout the workflow"""
        intent_classifier = MagicMock()
        cultural_processor = MagicMock()
        workflow_builder = MagicMock()
        action_dispatcher = MagicMock()
        rollback_manager = MagicMock()
        
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Setup Hindi context
        voice_intent = VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence_level=ConfidenceLevel.HIGH,
            entities={"activities": ["journal"]},
            original_text="मैं अपनी डायरी लिखना चाहता हूं"
        )
        intent_classifier.classify_intent.return_value = voice_intent
        
        hindi_context = CulturalContext(
            language="hi",
            cultural_region="india_north",
            communication_style="respectful",
            formality_level="high",
            cultural_sensitivities=["family_values", "religious_respect"],
            time_zone="Asia/Kolkata",
            date_format="DD/MM/YYYY"
        )
        cultural_processor.process_cultural_context.return_value = hindi_context
        
        # Mock culturally adapted parameters
        cultural_processor.adapt_action_parameters.return_value = {
            "content": "डायरी एंट्री",
            "language": "hi",
            "formality_level": "high",
            "cultural_metadata": {
                "communication_style": "respectful",
                "cultural_sensitivities": ["family_values"]
            }
        }
        
        # Mock workflow with cultural adaptations
        workflow_steps = [
            WorkflowStep(
                step_id="cultural_step",
                service_action=ServiceAction(
                    service_name="journal_service",
                    action_type="create_entry",
                    parameters={
                        "content": "डायरी एंट्री",
                        "language": "hi",
                        "formality_level": "high"
                    },
                    timeout_seconds=30
                ),
                dependencies=[],
                rollback_action=None
            )
        ]
        
        workflow = ActionWorkflow(
            workflow_id="cultural_workflow",
            intent=voice_intent,
            cultural_context=hindi_context,
            steps=workflow_steps,
            created_at=datetime.utcnow()
        )
        workflow_builder.build_workflow.return_value = workflow
        
        action_dispatcher.execute_action.return_value = {
            "success": True,
            "entry_id": "hindi_entry_123",
            "message": "डायरी एंट्री सफलतापूर्वक बनाई गई"
        }
        
        # Execute with cultural adaptation
        result = await orchestrator.orchestrate_voice_workflow(
            voice_input="मैं अपनी डायरी लिखना चाहता हूं",
            user_id="user_hindi",
            cultural_preferences={"language": "hi", "cultural_region": "india_north"}
        )
        
        # Verify cultural adaptation was applied
        assert result.cultural_context.language == "hi"
        assert result.cultural_context.cultural_region == "india_north"
        assert result.cultural_context.formality_level == "high"
        
        # Verify cultural processor was used for adaptation
        cultural_processor.adapt_action_parameters.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
