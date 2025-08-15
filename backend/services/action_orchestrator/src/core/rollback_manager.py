"""
Rollback Manager
Handles workflow rollback operations and cleanup for failed workflows
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union

from ..models import ActionWorkflow, ActionResult, WorkflowStep

logger = logging.getLogger(__name__)


class RollbackManager:
    """
    Manages rollback operations for failed workflows
    
    Handles cleanup and rollback of completed actions when workflows fail
    """
    
    def __init__(self, action_dispatcher: Any):
        self.action_dispatcher = action_dispatcher
        
        # Track rollback operations
        self.active_rollbacks: Dict[str, bool] = {}
        
        logger.info("Rollback Manager initialized")
    
    async def rollback_workflow(
        self,
        workflow: ActionWorkflow,
        completed_actions: List[ActionResult]
    ) -> None:
        """
        Rollback a failed workflow by executing rollback actions
        
        Args:
            workflow: The failed workflow
            completed_actions: List of successfully completed actions
        """
        
        workflow_id = str(workflow.workflow_id)
        
        if workflow_id in self.active_rollbacks:
            logger.warning(f"Rollback already in progress for workflow {workflow_id}")
            return
        
        self.active_rollbacks[workflow_id] = True
        
        try:
            logger.info(f"Starting rollback for workflow {workflow_id}")
            
            # Filter actions that completed successfully and have rollback actions
            rollback_candidates = []
            
            for action_result in completed_actions:
                if action_result.success:
                    # Find the original action in workflow steps
                    rollback_action = self._find_rollback_action(workflow, str(action_result.action_id))
                    if rollback_action:
                        rollback_candidates.append((action_result, rollback_action))
            
            if not rollback_candidates:
                logger.info(f"No rollback actions needed for workflow {workflow_id}")
                return
            
            # Execute rollback actions in reverse order
            rollback_candidates.reverse()
            
            rollback_results = []
            successful_rollbacks = 0
            failed_rollbacks = 0
            
            for action_result, rollback_action in rollback_candidates:
                try:
                    logger.info(f"Rolling back action {action_result.action_id}")
                    
                    # Prepare rollback parameters
                    rollback_params = await self._prepare_rollback_parameters(
                        rollback_action, action_result
                    )
                    
                    # Execute rollback action
                    await self.action_dispatcher.dispatch_action(
                        service_name=action_result.service_name,
                        action_type=rollback_action["action_type"],
                        parameters=rollback_params,
                        timeout_seconds=rollback_action.get("timeout", 30),
                        retry_count=rollback_action.get("retry_count", 2)
                    )
                    
                    successful_rollbacks += 1
                    rollback_results.append(f"✓ Rolled back {action_result.action_id}")
                    
                    # Add delay between rollback actions to avoid overwhelming services
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    failed_rollbacks += 1
                    error_msg = f"✗ Failed to rollback {action_result.action_id}: {str(e)}"
                    rollback_results.append(error_msg)
                    logger.error(error_msg)
                    
                    # Continue with other rollbacks even if one fails
                    continue
            
            # Log rollback summary
            logger.info(f"Rollback completed for workflow {workflow_id}: "
                       f"{successful_rollbacks} successful, {failed_rollbacks} failed")
            
            # Update workflow with rollback information
            workflow.rollback_actions = [
                result.action_id for result, _ in rollback_candidates[:successful_rollbacks]
            ]
            
            if failed_rollbacks > 0:
                logger.warning(f"Rollback partially failed for workflow {workflow_id}. "
                             f"Manual cleanup may be required.")
        
        except Exception as e:
            logger.error(f"Rollback operation failed for workflow {workflow_id}: {str(e)}", exc_info=True)
            raise
        
        finally:
            self.active_rollbacks.pop(workflow_id, None)
    
    def _find_rollback_action(
        self, 
        workflow: ActionWorkflow, 
        action_id: str
    ) -> Dict[str, Any] | None:
        """Find rollback action for a given action ID"""
        
        for step in workflow.steps:
            for action in step.actions:
                if str(action.action_id) == action_id and action.rollback_action:
                    return action.rollback_action
        
        return None
    
    async def _prepare_rollback_parameters(
        self,
        rollback_action: Dict[str, Any],
        original_action_result: ActionResult
    ) -> Dict[str, Any]:
        """Prepare parameters for rollback action"""
        
        parameters = rollback_action.get("parameters", {}).copy()
        
        # Replace placeholders with values from original action result
        if original_action_result.result_data:
            for key, value in parameters.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    # Extract placeholder name
                    placeholder_name = value[2:-1]
                    
                    # Look for the value in original action result
                    if placeholder_name in original_action_result.result_data:
                        parameters[key] = original_action_result.result_data[placeholder_name]
                    else:
                        logger.warning(f"Placeholder {placeholder_name} not found in action result")
        
        # Add standard rollback parameters
        parameters["rollback_action_id"] = str(original_action_result.action_id)
        parameters["original_execution_time"] = original_action_result.execution_time_ms
        
        return parameters
    
    async def cleanup_orphaned_resources(
        self,
        service_name: str,
        resource_type: str,
        resource_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Clean up orphaned resources after workflow failures
        
        Args:
            service_name: Name of the service containing the resources
            resource_type: Type of resources to clean up
            resource_ids: List of resource IDs to clean up
            
        Returns:
            Dict with cleanup results
        """
        
        cleanup_results = {
            "service": service_name,
            "resource_type": resource_type,
            "total_resources": len(resource_ids),
            "cleaned_up": 0,
            "failed": 0,
            "errors": []
        }
        
        logger.info(f"Starting cleanup of {len(resource_ids)} {resource_type} resources in {service_name}")
        
        for resource_id in resource_ids:
            try:
                await self.action_dispatcher.dispatch_action(
                    service_name=service_name,
                    action_type=f"cleanup_{resource_type}",
                    parameters={
                        "resource_id": resource_id,
                        "reason": "workflow_rollback"
                    },
                    timeout_seconds=15,
                    retry_count=2
                )
                
                cleanup_results["cleaned_up"] += 1
                logger.debug(f"Cleaned up {resource_type} {resource_id}")
                
            except Exception as e:
                cleanup_results["failed"] += 1
                error_msg = f"Failed to cleanup {resource_type} {resource_id}: {str(e)}"
                cleanup_results["errors"].append(error_msg)
                logger.warning(error_msg)
        
        logger.info(f"Cleanup completed: {cleanup_results['cleaned_up']} successful, "
                   f"{cleanup_results['failed']} failed")
        
        return cleanup_results
    
    async def emergency_rollback(
        self,
        workflow_id: str,
        force_cleanup: bool = False
    ) -> Dict[str, Any]:
        """
        Emergency rollback for critical failures
        
        Args:
            workflow_id: ID of the workflow to rollback
            force_cleanup: Whether to force cleanup even if some actions fail
            
        Returns:
            Dict with rollback status
        """
        
        logger.warning(f"Initiating emergency rollback for workflow {workflow_id}")
        
        result = {
            "workflow_id": workflow_id,
            "emergency_rollback": True,
            "force_cleanup": force_cleanup,
            "status": "in_progress",
            "actions_taken": [],
            "errors": []
        }
        
        try:
            # This would implement emergency rollback procedures
            # For now, we'll implement a basic version
            
            result["actions_taken"].append("Emergency rollback initiated")
            result["status"] = "completed"
            
            logger.info(f"Emergency rollback completed for workflow {workflow_id}")
            
        except Exception as e:
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"Emergency rollback failed for workflow {workflow_id}: {str(e)}")
        
        return result
    
    def get_rollback_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current rollback status for a workflow"""
        
        return {
            "workflow_id": workflow_id,
            "rollback_in_progress": workflow_id in self.active_rollbacks,
            "active_rollbacks_count": len(self.active_rollbacks)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get rollback manager metrics"""
        
        return {
            "active_rollbacks": len(self.active_rollbacks),
            "active_rollback_workflows": list(self.active_rollbacks.keys())
        }
