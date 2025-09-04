#!/usr/bin/env python3
"""
Simple Models Service Testing Suite (No Audio Recording)
Test STT, TTS, and NLP capabilities with sample files
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime

class SimpleModelsServiceTester:
    def __init__(self, base_url="http://localhost:8085"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent / "test_outputs"
        self.test_dir.mkdir(exist_ok=True)
        
        # Sample texts for different languages
        self.sample_texts = {
            "en": "Hello, I am MantraPath. This is a test of the text-to-speech system.",
            "hi": "नमस्ते, मैं मंत्रपथ हूं। यह एक टेस्ट है।",
            "bn": "হ্যালো, আমি মন্ত্রপথ। এটি একটি পরীক্ষা।",
            "te": "హలో, నేను మంత్రపథ్. ఇది ఒక పరీక్ష.",
            "ta": "வணக்கம், நான் மந்திரபாதை. இது ஒரு சோதனை.",
            "mr": "नमस्कार, मी मंत्रपथ आहे. ही एक चाचणी आहे.",
            "gu": "નમસ્તે, હું મંત્રપથ છું. આ એક પરીક્ષણ છે.",
            "kn": "ನಮಸ್ತೆ, ನಾನು ಮಂತ್ರಪಥ್. ಇದು ಒಂದು ಪರೀಕ್ಷೆ.",
            "ml": "ഹലോ, ഞാൻ മന്ത്രപഥ്. ഇത് ഒരു പരീക്ഷണമാണ്.",
            "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਂ ਮੰਤ੍ਰਪਥ ਹਾਂ। ਇਹ ਇੱਕ ਟੈਸਟ ਹੈ।"
        }
    
    def check_service_health(self):
        """Check if Models Service is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Models Service is healthy")
                return True
            else:
                print(f"❌ Models Service returned status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Models Service. Make sure it's running on port 8085")
            return False
        except Exception as e:
            print(f"❌ Error checking service: {e}")
            return False
    
    def get_service_status(self):
        """Get detailed service status"""
        try:
            response = requests.get(f"{self.base_url}/status")
            status = response.json()
            
            print("\n📊 SERVICE STATUS")
            print("=" * 50)
            print(f"Service: {status['service']}")
            print(f"Status: {status['status']}")
            print(f"CPU Cores: {status['hardware']['cpu_count']}")
            print(f"Memory: {status['hardware']['memory_gb']:.2f} GB")
            print(f"GPU Available: {status['hardware']['gpu_available']}")
            
            print(f"\n📱 LOADED MODELS")
            print(f"STT Models: {status['models']['stt_loaded']}")
            print(f"TTS Models: {status['models']['tts_loaded']}")
            print(f"NLP Models: {status['models']['nlp_loaded']}")
            
            return status
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return None
    
    def get_all_capabilities(self):
        """Get all service capabilities"""
        try:
            # Get STT languages
            stt_response = requests.get(f"{self.base_url}/api/v1/stt/languages")
            stt_languages = stt_response.json()["supported_languages"]
            
            # Get TTS languages
            tts_response = requests.get(f"{self.base_url}/api/v1/tts/languages")
            tts_languages = tts_response.json()["supported_languages"]
            
            print("\n🎤 STT CAPABILITIES")
            print("=" * 50)
            for lang, models in stt_languages.items():
                print(f"{lang.upper():4s}: {', '.join(models)}")
            
            print("\n🔊 TTS CAPABILITIES")
            print("=" * 50)
            for lang, models in tts_languages.items():
                print(f"{lang.upper():4s}: {', '.join(models)}")
            
            return stt_languages, tts_languages
            
        except Exception as e:
            print(f"❌ Error getting capabilities: {e}")
            return {}, {}
    
    def test_tts_all_languages(self):
        """Test TTS for all available languages"""
        print("\n🔊 TESTING TTS FOR ALL LANGUAGES")
        print("=" * 60)
        
        try:
            tts_response = requests.get(f"{self.base_url}/api/v1/tts/languages")
            tts_languages = tts_response.json()["supported_languages"]
            
            for lang, models in tts_languages.items():
                print(f"\n🌍 Testing {lang.upper()}...")
                
                # Get text for this language
                text = self.sample_texts.get(lang, "Hello, this is a test.")
                
                for model in models:
                    print(f"  🤖 Testing model: {model}")
                    
                    payload = {
                        "text": text,
                        "language": lang,
                        "model_preference": model
                    }
                    
                    try:
                        response = requests.post(
                            f"{self.base_url}/api/v1/tts/synthesize",
                            json=payload,
                            headers={"Content-Type": "application/json"},
                            timeout=30
                        )
                        
                        if response.status_code == 200:
                            # Save audio file
                            timestamp = datetime.now().strftime("%H%M%S")
                            filename = self.test_dir / f"tts_{lang}_{model}_{timestamp}.wav"
                            
                            with open(filename, 'wb') as f:
                                f.write(response.content)
                            
                            # Get metadata
                            duration = response.headers.get('x-duration', 'Unknown')
                            sample_rate = response.headers.get('x-sample-rate', 'Unknown')
                            
                            print(f"    ✅ Success! Duration: {duration}s, Rate: {sample_rate}Hz")
                            print(f"    💾 Saved: {filename.name}")
                        else:
                            print(f"    ❌ Failed: {response.status_code}")
                    
                    except requests.exceptions.Timeout:
                        print(f"    ⏰ Timeout (>30s)")
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
        
        except Exception as e:
            print(f"❌ Error in TTS testing: {e}")
    
    def test_tts_specific_model(self, language, model):
        """Test specific TTS model"""
        print(f"\n🔊 TESTING TTS: {language.upper()} with {model}")
        print("=" * 50)
        
        text = self.sample_texts.get(language, "Hello, this is a test.")
        print(f"📝 Text: {text}")
        
        payload = {
            "text": text,
            "language": language,
            "model_preference": model
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/tts/synthesize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.test_dir / f"tts_{language}_{model}_{timestamp}.wav"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                duration = response.headers.get('x-duration', 'Unknown')
                sample_rate = response.headers.get('x-sample-rate', 'Unknown')
                model_used = response.headers.get('x-model-used', 'Unknown')
                
                print(f"✅ TTS synthesis successful!")
                print(f"💾 Audio saved: {filename}")
                print(f"🎵 Sample Rate: {sample_rate}")
                print(f"⏱️ Duration: {duration}")
                print(f"🤖 Model Used: {model_used}")
                
                return filename
            else:
                print(f"❌ TTS failed with status: {response.status_code}")
                print(f"Error: {response.text}")
                return None
        
        except Exception as e:
            print(f"❌ Error testing TTS: {e}")
            return None
    
    def test_nlp_capabilities(self):
        """Test all NLP capabilities"""
        print("\n🧠 TESTING NLP CAPABILITIES")
        print("=" * 50)
        
        # Test sentiment analysis
        print("\n😊 Testing Sentiment Analysis...")
        test_texts = [
            "I am very happy with this service!",
            "This is terrible and I hate it.",
            "This is okay, nothing special.",
            "Amazing work! Best service ever!",
            "मैं इस सेवा से बहुत खुश हूं!"
        ]
        
        for text in test_texts:
            try:
                payload = {"text": text, "language": "en"}
                response = requests.post(
                    f"{self.base_url}/api/v1/nlp/sentiment",
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    sentiment = result.get('sentiment', 'N/A')
                    confidence = result.get('confidence', 'N/A')
                    print(f"  📝 '{text[:30]}...' → {sentiment} ({confidence})")
                else:
                    print(f"  ❌ Failed for: {text[:30]}...")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        # Test translation
        print("\n🌍 Testing Translation...")
        translation_tests = [
            ("Hello, how are you?", "en", "hi"),
            ("नमस्ते, आप कैसे हैं?", "hi", "en"),
            ("Thank you very much", "en", "bn"),
            ("I love programming", "en", "te"),
            ("This is a beautiful day", "en", "ta")
        ]
        
        for text, source, target in translation_tests:
            try:
                payload = {
                    "text": text,
                    "source_lang": source,
                    "target_lang": target
                }
                
                response = requests.post(
                    f"{self.base_url}/api/v1/nlp/translate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated = result.get('translated_text', 'N/A')
                    confidence = result.get('confidence', 'N/A')
                    print(f"  📝 {source}→{target}: '{text}' → '{translated}' ({confidence})")
                else:
                    print(f"  ❌ Translation failed: {source}→{target}")
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    def test_indian_languages_focus(self):
        """Test specifically Indian languages"""
        print("\n🇮🇳 TESTING INDIAN LANGUAGES FOCUS")
        print("=" * 50)
        
        indian_languages = ["hi", "bn", "te", "ta", "mr", "gu", "kn", "ml", "pa"]
        
        try:
            tts_response = requests.get(f"{self.base_url}/api/v1/tts/languages")
            tts_languages = tts_response.json()["supported_languages"]
            
            for lang in indian_languages:
                if lang in tts_languages:
                    print(f"\n🌍 Testing {lang.upper()}...")
                    models = tts_languages[lang]
                    
                    # Test with the first available model
                    if models:
                        model = models[0]
                        text = self.sample_texts.get(lang, "Test")
                        
                        print(f"  📝 Text: {text}")
                        print(f"  🤖 Model: {model}")
                        
                        result = self.test_tts_specific_model(lang, model)
                        if result:
                            print(f"  ✅ Success!")
                        else:
                            print(f"  ❌ Failed")
                else:
                    print(f"❌ {lang.upper()} not supported")
        
        except Exception as e:
            print(f"❌ Error testing Indian languages: {e}")
    
    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        if not self.check_service_health():
            return
        
        print("\n🧪 COMPREHENSIVE MODELS SERVICE TESTING")
        print("=" * 60)
        
        # Get service status
        self.get_service_status()
        
        # Get all capabilities
        print("\n📋 ANALYZING CAPABILITIES...")
        self.get_all_capabilities()
        
        # Test NLP capabilities
        self.test_nlp_capabilities()
        
        # Test Indian languages specifically
        self.test_indian_languages_focus()
        
        print(f"\n✅ TESTING COMPLETE!")
        print(f"📁 Output files saved in: {self.test_dir}")
        print(f"🎵 You can play the generated .wav files to hear the TTS output")
    
    def run_interactive_menu(self):
        """Interactive menu"""
        if not self.check_service_health():
            return
        
        while True:
            print("\n" + "=" * 60)
            print("🧪 SIMPLE MODELS SERVICE TESTING SUITE")
            print("=" * 60)
            
            print(f"\n📋 TEST OPTIONS:")
            print("1. 📊 Service Status & Capabilities")
            print("2. 🔊 Test TTS for All Languages")
            print("3. 🇮🇳 Test Indian Languages Focus")
            print("4. 🧠 Test NLP Capabilities")
            print("5. 🎯 Test Specific TTS Model")
            print("6. 🚀 Run Comprehensive Test")
            print("7. 🚪 Exit")
            
            try:
                choice = input(f"\nSelect option (1-7): ").strip()
                
                if choice == "1":
                    self.get_service_status()
                    self.get_all_capabilities()
                elif choice == "2":
                    self.test_tts_all_languages()
                elif choice == "3":
                    self.test_indian_languages_focus()
                elif choice == "4":
                    self.test_nlp_capabilities()
                elif choice == "5":
                    lang = input("Enter language code (e.g., hi, en): ").strip()
                    model = input("Enter model name (e.g., espeak_hi, coqui_xtts_v2): ").strip()
                    if lang and model:
                        self.test_tts_specific_model(lang, model)
                elif choice == "6":
                    self.run_comprehensive_test()
                elif choice == "7":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")

def main():
    """Main function"""
    print("🚀 Starting Simple Models Service Testing Suite...")
    
    tester = SimpleModelsServiceTester()
    tester.run_interactive_menu()

if __name__ == "__main__":
    main()
