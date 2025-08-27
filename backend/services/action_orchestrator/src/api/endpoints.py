"""
Action Orchestrator API Endpoints
REST API for orchestrating cross-service actions
"""
import logging
from typing import Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..core import ActionOrchestrator
from ..models import OrchestrationRequest, OrchestrationResponse, WorkflowStatus

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["orchestration"])


async def get_orchestrator() -> ActionOrchestrator:
    """Dependency to get orchestrator instance"""
    # This would be injected by the main application
    # For now, we'll create a placeholder
    from ..services.orchestrator_factory import create_orchestrator
    return await create_orchestrator()


@router.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_action(
    request: OrchestrationRequest,
    orchestrator: ActionOrchestrator = Depends(get_orchestrator)
) -> OrchestrationResponse:
    """
    Orchestrate cross-service action based on voice input
    
    This endpoint handles the main orchestration functionality:
    - Voice intent processing and classification
    - Cross-service workflow coordination
    - Cultural context handling in workflows  
    - Rollback and error handling for complex workflows
    """
    try:
        logger.info(f"Processing orchestration request for user {request.user_id}")
        
        # Orchestrate the action
        response = await orchestrator.orchestrate_action(request)
        
        logger.info(f"Orchestration completed with status: {response.status}")
        return response
        
    except Exception as e:
        logger.error(f"Orchestration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration failed: {str(e)}"
        )


@router.get("/workflow/{workflow_id}/status")
async def get_workflow_status(
    workflow_id: UUID,
    orchestrator: ActionOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Get the current status of a workflow"""
    try:
        status = await orchestrator.get_workflow_status(workflow_id)
        
        if status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow {workflow_id} not found"
            )
        
        return {
            "workflow_id": str(workflow_id),
            "status": status.value,
            "timestamp": "now"  # Would use actual timestamp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get workflow status: {str(e)}"
        )


@router.post("/workflow/{workflow_id}/cancel")
async def cancel_workflow(
    workflow_id: UUID,
    orchestrator: ActionOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Cancel an active workflow"""
    try:
        success = await orchestrator.cancel_workflow(workflow_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Workflow {workflow_id} not found or cannot be cancelled"
            )
        
        return {
            "workflow_id": str(workflow_id),
            "status": "cancelled",
            "message": "Workflow cancelled successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel workflow: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "action_orchestrator",
        "version": "1.0.0"
    }


@router.get("/metrics")
async def get_metrics(
    orchestrator: ActionOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Get orchestrator metrics"""
    try:
        metrics = orchestrator.get_metrics()
        
        return {
            "service": "action_orchestrator",
            "metrics": metrics,
            "timestamp": "now"  # Would use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get metrics: {str(e)}"
        )


@router.get("/services/status")
async def get_service_status(
    orchestrator: ActionOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Get status of all connected services"""
    try:
        # Get service status from action dispatcher
        status = await orchestrator.action_dispatcher.get_service_status()
        
        return {
            "services": status,
            "timestamp": "now"  # Would use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Failed to get service status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service status: {str(e)}"
        )


# Voice-specific endpoints
@router.post("/voice/intent/classify")
async def classify_voice_intent(
    request: Dict[str, Any],
    orchestrator: ActionOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Classify voice intent without executing workflow"""
    try:
        voice_input = request.get("voice_input", "")
        user_id = request.get("user_id")
        cultural_preferences = request.get("cultural_preferences")
        
        if not voice_input or not user_id:
            raise HTTPException(
                status_code=400,
                detail="voice_input and user_id are required"
            )
        
        # Process voice intent
        intent = await orchestrator._process_voice_intent(
            voice_input=voice_input,
            user_id=UUID(user_id),
            session_id=request.get("session_id"),
            cultural_preferences=cultural_preferences
        )
        
        return {
            "intent_type": intent.intent_type.value,
            "confidence": intent.confidence,
            "confidence_level": intent.confidence_level.value,
            "parameters": intent.parameters,
            "cultural_context": {
                "language": intent.cultural_context.language,
                "cultural_region": intent.cultural_context.cultural_region,
                "communication_style": intent.cultural_context.communication_style,
                "formality_level": intent.cultural_context.formality_level
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Intent classification failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Intent classification failed: {str(e)}"
        )


# Cultural adaptation endpoint
@router.post("/cultural/adapt")
async def adapt_cultural_context(
    request: Dict[str, Any],
    orchestrator: ActionOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Adapt content based on cultural context"""
    try:
        content = request.get("content", "")
        cultural_preferences = request.get("cultural_preferences", {})
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="content is required"
            )
        
        # Process cultural context
        cultural_context = await orchestrator.cultural_processor.process_cultural_context(
            voice_input=content,
            cultural_preferences=cultural_preferences
        )
        
        # Normalize text
        normalized_text = await orchestrator.cultural_processor.normalize_text(
            content, cultural_context
        )
        
        return {
            "original_content": content,
            "normalized_content": normalized_text,
            "cultural_context": {
                "language": cultural_context.language,
                "cultural_region": cultural_context.cultural_region,
                "communication_style": cultural_context.communication_style,
                "formality_level": cultural_context.formality_level,
                "cultural_sensitivities": cultural_context.cultural_sensitivities
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cultural adaptation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Cultural adaptation failed: {str(e)}"
        )
