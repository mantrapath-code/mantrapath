"""
Integration tests for Voice Service
Tests end-to-end functionality with real scenarios
"""
import pytest
import asyncio
import aiohttp
from unittest.mock import patch, AsyncMock
from tests.fixtures.test_data import (
    INDIAN_LANGUAGE_TEST_DATA, 
    CODE_SWITCHING_TEST_DATA,
    CONVERSATION_SCENARIOS,
    PERFORMANCE_BENCHMARKS
)

class TestVoiceServiceIntegration:
    
    @pytest.fixture
    def base_url(self):
        """Base URL for voice service"""
        return "http://localhost:8010"
    
    @pytest.fixture
    async def client_session(self):
        """HTTP client session for testing"""
        async with aiohttp.ClientSession() as session:
            yield session
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, client_session, base_url):
        """Test health check endpoint"""
        try:
            async with client_session.get(f"{base_url}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] in ["healthy", "degraded"]
                assert "components" in data
                assert "voice_service" in data["components"]
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_create_session_endpoint(self, client_session, base_url):
        """Test session creation endpoint"""
        session_data = {
            "user_id": "test_user_integration",
            "language": "hi",
            "preferences": {
                "voice_speed": "normal",
                "voice_gender": "female"
            }
        }
        
        try:
            async with client_session.post(
                f"{base_url}/api/sessions",
                json=session_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert "session_id" in data["data"]
                return data["data"]["session_id"]
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_conversation_flow_hindi(self, client_session, base_url):
        """Test complete conversation flow in Hindi"""
        # Create session first
        session_data = {
            "user_id": "test_hindi_conversation",
            "language": "hi",
            "preferences": {"voice_speed": "normal"}
        }
        
        try:
            # Create session
            async with client_session.post(
                f"{base_url}/api/sessions",
                json=session_data
            ) as response:
                session_response = await response.json()
                session_id = session_response["data"]["session_id"]
            
            # Test conversation
            conversation_data = {
                "text": "नमस्ते, मुझे आपकी मदद चाहिए",
                "session_id": session_id,
                "language": "hi",
                "voice_response": True
            }
            
            async with client_session.post(
                f"{base_url}/api/conversation",
                json=conversation_data
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                assert "bot_response" in data["data"]
                assert "audio_response" in data["data"]
                assert data["data"]["language_info"]["detected_language"] == "hi"
                
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_all_indian_languages_support(self, client_session, base_url):
        """Test support for all Indian languages"""
        try:
            for lang_name, lang_data in INDIAN_LANGUAGE_TEST_DATA.items():
                # Create session for each language
                session_data = {
                    "user_id": f"test_{lang_name}_user",
                    "language": lang_data["language_code"],
                    "preferences": {"voice_speed": "normal"}
                }
                
                async with client_session.post(
                    f"{base_url}/api/sessions",
                    json=session_data
                ) as response:
                    session_response = await response.json()
                    session_id = session_response["data"]["session_id"]
                
                # Test conversation in that language
                conversation_data = {
                    "text": lang_data["text"],
                    "session_id": session_id,
                    "language": lang_data["language_code"],
                    "voice_response": True
                }
                
                async with client_session.post(
                    f"{base_url}/api/conversation",
                    json=conversation_data
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["success"] is True
                    
                    # Check language detection
                    detected_lang = data["data"]["language_info"]["detected_language"]
                    assert detected_lang == lang_data["language_code"]
                    
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_code_switching_scenarios(self, client_session, base_url):
        """Test code-switching scenarios (Hindi-English)"""
        try:
            # Create session
            session_data = {
                "user_id": "test_code_switching",
                "language": "auto",
                "preferences": {"handle_code_switching": True}
            }
            
            async with client_session.post(
                f"{base_url}/api/sessions",
                json=session_data
            ) as response:
                session_response = await response.json()
                session_id = session_response["data"]["session_id"]
            
            # Test each code-switching example
            for example in CODE_SWITCHING_TEST_DATA:
                conversation_data = {
                    "text": example["text"],
                    "session_id": session_id,
                    "language": "auto",
                    "voice_response": True
                }
                
                async with client_session.post(
                    f"{base_url}/api/conversation",
                    json=conversation_data
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["success"] is True
                    
                    # Check mixed language detection
                    lang_info = data["data"]["language_info"]
                    if "is_mixed" in lang_info:
                        assert lang_info["is_mixed"] is True
                        
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation_medical(self, client_session, base_url):
        """Test multi-turn medical consultation scenario"""
        medical_scenario = None
        for scenario in CONVERSATION_SCENARIOS:
            if scenario["name"] == "medical_consultation":
                medical_scenario = scenario
                break
        
        if not medical_scenario:
            pytest.skip("Medical scenario not found")
        
        try:
            # Create session with medical context
            session_data = {
                "user_id": "test_medical_patient",
                "language": medical_scenario["language"],
                "preferences": {
                    "context": "medical",
                    "tone": "professional"
                }
            }
            
            async with client_session.post(
                f"{base_url}/api/sessions",
                json=session_data
            ) as response:
                session_response = await response.json()
                session_id = session_response["data"]["session_id"]
            
            # Process each turn in the medical conversation
            for i, turn in enumerate(medical_scenario["turns"]):
                conversation_data = {
                    "text": turn["user"],
                    "session_id": session_id,
                    "language": medical_scenario["language"],
                    "context": {"domain": "medical", "turn": i + 1},
                    "voice_response": True
                }
                
                async with client_session.post(
                    f"{base_url}/api/conversation",
                    json=conversation_data
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["success"] is True
                    assert data["data"]["conversation_turn"] == i + 1
                    
                    # Check context awareness
                    if i > 0:
                        context_used = data["data"].get("context_used", {})
                        assert "domain" in context_used
                        assert context_used["domain"] == "medical"
                        
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_voice_tts_endpoints(self, client_session, base_url):
        """Test TTS (Text-to-Speech) endpoints"""
        try:
            tts_requests = [
                {
                    "text": "नमस्ते, आप कैसे हैं?",
                    "language": "hi",
                    "voice": "female",
                    "enhance_output": True
                },
                {
                    "text": "Hello, how are you?",
                    "language": "en",
                    "voice": "male",
                    "enhance_output": False
                }
            ]
            
            for tts_request in tts_requests:
                async with client_session.post(
                    f"{base_url}/api/tts/synthesize",
                    json=tts_request
                ) as response:
                    assert response.status == 200
                    data = await response.json()
                    assert data["success"] is True
                    assert "audio_url" in data["data"]
                    assert "duration" in data["data"]
                    assert data["data"]["model_used"] is not None
                    
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, client_session, base_url):
        """Test performance against benchmarks"""
        try:
            # Create session
            session_data = {
                "user_id": "performance_test",
                "language": "hi",
                "preferences": {"performance_mode": True}
            }
            
            async with client_session.post(
                f"{base_url}/api/sessions",
                json=session_data
            ) as response:
                session_response = await response.json()
                session_id = session_response["data"]["session_id"]
            
            # Test conversation response time
            import time
            start_time = time.time()
            
            conversation_data = {
                "text": "नमस्ते, मुझे मदद चाहिए",
                "session_id": session_id,
                "language": "hi",
                "voice_response": True
            }
            
            async with client_session.post(
                f"{base_url}/api/conversation",
                json=conversation_data
            ) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                
                # Check against performance benchmarks
                max_response_time = PERFORMANCE_BENCHMARKS["conversation_response"]["max_ms"]
                target_response_time = PERFORMANCE_BENCHMARKS["conversation_response"]["target_ms"]
                
                assert response_time_ms < max_response_time
                
                # Log if slower than target
                if response_time_ms > target_response_time:
                    print(f"Warning: Response time {response_time_ms}ms exceeds target {target_response_time}ms")
                    
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, client_session, base_url):
        """Test error handling in integration scenarios"""
        try:
            error_test_cases = [
                {
                    "name": "empty_text",
                    "data": {"text": "", "language": "hi"},
                    "expected_status": 400
                },
                {
                    "name": "invalid_language",
                    "data": {"text": "test", "language": "xyz"},
                    "expected_status": 400
                },
                {
                    "name": "missing_session",
                    "data": {"text": "test", "session_id": "nonexistent"},
                    "expected_status": 404
                }
            ]
            
            for test_case in error_test_cases:
                async with client_session.post(
                    f"{base_url}/api/conversation",
                    json=test_case["data"]
                ) as response:
                    # Should handle errors gracefully
                    assert response.status in [200, test_case["expected_status"]]
                    
                    if response.status == 200:
                        data = await response.json()
                        # Should indicate error in response
                        assert data.get("success") is False or "error" in data
                        
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, client_session, base_url):
        """Test handling multiple concurrent sessions"""
        try:
            # Create multiple sessions concurrently
            tasks = []
            for i in range(5):
                session_data = {
                    "user_id": f"concurrent_user_{i}",
                    "language": "hi",
                    "preferences": {"session_id": i}
                }
                
                task = client_session.post(
                    f"{base_url}/api/sessions",
                    json=session_data
                )
                tasks.append(task)
            
            # Wait for all sessions to be created
            responses = []
            for task in tasks:
                async with task as response:
                    data = await response.json()
                    responses.append(data)
            
            # All sessions should be created successfully
            assert len(responses) == 5
            for response in responses:
                assert response["success"] is True
                assert "session_id" in response["data"]
            
            # Test concurrent conversations
            conversation_tasks = []
            for i, response in enumerate(responses):
                session_id = response["data"]["session_id"]
                conversation_data = {
                    "text": f"नमस्ते {i}",
                    "session_id": session_id,
                    "language": "hi"
                }
                
                task = client_session.post(
                    f"{base_url}/api/conversation",
                    json=conversation_data
                )
                conversation_tasks.append(task)
            
            # Process concurrent conversations
            conversation_responses = []
            for task in conversation_tasks:
                async with task as response:
                    data = await response.json()
                    conversation_responses.append(data)
            
            # All conversations should succeed
            assert len(conversation_responses) == 5
            for response in conversation_responses:
                assert response["success"] is True
                
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_websocket_conversation(self, base_url):
        """Test WebSocket-based real-time conversation"""
        import websockets
        
        try:
            websocket_url = base_url.replace("http://", "ws://") + "/ws/conversation"
            
            async with websockets.connect(websocket_url) as websocket:
                # Send session creation
                session_message = {
                    "type": "create_session",
                    "data": {
                        "user_id": "websocket_test",
                        "language": "hi"
                    }
                }
                await websocket.send(json.dumps(session_message))
                
                # Receive session confirmation
                response = await websocket.recv()
                session_data = json.loads(response)
                assert session_data["type"] == "session_created"
                session_id = session_data["data"]["session_id"]
                
                # Send conversation message
                conversation_message = {
                    "type": "conversation",
                    "data": {
                        "text": "नमस्ते",
                        "session_id": session_id,
                        "language": "hi"
                    }
                }
                await websocket.send(json.dumps(conversation_message))
                
                # Receive conversation response
                response = await websocket.recv()
                conversation_data = json.loads(response)
                assert conversation_data["type"] == "conversation_response"
                assert conversation_data["data"]["success"] is True
                
        except (ImportError, ConnectionError):
            pytest.skip("WebSocket support not available or service not running")
    
    @pytest.mark.asyncio
    async def test_analytics_endpoints(self, client_session, base_url):
        """Test analytics and monitoring endpoints"""
        try:
            # Test metrics endpoint
            async with client_session.get(f"{base_url}/api/analytics/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    assert "total_sessions" in data
                    assert "total_conversations" in data
                    assert "language_distribution" in data
                
            # Test performance metrics
            async with client_session.get(f"{base_url}/api/analytics/performance") as response:
                if response.status == 200:
                    data = await response.json()
                    assert "average_response_time" in data
                    assert "cache_hit_rate" in data
                    
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, client_session, base_url):
        """Test audio caching functionality"""
        try:
            # First TTS request
            tts_request = {
                "text": "नमस्ते, यह एक टेस्ट है",
                "language": "hi",
                "cache_audio": True
            }
            
            import time
            
            # First request (should generate audio)
            start_time = time.time()
            async with client_session.post(
                f"{base_url}/api/tts/synthesize",
                json=tts_request
            ) as response:
                first_response_time = time.time() - start_time
                data1 = await response.json()
                assert data1["success"] is True
                assert data1["data"]["cached"] is False
                cache_key = data1["data"].get("cache_key")
            
            # Second request (should use cache)
            start_time = time.time()
            async with client_session.post(
                f"{base_url}/api/tts/synthesize",
                json=tts_request
            ) as response:
                second_response_time = time.time() - start_time
                data2 = await response.json()
                assert data2["success"] is True
                
                # Should be faster and marked as cached
                if "cached" in data2["data"]:
                    assert data2["data"]["cached"] is True
                    assert second_response_time < first_response_time
                
        except aiohttp.ClientConnectionError:
            pytest.skip("Voice service not running")
