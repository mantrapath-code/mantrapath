#!/usr/bin/env python3
"""
Enhanced Chatbot Voice Integration Test

Tests the enhanced chatbot service with voice interactions and multi-language support.

Author: MantraPath Development Team
Version: 1.0.0
"""

import asyncio
import aiohttp
import json
import base64
import wave
import numpy as np
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceChatbotTester:
    """Test suite for enhanced voice chatbot functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8104"):
        self.base_url = base_url
        self.session = None
        self.test_session_id = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def generate_test_audio(self, text: str = "Hello, how are you today?") -> bytes:
        """Generate test audio data for testing"""
        # Generate simple sine wave as test audio
        duration = 2.0  # seconds
        sample_rate = 16000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(frequency * 2 * np.pi * t) * 0.3
        
        # Convert to 16-bit PCM
        audio_16bit = (audio_data * 32767).astype(np.int16)
        
        # Create WAV file bytes
        import io
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_16bit.tobytes())
        
        return wav_buffer.getvalue()
    
    async def test_health_check(self) -> bool:
        """Test service health"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Health check passed: {data}")
                    return True
                else:
                    logger.error(f"Health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    async def test_language_detection(self) -> bool:
        """Test language detection endpoint"""
        try:
            test_texts = [
                "Hello, how are you?",  # English
                "Hola, ¿cómo estás?",   # Spanish
                "Bonjour, comment allez-vous?",  # French
                "नमस्ते, आप कैसे हैं?",  # Hindi
                "こんにちは、元気ですか？"   # Japanese
            ]
            
            for text in test_texts:
                data = aiohttp.FormData()
                data.add_field('text', text)
                
                async with self.session.post(f"{self.base_url}/api/language/detect", data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Language detection for '{text}': {result['detected_language']}")
                    else:
                        logger.error(f"Language detection failed for '{text}': {response.status}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Language detection test error: {e}")
            return False
    
    async def test_text_chat(self) -> bool:
        """Test text chat with multi-language support"""
        try:
            test_messages = [
                {
                    "message": "Hello! I'm feeling a bit anxious today. Can you help me?",
                    "language": "en",
                    "preferred_response_language": "en",
                    "include_platform_context": True,
                    "voice_response": False
                },
                {
                    "message": "नमस्ते! मैं आज थोड़ा चिंतित महसूस कर रहा हूं। क्या आप मेरी मदद कर सकते हैं?",
                    "language": "hi",
                    "preferred_response_language": "hi",
                    "include_platform_context": True,
                    "voice_response": False
                },
                {
                    "message": "Hola, me siento muy feliz hoy. ¿Qué ejercicios de respiración recomiendas?",
                    "language": "es",
                    "preferred_response_language": "es",
                    "include_platform_context": True,
                    "voice_response": True
                }
            ]
            
            for i, msg_data in enumerate(test_messages):
                if i == 0:
                    # First message creates session
                    msg_data["session_id"] = None
                else:
                    # Subsequent messages use the same session
                    msg_data["session_id"] = self.test_session_id
                
                async with self.session.post(f"{self.base_url}/api/chat/text", json=msg_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if i == 0:
                            self.test_session_id = result["session_id"]
                        
                        logger.info(f"Text chat {i+1} successful:")
                        logger.info(f"  Detected language: {result['detected_language']}")
                        logger.info(f"  Response language: {result['response_language']}")
                        logger.info(f"  Response: {result['response_text'][:100]}...")
                        logger.info(f"  Intervention type: {result['intervention_type']}")
                        logger.info(f"  Audio URL: {result.get('audio_url', 'None')}")
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"Text chat {i+1} failed: {response.status} - {error_text}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Text chat test error: {e}")
            return False
    
    async def test_voice_chat(self) -> bool:
        """Test voice chat functionality"""
        try:
            # Generate test audio
            test_audio = self.generate_test_audio("I need some breathing exercises to help with anxiety")
            
            # Prepare multipart form data
            data = aiohttp.FormData()
            data.add_field('audio', test_audio, filename='test_audio.wav', content_type='audio/wav')
            
            request_data = {
                "session_id": self.test_session_id,
                "preferred_language": "auto",
                "include_platform_context": True,
                "voice_response": True
            }
            data.add_field('request_data', json.dumps(request_data))
            
            async with self.session.post(f"{self.base_url}/api/chat/voice", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("Voice chat successful:")
                    logger.info(f"  Detected language: {result['detected_language']}")
                    logger.info(f"  Response language: {result['response_language']}")
                    logger.info(f"  Response: {result['response_text'][:100]}...")
                    logger.info(f"  Audio URL: {result.get('audio_url', 'None')}")
                    logger.info(f"  Platform insights available: {bool(result.get('platform_insights'))}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Voice chat failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Voice chat test error: {e}")
            return False
    
    async def test_conversation_memory(self) -> bool:
        """Test conversation memory and history"""
        try:
            # Get chat sessions
            async with self.session.get(f"{self.base_url}/api/chat/sessions") as response:
                if response.status == 200:
                    sessions = await response.json()
                    logger.info(f"Found {len(sessions)} chat sessions")
                    
                    if sessions and self.test_session_id:
                        # Get chat history
                        async with self.session.get(f"{self.base_url}/api/chat/history/{self.test_session_id}") as hist_response:
                            if hist_response.status == 200:
                                history = await hist_response.json()
                                logger.info(f"Chat history contains {len(history)} messages")
                                
                                for msg in history[-3:]:  # Show last 3 messages
                                    logger.info(f"  {msg['sender']}: {msg['content'][:50]}...")
                                
                                return True
                            else:
                                logger.error(f"Failed to get chat history: {hist_response.status}")
                                return False
                else:
                    logger.error(f"Failed to get sessions: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Conversation memory test error: {e}")
            return False
    
    async def test_platform_context_integration(self) -> bool:
        """Test platform context integration"""
        try:
            # Send a message that should trigger platform context
            msg_data = {
                "message": "I've been journaling about my mood lately. How can I better track my progress?",
                "session_id": self.test_session_id,
                "language": "en",
                "include_platform_context": True,
                "voice_response": False
            }
            
            async with self.session.post(f"{self.base_url}/api/chat/text", json=msg_data) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Check for platform insights
                    platform_insights = result.get('platform_insights', {})
                    
                    logger.info("Platform context integration test:")
                    logger.info(f"  Mood data available: {platform_insights.get('mood_data', {}).get('available', False)}")
                    logger.info(f"  Profile data available: {platform_insights.get('profile_data', {}).get('available', False)}")
                    logger.info(f"  Community activity available: {platform_insights.get('community_activity', {}).get('available', False)}")
                    logger.info(f"  Memory insights available: {platform_insights.get('memory_insights', {}).get('available', False)}")
                    
                    # Check conversation memory
                    conversation_memory = result.get('conversation_memory', {})
                    logger.info(f"  Total messages in session: {conversation_memory.get('total_messages', 0)}")
                    logger.info(f"  Detected patterns: {len(conversation_memory.get('detected_patterns', []))}")
                    
                    return True
                else:
                    logger.error(f"Platform context test failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Platform context test error: {e}")
            return False
    
    async def run_comprehensive_test(self) -> Dict[str, bool]:
        """Run comprehensive test suite"""
        test_results = {}
        
        logger.info("Starting Enhanced Chatbot Voice Integration Tests")
        logger.info("=" * 60)
        
        # Test 1: Health Check
        logger.info("Test 1: Health Check")
        test_results["health_check"] = await self.test_health_check()
        
        # Test 2: Language Detection
        logger.info("\nTest 2: Language Detection")
        test_results["language_detection"] = await self.test_language_detection()
        
        # Test 3: Text Chat
        logger.info("\nTest 3: Text Chat with Multi-language Support")
        test_results["text_chat"] = await self.test_text_chat()
        
        # Test 4: Voice Chat
        logger.info("\nTest 4: Voice Chat Integration")
        test_results["voice_chat"] = await self.test_voice_chat()
        
        # Test 5: Conversation Memory
        logger.info("\nTest 5: Conversation Memory")
        test_results["conversation_memory"] = await self.test_conversation_memory()
        
        # Test 6: Platform Context Integration
        logger.info("\nTest 6: Platform Context Integration")
        test_results["platform_context"] = await self.test_platform_context_integration()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name:25} | {status}")
            if result:
                passed += 1
        
        logger.info("=" * 60)
        logger.info(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        return test_results

async def main():
    """Main test runner"""
    async with VoiceChatbotTester() as tester:
        results = await tester.run_comprehensive_test()
        
        # Return appropriate exit code
        all_passed = all(results.values())
        return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test runner error: {e}")
        sys.exit(1)
