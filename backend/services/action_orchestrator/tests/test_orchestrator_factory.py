"""
Comprehensive tests for Orchestrator Factory
Tests all factory functions with dependency injection and lifecycle management
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from src.services.orchestrator_factory import (
    create_orchestrator,
    shutdown_orchestrator,
    get_orchestrator_instance,
    get_orchestrator_info,
    is_orchestrator_healthy,
    restart_orchestrator
)
from src.core import ActionOrchestrator


class TestOrchestratorFactory:
    """Test suite for orchestrator factory functions"""

    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Setup and teardown for each test"""
        # Clear global state before each test by calling shutdown
        try:
            await shutdown_orchestrator()
        except:
            pass
        
        yield
        
        # Cleanup after each test
        try:
            await shutdown_orchestrator()
        except:
            pass

    @pytest.mark.asyncio
    async def test_create_orchestrator_new_instance(self):
        """Test creating a new orchestrator instance"""
        config = {"test_setting": "test_value"}
        
        with patch('src.services.orchestrator_factory.IntentClassifier') as mock_intent, \
             patch('src.services.orchestrator_factory.CulturalProcessor') as mock_cultural, \
             patch('src.services.orchestrator_factory.WorkflowBuilder') as mock_workflow, \
             patch('src.services.orchestrator_factory.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.orchestrator_factory.RollbackManager') as mock_rollback, \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            # Configure mocks
            mock_intent_instance = MagicMock()
            mock_cultural_instance = MagicMock()
            mock_workflow_instance = MagicMock()
            mock_dispatcher_instance = MagicMock()
            mock_rollback_instance = MagicMock()
            mock_orchestrator_instance = MagicMock(spec=ActionOrchestrator)
            
            mock_intent.return_value = mock_intent_instance
            mock_cultural.return_value = mock_cultural_instance
            mock_workflow.return_value = mock_workflow_instance
            mock_dispatcher.return_value = mock_dispatcher_instance
            mock_rollback.return_value = mock_rollback_instance
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Create orchestrator
            result = await create_orchestrator(config)
            
            # Verify component creation
            mock_intent.assert_called_once()
            mock_cultural.assert_called_once()
            mock_workflow.assert_called_once()
            mock_dispatcher.assert_called_once()
            mock_rollback.assert_called_once_with(mock_dispatcher_instance)
            
            # Verify orchestrator creation with dependencies
            mock_orchestrator.assert_called_once_with(
                intent_classifier=mock_intent_instance,
                cultural_processor=mock_cultural_instance,
                workflow_builder=mock_workflow_instance,
                action_dispatcher=mock_dispatcher_instance,
                rollback_manager=mock_rollback_instance
            )
            
            # Verify result
            assert result == mock_orchestrator_instance
            assert get_orchestrator_instance() == mock_orchestrator_instance
            
            # Verify global state
            info = get_orchestrator_info()
            assert info["instance_exists"] is True
            assert info["configuration"] == config
            assert info["creation_timestamp"] is not None
            assert info["uptime_seconds"] is not None

    @pytest.mark.asyncio
    async def test_create_orchestrator_existing_instance(self):
        """Test returning existing orchestrator instance"""
        # First create an instance
        config1 = {"setting1": "value1"}
        
        with patch('src.services.orchestrator_factory.IntentClassifier'), \
             patch('src.services.orchestrator_factory.CulturalProcessor'), \
             patch('src.services.orchestrator_factory.WorkflowBuilder'), \
             patch('src.services.orchestrator_factory.ActionDispatcher'), \
             patch('src.services.orchestrator_factory.RollbackManager'), \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            mock_orchestrator_instance = MagicMock(spec=ActionOrchestrator)
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            first_result = await create_orchestrator(config1)
            
            # Reset mock call count
            mock_orchestrator.reset_mock()
            
            # Try to create again with different config
            config2 = {"setting2": "value2"}
            second_result = await create_orchestrator(config2)
            
            # Should return same instance without creating new one
            assert first_result == second_result
            assert mock_orchestrator.call_count == 0  # No new calls

    @pytest.mark.asyncio
    async def test_create_orchestrator_with_exception(self):
        """Test orchestrator creation failure handling"""
        config = {"test_setting": "test_value"}
        
        with patch('src.services.orchestrator_factory.IntentClassifier') as mock_intent:
            # Make IntentClassifier raise an exception
            mock_intent.side_effect = Exception("Component creation failed")
            
            # Should raise exception and clean up global state
            with pytest.raises(Exception, match="Component creation failed"):
                await create_orchestrator(config)
            
            # Verify global state is cleaned up
            assert get_orchestrator_instance() is None
            info = get_orchestrator_info()
            assert info["instance_exists"] is False
            assert info["configuration"] is None
            assert info["creation_timestamp"] is None

    @pytest.mark.asyncio
    async def test_shutdown_orchestrator_with_instance(self):
        """Test shutting down existing orchestrator"""
        # First create an instance
        with patch('src.services.orchestrator_factory.IntentClassifier'), \
             patch('src.services.orchestrator_factory.CulturalProcessor'), \
             patch('src.services.orchestrator_factory.WorkflowBuilder'), \
             patch('src.services.orchestrator_factory.ActionDispatcher'), \
             patch('src.services.orchestrator_factory.RollbackManager'), \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            mock_orchestrator_instance = MagicMock(spec=ActionOrchestrator)
            mock_dispatcher = AsyncMock()
            mock_orchestrator_instance.action_dispatcher = mock_dispatcher
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            await create_orchestrator()
            
            # Verify instance exists
            assert get_orchestrator_instance() is not None
            
            # Shutdown
            await shutdown_orchestrator()
            
            # Verify dispatcher close was called
            mock_dispatcher.close.assert_called_once()
            
            # Verify global state is cleared
            assert get_orchestrator_instance() is None
            info = get_orchestrator_info()
            assert info["instance_exists"] is False
            assert info["configuration"] is None
            assert info["creation_timestamp"] is None

    @pytest.mark.asyncio
    async def test_shutdown_orchestrator_no_instance(self):
        """Test shutting down when no orchestrator exists"""
        # Ensure no instance exists
        assert get_orchestrator_instance() is None
        
        # Should not raise exception
        await shutdown_orchestrator()
        
        # State should remain clear
        assert get_orchestrator_instance() is None

    @pytest.mark.asyncio
    async def test_shutdown_orchestrator_with_exception(self):
        """Test shutdown with exception during cleanup"""
        # Create instance with mock that raises exception on close
        with patch('src.services.orchestrator_factory.IntentClassifier'), \
             patch('src.services.orchestrator_factory.CulturalProcessor'), \
             patch('src.services.orchestrator_factory.WorkflowBuilder'), \
             patch('src.services.orchestrator_factory.ActionDispatcher'), \
             patch('src.services.orchestrator_factory.RollbackManager'), \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            mock_orchestrator_instance = MagicMock(spec=ActionOrchestrator)
            mock_dispatcher = AsyncMock()
            mock_dispatcher.close.side_effect = Exception("Close failed")
            mock_orchestrator_instance.action_dispatcher = mock_dispatcher
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            await create_orchestrator()
            
            # Shutdown should not raise exception even if close fails
            await shutdown_orchestrator()
            
            # Global state should still be cleared
            assert get_orchestrator_instance() is None

    def test_get_orchestrator_instance_exists(self):
        """Test getting orchestrator instance when it exists"""
        async def test_async():
            with patch('src.services.orchestrator_factory.IntentClassifier'), \
                 patch('src.services.orchestrator_factory.CulturalProcessor'), \
                 patch('src.services.orchestrator_factory.WorkflowBuilder'), \
                 patch('src.services.orchestrator_factory.ActionDispatcher'), \
                 patch('src.services.orchestrator_factory.RollbackManager'), \
                 patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
                
                mock_instance = MagicMock(spec=ActionOrchestrator)
                mock_orchestrator.return_value = mock_instance
                
                # Create orchestrator first
                await create_orchestrator()
                
                # Then test getting it
                result = get_orchestrator_instance()
                assert result == mock_instance
        
        asyncio.run(test_async())

    def test_get_orchestrator_instance_none(self):
        """Test getting orchestrator instance when none exists"""
        result = get_orchestrator_instance()
        assert result is None

    def test_get_orchestrator_info_with_instance(self):
        """Test getting orchestrator info when instance exists"""
        async def test_async():
            mock_config = {"test": "config"}
            
            with patch('src.services.orchestrator_factory.IntentClassifier'), \
                 patch('src.services.orchestrator_factory.CulturalProcessor'), \
                 patch('src.services.orchestrator_factory.WorkflowBuilder'), \
                 patch('src.services.orchestrator_factory.ActionDispatcher'), \
                 patch('src.services.orchestrator_factory.RollbackManager'), \
                 patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
                
                mock_instance = MagicMock(spec=ActionOrchestrator)
                mock_orchestrator.return_value = mock_instance
                
                # Create orchestrator with config
                await create_orchestrator(mock_config)
                
                # Test info
                info = get_orchestrator_info()
                
                assert info["instance_exists"] is True
                assert info["configuration"] == mock_config
                assert info["creation_timestamp"] is not None
                assert isinstance(info["uptime_seconds"], float)
                assert info["uptime_seconds"] >= 0
        
        asyncio.run(test_async())

    def test_get_orchestrator_info_no_instance(self):
        """Test getting orchestrator info when no instance exists"""
        info = get_orchestrator_info()
        
        assert info["instance_exists"] is False
        assert info["creation_timestamp"] is None
        assert info["configuration"] is None
        assert info["uptime_seconds"] is None

    def test_is_orchestrator_healthy_with_healthy_instance(self):
        """Test health check with healthy orchestrator"""
        async def test_async():
            with patch('src.services.orchestrator_factory.IntentClassifier'), \
                 patch('src.services.orchestrator_factory.CulturalProcessor'), \
                 patch('src.services.orchestrator_factory.WorkflowBuilder'), \
                 patch('src.services.orchestrator_factory.ActionDispatcher'), \
                 patch('src.services.orchestrator_factory.RollbackManager'), \
                 patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
                
                # Create mock orchestrator with all required attributes
                mock_instance = MagicMock(spec=ActionOrchestrator)
                mock_instance.intent_classifier = MagicMock()
                mock_instance.cultural_processor = MagicMock()
                mock_instance.workflow_builder = MagicMock()
                mock_instance.action_dispatcher = MagicMock()
                mock_instance.rollback_manager = MagicMock()
                mock_orchestrator.return_value = mock_instance
                
                # Create orchestrator
                await create_orchestrator()
                
                # Test health check
                assert is_orchestrator_healthy() is True
        
        asyncio.run(test_async())

    def test_is_orchestrator_healthy_missing_components(self):
        """Test health check with orchestrator missing components"""
        async def test_async():
            with patch('src.services.orchestrator_factory.IntentClassifier'), \
                 patch('src.services.orchestrator_factory.CulturalProcessor'), \
                 patch('src.services.orchestrator_factory.WorkflowBuilder'), \
                 patch('src.services.orchestrator_factory.ActionDispatcher'), \
                 patch('src.services.orchestrator_factory.RollbackManager'), \
                 patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
                
                # Create mock orchestrator missing some attributes
                mock_instance = MagicMock(spec=ActionOrchestrator)
                mock_instance.intent_classifier = MagicMock()
                # Missing other components - will fail hasattr checks
                del mock_instance.cultural_processor
                mock_orchestrator.return_value = mock_instance
                
                # Create orchestrator
                await create_orchestrator()
                
                # Test health check - should fail due to missing components
                assert is_orchestrator_healthy() is False
        
        asyncio.run(test_async())

    def test_is_orchestrator_healthy_no_instance(self):
        """Test health check when no orchestrator exists"""
        assert is_orchestrator_healthy() is False

    def test_is_orchestrator_healthy_with_exception(self):
        """Test health check with exception during check"""
        async def test_async():
            with patch('src.services.orchestrator_factory.IntentClassifier'), \
                 patch('src.services.orchestrator_factory.CulturalProcessor'), \
                 patch('src.services.orchestrator_factory.WorkflowBuilder'), \
                 patch('src.services.orchestrator_factory.ActionDispatcher'), \
                 patch('src.services.orchestrator_factory.RollbackManager'), \
                 patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
                
                # Create mock that raises exception on hasattr check
                mock_instance = MagicMock(spec=ActionOrchestrator)
                
                # Mock getattr to raise exception for component access
                def mock_getattr(name: str):
                    if name in ['intent_classifier', 'cultural_processor', 'workflow_builder', 'action_dispatcher', 'rollback_manager']:
                        raise Exception("Access failed")
                    return MagicMock()
                
                mock_instance.__getattribute__ = mock_getattr
                mock_orchestrator.return_value = mock_instance
                
                # Create orchestrator
                await create_orchestrator()
                
                # Test health check - should return False on exception
                assert is_orchestrator_healthy() is False
        
        asyncio.run(test_async())

    @pytest.mark.asyncio
    async def test_restart_orchestrator(self):
        """Test restarting orchestrator"""
        original_config = {"original": "config"}
        new_config = {"new": "config"}
        
        # Create initial instance
        with patch('src.services.orchestrator_factory.IntentClassifier'), \
             patch('src.services.orchestrator_factory.CulturalProcessor'), \
             patch('src.services.orchestrator_factory.WorkflowBuilder'), \
             patch('src.services.orchestrator_factory.ActionDispatcher'), \
             patch('src.services.orchestrator_factory.RollbackManager'), \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            mock_instance1 = MagicMock(spec=ActionOrchestrator)
            mock_instance1.action_dispatcher = AsyncMock()
            mock_instance2 = MagicMock(spec=ActionOrchestrator)
            
            # First call returns first instance, second call returns second instance
            mock_orchestrator.side_effect = [mock_instance1, mock_instance2]
            
            # Create initial orchestrator
            first_result = await create_orchestrator(original_config)
            assert first_result == mock_instance1
            
            # Restart with new config
            restart_result = await restart_orchestrator(new_config)
            assert restart_result == mock_instance2
            assert restart_result != first_result
            
            # Verify shutdown was called on first instance
            mock_instance1.action_dispatcher.close.assert_called_once()
            
            # Verify new configuration is set
            info = get_orchestrator_info()
            assert info["configuration"] == new_config

    @pytest.mark.asyncio
    async def test_restart_orchestrator_no_existing_instance(self):
        """Test restarting when no orchestrator exists"""
        config = {"restart": "config"}
        
        with patch('src.services.orchestrator_factory.IntentClassifier'), \
             patch('src.services.orchestrator_factory.CulturalProcessor'), \
             patch('src.services.orchestrator_factory.WorkflowBuilder'), \
             patch('src.services.orchestrator_factory.ActionDispatcher'), \
             patch('src.services.orchestrator_factory.RollbackManager'), \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            mock_instance = MagicMock(spec=ActionOrchestrator)
            mock_orchestrator.return_value = mock_instance
            
            # Restart when no instance exists
            result = await restart_orchestrator(config)
            
            assert result == mock_instance
            assert get_orchestrator_instance() == mock_instance

    def test_create_orchestrator_default_config(self):
        """Test creating orchestrator with default (None) config"""
        async def test_async():
            with patch('src.services.orchestrator_factory.IntentClassifier'), \
                 patch('src.services.orchestrator_factory.CulturalProcessor'), \
                 patch('src.services.orchestrator_factory.WorkflowBuilder'), \
                 patch('src.services.orchestrator_factory.ActionDispatcher'), \
                 patch('src.services.orchestrator_factory.RollbackManager'), \
                 patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
                
                mock_instance = MagicMock(spec=ActionOrchestrator)
                mock_orchestrator.return_value = mock_instance
                
                await create_orchestrator(None)
                
                # Verify empty dict was stored as configuration
                info = get_orchestrator_info()
                assert info["configuration"] == {}
        
        asyncio.run(test_async())

    def test_module_exports(self):
        """Test that all expected functions are exported in __all__"""
        from src.services.orchestrator_factory import __all__
        
        expected_exports = [
            "create_orchestrator",
            "shutdown_orchestrator", 
            "get_orchestrator_instance",
            "get_orchestrator_info",
            "is_orchestrator_healthy",
            "restart_orchestrator"
        ]
        
        for export in expected_exports:
            assert export in __all__, f"Expected export '{export}' not found in __all__"
        
        # Verify no extra exports
        assert len(__all__) == len(expected_exports), "Unexpected extra exports in __all__"


if __name__ == "__main__":
    pytest.main([__file__])
