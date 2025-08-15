"""
Comprehensive tests for Orchestrator Factory Services - targeting 80% coverage
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services import create_orchestrator, shutdown_orchestrator, get_orchestrator_instance
from src.core import ActionOrchestrator


@pytest.mark.asyncio
class TestOrchestratorFactory:
    """Comprehensive test suite for Orchestrator Factory"""

    @pytest.fixture(autouse=True)
    async def cleanup_global_instance(self):
        """Clean up global instance before each test"""
        # Clear global instance before test
        import src.services
        src.services._orchestrator_instance = None
        yield
        # Clean up after test
        src.services._orchestrator_instance = None

    async def test_create_orchestrator_first_time(self):
        """Test creating orchestrator for the first time"""
        with patch('src.services.IntentClassifier') as mock_intent, \
             patch('src.services.CulturalProcessor') as mock_cultural, \
             patch('src.services.WorkflowBuilder') as mock_workflow, \
             patch('src.services.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.RollbackManager') as mock_rollback, \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            # Configure mocks
            mock_intent_instance = MagicMock()
            mock_cultural_instance = MagicMock()
            mock_workflow_instance = MagicMock()
            mock_dispatcher_instance = MagicMock()
            mock_rollback_instance = MagicMock()
            mock_orchestrator_instance = MagicMock()
            
            mock_intent.return_value = mock_intent_instance
            mock_cultural.return_value = mock_cultural_instance
            mock_workflow.return_value = mock_workflow_instance
            mock_dispatcher.return_value = mock_dispatcher_instance
            mock_rollback.return_value = mock_rollback_instance
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Call create_orchestrator
            result = await create_orchestrator()
            
            # Verify all components were created
            mock_intent.assert_called_once()
            mock_cultural.assert_called_once()
            mock_workflow.assert_called_once()
            mock_dispatcher.assert_called_once()
            mock_rollback.assert_called_once_with(mock_dispatcher_instance)
            
            # Verify orchestrator was created with correct components
            mock_orchestrator.assert_called_once_with(
                intent_classifier=mock_intent_instance,
                cultural_processor=mock_cultural_instance,
                workflow_builder=mock_workflow_instance,
                action_dispatcher=mock_dispatcher_instance,
                rollback_manager=mock_rollback_instance
            )
            
            # Verify result
            assert result == mock_orchestrator_instance

    async def test_create_orchestrator_returns_existing_instance(self):
        """Test that create_orchestrator returns existing instance if already created"""
        with patch('src.services.IntentClassifier') as mock_intent, \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            mock_orchestrator_instance = MagicMock()
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Create first instance
            first_result = await create_orchestrator()
            
            # Create second instance - should return the same
            second_result = await create_orchestrator()
            
            # Should be the same instance
            assert first_result == second_result
            assert first_result == mock_orchestrator_instance
            
            # Components should only be created once
            mock_intent.assert_called_once()
            mock_orchestrator.assert_called_once()

    async def test_create_orchestrator_component_creation_failure(self):
        """Test create_orchestrator when component creation fails"""
        with patch('src.services.IntentClassifier') as mock_intent:
            mock_intent.side_effect = Exception("Intent classifier creation failed")
            
            with pytest.raises(Exception) as exc_info:
                await create_orchestrator()
            
            assert "Intent classifier creation failed" in str(exc_info.value)

    async def test_create_orchestrator_orchestrator_creation_failure(self):
        """Test create_orchestrator when orchestrator creation fails"""
        with patch('src.services.IntentClassifier'), \
             patch('src.services.CulturalProcessor'), \
             patch('src.services.WorkflowBuilder'), \
             patch('src.services.ActionDispatcher'), \
             patch('src.services.RollbackManager'), \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            mock_orchestrator.side_effect = Exception("Orchestrator creation failed")
            
            with pytest.raises(Exception) as exc_info:
                await create_orchestrator()
            
            assert "Orchestrator creation failed" in str(exc_info.value)

    async def test_shutdown_orchestrator_with_instance(self):
        """Test shutting down orchestrator when instance exists"""
        # First create an orchestrator
        with patch('src.services.IntentClassifier'), \
             patch('src.services.CulturalProcessor'), \
             patch('src.services.WorkflowBuilder'), \
             patch('src.services.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.RollbackManager'), \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            mock_dispatcher_instance = MagicMock()
            mock_dispatcher_instance.close = AsyncMock()
            mock_dispatcher.return_value = mock_dispatcher_instance
            
            mock_orchestrator_instance = MagicMock()
            mock_orchestrator_instance.action_dispatcher = mock_dispatcher_instance
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Create orchestrator
            orchestrator = await create_orchestrator()
            assert orchestrator is not None
            
            # Now shutdown
            await shutdown_orchestrator()
            
            # Verify close was called
            mock_dispatcher_instance.close.assert_called_once()
            
            # Verify global instance is cleared
            assert get_orchestrator_instance() is None

    async def test_shutdown_orchestrator_without_instance(self):
        """Test shutting down orchestrator when no instance exists"""
        # Should not raise an exception
        await shutdown_orchestrator()
        
        # Global instance should remain None
        assert get_orchestrator_instance() is None

    async def test_shutdown_orchestrator_close_failure(self):
        """Test shutdown when action dispatcher close fails"""
        # Create an orchestrator first
        with patch('src.services.IntentClassifier'), \
             patch('src.services.CulturalProcessor'), \
             patch('src.services.WorkflowBuilder'), \
             patch('src.services.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.RollbackManager'), \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            mock_dispatcher_instance = MagicMock()
            mock_dispatcher_instance.close = AsyncMock()
            mock_dispatcher_instance.close.side_effect = Exception("Close failed")
            mock_dispatcher.return_value = mock_dispatcher_instance
            
            mock_orchestrator_instance = MagicMock()
            mock_orchestrator_instance.action_dispatcher = mock_dispatcher_instance
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Create orchestrator
            await create_orchestrator()
            
            # Shutdown should not raise exception even if close fails
            await shutdown_orchestrator()
            
            # Verify close was attempted
            mock_dispatcher_instance.close.assert_called_once()
            
            # Global instance should still be cleared in __init__.py but not factory.py
            # since we're testing the __init__.py shutdown function
            assert get_orchestrator_instance() is None

    async def test_get_orchestrator_instance_when_exists(self):
        """Test getting orchestrator instance when it exists"""
        with patch('src.services.IntentClassifier'), \
             patch('src.services.CulturalProcessor'), \
             patch('src.services.WorkflowBuilder'), \
             patch('src.services.ActionDispatcher'), \
             patch('src.services.RollbackManager'), \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            mock_orchestrator_instance = MagicMock()
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Create orchestrator
            created_instance = await create_orchestrator()
            
            # Get instance
            retrieved_instance = get_orchestrator_instance()
            
            # Should be the same
            assert retrieved_instance == created_instance
            assert retrieved_instance == mock_orchestrator_instance

    async def test_get_orchestrator_instance_when_none(self):
        """Test getting orchestrator instance when none exists"""
        # Should return None
        instance = get_orchestrator_instance()
        assert instance is None

    async def test_component_integration(self):
        """Test that components are properly integrated"""
        with patch('src.services.IntentClassifier') as mock_intent, \
             patch('src.services.CulturalProcessor') as mock_cultural, \
             patch('src.services.WorkflowBuilder') as mock_workflow, \
             patch('src.services.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.RollbackManager') as mock_rollback, \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            # Create mock instances
            mock_intent_instance = MagicMock()
            mock_cultural_instance = MagicMock()
            mock_workflow_instance = MagicMock()
            mock_dispatcher_instance = MagicMock()
            mock_rollback_instance = MagicMock()
            mock_orchestrator_instance = MagicMock()
            
            # Configure return values
            mock_intent.return_value = mock_intent_instance
            mock_cultural.return_value = mock_cultural_instance
            mock_workflow.return_value = mock_workflow_instance
            mock_dispatcher.return_value = mock_dispatcher_instance
            mock_rollback.return_value = mock_rollback_instance
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Create orchestrator
            orchestrator = await create_orchestrator()
            
            # Verify rollback manager was created with action dispatcher
            mock_rollback.assert_called_once_with(mock_dispatcher_instance)
            
            # Verify orchestrator was created with all components
            call_args = mock_orchestrator.call_args
            assert call_args.kwargs['intent_classifier'] == mock_intent_instance
            assert call_args.kwargs['cultural_processor'] == mock_cultural_instance
            assert call_args.kwargs['workflow_builder'] == mock_workflow_instance
            assert call_args.kwargs['action_dispatcher'] == mock_dispatcher_instance
            assert call_args.kwargs['rollback_manager'] == mock_rollback_instance

    async def test_multiple_create_shutdown_cycles(self):
        """Test multiple create and shutdown cycles"""
        with patch('src.services.IntentClassifier'), \
             patch('src.services.CulturalProcessor'), \
             patch('src.services.WorkflowBuilder'), \
             patch('src.services.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.RollbackManager'), \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            mock_dispatcher_instance = MagicMock()
            mock_dispatcher_instance.close = AsyncMock()
            mock_dispatcher.return_value = mock_dispatcher_instance
            
            mock_orchestrator_instance = MagicMock()
            mock_orchestrator_instance.action_dispatcher = mock_dispatcher_instance
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # First cycle
            orchestrator1 = await create_orchestrator()
            assert orchestrator1 is not None
            assert get_orchestrator_instance() == orchestrator1
            
            await shutdown_orchestrator()
            assert get_orchestrator_instance() is None
            
            # Second cycle
            # Reset mock to return new instance
            mock_orchestrator_instance2 = MagicMock()
            mock_orchestrator_instance2.action_dispatcher = mock_dispatcher_instance
            mock_orchestrator.return_value = mock_orchestrator_instance2
            
            orchestrator2 = await create_orchestrator()
            assert orchestrator2 is not None
            assert get_orchestrator_instance() == orchestrator2
            
            await shutdown_orchestrator()
            assert get_orchestrator_instance() is None
            
            # Should have called close twice
            assert mock_dispatcher_instance.close.call_count == 2

    async def test_global_instance_state_management(self):
        """Test global instance state is properly managed"""
        import src.services
        
        # Initially should be None
        assert src.services._orchestrator_instance is None
        assert get_orchestrator_instance() is None
        
        with patch('src.services.IntentClassifier'), \
             patch('src.services.CulturalProcessor'), \
             patch('src.services.WorkflowBuilder'), \
             patch('src.services.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.RollbackManager'), \
             patch('src.services.ActionOrchestrator') as mock_orchestrator:
            
            mock_dispatcher_instance = MagicMock()
            mock_dispatcher_instance.close = AsyncMock()
            mock_dispatcher.return_value = mock_dispatcher_instance
            
            mock_orchestrator_instance = MagicMock()
            mock_orchestrator_instance.action_dispatcher = mock_dispatcher_instance
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Create orchestrator
            orchestrator = await create_orchestrator()
            
            # Global instance should be set
            assert src.services._orchestrator_instance == orchestrator
            assert get_orchestrator_instance() == orchestrator
            
            # Shutdown
            await shutdown_orchestrator()
            
            # Global instance should be cleared
            assert src.services._orchestrator_instance is None
            assert get_orchestrator_instance() is None
