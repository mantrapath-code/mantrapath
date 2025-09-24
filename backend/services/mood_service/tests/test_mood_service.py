"""
Tests for the modularized Mood Service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Import the main app
from src.main import app
from src.models.schemas import (
    MoodCreateRequest, 
    EmotionAnalysisRequest,
    MoodContextRequest
)

# Test client
client = TestClient(app)

# Mock data
MOCK_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJleHAiOjk5OTk5OTk5OTl9.test"
MOCK_USER_ID = "test-user-id"

def get_auth_headers():
    """Helper to get auth headers"""
    return {"Authorization": f"Bearer {MOCK_TOKEN}"}


class TestMoodEntryEndpoints:
    """Test mood entry creation and retrieval"""
    
    @patch('shared.auth.verify_token')
    def test_create_mood_entry_success(self, mock_verify_token, test_db):
        """Test successful mood entry creation"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        mood_data = {
            "mood_score": 8,
            "description": "Feeling great today!",
            "location": "Home",
            "activity": "Working",
            "context_tags": ["productive", "happy"]
        }
        
        response = client.post(
            "/api/v1/mood/entries",
            json=mood_data,
            headers=get_auth_headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["mood_score"] == 8
        assert data["description"] == "Feeling great today!"
        assert "id" in data
        assert data["user_id"] == MOCK_USER_ID
    
    @patch('shared.auth.verify_token')
    def test_create_mood_entry_invalid_score(self, mock_verify_token):
        """Test mood entry creation with invalid score"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        mood_data = {
            "mood_score": 15,  # Invalid score > 10
            "description": "Invalid score test"
        }
        
        response = client.post(
            "/api/v1/mood/entries",
            json=mood_data,
            headers=get_auth_headers()
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('shared.auth.verify_token')
    def test_get_mood_entries(self, mock_verify_token, test_db):
        """Test retrieving mood entries"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        # First create some entries
        for i in range(3):
            mood_data = {
                "mood_score": i + 5,
                "description": f"Test entry {i}"
            }
            client.post(
                "/api/v1/mood/entries",
                json=mood_data,
                headers=get_auth_headers()
            )
        
        # Then retrieve them
        response = client.get(
            "/api/v1/mood/entries",
            headers=get_auth_headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("mood_score" in entry for entry in data)


class TestEmotionAnalysis:
    """Test emotion analysis endpoints"""
    
    @patch('shared.auth.verify_token')
    @patch('src.services.emotion_analysis.emotion_service.analyze_emotion')
    async def test_analyze_emotion_success(self, mock_analyze, mock_verify_token):
        """Test successful emotion analysis"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        # Mock emotion analysis result
        mock_analyze.return_value = Mock(
            top_emotions=[
                Mock(
                    emotion="joy",
                    sentiment="positive",
                    confidence=85.5,
                    color="#22c55e"
                )
            ],
            primary_emotion="joy",
            primary_sentiment="positive",
            confidence_score=85.5,
            model_dump=lambda: {
                "top_emotions": [{
                    "emotion": "joy",
                    "sentiment": "positive", 
                    "confidence": 85.5,
                    "color": "#22c55e"
                }],
                "primary_emotion": "joy",
                "primary_sentiment": "positive",
                "confidence_score": 85.5
            }
        )
        
        analysis_data = {
            "text": "I am so happy today!",
            "include_mood_entry": False
        }
        
        response = client.post(
            "/api/v1/mood/analyze",
            json=analysis_data,
            headers=get_auth_headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["primary_emotion"] == "joy"
        assert data["primary_sentiment"] == "positive"
        assert len(data["top_emotions"]) > 0
    
    @patch('shared.auth.verify_token')
    def test_analyze_emotion_empty_text(self, mock_verify_token):
        """Test emotion analysis with empty text"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        analysis_data = {
            "text": "",
            "include_mood_entry": False
        }
        
        response = client.post(
            "/api/v1/mood/analyze",
            json=analysis_data,
            headers=get_auth_headers()
        )
        
        assert response.status_code == 422  # Validation error


class TestMoodAnalytics:
    """Test mood analytics endpoints"""
    
    @patch('shared.auth.verify_token')
    def test_get_analytics_overview(self, mock_verify_token, test_db):
        """Test analytics overview endpoint"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        # Create some mood entries first
        for i in range(5):
            mood_data = {
                "mood_score": (i % 3) + 6,  # Scores: 6, 7, 8, 6, 7
                "description": f"Test entry {i}"
            }
            client.post(
                "/api/v1/mood/entries",
                json=mood_data,
                headers=get_auth_headers()
            )
        
        response = client.get(
            "/api/v1/mood/analytics/overview",
            headers=get_auth_headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "total_entries" in data
        assert "average_mood" in data
        assert "current_streak" in data
        assert "mood_distribution" in data
        assert data["total_entries"] == 5
    
    @patch('shared.auth.verify_token')
    def test_get_mood_patterns(self, mock_verify_token, test_db):
        """Test mood patterns endpoint"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        response = client.get(
            "/api/v1/mood/analytics/patterns",
            headers=get_auth_headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "weekly_patterns" in data
        assert "insights" in data
        assert "recommendations" in data
        assert "trend_analysis" in data


class TestMoodContext:
    """Test mood context for memory integration"""
    
    @patch('shared.auth.verify_token')
    def test_create_mood_context(self, mock_verify_token, test_db):
        """Test mood context creation"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        context_data = {
            "session_id": "test-session",
            "context_summary": "Test context",
            "time_range_hours": 24
        }
        
        response = client.post(
            "/api/v1/mood/context",
            json=context_data,
            headers=get_auth_headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["session_id"] == "test-session"
        assert data["user_id"] == MOCK_USER_ID
    
    @patch('shared.auth.verify_token')
    def test_get_mood_contexts(self, mock_verify_token, test_db):
        """Test retrieving mood contexts"""
        mock_verify_token.return_value = {"sub": MOCK_USER_ID}
        
        response = client.get(
            "/api/v1/mood/context",
            headers=get_auth_headers()
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "dependencies" in data
    
    def test_service_info(self):
        """Test service info endpoint"""
        response = client.get("/api/v1/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "endpoints" in data
        assert "features" in data


class TestAuthentication:
    """Test authentication requirements"""
    
    def test_mood_entry_requires_auth(self):
        """Test that mood entry endpoints require authentication"""
        mood_data = {
            "mood_score": 5,
            "description": "Test"
        }
        
        response = client.post("/api/v1/mood/entries", json=mood_data)
        assert response.status_code == 401
    
    def test_analytics_requires_auth(self):
        """Test that analytics endpoints require authentication"""
        response = client.get("/api/v1/mood/analytics/overview")
        assert response.status_code == 401
    
    def test_emotion_analysis_requires_auth(self):
        """Test that emotion analysis requires authentication"""
        analysis_data = {
            "text": "Test text",
            "include_mood_entry": False
        }
        
        response = client.post("/api/v1/mood/analyze", json=analysis_data)
        assert response.status_code == 401


# Fixtures
@pytest.fixture
def test_db():
    """Fixture for test database setup"""
    from shared.database import create_tables
    create_tables()
    yield
    # Cleanup would go here if needed


# Integration test for emotion service
class TestEmotionService:
    """Test the emotion analysis service directly"""
    
    @pytest.mark.asyncio
    async def test_emotion_service_initialization(self):
        """Test that emotion service initializes correctly"""
        from src.services.emotion_analysis import emotion_service
        
        # The service should be initialized
        assert emotion_service is not None
        assert hasattr(emotion_service, 'SENTIMENT_GROUPS')
        assert len(emotion_service.SENTIMENT_GROUPS) > 0
    
    @pytest.mark.asyncio
    async def test_emotion_analysis_fallback(self):
        """Test emotion analysis fallback when model is not available"""
        from src.services.emotion_analysis import EmotionAnalysisService
        
        # Create service instance without model
        service = EmotionAnalysisService()
        service.classifier = None  # Simulate model not loaded
        
        result = await service.analyze_emotion("Test text")
        
        assert result.primary_emotion == "neutral"
        assert result.primary_sentiment.value == "neutral"
        assert len(result.top_emotions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])