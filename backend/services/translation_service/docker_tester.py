#!/usr/bin/env python3
"""
MantraPath Translation Service Docker Tester
Interactive testing tool for the Docker-based translation service
"""
import requests
import json
import time
import sys
from typing import Dict, Optional, Any
import os

class DockerTranslationTester:
    def __init__(self, base_url: str = None):
        if base_url is None:
            base_url = os.getenv("TRANSLATION_SERVICE_URL", "http://translation-service:8010")
        self.base_url = base_url
        self.session_stats = {
            "total_tests": 0,
            "successful": 0,
            "failed": 0,
            "cache_hits": 0
        }
    
    def print_header(self):
        """Print application header"""
        print("\n" + "="*70)
        print("🌍 MantraPath Translation Service - Docker Tester 🌍")
        print("="*70)
        print("Testing Docker service at:", self.base_url)
    
    def check_service_health(self) -> bool:
        """Check if translation service is running and healthy"""
        try:
            print("\n🔍 Checking service health...")
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get('status', 'unknown')
                
                print(f"✅ Service Status: {status}")
                print(f"📊 Version: {health_data.get('version', 'unknown')}")
                print(f"⏱️  Uptime: {health_data.get('uptime_seconds', 0)} seconds")
                
                # Show engine status
                engines = health_data.get('engines_status', {})
                for engine, engine_status in engines.items():
                    emoji = "✅" if engine_status == "healthy" else "⚠️"
                    print(f"{emoji} Engine '{engine}': {engine_status}")
                
                # Show cache status
                cache_status = health_data.get('cache_status', 'unknown')
                cache_emoji = "✅" if cache_status == "healthy" else "⚠️"
                print(f"{cache_emoji} Cache: {cache_status}")
                
                return True
            else:
                print(f"❌ Service returned status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Service unavailable: {e}")
            print("Make sure Docker services are running:")
            print("cd backend && docker-compose up")
            return False
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get supported languages from the service"""
        try:
            response = requests.get(f"{self.base_url}/languages", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️  Could not fetch languages: {e}")
        
        # Fallback language info
        return {
            "supported_languages": {
                "hi": "Hindi", "ta": "Tamil", "bn": "Bengali", "te": "Telugu",
                "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
                "pa": "Punjabi", "or": "Odia", "as": "Assamese", "ne": "Nepali",
                "en": "English", "es": "Spanish", "fr": "French", "de": "German"
            }
        }
    
    def show_supported_languages(self):
        """Display supported languages"""
        print("\n📋 Supported Languages:")
        lang_data = self.get_supported_languages()
        languages = lang_data.get("supported_languages", {})
        
        print("\n🇮🇳 Indian Languages:")
        indian_langs = ["hi", "ta", "bn", "te", "mr", "gu", "kn", "ml", "pa", "or", "as", "ne"]
        for code in indian_langs:
            if code in languages:
                print(f"  {code:4} - {languages[code]}")
        
        print("\n🌍 International Languages:")
        international_langs = ["en", "es", "fr", "de", "ja", "zh"]
        for code in international_langs:
            if code in languages:
                print(f"  {code:4} - {languages[code]}")
    
    def detect_language(self, text: str) -> Optional[str]:
        """Auto-detect language of input text"""
        try:
            print("🔍 Detecting language...")
            response = requests.post(
                f"{self.base_url}/detect",
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                detected = result.get("detected_language", "unknown")
                confidence = result.get("confidence", 0.0)
                print(f"🎯 Detected: {detected} (confidence: {confidence:.2f})")
                return detected
            else:
                print(f"⚠️  Detection failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Detection error: {e}")
        
        return None
    
    def translate_text(self, text: str, source_lang: str = "auto", target_lang: str = "en") -> Dict:
        """Perform translation"""
        start_time = time.time()
        
        try:
            # Prepare payload
            payload = {
                "text": text,
                "target_language": target_lang
            }
            
            if source_lang != "auto":
                payload["source_language"] = source_lang
            
            print(f"🔄 Translating '{text[:50]}...' from {source_lang} to {target_lang}")
            
            response = requests.post(
                f"{self.base_url}/translate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                result["duration"] = duration
                
                # Check if this was a cache hit
                if "cached" in result.get("engine", "").lower():
                    self.session_stats["cache_hits"] += 1
                
                return result
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "duration": duration
                }
        
        except Exception as e:
            return {
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def display_result(self, result: Dict, original_text: str):
        """Display formatted translation result"""
        if "error" in result:
            print(f"\n❌ Translation Failed:")
            print(f"   Error: {result['error']}")
            print(f"   Duration: {result.get('duration', 0):.2f}s")
            self.session_stats["failed"] += 1
            return
        
        self.session_stats["successful"] += 1
        
        # Extract data
        translated = result.get("translated_text", "N/A")
        source = result.get("source_language", "unknown")
        target = result.get("target_language", "unknown")
        confidence = result.get("confidence_score", 0.0)
        engine = result.get("engine", "unknown")
        duration = result.get("duration", 0.0)
        
        # Check if cached
        cached_indicator = "🚀 CACHED" if "cached" in engine.lower() else "🔄 FRESH"
        
        print(f"\n{cached_indicator} Translation Result:")
        print("-" * 60)
        print(f"📝 Original ({source.upper()}): {original_text}")
        print(f"🎯 Translation ({target.upper()}): {translated}")
        print(f"⚙️  Engine: {engine}")
        print(f"📊 Confidence: {confidence:.2f}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print("-" * 60)
    
    def run_batch_test(self):
        """Run predefined batch tests"""
        test_cases = [
            {"text": "नमस्ते, आप कैसे हैं?", "source": "hi", "target": "en"},
            {"text": "Hello, how are you?", "source": "en", "target": "hi"},
            {"text": "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?", "source": "ta", "target": "en"},
            {"text": "Good morning", "source": "en", "target": "ta"},
            {"text": "আমি ভাল আছি", "source": "bn", "target": "en"},
        ]
        
        print(f"\n🧪 Running Batch Tests ({len(test_cases)} tests)...")
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n--- Test {i}/{len(test_cases)} ---")
            self.session_stats["total_tests"] += 1
            
            result = self.translate_text(
                test["text"], 
                test["source"], 
                test["target"]
            )
            self.display_result(result, test["text"])
            
            # Small delay between tests
            time.sleep(1)
    
    def run_interactive_mode(self):
        """Run interactive translation testing"""
        print("\n🚀 Interactive Mode Started!")
        print("Commands: 'batch' (run tests), 'stats' (show stats), 'help' (show help), 'quit' (exit)")
        
        while True:
            try:
                print(f"\n{'='*50}")
                text = input("Enter text to translate (or command): ").strip()
                
                if not text:
                    continue
                
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                
                if text.lower() == 'help':
                    self.show_help()
                    continue
                
                if text.lower() == 'stats':
                    self.show_stats()
                    continue
                
                if text.lower() == 'batch':
                    self.run_batch_test()
                    continue
                
                if text.lower() == 'langs':
                    self.show_supported_languages()
                    continue
                
                # Get language preferences
                source_lang = input("Source language (auto/hi/en/ta/etc): ").strip().lower()
                source_lang = source_lang if source_lang else "auto"
                
                target_lang = input("Target language (en/hi/ta/etc): ").strip().lower()
                target_lang = target_lang if target_lang else "en"
                
                # Perform translation
                self.session_stats["total_tests"] += 1
                result = self.translate_text(text, source_lang, target_lang)
                self.display_result(result, text)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_help(self):
        """Show help information"""
        print(f"\n📚 Help - Available Commands:")
        print("  batch  - Run predefined batch tests")
        print("  stats  - Show session statistics")
        print("  langs  - Show supported languages")
        print("  help   - Show this help")
        print("  quit   - Exit the tester")
        print(f"\n🌍 Language Codes:")
        print("  auto - Auto-detect source language")
        print("  hi   - Hindi       ta   - Tamil")
        print("  en   - English     bn   - Bengali")
        print("  es   - Spanish     te   - Telugu")
        print(f"\n💡 Example:")
        print("  Text: नमस्ते दुनिया")
        print("  Source: auto (or hi)")
        print("  Target: en")
        print("  Result: Hello world")
    
    def show_stats(self):
        """Display session statistics"""
        total = self.session_stats["total_tests"]
        if total == 0:
            print("\n📊 No tests run yet!")
            return
        
        success_rate = (self.session_stats["successful"] / total) * 100
        cache_rate = (self.session_stats["cache_hits"] / total) * 100 if total > 0 else 0
        
        print(f"\n📊 Session Statistics:")
        print(f"  Total Tests: {total}")
        print(f"  ✅ Successful: {self.session_stats['successful']}")
        print(f"  ❌ Failed: {self.session_stats['failed']}")
        print(f"  🚀 Cache Hits: {self.session_stats['cache_hits']}")
        print(f"  📈 Success Rate: {success_rate:.1f}%")
        print(f"  ⚡ Cache Hit Rate: {cache_rate:.1f}%")

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = os.getenv("TRANSLATION_SERVICE_URL", "http://translation-service:8010")
    
    tester = DockerTranslationTester(base_url)
    tester.print_header()
    
    if not tester.check_service_health():
        return
    
    tester.show_supported_languages()
    
    # Ask user for test mode
    print(f"\n🎯 Test Options:")
    print("1. Interactive Mode - Test any text manually")
    print("2. Batch Mode - Run predefined tests")
    print("3. Both - Run batch tests then interactive")
    
    try:
        choice = input("\nChoose option (1/2/3): ").strip()
        
        if choice == "2":
            tester.run_batch_test()
        elif choice == "3":
            tester.run_batch_test()
            tester.run_interactive_mode()
        else:
            tester.run_interactive_mode()
    
    except KeyboardInterrupt:
        pass
    
    print(f"\n👋 Final Statistics:")
    tester.show_stats()
    print("Thanks for testing MantraPath Translation Service!")

if __name__ == "__main__":
    main()
