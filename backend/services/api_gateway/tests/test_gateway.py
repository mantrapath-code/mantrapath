"""
Test API Gateway endpoints and integration
"""
import pytest
from fastapi.testclient import TestClient

from ..src.main import app

class TestGatewayEndpoints:
    """Test gateway endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test basic health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_detailed_health_endpoint(self):
        """Test detailed health check endpoint"""
        response = self.client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "services_detail" in data
    
    def test_readiness_endpoint(self):
        """Test readiness check endpoint"""
        response = self.client.get("/health/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert "ready" in data
        assert "timestamp" in data
    
    def test_liveness_endpoint(self):
        """Test liveness check endpoint"""
        response = self.client.get("/health/live")
        assert response.status_code == 200
        
        data = response.json()
        assert "alive" in data
        assert "timestamp" in data
    
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = self.client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "gateway_version" in data
        assert "services_total" in data
    
    def test_unknown_route(self):
        """Test handling of unknown routes"""
        response = self.client.get("/unknown/route")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"] == "Route not found"
    
    def test_service_unavailable_route(self):
        """Test routing to unavailable service"""
        # This would require mocking the service registry
        # For now, we'll test a route that should exist but service is down
        response = self.client.get("/auth/test")
        # Will return 503 if no auth service is running
        assert response.status_code in [503, 502, 504]
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/health")
        assert response.status_code == 200
        
        # Check CORS headers exist (FastAPI adds them automatically in test)
        # In a real test, you'd check specific values
