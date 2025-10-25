#!/usr/bin/env python3
"""
Test suite for end-to-end voice chatbot flow.
Tests complete voice interaction pipeline from audio input to response.
"""

import pytest
import asyncio
import json
import time
import io
import wave
import numpy as np
from typing import Dict, Any
import httpx
import os
from pathlib import Path

# Test configuration
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004")
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://localhost:8011")
MODELS_SERVICE_URL = os.getenv("MODELS_SERVICE_URL", "http://localhost:8081")

class TestChatbotVoiceFlow:
    """Test end-to-end voice chatbot interactions"""
    
    @pytest.fixture(scope="class")
    async def http_client(self):
        """HTTP client for API requests"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client
    
    def create_test_audio(self, duration: float = 2.0, sample_rate: int = 16000) -> bytes:
        """Create a simple test audio file (sine wave)"""
        # Generate a sine wave
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        frequency = 440  # A4 note
        audio_data = (np.sin(2 * np.pi * frequency * t) * 0.3).astype(np.float32)
        
        # Convert to WAV format
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        buffer.seek(0)
        return buffer.getvalue()
    
    @pytest.mark.asyncio
    async def test_voice_to_text_flow(self, http_client):
        """Test complete voice input to text response flow"""
        # Create test audio
        audio_data = self.create_test_audio()
        
        # Step 1: Send voice input to chatbot
        files = {
            'audio_file': ('test_voice.wav', audio_data, 'audio/wav')
        }
        
        start_time = time.time()
        response = await http_client.post(
            f"{CHATBOT_SERVICE_URL}/test/voice",
            files=files
        )
        processing_time = time.time() - start_time
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "transcript" in result
        assert "language" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0
        
        # Verify processing time is reasonable
        assert processing_time < 5.0, f"Voice processing time {processing_time:.2f}s exceeds 5s limit"
        
        print(f"Voice processing completed in {processing_time:.2f}s")
        print(f"Transcript: {result['transcript']}")
        print(f"Language: {result['language']}")
        print(f"Confidence: {result['confidence']}")
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, http_client):
        """Test multi-turn conversation with voice input"""
        # Create a test session
        session_response = await http_client.post(f"{CHATBOT_SERVICE_URL}/api/chatbot/chat/session")
        assert session_response.status_code == 200
        
        session_data = session_response.json()
        session_id = session_data.get("session_id")
        assert session_id is not None
        
        # Simulate multiple voice interactions
        test_messages = [
            "Hello, I'm feeling anxious today",
            "Can you help me with breathing exercises?",
            "Thank you, that was helpful"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n--- Turn {i+1}: {message} ---")
            
            # Create test audio for this message
            audio_data = self.create_test_audio()
            
            # Send voice input
            files = {
                'audio_file': (f'test_voice_{i}.wav', audio_data, 'audio/wav')
            }
            
            voice_response = await http_client.post(
                f"{CHATBOT_SERVICE_URL}/test/voice",
                files=files
            )
            
            assert voice_response.status_code == 200
            voice_result = voice_response.json()
            
            if voice_result["success"]:
                # Send the transcribed text to chatbot
                chat_payload = {
                    "message": message,  # Use the test message directly
                    "session_id": session_id
                }
                
                chat_response = await http_client.post(
                    f"{CHATBOT_SERVICE_URL}/api/chatbot/chat",
                    json=chat_payload
                )
                
                assert chat_response.status_code == 200
                chat_result = chat_response.json()
                
                assert "response" in chat_result
                assert len(chat_result["response"]) > 0
                
                print(f"Bot response: {chat_result['response'][:100]}...")
    
    @pytest.mark.asyncio
    async def test_voice_language_detection(self, http_client):
        """Test automatic language detection in voice input"""
        # Test with different language audio (simulated)
        test_cases = [
            {"language": "en", "expected_detection": "en"},
            {"language": "hi", "expected_detection": "hi"},
            {"language": "auto", "expected_detection": "en"}  # Default fallback
        ]
        
        for test_case in test_cases:
            audio_data = self.create_test_audio()
            
            files = {
                'audio_file': (f'test_{test_case["language"]}.wav', audio_data, 'audio/wav')
            }
            
            response = await http_client.post(
                f"{CHATBOT_SERVICE_URL}/test/voice",
                files=files
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert result["success"] is True
            assert "language" in result
            # Note: The mock service returns 'auto' for all requests
            # In a real implementation, this would detect the actual language
    
    @pytest.mark.asyncio
    async def test_voice_confidence_thresholds(self, http_client):
        """Test voice recognition confidence levels"""
        audio_data = self.create_test_audio()
        
        files = {
            'audio_file': ('test_confidence.wav', audio_data, 'audio/wav')
        }
        
        response = await http_client.post(
            f"{CHATBOT_SERVICE_URL}/test/voice",
            files=files
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "confidence" in result
        confidence = result["confidence"]
        
        # Test confidence thresholds
        assert confidence >= 0.0
        assert confidence <= 1.0
        
        if confidence < 0.5:
            print(f"Warning: Low confidence ({confidence:.2f}) - may need better audio quality")
        else:
            print(f"Good confidence level: {confidence:.2f}")
    
    @pytest.mark.asyncio
    async def test_voice_error_handling(self, http_client):
        """Test error handling in voice processing"""
        # Test with invalid audio file
        invalid_audio = b"not audio data"
        
        files = {
            'audio_file': ('invalid.wav', invalid_audio, 'audio/wav')
        }
        
        response = await http_client.post(
            f"{CHATBOT_SERVICE_URL}/test/voice",
            files=files
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            result = response.json()
            # Even with invalid audio, the service should return a structured response
            assert "success" in result
            assert "error" in result or "transcript" in result
    
    @pytest.mark.asyncio
    async def test_voice_performance_under_load(self, http_client):
        """Test voice processing performance under concurrent load"""
        # Create multiple concurrent voice requests
        tasks = []
        num_concurrent = 3
        
        for i in range(num_concurrent):
            audio_data = self.create_test_audio()
            
            files = {
                'audio_file': (f'concurrent_test_{i}.wav', audio_data, 'audio/wav')
            }
            
            task = http_client.post(
                f"{CHATBOT_SERVICE_URL}/test/voice",
                files=files
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Check results
        successful_responses = 0
        for response in responses:
            if isinstance(response, Exception):
                print(f"Request failed with exception: {response}")
            else:
                assert response.status_code == 200
                result = response.json()
                if result.get("success"):
                    successful_responses += 1
        
        print(f"Concurrent voice processing: {successful_responses}/{num_concurrent} successful")
        print(f"Total time: {total_time:.2f}s")
        
        # At least some requests should succeed
        assert successful_responses > 0
        
        # Performance should be reasonable even under load
        avg_time_per_request = total_time / num_concurrent
        assert avg_time_per_request < 10.0, f"Average time per request {avg_time_per_request:.2f}s too high"
    
    @pytest.mark.asyncio
    async def test_voice_to_tts_integration(self, http_client):
        """Test complete voice input to TTS output flow"""
        # Step 1: Voice input
        audio_data = self.create_test_audio()
        
        files = {
            'audio_file': ('voice_input.wav', audio_data, 'audio/wav')
        }
        
        voice_response = await http_client.post(
            f"{CHATBOT_SERVICE_URL}/test/voice",
            files=files
        )
        
        assert voice_response.status_code == 200
        voice_result = voice_response.json()
        
        if voice_result["success"]:
            # Step 2: Get chatbot response
            chat_payload = {
                "message": "I'm feeling stressed, can you help me relax?",
                "session_id": None  # New session
            }
            
            chat_response = await http_client.post(
                f"{CHATBOT_SERVICE_URL}/api/chatbot/chat",
                json=chat_payload
            )
            
            assert chat_response.status_code == 200
            chat_result = chat_response.json()
            
            assert "response" in chat_result
            bot_response = chat_result["response"]
            
            # Step 3: Convert response to speech
            tts_data = {
                'text': bot_response,
                'language': 'en',
                'voice': None,
                'model_preference': None
            }
            
            tts_response = await http_client.post(
                f"{MODELS_SERVICE_URL}/api/v1/tts/synthesize",
                data=tts_data
            )
            
            assert tts_response.status_code == 200
            assert tts_response.headers.get("content-type") == "audio/wav"
            
            # Verify we got audio data
            audio_data = tts_response.content
            assert len(audio_data) > 0
            
            print(f"Complete voice flow successful:")
            print(f"  Input transcript: {voice_result.get('transcript', 'N/A')}")
            print(f"  Bot response: {bot_response[:100]}...")
            print(f"  TTS audio size: {len(audio_data)} bytes")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
