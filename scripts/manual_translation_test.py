#!/usr/bin/env python3
"""
Quick Manual Translation Testing Script
=====================================

Simple script for manual testing of the translation service during development.
Use this for quick validation of specific translations.

Usage:
    python manual_translation_test.py
    
Then follow the interactive prompts.
"""

import asyncio
import aiohttp

class QuickTranslationTester:
    def __init__(self, base_url: str = "http://localhost:8010"):
        self.base_url = base_url
    
    async def test_translation(self, text: str, target_lang: str, source_lang: str = "auto"):
        """Test a single translation"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang
            }
            
            try:
                async with session.post(f"{self.base_url}/translate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        print("\n" + "="*60)
                        print("TRANSLATION RESULT")
                        print("="*60)
                        print(f"Original Text: {text}")
                        print(f"Target Language: {target_lang}")
                        print(f"Detected Source: {data['source_language']}")
                        print(f"Translated Text: {data['translated_text']}")
                        print(f"Confidence: {data['confidence_score']}")
                        print(f"Engine: {data['engine']}")
                        print(f"Processing Time: {data.get('processing_time_ms', 0)}ms")
                        print(f"Cache Hit: {data.get('cache_hit', False)}")
                        print("="*60)
                        
                        return True
                    else:
                        print(f"❌ Translation failed with status {response.status}")
                        print(await response.text())
                        return False
            except Exception as e:
                print(f"❌ Error: {e}")
                return False
    
    async def get_supported_languages(self):
        """Get list of supported languages"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/languages") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        print("\n" + "="*60)
                        print("SUPPORTED LANGUAGES")
                        print("="*60)
                        print(f"Total Languages: {len(data['supported_languages'])}")
                        print(f"Indian Languages: {len(data['indian_languages'])}")
                        print("\nAll Supported Languages:")
                        for i, lang in enumerate(data['supported_languages']):
                            print(f"  {lang}", end="")
                            if (i + 1) % 8 == 0:  # New line every 8 languages
                                print()
                        print("\n" + "="*60)
                        
                        return data
                    else:
                        print(f"❌ Failed to get languages: {response.status}")
                        return None
            except Exception as e:
                print(f"❌ Error getting languages: {e}")
                return None

async def main():
    print("🧘‍♀️ MantraPath Translation Service - Manual Tester")
    print("="*55)
    
    tester = QuickTranslationTester()
    
    # Check if service is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{tester.base_url}/health") as response:
                if response.status != 200:
                    print("❌ Translation service is not running!")
                    print(f"   Make sure the service is running on {tester.base_url}")
                    return
                else:
                    print("✅ Translation service is running!")
    except Exception as e:
        print("❌ Cannot connect to translation service!")
        print(f"   Error: {e}")
        print(f"   Make sure the service is running on {tester.base_url}")
        return
    
    while True:
        print("\n" + "="*55)
        print("MANUAL TRANSLATION TESTING MENU")
        print("="*55)
        print("1. Test a translation")
        print("2. Show supported languages")
        print("3. Quick test examples")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\n--- Translation Test ---")
            text = input("Enter text to translate: ").strip()
            if not text:
                print("❌ Text cannot be empty!")
                continue
            
            target_lang = input("Enter target language code (e.g., hi, es, fr): ").strip().lower()
            if not target_lang:
                print("❌ Target language cannot be empty!")
                continue
            
            source_lang = input("Enter source language (or press Enter for auto-detection): ").strip().lower()
            if not source_lang:
                source_lang = "auto"
            
            await tester.test_translation(text, target_lang, source_lang)
        
        elif choice == "2":
            await tester.get_supported_languages()
        
        elif choice == "3":
            print("\n--- Quick Test Examples ---")
            examples = [
                ("Hello world", "hi", "en"),
                ("नमस्ते दुनिया", "en", "auto"),
                ("Hola mundo", "hi", "auto"),
                ("I am feeling happy today", "hi", "auto"),
                ("वॉलम अचन कस आहेत", "en", "auto"),  # Marathi
            ]
            
            for text, target, source in examples:
                print(f"\n🔄 Testing: '{text}' -> {target}")
                await tester.test_translation(text, target, source)
                
                choice = input("\nContinue to next example? (y/n): ").strip().lower()
                if choice != 'y':
                    break
        
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice! Please enter 1-4.")

if __name__ == "__main__":
    asyncio.run(main())
