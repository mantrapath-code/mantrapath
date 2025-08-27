"""
Orchestrator Factory
Creates and configures ActionOrchestrator instances with dependency injection
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from ..core import (
    ActionOrchestrator,
    IntentClassifier,
    CulturalProcessor,
    WorkflowBuilder,
    ActionDispatcher,
    RollbackManager
)

logger = logging.getLogger(__name__)

# Global orchestrator instance
_orchestrator_instance: Optional[ActionOrchestrator] = None
_creation_timestamp: Optional[datetime] = None
_configuration: Optional[Dict[str, Any]] = None


async def create_orchestrator(config: Optional[Dict[str, Any]] = None) -> ActionOrchestrator:
    """
    Create and configure ActionOrchestrator instance with dependency injection
    
    Args:
        config: Optional configuration dictionary for components
        
    Returns:
        Configured ActionOrchestrator instance
    """
    global _orchestrator_instance, _creation_timestamp, _configuration
    
    if _orchestrator_instance is not None:
        logger.info("Returning existing ActionOrchestrator instance")
        return _orchestrator_instance
    
    try:
        logger.info("Creating new ActionOrchestrator components...")
        
        # Store configuration
        _configuration = config or {}
        
        # Create core components with configuration
        intent_classifier = IntentClassifier()
        cultural_processor = CulturalProcessor()
        workflow_builder = WorkflowBuilder()
        action_dispatcher = ActionDispatcher()
        rollback_manager = RollbackManager(action_dispatcher)
        
        # Create orchestrator with all dependencies
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        # Store global instance and metadata
        _orchestrator_instance = orchestrator
        _creation_timestamp = datetime.now(timezone.utc)
        
        logger.info("ActionOrchestrator created successfully")
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to create ActionOrchestrator: {str(e)}", exc_info=True)
        # Reset global state on failure
        _orchestrator_instance = None
        _creation_timestamp = None
        _configuration = None
        raise


async def shutdown_orchestrator() -> None:
    """
    Shutdown orchestrator and cleanup all resources
    """
    global _orchestrator_instance, _creation_timestamp, _configuration
    
    if _orchestrator_instance is not None:
        try:
            logger.info("Shutting down ActionOrchestrator...")
            
            # Close HTTP client in action dispatcher
            if hasattr(_orchestrator_instance, 'action_dispatcher'):
                await _orchestrator_instance.action_dispatcher.close()
            
            # Clear global state
            _orchestrator_instance = None
            _creation_timestamp = None
            _configuration = None
            
            logger.info("ActionOrchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during orchestrator shutdown: {str(e)}", exc_info=True)
            # Force clear global state even on error
            _orchestrator_instance = None
            _creation_timestamp = None
            _configuration = None


def get_orchestrator_instance() -> Optional[ActionOrchestrator]:
    """
    Get current orchestrator instance if available
    
    Returns:
        Current ActionOrchestrator instance or None
    """
    return _orchestrator_instance


def get_orchestrator_info() -> Dict[str, Any]:
    """
    Get information about the current orchestrator instance
    
    Returns:
        Dictionary with orchestrator metadata
    """
    return {
        "instance_exists": _orchestrator_instance is not None,
        "creation_timestamp": _creation_timestamp.isoformat() if _creation_timestamp else None,
        "configuration": _configuration,
        "uptime_seconds": (
            (datetime.now(timezone.utc) - _creation_timestamp).total_seconds()
            if _creation_timestamp else None
        )
    }


def is_orchestrator_healthy() -> bool:
    """
    Check if orchestrator instance is healthy
    
    Returns:
        True if orchestrator exists and is healthy
    """
    if _orchestrator_instance is None:
        return False
    
    try:
        # Basic health check - verify components exist
        return all([
            hasattr(_orchestrator_instance, 'intent_classifier'),
            hasattr(_orchestrator_instance, 'cultural_processor'),
            hasattr(_orchestrator_instance, 'workflow_builder'),
            hasattr(_orchestrator_instance, 'action_dispatcher'),
            hasattr(_orchestrator_instance, 'rollback_manager'),
        ])
    except Exception:
        return False


async def restart_orchestrator(config: Optional[Dict[str, Any]] = None) -> ActionOrchestrator:
    """
    Restart orchestrator by shutting down and creating new instance
    
    Args:
        config: Optional new configuration
        
    Returns:
        New ActionOrchestrator instance
    """
    logger.info("Restarting ActionOrchestrator...")
    
    # Shutdown existing instance
    await shutdown_orchestrator()
    
    # Create new instance
    return await create_orchestrator(config)


__all__ = [
    "create_orchestrator", 
    "shutdown_orchestrator", 
    "get_orchestrator_instance",
    "get_orchestrator_info",
    "is_orchestrator_healthy",
    "restart_orchestrator"
]
