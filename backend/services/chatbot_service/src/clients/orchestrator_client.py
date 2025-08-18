"""
Action Orchestrator Client for Chatbot Service
Provides workflow orchestration and action coordination capabilities
"""
import logging
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ActionStatus(Enum):
    """Action execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class ActionRequest:
    """Action request data"""
    action_type: str
    parameters: Dict[str, Any]
    priority: str
    context: Dict[str, Any]
    dependencies: List[str]

@dataclass
class ActionResult:
    """Action execution result"""
    action_id: str
    action_type: str
    status: ActionStatus
    result_data: Dict[str, Any]
    error_message: Optional[str]
    execution_time: float
    created_at: str
    completed_at: Optional[str]

@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    workflow_id: str
    name: str
    description: str
    actions: List[ActionRequest]
    workflow_type: str
    trigger_conditions: Dict[str, Any]

@dataclass
class WorkflowExecution:
    """Workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_action: Optional[str]
    completed_actions: List[str]
    failed_actions: List[str]
    context: Dict[str, Any]
    started_at: str
    completed_at: Optional[str]

class ActionOrchestratorClient:
    """Client for communicating with Action Orchestrator Service"""
    
    def __init__(self):
        import os
        self.orchestrator_url = os.getenv("ACTION_ORCHESTRATOR_URL", "http://action-orchestrator:8009")
        self.timeout = int(os.getenv("ACTION_ORCHESTRATOR_TIMEOUT", "60"))
        self.max_retries = int(os.getenv("ACTION_ORCHESTRATOR_MAX_RETRIES", "3"))
        self.default_priority = os.getenv("ACTION_DEFAULT_PRIORITY", "medium")
        self.workflow_timeout = int(os.getenv("WORKFLOW_TIMEOUT", "300"))
        self.is_enabled = os.getenv("ACTION_ORCHESTRATOR_ENABLED", "true").lower() == "true"
        
        # Supported action types
        self.supported_actions = {
            "crisis_intervention",
            "mood_assessment", 
            "resource_recommendation",
            "followup_scheduling",
            "escalation_trigger",
            "context_update",
            "notification_send",
            "data_analysis",
            "user_engagement",
            "content_generation"
        }
        
        logger.info(f"Action Orchestrator Client initialized - URL: {self.orchestrator_url}, Enabled: {self.is_enabled}")
    
    async def health_check(self) -> bool:
        """Check if Action Orchestrator Service is healthy"""
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.orchestrator_url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Action Orchestrator health check failed: {e}")
            return False
    
    async def execute_action(
        self, 
        action_type: str,
        parameters: Dict[str, Any],
        priority: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> Optional[ActionResult]:
        """
        Execute a single action via Action Orchestrator
        
        Args:
            action_type: Type of action to execute
            parameters: Action parameters
            priority: Action priority (low, medium, high, urgent)
            context: Additional context for action
            jwt_token: JWT token for authentication
            
        Returns:
            ActionResult object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Action Orchestrator is disabled, action not executed")
            return self._mock_action_result(action_type, parameters)
            
        if action_type not in self.supported_actions:
            logger.warning(f"Unsupported action type: {action_type}")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "action_type": action_type,
                "parameters": parameters,
                "priority": priority or self.default_priority,
                "context": context or {}
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.orchestrator_url}/api/actions/execute",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_action_result(data)
                else:
                    logger.error(f"Action execution failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return None
    
    async def execute_workflow(
        self, 
        workflow_id: str,
        context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> Optional[WorkflowExecution]:
        """
        Execute a predefined workflow
        
        Args:
            workflow_id: ID of workflow to execute
            context: Initial workflow context
            jwt_token: JWT token for authentication
            
        Returns:
            WorkflowExecution object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Action Orchestrator is disabled, workflow not executed")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "workflow_id": workflow_id,
                "context": context or {}
            }
            
            async with httpx.AsyncClient(timeout=self.workflow_timeout) as client:
                response = await client.post(
                    f"{self.orchestrator_url}/api/workflows/execute",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_workflow_execution(data)
                else:
                    logger.error(f"Workflow execution failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return None
    
    async def create_workflow(
        self, 
        workflow_definition: WorkflowDefinition,
        jwt_token: Optional[str] = None
    ) -> bool:
        """
        Create a new workflow definition
        
        Args:
            workflow_definition: Workflow definition to create
            jwt_token: JWT token for authentication
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled:
            logger.debug("Action Orchestrator is disabled, workflow not created")
            return False
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            payload = {
                "workflow_id": workflow_definition.workflow_id,
                "name": workflow_definition.name,
                "description": workflow_definition.description,
                "workflow_type": workflow_definition.workflow_type,
                "actions": [self._action_request_to_dict(action) for action in workflow_definition.actions],
                "trigger_conditions": workflow_definition.trigger_conditions
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.orchestrator_url}/api/workflows/create",
                    headers=headers,
                    json=payload
                )
                
                return response.status_code == 201
                    
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return False
    
    async def get_action_status(
        self, 
        action_id: str,
        jwt_token: Optional[str] = None
    ) -> Optional[ActionResult]:
        """
        Get status of a specific action
        
        Args:
            action_id: ID of action to check
            jwt_token: JWT token for authentication
            
        Returns:
            ActionResult object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Action Orchestrator is disabled, action status not available")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.orchestrator_url}/api/actions/{action_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_action_result(data)
                else:
                    logger.error(f"Get action status failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting action status: {e}")
            return None
    
    async def get_workflow_status(
        self, 
        execution_id: str,
        jwt_token: Optional[str] = None
    ) -> Optional[WorkflowExecution]:
        """
        Get status of a workflow execution
        
        Args:
            execution_id: ID of workflow execution to check
            jwt_token: JWT token for authentication
            
        Returns:
            WorkflowExecution object or None if failed
        """
        if not self.is_enabled:
            logger.debug("Action Orchestrator is disabled, workflow status not available")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.orchestrator_url}/api/workflows/executions/{execution_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_workflow_execution(data)
                else:
                    logger.error(f"Get workflow status failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return None
    
    def get_supported_actions(self) -> List[str]:
        """Get list of supported action types"""
        return list(self.supported_actions)
    
    def _mock_action_result(self, action_type: str, parameters: Dict[str, Any]) -> ActionResult:
        """Create mock action result for fallback"""
        import uuid
        from datetime import datetime
        
        return ActionResult(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            status=ActionStatus.COMPLETED,
            result_data={"mock": True, "parameters": parameters},
            error_message=None,
            execution_time=0.1,
            created_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat()
        )
    
    def _action_request_to_dict(self, action_request: ActionRequest) -> Dict[str, Any]:
        """Convert ActionRequest to dictionary"""
        return {
            "action_type": action_request.action_type,
            "parameters": action_request.parameters,
            "priority": action_request.priority,
            "context": action_request.context,
            "dependencies": action_request.dependencies
        }
    
    def _parse_action_result(self, data: Dict[str, Any]) -> ActionResult:
        """Parse action result from API response"""
        return ActionResult(
            action_id=data.get("action_id", ""),
            action_type=data.get("action_type", ""),
            status=ActionStatus(data.get("status", "pending")),
            result_data=data.get("result_data", {}),
            error_message=data.get("error_message"),
            execution_time=data.get("execution_time", 0.0),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at")
        )
    
    def _parse_workflow_execution(self, data: Dict[str, Any]) -> WorkflowExecution:
        """Parse workflow execution from API response"""
        return WorkflowExecution(
            execution_id=data.get("execution_id", ""),
            workflow_id=data.get("workflow_id", ""),
            status=WorkflowStatus(data.get("status", "created")),
            current_action=data.get("current_action"),
            completed_actions=data.get("completed_actions", []),
            failed_actions=data.get("failed_actions", []),
            context=data.get("context", {}),
            started_at=data.get("started_at", ""),
            completed_at=data.get("completed_at")
        )

# Global client instance
action_orchestrator_client = ActionOrchestratorClient()
