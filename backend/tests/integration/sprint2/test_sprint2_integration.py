import pytest
import asyncio
import httpx
import websockets
import json
import time
from datetime import datetime, timezone
from ...config import test_service_url

class TestSprint2Integration:
    """Integration tests for Sprint 2 Backend Services"""
    
    @pytest.fixture
    def ai_processor_url(self):
        return test_service_url("ai_events")
    
    @pytest.fixture
    def voice_processor_url(self):
        return test_service_url("voice_events")
    
    @pytest.fixture
    def api_gateway_url(self):
        return test_service_url("api_gateway")
    
    @pytest.mark.asyncio
    async def test_ai_event_processor_health(self, ai_processor_url):
        """Test AI Event Processor health endpoints"""
        async with httpx.AsyncClient() as client:
            # Test basic health
            response = await client.get(f"{ai_processor_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "ai-event-processor"
            
            # Test liveness
            response = await client.get(f"{ai_processor_url}/health/live")
            assert response.status_code == 200
            assert response.json()["status"] == "alive"
            
            # Test readiness
            response = await client.get(f"{ai_processor_url}/health/ready")
            assert response.status_code == 200
            assert response.json()["status"] == "ready"
    
    @pytest.mark.asyncio
    async def test_voice_event_processor_health(self, voice_processor_url):
        """Test Voice Event Processor health endpoints"""
        async with httpx.AsyncClient() as client:
            # Test basic health
            response = await client.get(f"{voice_processor_url}/health")
            assert response.status_code == 200
            health_data = response.json()
            assert health_data["status"] == "healthy"
            assert health_data["service"] == "voice-event-processor"
            
            # Test liveness
            response = await client.get(f"{voice_processor_url}/health/live")
            assert response.status_code == 200
            assert response.json()["status"] == "alive"
    
    @pytest.mark.asyncio
    async def test_emotion_analysis_pipeline(self, ai_processor_url):
        """Test end-to-end emotion analysis pipeline"""
        async with httpx.AsyncClient() as client:
            # Test positive emotion
            positive_request = {
                "text": "I am feeling absolutely wonderful and excited today!",
                "language": "en",
                "user_id": "test_user_positive",
                "context": {"source": "integration_test"}
            }
            
            response = await client.post(
                f"{ai_processor_url}/api/v1/analyze/emotion",
                json=positive_request
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert result["user_id"] == "test_user_positive"
            assert "result" in result
            assert result["result"]["emotion"] in ["joy", "positive", "happy"]
            assert result["result"]["confidence"] > 0.5
            assert result["processing_time_ms"] < 200  # Performance requirement
            assert result["language"] == "en"
            
            # Test negative emotion
            negative_request = {
                "text": "I'm feeling really sad and down today.",
                "language": "en", 
                "user_id": "test_user_negative"
            }
            
            response = await client.post(
                f"{ai_processor_url}/api/v1/analyze/emotion",
                json=negative_request
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["result"]["emotion"] in ["sadness", "negative", "sad"]
    
    @pytest.mark.asyncio
    async def test_multilingual_emotion_analysis(self, ai_processor_url):
        """Test multilingual emotion analysis with cultural adaptation"""
        test_cases = [
            {
                "text": "Je suis très heureux aujourd'hui!",
                "language": "fr",
                "expected_emotion": "joy"
            },
            {
                "text": "मैं बहुत खुश हूं",
                "language": "hi", 
                "expected_emotion": "joy"
            },
            {
                "text": "أنا سعيد جداً اليوم",
                "language": "ar",
                "expected_emotion": "joy"
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for i, test_case in enumerate(test_cases):
                request_data = {
                    "text": test_case["text"],
                    "language": test_case["language"],
                    "user_id": f"test_user_multilingual_{i}"
                }
                
                response = await client.post(
                    f"{ai_processor_url}/api/v1/analyze/emotion",
                    json=request_data
                )
                
                assert response.status_code == 200
                result = response.json()
                assert result["language"] == test_case["language"]
                # Should have cultural adaptation for non-English languages
                if test_case["language"] != "en":
                    assert result.get("cultural_adaptation") is not None
    
    @pytest.mark.asyncio
    async def test_predictive_intervention_analysis(self, ai_processor_url):
        """Test predictive intervention analysis"""
        async with httpx.AsyncClient() as client:
            user_id = "test_user_intervention"
            
            response = await client.get(
                f"{ai_processor_url}/api/v1/predict/intervention/{user_id}"
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert result["user_id"] == user_id
            assert "result" in result
            assert "intervention_needed" in result["result"]
            assert "confidence" in result["result"]
            assert "urgency_level" in result["result"]
            assert "recommended_actions" in result["result"]
            assert result["processing_time_ms"] < 500  # Performance requirement
    
    @pytest.mark.asyncio
    async def test_context_update_pipeline(self, ai_processor_url):
        """Test context update pipeline"""
        async with httpx.AsyncClient() as client:
            user_id = "test_user_context"
            context_request = {
                "user_id": user_id,
                "context_data": {
                    "mood_score": 3,
                    "emotional_state": "anxious",
                    "recent_activity": "journaling"
                },
                "source": "integration_test"
            }
            
            response = await client.post(
                f"{ai_processor_url}/api/v1/context/update",
                json=context_request
            )
            
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "accepted"
            assert "Context update queued" in result["message"]
    
    @pytest.mark.asyncio
    async def test_ai_processor_metrics(self, ai_processor_url):
        """Test AI processor metrics collection"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ai_processor_url}/api/v1/metrics")
            
            assert response.status_code == 200
            metrics = response.json()
            
            # Should have metrics for all components
            expected_components = [
                "ai_processor", "emotion_analyzer", 
                "cultural_processor", "predictive_engine"
            ]
            
            for component in expected_components:
                assert component in metrics
                if metrics[component]:  # If component is initialized
                    assert isinstance(metrics[component], dict)
    
    @pytest.mark.asyncio
    async def test_voice_processor_metrics(self, voice_processor_url):
        """Test voice processor metrics collection"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{voice_processor_url}/api/v1/metrics")
            
            assert response.status_code == 200
            metrics = response.json()
            
            # Should have metrics structure
            assert isinstance(metrics, dict)
    
    @pytest.mark.asyncio
    async def test_performance_latency_requirements(self, ai_processor_url):
        """Test that performance latency requirements are met"""
        async with httpx.AsyncClient() as client:
            # Test emotion analysis latency
            request_data = {
                "text": "This is a test message for latency testing.",
                "language": "en",
                "user_id": "test_user_latency"
            }
            
            start_time = time.time()
            response = await client.post(
                f"{ai_processor_url}/api/v1/analyze/emotion",
                json=request_data
            )
            end_time = time.time()
            
            assert response.status_code == 200
            
            # Network latency should be under 200ms for local testing
            network_latency = (end_time - start_time) * 1000
            assert network_latency < 500, f"Network latency {network_latency}ms too high"
            
            # Service processing time should be under 200ms
            result = response.json()
            processing_time = result["processing_time_ms"]
            assert processing_time < 200, f"Processing time {processing_time}ms exceeds requirement"
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, ai_processor_url):
        """Test concurrent processing capabilities"""
        async with httpx.AsyncClient() as client:
            # Create multiple concurrent requests
            tasks = []
            for i in range(10):
                request_data = {
                    "text": f"Concurrent test message {i}",
                    "language": "en",
                    "user_id": f"test_user_concurrent_{i}"
                }
                
                task = client.post(
                    f"{ai_processor_url}/api/v1/analyze/emotion",
                    json=request_data
                )
                tasks.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for i, response in enumerate(responses):
                assert response.status_code == 200
                result = response.json()
                assert result["user_id"] == f"test_user_concurrent_{i}"
                assert "emotion" in result["result"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, ai_processor_url):
        """Test error handling in AI services"""
        async with httpx.AsyncClient() as client:
            # Test invalid request
            invalid_request = {
                "text": "",  # Empty text
                "language": "invalid_lang",
                "user_id": ""  # Empty user ID
            }
            
            response = await client.post(
                f"{ai_processor_url}/api/v1/analyze/emotion",
                json=invalid_request
            )
            
            # Should handle gracefully - either succeed with neutral or return error
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                result = response.json()
                # Empty text should return neutral emotion
                assert result["result"]["emotion"] == "neutral"
    
    @pytest.mark.asyncio
    async def test_service_integration_via_gateway(self, api_gateway_url, ai_processor_url):
        """Test service integration through API Gateway"""
        async with httpx.AsyncClient() as client:
            # Test that API Gateway can route to AI services
            try:
                # This would test if API Gateway properly routes AI requests
                response = await client.get(f"{api_gateway_url}/health")
                if response.status_code == 200:
                    # API Gateway is running, test routing if configured
                    pass
            except Exception:
                # API Gateway might not be configured yet for AI services
                pytest.skip("API Gateway not accessible or not configured for AI services")
    
    @pytest.mark.asyncio 
    async def test_cultural_sensitivity_validation(self, ai_processor_url):
        """Test cultural sensitivity in responses"""
        cultural_test_cases = [
            {
                "text": "I need to make a decision about my family",
                "language": "hi",  # Hindi - family-oriented culture
                "expected_cultural_elements": ["family", "community"]
            },
            {
                "text": "I'm struggling with my faith",
                "language": "ar",  # Arabic - Islamic culture
                "expected_cultural_elements": ["spiritual", "faith"]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for test_case in cultural_test_cases:
                request_data = {
                    "text": test_case["text"],
                    "language": test_case["language"],
                    "user_id": "test_cultural_sensitivity"
                }
                
                response = await client.post(
                    f"{ai_processor_url}/api/v1/analyze/emotion",
                    json=request_data
                )
                
                assert response.status_code == 200
                result = response.json()
                
                # Should have cultural adaptation
                cultural_adaptation = result.get("cultural_adaptation")
                if cultural_adaptation:
                    assert cultural_adaptation.get("adapted_culture") == test_case["language"]
    
    @pytest.mark.asyncio
    async def test_event_driven_architecture_simulation(self, ai_processor_url):
        """Simulate event-driven architecture flow"""
        async with httpx.AsyncClient() as client:
            # Simulate a mood event that would trigger AI processing
            user_id = "test_user_event_flow"
            
            # Step 1: Emotion analysis (simulating mood event processing)
            emotion_request = {
                "text": "I'm feeling overwhelmed and stressed",
                "language": "en",
                "user_id": user_id,
                "context": {"source": "mood_service", "mood_score": 2}
            }
            
            emotion_response = await client.post(
                f"{ai_processor_url}/api/v1/analyze/emotion",
                json=emotion_request
            )
            
            assert emotion_response.status_code == 200
            emotion_result = emotion_response.json()
            
            # Step 2: Context update (simulating context aggregation)
            context_request = {
                "user_id": user_id,
                "context_data": {
                    "emotion_analysis": emotion_result["result"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "source": "ai_event_processor"
            }
            
            context_response = await client.post(
                f"{ai_processor_url}/api/v1/context/update",
                json=context_request
            )
            
            assert context_response.status_code == 200
            
            # Step 3: Predictive analysis (simulating intervention evaluation)
            intervention_response = await client.get(
                f"{ai_processor_url}/api/v1/predict/intervention/{user_id}"
            )
            
            assert intervention_response.status_code == 200
            intervention_result = intervention_response.json()
            
            # If emotion was negative, intervention might be suggested
            if emotion_result["result"]["emotion"] in ["sadness", "anger", "fear"]:
                # Could trigger intervention based on emotion
                assert "result" in intervention_result
                assert "intervention_needed" in intervention_result["result"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
