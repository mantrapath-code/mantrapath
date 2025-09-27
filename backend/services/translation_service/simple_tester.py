#!/usr/bin/env python3
"""
Interactive Translation Testing Tool
Test any language pair supported by the translation service

Usage: python simple_tester.py
"""
import json
import os
import sys
import requests

# Service configuration
# Prefer environment variable so this script works both inside and outside Docker.
# Default now points to the docker-compose service DNS name instead of localhost.
SERVICE_URL = os.getenv("TRANSLATION_SERVICE_URL", "http://translation-service:8010")

class TranslationTester:
    def __init__(self):
        self.supported_languages = {
            # Indian Languages (primary - via Bhashini/Anuvadini)
            'hi': 'Hindi (हिन्दी)',
            'bn': 'Bengali (বাংলা)', 
            'te': 'Telugu (తెలుగు)',
            'mr': 'Marathi (मराठी)',
            'ta': 'Tamil (தமிழ்)',
            'gu': 'Gujarati (ગુજરાતી)',
            'kn': 'Kannada (ಕನ್ನಡ)',
            'ml': 'Malayalam (മലയാളം)',
            'pa': 'Punjabi (ਪੰਜਾਬੀ)',
            'or': 'Odia (ଓଡ଼ିଆ)',
            'as': 'Assamese (অসমীয়া)',
            'ur': 'Urdu (اردو)',
            'sd': 'Sindhi (سنڌي)',
            'ne': 'Nepali (नेपाली)',
            'si': 'Sinhala (සිංහල)',
            'my': 'Myanmar (မြန်မာ)',
            'mni': 'Manipuri (ꯃꯩꯇꯩꯂꯣꯟ)',
            'sat': 'Santali (ᱥᱟᱱᱛᱟᱲᱤ)',
            'gom': 'Konkani (कोंकणी)',
            'mai': 'Maithili (मैथिली)',
            'brx': 'Bodo (बड़ो)',
            'doi': 'Dogri (डोगरी)',
            
            # Common International Languages  
            'en': 'English',
            'es': 'Spanish (Español)',
            'fr': 'French (Français)',
            'de': 'German (Deutsch)',
            'it': 'Italian (Italiano)',
            'pt': 'Portuguese (Português)',
            'ru': 'Russian (Русский)',
            'ja': 'Japanese (日本語)',
            'ko': 'Korean (한국어)',
            'zh': 'Chinese (中文)',
            'ar': 'Arabic (العربية)',
        }

    def display_banner(self):
        """Display welcome banner"""
        print("\n" + "="*60)
        print("🌐 MANTRAPATH TRANSLATION SERVICE TESTER")
        print("   Interactive Language Translation Testing Tool")
        print("="*60)
        print("🚀 Features:")
        print("   • Auto language detection")
        print("   • 22+ Indian languages via Bhashini/Anuvadini")
        print("   • International language support") 
        print("   • Real-time translation with caching")
        print("   • Performance metrics")
        print("="*60)

    def display_languages(self):
        """Display supported languages"""
        print("\n📋 SUPPORTED LANGUAGES:")
        print("-" * 40)
        
        # Indian Languages
        print("\n🇮🇳 Indian Languages (Primary - Bhashini):")
        indian_langs = [(k, v) for k, v in self.supported_languages.items() 
                       if k in ['hi', 'bn', 'te', 'mr', 'ta', 'gu', 'kn', 'ml', 'pa', 'or', 'as', 'ur', 'sd', 'ne', 'si', 'my', 'mni', 'sat', 'gom', 'mai', 'brx', 'doi']]
        
        for i, (code, name) in enumerate(indian_langs, 1):
            print(f"   {i:2d}. {code} - {name}")
        
        # International Languages
        print("\n🌍 International Languages:")
        intl_langs = [(k, v) for k, v in self.supported_languages.items() 
                     if k in ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']]
        
        for i, (code, name) in enumerate(intl_langs, 1):
            print(f"   {i:2d}. {code} - {name}")

    def get_user_input(self):
        """Get translation request from user"""
        print("\n" + "-"*50)
        print("📝 TRANSLATION REQUEST")
        print("-"*50)
        
        # Get text to translate
        text = input("\n🔤 Enter text to translate: ").strip()
        if not text:
            print("❌ Empty text! Please try again.")
            return {}
        
        # Get source language (auto-detect option)
        print("\n🔍 Source Language:")
        print("   • Press ENTER for auto-detection")
        print("   • Or enter language code (e.g., 'hi', 'en', 'ta')")
        source = input("   Source language [auto]: ").strip().lower()
        if not source:
            source = "auto"
        
        # Get target language
        print(f"\n🎯 Target Language:")
        print("   • Enter language code (e.g., 'en', 'hi', 'ta')")
        target = input("   Target language: ").strip().lower()
        if not target:
            print("❌ Target language required! Please try again.")
            return {}
        
        return {
            "text": text,
            "source_lang": source,
            "target_lang": target
        }

    def test_translation(self, text, source_lang, target_lang):
        """Test translation with the service"""
        print(f"\n⚡ TRANSLATING...")
        print(f"   📤 From: {source_lang} → 📥 To: {target_lang}")
        print("-"*50)
        
        try:
            # Prepare request payload
            payload = {
                "text": text,
                "target_language": target_lang
            }
            
            # Add source language if not auto
            if source_lang != "auto":
                payload["source_language"] = source_lang
            
            # Make API request
            response = requests.post(f"{SERVICE_URL}/translate", json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                self.display_translation_result(result)
            else:
                print(f"❌ Translation failed ({response.status_code}): {response.text}")
                        
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to translation service at {SERVICE_URL}")
            print("   Please make sure the service is running on port 8005")
        except Exception as e:
            print(f"❌ Error: {e}")

    def display_translation_result(self, result):
        """Display translation results"""
        print("✅ TRANSLATION SUCCESSFUL!")
        print("="*50)
        
        # Main translation result
        print(f"📝 Original:  {result.get('original_text', 'N/A')}")
        print(f"🔤 Translated: {result.get('translated_text', 'N/A')}")
        
        # Language information
        detected_lang = result.get('detected_language', 'Unknown')
        source_lang = result.get('source_language', 'Unknown')
        target_lang = result.get('target_language', 'Unknown')
        
        print(f"\n🔍 Languages:")
        if detected_lang != source_lang:
            print(f"   • Detected: {detected_lang} ({self.supported_languages.get(detected_lang, 'Unknown')})")
        print(f"   • Source: {source_lang} ({self.supported_languages.get(source_lang, 'Unknown')})")
        print(f"   • Target: {target_lang} ({self.supported_languages.get(target_lang, 'Unknown')})")
        
        # Engine and performance info
        engine = result.get('engine', 'Unknown')
        confidence = result.get('confidence_score', 0)
        
        print(f"\n⚙️  Translation Engine: {engine}")
        print(f"📊 Confidence Score: {confidence:.2f}")
        
        # Cache info if available
        if 'cached' in engine.lower():
            print("🚀 Result served from cache (super fast!)")

    def run_interactive_session(self):
        """Run interactive testing session"""
        self.display_banner()
        
        while True:
            print("\n" + "="*60)
            print("🎮 INTERACTIVE MENU")
            print("="*60)
            print("1. 📋 Show supported languages")
            print("2. 🔤 Test translation")  
            print("3. 🚀 Test service health")
            print("4. ❌ Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == "1":
                self.display_languages()
                
            elif choice == "2":
                request = self.get_user_input()
                if request:
                    self.test_translation(
                        request["text"],
                        request["source_lang"], 
                        request["target_lang"]
                    )
                    
            elif choice == "3":
                self.test_service_health()
                
            elif choice == "4":
                print("\n👋 Thank you for using MantraPath Translation Tester!")
                print("   🌟 Keep exploring multilingual capabilities!")
                break
                
            else:
                print("❌ Invalid choice! Please select 1-4.")

    def test_service_health(self):
        """Test service health"""
        print("\n🔍 CHECKING SERVICE HEALTH...")
        print("-"*40)
        
        try:
            response = requests.get(f"{SERVICE_URL}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                print("✅ Service is healthy!")
                print(f"   • Status: {health.get('status', 'Unknown')}")
                print(f"   • Version: {health.get('version', 'Unknown')}")
                print(f"   • Timestamp: {health.get('timestamp', 'Unknown')}")
            else:
                print(f"⚠️  Service health check failed ({response.status_code})")
                        
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to service at {SERVICE_URL}")
        except Exception as e:
            print(f"❌ Health check error: {e}")

# Quick test examples
def run_quick_tests():
    """Run some quick test examples"""
    tester = TranslationTester()
    
    print("\n🚀 RUNNING QUICK TESTS...")
    print("="*50)
    
    test_cases = [
        {"text": "Hello, how are you?", "source": "en", "target": "hi"},
        {"text": "मैं खुश हूं", "source": "hi", "target": "en"},
        {"text": "ধন্যবাদ", "source": "auto", "target": "en"},
        {"text": "Welcome to India", "source": "en", "target": "ta"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test['text']}")
        tester.test_translation(test["text"], test["source"], test["target"])
        print("Waiting 2 seconds...")
        import time
        time.sleep(2)  # Brief pause between tests

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_tests()
    else:
        tester = TranslationTester()
        tester.run_interactive_session()

if __name__ == "__main__":
    main()
