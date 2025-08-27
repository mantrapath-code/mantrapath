"""
Unit tests for Models Service Client
Tests all functionality with 80%+ code coverage
"""
import pytest
import httpx
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import json
import base64

# Import the client and related classes
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from clients.models_service_client import (
    ModelsServiceClient, 
    SentimentAnalysis, 
    TextEmbedding, 
    IntentClassification,
    models_service_client
)

class TestModelsServiceClient:
    """Test class for Models Service Client"""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance"""
        return ModelsServiceClient()
    
    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx AsyncClient"""
        return AsyncMock()
    
    @pytest.fixture
    def sample_sentiment_response(self):
        """Sample sentiment analysis response"""
        return {
            "sentiment": "positive",
            "confidence": 0.85,
            "scores": {
                "positive": 0.85,
                "negative": 0.10,
                "neutral": 0.05
            },
            "emotions": {
                "joy": 0.7,
                "sadness": 0.1,
                "anger": 0.05,
                "fear": 0.1,
                "surprise": 0.05
            }
        }
    
    @pytest.fixture
    def sample_embedding_response(self):
        """Sample text embedding response"""
        return {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 100,  # 500-dim vector
            "model": "multilingual-embeddings",
            "dimensions": 500
        }
    
    @pytest.fixture
    def sample_intent_response(self):
        """Sample intent classification response"""
        return {
            "intent": "crisis_support",
            "confidence": 0.92,
            "all_intents": {
                "crisis_support": 0.92,
                "general_chat": 0.05,
                "emotional_support": 0.03
            },
            "entities": [
                {
                    "entity": "emotion",
                    "value": "sadness",
                    "confidence": 0.88
                }
            ]
        }
    
    def test_init_default_config(self):
        """Test client initialization with default configuration"""
        with patch.dict(os.environ, {}, clear=True):
            client = ModelsServiceClient()
            
            assert client.models_service_url == "http://models-service:8085"
            assert client.timeout == 30
            assert client.max_retries == 3
            assert client.is_enabled == True
            assert "hi" in client.supported_languages
            assert "en" in client.supported_languages
    
    def test_init_custom_config(self):
        """Test client initialization with custom configuration"""
        with patch.dict(os.environ, {
            "MODELS_SERVICE_URL": "http://custom-models:9000",
            "MODELS_SERVICE_TIMEOUT": "60",
            "MODELS_SERVICE_MAX_RETRIES": "5",
            "MODELS_SERVICE_ENABLED": "false"
        }):
            client = ModelsServiceClient()
            
            assert client.models_service_url == "http://custom-models:9000"
            assert client.timeout == 60
            assert client.max_retries == 5
            assert client.is_enabled == False
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, client, mock_httpx_client):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_httpx_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.health_check()
            
            assert result == True
            mock_httpx_client.get.assert_called_once_with("http://models-service:8085/health")
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, client, mock_httpx_client):
        """Test failed health check"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_httpx_client.get.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.health_check()
            
            assert result == False
    
    @pytest.mark.asyncio
    async def test_health_check_disabled(self):
        """Test health check when service is disabled"""
        with patch.dict(os.environ, {"MODELS_SERVICE_ENABLED": "false"}):
            client = ModelsServiceClient()
            result = await client.health_check()
            
            assert result == False
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_success(self, client, mock_httpx_client, sample_sentiment_response):
        """Test successful sentiment analysis"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_sentiment_response
        mock_httpx_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.analyze_sentiment("I am feeling happy today", "en")
            
            assert isinstance(result, SentimentAnalysis)
            assert result.sentiment == "positive"
            assert result.confidence == 0.85
            assert result.scores["positive"] == 0.85
            assert result.emotions["joy"] == 0.7
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_disabled(self, client):
        """Test sentiment analysis when service is disabled"""
        with patch.dict(os.environ, {"MODELS_SERVICE_ENABLED": "false"}):
            client = ModelsServiceClient()
            result = await client.analyze_sentiment("I am feeling happy today", "en")
            
            assert isinstance(result, SentimentAnalysis)
            assert result.sentiment == "neutral"
            assert result.confidence == 0.5
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_unsupported_language(self, client):
        """Test sentiment analysis with unsupported language"""
        result = await client.analyze_sentiment("Hello", "xx")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_analyze_sentiment_api_error(self, client, mock_httpx_client):
        """Test sentiment analysis with API error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_httpx_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.analyze_sentiment("Hello", "en")
            
            # Should return basic sentiment analysis
            assert isinstance(result, SentimentAnalysis)
            assert result.sentiment == "neutral"
    
    @pytest.mark.asyncio
    async def test_get_text_embedding_success(self, client, mock_httpx_client, sample_embedding_response):
        """Test successful text embedding generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_embedding_response
        mock_httpx_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.get_text_embedding("Hello world", "en")
            
            assert isinstance(result, TextEmbedding)
            assert len(result.embedding) == 500
            assert result.model == "multilingual-embeddings"
            assert result.dimensions == 500
    
    @pytest.mark.asyncio
    async def test_get_text_embedding_disabled(self, client):
        """Test text embedding when service is disabled"""
        with patch.dict(os.environ, {"MODELS_SERVICE_ENABLED": "false"}):
            client = ModelsServiceClient()
            result = await client.get_text_embedding("Hello world", "en")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_classify_intent_success(self, client, mock_httpx_client, sample_intent_response):
        """Test successful intent classification"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_intent_response
        mock_httpx_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.classify_intent("I need help", "en")
            
            assert isinstance(result, IntentClassification)
            assert result.intent == "crisis_support"
            assert result.confidence == 0.92
            assert len(result.entities) == 1
            assert result.entities[0]["entity"] == "emotion"
    
    @pytest.mark.asyncio
    async def test_classify_intent_disabled(self, client):
        """Test intent classification when service is disabled"""
        with patch.dict(os.environ, {"MODELS_SERVICE_ENABLED": "false"}):
            client = ModelsServiceClient()
            result = await client.classify_intent("I need help", "en")
            
            assert isinstance(result, IntentClassification)
            assert result.intent == "general_chat"
            assert result.confidence == 0.5
    
    @pytest.mark.asyncio
    async def test_generate_response_success(self, client, mock_httpx_client):
        """Test successful response generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "I understand you're feeling sad. How can I help you today?",
            "confidence": 0.88,
            "response_type": "empathetic_support",
            "cultural_adaptations": ["formal_tone", "respectful_language"]
        }
        mock_httpx_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.generate_response(
                "I am feeling sad",
                {"mood": "sad", "language": "en"}
            )
            
            assert "I understand you're feeling sad" in result
    
    @pytest.mark.asyncio
    async def test_generate_response_disabled(self, client):
        """Test response generation when service is disabled"""
        with patch.dict(os.environ, {"MODELS_SERVICE_ENABLED": "false"}):
            client = ModelsServiceClient()
            result = await client.generate_response(
                "Hello",
                {"language": "en"}
            )
            
            assert "I understand" in result
            assert "How can I help" in result
    
    @pytest.mark.asyncio
    async def test_text_to_speech_success(self, client, mock_httpx_client):
        """Test successful text-to-speech conversion"""
        # Sample audio data as base64
        sample_audio = base64.b64encode(b"fake_audio_data").decode('utf-8')
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "audio_data": sample_audio,
            "format": "wav",
            "language": "hi",
            "voice_id": "hi_female_1",
            "duration": 2.5
        }
        mock_httpx_client.post.return_value = mock_response
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.text_to_speech("नमस्ते", "hi")
            
            assert result is not None
            assert len(result) > 0  # Should contain audio bytes
    
    @pytest.mark.asyncio
    async def test_speech_to_text_success(self, client, mock_httpx_client):
        """Test successful speech-to-text conversion"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "text": "नमस्ते",
            "confidence": 0.95,
            "language": "hi"
        }
        mock_httpx_client.post.return_value = mock_response
        
        audio_data = b"fake_audio_data"
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.speech_to_text(audio_data, "hi")
            
            assert result == "नमस्ते"
    
    @pytest.mark.asyncio
    async def test_batch_analyze_sentiments(self, client, mock_httpx_client, sample_sentiment_response):
        """Test batch sentiment analysis"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [sample_sentiment_response, sample_sentiment_response]
        }
        mock_httpx_client.post.return_value = mock_response
        
        texts = ["I am happy", "I am excited"]
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            results = await client.batch_analyze_sentiments(texts, "en")
            
            assert len(results) == 2
            assert all(isinstance(r, SentimentAnalysis) for r in results)
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, client, mock_httpx_client):
        """Test exception handling in API calls"""
        mock_httpx_client.post.side_effect = httpx.RequestError("Connection failed")
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            result = await client.analyze_sentiment("Hello", "en")
            
            # Should return basic sentiment analysis on error
            assert isinstance(result, SentimentAnalysis)
            assert result.sentiment == "neutral"
    
    def test_supported_languages(self, client):
        """Test supported languages getter"""
        languages = client.get_supported_languages()
        
        assert isinstance(languages, dict)
        assert "hi" in languages
        assert "en" in languages
        assert len(languages) >= 17  # Should support 17+ languages
    
    def test_language_support_check(self, client):
        """Test language support checking"""
        assert client.is_language_supported("hi") == True
        assert client.is_language_supported("en") == True
        assert client.is_language_supported("xx") == False
    
    def test_basic_sentiment_analysis_fallback(self, client):
        """Test basic sentiment analysis fallback logic"""
        # Test positive keywords
        result = client._basic_sentiment_analysis("I am very happy and joyful!")
        assert result.sentiment == "positive"
        assert result.confidence > 0.5
        
        # Test negative keywords
        result = client._basic_sentiment_analysis("I am very sad and depressed")
        assert result.sentiment == "negative"
        assert result.confidence > 0.5
        
        # Test neutral text
        result = client._basic_sentiment_analysis("This is a regular statement")
        assert result.sentiment == "neutral"
    
    def test_basic_intent_classification_fallback(self, client):
        """Test basic intent classification fallback logic"""
        # Test crisis keywords
        result = client._basic_intent_classification("I want to hurt myself")
        assert result.intent == "crisis_support"
        assert result.confidence > 0.7
        
        # Test emotional support keywords
        result = client._basic_intent_classification("I am feeling anxious")
        assert result.intent == "emotional_support"
        assert result.confidence > 0.6
        
        # Test general chat
        result = client._basic_intent_classification("What is the weather like?")
        assert result.intent == "general_chat"
    
    def test_parse_sentiment_analysis(self, client, sample_sentiment_response):
        """Test parsing sentiment analysis response"""
        result = client._parse_sentiment_analysis(sample_sentiment_response)
        
        assert isinstance(result, SentimentAnalysis)
        assert result.sentiment == "positive"
        assert result.confidence == 0.85
        assert result.scores["positive"] == 0.85
        assert result.emotions["joy"] == 0.7
    
    def test_parse_text_embedding(self, client, sample_embedding_response):
        """Test parsing text embedding response"""
        result = client._parse_text_embedding(sample_embedding_response)
        
        assert isinstance(result, TextEmbedding)
        assert len(result.embedding) == 500
        assert result.model == "multilingual-embeddings"
        assert result.dimensions == 500
    
    def test_parse_intent_classification(self, client, sample_intent_response):
        """Test parsing intent classification response"""
        result = client._parse_intent_classification(sample_intent_response)
        
        assert isinstance(result, IntentClassification)
        assert result.intent == "crisis_support"
        assert result.confidence == 0.92
        assert len(result.entities) == 1
    
    def test_global_client_instance(self):
        """Test that global client instance is properly initialized"""
        assert models_service_client is not None
        assert isinstance(models_service_client, ModelsServiceClient)
    
    @pytest.mark.asyncio
    async def test_jwt_token_handling(self, client, mock_httpx_client, sample_sentiment_response):
        """Test JWT token handling in requests"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_sentiment_response
        mock_httpx_client.post.return_value = mock_response
        
        jwt_token = "test_jwt_token"
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            await client.analyze_sentiment("Hello", "en", jwt_token=jwt_token)
            
            # Verify that the Authorization header was set
            call_args = mock_httpx_client.post.call_args
            headers = call_args[1]['headers']
            assert headers['Authorization'] == f"Bearer {jwt_token}"
    
    def test_dataclass_creation(self):
        """Test dataclass creation and properties"""
        # Test SentimentAnalysis
        sentiment = SentimentAnalysis(
            sentiment="positive",
            confidence=0.8,
            scores={"positive": 0.8, "negative": 0.2},
            emotions={"joy": 0.7}
        )
        assert sentiment.sentiment == "positive"
        assert sentiment.confidence == 0.8
        
        # Test TextEmbedding
        embedding = TextEmbedding(
            embedding=[0.1, 0.2, 0.3],
            model="test-model",
            dimensions=3
        )
        assert len(embedding.embedding) == 3
        assert embedding.model == "test-model"
        
        # Test IntentClassification
        intent = IntentClassification(
            intent="test_intent",
            confidence=0.9,
            all_intents={"test_intent": 0.9},
            entities=[]
        )
        assert intent.intent == "test_intent"
        assert intent.confidence == 0.9

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=clients.models_service_client", "--cov-report=term-missing"])
