#!/usr/bin/env python3
"""
Automated Models Service Demo
Demonstrates key capabilities without user interaction
"""

import requests
import json
from pathlib import Path
from datetime import datetime

def demo_models_service():
    """Run automated demo of Models Service"""
    base_url = "http://localhost:8085"
    test_dir = Path(__file__).parent / "demo_outputs"
    test_dir.mkdir(exist_ok=True)
    
    print("🚀 MODELS SERVICE AUTOMATED DEMO")
    print("=" * 50)
    
    # Check health
    print("\n1. 🔍 Checking Service Health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Service is healthy")
        else:
            print("   ❌ Service unhealthy")
            return
    except:
        print("   ❌ Cannot connect to service")
        return
    
    # Get status
    print("\n2. 📊 Getting Service Status...")
    try:
        response = requests.get(f"{base_url}/status")
        status = response.json()
        print(f"   📱 STT Models Loaded: {status['models']['stt_loaded']}")
        print(f"   🔊 TTS Models Loaded: {status['models']['tts_loaded']}")
        print(f"   🧠 NLP Models Loaded: {status['models']['nlp_loaded']}")
        print(f"   🌍 STT Languages: {len(status['supported_languages']['stt'])}")
        print(f"   🌍 TTS Languages: {len(status['supported_languages']['tts'])}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test TTS with different languages
    print("\n3. 🔊 Testing TTS for Key Languages...")
    test_cases = [
        ("en", "espeak_en", "Hello, I am MantraPath. This is a demonstration."),
        ("hi", "espeak_hi", "नमस्ते, मैं मंत्रपथ हूं। यह एक प्रदर्शन है।"),
        ("bn", "espeak_bn", "হ্যালো, আমি মন্ত্রপথ। এটি একটি প্রদর্শনী।"),
        ("te", "espeak_te", "హలో, నేను మంత్రపథ్. ఇది ఒక ప్రదర్శన."),
        ("ta", "espeak_ta", "வணக்கம், நான் மந்திரபாதை. இது ஒரு ஆர்ப்பாட்டம்.")
    ]
    
    for lang, model, text in test_cases:
        print(f"\n   🌍 Testing {lang.upper()} with {model}...")
        try:
            payload = {
                "text": text,
                "language": lang,
                "model_preference": model
            }
            
            response = requests.post(
                f"{base_url}/api/v1/tts/synthesize",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%H%M%S")
                filename = test_dir / f"demo_{lang}_{model}_{timestamp}.wav"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                duration = response.headers.get('x-duration', 'Unknown')
                print(f"   ✅ Success! Duration: {duration}s")
                print(f"   💾 Saved: {filename.name}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test sentiment analysis
    print("\n4. 😊 Testing Sentiment Analysis...")
    sentiment_tests = [
        "I love this service! It's amazing!",
        "This is terrible and doesn't work.",
        "It's okay, nothing special really.",
        "Absolutely fantastic! Best ever!"
    ]
    
    for text in sentiment_tests:
        try:
            payload = {"text": text, "language": "en"}
            response = requests.post(
                f"{base_url}/api/v1/nlp/sentiment",
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                result = response.json()
                sentiment = result.get('sentiment', 'N/A')
                confidence = result.get('confidence', 'N/A')
                print(f"   📝 '{text[:30]}...' → {sentiment} ({confidence})")
            else:
                print(f"   ❌ Failed for: {text[:30]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test translation
    print("\n5. 🌍 Testing Translation...")
    translation_tests = [
        ("Hello, how are you?", "en", "hi"),
        ("Thank you very much", "en", "bn"),
        ("Good morning", "en", "te"),
        ("Welcome to MantraPath", "en", "ta")
    ]
    
    for text, source, target in translation_tests:
        try:
            payload = {
                "text": text,
                "source_lang": source,
                "target_lang": target
            }
            
            response = requests.post(
                f"{base_url}/api/v1/nlp/translate",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                translated = result.get('translated_text', 'N/A')
                confidence = result.get('confidence', 'N/A')
                print(f"   📝 {source}→{target}: '{text}' → '{translated[:50]}...' ({confidence})")
            else:
                print(f"   ❌ Failed: {source}→{target}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n✅ DEMO COMPLETE!")
    print(f"📁 Audio files saved in: {test_dir}")
    print(f"🎵 Play the .wav files to hear TTS output")
    print(f"💡 Run 'python3 simple_tester.py' for interactive testing")

if __name__ == "__main__":
    demo_models_service()
