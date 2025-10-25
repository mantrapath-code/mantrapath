#!/usr/bin/env python3
"""
MantraPath Voice Chatbot Demo Script
Demonstrates the complete voice-enabled chatbot with Qwen2.5-1.5B-Instruct integration.
"""

import asyncio
import httpx
import json
import time
import io
import wave
import numpy as np
from typing import Dict, Any, List, Optional
import os
import sys
from pathlib import Path

class VoiceChatbotDemo:
    """Interactive demo for MantraPath voice-enabled chatbot"""
    
    def __init__(self):
        self.base_url = "http://localhost:8004"
        self.models_url = "http://localhost:8081"
        self.voice_url = "http://localhost:8011"
        self.session_id = None
        self.conversation_history = []
        
    def create_test_audio(self, duration: float = 2.0, sample_rate: int = 16000) -> bytes:
        """Create a simple test audio file (sine wave) for demo purposes"""
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
    
    async def check_services(self) -> Dict[str, bool]:
        """Check if all required services are running"""
        print("🔍 Checking service health...")
        
        services = {
            "Chatbot Service": f"{self.base_url}/health",
            "Models Service": f"{self.models_url}/health",
            "Voice Service": f"{self.voice_url}/health"
        }
        
        health_status = {}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            for service_name, health_url in services.items():
                try:
                    response = await client.get(health_url)
                    is_healthy = response.status_code == 200
                    health_status[service_name] = is_healthy
                    status_icon = "✅" if is_healthy else "❌"
                    print(f"  {status_icon} {service_name}")
                    
                    if is_healthy:
                        data = response.json()
                        if "model" in data:
                            print(f"    Model: {data['model']}")
                        if "features" in data:
                            print(f"    Features: {', '.join(data['features'])}")
                            
                except Exception as e:
                    health_status[service_name] = False
                    print(f"  ❌ {service_name}: {e}")
        
        return health_status
    
    async def create_session(self) -> str:
        """Create a new chat session"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/chatbot/chat/session")
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                print(f"📝 Created session: {self.session_id}")
                return self.session_id
            else:
                raise Exception(f"Failed to create session: {response.status_code}")
    
    async def send_text_message(self, message: str) -> Dict[str, Any]:
        """Send a text message to the chatbot"""
        if not self.session_id:
            await self.create_session()
        
        payload = {
            "message": message,
            "session_id": self.session_id
        }
        
        start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chatbot/chat",
                json=payload
            )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "response": data.get("response", ""),
                "response_time": response_time,
                "session_id": self.session_id
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response_time": response_time
            }
    
    async def send_voice_message(self, audio_data: bytes) -> Dict[str, Any]:
        """Send a voice message to the chatbot"""
        if not self.session_id:
            await self.create_session()
        
        files = {
            'audio_file': ('voice_input.wav', audio_data, 'audio/wav')
        }
        
        start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/test/voice",
                files=files
            )
        
        voice_time = time.time() - start_time
        
        if response.status_code == 200:
            voice_result = response.json()
            
            if voice_result.get("success"):
                # Now send the transcribed text to chatbot
                chat_result = await self.send_text_message(voice_result["transcript"])
                
                return {
                    "success": True,
                    "transcript": voice_result["transcript"],
                    "language": voice_result.get("language", "en"),
                    "confidence": voice_result.get("confidence", 0.0),
                    "chat_response": chat_result.get("response", ""),
                    "voice_time": voice_time,
                    "total_time": voice_time + chat_result.get("response_time", 0)
                }
            else:
                return {
                    "success": False,
                    "error": "Voice processing failed",
                    "voice_time": voice_time
                }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "voice_time": voice_time
            }
    
    async def test_tts_synthesis(self, text: str, language: str = "en") -> Dict[str, Any]:
        """Test text-to-speech synthesis"""
        data = {
            'text': text,
            'language': language,
            'voice': None,
            'model_preference': None
        }
        
        start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.models_url}/api/v1/tts/synthesize",
                data=data
            )
        
        tts_time = time.time() - start_time
        
        if response.status_code == 200:
            audio_data = response.content
            return {
                "success": True,
                "audio_size": len(audio_data),
                "content_type": response.headers.get("content-type"),
                "sample_rate": response.headers.get("X-Sample-Rate"),
                "duration": response.headers.get("X-Duration"),
                "model_used": response.headers.get("X-Model-Used"),
                "tts_time": tts_time
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "tts_time": tts_time
            }
    
    def print_separator(self, title: str = ""):
        """Print a visual separator"""
        if title:
            print(f"\n{'='*60}")
            print(f"  {title}")
            print(f"{'='*60}")
        else:
            print(f"\n{'-'*60}")
    
    async def demo_text_chat(self):
        """Demonstrate text-based chat functionality"""
        self.print_separator("TEXT CHAT DEMO")
        
        test_messages = [
            "Hello! I'm feeling anxious today. Can you help me?",
            "I've been having trouble sleeping lately. What should I do?",
            "I'm feeling overwhelmed with work. Can you give me some breathing exercises?",
            "Thank you, that was very helpful!"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n💬 User Message {i}: {message}")
            
            result = await self.send_text_message(message)
            
            if result["success"]:
                print(f"🤖 Bot Response: {result['response']}")
                print(f"⏱️  Response Time: {result['response_time']:.2f}s")
                
                # Store in conversation history
                self.conversation_history.append({
                    "type": "text",
                    "user": message,
                    "bot": result["response"],
                    "time": result["response_time"]
                })
            else:
                print(f"❌ Error: {result['error']}")
    
    async def demo_voice_chat(self):
        """Demonstrate voice-based chat functionality"""
        self.print_separator("VOICE CHAT DEMO")
        
        print("🎤 Testing voice input processing...")
        
        # Create test audio
        audio_data = self.create_test_audio()
        print(f"📊 Generated test audio: {len(audio_data)} bytes")
        
        result = await self.send_voice_message(audio_data)
        
        if result["success"]:
            print(f"🎯 Transcript: '{result['transcript']}'")
            print(f"🌐 Language: {result['language']}")
            print(f"📈 Confidence: {result['confidence']:.2f}")
            print(f"🤖 Bot Response: {result['chat_response']}")
            print(f"⏱️  Voice Processing: {result['voice_time']:.2f}s")
            print(f"⏱️  Total Time: {result['total_time']:.2f}s")
            
            # Store in conversation history
            self.conversation_history.append({
                "type": "voice",
                "transcript": result["transcript"],
                "language": result["language"],
                "confidence": result["confidence"],
                "bot": result["chat_response"],
                "voice_time": result["voice_time"],
                "total_time": result["total_time"]
            })
        else:
            print(f"❌ Voice processing failed: {result['error']}")
    
    async def demo_tts_functionality(self):
        """Demonstrate text-to-speech functionality"""
        self.print_separator("TEXT-TO-SPEECH DEMO")
        
        test_texts = [
            ("Hello! I'm here to help you with your mental wellness.", "en"),
            ("नमस्ते! मैं आपकी मानसिक सेहत में आपकी मदद करने के लिए यहाँ हूँ।", "hi"),
            ("I understand you're feeling anxious. Let's try some breathing exercises.", "en")
        ]
        
        for i, (text, language) in enumerate(test_texts, 1):
            print(f"\n🔊 TTS Test {i} ({language}): {text[:50]}...")
            
            result = await self.test_tts_synthesis(text, language)
            
            if result["success"]:
                print(f"✅ Audio generated: {result['audio_size']} bytes")
                print(f"📊 Sample Rate: {result['sample_rate']} Hz")
                print(f"⏱️  Duration: {result['duration']}s")
                print(f"🤖 Model: {result['model_used']}")
                print(f"⏱️  Processing Time: {result['tts_time']:.2f}s")
            else:
                print(f"❌ TTS failed: {result['error']}")
    
    async def demo_multilingual_support(self):
        """Demonstrate multilingual support"""
        self.print_separator("MULTILINGUAL SUPPORT DEMO")
        
        # Test supported languages
        languages_to_test = ["en", "hi", "bn", "te", "ta"]
        
        async with httpx.AsyncClient() as client:
            # Test STT languages
            print("🎤 Testing STT supported languages...")
            stt_response = await client.get(f"{self.models_url}/api/v1/stt/languages")
            if stt_response.status_code == 200:
                stt_data = stt_response.json()
                print(f"✅ STT Languages: {', '.join(stt_data.get('languages', []))}")
            
            # Test TTS languages
            print("🔊 Testing TTS supported languages...")
            tts_response = await client.get(f"{self.models_url}/api/v1/tts/languages")
            if tts_response.status_code == 200:
                tts_data = tts_response.json()
                print(f"✅ TTS Languages: {', '.join(tts_data.get('languages', []))}")
    
    def print_performance_summary(self):
        """Print performance summary"""
        self.print_separator("PERFORMANCE SUMMARY")
        
        if not self.conversation_history:
            print("No conversation data to analyze.")
            return
        
        text_interactions = [c for c in self.conversation_history if c["type"] == "text"]
        voice_interactions = [c for c in self.conversation_history if c["type"] == "voice"]
        
        print(f"📊 Total Interactions: {len(self.conversation_history)}")
        print(f"💬 Text Interactions: {len(text_interactions)}")
        print(f"🎤 Voice Interactions: {len(voice_interactions)}")
        
        if text_interactions:
            avg_text_time = sum(c["time"] for c in text_interactions) / len(text_interactions)
            print(f"⏱️  Average Text Response Time: {avg_text_time:.2f}s")
        
        if voice_interactions:
            avg_voice_time = sum(c["total_time"] for c in voice_interactions) / len(voice_interactions)
            print(f"⏱️  Average Voice Response Time: {avg_voice_time:.2f}s")
            
            avg_confidence = sum(c["confidence"] for c in voice_interactions) / len(voice_interactions)
            print(f"📈 Average Voice Confidence: {avg_confidence:.2f}")
        
        # Performance criteria
        print(f"\n🎯 Performance Criteria:")
        print(f"✅ Text Response < 3s: {'PASS' if avg_text_time < 3.0 else 'FAIL'}")
        print(f"✅ Voice Response < 5s: {'PASS' if avg_voice_time < 5.0 else 'FAIL'}")
        print(f"✅ Voice Confidence > 0.5: {'PASS' if avg_confidence > 0.5 else 'FAIL'}")
    
    async def run_interactive_demo(self):
        """Run interactive demo with user input"""
        self.print_separator("INTERACTIVE DEMO")
        
        print("🎮 Interactive Chatbot Demo")
        print("Type 'quit' to exit, 'voice' for voice test, 'tts <text>' for TTS test")
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'voice':
                    print("🎤 Processing voice input...")
                    audio_data = self.create_test_audio()
                    result = await self.send_voice_message(audio_data)
                    
                    if result["success"]:
                        print(f"🎯 Heard: '{result['transcript']}'")
                        print(f"🤖 Response: {result['chat_response']}")
                    else:
                        print(f"❌ Voice failed: {result['error']}")
                        
                elif user_input.lower().startswith('tts '):
                    text = user_input[4:]
                    print(f"🔊 Synthesizing: '{text}'")
                    result = await self.test_tts_synthesis(text)
                    
                    if result["success"]:
                        print(f"✅ Audio generated: {result['audio_size']} bytes")
                    else:
                        print(f"❌ TTS failed: {result['error']}")
                        
                elif user_input:
                    result = await self.send_text_message(user_input)
                    
                    if result["success"]:
                        print(f"🤖 Bot: {result['response']}")
                    else:
                        print(f"❌ Error: {result['error']}")
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    async def run_full_demo(self):
        """Run the complete demo"""
        print("🚀 MantraPath Voice Chatbot Demo")
        print("=" * 60)
        
        # Check services
        health_status = await self.check_services()
        
        if not all(health_status.values()):
            print("\n❌ Some services are not healthy!")
            print("Please ensure all services are running before running the demo.")
            return
        
        print("\n✅ All services are healthy!")
        
        # Run demo sections
        await self.demo_text_chat()
        await self.demo_voice_chat()
        await self.demo_tts_functionality()
        await self.demo_multilingual_support()
        
        # Performance summary
        self.print_performance_summary()
        
        # Interactive demo
        await self.run_interactive_demo()
        
        print("\n🎉 Demo completed successfully!")

async def main():
    """Main entry point"""
    demo = VoiceChatbotDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    asyncio.run(main())