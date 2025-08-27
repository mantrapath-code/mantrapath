"""
Unit tests for Intent Classifier
"""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.core.intent_classifier import IntentClassifier
from src.models import VoiceIntent, CulturalContext, IntentType, ConfidenceLevel


class TestIntentClassifier:
    """Test IntentClassifier functionality"""
    
    @pytest.fixture
    def intent_classifier(self):
        """Create intent classifier instance"""
        return IntentClassifier()
    
    def test_pattern_matching_journal_keywords(self, intent_classifier):
        """Test pattern matching for journal keywords"""
        text = "I want to write in my diary about today"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "journal_creation"
        
        text = "Let me journal this experience"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "journal_creation"
    
    def test_pattern_matching_mood_keywords(self, intent_classifier):
        """Test pattern matching for mood keywords"""
        text = "I'm feeling great today"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "mood_tracking"
        
        text = "My mood is really positive"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "mood_tracking"
    
    def test_pattern_matching_sharing_keywords(self, intent_classifier):
        """Test pattern matching for sharing keywords"""
        text = "Share this with my meditation group"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "community_sharing"
        
        text = "Post this to the community"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "community_sharing"
    
    def test_pattern_matching_question_keywords(self, intent_classifier):
        """Test pattern matching for question keywords"""
        text = "Can you help me with breathing techniques?"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "chatbot_conversation"
        
        text = "What are some good meditation practices?"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "chatbot_conversation"
    
    def test_pattern_matching_analytics_keywords(self, intent_classifier):
        """Test pattern matching for analytics keywords"""
        text = "Show me my progress report"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "analytics_request"
        
        text = "What are my meditation statistics?"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "analytics_request"
    
    def test_pattern_matching_profile_keywords(self, intent_classifier):
        """Test pattern matching for profile keywords"""
        text = "Update my preferences for notifications"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "profile_update"
        
        text = "Change my meditation goals"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "profile_update"
    
    def test_pattern_matching_unknown_text(self, intent_classifier):
        """Test pattern matching for unknown text"""
        text = "Random unrelated text that doesn't match any patterns"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "unknown"
    
    def test_extract_entities_meditation(self, intent_classifier):
        """Test entity extraction for meditation activities"""
        text = "I did a 20-minute mindfulness meditation session"
        
        entities = intent_classifier._extract_entities(text)
        
        assert "meditation" in entities["activity"]
        assert entities["duration"] == "20-minute"
        assert "mindfulness" in entities["meditation_type"]
    
    def test_extract_entities_mood(self, intent_classifier):
        """Test entity extraction for mood-related text"""
        text = "I'm feeling anxious and stressed about work"
        
        entities = intent_classifier._extract_entities(text)
        
        assert entities["sentiment"] == "negative"
        assert "anxious" in entities["emotions"]
        assert "stressed" in entities["emotions"]
        assert "work" in entities["context"]
    
    def test_extract_entities_goals(self, intent_classifier):
        """Test entity extraction for goal-related text"""
        text = "Set my daily meditation goal to 45 minutes"
        
        entities = intent_classifier._extract_entities(text)
        
        assert entities["goal_type"] == "meditation"
        assert entities["duration"] == "45 minutes"
        assert entities["frequency"] == "daily"
    
    @pytest.mark.asyncio
    async def test_classify_intent_with_mocked_components(self, intent_classifier):
        """Test classify_intent method with mocked internal components"""
        # Create sample cultural context
        cultural_context = CulturalContext(
            language="en",
            cultural_region="US"
        )
        
        # Create sample voice intent
        voice_intent = VoiceIntent(
            intent_type=IntentType.JOURNAL_ENTRY,
            confidence=0.95,
            confidence_level=ConfidenceLevel.HIGH,
            raw_text="I want to journal about my meditation",
            processed_text="I want to journal about my meditation",
            cultural_context=cultural_context,
            user_id=uuid4()
        )
        
        # Mock the internal methods
        with patch.object(intent_classifier, '_match_intent_patterns', return_value='journal_creation'):
            with patch.object(intent_classifier, '_extract_entities', return_value={
                'activity': ['meditation'],
                'sentiment': 'positive'
            }):
                result = await intent_classifier.classify_intent(voice_intent)
                
                assert "intent_type" in result
                assert "confidence" in result
                assert "entities" in result
                assert "suggested_services" in result
    
    def test_supported_languages(self, intent_classifier):
        """Test supported languages list"""
        languages = intent_classifier.supported_languages
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert len(languages) >= 3
    
    def test_confidence_calculation(self, intent_classifier):
        """Test confidence calculation logic"""
        # High confidence text
        high_conf_text = "I want to write in my journal about today's meditation"
        high_confidence = intent_classifier._calculate_confidence(high_conf_text, "journal_creation")
        assert high_confidence > 0.8
        
        # Low confidence text
        low_conf_text = "maybe something about writing"
        low_confidence = intent_classifier._calculate_confidence(low_conf_text, "journal_creation")
        assert low_confidence < 0.6
    
    def test_service_mapping(self, intent_classifier):
        """Test service mapping for different intent types"""
        services = intent_classifier._get_suggested_services("journal_creation")
        assert "journal_service" in services
        
        services = intent_classifier._get_suggested_services("mood_tracking")
        assert "mood_service" in services
        
        services = intent_classifier._get_suggested_services("community_sharing")
        assert "community_service" in services
        
        services = intent_classifier._get_suggested_services("chatbot_conversation")
        assert "chatbot_service" in services
        
        services = intent_classifier._get_suggested_services("profile_update")
        assert "profile_service" in services
        
        services = intent_classifier._get_suggested_services("analytics_request")
        assert "analytics_service" in services
    
    @pytest.mark.asyncio
    async def test_classify_intent_community_sharing(self, intent_classifier):
        """Test classifying community sharing intent"""
        voice_intent = VoiceIntent(
            text="Share my meditation progress with the community",
            language="en",
            confidence=0.88
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["intent_type"] == "community_sharing"
        assert "community_service" in result["suggested_services"]
        assert "meditation" in result["entities"]["activity"]
    
    @pytest.mark.asyncio
    async def test_classify_intent_chatbot_conversation(self, intent_classifier):
        """Test classifying chatbot conversation intent"""
        voice_intent = VoiceIntent(
            text="Can you help me with meditation techniques?",
            language="en",
            confidence=0.90
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["intent_type"] == "chatbot_conversation"
        assert "chatbot_service" in result["suggested_services"]
        assert "meditation" in result["entities"]["topic"]
    
    @pytest.mark.asyncio
    async def test_classify_intent_profile_update(self, intent_classifier):
        """Test classifying profile update intent"""
        voice_intent = VoiceIntent(
            text="Update my meditation goals to 30 minutes daily",
            language="en",
            confidence=0.85
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["intent_type"] == "profile_update"
        assert "profile_service" in result["suggested_services"]
        assert "goals" in result["entities"]["update_type"]
    
    @pytest.mark.asyncio
    async def test_classify_intent_analytics_request(self, intent_classifier):
        """Test classifying analytics request intent"""
        voice_intent = VoiceIntent(
            text="Show me my meditation progress this month",
            language="en",
            confidence=0.87
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["intent_type"] == "analytics_request"
        assert "analytics_service" in result["suggested_services"]
        assert "progress" in result["entities"]["request_type"]
    
    @pytest.mark.asyncio
    async def test_classify_intent_spanish(self, intent_classifier):
        """Test classifying Spanish intent"""
        voice_intent = VoiceIntent(
            text="Quiero escribir en mi diario sobre la meditación",
            language="es",
            confidence=0.89
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["intent_type"] == "journal_creation"
        assert result["confidence"] > 0.7
        assert "journal_service" in result["suggested_services"]
    
    @pytest.mark.asyncio
    async def test_classify_intent_with_cultural_context(self, intent_classifier):
        """Test intent classification with cultural context"""
        voice_intent = VoiceIntent(
            text="I want to share my wellness journey",
            language="en",
            confidence=0.91
        )
        
        cultural_context = CulturalContext(
            country="JP",
            timezone="Asia/Tokyo",
            language="en",
            cultural_preferences={
                "communication_style": "indirect",
                "privacy_level": "high"
            }
        )
        
        result = await intent_classifier.classify_intent(
            voice_intent, 
            cultural_context
        )
        
        assert result["intent_type"] == "community_sharing"
        # Should respect cultural privacy preferences
        assert result["cultural_adaptations"]["privacy_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_classify_intent_low_confidence(self, intent_classifier):
        """Test handling low confidence classification"""
        voice_intent = VoiceIntent(
            text="Something something unclear mumble",
            language="en",
            confidence=0.3  # Low confidence input
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["intent_type"] == "unknown"
        assert result["confidence"] < 0.5
        assert result["suggested_services"] == []
    
    @pytest.mark.asyncio
    async def test_classify_intent_multiple_activities(self, intent_classifier):
        """Test classifying intent with multiple activities"""
        voice_intent = VoiceIntent(
            text="I meditated and did yoga today, want to journal and track mood",
            language="en",
            confidence=0.93
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        # Should handle multiple intents
        assert len(result["suggested_services"]) >= 2
        assert "journal_service" in result["suggested_services"]
        assert "mood_service" in result["suggested_services"]
        assert len(result["entities"]["activity"]) >= 2
    
    @pytest.mark.asyncio
    async def test_extract_entities_meditation(self, intent_classifier):
        """Test entity extraction for meditation activities"""
        text = "I did a 20-minute mindfulness meditation session"
        
        entities = intent_classifier._extract_entities(text)
        
        assert "meditation" in entities["activity"]
        assert entities["duration"] == "20-minute"
        assert "mindfulness" in entities["meditation_type"]
    
    @pytest.mark.asyncio
    async def test_extract_entities_mood(self, intent_classifier):
        """Test entity extraction for mood-related text"""
        text = "I'm feeling anxious and stressed about work"
        
        entities = intent_classifier._extract_entities(text)
        
        assert entities["sentiment"] == "negative"
        assert "anxious" in entities["emotions"]
        assert "stressed" in entities["emotions"]
        assert "work" in entities["context"]
    
    @pytest.mark.asyncio
    async def test_extract_entities_goals(self, intent_classifier):
        """Test entity extraction for goal-related text"""
        text = "Set my daily meditation goal to 45 minutes"
        
        entities = intent_classifier._extract_entities(text)
        
        assert entities["goal_type"] == "meditation"
        assert entities["duration"] == "45 minutes"
        assert entities["frequency"] == "daily"
    
    def test_pattern_matching_journal_keywords(self, intent_classifier):
        """Test pattern matching for journal keywords"""
        text = "I want to write in my diary about today"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "journal_creation"
        
        text = "Let me journal this experience"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "journal_creation"
    
    def test_pattern_matching_mood_keywords(self, intent_classifier):
        """Test pattern matching for mood keywords"""
        text = "I'm feeling great today"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "mood_tracking"
        
        text = "My mood is really positive"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "mood_tracking"
    
    def test_pattern_matching_sharing_keywords(self, intent_classifier):
        """Test pattern matching for sharing keywords"""
        text = "Share this with my meditation group"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "community_sharing"
        
        text = "Post this to the community"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "community_sharing"
    
    def test_pattern_matching_question_keywords(self, intent_classifier):
        """Test pattern matching for question keywords"""
        text = "Can you help me with breathing techniques?"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "chatbot_conversation"
        
        text = "What are some good meditation practices?"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "chatbot_conversation"
    
    def test_pattern_matching_analytics_keywords(self, intent_classifier):
        """Test pattern matching for analytics keywords"""
        text = "Show me my progress report"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "analytics_request"
        
        text = "What are my meditation statistics?"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "analytics_request"
    
    def test_pattern_matching_profile_keywords(self, intent_classifier):
        """Test pattern matching for profile keywords"""
        text = "Update my preferences for notifications"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "profile_update"
        
        text = "Change my meditation goals"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "profile_update"
    
    def test_pattern_matching_unknown_text(self, intent_classifier):
        """Test pattern matching for unknown text"""
        text = "Random unrelated text that doesn't match any patterns"
        intent_type = intent_classifier._match_intent_patterns(text)
        assert intent_type == "unknown"
    
    @pytest.mark.asyncio
    async def test_multilingual_support_french(self, intent_classifier):
        """Test French language support"""
        voice_intent = VoiceIntent(
            text="Je veux écrire dans mon journal",
            language="fr",
            confidence=0.87
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["intent_type"] == "journal_creation"
        assert result["confidence"] > 0.7
    
    @pytest.mark.asyncio
    async def test_multilingual_support_german(self, intent_classifier):
        """Test German language support"""
        voice_intent = VoiceIntent(
            text="Ich möchte meditieren",
            language="de",
            confidence=0.84
        )
        
        result = await intent_classifier.classify_intent(voice_intent)
        
        assert result["confidence"] > 0.7
        assert len(result["suggested_services"]) > 0
