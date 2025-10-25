#!/usr/bin/env python3
"""
Test suite for voice service integration (STT/TTS pipeline).
Tests speech-to-text and text-to-speech functionality.
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
VOICE_SERVICE_URL = os.getenv("VOICE_SERVICE_URL", "http://localhost:8011")
MODELS_SERVICE_URL = os.getenv("MODELS_SERVICE_URL", "http://localhost:8081")
CHATBOT_SERVICE_URL = os.getenv("CHATBOT_SERVICE_URL", "http://localhost:8004")

class TestVoiceIntegration:
    """Test voice service STT/TTS integration"""
    
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
    async def test_voice_service_health(self, http_client):
        """Test voice service health"""
        response = await http_client.get(f"{VOICE_SERVICE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "voice" in data.get("service", "").lower()
    
    @pytest.mark.asyncio
    async def test_models_service_stt_languages(self, http_client):
        """Test STT supported languages from models service"""
        response = await http_client.get(f"{MODELS_SERVICE_URL}/api/v1/stt/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "languages" in data
        assert len(data["languages"]) > 0
        
        # Check for expected languages
        languages = data["languages"]
        expected_languages = ["en", "hi", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa", "or", "as", "ur"]
        for lang in expected_languages:
            assert lang in languages, f"Language {lang} not found in supported languages"
    
    @pytest.mark.asyncio
    async def test_models_service_tts_languages(self, http_client):
        """Test TTS supported languages from models service"""
        response = await http_client.get(f"{MODELS_SERVICE_URL}/api/v1/tts/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "languages" in data
        assert len(data["languages"]) > 0
        
        # Check for expected languages
        languages = data["languages"]
        expected_languages = ["en", "hi", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa", "or", "as", "ur"]
        for lang in expected_languages:
            assert lang in languages, f"Language {lang} not found in supported languages"
    
    @pytest.mark.asyncio
    async def test_stt_transcription(self, http_client):
        """Test speech-to-text transcription"""
        # Create test audio
        audio_data = self.create_test_audio()
        
        # Test STT endpoint
        files = {
            'audio': ('test_audio.wav', audio_data, 'audio/wav')
        }
        data = {
            'language': 'en',
            'model_preference': None
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/stt/transcribe",
            files=files,
            data=data
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "text" in result
        assert "language" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_tts_synthesis(self, http_client):
        """Test text-to-speech synthesis"""
        test_text = "Hello, this is a test message."
        
        data = {
            'text': test_text,
            'language': 'en',
            'voice': None,
            'model_preference': None
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/tts/synthesize",
            data=data
        )
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "audio/wav"
        
        # Check that we got audio data
        audio_data = response.content
        assert len(audio_data) > 0
        
        # Check headers for metadata
        assert "X-Sample-Rate" in response.headers
        assert "X-Duration" in response.headers
        assert "X-Model-Used" in response.headers
    
    @pytest.mark.asyncio
    async def test_multilingual_stt(self, http_client):
        """Test STT with different languages"""
        test_cases = [
            {"language": "en", "expected_text": "Hello"},
            {"language": "hi", "expected_text": "नमस्ते"},
            {"language": "bn", "expected_text": "হ্যালো"}
        ]
        
        for test_case in test_cases:
            # Create test audio
            audio_data = self.create_test_audio()
            
            files = {
                'audio': ('test_audio.wav', audio_data, 'audio/wav')
            }
            data = {
                'language': test_case["language"],
                'model_preference': None
            }
            
            response = await http_client.post(
                f"{MODELS_SERVICE_URL}/api/v1/stt/transcribe",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert result["success"] is True
            assert result["language"] == test_case["language"]
            assert "text" in result
    
    @pytest.mark.asyncio
    async def test_multilingual_tts(self, http_client):
        """Test TTS with different languages"""
        test_cases = [
            {"language": "en", "text": "Hello, how are you?"},
            {"language": "hi", "text": "नमस्ते, आप कैसे हैं?"},
            {"language": "bn", "text": "হ্যালো, আপনি কেমন আছেন?"}
        ]
        
        for test_case in test_cases:
            data = {
                'text': test_case["text"],
                'language': test_case["language"],
                'voice': None,
                'model_preference': None
            }
            
            response = await http_client.post(
                f"{MODELS_SERVICE_URL}/api/v1/tts/synthesize",
                data=data
            )
            
            assert response.status_code == 200
            assert response.headers.get("content-type") == "audio/wav"
            
            # Check that we got audio data
            audio_data = response.content
            assert len(audio_data) > 0
    
    @pytest.mark.asyncio
    async def test_voice_performance(self, http_client):
        """Test voice processing performance (< 5 seconds for voice)"""
        # Test STT performance
        audio_data = self.create_test_audio()
        
        start_time = time.time()
        
        files = {
            'audio': ('test_audio.wav', audio_data, 'audio/wav')
        }
        data = {
            'language': 'en',
            'model_preference': None
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/stt/transcribe",
            files=files,
            data=data
        )
        
        stt_time = time.time() - start_time
        
        assert response.status_code == 200
        assert stt_time < 5.0, f"STT processing time {stt_time:.2f}s exceeds 5s limit"
        
        # Test TTS performance
        start_time = time.time()
        
        tts_data = {
            'text': "This is a test message for performance testing.",
            'language': 'en',
            'voice': None,
            'model_preference': None
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/tts/synthesize",
            data=tts_data
        )
        
        tts_time = time.time() - start_time
        
        assert response.status_code == 200
        assert tts_time < 5.0, f"TTS processing time {tts_time:.2f}s exceeds 5s limit"
    
    @pytest.mark.asyncio
    async def test_chatbot_voice_integration(self, http_client):
        """Test chatbot voice endpoint integration"""
        # Create test audio
        audio_data = self.create_test_audio()
        
        files = {
            'audio_file': ('test_voice.wav', audio_data, 'audio/wav')
        }
        
        response = await http_client.post(
            f"{CHATBOT_SERVICE_URL}/test/voice",
            files=files
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert "transcript" in result
        assert "language" in result
        assert "confidence" in result
        assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, http_client):
        """Test error handling for invalid voice requests"""
        # Test with invalid audio file
        invalid_audio = b"not audio data"
        
        files = {
            'audio': ('invalid.wav', invalid_audio, 'audio/wav')
        }
        data = {
            'language': 'en',
            'model_preference': None
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/stt/transcribe",
            files=files,
            data=data
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]
        
        # Test with empty text for TTS
        tts_data = {
            'text': '',
            'language': 'en',
            'voice': None,
            'model_preference': None
        }
        
        response = await http_client.post(
            f"{MODELS_SERVICE_URL}/api/v1/tts/synthesize",
            data=tts_data
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
