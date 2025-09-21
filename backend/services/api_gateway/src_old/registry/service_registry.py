"""
Service Registry - Manages service discovery and health monitoring
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from src.core.models import ServiceInstance, ServiceStatus, HealthCheckResult
from src.core.config import gateway_config, service_config

logger = logging.getLogger(__name__)

class ServiceRegistry:
    """Manages service instances and health checks"""
    
    def __init__(self):
        self._services: Dict[str, List[ServiceInstance]] = {}
        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """Start the service registry"""
        logger.info("Starting service registry...")
        await self._initialize_services()
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Service registry started")
    
    async def stop(self):
        """Stop the service registry"""
        logger.info("Stopping service registry...")
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Service registry stopped")
    
    async def _initialize_services(self):
        """Initialize services from configuration with standardized ports.
        If discovery is enabled, allow multiple instances via env lists for targeted services.
        """
        def _register_list(name: str, urls: List[str], health_path: str):
            if not urls:
                return False
            instances: List[ServiceInstance] = []
            for idx, url in enumerate(urls, start=1):
                inst = ServiceInstance(
                    id=f"{name}-{idx}",
                    name=name,
                    url=url,
                    health_path=health_path,
                    weight=1,
                )
                instances.append(inst)
                logger.info(f"Registered service: {name} instance {idx} at {url} (health: {health_path})")
            self._services[name] = instances
            return True

        # Default single-instance registrations (backward compatible)
        defaults = [
            ("auth", service_config.auth_service_url, service_config.auth_service_health_path),
            ("profile", service_config.profile_service_url, service_config.profile_service_health_path),
            ("mood", service_config.mood_service_url, service_config.mood_service_health_path),
            ("chatbot", service_config.chatbot_service_url, service_config.chatbot_service_health_path),
            ("content", service_config.content_service_url, service_config.content_service_health_path),
            ("community", service_config.community_service_url, service_config.community_service_health_path),
            ("notification", service_config.notification_service_url, service_config.notification_service_health_path),
            ("ml", service_config.ml_service_url, service_config.ml_service_health_path),
            ("media", service_config.media_service_url, service_config.media_service_health_path),
            ("translation", service_config.translation_service_url, service_config.translation_service_health_path),
            ("voice", service_config.voice_service_url, service_config.voice_service_health_path),
            ("action-orchestrator", service_config.action_orchestrator_url, service_config.action_orchestrator_health_path),
            ("models", service_config.models_service_url, service_config.models_service_health_path),
            ("ai-events", service_config.ai_event_processor_url, service_config.ai_event_processor_health_path),
            ("ai-context", service_config.ai_context_store_url, service_config.ai_context_store_health_path),
        ]

        # If discovery is enabled, override specific services with multi-instance lists
        if gateway_config.discovery_enabled:
            # Translation service multi-instance
            if service_config.translation_service_urls:
                _register_list("translation", service_config.translation_service_urls, service_config.translation_service_health_path)
            # Models service multi-instance
            if service_config.models_service_urls:
                _register_list("models", service_config.models_service_urls, service_config.models_service_health_path)

        # Register any service not overridden above using single-instance default
        for name, url, health_path in defaults:
            if name in self._services:
                continue
            service_instance = ServiceInstance(
                id=f"{name}-1",
                name=name,
                url=url,
                health_path=health_path,
                weight=1
            )
            self._services[name] = [service_instance]
            logger.info(f"Registered service: {name} at {url} (health: {health_path})")
    
    async def register_service(self, service: ServiceInstance):
        """Register a new service instance"""
        if service.name not in self._services:
            self._services[service.name] = []
        
        # Check if service already exists
        for existing in self._services[service.name]:
            if existing.id == service.id:
                logger.warning(f"Service {service.id} already registered, updating...")
                existing.url = service.url
                existing.weight = service.weight
                existing.metadata = service.metadata
                return
        
        self._services[service.name].append(service)
        logger.info(f"Registered new service instance: {service.id}")
    
    async def deregister_service(self, service_name: str, service_id: str):
        """Deregister a service instance"""
        if service_name in self._services:
            self._services[service_name] = [
                s for s in self._services[service_name] if s.id != service_id
            ]
            logger.info(f"Deregistered service instance: {service_id}")
    
    def get_healthy_services(self, service_name: str) -> List[ServiceInstance]:
        """Get all healthy instances of a service"""
        if service_name not in self._services:
            return []
        
        return [
            service for service in self._services[service_name]
            if service.status == ServiceStatus.HEALTHY
        ]
    
    def get_all_services(self) -> Dict[str, List[ServiceInstance]]:
        """Get all registered services"""
        return self._services.copy()
    
    async def _health_check_loop(self):
        """Continuous health checking loop"""
        while self._running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(gateway_config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5)  # Short delay before retrying
    
    async def _perform_health_checks(self):
        """Perform health checks on all services"""
        tasks = []
        for service_list in self._services.values():
            for service in service_list:
                task = asyncio.create_task(self._check_service_health(service))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_service_health(self, service: ServiceInstance) -> HealthCheckResult:
        """Check health of a single service"""
        start_time = datetime.now()
        
        try:
            health_url = f"{service.url.rstrip('/')}{service.health_path}"
            
            async with httpx.AsyncClient(timeout=gateway_config.health_check_timeout) as client:
                response = await client.get(health_url)
                response_time = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    service.status = ServiceStatus.HEALTHY
                    service.failure_count = 0
                    status = ServiceStatus.HEALTHY
                else:
                    service.status = ServiceStatus.UNHEALTHY
                    service.failure_count += 1
                    status = ServiceStatus.UNHEALTHY
                
                service.last_health_check = datetime.now()
                
                result = HealthCheckResult(
                    service_id=service.id,
                    status=status,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    details={"status_code": response.status_code}
                )
                
                if status == ServiceStatus.HEALTHY:
                    logger.debug(f"Health check passed for {service.id}: {response_time:.3f}s")
                else:
                    logger.warning(f"Health check failed for {service.id}: HTTP {response.status_code}")
                
                return result
                
        except Exception as e:
            service.status = ServiceStatus.UNHEALTHY
            service.failure_count += 1
            service.last_health_check = datetime.now()
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            result = HealthCheckResult(
                service_id=service.id,
                status=ServiceStatus.UNHEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                error=str(e)
            )
            
            logger.warning(f"Health check failed for {service.id}: {e}")
            return result
