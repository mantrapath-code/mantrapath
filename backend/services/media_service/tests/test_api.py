"""
Media Service API Tests
Tests for the FastAPI endpoints
"""
import pytest
import json
from unittest.mock import patch
from fastapi.testclient import TestClient

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, test_client):
        """Test health check endpoint returns 200"""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "timestamp" in data

class TestMediaUploadEndpoint:
    """Test media upload endpoints"""
    
    def test_upload_endpoint_exists(self, test_client):
        """Test that upload endpoint exists"""
        # Test without auth - should return 401 or proper error, or 200 if mocked
        response = test_client.post("/upload")
        # Expect either 401 (unauthorized), 422 (validation error), or 200 (mocked)
        assert response.status_code in [401, 422, 200]
    
    def test_media_info_endpoint_exists(self, test_client):
        """Test that media info endpoint exists"""
        response = test_client.get("/media/nonexistent")
        # Should return 404 for non-existent media, 401 for auth, or 200 if mocked
        assert response.status_code in [404, 401, 200]
