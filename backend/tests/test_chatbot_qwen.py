#!/usr/bin/env python3
"""
Test suite for Qwen2.5-1.5B-Instruct integration in the chatbot service.
Tests model loading, response generation, and performance.
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any
import httpx
import os
from pathlib import Path

# Test configuration
BASE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004")
MODELS_SERVICE_URL = os.getenv("MODELS_SERVICE_URL", "http://localhost:8081")

class TestQwenIntegration:
    """Test Qwen2.5-1.5B-Instruct integration"""
    
    @pytest.fixture(scope="class")
    async def http_client(self):
        """HTTP client for API requests"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_models_service_health(self, http_client):
        """Test that models service is healthy and reports Qwen model"""
        response = await http_client.get(f"{MODELS_SERVICE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "qwen" in data.get("model", "").lower()
        assert "text-generation" in data.get("features", [])
    
    @pytest.mark.asyncio
    async def test_qwen_text_generation(self, http_client):
        """Test Qwen model text generation"""
        test_payload = {
            "text": "Hello, how are you feeling today?",
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/nlp/generate",
            json=test_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "response" in data
        assert len(data["response"]) > 0
        assert data.get("model_used", "").lower().find("qwen") != -1
        assert data.get("confidence", 0) > 0.5
    
    @pytest.mark.asyncio
    async def test_chatbot_service_health(self, http_client):
        """Test chatbot service health"""
        response = await http_client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "chatbot" in data.get("service", "").lower()
    
    @pytest.mark.asyncio
    async def test_chatbot_text_chat(self, http_client):
        """Test basic text chat functionality"""
        # Create a test session
        session_response = await http_client.post(f"{BASE_URL}/api/chatbot/chat/session")
        assert session_response.status_code == 200
        
        session_data = session_response.json()
        session_id = session_data.get("session_id")
        assert session_id is not None
        
        # Send a test message
        chat_payload = {
            "message": "Hello, I'm feeling anxious today. Can you help me?",
            "session_id": session_id
        }
        
        response = await http_client.post(
            f"{BASE_URL}/api/chatbot/chat",
            json=chat_payload
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert len(data["response"]) > 0
        assert data.get("success", False) is True
    
    @pytest.mark.asyncio
    async def test_voice_endpoint_availability(self, http_client):
        """Test that voice endpoints are available"""
        # Test the voice test endpoint
        response = await http_client.get(f"{BASE_URL}/test/simple")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "ok"
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, http_client):
        """Test that response times meet requirements (< 3 seconds for text)"""
        start_time = time.time()
        
        test_payload = {
            "text": "I need help with my anxiety. What should I do?",
            "max_tokens": 150,
            "temperature": 0.8
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/nlp/generate",
            json=test_payload
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0, f"Response time {response_time:.2f}s exceeds 3s limit"
        
        data = response.json()
        assert data["success"] is True
        assert len(data.get("response", "")) > 10  # Ensure meaningful response
    
    @pytest.mark.asyncio
    async def test_multiple_languages(self, http_client):
        """Test Qwen model with different language prompts"""
        test_cases = [
            {
                "text": "Hello, how are you?",
                "expected_language": "en"
            },
            {
                "text": "नमस्ते, आप कैसे हैं?",
                "expected_language": "hi"
            },
            {
                "text": "Bonjour, comment allez-vous?",
                "expected_language": "fr"
            }
        ]
        
        for test_case in test_cases:
            payload = {
                "text": test_case["text"],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            response = await http_client.post(
                f"{MODELS_SERVICE_URL}/api/v1/nlp/generate",
                json=payload
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data.get("response", "")) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, http_client):
        """Test error handling for invalid requests"""
        # Test with empty text
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/nlp/generate",
            json={"text": "", "max_tokens": 50}
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
        
        # Test with very long text
        long_text = "This is a very long text. " * 1000
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/nlp/generate",
            json={"text": long_text, "max_tokens": 50}
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 413]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

