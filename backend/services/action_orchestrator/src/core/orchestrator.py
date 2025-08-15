"""
Action Orchestrator Core Engine
Implements voice intent processing and cross-service workflow coordination
"""
import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4

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
        
        # Service coordination
        self.supported_intents = [
            IntentType.JOURNAL_ENTRY,
            IntentType.MOOD_TRACKING,
            IntentType.CHAT_CONVERSATION,
            IntentType.COMMUNITY_INTERACTION,
            IntentType.PROFILE_UPDATE,
            IntentType.ANALYTICS_QUERY,
            IntentType.CONTENT_SEARCH,
            IntentType.VOICE_COMMAND
        ]
        
        logger.info("Action Orchestrator initialized")
    
    async def orchestrate_action(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """
        Main orchestration method for processing voice input into cross-service workflows
        """
        workflow_id: Optional[UUID] = None
        start_time = time.time()
        
        try:
            # Input validation
            if not request.voice_input or not request.voice_input.strip():
                raise ValueError("Voice input is required")
            
            logger.info(f"Starting orchestration for user {request.user_id}")
            
            # Step 1: Process cultural context
            cultural_context = await self._process_cultural_context(
                request.voice_input, request.cultural_preferences
            )
            
            # Step 2: Classify intent with cultural context
            intent = await self._classify_intent(
                request.voice_input, cultural_context, request.user_id
            )
            
            logger.info(f"Intent classified: {intent.intent_type} (confidence: {intent.confidence})")
            
            # Step 3: Build workflow based on intent and cultural context
            workflow = await self._build_workflow(intent, cultural_context)
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
            return await self._create_error_response(
                e, request, time.time() - start_time
            )
        
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
        try:
            return await self.cultural_processor.process_cultural_context(
                voice_input, cultural_preferences or {}
            )
        except Exception as e:
            logger.warning(f"Cultural processing failed, using defaults: {e}")
            return self._get_default_cultural_context()

    async def _classify_intent(
        self,
        voice_input: str,
        cultural_context: CulturalContext,
        user_id: UUID
    ) -> VoiceIntent:
        """Classify intent with cultural context"""
        try:
            intent_result = await self.intent_classifier.classify_intent(
                voice_input, cultural_context
            )
            
            # Handle different return types from classifier
            if hasattr(intent_result, 'intent_type'):
                # It's already a VoiceIntent or similar object
                return intent_result
            elif isinstance(intent_result, dict):
                # It's a dictionary result
                confidence = intent_result.get('confidence', 0.8)
                intent_type = intent_result.get('intent_type', IntentType.UNKNOWN)
                parameters = intent_result.get('parameters', {})
                
                return VoiceIntent(
                    intent_type=intent_type,
                    confidence=confidence,
                    confidence_level=self._get_confidence_level(confidence),
                    raw_text=voice_input,
                    processed_text=voice_input.strip(),
                    parameters=parameters,
                    cultural_context=cultural_context,
                    user_id=user_id
                )
            else:
                # Fallback
                return self._create_fallback_intent(voice_input, cultural_context, user_id)
                
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return self._create_fallback_intent(voice_input, cultural_context, user_id)

    async def _build_workflow(
        self, 
        intent: VoiceIntent,
        cultural_context: CulturalContext
    ) -> ActionWorkflow:
        """Build workflow steps based on intent and cultural context"""
        try:
            return await self.workflow_builder.build_workflow(intent, cultural_context)
        except Exception as e:
            logger.error(f"Workflow building failed: {e}")
            return self._create_fallback_workflow(intent, cultural_context)

    async def _execute_workflow_safely(self, workflow: ActionWorkflow) -> WorkflowResult:
        """Execute workflow with proper error handling and rollback"""
        workflow_id = workflow.workflow_id
        start_time = time.time()
        action_results: List[ActionResult] = []
        
        try:
            # Update workflow status
            workflow.status = WorkflowStatus.PENDING
            workflow.started_at = datetime.now(timezone.utc)
            
            # Execute steps sequentially
            for step_index, step in enumerate(workflow.steps):
                workflow.current_step_index = step_index
                
                # Execute actions in step
                step_results = await self._execute_step(step)
                action_results.extend(step_results)
                
                # Check for failures
                failed_results = [r for r in step_results if not r.success]
                if failed_results:
                    logger.error(f"Step {step_index} failed, triggering rollback")
                    await self._trigger_rollback(workflow, action_results)
                    workflow.status = WorkflowStatus.FAILED
                    break
            
            # Mark workflow as completed if all steps succeeded
            if workflow.status != WorkflowStatus.FAILED:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now(timezone.utc)
            else:
                workflow.completed_at = datetime.now(timezone.utc)
            
            # Create workflow result
            execution_time_ms = int((time.time() - start_time) * 1000)
            successful_actions = len([r for r in action_results if r.success])
            failed_actions = len([r for r in action_results if not r.success])
            
            return WorkflowResult(
                workflow_id=workflow_id,
                intent=workflow.intent,
                status=workflow.status,
                action_results=action_results,
                total_execution_time_ms=execution_time_ms,
                successful_actions=successful_actions,
                failed_actions=failed_actions,
                cultural_context=workflow.cultural_context,
                started_at=workflow.started_at or datetime.now(timezone.utc),
                completed_at=workflow.completed_at or datetime.now(timezone.utc)
            )
                
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            workflow.status = WorkflowStatus.FAILED
            workflow.error_message = str(e)
            workflow.completed_at = datetime.now(timezone.utc)
            
            # Trigger rollback for any completed actions
            if action_results:
                await self._trigger_rollback(workflow, action_results)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            successful_actions = len([r for r in action_results if r.success])
            failed_actions = len([r for r in action_results if not r.success])
            
            return WorkflowResult(
                workflow_id=workflow_id,
                intent=workflow.intent,
                status=WorkflowStatus.FAILED,
                action_results=action_results,
                total_execution_time_ms=execution_time_ms,
                successful_actions=successful_actions,
                failed_actions=failed_actions,
                cultural_context=workflow.cultural_context,
                started_at=workflow.started_at or datetime.now(timezone.utc),
                completed_at=workflow.completed_at or datetime.now(timezone.utc),
                error_summary=str(e)
            )

    async def _execute_step(self, step: WorkflowStep) -> List[ActionResult]:
        """Execute a workflow step with its actions"""
        action_results: List[ActionResult] = []
        
        if step.parallel_execution:
            # Execute actions in parallel
            tasks = []
            for action in step.actions:
                task = self._execute_action(action)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
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
            for action in step.actions:
                try:
                    result = await self._execute_action(action)
                    action_results.append(result)
                except Exception as e:
                    action_results.append(ActionResult(
                        action_id=action.action_id,
                        service_name=action.service_name,
                        success=False,
                        error_message=str(e),
                        execution_time_ms=0
                    ))
        
        return action_results

    async def _execute_action(self, action: ServiceAction) -> ActionResult:
        """Execute an individual service action"""
        start_time = time.time()
        
        try:
            result = await self.action_dispatcher.dispatch_action(
                service_name=action.service_name,
                action_type=action.action_type,
                parameters=action.parameters,
                timeout_seconds=action.timeout_seconds,
                retry_count=action.retry_count
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            return ActionResult(
                action_id=action.action_id,
                service_name=action.service_name,
                success=True,
                result_data=result,
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            return ActionResult(
                action_id=action.action_id,
                service_name=action.service_name,
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time_ms
            )

    async def _trigger_rollback(self, workflow: ActionWorkflow, completed_actions: List[ActionResult]):
        """Trigger rollback for failed workflow"""
        try:
            await self.rollback_manager.rollback_workflow(workflow, completed_actions)
        except Exception as e:
            logger.error(f"Rollback failed: {e}")

    async def _create_response(
        self,
        workflow: ActionWorkflow,
        workflow_result: WorkflowResult,
        intent: VoiceIntent,
        execution_time_seconds: float
    ) -> OrchestrationResponse:
        """Create response with cultural adaptations"""
        return OrchestrationResponse(
            workflow_id=workflow.workflow_id,
            intent=intent,
            workflow_result=workflow_result,
            status=workflow_result.status,
            message=f"Workflow completed in {execution_time_seconds:.2f} seconds"
        )

    async def _create_error_response(
        self,
        error: Exception,
        request: OrchestrationRequest,
        execution_time: float
    ) -> OrchestrationResponse:
        """Create error response with cultural context"""
        default_cultural_context = self._get_default_cultural_context()
        
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
            workflow_id=uuid4(),
            intent=error_intent,
            status=WorkflowStatus.FAILED,
            message=f"Orchestration failed: {str(error)}"
        )

    async def get_workflow_status(self, workflow_id: UUID) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                "workflow_id": str(workflow_id),
                "status": workflow.status.value,
                "current_step": workflow.current_step_index,
                "total_steps": len(workflow.steps),
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None
            }
        
        # Return a basic status for unknown workflows
        return {
            "workflow_id": str(workflow_id),
            "status": "unknown",
            "message": "Workflow not found"
        }

    async def _cleanup_failed_workflow(self, workflow_id: UUID):
        """Clean up resources for failed workflow"""
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                await self._trigger_rollback(workflow, [])
        except Exception as e:
            logger.error(f"Failed to clean up workflow {workflow_id}: {str(e)}")

    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Determine confidence level from numeric confidence"""
        if confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def _get_default_cultural_context(self) -> CulturalContext:
        """Get default cultural context for fallback scenarios"""
        return CulturalContext(
            language="en",
            cultural_region="global",
            communication_style="neutral",
            formality_level="moderate",
            time_zone="UTC",
            date_format="ISO"
        )

    def _create_fallback_intent(self, voice_input: str, cultural_context: CulturalContext, user_id: UUID) -> VoiceIntent:
        """Create fallback intent when classification fails"""
        return VoiceIntent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.1,
            confidence_level=ConfidenceLevel.VERY_LOW,
            raw_text=voice_input,
            processed_text=voice_input.strip(),
            parameters={},
            cultural_context=cultural_context,
            user_id=user_id
        )

    def _create_fallback_workflow(self, intent: VoiceIntent, cultural_context: CulturalContext) -> ActionWorkflow:
        """Create fallback workflow when building fails"""
        return ActionWorkflow(
            intent=intent,
            steps=[],
            status=WorkflowStatus.PENDING,
            cultural_context=cultural_context
        )

    # Additional Service Coordination Methods
    async def get_supported_intents(self) -> List[IntentType]:
        """Get list of supported intent types"""
        return self.supported_intents.copy()

    async def rollback_workflow(self, workflow_id: UUID) -> Dict[str, Any]:
        """Rollback a completed workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            try:
                await self._trigger_rollback(workflow, [])
                workflow.status = WorkflowStatus.ROLLED_BACK
                return {
                    "workflow_id": str(workflow_id),
                    "rollback_status": "completed",
                    "rollback_steps": len(workflow.steps),
                    "execution_time": 1.0
                }
            except Exception as e:
                return {
                    "workflow_id": str(workflow_id),
                    "rollback_status": "failed",
                    "error": str(e),
                    "execution_time": 0.0
                }
        return {
            "workflow_id": str(workflow_id),
            "rollback_status": "not_found",
            "execution_time": 0.0
        }

    # Workflow Management Methods
    async def estimate_workflow_duration(self, intent: VoiceIntent) -> int:
        """Estimate workflow execution duration in milliseconds"""
        try:
            # Basic estimation based on intent complexity
            base_time = 1000  # 1 second base
            
            complexity_multipliers = {
                IntentType.JOURNAL_ENTRY: 2.0,
                IntentType.MOOD_TRACKING: 1.5,
                IntentType.CHAT_CONVERSATION: 1.0,
                IntentType.COMMUNITY_INTERACTION: 3.0,
                IntentType.PROFILE_UPDATE: 1.2,
                IntentType.ANALYTICS_QUERY: 2.5,
                IntentType.CONTENT_SEARCH: 1.8,
                IntentType.VOICE_COMMAND: 1.0
            }
            
            multiplier = complexity_multipliers.get(intent.intent_type, 1.0)
            return int(base_time * multiplier)
            
        except Exception as e:
            logger.warning(f"Duration estimation failed: {e}")
            return 2000  # Default 2 seconds

    async def validate_workflow_feasibility(self, intent: VoiceIntent) -> Dict[str, Any]:
        """Validate if a workflow can be executed"""
        try:
            # Check intent support
            supported_intents = await self.get_supported_intents()
            if intent.intent_type not in supported_intents:
                return {
                    "feasible": False,
                    "reason": f"Intent type {intent.intent_type} not supported"
                }
            
            # Check confidence level
            if intent.confidence_level == ConfidenceLevel.VERY_LOW:
                return {
                    "feasible": False,
                    "reason": "Intent confidence too low for execution"
                }
            
            # Check service availability (simplified)
            estimated_duration = await self.estimate_workflow_duration(intent)
            
            return {
                "feasible": True,
                "estimated_duration_ms": estimated_duration,
                "required_services": self._get_required_services(intent),
                "confidence_assessment": intent.confidence_level.value
            }
            
        except Exception as e:
            logger.error(f"Feasibility validation failed: {e}")
            return {
                "feasible": False,
                "reason": f"Validation error: {str(e)}"
            }

    def _get_required_services(self, intent: VoiceIntent) -> List[str]:
        """Get list of services required for an intent"""
        service_mapping = {
            IntentType.JOURNAL_ENTRY: ["journal_service", "analytics_service"],
            IntentType.MOOD_TRACKING: ["mood_service", "analytics_service"],
            IntentType.CHAT_CONVERSATION: ["chatbot_service"],
            IntentType.COMMUNITY_INTERACTION: ["community_service", "profile_service"],
            IntentType.PROFILE_UPDATE: ["profile_service"],
            IntentType.ANALYTICS_QUERY: ["analytics_service"],
            IntentType.CONTENT_SEARCH: ["search_service", "content_service"],
            IntentType.VOICE_COMMAND: ["command_service"]
        }
        return service_mapping.get(intent.intent_type, ["general_service"])

    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator metrics"""
        return {
            "active_workflows": len(self.active_workflows),
            "supported_intents": len(self.supported_intents),
            "workflow_statuses": {
                status.value: sum(1 for w in self.active_workflows.values() if w.status == status)
                for status in WorkflowStatus
            }
        }
