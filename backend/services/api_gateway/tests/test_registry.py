"""
Test Serfrom core.service_registry import ServiceRegistry, ServiceInstance, ServiceStatus

# Test service URLs - configurable via environment
TEST_SERVICE_URL = os.getenv("TEST_SERVICE_URL", "http://test-service:8080")
TEST_SERVICE_UNHEALTHY_URL = os.getenv("TEST_SERVICE_UNHEALTHY_URL", "http://test-service-2:8081")
TEST_SERVICE_UPDATED_URL = os.getenv("TEST_SERVICE_UPDATED_URL", "http://test-service-updated:9090")

@pytest.mark.asyncio
class TestServiceRegistry:Registry functionality
"""
import os
import pytest
import sys
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from registry.service_registry import ServiceRegistry
from core.models import ServiceInstance, ServiceStatus

@pytest.mark.asyncio
class TestServiceRegistry:
    """Test service registry operations"""
    
    async def test_register_service(self):
        """Test service registration"""
        registry = ServiceRegistry()
        
        service = ServiceInstance(
            id="test-service-1",
            name="test-service",
            url=TEST_SERVICE_URL,
            health_path="/health"
        )
        
        await registry.register_service(service)
        
        services = registry.get_all_services()
        assert "test-service" in services
        assert len(services["test-service"]) == 1
        assert services["test-service"][0].id == "test-service-1"
    
    async def test_deregister_service(self):
        """Test service deregistration"""
        registry = ServiceRegistry()
        
        service = ServiceInstance(
            id="test-service-1",
            name="test-service",
            url=TEST_SERVICE_URL
        )
        
        await registry.register_service(service)
        await registry.deregister_service("test-service", "test-service-1")
        
        services = registry.get_all_services()
        assert len(services.get("test-service", [])) == 0
    
    async def test_get_healthy_services(self):
        """Test getting healthy services only"""
        registry = ServiceRegistry()
        
        healthy_service = ServiceInstance(
            id="healthy-1",
            name="test-service",
            url=TEST_SERVICE_URL,
            status=ServiceStatus.HEALTHY
        )
        
        unhealthy_service = ServiceInstance(
            id="unhealthy-1",
            name="test-service",
            url=TEST_SERVICE_UNHEALTHY_URL,
            status=ServiceStatus.UNHEALTHY
        )
        
        await registry.register_service(healthy_service)
        await registry.register_service(unhealthy_service)
        
        healthy_services = registry.get_healthy_services("test-service")
        assert len(healthy_services) == 1
        assert healthy_services[0].id == "healthy-1"
    
    async def test_update_existing_service(self):
        """Test updating an existing service"""
        registry = ServiceRegistry()
        
        service = ServiceInstance(
            id="test-service-1",
            name="test-service",
            url=TEST_SERVICE_URL,
            weight=1
        )
        
        await registry.register_service(service)
        
        # Update the same service with new URL
        updated_service = ServiceInstance(
            id="test-service-1",
            name="test-service",
            url=TEST_SERVICE_UPDATED_URL,
            weight=2
        )
        
        await registry.register_service(updated_service)
        
        services = registry.get_all_services()
        assert len(services["test-service"]) == 1
        assert services["test-service"][0].url == TEST_SERVICE_UPDATED_URL
        assert services["test-service"][0].weight == 2
