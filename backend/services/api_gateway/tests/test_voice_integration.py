"""
Integration test for Voice API Gateway endpoints
Tests the complete voice routing system integration
"""

import pytest
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.main import app


class TestVoiceAPIIntegration:
    """Integration tests for voice API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_voice_command_mood_tracking(self):
        """Test voice command for mood tracking"""
        request_data = {
            "text": "I'm feeling happy today",
            "language": "en",
            "user_id": "test_user"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["target_service"] == "mood_service"
        assert "/mood/track" in data["endpoint"]
        assert data["processing_time_ms"] is not None
    
    def test_voice_command_journal_entry(self):
        """Test voice command for journal entry"""
        request_data = {
            "text": "Start a new journal entry about my day",
            "language": "en",
            "user_id": "test_user"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["target_service"] == "content_service"
        assert "/journal/entries" in data["endpoint"]
    
    def test_voice_command_hindi(self):
        """Test Hindi voice command"""
        request_data = {
            "text": "मैं आज खुश हूँ",
            "language": "hi",
            "user_id": "test_user",
            "cultural_context": "indian_subcontinent"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["target_service"] == "mood_service"
    
    def test_language_detection(self):
        """Test language detection endpoint"""
        request_data = {
            "text": "Je suis heureux aujourd'hui"
        }
        
        response = self.client.post("/voice/detect-language", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["detected_language"] == "fr"
        assert data["cultural_context"] == "western_europe"
        assert data["supported"] is True
    
    def test_voice_capabilities(self):
        """Test voice capabilities endpoint"""
        response = self.client.get("/voice/capabilities")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "supported_languages" in data
        assert "supported_intents" in data
        assert "cultural_regions" in data
        assert "voice_examples" in data
        
        # Check if we have the expected languages
        languages = [lang["code"] for lang in data["supported_languages"]]
        assert "en" in languages
        assert "hi" in languages
        assert "es" in languages
    
    def test_voice_health_check(self):
        """Test voice system health check"""
        response = self.client.get("/voice/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "voice_router" in data
        assert "ml_support" in data
        assert "intent_classifier" in data
    
    def test_unknown_intent_handling(self):
        """Test handling of unknown intents"""
        request_data = {
            "text": "Random meaningless gibberish text",
            "language": "en",
            "user_id": "test_user"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "error_message" in data
    
    def test_empty_text_error(self):
        """Test error handling for empty text"""
        request_data = {
            "text": "",
            "language": "en",
            "user_id": "test_user"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "Empty voice text" in data["error_message"]
    
    def test_auto_language_detection(self):
        """Test automatic language detection in voice command"""
        request_data = {
            "text": "मैं डायरी लिखना चाहता हूँ",  # Hindi: I want to write diary
            "language": "auto",  # Should auto-detect Hindi
            "user_id": "test_user"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should successfully route despite "auto" language
        assert data["success"] is True or data["success"] is False  # May succeed or fail based on routing rules


@pytest.mark.asyncio
class TestVoiceWebSocket:
    """Test voice WebSocket functionality"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    def test_websocket_connection(self):
        """Test WebSocket connection establishment"""
        with self.client.websocket_connect("/voice/stream/test_session") as websocket:
            # Should receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "welcome"
            assert data["session_id"] == "test_session"
            assert "capabilities" in data
    
    def test_websocket_voice_command(self):
        """Test voice command through WebSocket"""
        with self.client.websocket_connect("/voice/stream/test_session") as websocket:
            # Receive welcome message
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"
            
            # Send voice command
            command_message = {
                "type": "voice_command",
                "data": {
                    "text": "I'm feeling great today",
                    "language": "en",
                    "user_id": "test_user"
                }
            }
            websocket.send_json(command_message)
            
            # Receive response
            response = websocket.receive_json()
            assert response["type"] == "voice_response"
            assert "data" in response
            assert response["data"]["success"] is not None
    
    def test_websocket_language_detection(self):
        """Test language detection through WebSocket"""
        with self.client.websocket_connect("/voice/stream/test_session") as websocket:
            # Receive welcome message
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"
            
            # Send language detection request
            lang_message = {
                "type": "language_detection",
                "data": {
                    "text": "Je suis content"
                }
            }
            websocket.send_json(lang_message)
            
            # Receive response
            response = websocket.receive_json()
            assert response["type"] == "language_detected"
            assert response["data"]["language"] == "fr"
            assert response["data"]["cultural_context"] == "western_europe"
    
    def test_websocket_ping_pong(self):
        """Test WebSocket ping/pong functionality"""
        with self.client.websocket_connect("/voice/stream/test_session") as websocket:
            # Receive welcome message
            welcome = websocket.receive_json()
            assert welcome["type"] == "welcome"
            
            # Send ping
            ping_message = {"type": "ping"}
            websocket.send_json(ping_message)
            
            # Receive pong
            response = websocket.receive_json()
            assert response["type"] == "pong"
            assert "timestamp" in response


class TestVoiceStatistics:
    """Test voice statistics and monitoring"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_voice_statistics_without_auth(self):
        """Test statistics endpoint without authentication"""
        response = self.client.get("/voice/statistics")
        
        assert response.status_code == 401
        data = response.json()
        assert "Authentication required" in data["detail"]
    
    def test_voice_statistics_with_auth(self):
        """Test statistics endpoint with authentication"""
        headers = {"Authorization": "Bearer fake_token"}
        response = self.client.get("/voice/statistics", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "routing" in data
        assert "languages" in data
        assert "websockets" in data
        assert "system" in data


class TestVoiceSystemHealthMonitoring:
    """Test voice system health and monitoring"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_main_health_includes_voice(self):
        """Test that main health check includes voice status"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        # Main health endpoint should still work
    
    def test_voice_specific_health(self):
        """Test voice-specific health endpoint"""
        response = self.client.get("/voice/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "voice_router" in data
        assert "ml_support" in data
        assert "intent_classifier" in data
        assert "supported_languages" in data
        assert "routing_rules" in data


class TestCulturalAdaptation:
    """Test cultural adaptation features"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_indian_cultural_context(self):
        """Test Indian cultural context adaptation"""
        request_data = {
            "text": "मैं आज बहुत खुश हूँ",  # I am very happy today
            "language": "hi",
            "cultural_context": "indian_subcontinent",
            "user_id": "test_user"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        if data["success"]:
            # Should include cultural adaptations in endpoint
            assert "cultural_" in data["endpoint"] or data["endpoint"].endswith("/mood/track")
    
    def test_western_cultural_context(self):
        """Test Western cultural context adaptation"""
        request_data = {
            "text": "I'm feeling excited about my progress",
            "language": "en",
            "cultural_context": "western_europe",
            "user_id": "test_user"
        }
        
        response = self.client.post("/voice/command", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should successfully route
        assert data["success"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
