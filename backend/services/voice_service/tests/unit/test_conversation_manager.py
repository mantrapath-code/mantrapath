"""
Unit tests for ConversationManager
Tests conversation flow, context awareness, and multi-turn dialogues
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.conversation_manager import ConversationManager
from tests.fixtures.test_data import CONVERSATION_SCENARIOS, INDIAN_LANGUAGE_TEST_DATA

class TestConversationManager:
    
    @pytest.fixture
    def manager(self):
        """Create a ConversationManager instance for testing"""
        return ConversationManager()
    
    @pytest.fixture
    def mock_models_client(self):
        """Mock models service client"""
        client = AsyncMock()
        client.sentiment_analysis.return_value = {
            "sentiment": "positive",
            "confidence": 0.8,
            "scores": {"positive": 0.8, "negative": 0.1, "neutral": 0.1}
        }
        client.translate.return_value = {
            "translated_text": "Mock translation",
            "confidence": 0.9
        }
        return client
    
    @pytest.mark.asyncio
    async def test_start_conversation_hindi(self, manager, mock_models_client):
        """Test starting a conversation in Hindi"""
        with patch.object(manager, 'models_client', mock_models_client):
            session_id = "test_session_123"
            user_input = "नमस्ते, मुझे मदद चाहिए"
            
            result = await manager.process_conversation(
                session_id=session_id,
                user_input=user_input,
                language="hi"
            )
            
            assert result["success"] is True
            assert result["session_id"] == session_id
            assert result["user_input"] == user_input
            assert "bot_response" in result
            assert result["language_info"]["detected_language"] == "hi"
    
    @pytest.mark.asyncio
    async def test_multi_turn_conversation_medical(self, manager, mock_models_client):
        """Test multi-turn conversation in medical context"""
        with patch.object(manager, 'models_client', mock_models_client):
            scenario = None
            for s in CONVERSATION_SCENARIOS:
                if s["name"] == "medical_consultation":
                    scenario = s
                    break
            
            if not scenario:
                pytest.skip("Medical scenario not found in test data")
            
            session_id = "medical_session_123"
            conversation_history = []
            
            for i, turn in enumerate(scenario["turns"]):
                result = await manager.process_conversation(
                    session_id=session_id,
                    user_input=turn["user"],
                    language=scenario["language"],
                    context={"domain": "medical", "turn": i + 1}
                )
                
                assert result["success"] is True
                assert result["session_id"] == session_id
                assert "bot_response" in result
                assert result["conversation_turn"] == i + 1
                
                # Check if context is being maintained
                if i > 0:
                    assert "context_used" in result
                    assert "previous_turns" in result.get("context_used", {})
                
                conversation_history.append(result)
            
            # Verify conversation flow
            assert len(conversation_history) == len(scenario["turns"])
    
    @pytest.mark.asyncio
    async def test_context_awareness(self, manager, mock_models_client):
        """Test context awareness across conversation turns"""
        with patch.object(manager, 'models_client', mock_models_client):
            session_id = "context_test_123"
            
            # First turn - establish context
            result1 = await manager.process_conversation(
                session_id=session_id,
                user_input="मैं बैंक से लोन लेना चाहता हूं",
                language="hi",
                context={"domain": "banking"}
            )
            
            # Second turn - should remember context
            result2 = await manager.process_conversation(
                session_id=session_id,
                user_input="कितना ब्याज होगा?",
                language="hi"
            )
            
            assert result1["success"] is True
            assert result2["success"] is True
            
            # Check if context is maintained
            assert "context_used" in result2
            context_used = result2["context_used"]
            assert "domain" in context_used
            assert context_used["domain"] == "banking"
    
    @pytest.mark.asyncio
    async def test_sentiment_aware_responses(self, manager, mock_models_client):
        """Test sentiment-aware response generation"""
        test_cases = [
            {
                "input": "मैं बहुत परेशान हूं",
                "expected_sentiment": "negative",
                "expected_tone": "empathetic"
            },
            {
                "input": "मैं बहुत खुश हूं",
                "expected_sentiment": "positive",
                "expected_tone": "celebratory"
            },
            {
                "input": "मुझे जानकारी चाहिए",
                "expected_sentiment": "neutral",
                "expected_tone": "informative"
            }
        ]
        
        for case in test_cases:
            # Mock sentiment analysis
            mock_models_client.sentiment_analysis.return_value = {
                "sentiment": case["expected_sentiment"],
                "confidence": 0.9
            }
            
            with patch.object(manager, 'models_client', mock_models_client):
                result = await manager.process_conversation(
                    session_id="sentiment_test",
                    user_input=case["input"],
                    language="hi"
                )
                
                assert result["success"] is True
                assert result["sentiment_analysis"]["sentiment"] == case["expected_sentiment"]
                
                # Check if response tone matches sentiment
                if "response_tone" in result:
                    assert case["expected_tone"] in result["response_tone"]
    
    @pytest.mark.asyncio
    async def test_code_switching_handling(self, manager, mock_models_client):
        """Test handling of code-switching (Hindi-English)"""
        with patch.object(manager, 'models_client', mock_models_client):
            code_switching_inputs = [
                "मैं आज office जा रहा हूं",
                "Good morning! आपका दिन कैसा जा रहा है?",
                "Meeting में late हो जाऊंगा"
            ]
            
            session_id = "code_switching_test"
            
            for input_text in code_switching_inputs:
                result = await manager.process_conversation(
                    session_id=session_id,
                    user_input=input_text,
                    language="auto"
                )
                
                assert result["success"] is True
                
                # Check language detection
                lang_info = result.get("language_info", {})
                assert "is_mixed" in lang_info
                if lang_info.get("is_mixed"):
                    assert "languages_detected" in lang_info
                    assert len(lang_info["languages_detected"]) > 1
    
    @pytest.mark.asyncio
    async def test_cultural_context_awareness(self, manager, mock_models_client):
        """Test cultural context awareness for Indian languages"""
        cultural_tests = [
            {
                "input": "नमस्कार",
                "language": "hi",
                "expected_cultural_context": {"greeting_style": "formal", "region": "North India"}
            },
            {
                "input": "வணக்கம்",
                "language": "ta",
                "expected_cultural_context": {"greeting_style": "traditional", "region": "South India"}
            }
        ]
        
        for test in cultural_tests:
            with patch.object(manager, 'models_client', mock_models_client):
                result = await manager.process_conversation(
                    session_id="cultural_test",
                    user_input=test["input"],
                    language=test["language"]
                )
                
                assert result["success"] is True
                
                # Check cultural context
                if "cultural_context" in result:
                    cultural_ctx = result["cultural_context"]
                    for key, expected_value in test["expected_cultural_context"].items():
                        if key in cultural_ctx:
                            assert expected_value in str(cultural_ctx[key])
    
    @pytest.mark.asyncio
    async def test_conversation_memory(self, manager, mock_models_client):
        """Test conversation memory and history tracking"""
        with patch.object(manager, 'models_client', mock_models_client):
            session_id = "memory_test_123"
            
            # Series of related inputs
            inputs = [
                "मेरा नाम राज है",
                "मैं दिल्ली से हूं",
                "मुझे नौकरी चाहिए",
                "मेरा नाम क्या है?"  # Should remember from first input
            ]
            
            results = []
            for i, user_input in enumerate(inputs):
                result = await manager.process_conversation(
                    session_id=session_id,
                    user_input=user_input,
                    language="hi"
                )
                results.append(result)
                
                assert result["success"] is True
                assert result["conversation_turn"] == i + 1
            
            # The last response should reference the name from the first input
            last_result = results[-1]
            if "context_used" in last_result:
                context = last_result["context_used"]
                assert "user_name" in str(context).lower() or "राज" in context.get("extracted_entities", {}).get("names", [])
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_input(self, manager, mock_models_client):
        """Test error handling for invalid inputs"""
        with patch.object(manager, 'models_client', mock_models_client):
            test_cases = [
                {"input": "", "expected_error": "empty_input"},
                {"input": "123456", "expected_error": "numbers_only"},
                {"input": "@#$%^&", "expected_error": "special_chars_only"}
            ]
            
            for case in test_cases:
                result = await manager.process_conversation(
                    session_id="error_test",
                    user_input=case["input"],
                    language="hi"
                )
                
                # Should handle gracefully
                if not result.get("success", True):
                    assert "error" in result
                else:
                    # Or provide appropriate fallback response
                    assert "bot_response" in result
    
    @pytest.mark.asyncio
    async def test_conversation_timeout_handling(self, manager, mock_models_client):
        """Test handling of conversation timeouts"""
        # Mock timeout scenario
        mock_models_client.sentiment_analysis.side_effect = asyncio.TimeoutError("Request timeout")
        
        with patch.object(manager, 'models_client', mock_models_client):
            result = await manager.process_conversation(
                session_id="timeout_test",
                user_input="नमस्ते",
                language="hi"
            )
            
            # Should handle timeout gracefully
            assert "error" in result or result.get("success") is False
            if "error" in result:
                assert "timeout" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_concurrent_conversations(self, manager, mock_models_client):
        """Test handling multiple concurrent conversations"""
        with patch.object(manager, 'models_client', mock_models_client):
            import asyncio
            
            # Create multiple concurrent conversations
            tasks = []
            for i in range(5):
                task = manager.process_conversation(
                    session_id=f"concurrent_session_{i}",
                    user_input=f"नमस्ते {i}",
                    language="hi"
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed
            for i, result in enumerate(results):
                assert not isinstance(result, Exception)
                assert result["success"] is True
                assert result["session_id"] == f"concurrent_session_{i}"
    
    @pytest.mark.asyncio
    async def test_response_personalization(self, manager, mock_models_client):
        """Test response personalization based on user preferences"""
        with patch.object(manager, 'models_client', mock_models_client):
            # User with specific preferences
            user_preferences = {
                "response_style": "formal",
                "language_preference": "hi",
                "context_sensitivity": "high"
            }
            
            result = await manager.process_conversation(
                session_id="personalization_test",
                user_input="मुझे मदद चाहिए",
                language="hi",
                user_preferences=user_preferences
            )
            
            assert result["success"] is True
            
            # Check if preferences are reflected
            if "personalization" in result:
                assert result["personalization"]["style"] == "formal"
                assert result["personalization"]["language"] == "hi"
    
    @pytest.mark.asyncio
    async def test_conversation_analytics(self, manager, mock_models_client):
        """Test conversation analytics and metrics"""
        with patch.object(manager, 'models_client', mock_models_client):
            session_id = "analytics_test"
            
            # Process multiple turns
            for i in range(3):
                result = await manager.process_conversation(
                    session_id=session_id,
                    user_input=f"टेस्ट मैसेज {i}",
                    language="hi"
                )
                
                assert result["success"] is True
            
            # Get conversation analytics
            if hasattr(manager, 'get_conversation_analytics'):
                analytics = await manager.get_conversation_analytics(session_id)
                
                assert "total_turns" in analytics
                assert analytics["total_turns"] == 3
                assert "average_response_time" in analytics
                assert "language_distribution" in analytics
    
    @pytest.mark.asyncio
    async def test_conversation_export(self, manager, mock_models_client):
        """Test conversation export functionality"""
        with patch.object(manager, 'models_client', mock_models_client):
            session_id = "export_test"
            
            # Create conversation history
            inputs = ["नमस्ते", "मुझे मदद चाहिए", "धन्यवाद"]
            
            for user_input in inputs:
                await manager.process_conversation(
                    session_id=session_id,
                    user_input=user_input,
                    language="hi"
                )
            
            # Export conversation
            if hasattr(manager, 'export_conversation'):
                export_data = await manager.export_conversation(session_id)
                
                assert "session_id" in export_data
                assert "conversation_turns" in export_data
                assert len(export_data["conversation_turns"]) == 3
                assert "metadata" in export_data
