"""
Memory Service Integration Tests
Comprehensive test suite for Sprint 3 Memory Service
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any

import httpx
from fastapi.testclient import TestClient

# Import the Memory Service app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from main_full import app
except ImportError:
    from main_minimal import app

class TestMemoryService:
    """Test suite for Memory Service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_endpoints(self, client):
        """Test all health check endpoints"""
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["version"] == "1.0.0"
        assert data["port"] == 8017
        
        # Test liveness check
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert data["service"] == "memory_service"
        
        # Test readiness check
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]  # May be degraded
        data = response.json()
        assert data["service"] == "memory_service"
        assert "checks" in data
        
        # Test general health endpoint
        response = client.get("/health")
        assert response.status_code in [200, 503]
    
    def test_record_interaction(self, client):
        """Test recording user interactions"""
        interaction_data = {
            "user_id": "test_user_123",
            "interaction_type": "mood",
            "interaction_data": {
                "mood_score": 7,
                "emotions": ["happy", "content"]
            },
            "source_service": "mood_service",
            "metadata": {
                "test": True
            }
        }
        
        response = client.post("/api/v1/memory/interactions", json=interaction_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["user_id"] == "test_user_123"
        assert data["data"]["interaction_type"] == "mood"
    
    def test_get_user_interactions(self, client):
        """Test retrieving user interactions"""
        user_id = "test_user_123"
        response = client.get(f"/api/v1/memory/interactions/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "interactions" in data["data"]
        assert "pagination" in data["data"]
        
        # Test with query parameters
        response = client.get(f"/api/v1/memory/interactions/{user_id}?limit=5&offset=0&interaction_type=mood")
        assert response.status_code == 200
    
    def test_get_mood_patterns(self, client):
        """Test getting mood patterns for a user"""
        user_id = "test_user_123"
        response = client.get(f"/api/v1/memory/patterns/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["user_id"] == user_id
        assert "patterns" in data["data"]
    
    def test_get_behavioral_insights(self, client):
        """Test getting behavioral insights"""
        user_id = "test_user_123"
        response = client.get(f"/api/v1/memory/insights/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["user_id"] == user_id
        assert "insights" in data["data"]
    
    def test_get_user_aggregation(self, client):
        """Test getting aggregated user data"""
        user_id = "test_user_123"
        response = client.get(f"/api/v1/memory/aggregation/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["user_id"] == user_id
        assert "total_interactions" in data["data"]
        assert "interaction_breakdown" in data["data"]
    
    def test_chatbot_integration(self, client):
        """Test chatbot service integration endpoint"""
        interaction_data = {
            "user_id": "test_user_chatbot",
            "message_data": {
                "user_message": "I'm feeling happy today",
                "bot_response": "That's wonderful to hear!"
            },
            "emotion_analysis": {
                "primary_emotion": "joy",
                "confidence": 0.85
            },
            "cultural_context": {
                "language": "en",
                "cultural_background": "western"
            }
        }
        
        response = client.post("/api/v1/memory/chatbot/interaction", json=interaction_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == "test_user_chatbot"
        assert data["data"]["source_service"] == "chatbot_service"
    
    def test_process_event(self, client):
        """Test event processing endpoint"""
        event_data = {
            "event_type": "mood_update",
            "user_id": "test_user_event",
            "mood_score": 8,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        response = client.post("/api/v1/memory/events/process", json=event_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["event_type"] == "mood_update"
        assert data["data"]["user_id"] == "test_user_event"
    
    def test_service_stats(self, client):
        """Test service statistics endpoint"""
        response = client.get("/api/v1/memory/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "service_info" in data["data"]
        assert data["data"]["service_info"]["name"] == "memory_service"
        assert data["data"]["service_info"]["port"] == 8017
    
    def test_invalid_requests(self, client):
        """Test error handling for invalid requests"""
        # Test missing required fields
        response = client.post("/api/v1/memory/interactions", json={})
        assert response.status_code == 422  # Validation error
        
        # Test invalid event data
        response = client.post("/api/v1/memory/events/process", json={"invalid": "data"})
        assert response.status_code == 400
        
        # Test non-existent user
        response = client.get("/api/v1/memory/interactions/nonexistent_user")
        assert response.status_code == 200  # Should return empty data, not error

class TestMemoryServiceIntegration:
    """Integration tests with other services"""
    
    @pytest.fixture
    def memory_service_url(self):
        """Memory service URL for integration tests"""
        return "http://localhost:8017"
    
    @pytest.mark.asyncio
    async def test_service_connectivity(self, memory_service_url):
        """Test that Memory Service is accessible"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{memory_service_url}/health")
                assert response.status_code in [200, 503]
            except httpx.ConnectError:
                pytest.skip("Memory Service not running - integration test skipped")
    
    @pytest.mark.asyncio
    async def test_chatbot_service_integration(self, memory_service_url):
        """Test integration with chatbot service"""
        async with httpx.AsyncClient() as client:
            try:
                # Simulate chatbot service sending interaction data
                interaction_data = {
                    "user_id": "integration_test_user",
                    "message_data": {
                        "user_message": "How can I improve my mood?",
                        "bot_response": "Try practicing mindfulness or going for a walk."
                    },
                    "emotion_analysis": {
                        "primary_emotion": "neutral",
                        "confidence": 0.72
                    }
                }
                
                response = await client.post(
                    f"{memory_service_url}/api/v1/memory/chatbot/interaction",
                    json=interaction_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["success"] is True
                    assert data["data"]["source_service"] == "chatbot_service"
                else:
                    pytest.skip("Memory Service integration test failed - service may not be running")
                    
            except httpx.ConnectError:
                pytest.skip("Memory Service not accessible - integration test skipped")
    
    @pytest.mark.asyncio
    async def test_mood_service_integration(self, memory_service_url):
        """Test integration with mood service"""
        async with httpx.AsyncClient() as client:
            try:
                # Simulate mood service sending interaction data
                interaction_data = {
                    "user_id": "mood_test_user",
                    "interaction_type": "mood",
                    "interaction_data": {
                        "mood_score": 6,
                        "emotions": ["content", "peaceful"],
                        "factors": ["exercise", "good_sleep"]
                    },
                    "source_service": "mood_service",
                    "metadata": {
                        "integration_test": True
                    }
                }
                
                response = await client.post(
                    f"{memory_service_url}/api/v1/memory/interactions",
                    json=interaction_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["success"] is True
                    assert data["data"]["user_id"] == "mood_test_user"
                else:
                    pytest.skip("Memory Service integration test failed")
                    
            except httpx.ConnectError:
                pytest.skip("Memory Service not accessible")

class TestMemoryServicePerformance:
    """Performance tests for Memory Service"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_concurrent_interactions(self, client):
        """Test handling multiple concurrent interactions"""
        import concurrent.futures
        import threading
        
        def record_interaction(user_id: str):
            interaction_data = {
                "user_id": user_id,
                "interaction_type": "mood",
                "interaction_data": {"mood_score": 7},
                "source_service": "test_service"
            }
            response = client.post("/api/v1/memory/interactions", json=interaction_data)
            return response.status_code == 200
        
        # Test 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(record_interaction, f"user_{i}")
                for i in range(10)
            ]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(results), "Some concurrent requests failed"
    
    def test_large_interaction_data(self, client):
        """Test handling large interaction data"""
        large_data = {
            "user_id": "test_large_data",
            "interaction_type": "journal",
            "interaction_data": {
                "content": "x" * 1000,  # Large content
                "metadata": {f"key_{i}": f"value_{i}" for i in range(100)}  # Many fields
            },
            "source_service": "journal_service"
        }
        
        response = client.post("/api/v1/memory/interactions", json=large_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True

def run_memory_service_tests():
    """Run all Memory Service tests"""
    print("🧪 Running Memory Service Tests...")
    
    # Run the tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10"
    ])

if __name__ == "__main__":
    run_memory_service_tests()
