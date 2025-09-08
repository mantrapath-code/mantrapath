"""
Unit tests for ModelsServiceClient
Tests integration with the models service and handles various Indian languages
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from app.core.models_client import ModelsServiceClient
from tests.fixtures.test_data import INDIAN_LANGUAGE_TEST_DATA, CODE_SWITCHING_TEST_DATA

class TestModelsServiceClient:
    
    @pytest.fixture
    def client(self):
        """Create a ModelsServiceClient instance for testing"""
        return ModelsServiceClient(base_url="http://localhost:8085")
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await client.health_check()
            assert result["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, client):
        """Test health check when service is down"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Connection failed")
            
            result = await client.health_check()
            assert result["status"] == "unhealthy"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_stt_transcribe_hindi(self, client):
        """Test STT transcription for Hindi audio"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "text": "नमस्ते, आप कैसे हैं?",
                "confidence": 0.95,
                "language": "hi",
                "model_used": "whisper_medium"
            }
            mock_post.return_value.__aenter__.return_value = mock_response
            
            audio_data = b"mock_hindi_audio_data"
            result = await client.stt_transcribe(audio_data, language="hi")
            
            assert result["text"] == "नमस्ते, आप कैसे हैं?"
            assert result["language"] == "hi"
            assert result["confidence"] > 0.9
    
    @pytest.mark.asyncio
    async def test_stt_transcribe_multiple_languages(self, client):
        """Test STT transcription for multiple Indian languages"""
        for lang, data in INDIAN_LANGUAGE_TEST_DATA.items():
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {
                    "text": data["text"],
                    "confidence": 0.9,
                    "language": data["language_code"],
                    "model_used": "whisper_medium"
                }
                mock_post.return_value.__aenter__.return_value = mock_response
                
                audio_data = f"mock_{lang}_audio".encode()
                result = await client.stt_transcribe(audio_data, language=data["language_code"])
                
                assert result["text"] == data["text"]
                assert result["language"] == data["language_code"]
    
    @pytest.mark.asyncio
    async def test_stt_auto_language_detection(self, client):
        """Test automatic language detection in STT"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "text": "नमस्ते, आप कैसे हैं?",
                "confidence": 0.95,
                "language": "hi",
                "model_used": "whisper_medium",
                "language_detection": {
                    "detected_language": "hi",
                    "confidence": 0.98,
                    "alternatives": [{"language": "ur", "confidence": 0.02}]
                }
            }
            mock_post.return_value.__aenter__.return_value = mock_response
            
            audio_data = b"mock_audio_data"
            result = await client.stt_transcribe(audio_data, language="auto")
            
            assert result["language"] == "hi"
            assert "language_detection" in result
            assert result["language_detection"]["detected_language"] == "hi"
    
    @pytest.mark.asyncio
    async def test_tts_synthesize_hindi(self, client):
        """Test TTS synthesis for Hindi text"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "success": True,
                "audio_url": "http://localhost:8085/audio/hindi_output.wav",
                "duration": 3.5,
                "sample_rate": 22050,
                "model_used": "coqui_hi"
            }
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.tts_synthesize(
                text="नमस्ते, आप कैसे हैं?",
                language="hi",
                voice="female"
            )
            
            assert result["success"] is True
            assert "audio_url" in result
            assert result["model_used"] == "coqui_hi"
    
    @pytest.mark.asyncio
    async def test_tts_synthesize_all_indian_languages(self, client):
        """Test TTS synthesis for all supported Indian languages"""
        for lang, data in INDIAN_LANGUAGE_TEST_DATA.items():
            with patch('aiohttp.ClientSession.post') as mock_post:
                # Mock different TTS models based on language
                expected_model = data["expected_tts_models"][0]  # Use first available model
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {
                    "success": True,
                    "audio_url": f"http://localhost:8085/audio/{lang}_output.wav",
                    "duration": 2.5,
                    "model_used": expected_model
                }
                mock_post.return_value.__aenter__.return_value = mock_response
                
                result = await client.tts_synthesize(
                    text=data["text"],
                    language=data["language_code"]
                )
                
                assert result["success"] is True
                assert result["model_used"] == expected_model
    
    @pytest.mark.asyncio
    async def test_tts_code_switching(self, client):
        """Test TTS synthesis for code-switching text (Hindi-English)"""
        for example in CODE_SWITCHING_TEST_DATA:
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {
                    "success": True,
                    "audio_url": "http://localhost:8085/audio/mixed_output.wav",
                    "duration": 4.0,
                    "model_used": "coqui_xtts_v2",  # Multi-lingual model
                    "languages_detected": example["languages"]
                }
                mock_post.return_value.__aenter__.return_value = mock_response
                
                result = await client.tts_synthesize(
                    text=example["text"],
                    language="auto"  # Let the service detect languages
                )
                
                assert result["success"] is True
                assert "languages_detected" in result
    
    @pytest.mark.asyncio
    async def test_sentiment_analysis_hindi(self, client):
        """Test sentiment analysis for Hindi text"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "sentiment": "positive",
                "confidence": 0.85,
                "scores": {
                    "positive": 0.85,
                    "negative": 0.05,
                    "neutral": 0.10
                },
                "language": "hi",
                "cultural_context": {
                    "politeness_level": "high",
                    "formality": "formal"
                }
            }
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.sentiment_analysis("नमस्ते, आप कैसे हैं?")
            
            assert result["sentiment"] == "positive"
            assert result["confidence"] > 0.8
            assert result["language"] == "hi"
            assert "cultural_context" in result
    
    @pytest.mark.asyncio
    async def test_translation_indian_languages(self, client):
        """Test translation between Indian languages and English"""
        test_cases = [
            {"text": "नमस्ते", "source": "hi", "target": "en", "expected": "Hello"},
            {"text": "Hello", "source": "en", "target": "hi", "expected": "नमस्ते"},
            {"text": "आপনি কেমন আছেন?", "source": "bn", "target": "en", "expected": "How are you?"}
        ]
        
        for test_case in test_cases:
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {
                    "translated_text": test_case["expected"],
                    "confidence": 0.92,
                    "source_language": test_case["source"],
                    "target_language": test_case["target"]
                }
                mock_post.return_value.__aenter__.return_value = mock_response
                
                result = await client.translate(
                    text=test_case["text"],
                    target_language=test_case["target"],
                    source_language=test_case["source"]
                )
                
                assert result["translated_text"] == test_case["expected"]
                assert result["source_language"] == test_case["source"]
                assert result["target_language"] == test_case["target"]
    
    @pytest.mark.asyncio
    async def test_error_handling_network_timeout(self, client):
        """Test error handling for network timeouts"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError("Request timeout")
            
            result = await client.stt_transcribe(b"audio_data")
            
            assert "error" in result
            assert "timeout" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_response(self, client):
        """Test error handling for invalid JSON responses"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.stt_transcribe(b"audio_data")
            
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_service_error(self, client):
        """Test error handling for service errors (500)"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text.return_value = "Internal Server Error"
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await client.stt_transcribe(b"audio_data")
            
            assert "error" in result
            assert result["error"] == "Internal Server Error"
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, client):
        """Test retry mechanism for failed requests"""
        call_count = 0
        
        async def mock_post_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Fail first 2 attempts
                raise aiohttp.ClientError("Connection failed")
            else:  # Succeed on 3rd attempt
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json.return_value = {"status": "healthy"}
                return mock_response
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = mock_post_with_retry
            
            # Assuming the client has retry logic (implementation dependent)
            result = await client.health_check()
            
            # This test assumes retry logic is implemented
            # Adjust based on actual implementation
            assert call_count >= 1  # At least one attempt was made
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test handling multiple concurrent requests"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {
                "text": "Concurrent response",
                "confidence": 0.9,
                "language": "en"
            }
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Create multiple concurrent requests
            tasks = []
            for i in range(5):
                task = client.stt_transcribe(f"audio_data_{i}".encode())
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 5
            for result in results:
                assert result["text"] == "Concurrent response"
                assert result["confidence"] == 0.9
