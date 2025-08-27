"""
Orchestrator Factory
Creates and configures ActionOrchestrator instances
"""
import logging
from typing import Optional

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


async def create_orchestrator() -> ActionOrchestrator:
    """
    Create and configure ActionOrchestrator instance
    
    This factory function creates all required components and wires them together
    """
    global _orchestrator_instance
    
    if _orchestrator_instance is not None:
        return _orchestrator_instance
    
    try:
        logger.info("Creating Action Orchestrator components...")
        
        # Create core components
        intent_classifier = IntentClassifier()
        cultural_processor = CulturalProcessor()
        workflow_builder = WorkflowBuilder()
        action_dispatcher = ActionDispatcher()
        rollback_manager = RollbackManager(action_dispatcher)
        
        # Create orchestrator
        orchestrator = ActionOrchestrator(
            intent_classifier=intent_classifier,
            cultural_processor=cultural_processor,
            workflow_builder=workflow_builder,
            action_dispatcher=action_dispatcher,
            rollback_manager=rollback_manager
        )
        
        _orchestrator_instance = orchestrator
        
        logger.info("Action Orchestrator created successfully")
        return orchestrator
        
    except Exception as e:
        logger.error(f"Failed to create Action Orchestrator: {str(e)}", exc_info=True)
        raise


async def shutdown_orchestrator() -> None:
    """Shutdown orchestrator and cleanup resources"""
    global _orchestrator_instance
    
    if _orchestrator_instance is not None:
        try:
            # Close HTTP client in action dispatcher
            await _orchestrator_instance.action_dispatcher.close()
            
            _orchestrator_instance = None
            logger.info("Action Orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during orchestrator shutdown: {str(e)}", exc_info=True)


def get_orchestrator_instance() -> Optional[ActionOrchestrator]:
    """Get current orchestrator instance if available"""
    return _orchestrator_instance
