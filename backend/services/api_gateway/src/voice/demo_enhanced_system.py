"""
Enhanced Voice System Demo Script
Demonstrates the real language processing capabilities
"""

import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_enhanced_voice_system():
    """Demonstrate the enhanced voice system capabilities"""
    
    print("🎤 Enhanced MantraPath Voice System Demo")
    print("=" * 50)
    
    # Import our enhanced components (using relative imports for demo)
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    
    from voice.language_support import MultilingualVoiceSupport
    from voice.classifier import VoiceIntentClassifier
    from voice.router import VoiceCommandRouter
    
    # Initialize components
    print("📦 Initializing enhanced voice components...")
    ml_support = MultilingualVoiceSupport()
    classifier = VoiceIntentClassifier()
    router = VoiceCommandRouter(classifier)
    
    print(f"✅ Loaded {len(ml_support.supported_languages)} languages")
    print(f"✅ Configured {len(router.routing_rules)} routing rules")
    
    # Demo real language detection
    print("\n🔍 Testing Enhanced Language Detection:")
    test_texts = [
        ("मैं आज बहुत खुश हूँ", "Hindi mood expression"),
        ("আমি আজ খুব খুশি", "Bengali mood expression"),
        ("நான் இன்று மகிழ்ச்சியாக இருக்கிறேன்", "Tamil mood expression"),
        ("నేను ఈరోజు చాలా సంతోషంగా ఉన్నాను", "Telugu mood expression"),
        ("I'm feeling great about my journal today", "English journal intent"),
        ("Je me sens heureux aujourd'hui", "French mood expression"),
    ]
    
    for text, description in test_texts:
        try:
            detected_lang = await ml_support.detect_language(text)
            cultural_context = ml_support.get_cultural_context(detected_lang)
            
            print(f"  📝 {description}")
            print(f"     Text: {text}")
            print(f"     Detected: {detected_lang} ({cultural_context})")
            
            # Test intent classification
            command = classifier.classify_intent(text, detected_lang)
            print(f"     Intent: {command.intent.value} (confidence: {command.confidence:.2f})")
            
            # Test routing
            routing_result = router.route_voice_command(text, detected_lang, "demo_user", cultural_context)
            if routing_result.success:
                print(f"     Route: {routing_result.target_service} -> {routing_result.endpoint}")
            else:
                print(f"     Route: Failed - {routing_result.error_message}")
            
            print()
        except Exception as e:
            print(f"     ❌ Error: {e}")
            print()
    
    # Demo Indian regional language capabilities
    print("🇮🇳 Indian Regional Language Support:")
    indian_langs = ml_support.get_supported_languages_by_level("primary")
    indian_count = sum(1 for lang in indian_langs if lang.cultural_context == "indian_subcontinent")
    print(f"   Primary Indian languages: {indian_count}")
    
    for lang in indian_langs:
        if lang.cultural_context == "indian_subcontinent":
            examples = ml_support.get_voice_examples_for_language(lang.code.value)
            print(f"   • {lang.name} ({lang.code.value}): {len(examples)} voice patterns")
    
    # Demo cultural adaptations
    print("\n🌍 Cultural Context Adaptations:")
    indian_region = ml_support.get_regional_adaptations("indian_subcontinent")
    if indian_region:
        print(f"   Indian Subcontinent:")
        print(f"   • Communication Style: {indian_region.communication_style}")
        print(f"   • Script Systems: {', '.join(indian_region.script_systems)}")
        print(f"   • Cultural Values: {len(indian_region.cultural_values)} dimensions")
    
    # Demo performance statistics
    print("\n📊 System Statistics:")
    stats = ml_support.get_language_statistics()
    routing_stats = router.get_routing_statistics()
    
    print(f"   Languages: {stats['total_languages']}")
    print(f"   Indian Regional: {stats['indian_regional_languages']}")
    print(f"   Script Systems: {len(stats['by_script_system'])}")
    print(f"   Routing Success Rate: {routing_stats['success_rate_percent']:.1f}%")
    
    # Demo voice validation
    print("\n✅ Voice Input Validation:")
    validation_tests = [
        ("मैं खुश हूँ", "hi", "Good Hindi input"),
        ("", "en", "Empty input test"),
        ("xyz", "hi", "Invalid Hindi input"),
    ]
    
    for text, expected_lang, description in validation_tests:
        try:
            validation = await ml_support.validate_voice_input(text, expected_lang)
            status = "✅ Valid" if validation["is_valid"] else "❌ Invalid"
            print(f"   {description}: {status}")
            if validation["issues"]:
                for issue in validation["issues"]:
                    print(f"     Issue: {issue}")
        except Exception as e:
            print(f"   {description}: ❌ Error - {e}")
    
    print("\n🎯 Enhanced Voice System Demo Complete!")
    print("   Key Improvements:")
    print("   • Real language detection via translation service")
    print("   • Comprehensive Indian regional language support")
    print("   • Enhanced cultural context awareness")
    print("   • Intelligent fallback mechanisms")
    print("   • Voice input validation")
    print("   • Performance monitoring")


if __name__ == "__main__":
    asyncio.run(demo_enhanced_voice_system())
