#!/usr/bin/env python3
"""
Direct test of Coqui TTS library to verify installation and available models
"""

import sys
import traceback

def test_coqui_tts():
    """Test Coqui TTS library installation and functionality"""
    
    print("🧪 Testing Coqui TTS Library...")
    print("=" * 50)
    
    try:
        # Test basic import
        print("📦 Testing Coqui TTS import...")
        from TTS.api import TTS
        print("✅ Coqui TTS library imported successfully!")
        
        # List available models
        print("\n📋 Listing available models...")
        tts_instance = TTS()
        available_models = tts_instance.list_models()
        
        print(f"✅ Found available models (ModelManager object)")
        
        # Show TTS models specifically by iterating the manager
        print("\n🔊 Available TTS Models:")
        
        # Try to get tts models
        try:
            tts_models = []
            # Access the models differently
            if hasattr(available_models, 'list'):
                model_list = available_models.list
            elif hasattr(available_models, 'models'):
                model_list = available_models.models
            else:
                # Try direct iteration or other attributes
                model_list = []
                
            print(f"   Available model categories: {dir(available_models)}")
            
        except Exception as list_error:
            print(f"   Could not list models: {list_error}")
            
        # Test with a simple English model
        print("\n🔧 Testing model initialization...")
        try:
            # Try a basic English model that's commonly available
            test_model = "tts_models/en/ljspeech/tacotron2-DDC"
            print(f"   Initializing: {test_model}")
            tts_test = TTS(test_model)
            print("✅ Model initialization successful!")
            
            # Test text synthesis 
            print("   Testing text synthesis...")
            test_text = "Hello, this is a test of Coqui TTS."
            tts_test.tts_to_file(text=test_text, file_path="/tmp/test_coqui.wav")
            print("✅ Text synthesis successful!")
            
        except Exception as model_error:
            print(f"⚠️  Model test failed: {model_error}")
            print("   Trying alternative model...")
            
            # Try a different model
            try:
                print("   Trying: tts_models/en/vctk/vits")
                alt_tts = TTS("tts_models/en/vctk/vits")
                print("✅ Alternative model initialization successful!")
            except Exception as alt_error:
                print(f"   Alternative model also failed: {alt_error}")
        
        # Test Hindi models specifically
        print("\n🇮🇳 Testing Hindi model...")
        try:
            hindi_model = "tts_models/hi/male/fairseq"
            print(f"   Trying Hindi model: {hindi_model}")
            hindi_tts = TTS(hindi_model)
            print("✅ Hindi model initialization successful!")
        except Exception as hindi_error:
            print(f"⚠️  Hindi model failed: {hindi_error}")
            
            # Try alternative Hindi model names
            alternative_hindi = [
                "hi",
                "tts_models/hi/female/tacotron2",
                "tts_models/multilingual/multi-dataset/xtts_v2"
            ]
            
            for alt_model in alternative_hindi:
                try:
                    print(f"   Trying alternative Hindi model: {alt_model}")
                    alt_hindi_tts = TTS(alt_model)
                    print(f"✅ Alternative Hindi model successful: {alt_model}")
                    break
                except Exception as alt_hindi_error:
                    print(f"   Failed: {alt_hindi_error}")
            else:
                print("   No Hindi models could be initialized")
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import Coqui TTS: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Coqui TTS: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Coqui TTS Direct Test")
    print("=" * 50)
    
    success = test_coqui_tts()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Coqui TTS test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Coqui TTS test failed!")
        sys.exit(1)
