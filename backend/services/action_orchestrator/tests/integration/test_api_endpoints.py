"""
Integration tests for Action Orchestrator API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

from main import app


class TestActionOrchestratorAPI:
    """Integration tests for Action Orchestrator API"""
    
    @pytest.fixture
    def client(self):
        """Test client for API"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "MantraPath Action Orchestrator"
        assert data["status"] == "running"
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "action_orchestrator"
    
    @patch('src.services.get_orchestrator_instance')
    def test_orchestrate_endpoint_success(self, mock_get_orchestrator, client):
        """Test orchestrate endpoint with successful workflow"""
        # Mock orchestrator instance
        mock_orchestrator = AsyncMock()
        mock_orchestrator.orchestrate_action.return_value = {
            "workflow_id": "wf_123",
            "status": "completed",
            "results": [{
                "step_id": "step_1",
                "success": True,
                "data": {"id": "entry_123"},
                "execution_time": 1.5
            }],
            "execution_time": 2.0
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        # Test request
        request_data = {
            "voice_intent": {
                "text": "I want to journal about my meditation",
                "language": "en",
                "confidence": 0.95
            },
            "user_id": "user123",
            "cultural_context": {
                "country": "US",
                "timezone": "America/New_York",
                "language": "en"
            }
        }
        
        response = client.post("/orchestrate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "wf_123"
        assert data["status"] == "completed"
        assert len(data["results"]) == 1
    
    @patch('src.services.get_orchestrator_instance')
    def test_orchestrate_endpoint_validation_error(self, mock_get_orchestrator, client):
        """Test orchestrate endpoint with validation error"""
        # Invalid request - missing required fields
        request_data = {
            "voice_intent": {
                "text": "",  # Empty text
                "language": "en"
                # Missing confidence
            },
            "user_id": "user123"
        }
        
        response = client.post("/orchestrate", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.services.get_orchestrator_instance')
    def test_get_workflow_status_success(self, mock_get_orchestrator, client):
        """Test getting workflow status"""
        # Mock orchestrator instance
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_workflow_status.return_value = {
            "workflow_id": "wf_123",
            "status": "completed",
            "created_at": "2024-01-01T12:00:00Z",
            "completed_at": "2024-01-01T12:00:02Z",
            "execution_time": 2.0
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        response = client.get("/workflow/wf_123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "wf_123"
        assert data["status"] == "completed"
    
    @patch('src.services.get_orchestrator_instance')
    def test_get_workflow_status_not_found(self, mock_get_orchestrator, client):
        """Test getting workflow status for non-existent workflow"""
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_workflow_status.return_value = None
        mock_get_orchestrator.return_value = mock_orchestrator
        
        response = client.get("/workflow/nonexistent")
        
        assert response.status_code == 404
    
    @patch('src.services.get_orchestrator_instance')
    def test_rollback_workflow_success(self, mock_get_orchestrator, client):
        """Test rolling back a workflow"""
        mock_orchestrator = AsyncMock()
        mock_orchestrator.rollback_workflow.return_value = {
            "workflow_id": "wf_123",
            "rollback_status": "completed",
            "rollback_steps": 2,
            "execution_time": 1.0
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        response = client.post("/workflow/wf_123/rollback")
        
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "wf_123"
        assert data["rollback_status"] == "completed"
    
    def test_get_supported_intents(self, client):
        """Test getting supported intents"""
        response = client.get("/intents")
        
        assert response.status_code == 200
        data = response.json()
        assert "intents" in data
        assert len(data["intents"]) > 0
        
        # Check for expected intent types
        intent_types = [intent["type"] for intent in data["intents"]]
        assert "journal_creation" in intent_types
        assert "mood_tracking" in intent_types
    
    @patch('src.services.get_orchestrator_instance')
    def test_orchestrate_endpoint_processing_error(self, mock_get_orchestrator, client):
        """Test orchestrate endpoint with processing error"""
        # Mock orchestrator that raises an exception
        mock_orchestrator = AsyncMock()
        mock_orchestrator.orchestrate_action.side_effect = Exception("Processing failed")
        mock_get_orchestrator.return_value = mock_orchestrator
        
        request_data = {
            "voice_intent": {
                "text": "I want to journal",
                "language": "en",
                "confidence": 0.95
            },
            "user_id": "user123"
        }
        
        response = client.post("/orchestrate", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/")
        
        # Should have CORS headers configured
        assert response.status_code in [200, 405]  # OPTIONS may not be explicitly handled
    
    def test_api_documentation_endpoints(self, client):
        """Test that API documentation endpoints are available"""
        # OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        # Should be valid JSON
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
    
    @patch('src.services.get_orchestrator_instance')
    def test_concurrent_requests(self, mock_get_orchestrator, client):
        """Test handling concurrent requests"""
        import concurrent.futures
        import threading
        
        mock_orchestrator = AsyncMock()
        mock_orchestrator.orchestrate_action.return_value = {
            "workflow_id": "wf_concurrent",
            "status": "completed",
            "results": [],
            "execution_time": 1.0
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        def make_request():
            request_data = {
                "voice_intent": {
                    "text": "I want to journal",
                    "language": "en",
                    "confidence": 0.95
                },
                "user_id": f"user_{threading.current_thread().ident}"
            }
            return client.post("/orchestrate", json=request_data)
        
        # Execute multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_request_validation_edge_cases(self, client):
        """Test request validation edge cases"""
        # Empty request body
        response = client.post("/orchestrate", json={})
        assert response.status_code == 422
        
        # Invalid confidence value
        request_data = {
            "voice_intent": {
                "text": "test",
                "language": "en",
                "confidence": 1.5  # Invalid - > 1.0
            },
            "user_id": "user123"
        }
        response = client.post("/orchestrate", json=request_data)
        assert response.status_code == 422
        
        # Invalid language code
        request_data = {
            "voice_intent": {
                "text": "test",
                "language": "",  # Empty language
                "confidence": 0.9
            },
            "user_id": "user123"
        }
        response = client.post("/orchestrate", json=request_data)
        assert response.status_code == 422
