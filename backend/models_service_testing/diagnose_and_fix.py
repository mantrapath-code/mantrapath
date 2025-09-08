#!/usr/bin/env python3
"""
Models Service Setup and Testing Script
Downloads models and tests functionality properly
"""

import requests
import json
import time
from datetime import datetime

class ModelsServiceSetup:
    def __init__(self, base_url="http://localhost:8085"):
        self.base_url = base_url
    
    def check_health(self):
        """Check service health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def download_model(self, model_name, force=False):
        """Download a specific model"""
        print(f"📥 Downloading model: {model_name}")
        
        payload = {
            "model_name": model_name,
            "force": force
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/models/download",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {model_name}: {result}")
                return True
            else:
                print(f"❌ Failed to download {model_name}: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
        except requests.exceptions.Timeout:
            print(f"⏰ Timeout downloading {model_name}")
            return False
        except Exception as e:
            print(f"❌ Error downloading {model_name}: {e}")
            return False
    
    def check_download_progress(self, model_name):
        """Check download progress"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/models/download/{model_name}/progress")
            if response.status_code == 200:
                progress = response.json()
                print(f"📊 {model_name} progress: {progress}")
                return progress
        except Exception as e:
            print(f"❌ Error checking progress: {e}")
        return None
    
    def get_loaded_models(self):
        """Get currently loaded models"""
        try:
            response = requests.get(f"{self.base_url}/models/loaded")
            return response.json()
        except:
            return {"stt": [], "tts": [], "nlp": []}
    
    def setup_basic_models(self):
        """Download and setup basic models for testing"""
        print("\n🚀 SETTING UP BASIC MODELS")
        print("=" * 50)
        
        if not self.check_health():
            print("❌ Models service not available")
            return False
        
        print("📊 Current loaded models:")
        loaded = self.get_loaded_models()
        print(f"   STT: {loaded['stt']}")
        print(f"   TTS: {loaded['tts']}")
        print(f"   NLP: {loaded['nlp']}")
        
        # Download essential models (small/fast ones first)
        essential_models = [
            "whisper_tiny",      # Small STT model (39MB)
            "vosk_en_us_small",  # Small English STT (40MB)
            "vosk_hi_small",     # Small Hindi STT (45MB)
        ]
        
        print(f"\n📥 Downloading essential models...")
        for model in essential_models:
            print(f"\n🔄 Starting download: {model}")
            success = self.download_model(model)
            if success:
                print(f"✅ {model} download completed")
            else:
                print(f"❌ {model} download failed")
            
            # Small delay between downloads
            time.sleep(2)
        
        # Check what's loaded now
        print(f"\n📊 Models after download:")
        loaded = self.get_loaded_models()
        print(f"   STT: {loaded['stt']}")
        print(f"   TTS: {loaded['tts']}")
        print(f"   NLP: {loaded['nlp']}")
        
        return True
    
    def test_stt_with_downloaded_models(self):
        """Test STT with downloaded models"""
        print("\n🎤 TESTING STT WITH DOWNLOADED MODELS")
        print("=" * 50)
        
        # We need an audio file to test STT
        # For now, let's just check if STT models are loaded
        loaded = self.get_loaded_models()
        stt_models = loaded.get('stt', [])
        
        if not stt_models:
            print("❌ No STT models loaded. Download may still be in progress.")
            return False
        
        print(f"✅ STT models available: {stt_models}")
        # Note: To properly test STT, we would need audio files
        # This is why the original endpoints show languages but can't actually transcribe
        return True
    
    def test_real_translation(self):
        """Test if real translation models are working"""
        print("\n🌍 TESTING TRANSLATION MODELS")
        print("=" * 50)
        
        # Check if NLP models are loaded
        loaded = self.get_loaded_models()
        nlp_models = loaded.get('nlp', [])
        
        if not nlp_models:
            print("❌ No NLP models loaded. This explains why translation is just echoing.")
            print("💡 The translation endpoint is returning mock responses.")
            return False
        
        print(f"✅ NLP models available: {nlp_models}")
        
        # Test translation
        test_text = "Hello, how are you?"
        payload = {
            "text": test_text,
            "source_lang": "en", 
            "target_lang": "hi"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/nlp/translate",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get('translated_text', '')
                
                # Check if it's actually translated or just echoed
                if test_text.lower() in translated.lower() and 'translated from' in translated.lower():
                    print(f"❌ Translation is mock: {translated}")
                    return False
                else:
                    print(f"✅ Real translation: {translated}")
                    return True
            else:
                print(f"❌ Translation request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Translation test error: {e}")
            return False
    
    def diagnose_issues(self):
        """Diagnose what's wrong with the models service"""
        print("\n🔍 DIAGNOSING MODELS SERVICE ISSUES")
        print("=" * 60)
        
        if not self.check_health():
            print("❌ Models service is not running!")
            return
        
        print("✅ Models service is running")
        
        # Check loaded models
        loaded = self.get_loaded_models()
        print(f"\n📊 LOADED MODELS:")
        print(f"   STT: {len(loaded['stt'])} models - {loaded['stt']}")
        print(f"   TTS: {len(loaded['tts'])} models - {loaded['tts']}")
        print(f"   NLP: {len(loaded['nlp'])} models - {loaded['nlp']}")
        
        # Analyze issues
        issues = []
        if not loaded['stt']:
            issues.append("🎤 NO STT MODELS LOADED - Speech recognition won't work")
        
        if not loaded['nlp']:
            issues.append("🧠 NO NLP MODELS LOADED - Translation/sentiment will be mock")
        
        if len(loaded['tts']) <= 5:
            issues.append("🔊 LIMITED TTS MODELS - Only basic espeak available")
        
        if issues:
            print(f"\n❌ IDENTIFIED ISSUES:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ No major issues found")
        
        # Check available models
        try:
            response = requests.get(f"{self.base_url}/models/available")
            available = response.json()
            downloadable = available.get('downloadable_models', {})
            
            print(f"\n📋 AVAILABLE FOR DOWNLOAD:")
            
            # Count by type
            stt_available = [k for k, v in downloadable.items() if v.get('type') == 'stt']
            tts_available = [k for k, v in downloadable.items() if v.get('type') == 'tts']
            
            print(f"   STT models: {len(stt_available)} available")
            print(f"   TTS models: {len(tts_available)} available")
            
            # Show small models that can be downloaded quickly
            print(f"\n💡 RECOMMENDED QUICK DOWNLOADS:")
            quick_models = []
            for name, info in downloadable.items():
                size = info.get('size', '')
                if any(quick in size.lower() for quick in ['mb', '40mb', '50mb', '100mb', '200mb']):
                    quality = info.get('quality', 'unknown')
                    model_type = info.get('type', 'unknown')
                    print(f"   {name} ({model_type}) - {size} - {quality}")
                    quick_models.append(name)
            
            if quick_models:
                print(f"\n🚀 SUGGESTION: Download {len(quick_models)} small models for testing")
            
        except Exception as e:
            print(f"❌ Error checking available models: {e}")
        
        # Final recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"   1. Download small models first (whisper_tiny, vosk_*_small)")
        print(f"   2. Models service needs actual model files, not just configurations")
        print(f"   3. Translation is currently mock - needs real NLP models")
        print(f"   4. Only eSpeak TTS is working - Coqui models need download")

def main():
    """Main function"""
    print("🔧 MODELS SERVICE DIAGNOSTIC & SETUP TOOL")
    print("=" * 60)
    
    setup = ModelsServiceSetup()
    
    # First diagnose issues
    setup.diagnose_issues()
    
    print(f"\n" + "=" * 60)
    choice = input("Would you like to download basic models? (y/n): ").strip().lower()
    
    if choice == 'y':
        setup.setup_basic_models()
        
        print(f"\n⏳ Waiting 30 seconds for models to load...")
        time.sleep(30)
        
        # Test again
        setup.test_stt_with_downloaded_models()
        setup.test_real_translation()
        
        print(f"\n🎯 FINAL STATUS:")
        setup.diagnose_issues()
    
    else:
        print("ℹ️  Skipped model download. Service will continue with limited functionality.")

if __name__ == "__main__":
    main()
