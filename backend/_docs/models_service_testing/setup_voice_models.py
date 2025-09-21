#!/usr/bin/env python3
"""
Voice Service Models Setup Script
Downloads and configures the essential models for Voice Service:
- Vosk (STT)
- Coqui TTS (TTS) 
- Hugging Face sentiment models (for context)
"""

import requests
import json
import time
from datetime import datetime
import sys

class VoiceServiceModelsSetup:
    def __init__(self, base_url="http://localhost:8085"):
        self.base_url = base_url
        
        # Essential models for Voice Service
        self.voice_service_models = {
            # STT Models (Vosk - as requested)
            "stt": [
                {
                    "name": "vosk_en_us_small",
                    "size": "40MB",
                    "languages": ["en"],
                    "priority": "high",
                    "description": "Fast English STT"
                },
                {
                    "name": "vosk_hi_small", 
                    "size": "45MB",
                    "languages": ["hi"],
                    "priority": "high",
                    "description": "Fast Hindi STT"
                },
                {
                    "name": "whisper_tiny",
                    "size": "39MB", 
                    "languages": ["en", "hi", "bn", "te", "ta"],
                    "priority": "medium",
                    "description": "Backup multilingual STT"
                }
            ],
            
            # TTS Models (Coqui - as requested)
            "tts": [
                {
                    "name": "coqui_hi",
                    "size": "500MB",
                    "languages": ["hi"],
                    "priority": "high",
                    "description": "High quality Hindi TTS"
                },
                {
                    "name": "coqui_bn",
                    "size": "200MB", 
                    "languages": ["bn"],
                    "priority": "medium",
                    "description": "High quality Bengali TTS"
                },
                {
                    "name": "coqui_xtts_v2",
                    "size": "6GB",
                    "languages": ["en", "hi", "bn", "te", "ta"],
                    "priority": "low",
                    "description": "Multi-language TTS with voice cloning"
                }
            ],
            
            # NLP Models (Hugging Face sentiment - as requested)
            "nlp": [
                {
                    "name": "sentiment_analysis_en",
                    "model_id": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                    "size": "500MB",
                    "languages": ["en"],
                    "priority": "high",
                    "description": "English sentiment analysis"
                },
                {
                    "name": "sentiment_analysis_multilingual",
                    "model_id": "nlptown/bert-base-multilingual-uncased-sentiment",
                    "size": "700MB",
                    "languages": ["hi", "bn", "te", "ta"],
                    "priority": "medium", 
                    "description": "Multilingual sentiment analysis"
                }
            ]
        }
    
    def check_health(self):
        """Check if Models Service is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def download_model(self, model_name, timeout=600):
        """Download a specific model with progress tracking"""
        print(f"📥 Downloading {model_name}...")
        
        payload = {"model_name": model_name, "force": False}
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/models/download",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model_name}: {result}")
                return True
            elif response.status_code == 409:
                print(f"✅ {model_name}: Already downloaded")
                return True
            else:
                print(f"❌ Failed to download {model_name}: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Error: {response.text}")
                return False
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout downloading {model_name} (>{timeout}s)")
            return False
        except Exception as e:
            print(f"❌ Error downloading {model_name}: {e}")
            return False
    
    def get_loaded_models(self):
        """Get currently loaded models"""
        try:
            response = requests.get(f"{self.base_url}/models/loaded")
            return response.json()
        except:
            return {"stt": [], "tts": [], "nlp": []}
    
    def setup_voice_service_models(self, priority_filter="high"):
        """Setup models specifically for Voice Service"""
        print("\n🎤 VOICE SERVICE MODELS SETUP")
        print("=" * 60)
        print("Setting up: Vosk (STT) + Coqui TTS + Hugging Face sentiment")
        print("=" * 60)
        
        if not self.check_health():
            print("❌ Models service not available")
            return False
        
        print("📊 Current state:")
        loaded = self.get_loaded_models()
        print(f"   STT: {len(loaded['stt'])} models")
        print(f"   TTS: {len(loaded['tts'])} models") 
        print(f"   NLP: {len(loaded['nlp'])} models")
        
        # Download models by priority
        priorities = ["high", "medium", "low"]
        if priority_filter == "high":
            priorities = ["high"]
        elif priority_filter == "essential":
            priorities = ["high", "medium"]
        
        total_downloaded = 0
        total_failed = 0
        
        for priority in priorities:
            print(f"\n📥 Downloading {priority.upper()} priority models...")
            
            # Download STT models
            for model in self.voice_service_models["stt"]:
                if model["priority"] == priority:
                    print(f"\n🎤 STT: {model['name']} ({model['size']}) - {model['description']}")
                    success = self.download_model(model["name"])
                    if success:
                        total_downloaded += 1
                    else:
                        total_failed += 1
                    time.sleep(2)
            
            # Download TTS models
            for model in self.voice_service_models["tts"]:
                if model["priority"] == priority:
                    print(f"\n🔊 TTS: {model['name']} ({model['size']}) - {model['description']}")
                    success = self.download_model(model["name"])
                    if success:
                        total_downloaded += 1
                    else:
                        total_failed += 1
                    time.sleep(2)
            
            # Note: NLP models might need special handling
            # They're typically auto-downloaded by Hugging Face
            for model in self.voice_service_models["nlp"]:
                if model["priority"] == priority:
                    print(f"\n🧠 NLP: {model['name']} ({model['size']}) - {model['description']}")
                    print(f"   Model ID: {model['model_id']}")
                    print("   ℹ️  NLP models are typically auto-downloaded on first use")
        
        print(f"\n📊 DOWNLOAD SUMMARY:")
        print(f"   ✅ Downloaded: {total_downloaded}")
        print(f"   ❌ Failed: {total_failed}")
        
        # Wait for models to load
        print(f"\n⏳ Waiting 30 seconds for models to load...")
        time.sleep(30)
        
        # Check final state
        print(f"\n📊 Final state:")
        loaded = self.get_loaded_models()
        print(f"   STT: {len(loaded['stt'])} models - {loaded['stt']}")
        print(f"   TTS: {len(loaded['tts'])} models - {loaded['tts']}")
        print(f"   NLP: {len(loaded['nlp'])} models - {loaded['nlp']}")
        
        return total_failed == 0
    
    def verify_voice_service_readiness(self):
        """Verify that Voice Service has the required models"""
        print("\n🔍 VOICE SERVICE READINESS CHECK")
        print("=" * 50)
        
        loaded = self.get_loaded_models()
        
        # Check STT requirements
        stt_ready = False
        required_stt = ["vosk_en_us_small", "vosk_hi_small", "whisper_tiny"]
        available_stt = loaded.get('stt', [])
        
        for req_model in required_stt:
            if req_model in available_stt:
                stt_ready = True
                print(f"✅ STT: {req_model} available")
                break
        
        if not stt_ready:
            print(f"❌ STT: No required models available")
            print(f"   Available: {available_stt}")
            print(f"   Required: {required_stt}")
        
        # Check TTS requirements  
        tts_ready = False
        required_tts = ["coqui_hi", "coqui_bn", "espeak_hi"]
        available_tts = loaded.get('tts', [])
        
        for req_model in required_tts:
            if req_model in available_tts:
                tts_ready = True
                print(f"✅ TTS: {req_model} available")
                break
        
        if not tts_ready:
            print(f"❌ TTS: No required models available")
            print(f"   Available: {available_tts}")
            print(f"   Required: {required_tts}")
        
        # Check NLP (sentiment analysis)
        nlp_ready = len(loaded.get('nlp', [])) > 0
        if nlp_ready:
            print(f"✅ NLP: {len(loaded['nlp'])} models available")
        else:
            print(f"❌ NLP: No models available for sentiment analysis")
        
        # Overall readiness
        overall_ready = stt_ready and tts_ready
        
        print(f"\n🎯 VOICE SERVICE READINESS:")
        print(f"   🎤 STT Ready: {'✅' if stt_ready else '❌'}")
        print(f"   🔊 TTS Ready: {'✅' if tts_ready else '❌'}")
        print(f"   🧠 NLP Ready: {'✅' if nlp_ready else '⚠️'}")
        print(f"   🎵 Overall: {'✅ READY' if overall_ready else '❌ NOT READY'}")
        
        return overall_ready
    
    def test_voice_service_integration(self):
        """Test the essential Voice Service functions"""
        print("\n🧪 TESTING VOICE SERVICE INTEGRATION")
        print("=" * 50)
        
        # Test TTS (should work)
        print("\n🔊 Testing TTS...")
        tts_payload = {
            "text": "नमस्ते, मैं मंत्रपथ हूं। आपका स्वागत है।",
            "language": "hi",
            "model_preference": "coqui_hi"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/tts/synthesize",
                json=tts_payload
            )
            
            if response.status_code == 200:
                duration = response.headers.get('x-duration', 'Unknown')
                model_used = response.headers.get('x-model-used', 'Unknown')
                print(f"✅ TTS Working - Duration: {duration}s, Model: {model_used}")
            else:
                print(f"❌ TTS Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ TTS Error: {e}")
        
        # Test Sentiment Analysis
        print("\n🧠 Testing Sentiment Analysis...")
        sentiment_payload = {
            "text": "I am very excited about this voice service!",
            "language": "en"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/nlp/sentiment",
                data=sentiment_payload
            )
            
            if response.status_code == 200:
                result = response.json()
                sentiment = result.get('sentiment', 'N/A')
                confidence = result.get('confidence', 'N/A')
                print(f"✅ Sentiment Working - {sentiment} ({confidence})")
            else:
                print(f"❌ Sentiment Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Sentiment Error: {e}")
        
        print(f"\n💡 Note: STT testing requires audio files")
        print(f"   Voice Service will handle audio recording and STT integration")

def main():
    """Main function with options"""
    print("🎤 VOICE SERVICE MODELS SETUP")
    print("=" * 60)
    print("This will setup: Vosk (STT) + Coqui TTS + Hugging Face sentiment")
    print("=" * 60)
    
    setup = VoiceServiceModelsSetup()
    
    if not setup.check_health():
        print("❌ Models Service is not running!")
        print("   Start it with: docker-compose up models-service")
        return
    
    print("\n📋 Setup Options:")
    print("1. High Priority Only (Fast setup - ~585MB)")
    print("2. Essential Models (Recommended - ~1.2GB)")
    print("3. Full Setup (Complete - ~7GB)")
    print("4. Verify Current Setup")
    print("5. Test Integration")
    
    try:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            setup.setup_voice_service_models("high")
            setup.verify_voice_service_readiness()
            setup.test_voice_service_integration()
            
        elif choice == "2":
            setup.setup_voice_service_models("essential") 
            setup.verify_voice_service_readiness()
            setup.test_voice_service_integration()
            
        elif choice == "3":
            setup.setup_voice_service_models("all")
            setup.verify_voice_service_readiness()
            setup.test_voice_service_integration()
            
        elif choice == "4":
            setup.verify_voice_service_readiness()
            
        elif choice == "5":
            setup.test_voice_service_integration()
            
        else:
            print("❌ Invalid option")
    
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")

if __name__ == "__main__":
    main()
