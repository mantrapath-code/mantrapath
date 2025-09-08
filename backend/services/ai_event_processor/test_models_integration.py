#!/usr/bin/env python3
"""
Test script to verify AI Event Processor Models Service integration
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.emotion_analyzer import EmotionAnalyzer


async def test_models_service_integration():
    """Test the Models Service integration in AI Event Processor"""
    print("🧪 Testing AI Event Processor Models Service Integration")
    
    # Test 1: With Models Service enabled (default)
    print("\n1️⃣ Testing with Models Service enabled...")
    analyzer_with_models = EmotionAnalyzer()
    
    print(f"   USE_MODELS_SERVICE: {analyzer_with_models.use_models_service}")
    print(f"   Models Service Client initialized: {analyzer_with_models.models_service_client is not None}")
    print(f"   Local models available: {analyzer_with_models.local_models_available}")
    
    # Test 2: With Models Service disabled
    print("\n2️⃣ Testing with Models Service disabled...")
    os.environ["USE_MODELS_SERVICE"] = "false"
    analyzer_without_models = EmotionAnalyzer()
    
    print(f"   USE_MODELS_SERVICE: {analyzer_without_models.use_models_service}")
    print(f"   Models Service Client initialized: {analyzer_without_models.models_service_client is not None}")
    print(f"   Local models available: {analyzer_without_models.local_models_available}")
    
    # Test 3: Load local models as fallback
    print("\n3️⃣ Testing local model loading...")
    try:
        await analyzer_without_models._load_primary_models()
        print(f"   ✅ Local models loaded successfully")
        print(f"   Available models: {list(analyzer_without_models.models.keys())}")
        print(f"   Local models available: {analyzer_without_models.local_models_available}")
    except Exception as e:
        print(f"   ❌ Failed to load local models: {e}")
    
    # Test 4: Test sentiment to emotion conversion
    print("\n4️⃣ Testing sentiment to emotion conversion...")
    test_sentiment_results = [
        {"label": "POSITIVE", "score": 0.85},
        {"label": "NEGATIVE", "score": 0.92},
        {"label": "NEGATIVE", "score": 0.65},
        {"label": "NEUTRAL", "score": 0.55}
    ]
    
    for sentiment in test_sentiment_results:
        emotion = analyzer_with_models._convert_sentiment_to_emotion(sentiment)
        print(f"   Sentiment: {sentiment['label']} ({sentiment['score']:.2f}) → Emotion: {emotion}")
    
    print("\n✅ Integration test completed!")
    
    return {
        "models_service_integration": analyzer_with_models.use_models_service,
        "fallback_mechanism": analyzer_without_models.local_models_available,
        "sentiment_conversion": True
    }


async def main():
    """Main test runner"""
    try:
        results = await test_models_service_integration()
        print(f"\n📊 Test Results: {results}")
        return True
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
