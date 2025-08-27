# Multilingual Language Support

## Overview

The MantraPath Voice Service provides comprehensive multilingual support across 16 languages, organized into tiered support levels that align with the Translation Service capabilities. This document details the language architecture, cultural adaptations, and technical implementation of multilingual voice processing.

## 🌍 Language Architecture

### Tiered Support System

The Voice Service implements a two-tier language support system:

```python
LANGUAGE_TIERS = {
    "tier_1": {
        "name": "Premium Support",
        "description": "Native models with cultural adaptation, meditation optimization",
        "languages": 10,
        "features": [
            "Advanced emotion detection",
            "Cultural voice adaptation", 
            "Meditation-specific vocabulary",
            "Premium voice quality",
            "Multiple engine support",
            "Real-time processing"
        ]
    },
    "tier_2": {
        "name": "Standard Support", 
        "description": "High-quality translation and voice processing",
        "languages": 6,
        "features": [
            "Standard emotion detection",
            "High-quality voice synthesis",
            "Multiple engine support",
            "Real-time processing"
        ]
    }
}
```

## 📋 Supported Languages

### Tier 1 - Premium Support (10 Languages)

| Language | Native | RTL | Voice Models | STT Engines | TTS Engines | Special Features |
|----------|--------|-----|--------------|-------------|-------------|------------------|
| **English** | English | No | neural, standard, premium | whisper, google, azure | elevenlabs, azure, google | Cultural variations |
| **Hindi** | हिन्दी | No | neural, standard | whisper, google | google, azure | Sanskrit integration |
| **Spanish** | Español | No | neural, standard, premium | whisper, google, azure | elevenlabs, azure, google | Regional dialects |
| **French** | Français | No | neural, standard | whisper, google, azure | azure, google | European focus |
| **Arabic** | العربية | Yes | neural, standard | whisper, google | azure, google | RTL support |
| **Chinese** | 中文 | No | neural, standard | whisper, google | azure, google | Mandarin/Cantonese |
| **Japanese** | 日本語 | No | neural, standard | whisper, google | azure, google | Honorific awareness |
| **Sanskrit** | संस्कृतम् | No | standard | whisper | google | Mantra optimization |
| **Thai** | ไทย | No | neural, standard | whisper, google | google | Buddhist meditation |
| **Myanmar** | မြန်မာ | No | standard | whisper | google | Buddhist tradition |

### Tier 2 - Standard Support (6 Languages)

| Language | Native | RTL | Voice Models | STT Engines | TTS Engines |
|----------|--------|-----|--------------|-------------|-------------|
| **German** | Deutsch | No | neural, standard | whisper, google | azure, google |
| **Italian** | Italiano | No | neural, standard | whisper, google | azure, google |
| **Portuguese** | Português | No | neural, standard | whisper, google | azure, google |
| **Russian** | Русский | No | neural, standard | whisper, google | azure, google |
| **Korean** | 한국어 | No | neural, standard | whisper, google | azure, google |
| **Dutch** | Nederlands | No | standard | whisper, google | azure, google |

## 🎯 Engine Selection Strategy

### Priority-Based Engine Selection
```python
ENGINE_PRIORITIES = {
    "stt": {
        "tier_1": ["whisper", "google", "azure"],
        "tier_2": ["whisper", "google"]
    },
    "tts": {
        "tier_1": ["elevenlabs", "azure", "google"],
        "tier_2": ["azure", "google"]
    }
}

class LanguageEngineSelector:
    """Intelligent engine selection based on language capabilities"""
    
    async def select_best_engine(self, language: str, engine_type: str, requirements: dict) -> str:
        """Select optimal engine for language and requirements"""
        lang_info = get_language_info(language)
        available_engines = lang_info.get(f"{engine_type}_engines", [])
        priorities = ENGINE_PRIORITIES[engine_type][f"tier_{lang_info['tier']}"]
        
        # Filter by requirements
        if requirements.get("premium_quality"):
            available_engines = [e for e in available_engines if e in ["elevenlabs", "neural"]]
        
        if requirements.get("fast_processing"):
            available_engines = [e for e in available_engines if e in ["whisper", "google"]]
        
        # Select highest priority available engine
        for engine in priorities:
            if engine in available_engines:
                # Check engine availability and load
                if await self.is_engine_available(engine):
                    return engine
        
        # Fallback to first available
        return available_engines[0] if available_engines else None
```

## 🕌 Cultural Adaptations

### Meditation-Specific Language Support
```python
MEDITATION_LANGUAGES = {
    "sa": {
        "mantras_supported": True,
        "pronunciation_guide": True,
        "traditional_voices": ["male_priest", "female_teacher"],
        "special_features": {
            "vedic_pronunciation": True,
            "mantra_repetition_timing": True,
            "sanskrit_transliteration": True
        }
    },
    "hi": {
        "mantras_supported": True,
        "pronunciation_guide": True,
        "traditional_voices": ["classical_male", "classical_female"],
        "special_features": {
            "devanagari_support": True,
            "hindi_mantras": True,
            "regional_accents": ["delhi", "mumbai", "kolkata"]
        }
    },
    "th": {
        "meditation_tradition": "buddhist",
        "chanting_support": True,
        "special_features": {
            "buddhist_chants": True,
            "pali_pronunciation": True,
            "temple_voices": True
        }
    },
    "my": {
        "meditation_tradition": "buddhist", 
        "chanting_support": True,
        "special_features": {
            "vipassana_guidance": True,
            "burmese_chants": True,
            "monastery_voices": True
        }
    },
    "ar": {
        "meditation_tradition": "sufi",
        "rtl_support": True,
        "special_features": {
            "sufi_dhikr": True,
            "arabic_prayers": True,
            "quranic_recitation_style": True
        }
    }
}
```

### Cultural Voice Adaptation
```python
class CulturalVoiceAdapter:
    """Adapts voice characteristics based on cultural context"""
    
    async def adapt_voice_for_culture(self, language: str, context: str, voice_params: dict) -> dict:
        """Apply cultural adaptations to voice parameters"""
        cultural_settings = MEDITATION_LANGUAGES.get(language, {})
        
        if context == "meditation":
            if cultural_settings.get("meditation_tradition") == "buddhist":
                voice_params.update({
                    "tone": "calm_contemplative",
                    "pace": "slow_mindful",
                    "pitch": "lower_register"
                })
            
            elif cultural_settings.get("meditation_tradition") == "sufi":
                voice_params.update({
                    "tone": "warm_devotional",
                    "pace": "rhythmic_flowing",
                    "pitch": "resonant"
                })
        
        elif context == "mantra":
            if language == "sa":  # Sanskrit
                voice_params.update({
                    "pronunciation": "vedic_classical",
                    "tone": "reverent_clear",
                    "pace": "measured_precise"
                })
        
        return voice_params
```

## 🔄 Language Detection & Auto-Switching

### Automatic Language Detection
```python
class LanguageDetector:
    """Intelligent language detection from voice input"""
    
    def __init__(self):
        self.detection_models = self.load_detection_models()
        self.confidence_threshold = 0.85
    
    async def detect_language(self, audio_data: bytes, user_context: dict) -> LanguageDetectionResult:
        """Detect language from audio with confidence scoring"""
        
        # Primary detection using Whisper
        whisper_result = await self.detect_with_whisper(audio_data)
        
        # Secondary detection using Google Speech
        google_result = await self.detect_with_google(audio_data)
        
        # Ensemble voting
        detected_language = self.ensemble_vote([whisper_result, google_result])
        
        # Context validation
        validated_language = await self.validate_with_context(detected_language, user_context)
        
        return LanguageDetectionResult(
            language=validated_language.language,
            confidence=validated_language.confidence,
            alternatives=validated_language.alternatives,
            detection_time=validated_language.detection_time
        )
    
    async def validate_with_context(self, detection: LanguageDetection, context: dict) -> ValidatedLanguage:
        """Validate language detection against user context"""
        user_languages = context.get("preferred_languages", [])
        location = context.get("location", {})
        time_zone = context.get("time_zone", "UTC")
        
        # Boost confidence for user's preferred languages
        if detection.language in user_languages:
            detection.confidence += 0.1
        
        # Geographic context validation
        regional_languages = self.get_regional_languages(location)
        if detection.language in regional_languages:
            detection.confidence += 0.05
        
        return ValidatedLanguage(
            language=detection.language,
            confidence=min(detection.confidence, 1.0),
            validation_factors={
                "user_preference": detection.language in user_languages,
                "geographic_match": detection.language in regional_languages,
                "time_context": self.get_time_context_match(detection.language, time_zone)
            }
        )
```

### Code-Switching Support
```python
class CodeSwitchingHandler:
    """Handles multilingual conversations with code-switching"""
    
    async def process_multilingual_input(self, audio_data: bytes, context: dict) -> MultilingualResult:
        """Process audio that may contain multiple languages"""
        
        # Segment audio by language
        language_segments = await self.segment_by_language(audio_data)
        
        results = []
        for segment in language_segments:
            # Process each segment in its detected language
            segment_result = await self.process_segment(segment)
            results.append(segment_result)
        
        # Merge results preserving language context
        merged_result = await self.merge_multilingual_results(results)
        
        return merged_result
    
    async def segment_by_language(self, audio_data: bytes) -> List[LanguageSegment]:
        """Segment audio by detected languages"""
        segments = []
        
        # Use sliding window for language detection
        window_size = 3.0  # 3 seconds
        step_size = 1.0    # 1 second step
        
        audio_duration = self.get_audio_duration(audio_data)
        for start_time in range(0, int(audio_duration), int(step_size)):
            end_time = min(start_time + window_size, audio_duration)
            
            segment_audio = self.extract_audio_segment(audio_data, start_time, end_time)
            detected_lang = await self.detect_language(segment_audio, {})
            
            segments.append(LanguageSegment(
                start_time=start_time,
                end_time=end_time,
                language=detected_lang.language,
                confidence=detected_lang.confidence,
                audio_data=segment_audio
            ))
        
        # Consolidate consecutive segments with same language
        return self.consolidate_segments(segments)
```

## 🎵 Voice Synthesis Localization

### Language-Specific TTS Configuration
```python
class LocalizedTTSManager:
    """Manages localized text-to-speech synthesis"""
    
    TTS_VOICE_MAPPINGS = {
        "en": {
            "male": {"azure": "en-US-JasonNeural", "google": "en-US-Wavenet-D"},
            "female": {"azure": "en-US-JennyNeural", "google": "en-US-Wavenet-F"},
            "regional": {
                "us": "en-US-AriaNeural",
                "uk": "en-GB-LibbyNeural", 
                "au": "en-AU-NatashaNeural"
            }
        },
        "hi": {
            "male": {"azure": "hi-IN-MadhurNeural", "google": "hi-IN-Wavenet-C"},
            "female": {"azure": "hi-IN-SwaraNeural", "google": "hi-IN-Wavenet-A"},
            "classical": {"azure": "hi-IN-MadhurNeural"}
        },
        "es": {
            "male": {"azure": "es-ES-AlvaroNeural", "google": "es-ES-Wavenet-B"},
            "female": {"azure": "es-ES-ElviraNeural", "google": "es-ES-Wavenet-C"},
            "regional": {
                "mexico": "es-MX-DaliaNeural",
                "argentina": "es-AR-ElenaNeural",
                "spain": "es-ES-AlvaroNeural"
            }
        }
    }
    
    async def synthesize_localized_speech(self, text: str, language: str, voice_preferences: dict) -> AudioData:
        """Synthesize speech with cultural and linguistic adaptations"""
        
        # Apply language-specific text preprocessing
        processed_text = await self.preprocess_text_for_language(text, language)
        
        # Select appropriate voice
        voice_config = await self.select_voice_for_language(language, voice_preferences)
        
        # Apply cultural speech patterns
        speech_params = await self.apply_cultural_speech_patterns(language, voice_config)
        
        # Synthesize with selected engine
        audio_data = await self.synthesize_with_engine(
            text=processed_text,
            language=language,
            voice_config=voice_config,
            speech_params=speech_params
        )
        
        # Post-process for cultural authenticity
        enhanced_audio = await self.enhance_cultural_authenticity(audio_data, language)
        
        return enhanced_audio
```

### Pronunciation Guides
```python
class PronunciationGuideManager:
    """Manages pronunciation guides for complex terms"""
    
    PRONUNCIATION_GUIDES = {
        "sa": {
            "mantras": {
                "ॐ": {"ipa": "/oːm/", "guide": "OH-mmm", "audio": "om_pronunciation.wav"},
                "गायत्री": {"ipa": "/gaːjɐtriː/", "guide": "GAH-ya-tree", "audio": "gayatri_pronunciation.wav"},
                "शांति": {"ipa": "/ʃaːnti/", "guide": "SHAHN-tee", "audio": "shanti_pronunciation.wav"}
            }
        },
        "hi": {
            "meditation_terms": {
                "ध्यान": {"ipa": "/d̪ʱjaːn/", "guide": "DHYAAN", "audio": "dhyan_pronunciation.wav"},
                "साधना": {"ipa": "/saːd̪ʱɐnaː/", "guide": "SAADH-na", "audio": "sadhana_pronunciation.wav"}
            }
        }
    }
    
    async def get_pronunciation_guide(self, text: str, language: str) -> PronunciationGuide:
        """Get pronunciation guide for specific text"""
        guides = self.PRONUNCIATION_GUIDES.get(language, {})
        
        for category, terms in guides.items():
            if text.lower() in terms:
                term_guide = terms[text.lower()]
                return PronunciationGuide(
                    original_text=text,
                    ipa_transcription=term_guide["ipa"],
                    phonetic_guide=term_guide["guide"],
                    audio_example=term_guide.get("audio"),
                    language=language,
                    category=category
                )
        
        # Generate guide using ML model if not in predefined list
        return await self.generate_pronunciation_guide(text, language)
```

## 🧠 Machine Learning for Multilingual Processing

### Multilingual Model Training Pipeline
```python
class MultilingualModelTrainer:
    """Trains and maintains multilingual voice processing models"""
    
    def __init__(self):
        self.training_data_manager = TrainingDataManager()
        self.model_versioning = ModelVersioning()
        
    async def train_multilingual_intent_model(self, languages: List[str]) -> TrainingResult:
        """Train intent recognition model for multiple languages"""
        
        training_results = {}
        
        for language in languages:
            # Prepare language-specific training data
            training_data = await self.training_data_manager.get_training_data(language)
            
            # Augment with cross-linguistic patterns
            augmented_data = await self.augment_with_cross_linguistic_data(training_data, language)
            
            # Train language-specific model
            model = await self.train_language_model(augmented_data, language)
            
            # Evaluate model performance
            evaluation = await self.evaluate_model(model, language)
            
            training_results[language] = {
                "model": model,
                "evaluation": evaluation,
                "training_data_size": len(training_data),
                "accuracy": evaluation.accuracy,
                "f1_score": evaluation.f1_score
            }
        
        # Train unified multilingual model
        unified_model = await self.train_unified_model(training_results)
        
        return TrainingResult(
            language_models=training_results,
            unified_model=unified_model,
            training_timestamp=datetime.now(),
            model_version=self.model_versioning.get_next_version()
        )
    
    async def augment_with_cross_linguistic_data(self, training_data: TrainingData, target_language: str) -> AugmentedTrainingData:
        """Augment training data with cross-linguistic patterns"""
        
        # Find linguistically related languages
        related_languages = self.get_linguistically_related_languages(target_language)
        
        augmented_samples = []
        for related_lang in related_languages:
            # Get similar intents from related languages
            related_data = await self.training_data_manager.get_similar_intents(related_lang, training_data.intents)
            
            # Translate and adapt to target language
            translated_samples = await self.translate_training_samples(related_data, related_lang, target_language)
            
            augmented_samples.extend(translated_samples)
        
        return AugmentedTrainingData(
            original_data=training_data,
            augmented_samples=augmented_samples,
            augmentation_ratio=len(augmented_samples) / len(training_data.samples)
        )
```

## 🌐 Real-time Translation Integration

### Voice-to-Voice Translation
```python
class VoiceTranslationPipeline:
    """Real-time voice-to-voice translation"""
    
    async def translate_voice_to_voice(self, audio_data: bytes, source_language: str, target_language: str) -> VoiceTranslationResult:
        """Complete voice-to-voice translation pipeline"""
        
        # Step 1: Speech-to-Text in source language
        source_text = await self.transcribe_speech(audio_data, source_language)
        
        # Step 2: Text translation
        translated_text = await self.translate_text(source_text.text, source_language, target_language)
        
        # Step 3: Cultural adaptation of translated text
        culturally_adapted_text = await self.adapt_text_culturally(translated_text, target_language)
        
        # Step 4: Text-to-Speech in target language
        target_audio = await self.synthesize_speech(culturally_adapted_text, target_language)
        
        return VoiceTranslationResult(
            source_audio=audio_data,
            source_text=source_text.text,
            source_language=source_language,
            translated_text=translated_text,
            culturally_adapted_text=culturally_adapted_text,
            target_audio=target_audio,
            target_language=target_language,
            confidence_score=min(source_text.confidence, translated_text.confidence),
            processing_time=self.calculate_processing_time()
        )
```

## 📊 Language Analytics & Insights

### Multilingual Usage Analytics
```python
class MultilingualAnalytics:
    """Analytics for multilingual voice service usage"""
    
    async def generate_language_usage_report(self, time_period: str) -> LanguageUsageReport:
        """Generate comprehensive language usage analytics"""
        
        usage_stats = await self.get_usage_statistics(time_period)
        
        return LanguageUsageReport(
            time_period=time_period,
            total_requests=usage_stats["total_requests"],
            languages_used=usage_stats["languages_used"],
            top_languages=usage_stats["top_languages"],
            engine_performance=usage_stats["engine_performance"],
            cultural_feature_usage=usage_stats["cultural_features"],
            user_language_preferences=usage_stats["user_preferences"],
            geographic_distribution=usage_stats["geographic_stats"],
            quality_metrics={
                "average_confidence": usage_stats["avg_confidence"],
                "error_rates_by_language": usage_stats["error_rates"],
                "user_satisfaction_scores": usage_stats["satisfaction"]
            }
        )
```

## 🚀 Future Multilingual Enhancements

### Planned Language Additions
```yaml
future_languages:
  tier_1_candidates:
    - Vietnamese (vi): "Southeast Asian Buddhist tradition"
    - Turkish (tr): "Sufi meditation practices"
    - Tibetan (bo): "Tibetan Buddhist practices"
    
  tier_2_candidates:
    - Polish (pl): "European expansion"
    - Swedish (sv): "Nordic wellness practices"
    - Hebrew (he): "Jewish meditation traditions"
    
  specialized_support:
    - Latin (la): "Western meditation texts"
    - Pali (pi): "Buddhist canonical language"
    - Old Church Slavonic: "Orthodox Christian practices"
```

### Advanced Multilingual Features
- **Neural Voice Cloning**: Create personalized voices in any supported language
- **Accent Adaptation**: Adapt voice synthesis to user's regional accent
- **Emotion Transfer**: Maintain emotional tone across language translations
- **Cultural Context AI**: Advanced AI for cultural appropriateness
- **Multilingual Conversations**: Handle seamless language switching in conversations

---

This comprehensive multilingual support enables MantraPath to serve a global audience while respecting cultural nuances and maintaining high-quality voice processing across all supported languages.
