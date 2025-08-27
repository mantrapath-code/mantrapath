"""
Tests specifically for orchestrator_factory.py module - targeting 80% coverage
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from src.services.orchestrator_factory import (
    create_orchestrator, shutdown_orchestrator, get_orchestrator_instance,
    get_orchestrator_info, is_orchestrator_healthy, restart_orchestrator
)


@pytest.mark.asyncio
class TestOrchestratorFactoryModule:
    """Test suite specifically for orchestrator_factory.py"""

    @pytest.fixture(autouse=True)
    async def cleanup_factory_state(self):
        """Clean up factory state before each test"""
        # Import the module to reset its global state
        import src.services.orchestrator_factory as factory
        factory._orchestrator_instance = None
        factory._creation_timestamp = None
        factory._configuration = None
        yield
        # Clean up after test
        factory._orchestrator_instance = None
        factory._creation_timestamp = None
        factory._configuration = None

    async def test_create_orchestrator_first_time_with_config(self):
        """Test creating orchestrator for the first time with config"""
        test_config = {"debug": True, "timeout": 30}
        
        with patch('src.services.orchestrator_factory.IntentClassifier') as mock_intent, \
             patch('src.services.orchestrator_factory.CulturalProcessor') as mock_cultural, \
             patch('src.services.orchestrator_factory.WorkflowBuilder') as mock_workflow, \
             patch('src.services.orchestrator_factory.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.orchestrator_factory.RollbackManager') as mock_rollback, \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            # Configure mocks
            mock_orchestrator_instance = MagicMock()
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            # Call create_orchestrator with config
            result = await create_orchestrator(test_config)
            
            # Verify result
            assert result == mock_orchestrator_instance
            
            # Verify configuration was stored
            import src.services.orchestrator_factory as factory
            assert factory._configuration == test_config
            assert factory._creation_timestamp is not None

    async def test_create_orchestrator_returns_existing(self):
        """Test that create_orchestrator returns existing instance"""
        # Create first instance
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            mock_instance = MagicMock()
            mock_orchestrator.return_value = mock_instance
            
            first_result = await create_orchestrator()
            second_result = await create_orchestrator()
            
            # Should be the same instance
            assert first_result == second_result
            # Orchestrator should only be created once
            mock_orchestrator.assert_called_once()

    async def test_create_orchestrator_component_failure(self):
        """Test create_orchestrator when component creation fails"""
        with patch('src.services.orchestrator_factory.IntentClassifier') as mock_intent:
            mock_intent.side_effect = Exception("Component creation failed")
            
            with pytest.raises(Exception) as exc_info:
                await create_orchestrator()
            
            assert "Component creation failed" in str(exc_info.value)
            
            # Verify global state was reset
            import src.services.orchestrator_factory as factory
            assert factory._orchestrator_instance is None
            assert factory._creation_timestamp is None
            assert factory._configuration is None

    async def test_shutdown_orchestrator_with_instance(self):
        """Test shutting down orchestrator when instance exists"""
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            # Create mock instance with action dispatcher
            mock_dispatcher = MagicMock()
            mock_dispatcher.close = AsyncMock()
            
            mock_instance = MagicMock()
            mock_instance.action_dispatcher = mock_dispatcher
            mock_orchestrator.return_value = mock_instance
            
            # Create orchestrator
            await create_orchestrator()
            
            # Now shutdown
            await shutdown_orchestrator()
            
            # Verify close was called
            mock_dispatcher.close.assert_called_once()
            
            # Verify global state was cleared
            import src.services.orchestrator_factory as factory
            assert factory._orchestrator_instance is None
            assert factory._creation_timestamp is None
            assert factory._configuration is None

    async def test_shutdown_orchestrator_close_failure(self):
        """Test shutdown when close fails"""
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            # Create mock instance with failing action dispatcher
            mock_dispatcher = MagicMock()
            mock_dispatcher.close = AsyncMock(side_effect=Exception("Close failed"))
            
            mock_instance = MagicMock()
            mock_instance.action_dispatcher = mock_dispatcher
            mock_orchestrator.return_value = mock_instance
            
            # Create orchestrator
            await create_orchestrator()
            
            # Shutdown should not raise exception
            await shutdown_orchestrator()
            
            # Verify global state was still cleared
            import src.services.orchestrator_factory as factory
            assert factory._orchestrator_instance is None

    async def test_shutdown_orchestrator_without_instance(self):
        """Test shutting down when no instance exists"""
        # Should not raise exception
        await shutdown_orchestrator()
        
        # State should remain clean
        import src.services.orchestrator_factory as factory
        assert factory._orchestrator_instance is None

    async def test_get_orchestrator_instance_when_exists(self):
        """Test getting instance when it exists"""
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            mock_instance = MagicMock()
            mock_orchestrator.return_value = mock_instance
            
            # Create orchestrator
            created_instance = await create_orchestrator()
            
            # Get instance
            retrieved_instance = get_orchestrator_instance()
            
            # Should be the same
            assert retrieved_instance == created_instance

    async def test_get_orchestrator_instance_when_none(self):
        """Test getting instance when none exists"""
        instance = get_orchestrator_instance()
        assert instance is None

    async def test_get_orchestrator_info_with_instance(self):
        """Test getting orchestrator info when instance exists"""
        test_config = {"test": "value"}
        
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            mock_instance = MagicMock()
            mock_orchestrator.return_value = mock_instance
            
            # Create orchestrator with config
            await create_orchestrator(test_config)
            
            # Get info
            info = get_orchestrator_info()
            
            assert info["instance_exists"] is True
            assert info["configuration"] == test_config
            assert info["creation_timestamp"] is not None
            assert info["uptime_seconds"] is not None
            assert info["uptime_seconds"] >= 0

    async def test_get_orchestrator_info_without_instance(self):
        """Test getting orchestrator info when no instance exists"""
        info = get_orchestrator_info()
        
        assert info["instance_exists"] is False
        assert info["configuration"] is None
        assert info["creation_timestamp"] is None
        assert info["uptime_seconds"] is None

    async def test_is_orchestrator_healthy_when_healthy(self):
        """Test health check when orchestrator is healthy"""
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            # Create mock instance with all required components
            mock_instance = MagicMock()
            mock_instance.intent_classifier = MagicMock()
            mock_instance.cultural_processor = MagicMock()
            mock_instance.workflow_builder = MagicMock()
            mock_instance.action_dispatcher = MagicMock()
            mock_instance.rollback_manager = MagicMock()
            
            mock_orchestrator.return_value = mock_instance
            
            # Create orchestrator
            await create_orchestrator()
            
            # Check health
            is_healthy = is_orchestrator_healthy()
            assert is_healthy is True

    async def test_is_orchestrator_healthy_when_missing_components(self):
        """Test health check when components are missing"""
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            # Create mock instance missing some components
            mock_instance = MagicMock()
            del mock_instance.intent_classifier  # Remove component
            
            mock_orchestrator.return_value = mock_instance
            
            # Create orchestrator
            await create_orchestrator()
            
            # Check health
            is_healthy = is_orchestrator_healthy()
            assert is_healthy is False

    async def test_is_orchestrator_healthy_when_none(self):
        """Test health check when no instance exists"""
        is_healthy = is_orchestrator_healthy()
        assert is_healthy is False

    async def test_is_orchestrator_healthy_with_exception(self):
        """Test health check when exception occurs"""
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            # Create mock instance that raises exception on attribute access
            mock_instance = MagicMock()
            mock_instance.__getattribute__ = MagicMock(side_effect=Exception("Access error"))
            
            mock_orchestrator.return_value = mock_instance
            
            # Create orchestrator
            await create_orchestrator()
            
            # Check health - should handle exception
            is_healthy = is_orchestrator_healthy()
            assert is_healthy is False

    async def test_restart_orchestrator(self):
        """Test restarting orchestrator"""
        initial_config = {"initial": True}
        new_config = {"restarted": True}
        
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            mock_instance1 = MagicMock()
            mock_instance1.action_dispatcher = MagicMock()
            mock_instance1.action_dispatcher.close = AsyncMock()
            
            mock_instance2 = MagicMock()
            
            # Return different instances for each call
            mock_orchestrator.side_effect = [mock_instance1, mock_instance2]
            
            # Create initial orchestrator
            initial_instance = await create_orchestrator(initial_config)
            assert initial_instance == mock_instance1
            
            # Restart with new config
            restarted_instance = await restart_orchestrator(new_config)
            assert restarted_instance == mock_instance2
            
            # Verify old instance was shut down
            mock_instance1.action_dispatcher.close.assert_called_once()
            
            # Verify new configuration
            import src.services.orchestrator_factory as factory
            assert factory._configuration == new_config

    async def test_restart_orchestrator_without_config(self):
        """Test restarting orchestrator without new config"""
        with patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            mock_instance1 = MagicMock()
            mock_instance1.action_dispatcher = MagicMock()
            mock_instance1.action_dispatcher.close = AsyncMock()
            
            mock_instance2 = MagicMock()
            mock_orchestrator.side_effect = [mock_instance1, mock_instance2]
            
            # Create initial orchestrator
            await create_orchestrator({"initial": True})
            
            # Restart without config
            restarted_instance = await restart_orchestrator()
            
            # Should get new instance
            assert restarted_instance == mock_instance2
            
            # Configuration should be empty dict
            import src.services.orchestrator_factory as factory
            assert factory._configuration == {}

    async def test_component_integration_with_dependencies(self):
        """Test that components are properly integrated with dependencies"""
        with patch('src.services.orchestrator_factory.IntentClassifier') as mock_intent, \
             patch('src.services.orchestrator_factory.CulturalProcessor') as mock_cultural, \
             patch('src.services.orchestrator_factory.WorkflowBuilder') as mock_workflow, \
             patch('src.services.orchestrator_factory.ActionDispatcher') as mock_dispatcher, \
             patch('src.services.orchestrator_factory.RollbackManager') as mock_rollback, \
             patch('src.services.orchestrator_factory.ActionOrchestrator') as mock_orchestrator:
            
            mock_dispatcher_instance = MagicMock()
            mock_dispatcher.return_value = mock_dispatcher_instance
            
            # Create orchestrator
            await create_orchestrator()
            
            # Verify rollback manager was created with dispatcher dependency
            mock_rollback.assert_called_once_with(mock_dispatcher_instance)
            
            # Verify orchestrator was created with all components
            mock_orchestrator.assert_called_once()
            call_kwargs = mock_orchestrator.call_args.kwargs
            assert 'intent_classifier' in call_kwargs
            assert 'cultural_processor' in call_kwargs
            assert 'workflow_builder' in call_kwargs
            assert 'action_dispatcher' in call_kwargs
            assert 'rollback_manager' in call_kwargs

    async def test_factory_module_exports(self):
        """Test that all expected functions are exported"""
        import src.services.orchestrator_factory as factory
        
        expected_exports = [
            "create_orchestrator",
            "shutdown_orchestrator", 
            "get_orchestrator_instance",
            "get_orchestrator_info",
            "is_orchestrator_healthy",
            "restart_orchestrator"
        ]
        
        for export in expected_exports:
            assert hasattr(factory, export)
            assert export in factory.__all__
