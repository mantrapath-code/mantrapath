"""
Action Dispatcher
Handles routing and execution of service actions with retry logic
"""
import asyncio
import logging
import time
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class ActionDispatcher:
    """
    Dispatches actions to appropriate services with retry and timeout handling
    
    Manages service communication and error handling for cross-service coordination
    """
    
    def __init__(self):
        # Service endpoint configurations
        self.service_endpoints = self._initialize_service_endpoints()
        
        # HTTP client for service communication
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        
        # Circuit breaker states for services
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Action Dispatcher initialized")
    
    async def dispatch_action(
        self,
        service_name: str,
        action_type: str,
        parameters: Dict[str, Any],
        timeout_seconds: int = 30,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Dispatch action to specified service with retry logic
        
        Args:
            service_name: Target service name
            action_type: Type of action to perform
            parameters: Action parameters
            timeout_seconds: Timeout for the action
            retry_count: Maximum retry attempts
            
        Returns:
            Dict containing action result data
            
        Raises:
            Exception: If action fails after all retries
        """
        
        # Check if service is available (circuit breaker)
        if not await self._is_service_available(service_name):
            raise Exception(f"Service {service_name} is currently unavailable (circuit breaker open)")
        
        # Get service endpoint configuration
        endpoint_config = self.service_endpoints.get(service_name)
        if not endpoint_config:
            raise Exception(f"Unknown service: {service_name}")
        
        # Prepare request
        request_data = {
            "action_type": action_type,
            "parameters": parameters,
            "timeout": timeout_seconds
        }
        
        # Execute with retry logic
        last_exception = None
        for attempt in range(retry_count + 1):
            try:
                if attempt > 0:
                    # Exponential backoff
                    await asyncio.sleep(min(2 ** attempt, 10))
                    logger.info(f"Retrying {service_name}/{action_type} (attempt {attempt + 1})")
                
                result = await self._execute_service_action(
                    service_name, endpoint_config, request_data, timeout_seconds
                )
                
                # Mark service as healthy
                await self._mark_service_healthy(service_name)
                
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Action {service_name}/{action_type} failed (attempt {attempt + 1}): {str(e)}")
                
                # Update circuit breaker on failure
                await self._record_service_failure(service_name)
                
                if attempt == retry_count:
                    break
        
        # All retries failed
        await self._mark_service_unhealthy(service_name)
        raise Exception(f"Action {service_name}/{action_type} failed after {retry_count + 1} attempts: {str(last_exception)}")
    
    async def _execute_service_action(
        self,
        service_name: str,
        endpoint_config: Dict[str, Any],
        request_data: Dict[str, Any],
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """Execute action against service endpoint"""
        
        base_url = endpoint_config["base_url"]
        action_endpoint = f"{base_url}/api/v1/actions"
        
        # Add authentication if needed
        headers = {
            "Content-Type": "application/json",
            "X-Service-Name": "action_orchestrator"
        }
        
        start_time = time.time()
        
        try:
            response = await self.http_client.post(
                action_endpoint,
                json=request_data,
                headers=headers,
                timeout=timeout_seconds
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                logger.info(f"Action completed in {execution_time:.3f}s: {service_name}")
                return result_data
            else:
                error_message = f"Service returned status {response.status_code}"
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", error_message)
                except:
                    error_message = response.text
                
                raise Exception(f"Service error: {error_message}")
                
        except httpx.TimeoutException:
            execution_time = time.time() - start_time
            raise Exception(f"Service timeout after {execution_time:.1f}s")
        
        except httpx.RequestError as e:
            execution_time = time.time() - start_time
            raise Exception(f"Service connection error: {str(e)}")
    
    async def _is_service_available(self, service_name: str) -> bool:
        """Check if service is available (circuit breaker check)"""
        
        circuit_breaker = self.circuit_breakers.get(service_name, {
            "state": "closed",  # closed, open, half_open
            "failure_count": 0,
            "last_failure": None,
            "failure_threshold": 5,
            "recovery_timeout": 60  # seconds
        })
        
        current_time = time.time()
        
        if circuit_breaker["state"] == "open":
            # Check if we can move to half-open
            if circuit_breaker["last_failure"] and \
               current_time - circuit_breaker["last_failure"] > circuit_breaker["recovery_timeout"]:
                circuit_breaker["state"] = "half_open"
                self.circuit_breakers[service_name] = circuit_breaker
                logger.info(f"Circuit breaker for {service_name} moved to half-open")
                return True
            else:
                return False
        
        return True
    
    async def _record_service_failure(self, service_name: str) -> None:
        """Record service failure for circuit breaker"""
        
        circuit_breaker = self.circuit_breakers.get(service_name, {
            "state": "closed",
            "failure_count": 0,
            "last_failure": None,
            "failure_threshold": 5,
            "recovery_timeout": 60
        })
        
        circuit_breaker["failure_count"] += 1
        circuit_breaker["last_failure"] = time.time()
        
        # Check if we should open the circuit breaker
        if circuit_breaker["failure_count"] >= circuit_breaker["failure_threshold"]:
            circuit_breaker["state"] = "open"
            logger.warning(f"Circuit breaker opened for {service_name} after {circuit_breaker['failure_count']} failures")
        
        self.circuit_breakers[service_name] = circuit_breaker
    
    async def _mark_service_healthy(self, service_name: str) -> None:
        """Mark service as healthy (reset circuit breaker)"""
        
        if service_name in self.circuit_breakers:
            circuit_breaker = self.circuit_breakers[service_name]
            
            if circuit_breaker["state"] == "half_open":
                # Move to closed state
                circuit_breaker["state"] = "closed"
                circuit_breaker["failure_count"] = 0
                circuit_breaker["last_failure"] = None
                logger.info(f"Circuit breaker closed for {service_name}")
            elif circuit_breaker["state"] == "closed":
                # Reset failure count
                circuit_breaker["failure_count"] = 0
            
            self.circuit_breakers[service_name] = circuit_breaker
    
    async def _mark_service_unhealthy(self, service_name: str) -> None:
        """Mark service as unhealthy (open circuit breaker)"""
        
        circuit_breaker = self.circuit_breakers.get(service_name, {
            "state": "closed",
            "failure_count": 0,
            "last_failure": None,
            "failure_threshold": 5,
            "recovery_timeout": 60
        })
        
        circuit_breaker["state"] = "open"
        circuit_breaker["last_failure"] = time.time()
        
        self.circuit_breakers[service_name] = circuit_breaker
        logger.error(f"Service {service_name} marked as unhealthy")
    
    def _initialize_service_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Initialize service endpoint configurations"""
        return {
            "mood_service": {
                "base_url": "http://mood-service:8003",
                "timeout": 30,
                "health_endpoint": "/health"
            },
            "journal_service": {
                "base_url": "http://journal-service:8004",
                "timeout": 45,
                "health_endpoint": "/health"
            },
            "chatbot_service": {
                "base_url": "http://chatbot-service:8008",
                "timeout": 30,
                "health_endpoint": "/health"
            },
            "profile_service": {
                "base_url": "http://profile-service:8002",
                "timeout": 20,
                "health_endpoint": "/health"
            },
            "community_service": {
                "base_url": "http://community-service:8006",
                "timeout": 30,
                "health_endpoint": "/health"
            },
            "analytics_service": {
                "base_url": "http://ml-service:8010",
                "timeout": 60,
                "health_endpoint": "/health"
            },
            "content_service": {
                "base_url": "http://content-service:8005",
                "timeout": 25,
                "health_endpoint": "/health"
            }
        }
    
    async def health_check_service(self, service_name: str) -> bool:
        """Perform health check on service"""
        
        endpoint_config = self.service_endpoints.get(service_name)
        if not endpoint_config:
            return False
        
        health_url = f"{endpoint_config['base_url']}{endpoint_config['health_endpoint']}"
        
        try:
            response = await self.http_client.get(health_url, timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        
        status = {}
        
        for service_name in self.service_endpoints.keys():
            circuit_breaker = self.circuit_breakers.get(service_name, {"state": "closed"})
            health_check = await self.health_check_service(service_name)
            
            status[service_name] = {
                "circuit_breaker_state": circuit_breaker["state"],
                "failure_count": circuit_breaker.get("failure_count", 0),
                "health_check": health_check,
                "available": health_check and circuit_breaker["state"] != "open"
            }
        
        return status
    
    def _get_service_url(self, service_name: str) -> str:
        """Get service URL for a given service name"""
        from config import settings
        
        service_urls = {
            "journal_service": settings.MOOD_SERVICE_URL,  # Journal is part of mood service
            "mood_service": settings.MOOD_SERVICE_URL, 
            "content_service": settings.CONTENT_SERVICE_URL,
            "community_service": settings.COMMUNITY_SERVICE_URL,
            "notification_service": settings.NOTIFICATION_SERVICE_URL,
            "chatbot_service": settings.CHATBOT_SERVICE_URL,
            "profile_service": settings.PROFILE_SERVICE_URL,
            "ml_service": settings.ML_SERVICE_URL,
            "media_service": settings.MEDIA_SERVICE_URL,
            "translation_service": settings.TRANSLATION_SERVICE_URL,
            "voice_service": settings.VOICE_SERVICE_URL,
            "auth_service": settings.AUTH_SERVICE_URL
        }
        
        return service_urls.get(service_name, "http://localhost:8000")
    
    async def close(self) -> None:
        """Close HTTP client"""
        await self.http_client.aclose()
        logger.info("Action Dispatcher closed")
