#!/usr/bin/env python3
"""
Interactive Models Service Testing Suite
Test STT, TTS, and NLP capabilities with different models
"""

import requests
import json
import os
import tempfile
import wave
import pyaudio
import time
from pathlib import Path
import threading
from datetime import datetime

class ModelsServiceTester:
    def __init__(self, base_url="http://localhost:8085"):
        self.base_url = base_url
        self.test_dir = Path(__file__).parent / "test_outputs"
        self.test_dir.mkdir(exist_ok=True)
        
        # Audio recording parameters
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        
        self.audio_recorder = None
        self.is_recording = False
        
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
            
            print(f"\n🌍 SUPPORTED LANGUAGES")
            print(f"STT: {len(status['supported_languages']['stt'])} languages")
            print(f"TTS: {len(status['supported_languages']['tts'])} languages")
            
            return status
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return None
    
    def get_stt_languages(self):
        """Get STT languages and models"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/stt/languages")
            return response.json()["supported_languages"]
        except Exception as e:
            print(f"❌ Error getting STT languages: {e}")
            return {}
    
    def get_tts_languages(self):
        """Get TTS languages and models"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/tts/languages")
            return response.json()["supported_languages"]
        except Exception as e:
            print(f"❌ Error getting TTS languages: {e}")
            return {}
    
    def record_audio(self, duration=5):
        """Record audio from microphone"""
        try:
            audio = pyaudio.PyAudio()
            
            print(f"🎤 Recording for {duration} seconds... Speak now!")
            
            stream = audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            for _ in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.test_dir / f"recorded_audio_{timestamp}.wav"
            
            wf = wave.open(str(filename), 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.audio_format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            print(f"✅ Audio saved: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error recording audio: {e}")
            return None
    
    def test_stt_with_file(self, audio_file, language="auto", model_preference=None):
        """Test STT with audio file"""
        try:
            with open(audio_file, 'rb') as f:
                files = {'audio': f}
                data = {
                    'language': language,
                    'model_preference': model_preference
                }
                
                print(f"🎯 Testing STT with {model_preference or 'auto'} model...")
                response = requests.post(
                    f"{self.base_url}/api/v1/stt/transcribe",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Transcription successful!")
                    print(f"📝 Text: {result.get('text', 'N/A')}")
                    print(f"🌍 Language: {result.get('language_detected', 'N/A')}")
                    print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
                    print(f"🤖 Model: {result.get('model_used', 'N/A')}")
                    return result
                else:
                    print(f"❌ STT failed with status: {response.status_code}")
                    print(f"Error: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error testing STT: {e}")
            return None
    
    def test_tts_synthesis(self, text, language="en", voice=None, model_preference=None):
        """Test TTS synthesis"""
        try:
            payload = {
                "text": text,
                "language": language,
                "voice": voice,
                "model_preference": model_preference
            }
            
            print(f"🔊 Testing TTS with {model_preference or 'auto'} model...")
            print(f"📝 Text: {text}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/tts/synthesize",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Save audio file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.test_dir / f"tts_output_{language}_{model_preference}_{timestamp}.wav"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                # Get metadata from headers
                sample_rate = response.headers.get('x-sample-rate', 'Unknown')
                duration = response.headers.get('x-duration', 'Unknown')
                model_used = response.headers.get('x-model-used', 'Unknown')
                
                print(f"✅ TTS synthesis successful!")
                print(f"💾 Audio saved: {filename}")
                print(f"🎵 Sample Rate: {sample_rate}")
                print(f"⏱️ Duration: {duration}")
                print(f"🤖 Model: {model_used}")
                
                return filename
            else:
                print(f"❌ TTS failed with status: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing TTS: {e}")
            return None
    
    def test_sentiment_analysis(self, text, language="en"):
        """Test sentiment analysis"""
        try:
            payload = {
                "text": text,
                "language": language
            }
            
            print(f"😊 Testing sentiment analysis...")
            print(f"📝 Text: {text}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/nlp/sentiment",
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Sentiment analysis successful!")
                print(f"😊 Sentiment: {result.get('sentiment', 'N/A')}")
                print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
                print(f"📊 Scores: {result.get('scores', {})}")
                return result
            else:
                print(f"❌ Sentiment analysis failed: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing sentiment: {e}")
            return None
    
    def test_translation(self, text, source_lang, target_lang, model_preference=None):
        """Test translation"""
        try:
            payload = {
                "text": text,
                "source_lang": source_lang,
                "target_lang": target_lang,
                "model_preference": model_preference
            }
            
            print(f"🌍 Testing translation ({source_lang} → {target_lang})...")
            print(f"📝 Original: {text}")
            
            response = requests.post(
                f"{self.base_url}/api/v1/nlp/translate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Translation successful!")
                print(f"📝 Translated: {result.get('translated_text', 'N/A')}")
                print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
                return result
            else:
                print(f"❌ Translation failed: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error testing translation: {e}")
            return None
    
    def interactive_stt_test(self):
        """Interactive STT testing"""
        print("\n🎤 INTERACTIVE STT TESTING")
        print("=" * 50)
        
        stt_languages = self.get_stt_languages()
        if not stt_languages:
            print("❌ No STT languages available")
            return
        
        # Show available languages and models
        print("\n📋 Available STT Languages and Models:")
        for i, (lang, models) in enumerate(stt_languages.items(), 1):
            print(f"{i:2d}. {lang.upper()}: {', '.join(models)}")
        
        try:
            # Select language
            lang_choice = input(f"\nSelect language (1-{len(stt_languages)}) or enter language code: ").strip()
            
            if lang_choice.isdigit():
                lang_idx = int(lang_choice) - 1
                if 0 <= lang_idx < len(stt_languages):
                    selected_lang = list(stt_languages.keys())[lang_idx]
                else:
                    print("❌ Invalid selection")
                    return
            else:
                selected_lang = lang_choice.lower()
                if selected_lang not in stt_languages:
                    print(f"❌ Language '{selected_lang}' not supported")
                    return
            
            # Select model
            available_models = stt_languages[selected_lang]
            print(f"\n📋 Available models for {selected_lang.upper()}:")
            for i, model in enumerate(available_models, 1):
                print(f"{i}. {model}")
            
            model_choice = input(f"Select model (1-{len(available_models)}) or press Enter for auto: ").strip()
            
            if model_choice.isdigit():
                model_idx = int(model_choice) - 1
                if 0 <= model_idx < len(available_models):
                    selected_model = available_models[model_idx]
                else:
                    selected_model = None
            else:
                selected_model = None
            
            # Recording options
            print(f"\n🎤 STT Test Options:")
            print("1. Record new audio")
            print("2. Use existing audio file")
            
            option = input("Select option (1-2): ").strip()
            
            if option == "1":
                duration = input("Recording duration in seconds (default 5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                
                audio_file = self.record_audio(duration)
                if not audio_file:
                    return
            
            elif option == "2":
                audio_path = input("Enter path to audio file: ").strip()
                if not os.path.exists(audio_path):
                    print(f"❌ File not found: {audio_path}")
                    return
                audio_file = audio_path
            
            else:
                print("❌ Invalid option")
                return
            
            # Test STT
            print(f"\n🧪 Testing STT:")
            print(f"Language: {selected_lang}")
            print(f"Model: {selected_model or 'auto'}")
            print(f"Audio: {audio_file}")
            
            result = self.test_stt_with_file(audio_file, selected_lang, selected_model)
            
        except KeyboardInterrupt:
            print("\n❌ Test cancelled")
        except Exception as e:
            print(f"❌ Error in STT test: {e}")
    
    def interactive_tts_test(self):
        """Interactive TTS testing"""
        print("\n🔊 INTERACTIVE TTS TESTING")
        print("=" * 50)
        
        tts_languages = self.get_tts_languages()
        if not tts_languages:
            print("❌ No TTS languages available")
            return
        
        # Show available languages and models
        print("\n📋 Available TTS Languages and Models:")
        for i, (lang, models) in enumerate(tts_languages.items(), 1):
            print(f"{i:2d}. {lang.upper()}: {', '.join(models)}")
        
        try:
            # Select language
            lang_choice = input(f"\nSelect language (1-{len(tts_languages)}) or enter language code: ").strip()
            
            if lang_choice.isdigit():
                lang_idx = int(lang_choice) - 1
                if 0 <= lang_idx < len(tts_languages):
                    selected_lang = list(tts_languages.keys())[lang_idx]
                else:
                    print("❌ Invalid selection")
                    return
            else:
                selected_lang = lang_choice.lower()
                if selected_lang not in tts_languages:
                    print(f"❌ Language '{selected_lang}' not supported")
                    return
            
            # Select model
            available_models = tts_languages[selected_lang]
            print(f"\n📋 Available models for {selected_lang.upper()}:")
            for i, model in enumerate(available_models, 1):
                print(f"{i}. {model}")
            
            model_choice = input(f"Select model (1-{len(available_models)}) or press Enter for auto: ").strip()
            
            if model_choice.isdigit():
                model_idx = int(model_choice) - 1
                if 0 <= model_idx < len(available_models):
                    selected_model = available_models[model_idx]
                else:
                    selected_model = None
            else:
                selected_model = None
            
            # Get text to synthesize
            if selected_lang == "hi":
                default_text = "नमस्ते, मैं मंत्रपथ हूं। यह एक टेस्ट है।"
            elif selected_lang == "bn":
                default_text = "হ্যালো, আমি মন্ত্রপথ। এটি একটি পরীক্ষা।"
            elif selected_lang == "te":
                default_text = "హలో, నేను మంత్రపథ్. ఇది ఒక పరీక్ష."
            elif selected_lang == "ta":
                default_text = "வணக்கம், நான் மந்திரபாதை. இது ஒரு சோதனை."
            else:
                default_text = "Hello, I am MantraPath. This is a test of the text-to-speech system."
            
            text = input(f"Enter text to synthesize (or press Enter for default):\nDefault: {default_text}\nYour text: ").strip()
            if not text:
                text = default_text
            
            # Test TTS
            print(f"\n🧪 Testing TTS:")
            print(f"Language: {selected_lang}")
            print(f"Model: {selected_model or 'auto'}")
            
            audio_file = self.test_tts_synthesis(text, selected_lang, None, selected_model)
            
            if audio_file:
                play_choice = input("\n🎵 Play audio? (y/n): ").strip().lower()
                if play_choice == 'y':
                    self.play_audio(audio_file)
            
        except KeyboardInterrupt:
            print("\n❌ Test cancelled")
        except Exception as e:
            print(f"❌ Error in TTS test: {e}")
    
    def interactive_nlp_test(self):
        """Interactive NLP testing"""
        print("\n🧠 INTERACTIVE NLP TESTING")
        print("=" * 50)
        
        print("\n📋 Available NLP Tests:")
        print("1. Sentiment Analysis")
        print("2. Translation")
        print("3. Both")
        
        try:
            choice = input("Select test (1-3): ").strip()
            
            if choice in ["1", "3"]:
                # Sentiment Analysis
                print("\n😊 SENTIMENT ANALYSIS TEST")
                text = input("Enter text for sentiment analysis: ").strip()
                if text:
                    self.test_sentiment_analysis(text)
            
            if choice in ["2", "3"]:
                # Translation
                print("\n🌍 TRANSLATION TEST")
                text = input("Enter text to translate: ").strip()
                if not text:
                    print("❌ No text provided")
                    return
                
                source_lang = input("Source language (e.g., en, hi): ").strip().lower()
                target_lang = input("Target language (e.g., hi, en): ").strip().lower()
                
                if source_lang and target_lang:
                    self.test_translation(text, source_lang, target_lang)
            
        except KeyboardInterrupt:
            print("\n❌ Test cancelled")
        except Exception as e:
            print(f"❌ Error in NLP test: {e}")
    
    def play_audio(self, audio_file):
        """Play audio file"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", str(audio_file)])
            elif system == "Linux":
                subprocess.run(["aplay", str(audio_file)])
            elif system == "Windows":
                subprocess.run(["start", str(audio_file)], shell=True)
            else:
                print(f"❌ Cannot play audio on {system}")
                
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
    
    def run_interactive_menu(self):
        """Main interactive menu"""
        if not self.check_service_health():
            return
        
        while True:
            print("\n" + "=" * 60)
            print("🧪 MODELS SERVICE INTERACTIVE TESTING SUITE")
            print("=" * 60)
            
            self.get_service_status()
            
            print(f"\n📋 TEST OPTIONS:")
            print("1. 🎤 STT (Speech-to-Text) Testing")
            print("2. 🔊 TTS (Text-to-Speech) Testing")
            print("3. 🧠 NLP (Sentiment & Translation) Testing")
            print("4. 📊 Service Status")
            print("5. 🚪 Exit")
            
            try:
                choice = input(f"\nSelect option (1-5): ").strip()
                
                if choice == "1":
                    self.interactive_stt_test()
                elif choice == "2":
                    self.interactive_tts_test()
                elif choice == "3":
                    self.interactive_nlp_test()
                elif choice == "4":
                    self.get_service_status()
                elif choice == "5":
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
    print("🚀 Starting Models Service Testing Suite...")
    
    # Check dependencies
    try:
        import pyaudio
    except ImportError:
        print("❌ PyAudio not found. Install with: pip install pyaudio")
        return
    
    # Create tester and run
    tester = ModelsServiceTester()
    tester.run_interactive_menu()

if __name__ == "__main__":
    main()
