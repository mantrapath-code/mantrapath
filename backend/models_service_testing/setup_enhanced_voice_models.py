#!/usr/bin/env python3
"""
Enhanced Voice Models Setup for Models Service
Downloads and configures Vosk (STT) + Coqui TTS (TTS) + Rasa (dialogue/context) + Hugging Face sentiment models
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Configuration
MODELS_SERVICE_URL = "http://localhost:8085"
MODELS_DIR = "/app/models" if os.path.exists("/app") else "./models"
DOWNLOAD_TIMEOUT = 300  # 5 minutes per model

# Essential models for Voice Service
VOICE_MODELS_CONFIG = {
    "stt_models": {
        "whisper_tiny": {
            "engine": "whisper",
            "size": "39MB",
            "description": "Fast STT for English/Hindi",
            "priority": 1
        },
        "vosk_en_us_small": {
            "engine": "vosk", 
            "size": "40MB",
            "description": "English STT",
            "priority": 2
        },
        "vosk_hi_small": {
            "engine": "vosk",
            "size": "45MB", 
            "description": "Hindi STT",
            "priority": 3
        }
    },
    "tts_models": {
        "coqui_hi": {
            "engine": "coqui",
            "size": "500MB",
            "description": "High-quality Hindi TTS",
            "priority": 1
        },
        "coqui_en": {
            "engine": "coqui",
            "size": "500MB",
            "description": "High-quality English TTS", 
            "priority": 2
        }
    },
    "nlp_models": {
        "sentiment_roberta": {
            "engine": "huggingface",
            "model_name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "size": "500MB",
            "description": "Sentiment analysis",
            "priority": 1
        },
        "emotion_bert": {
            "engine": "huggingface", 
            "model_name": "j-hartmann/emotion-english-distilroberta-base",
            "size": "250MB",
            "description": "Emotion detection",
            "priority": 2
        }
    },
    "dialogue_models": {
        "rasa_hindi": {
            "engine": "rasa",
            "size": "100MB",
            "description": "Hindi dialogue context",
            "priority": 1
        },
        "rasa_english": {
            "engine": "rasa",
            "size": "100MB", 
            "description": "English dialogue context",
            "priority": 2
        }
    }
}

def check_service_health():
    """Check if models service is running"""
    try:
        response = requests.get(f"{MODELS_SERVICE_URL}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def wait_for_service():
    """Wait for models service to be ready"""
    print("🔄 Waiting for Models Service to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        if check_service_health():
            print("✅ Models Service is ready!")
            return True
        print(f"   Attempt {attempt + 1}/{max_attempts} - Service not ready, waiting...")
        time.sleep(2)
    
    print("❌ Models Service failed to start after 60 seconds")
    return False

def get_current_models():
    """Get currently loaded models"""
    try:
        response = requests.get(f"{MODELS_SERVICE_URL}/api/v1/models/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"❌ Error getting model status: {e}")
        return None

def download_model(model_name, model_info):
    """Download a specific model"""
    print(f"\n🔄 Downloading {model_name} ({model_info['size']})...")
    print(f"   📝 {model_info['description']}")
    
    try:
        # Prepare download request
        download_data = {"model_name": model_name}
        
        # Add model-specific parameters
        if model_info['engine'] == 'huggingface':
            download_data['model_path'] = model_info['model_name']
        
        response = requests.post(
            f"{MODELS_SERVICE_URL}/api/v1/models/download",
            json=download_data,
            timeout=DOWNLOAD_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {model_name} downloaded successfully!")
            return True
        else:
            print(f"❌ Failed to download {model_name}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ Timeout downloading {model_name} (>{DOWNLOAD_TIMEOUT}s)")
        return False
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False

def load_model(model_name, engine):
    """Load a downloaded model"""
    print(f"🔄 Loading {model_name}...")
    
    try:
        response = requests.post(
            f"{MODELS_SERVICE_URL}/api/v1/models/load",
            json={"model_name": model_name, "engine": engine}
        )
        
        if response.status_code == 200:
            print(f"✅ {model_name} loaded successfully!")
            return True
        else:
            print(f"❌ Failed to load {model_name}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error loading {model_name}: {e}")
        return False

def setup_voice_models():
    """Main setup function for voice models"""
    print("🚀 Enhanced Voice Models Setup")
    print("=" * 50)
    
    # Wait for service
    if not wait_for_service():
        return False
    
    # Get current status
    print("\n📊 Checking current model status...")
    current_models = get_current_models()
    if current_models:
        print(f"   STT Models: {len(current_models.get('stt_models', []))}")
        print(f"   TTS Models: {len(current_models.get('tts_models', []))}")
        print(f"   NLP Models: {len(current_models.get('nlp_models', []))}")
    
    download_success = 0
    download_total = 0
    
    # Download models by priority
    print("\n🔽 Downloading Essential Models...")
    
    # STT Models
    print("\n📞 Speech-to-Text Models:")
    for model_name, model_info in sorted(VOICE_MODELS_CONFIG['stt_models'].items(), 
                                       key=lambda x: x[1]['priority']):
        download_total += 1
        if download_model(model_name, model_info):
            download_success += 1
            # Try to load immediately
            load_model(model_name, model_info['engine'])
    
    # TTS Models  
    print("\n🗣️ Text-to-Speech Models:")
    for model_name, model_info in sorted(VOICE_MODELS_CONFIG['tts_models'].items(),
                                       key=lambda x: x[1]['priority']):
        download_total += 1
        if download_model(model_name, model_info):
            download_success += 1
            load_model(model_name, model_info['engine'])
    
    # NLP Models
    print("\n🧠 Natural Language Processing Models:")
    for model_name, model_info in sorted(VOICE_MODELS_CONFIG['nlp_models'].items(),
                                       key=lambda x: x[1]['priority']):
        download_total += 1
        if download_model(model_name, model_info):
            download_success += 1
            load_model(model_name, model_info['engine'])
    
    # Dialogue Models
    print("\n💬 Dialogue Management Models:")
    for model_name, model_info in sorted(VOICE_MODELS_CONFIG['dialogue_models'].items(),
                                       key=lambda x: x[1]['priority']):
        download_total += 1
        if download_model(model_name, model_info):
            download_success += 1
            load_model(model_name, model_info['engine'])
    
    # Final status check
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    
    final_models = get_current_models()
    if final_models:
        stt_count = len(final_models.get('stt_models', []))
        tts_count = len(final_models.get('tts_models', []))
        nlp_count = len(final_models.get('nlp_models', []))
        
        print(f"✅ STT Models Loaded: {stt_count}")
        print(f"✅ TTS Models Loaded: {tts_count}")
        print(f"✅ NLP Models Loaded: {nlp_count}")
        print(f"📈 Download Success Rate: {download_success}/{download_total}")
        
        if stt_count > 0 and tts_count > 0:
            print("\n🎉 Voice Service Ready!")
            print("   ✅ Speech Recognition Available")
            print("   ✅ Text-to-Speech Available") 
            if nlp_count > 0:
                print("   ✅ AI Context/Sentiment Available")
            
            return True
        else:
            print("\n⚠️ Voice Service Partially Ready")
            print("   Some essential models failed to download")
            return False
    else:
        print("❌ Failed to get final model status")
        return False

def test_voice_capabilities():
    """Test the downloaded voice models"""
    print("\n🧪 Testing Voice Capabilities...")
    
    # Test TTS
    try:
        response = requests.post(
            f"{MODELS_SERVICE_URL}/api/v1/tts/synthesize",
            json={
                "text": "नमस्ते, यह एक परीक्षण है",
                "language": "hi",
                "engine": "coqui"
            }
        )
        if response.status_code == 200:
            print("✅ Hindi TTS working!")
        else:
            print("❌ Hindi TTS failed")
    except Exception as e:
        print(f"❌ TTS test error: {e}")
    
    # Test Sentiment
    try:
        response = requests.post(
            f"{MODELS_SERVICE_URL}/api/v1/nlp/sentiment",
            json={"text": "I am very happy today!"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sentiment Analysis: {result}")
        else:
            print("❌ Sentiment analysis failed")
    except Exception as e:
        print(f"❌ Sentiment test error: {e}")

if __name__ == "__main__":
    print("🎯 Voice Service Models Setup")
    print("   Models: Vosk (STT) + Coqui TTS + Rasa + HuggingFace")
    print("   Purpose: Robust foundation for Voice Service")
    
    success = setup_voice_models()
    
    if success:
        test_voice_capabilities()
        print("\n✅ Setup Complete! Voice Service can now be developed.")
    else:
        print("\n❌ Setup had issues. Check the Models Service configuration.")
        sys.exit(1)
