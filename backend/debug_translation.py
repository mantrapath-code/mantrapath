#!/usr/bin/env python3
"""
Debug translation issue in chatbot service
"""
import requests
import json

def debug_translation():
    """Debug the translation flow"""
    
    print("🔍 Debugging Translation Issue...")
    
    # Test translation service directly
    print("\n1. Testing Translation Service Directly:")
    translation_payload = {
        "text": "Hi Friend, i notice you are having some challenges today",
        "source_language": "en",
        "target_language": "hi"
    }
    
    translation_response = requests.post(
        "http://localhost:8010/translate",
        json=translation_payload
    )
    
    if translation_response.status_code == 200:
        trans_data = translation_response.json()
        print(f"✅ Direct Translation Test:")
        print(f"   Original: {translation_payload['text']}")
        print(f"   Translated: {trans_data['translated_text']}")
        print(f"   Engine: {trans_data['engine']}")
        print(f"   Confidence: {trans_data['confidence_score']}")
        
        # Check if translated text is different
        original_text = translation_payload['text']
        translated_text = trans_data['translated_text']
        
        # Clean up the translation (remove [BHASHINI_DATA] prefix)
        if "[BHASHINI_DATA]" in translated_text:
            cleaned_translation = translated_text.replace("[BHASHINI_DATA]", "").strip()
        else:
            cleaned_translation = translated_text
            
        print(f"   Cleaned Translation: {cleaned_translation}")
        print(f"   Is Different from Original? {cleaned_translation != original_text}")
        
        if cleaned_translation == original_text:
            print("⚠️  Issue: Translation service is returning the same text!")
            print("   This means the translation engine isn't actually translating")
        else:
            print("✅ Translation service is working correctly")
            
    else:
        print(f"❌ Translation service error: {translation_response.status_code}")
        print(f"   Response: {translation_response.text}")
    
    # Test with a simpler, more translatable text
    print("\n2. Testing with Simple Text:")
    simple_payload = {
        "text": "Hello, how are you?",
        "source_language": "en", 
        "target_language": "hi"
    }
    
    simple_response = requests.post(
        "http://localhost:8010/translate",
        json=simple_payload
    )
    
    if simple_response.status_code == 200:
        simple_data = simple_response.json()
        print(f"✅ Simple Text Translation:")
        print(f"   Original: {simple_payload['text']}")
        print(f"   Translated: {simple_data['translated_text']}")
        
        if "[BHASHINI_DATA]" in simple_data['translated_text']:
            cleaned = simple_data['translated_text'].replace("[BHASHINI_DATA]", "").strip()
            print(f"   Cleaned: {cleaned}")
            
            if cleaned != simple_payload['text']:
                print("✅ Simple translation works!")
            else:
                print("⚠️  Simple translation also returns same text")
    
    print("\n3. Testing Language Detection:")
    detect_payload = {"text": "मैं आज बहुत खुश हूं"}
    detect_response = requests.post(
        "http://localhost:8010/detect-language",
        json=detect_payload
    )
    
    if detect_response.status_code == 200:
        detect_data = detect_response.json()
        print(f"✅ Language Detection:")
        print(f"   Text: {detect_payload['text']}")
        print(f"   Detected: {detect_data['language']}")
        print(f"   Confidence: {detect_data['confidence']}")

if __name__ == "__main__":
    debug_translation()
