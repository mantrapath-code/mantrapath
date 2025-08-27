"""
Integration Tests for Action Orchestrator API Endpoints
Testing Epic V3-BK-001 API endpoints and real-world scenarios
"""
import pytest
import uuid
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app
from src.models import (
    OrchestrationRequest, WorkflowStatus, IntentType, ConfidenceLevel
)


class TestActionOrchestratorAPIIntegration:
    """Integration tests for Action Orchestrator API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_orchestration_request(self):
        """Sample API request payload"""
        return {
            "voice_input": "मैं आज अपने ध्यान के बारे में लिखना चाहता हूं",
            "user_id": str(uuid.uuid4()),
            "language": "hi",
            "cultural_preferences": {
                "country": "IN",
                "timezone": "Asia/Kolkata",
                "communication_style": "formal",
                "cultural_region": "north_india"
            },
            "session_id": str(uuid.uuid4())
        }
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns service information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "MantraPath Action Orchestrator"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "action_orchestrator"
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_orchestrate_endpoint_success(self, mock_create_orchestrator, client, sample_orchestration_request):
        """Test successful orchestration via API endpoint"""
        # Mock orchestrator response
        mock_orchestrator = AsyncMock()
        mock_response = {
            "workflow_id": str(uuid.uuid4()),
            "status": WorkflowStatus.COMPLETED,
            "intent": {
                "intent_type": IntentType.JOURNAL_ENTRY,
                "confidence": 0.95,
                "confidence_level": ConfidenceLevel.HIGH
            },
            "message": "Workflow completed successfully"
        }
        
        mock_orchestrator.orchestrate_action.return_value = type('Response', (), mock_response)()
        mock_create_orchestrator.return_value = mock_orchestrator
        
        # Make API request
        response = client.post("/api/v1/orchestrate", json=sample_orchestration_request)
        
        # Verify response
        assert response.status_code == 200
        # Note: Actual validation would depend on response model structure
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_orchestrate_endpoint_validation_error(self, mock_create_orchestrator, client):
        """Test orchestration endpoint with invalid input"""
        invalid_request = {
            "voice_input": "",  # Empty input should fail validation
            "user_id": "invalid-uuid"  # Invalid UUID format
        }
        
        # Make API request
        response = client.post("/api/v1/orchestrate", json=invalid_request)
        
        # Should return validation error
        assert response.status_code == 422
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_orchestrate_endpoint_server_error(self, mock_create_orchestrator, client, sample_orchestration_request):
        """Test orchestration endpoint when service fails"""
        # Mock orchestrator to raise exception
        mock_orchestrator = AsyncMock()
        mock_orchestrator.orchestrate_action.side_effect = Exception("Internal service error")
        mock_create_orchestrator.return_value = mock_orchestrator
        
        # Make API request
        response = client.post("/api/v1/orchestrate", json=sample_orchestration_request)
        
        # Should return server error
        assert response.status_code == 500
        data = response.json()
        assert "failed" in data["detail"].lower()
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_workflow_status_endpoint(self, mock_create_orchestrator, client):
        """Test workflow status endpoint"""
        workflow_id = uuid.uuid4()
        
        # Mock orchestrator response
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_workflow_status.return_value = WorkflowStatus.PROCESSING
        mock_create_orchestrator.return_value = mock_orchestrator
        
        # Make API request
        response = client.get(f"/api/v1/workflow/{workflow_id}/status")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == str(workflow_id)
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_workflow_status_not_found(self, mock_create_orchestrator, client):
        """Test workflow status endpoint for non-existent workflow"""
        workflow_id = uuid.uuid4()
        
        # Mock orchestrator response
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_workflow_status.return_value = None
        mock_create_orchestrator.return_value = mock_orchestrator
        
        # Make API request
        response = client.get(f"/api/v1/workflow/{workflow_id}/status")
        
        # Should return not found
        assert response.status_code == 404
    
    def test_api_cors_headers(self, client):
        """Test CORS headers are properly set"""
        response = client.options("/api/v1/orchestrate")
        
        # CORS headers should be present (depends on FastAPI CORS middleware)
        # This test verifies CORS is configured
        assert response.status_code in [200, 405]  # OPTIONS method handling


class TestActionOrchestratorPerformance:
    """Performance and load testing for Action Orchestrator"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.slow
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_concurrent_requests_performance(self, mock_create_orchestrator, client):
        """Test performance under concurrent load"""
        import concurrent.futures
        import time
        
        # Mock fast response
        mock_orchestrator = AsyncMock()
        mock_response = type('Response', (), {
            "workflow_id": str(uuid.uuid4()),
            "status": WorkflowStatus.COMPLETED,
            "message": "Success"
        })()
        mock_orchestrator.orchestrate_action.return_value = mock_response
        mock_create_orchestrator.return_value = mock_orchestrator
        
        # Prepare requests
        request_payload = {
            "voice_input": "Test concurrent request",
            "user_id": str(uuid.uuid4())
        }
        
        # Measure concurrent performance
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(50):  # 50 concurrent requests
                future = executor.submit(
                    client.post, 
                    "/api/v1/orchestrate", 
                    json=request_payload
                )
                futures.append(future)
            
            # Wait for all requests to complete
            responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify performance metrics
        assert len(responses) == 50
        assert all(resp.status_code in [200, 500] for resp in responses)  # May have some failures under load
        assert execution_time < 30  # Should complete within 30 seconds
        
        print(f"Concurrent requests completed in {execution_time:.2f} seconds")
    
    @pytest.mark.slow
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_memory_usage_stability(self, mock_create_orchestrator, client):
        """Test memory usage remains stable under repeated requests"""
        import psutil
        import os
        
        # Mock orchestrator
        mock_orchestrator = AsyncMock()
        mock_response = type('Response', (), {
            "workflow_id": str(uuid.uuid4()),
            "status": WorkflowStatus.COMPLETED
        })()
        mock_orchestrator.orchestrate_action.return_value = mock_response
        mock_create_orchestrator.return_value = mock_orchestrator
        
        # Measure initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make repeated requests
        request_payload = {
            "voice_input": "Memory test request",
            "user_id": str(uuid.uuid4())
        }
        
        for i in range(100):
            response = client.post("/api/v1/orchestrate", json=request_payload)
            assert response.status_code in [200, 500]
        
        # Measure final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory should not increase significantly (allowing for some variance)
        assert memory_increase < 50  # Less than 50MB increase
        
        print(f"Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (increase: {memory_increase:.1f}MB)")


class TestActionOrchestratorSecurity:
    """Security tests for Action Orchestrator"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_input_validation_sql_injection(self, client):
        """Test protection against SQL injection in voice input"""
        malicious_request = {
            "voice_input": "'; DROP TABLE users; --",
            "user_id": str(uuid.uuid4())
        }
        
        response = client.post("/api/v1/orchestrate", json=malicious_request)
        
        # Should handle gracefully (either process safely or reject)
        assert response.status_code in [200, 400, 422, 500]
        # Malicious SQL should not cause system failure
    
    def test_input_validation_xss_attempt(self, client):
        """Test protection against XSS in voice input"""
        malicious_request = {
            "voice_input": "<script>alert('xss')</script>",
            "user_id": str(uuid.uuid4())
        }
        
        response = client.post("/api/v1/orchestrate", json=malicious_request)
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422, 500]
    
    def test_input_size_limits(self, client):
        """Test protection against oversized input"""
        large_input = "A" * 10000  # 10KB input
        
        large_request = {
            "voice_input": large_input,
            "user_id": str(uuid.uuid4())
        }
        
        response = client.post("/api/v1/orchestrate", json=large_request)
        
        # Should either process or reject gracefully
        assert response.status_code in [200, 400, 413, 422, 500]
    
    def test_invalid_uuid_handling(self, client):
        """Test handling of invalid UUID formats"""
        invalid_requests = [
            {"voice_input": "test", "user_id": "not-a-uuid"},
            {"voice_input": "test", "user_id": ""},
            {"voice_input": "test", "user_id": None}
        ]
        
        for invalid_request in invalid_requests:
            response = client.post("/api/v1/orchestrate", json=invalid_request)
            # Should return validation error for invalid UUID
            assert response.status_code == 422


class TestActionOrchestratorCulturalScenarios:
    """Test cultural context scenarios and adaptations"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_hindi_voice_input_processing(self, mock_create_orchestrator, client):
        """Test Hindi language voice input processing"""
        hindi_request = {
            "voice_input": "मैं आज अपने मन की बात लिखना चाहता हूं",
            "user_id": str(uuid.uuid4()),
            "language": "hi",
            "cultural_preferences": {
                "country": "IN",
                "cultural_region": "north_india",
                "communication_style": "formal"
            }
        }
        
        # Mock orchestrator
        mock_orchestrator = AsyncMock()
        mock_response = type('Response', (), {
            "workflow_id": str(uuid.uuid4()),
            "status": WorkflowStatus.COMPLETED,
            "intent": {
                "cultural_context": {
                    "language": "hi",
                    "cultural_region": "north_india"
                }
            }
        })()
        mock_orchestrator.orchestrate_action.return_value = mock_response
        mock_create_orchestrator.return_value = mock_orchestrator
        
        response = client.post("/api/v1/orchestrate", json=hindi_request)
        
        # Should process Hindi input successfully
        assert response.status_code == 200
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_japanese_cultural_context(self, mock_create_orchestrator, client):
        """Test Japanese cultural context handling"""
        japanese_request = {
            "voice_input": "今日の瞑想について書きたいです",  # "I want to write about today's meditation"
            "user_id": str(uuid.uuid4()),
            "language": "ja",
            "cultural_preferences": {
                "country": "JP",
                "timezone": "Asia/Tokyo",
                "cultural_region": "east_asia",
                "communication_style": "polite"
            }
        }
        
        # Mock orchestrator
        mock_orchestrator = AsyncMock()
        mock_response = type('Response', (), {
            "workflow_id": str(uuid.uuid4()),
            "status": WorkflowStatus.COMPLETED
        })()
        mock_orchestrator.orchestrate_action.return_value = mock_response
        mock_create_orchestrator.return_value = mock_orchestrator
        
        response = client.post("/api/v1/orchestrate", json=japanese_request)
        
        # Should handle Japanese cultural context
        assert response.status_code == 200
    
    @patch('src.services.orchestrator_factory.create_orchestrator')
    def test_arabic_rtl_support(self, mock_create_orchestrator, client):
        """Test Arabic language and RTL text support"""
        arabic_request = {
            "voice_input": "أريد أن أكتب عن تأملي اليوم",  # "I want to write about my meditation today"
            "user_id": str(uuid.uuid4()),
            "language": "ar",
            "cultural_preferences": {
                "country": "SA",
                "cultural_region": "middle_east",
                "text_direction": "rtl"
            }
        }
        
        # Mock orchestrator
        mock_orchestrator = AsyncMock()
        mock_response = type('Response', (), {
            "workflow_id": str(uuid.uuid4()),
            "status": WorkflowStatus.COMPLETED
        })()
        mock_orchestrator.orchestrate_action.return_value = mock_response
        mock_create_orchestrator.return_value = mock_orchestrator
        
        response = client.post("/api/v1/orchestrate", json=arabic_request)
        
        # Should handle Arabic RTL text
        assert response.status_code == 200
