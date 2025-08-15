"""
Action Orchestrator Core Engine
Implements voice intent processing and cross-service workflow coordination
"""
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID

from ..models import (
    VoiceIntent, ActionWorkflow, WorkflowResult, ActionResult,
    IntentType, ConfidenceLevel, WorkflowStatus, CulturalContext,
    ServiceAction, WorkflowStep, OrchestrationRequest, OrchestrationResponse
)
from .intent_classifier import IntentClassifier
from .cultural_processor import CulturalProcessor
from .workflow_builder import WorkflowBuilder
from .action_dispatcher import ActionDispatcher
from .rollback_manager import RollbackManager

logger = logging.getLogger(__name__)


class ActionOrchestrator:
    """
    Central orchestration service for voice-driven cross-service workflows
    Implements all requirements from Story V3-BK-001
    """
    
    def __init__(
        self,
        intent_classifier: IntentClassifier,
        cultural_processor: CulturalProcessor,
        workflow_builder: WorkflowBuilder,
        action_dispatcher: ActionDispatcher,
        rollback_manager: RollbackManager
    ):
        self.intent_classifier = intent_classifier
        self.cultural_processor = cultural_processor
        self.workflow_builder = workflow_builder
        self.action_dispatcher = action_dispatcher
        self.rollback_manager = rollback_manager
        
        # Execution tracking
        self.active_workflows: Dict[UUID, ActionWorkflow] = {}
        self.workflow_locks: Dict[UUID, asyncio.Lock] = {}
        
        logger.info("Action Orchestrator initialized")
    
    async def orchestrate_action(
        self,
        request: OrchestrationRequest
    ) -> OrchestrationResponse:
        """
        Main orchestration method for voice-driven actions
        
        Acceptance Criteria Implemented:
        - ✓ Voice intent processing and classification
        - ✓ Cross-service workflow coordination  
        - ✓ Cultural context handling in workflows
        - ✓ Rollback and error handling for complex workflows
        """
        start_time = time.time()
        workflow_id = None
        
        try:
            # Input validation
            if not request.voice_input or not request.voice_input.strip():
                raise ValueError("Voice input is required")
            
            logger.info(f"Starting orchestration for user {request.user_id}")
            
            # Step 1: Process cultural context
            cultural_context = await self._process_cultural_context(
                request.voice_input, request.cultural_preferences
            )
            
            # Step 2: Classify intent with enhanced context
            intent = await self._classify_intent(
                request.voice_input, cultural_context, request.user_id
            )
            
            logger.info(f"Intent classified: {intent.intent_type} (confidence: {intent.confidence})")
            
            # Step 3: Build workflow based on intent and cultural context
            workflow = await self._build_workflow(intent, cultural_context, request.user_id)
            workflow_id = workflow.workflow_id
            
            # Register workflow for tracking
            self.active_workflows[workflow_id] = workflow
            self.workflow_locks[workflow_id] = asyncio.Lock()
            
            # Step 4: Execute workflow with coordination
            workflow_result = await self._execute_workflow_safely(workflow)
            
            # Step 5: Create response with cultural adaptations
            response = await self._create_response(
                workflow, workflow_result, intent, time.time() - start_time
            )
            
            logger.info(f"Orchestration completed for workflow {workflow_id}")
            return response
            
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}", exc_info=True)
            
            # Cleanup if workflow was started
            if workflow_id:
                await self._cleanup_failed_workflow(workflow_id)
            
            # Create error response
            error_response = await self._create_error_response(
                e, request, time.time() - start_time
            )
            
            return error_response
        
        finally:
            # Cleanup completed workflow
            if workflow_id and workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
                if workflow_id in self.workflow_locks:
                    del self.workflow_locks[workflow_id]

    async def _process_cultural_context(
        self,
        voice_input: str,
        cultural_preferences: Optional[Dict[str, Any]]
    ) -> CulturalContext:
        """Process and enhance cultural context from voice input"""
        return await self.cultural_processor.process_cultural_context(
            voice_input, cultural_preferences
        )

    async def _classify_intent(
        self,
        voice_input: str,
        cultural_context: CulturalContext,
        user_id: UUID
    ) -> VoiceIntent:
        """Classify intent with cultural context"""
        intent_result = await self.intent_classifier.classify_intent(
            voice_input, cultural_context
        )
        
        # Create VoiceIntent from intent result
        confidence = intent_result.confidence if hasattr(intent_result, 'confidence') else 0.8
        intent_type = intent_result.intent_type if hasattr(intent_result, 'intent_type') else IntentType.UNKNOWN
        
        return VoiceIntent(
            intent_type=intent_type,
            confidence=confidence,
            confidence_level=self._get_confidence_level(confidence),
            raw_text=voice_input,
            processed_text=voice_input.strip(),
            parameters=getattr(intent_result, 'entities', {}),
            cultural_context=cultural_context,
            user_id=user_id
        )

    async def _execute_workflow_safely(self, workflow: ActionWorkflow) -> WorkflowResult:
        """Execute workflow with proper error handling and rollback"""
        try:
            return await self._execute_workflow(workflow)
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            # Note: rollback will be handled by the calling method
            raise

    async def _cleanup_failed_workflow(self, workflow_id: UUID):
        """Clean up resources for failed workflow"""
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                await self._trigger_rollback(workflow, [])
        except Exception as e:
            logger.error(f"Failed to clean up workflow {workflow_id}: {str(e)}")

    async def _create_error_response(
        self,
        error: Exception,
        request: OrchestrationRequest,
        execution_time: float
    ) -> OrchestrationResponse:
        """Create error response with cultural context"""
        default_cultural_context = await self._get_default_cultural_context()
        
        error_intent = VoiceIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.0,
            confidence_level=ConfidenceLevel.VERY_LOW,
            raw_text=request.voice_input,
            processed_text=request.voice_input,
            cultural_context=default_cultural_context,
            user_id=request.user_id
        )
        
        return OrchestrationResponse(
            workflow_id=UUID("00000000-0000-0000-0000-000000000000"),
            intent=error_intent,
            status=WorkflowStatus.FAILED,
            message=await self._create_error_message(str(error), request.cultural_preferences)
        )
    
    async def _process_voice_intent(
        self,
        voice_input: str,
        user_id: UUID,
        session_id: Optional[UUID],
        cultural_preferences: Optional[Dict[str, Any]]
    ) -> VoiceIntent:
        """Process voice input and classify intent with cultural context"""
        
        # Step 1: Detect and process cultural context
        cultural_context = await self.cultural_processor.process_cultural_context(
            voice_input, cultural_preferences
        )
        
        # Step 2: Normalize and clean text based on cultural context
        processed_text = await self.cultural_processor.normalize_text(
            voice_input, cultural_context
        )
        
        # Step 3: Classify intent with cultural awareness
        intent_result = await self.intent_classifier.classify_intent(
            processed_text, cultural_context
        )
        
        # Step 4: Create VoiceIntent with all context
        intent = VoiceIntent(
            intent_type=intent_result["intent_type"],
            confidence=intent_result["confidence"],
            confidence_level=self._get_confidence_level(intent_result["confidence"]),
            raw_text=voice_input,
            processed_text=processed_text,
            parameters=intent_result.get("parameters", {}),
            cultural_context=cultural_context,
            user_id=user_id,
            session_id=session_id
        )
        
        return intent
    
    async def _build_workflow(
        self, 
        intent: VoiceIntent,
        context: Optional[Dict[str, Any]]
    ) -> ActionWorkflow:
        """Build workflow steps based on intent and cultural context"""
        
        workflow = await self.workflow_builder.build_workflow(
            intent, context
        )
        
        # Track workflow
        self.active_workflows[workflow.workflow_id] = workflow
        self.workflow_locks[workflow.workflow_id] = asyncio.Lock()
        
        logger.info(f"Workflow built with {len(workflow.steps)} steps")
        return workflow
    
    async def _execute_workflow(self, workflow: ActionWorkflow) -> WorkflowResult:
        """Execute workflow with cross-service coordination and error handling"""
        
        async with self.workflow_locks[workflow.workflow_id]:
            try:
                workflow.status = WorkflowStatus.PROCESSING
                workflow.started_at = time.time()
                
                action_results: List[ActionResult] = []
                successful_actions = 0
                failed_actions = 0
                
                # Execute each step
                for step_index, step in enumerate(workflow.steps):
                    workflow.current_step_index = step_index
                    
                    logger.info(f"Executing step {step_index + 1}/{len(workflow.steps)}")
                    
                    step_results = await self._execute_workflow_step(step, workflow)
                    action_results.extend(step_results)
                    
                    # Count results
                    step_successful = sum(1 for r in step_results if r.success)
                    step_failed = sum(1 for r in step_results if not r.success)
                    
                    successful_actions += step_successful
                    failed_actions += step_failed
                    
                    # Check if step failed critically
                    if step_failed > 0 and step.failure_handling == "abort":
                        logger.warning(f"Step {step_index} failed critically, aborting workflow")
                        
                        # Trigger rollback
                        await self._trigger_rollback(workflow, action_results)
                        workflow.status = WorkflowStatus.ROLLED_BACK
                        break
                
                # Finalize workflow
                if workflow.status == WorkflowStatus.PROCESSING:
                    workflow.status = WorkflowStatus.COMPLETED
                
                workflow.completed_at = time.time()
                
                # Create result
                total_time_ms = int((workflow.completed_at - workflow.started_at) * 1000)
                
                result = WorkflowResult(
                    workflow_id=workflow.workflow_id,
                    intent=workflow.intent,
                    status=workflow.status,
                    action_results=action_results,
                    total_execution_time_ms=total_time_ms,
                    successful_actions=successful_actions,
                    failed_actions=failed_actions,
                    cultural_context=workflow.cultural_context,
                    started_at=workflow.started_at,
                    completed_at=workflow.completed_at
                )
                
                # Cleanup
                self._cleanup_workflow(workflow.workflow_id)
                
                return result
                
            except Exception as e:
                logger.error(f"Workflow execution failed: {str(e)}", exc_info=True)
                
                # Trigger rollback on critical failure
                await self._trigger_rollback(workflow, [])
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = time.time()
                
                self._cleanup_workflow(workflow.workflow_id)
                raise
    
    async def _execute_workflow_step(
        self, 
        step: WorkflowStep, 
        workflow: ActionWorkflow
    ) -> List[ActionResult]:
        """Execute a single workflow step with proper coordination"""
        
        if step.parallel_execution:
            # Execute actions in parallel
            tasks = [
                self._execute_action(action, workflow)
                for action in step.actions
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            action_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create error result
                    action_results.append(ActionResult(
                        action_id=step.actions[i].action_id,
                        service_name=step.actions[i].service_name,
                        success=False,
                        error_message=str(result),
                        execution_time_ms=0
                    ))
                else:
                    action_results.append(result)
                    
        else:
            # Execute actions sequentially
            action_results = []
            for action in step.actions:
                try:
                    result = await self._execute_action(action, workflow)
                    action_results.append(result)
                    
                    # Check dependencies
                    if not result.success and action.action_id in [dep for a in step.actions for dep in a.dependencies]:
                        logger.warning(f"Dependency action {action.action_id} failed, may affect subsequent actions")
                        
                except Exception as e:
                    logger.error(f"Action execution failed: {str(e)}")
                    action_results.append(ActionResult(
                        action_id=action.action_id,
                        service_name=action.service_name,
                        success=False,
                        error_message=str(e),
                        execution_time_ms=0
                    ))
        
        return action_results
    
    async def _execute_action(
        self, 
        action: ServiceAction, 
        workflow: ActionWorkflow
    ) -> ActionResult:
        """Execute individual service action with cultural adaptations"""
        
        start_time = time.time()
        
        try:
            # Apply cultural adaptations to action parameters
            adapted_parameters = await self.cultural_processor.adapt_action_parameters(
                action.parameters,
                action.cultural_adaptations,
                workflow.cultural_context
            )
            
            # Execute action via dispatcher
            result_data = await self.action_dispatcher.dispatch_action(
                service_name=action.service_name,
                action_type=action.action_type,
                parameters=adapted_parameters,
                timeout_seconds=action.timeout_seconds,
                retry_count=action.retry_count
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Track successful action
            workflow.executed_actions.append(action.action_id)
            
            return ActionResult(
                action_id=action.action_id,
                service_name=action.service_name,
                success=True,
                result_data=result_data,
                execution_time_ms=execution_time_ms,
                cultural_adaptations_applied=action.cultural_adaptations
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Track failed action
            workflow.failed_actions.append(action.action_id)
            
            logger.error(f"Action {action.action_id} failed: {str(e)}")
            
            return ActionResult(
                action_id=action.action_id,
                service_name=action.service_name,
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time_ms,
                cultural_adaptations_applied=action.cultural_adaptations
            )
    
    async def _trigger_rollback(
        self, 
        workflow: ActionWorkflow, 
        completed_actions: List[ActionResult]
    ) -> None:
        """Trigger rollback for failed workflow"""
        
        logger.info(f"Triggering rollback for workflow {workflow.workflow_id}")
        
        try:
            await self.rollback_manager.rollback_workflow(
                workflow, completed_actions
            )
            logger.info("Rollback completed successfully")
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}", exc_info=True)
            # Note: Rollback failure is logged but doesn't re-raise
            # to avoid masking the original workflow failure
    
    async def _create_response(
        self,
        workflow: ActionWorkflow,
        workflow_result: WorkflowResult,
        intent: VoiceIntent,
        execution_time_seconds: float
    ) -> OrchestrationResponse:
        """Create culturally adapted response"""
        
        # Create human-readable message based on cultural context
        message = await self.cultural_processor.create_response_message(
            workflow_result, intent.cultural_context
        )
        
        # Apply cultural adaptations to response
        cultural_adaptations = await self.cultural_processor.adapt_response(
            workflow_result, intent.cultural_context
        )
        
        return OrchestrationResponse(
            workflow_id=workflow.workflow_id,
            intent=intent,
            workflow_result=workflow_result,
            estimated_completion_time=int(execution_time_seconds),
            status=workflow_result.status,
            message=message,
            cultural_adaptations=cultural_adaptations
        )
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert confidence score to level"""
        if confidence > 0.8:
            return ConfidenceLevel.HIGH
        elif confidence > 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence > 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    async def _get_default_cultural_context(self) -> CulturalContext:
        """Get default cultural context for error cases"""
        return CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="neutral",
            formality_level="moderate"
        )
    
    async def _create_error_message(
        self, 
        error: str, 
        cultural_preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Create culturally appropriate error message"""
        # This would integrate with the cultural processor
        # For now, return a generic message
        return f"I apologize, but I encountered an issue processing your request: {error}"
    
    def _cleanup_workflow(self, workflow_id: UUID) -> None:
        """Clean up workflow tracking data"""
        self.active_workflows.pop(workflow_id, None)
        self.workflow_locks.pop(workflow_id, None)
        
        logger.debug(f"Cleaned up workflow {workflow_id}")
    
    # Status and monitoring methods
    async def get_workflow_status(self, workflow_id: UUID) -> Optional[WorkflowStatus]:
        """Get current status of a workflow"""
        workflow = self.active_workflows.get(workflow_id)
        return workflow.status if workflow else None
    
    async def cancel_workflow(self, workflow_id: UUID) -> bool:
        """Cancel an active workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if workflow and workflow.status == WorkflowStatus.PROCESSING:
            workflow.status = WorkflowStatus.CANCELLED
            await self._trigger_rollback(workflow, [])
            self._cleanup_workflow(workflow_id)
            return True
        return False
    
    def get_active_workflow_count(self) -> int:
        """Get number of currently active workflows"""
        return len(self.active_workflows)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        return {
            "active_workflows": len(self.active_workflows),
            "workflow_statuses": {
                status.value: sum(1 for w in self.active_workflows.values() if w.status == status)
                for status in WorkflowStatus
            }
        }
