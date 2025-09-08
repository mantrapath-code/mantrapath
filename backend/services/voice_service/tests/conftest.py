"""
Test configuration and utilities
"""
import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_models_service():
    """Mock models service responses"""
    class MockModelsService:
        def __init__(self):
            self.is_healthy = True
            self.responses = {}
        
        async def health_check(self):
            return {"status": "healthy" if self.is_healthy else "unhealthy"}
        
        async def stt_transcribe(self, audio_data, language="auto"):
            return {
                "text": "मॉक ट्रांस्क्रिप्शन",
                "confidence": 0.95,
                "language": language,
                "model_used": "whisper_medium"
            }
        
        async def tts_synthesize(self, text, language="hi", voice=None):
            return {
                "success": True,
                "audio_url": "http://localhost:8085/audio/mock.wav",
                "duration": 2.5,
                "model_used": "coqui_hi"
            }
        
        async def nlp_sentiment(self, text):
            return {
                "sentiment": "positive",
                "confidence": 0.8,
                "scores": {"positive": 0.8, "negative": 0.1, "neutral": 0.1}
            }
        
        async def nlp_translate(self, text, target_language="en"):
            return {
                "translated_text": "Mock translation",
                "confidence": 0.9,
                "source_language": "hi"
            }
    
    return MockModelsService()

@pytest.fixture
def sample_audio_data():
    """Sample audio data for testing"""
    return b"mock_audio_data"

@pytest.fixture
def indian_language_texts():
    """Indian language text samples"""
    return {
        "hindi": "नमस्ते, आप कैसे हैं?",
        "bengali": "আপনি কেমন আছেন?",
        "tamil": "நீங்கள் எப்படி இருக்கிறீர்கள்?",
        "telugu": "మీరు ఎలా ఉన్నారు?",
        "marathi": "तुम्ही कसे आहात?",
        "gujarati": "તમે કેમ છો?",
        "kannada": "ನೀವು ಹೇಗಿದ್ದೀರಿ?",
        "malayalam": "നിങ്ങൾ എങ്ങനെയുണ്ട്?",
        "punjabi": "ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?",
        "urdu": "آپ کیسے ہیں؟"
    }

@pytest.fixture
def code_switching_examples():
    """Code-switching examples (Hindi-English)"""
    return [
        "मैं आज office जा रहा हूँ",
        "Good morning! आपका दिन कैसा जा रहा है?",
        "Meeting में late हो जाऊंगा",
        "Please call me बाद में",
        "यह बहुत important है"
    ]

@pytest.fixture
def session_test_data():
    """Test data for session management"""
    return {
        "user_id": "test_user_123",
        "language": "hi",
        "preferences": {
            "voice_speed": "normal",
            "voice_gender": "female",
            "enhancement": True
        },
        "voice_settings": {
            "model": "coqui_hi",
            "pitch": 0.5,
            "speed": 1.0
        }
    }

@pytest.fixture
def conversation_contexts():
    """Different conversation contexts"""
    return {
        "medical": {
            "domain": "healthcare",
            "context": "patient consultation",
            "expected_tone": "professional, caring"
        },
        "banking": {
            "domain": "finance",
            "context": "customer service",
            "expected_tone": "formal, helpful"
        },
        "education": {
            "domain": "learning",
            "context": "tutoring session",
            "expected_tone": "encouraging, clear"
        }
    }
