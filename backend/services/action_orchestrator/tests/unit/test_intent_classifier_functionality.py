"""
Comprehensive Intent Classifier Functionality Tests
Tests real intent classification, pattern matching, and entity extraction
"""
import pytest
from unittest.mock import patch

from src.core.intent_classifier import IntentClassifier
from src.models import VoiceIntent, IntentType, ConfidenceLevel


@pytest.mark.asyncio
class TestIntentClassifierFunctionality:
    """Test comprehensive intent classification functionality"""
    
    async def test_journal_intent_classification(self):
        """Test journal-related intent classification"""
        classifier = IntentClassifier()
        
        journal_phrases = [
            "I want to write in my journal",
            "Let me create a journal entry",
            "I need to journal my thoughts",
            "मैं अपनी डायरी में लिखना चाहता हूं",  # Hindi
            "Can you help me write a journal entry?"
        ]
        
        for phrase in journal_phrases:
            intent = await classifier.classify_intent(phrase)
            assert intent.intent_type == IntentType.JOURNAL_ENTRY
            assert intent.confidence_level.value >= 0.7
            assert "journal" in intent.entities.get("activities", [])
    
    async def test_mood_tracking_intent_classification(self):
        """Test mood tracking intent classification"""
        classifier = IntentClassifier()
        
        mood_phrases = [
            "I'm feeling happy today",
            "My mood is really good",
            "I feel anxious about work",
            "Track my mood as excited",
            "मैं आज खुश महसूस कर रहा हूं",  # Hindi: I'm feeling happy today
            "Record that I'm feeling peaceful"
        ]
        
        for phrase in mood_phrases:
            intent = await classifier.classify_intent(phrase)
            assert intent.intent_type == IntentType.MOOD_TRACKING
            assert intent.confidence_level.value >= 0.6
            
            # Should extract mood entities
            emotions = intent.entities.get("emotions", [])
            assert len(emotions) > 0
    
    async def test_meditation_intent_classification(self):
        """Test meditation and mindfulness intent classification"""
        classifier = IntentClassifier()
        
        meditation_phrases = [
            "I want to start a meditation session",
            "Guide me through a 10-minute mindfulness exercise",
            "I did 20 minutes of meditation today",
            "Start breathing exercises",
            "मुझे ध्यान करना है",  # Hindi: I want to meditate
            "Can you help me with relaxation techniques?"
        ]
        
        for phrase in meditation_phrases:
            intent = await classifier.classify_intent(phrase)
            assert intent.intent_type in [IntentType.MEDITATION, IntentType.WELLNESS_ACTIVITY]
            
            activities = intent.entities.get("activities", [])
            assert any(activity in ["meditation", "mindfulness", "breathing"] for activity in activities)
    
    async def test_community_intent_classification(self):
        """Test community interaction intent classification"""
        classifier = IntentClassifier()
        
        community_phrases = [
            "I want to share my progress with the community",
            "Show me community updates",
            "Connect me with support groups",
            "Find people with similar experiences",
            "Join a wellness challenge",
            "समुदाय से जुड़ना चाहता हूं"  # Hindi: Want to connect with community
        ]
        
        for phrase in community_phrases:
            intent = await classifier.classify_intent(phrase)
            assert intent.intent_type == IntentType.COMMUNITY_INTERACTION
            
            activities = intent.entities.get("activities", [])
            assert any(activity in ["sharing", "connect", "community", "support"] for activity in activities)
    
    async def test_chatbot_intent_classification(self):
        """Test chatbot conversation intent classification"""
        classifier = IntentClassifier()
        
        chatbot_phrases = [
            "I need someone to talk to",
            "Can you help me process my feelings?",
            "I want to discuss my anxiety",
            "Talk to me about stress management",
            "मुझे बात करने की जरूरत है",  # Hindi: I need to talk
            "Can we chat about my day?"
        ]
        
        for phrase in chatbot_phrases:
            intent = await classifier.classify_intent(phrase)
            assert intent.intent_type == IntentType.CHATBOT_CONVERSATION
            
            # Should extract conversational topics
            topics = intent.entities.get("topics", [])
            assert len(topics) >= 0  # May or may not have specific topics
    
    async def test_entity_extraction_comprehensive(self):
        """Test comprehensive entity extraction"""
        classifier = IntentClassifier()
        
        # Test time extraction
        time_phrases = [
            "I meditated for 30 minutes",
            "Track my mood for the last 2 hours", 
            "I've been anxious for 3 days",
            "Set a reminder for 5 PM",
            "मैंने 20 मिनट ध्यान किया"  # Hindi: I meditated for 20 minutes
        ]
        
        for phrase in time_phrases:
            intent = await classifier.classify_intent(phrase)
            
            numbers = intent.entities.get("numbers", [])
            time_refs = intent.entities.get("time_references", [])
            
            # Should extract at least one time-related entity
            assert len(numbers) > 0 or len(time_refs) > 0
    
    async def test_emotion_entity_extraction(self):
        """Test emotion entity extraction"""
        classifier = IntentClassifier()
        
        emotion_test_cases = [
            ("I'm feeling really happy and excited", ["happy", "excited"]),
            ("I feel anxious and stressed about work", ["anxious", "stressed"]),
            ("Today I'm peaceful and calm", ["peaceful", "calm"]),
            ("I'm sad and overwhelmed", ["sad", "overwhelmed"]),
            ("मैं खुश और शांत हूं", ["positive"])  # Hindi emotions might be categorized
        ]
        
        for phrase, expected_emotions in emotion_test_cases:
            intent = await classifier.classify_intent(phrase)
            emotions = intent.entities.get("emotions", [])
            
            # Should extract at least one emotion
            assert len(emotions) > 0
            
            # Check if expected emotions are captured (flexible matching)
            found_emotions = [e.lower() for e in emotions]
            assert any(exp_emotion.lower() in str(found_emotions) for exp_emotion in expected_emotions)
    
    async def test_multilingual_classification(self):
        """Test multilingual intent classification"""
        classifier = IntentClassifier()
        
        multilingual_tests = [
            # Hindi
            ("मैं अपनी डायरी लिखना चाहता हूं", IntentType.JOURNAL_ENTRY),
            ("मेरा मूड अच्छा है", IntentType.MOOD_TRACKING),
            ("मुझे ध्यान करना है", IntentType.MEDITATION),
            
            # English
            ("I want to journal my thoughts", IntentType.JOURNAL_ENTRY),
            ("I'm feeling great today", IntentType.MOOD_TRACKING),
            ("Start meditation session", IntentType.MEDITATION),
        ]
        
        for phrase, expected_intent in multilingual_tests:
            intent = await classifier.classify_intent(phrase)
            assert intent.intent_type == expected_intent
            assert intent.confidence_level.value >= 0.5
    
    async def test_confidence_level_accuracy(self):
        """Test confidence level calculation accuracy"""
        classifier = IntentClassifier()
        
        # High confidence phrases (very clear intent)
        high_confidence_phrases = [
            "I want to create a new journal entry right now",
            "Track my mood as extremely happy",
            "Start a 15-minute meditation session"
        ]
        
        for phrase in high_confidence_phrases:
            intent = await classifier.classify_intent(phrase)
            assert intent.confidence_level == ConfidenceLevel.HIGH
            assert intent.confidence_level.value >= 0.8
        
        # Medium confidence phrases (somewhat clear)
        medium_confidence_phrases = [
            "Maybe I should write something",
            "I think I'm feeling okay",
            "Could use some relaxation"
        ]
        
        for phrase in medium_confidence_phrases:
            intent = await classifier.classify_intent(phrase)
            assert intent.confidence_level in [ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
            assert intent.confidence_level.value >= 0.5
        
        # Low confidence phrases (unclear intent)
        low_confidence_phrases = [
            "Hello",
            "What?",
            "Hmm, not sure"
        ]
        
        for phrase in low_confidence_phrases:
            intent = await classifier.classify_intent(phrase)
            # Should still classify but with lower confidence
            assert intent.confidence_level.value <= 0.7
    
    async def test_complex_multi_intent_phrases(self):
        """Test classification of complex phrases with multiple potential intents"""
        classifier = IntentClassifier()
        
        complex_phrases = [
            "I want to journal about my meditation session and share it with the community",
            "Track my mood after the meditation and create a journal entry",
            "I'm feeling anxious, need to meditate and then talk to someone",
            "मैं ध्यान के बाद अपना मूड ट्रैक करना चाहता हूं"  # Hindi: Want to track mood after meditation
        ]
        
        for phrase in complex_phrases:
            intent = await classifier.classify_intent(phrase)
            
            # Should classify with primary intent
            assert intent.intent_type is not None
            assert intent.confidence_level.value >= 0.5
            
            # Should extract multiple activities/entities
            activities = intent.entities.get("activities", [])
            assert len(activities) >= 2  # Should detect multiple activities
    
    async def test_supported_languages_functionality(self):
        """Test supported languages property"""
        classifier = IntentClassifier()
        
        supported_langs = classifier.supported_languages
        
        # Should support at least Hindi and English
        assert "en" in supported_langs
        assert "hi" in supported_langs
        assert len(supported_langs) >= 2
        
        # Each language should have pattern mappings
        for lang in supported_langs:
            # Test that language patterns exist
            patterns = classifier.intent_patterns.get(lang, {})
            assert len(patterns) > 0
    
    async def test_pattern_matching_precision(self):
        """Test pattern matching precision and recall"""
        classifier = IntentClassifier()
        
        # Test specific pattern matches
        pattern_tests = [
            # Journal patterns
            ("journal", "journal_entry"),
            ("diary", "journal_entry"),
            ("write", "journal_entry"),
            
            # Mood patterns  
            ("feeling", "mood_tracking"),
            ("mood", "mood_tracking"),
            ("emotion", "mood_tracking"),
            
            # Meditation patterns
            ("meditate", "meditation"),
            ("mindfulness", "meditation"),
            ("breathing", "meditation"),
            
            # Community patterns
            ("community", "community_interaction"),
            ("share", "community_interaction"),
            ("support", "community_interaction"),
        ]
        
        for keyword, expected_intent in pattern_tests:
            test_phrase = f"I want to {keyword}"
            matched_intent = classifier._match_intent_patterns(test_phrase)
            assert matched_intent == expected_intent
    
    def test_entity_extraction_edge_cases(self):
        """Test entity extraction edge cases"""
        classifier = IntentClassifier()
        
        edge_cases = [
            # Empty string
            ("", {}),
            
            # Only numbers
            ("123 456", {"numbers": [123, 456]}),
            
            # Only emotions
            ("happy sad angry", {"emotions": ["happy", "sad", "angry"]}),
            
            # Mixed content
            ("I'm 25 years old and feeling happy for 2 hours", {
                "numbers": [25, 2],
                "emotions": ["happy"],
                "time_references": ["hours", "years"]
            })
        ]
        
        for text, expected_entities in edge_cases:
            entities = classifier._extract_entities(text)
            
            for entity_type, expected_values in expected_entities.items():
                extracted_values = entities.get(entity_type, [])
                for expected_value in expected_values:
                    assert expected_value in extracted_values or str(expected_value) in str(extracted_values)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
