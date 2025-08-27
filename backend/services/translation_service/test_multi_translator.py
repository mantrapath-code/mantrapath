#!/usr/bin/env python3
"""
Test script for Enhanced Multi-Translator System
Tests Google Translate, Argos Translate, and Indic Translator integration
"""
import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from engines.enhanced_multi_translator import EnhancedMultiTranslator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_translation_engine():
    """Test the enhanced multi-translator"""
    print("🚀 Testing Enhanced Multi-Translator System")
    print("=" * 50)
    
    # Initialize the translator
    translator = EnhancedMultiTranslator()
    
    # Test initialization
    print("\n1. Testing Initialization...")
    init_result = await translator.initialize()
    print(f"   Initialization: {'✅ Success' if init_result else '❌ Failed'}")
    
    # Test health check
    print("\n2. Testing Health Check...")
    health = await translator.health_check()
    print(f"   Overall Status: {health.get('status', 'unknown')}")
    print(f"   Engines Available: {list(health.get('engines', {}).keys())}")
    
    for engine_name, engine_health in health.get('engines', {}).items():
        status = engine_health.get('status', 'unknown')
        print(f"   - {engine_name}: {status}")
    
    # Test language detection
    print("\n3. Testing Language Detection...")
    test_texts = [
        "Hello, how are you?",
        "नमस्ते, आप कैसे हैं?",  # Hindi
        "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?",  # Tamil
        "হ্যালো, আপনি কেমন আছেন?"  # Bengali
    ]
    
    for text in test_texts:
        try:
            detection = await translator.detect_language(text)
            print(f"   Text: '{text[:30]}...'")
            print(f"   Detected: {detection.get('language')} (confidence: {detection.get('confidence'):.2f})")
        except Exception as e:
            print(f"   Text: '{text[:30]}...' - Error: {str(e)}")
    
    # Test translations
    print("\n4. Testing Translations...")
    test_cases = [
        {
            "text": "Hello, welcome to MantraPath!",
            "source": "en",
            "target": "hi",
            "description": "English to Hindi"
        },
        {
            "text": "Thank you for using our service",
            "source": "en", 
            "target": "ta",
            "description": "English to Tamil"
        },
        {
            "text": "Good morning",
            "source": "en",
            "target": "bn", 
            "description": "English to Bengali"
        },
        {
            "text": "नमस्ते",
            "source": "hi",
            "target": "en",
            "description": "Hindi to English"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['description']}")
        print(f"   Input: '{test_case['text']}'")
        
        try:
            result = await translator.translate(
                text=test_case['text'],
                target_language=test_case['target'],
                source_language=test_case['source']
            )
            
            print(f"   Output: '{result.get('translated_text', 'N/A')}'")
            print(f"   Engine: {result.get('engine', 'unknown')}")
            print(f"   Confidence: {result.get('confidence_score', 0):.2f}")
            print(f"   Time: {result.get('processing_time_ms', 0):.1f}ms")
            
            if 'engines_used' in result:
                print(f"   Engines Used: {result['engines_used']}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    # Test batch translation
    print("\n5. Testing Batch Translation...")
    batch_requests = [
        {
            'text': 'Good morning',
            'target_language': 'hi',
            'source_language': 'en'
        },
        {
            'text': 'Good evening', 
            'target_language': 'hi',
            'source_language': 'en'
        },
        {
            'text': 'Thank you',
            'target_language': 'ta',
            'source_language': 'en'
        }
    ]
    
    try:
        batch_results = await translator.translate_batch(batch_requests, max_concurrent=2)
        print(f"   Batch Results: {len(batch_results)} translations")
        
        for i, result in enumerate(batch_results):
            if result.get('status') == 'success':
                print(f"   {i+1}. '{result.get('translated_text', 'N/A')}' ({result.get('engine', 'unknown')})")
            else:
                print(f"   {i+1}. Error: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"   ❌ Batch Error: {str(e)}")
    
    # Test supported languages
    print("\n6. Getting Supported Languages...")
    try:
        languages = await translator.get_supported_languages()
        print(f"   Total Supported: {len(languages.get('all_supported', []))}")
        print(f"   Indian Languages: {len(languages.get('indian_languages', []))}")
        
        print("   By Engine:")
        for engine, langs in languages.get('by_engine', {}).items():
            print(f"   - {engine}: {len(langs)} languages")
            
    except Exception as e:
        print(f"   ❌ Error getting languages: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Multi-Translator Test Complete!")

async def main():
    """Main test function"""
    try:
        await test_translation_engine()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
