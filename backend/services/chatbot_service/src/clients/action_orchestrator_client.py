"""
Action Orchestrator Client for Chatbot Service
Provides integration with Action Orchestrator for intelligent workflow coordination
"""
import os
import logging
from typing import Dict, Any, Optional, List
import httpx
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OrchestrationRequest:
    """Request for action orchestration"""
    voice_input: str
    user_id: str
    language: str = "en"
    cultural_preferences: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

@dataclass
class VoiceIntent:
    """Voice intent classification result"""
    intent_type: str
    confidence: float
    confidence_level: str
    parameters: Dict[str, Any]

@dataclass
class ActionResult:
    """Result of an orchestrated action"""
    action_id: str
    service_name: str
    success: bool
    execution_time_ms: int
    cultural_adaptations_applied: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@dataclass
class OrchestrationResponse:
    """Response from action orchestration"""
    workflow_id: str
    status: str
    intent: VoiceIntent
    results: List[ActionResult]
    total_execution_time_ms: int
    cultural_context: Dict[str, Any]

class ActionOrchestratorClient:
    """Client for communicating with Action Orchestrator service"""
    
    def __init__(self):
        self.action_orchestrator_url = os.getenv(
            "ACTION_ORCHESTRATOR_URL", 
            "http://action-orchestrator:8012"
        )
        self.timeout = int(os.getenv("ACTION_ORCHESTRATOR_TIMEOUT", "60"))
        self.max_retries = int(os.getenv("ACTION_ORCHESTRATOR_MAX_RETRIES", "3"))
        self.is_enabled = os.getenv("ACTION_ORCHESTRATOR_ENABLED", "true").lower() == "true"
        
        logger.info(f"Action Orchestrator Client initialized - URL: {self.action_orchestrator_url}, Enabled: {self.is_enabled}")
    
    async def orchestrate_action(
        self, 
        request: OrchestrationRequest,
        jwt_token: Optional[str] = None
    ) -> Optional[OrchestrationResponse]:
        """
        Orchestrate an action through the Action Orchestrator service
        
        Args:
            request: The orchestration request
            jwt_token: JWT token for authentication
            
        Returns:
            OrchestrationResponse if successful, None if disabled or failed
        """
        if not self.is_enabled:
            logger.debug("Action Orchestrator is disabled, skipping orchestration")
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            # Prepare request payload
            payload: Dict[str, Any] = {
                "voice_input": request.voice_input,
                "user_id": request.user_id,
                "language": request.language,
                "cultural_preferences": request.cultural_preferences or {},
                "session_id": request.session_id,
                "context": request.context or {}
            }
            
            logger.info(f"Sending orchestration request to {self.action_orchestrator_url}/api/v1/orchestrate")
            logger.info(f"Payload: user_id={payload['user_id']}, session_id={payload['session_id']}, message='{payload['voice_input']}'")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.action_orchestrator_url}/api/v1/orchestrate",
                    json=payload,
                    headers=headers
                )
                
                logger.info(f"Action Orchestrator response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Action Orchestrator success: workflow_id={data.get('workflow_id')}")
                    return self._parse_orchestration_response(data)
                else:
                    logger.warning(
                        f"Action orchestration failed with status {response.status_code}: {response.text}"
                    )
                    return None
                    
        except httpx.TimeoutException:
            logger.error("Action Orchestrator request timed out")
            return None
        except httpx.RequestError as e:
            logger.error(f"Action Orchestrator request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in action orchestration: {e}")
            return None
    
    async def classify_intent(
        self, 
        message: str, 
        user_id: str,
        language: str = "en",
        cultural_context: Optional[Dict[str, Any]] = None,
        jwt_token: Optional[str] = None
    ) -> Optional[VoiceIntent]:
        """
        Classify intent using Action Orchestrator's ML-powered intent classifier
        
        Args:
            message: User message to classify
            user_id: User identifier
            language: Language code
            cultural_context: Cultural context for classification
            jwt_token: JWT token for authentication
            
        Returns:
            VoiceIntent if successful, None if failed
        """
        if not self.is_enabled:
            return None
            
        try:
            # Use orchestrate_action to get intent classification
            request = OrchestrationRequest(
                voice_input=message,
                user_id=user_id,
                language=language,
                cultural_preferences=cultural_context,
                context={"intent_only": True}  # Flag for intent-only classification
            )
            
            response = await self.orchestrate_action(request, jwt_token)
            return response.intent if response else None
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return None
    
    async def get_workflow_status(
        self, 
        workflow_id: str,
        jwt_token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow
        
        Args:
            workflow_id: Workflow identifier
            jwt_token: JWT token for authentication
            
        Returns:
            Workflow status dict if successful, None if failed
        """
        if not self.is_enabled:
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.action_orchestrator_url}/api/v1/workflow/{workflow_id}/status",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Workflow status check failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Workflow status check failed: {e}")
            return None
    
    async def get_supported_intents(
        self, 
        jwt_token: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of supported intents from Action Orchestrator
        
        Args:
            jwt_token: JWT token for authentication
            
        Returns:
            List of supported intents if successful, None if failed
        """
        if not self.is_enabled:
            return None
            
        try:
            headers = {"Content-Type": "application/json"}
            if jwt_token:
                headers["Authorization"] = f"Bearer {jwt_token}"
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.action_orchestrator_url}/api/v1/intents",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Supported intents fetch failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Supported intents fetch failed: {e}")
            return None
    
    async def health_check(self) -> bool:
        """
        Check if Action Orchestrator service is healthy
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.is_enabled:
            return False
            
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.action_orchestrator_url}/health")
                return response.status_code == 200
        except Exception:
            return False
    
    def _parse_orchestration_response(self, data: Dict[str, Any]) -> OrchestrationResponse:
        """Parse orchestration response from API"""
        intent_data = data.get("intent", {})
        intent = VoiceIntent(
            intent_type=intent_data.get("intent_type", "unknown"),
            confidence=intent_data.get("confidence", 0.0),
            confidence_level=intent_data.get("confidence_level", "low"),
            parameters=intent_data.get("parameters", {})
        )
        
        results: List[ActionResult] = []
        for result_data in data.get("results", []):
            result = ActionResult(
                action_id=result_data.get("action_id", ""),
                service_name=result_data.get("service_name", ""),
                success=result_data.get("success", False),
                execution_time_ms=result_data.get("execution_time_ms", 0),
                cultural_adaptations_applied=result_data.get("cultural_adaptations_applied"),
                result_data=result_data.get("result_data"),
                error_message=result_data.get("error_message")
            )
            results.append(result)
        
        return OrchestrationResponse(
            workflow_id=data.get("workflow_id", ""),
            status=data.get("status", "unknown"),
            intent=intent,
            results=results,
            total_execution_time_ms=data.get("total_execution_time_ms", 0),
            cultural_context=data.get("cultural_context", {})
        )

# Global client instance
action_orchestrator_client = ActionOrchestratorClient()
