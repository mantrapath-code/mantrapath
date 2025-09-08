"""
Test fixtures and test data for voice service tests
"""

# Indian Regional Language Test Data
INDIAN_LANGUAGE_TEST_DATA = {
    "hindi": {
        "text": "नमस्ते, आप कैसे हैं?",
        "translation": "Hello, how are you?",
        "language_code": "hi",
        "script": "देवनागरी",
        "region": "North India",
        "expected_tts_models": ["coqui_hi", "festival_hi", "espeak_hi"]
    },
    "bengali": {
        "text": "আপনি কেমন আছেন?",
        "translation": "How are you?",
        "language_code": "bn",
        "script": "বাংলা",
        "region": "East India",
        "expected_tts_models": ["coqui_bn", "espeak_bn"]
    },
    "tamil": {
        "text": "நீங்கள் எப்படி இருக்கிறீர்கள்?",
        "translation": "How are you?",
        "language_code": "ta",
        "script": "தமிழ்",
        "region": "South India",
        "expected_tts_models": ["espeak_ta"]
    },
    "telugu": {
        "text": "మీరు ఎలా ఉన్నారు?",
        "translation": "How are you?",
        "language_code": "te",
        "script": "తెలుగు",
        "region": "South India",
        "expected_tts_models": ["espeak_te"]
    },
    "marathi": {
        "text": "तुम्ही कसे आहात?",
        "translation": "How are you?",
        "language_code": "mr",
        "script": "देवनागरी",
        "region": "West India",
        "expected_tts_models": ["vosk_mr", "espeak_mr"]
    },
    "gujarati": {
        "text": "તમે કેમ છો?",
        "translation": "How are you?",
        "language_code": "gu",
        "script": "ગુજરાતી",
        "region": "West India",
        "expected_tts_models": ["vosk_gu", "espeak_gu"]
    },
    "kannada": {
        "text": "ನೀವು ಹೇಗಿದ್ದೀರಿ?",
        "translation": "How are you?",
        "language_code": "kn",
        "script": "ಕನ್ನಡ",
        "region": "South India",
        "expected_tts_models": ["espeak_kn"]
    },
    "malayalam": {
        "text": "നിങ്ങൾ എങ്ങനെയുണ്ട്?",
        "translation": "How are you?",
        "language_code": "ml",
        "script": "മലയാളം",
        "region": "South India",
        "expected_tts_models": ["espeak_ml"]
    },
    "punjabi": {
        "text": "ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ?",
        "translation": "How are you?",
        "language_code": "pa",
        "script": "ਗੁਰਮੁਖੀ",
        "region": "North India",
        "expected_tts_models": ["espeak_pa"]
    },
    "urdu": {
        "text": "آپ کیسے ہیں؟",
        "translation": "How are you?",
        "language_code": "ur",
        "script": "اردو",
        "region": "North India",
        "expected_tts_models": ["espeak_ur"]
    }
}

# Code-switching test data (Hindi-English mix)
CODE_SWITCHING_TEST_DATA = [
    {
        "text": "मैं आज office जा रहा हूँ",
        "translation": "I am going to office today",
        "languages": ["hi", "en"],
        "type": "intra_sentential"
    },
    {
        "text": "Good morning! आपका दिन कैसा जा रहा है?",
        "translation": "Good morning! How is your day going?",
        "languages": ["en", "hi"],
        "type": "inter_sentential"
    },
    {
        "text": "Meeting में late हो जाऊंगा",
        "translation": "I will be late for the meeting",
        "languages": ["en", "hi"],
        "type": "intra_sentential"
    }
]

# Complex conversation scenarios
CONVERSATION_SCENARIOS = [
    {
        "name": "medical_consultation",
        "language": "hi",
        "turns": [
            {"user": "डॉक्टर साहब, मुझे सिर में दर्द हो रहा है", "bot_context": "medical_greeting"},
            {"user": "कल रात से ही शुरू हुआ है", "bot_context": "medical_symptom_inquiry"},
            {"user": "हाँ, बुखार भी है", "bot_context": "medical_diagnosis"}
        ]
    },
    {
        "name": "banking_inquiry",
        "language": "en",
        "turns": [
            {"user": "I want to check my account balance", "bot_context": "banking_greeting"},
            {"user": "My account number is 123456789", "bot_context": "banking_verification"},
            {"user": "Yes, that's correct", "bot_context": "banking_service"}
        ]
    },
    {
        "name": "educational_support",
        "language": "bn",
        "turns": [
            {"user": "আমি গণিত বুঝতে পারছি না", "bot_context": "education_greeting"},
            {"user": "বীজগণিত নিয়ে সমস্যা", "bot_context": "education_subject_specific"},
            {"user": "x + 2 = 5 এই সমীকরণটি সমাধান করুন", "bot_context": "education_problem_solving"}
        ]
    }
]

# Voice quality test patterns
VOICE_QUALITY_PATTERNS = {
    "clear_speech": {
        "noise_level": 0.1,
        "clarity": 0.9,
        "expected_confidence": 0.85
    },
    "noisy_environment": {
        "noise_level": 0.6,
        "clarity": 0.4,
        "expected_confidence": 0.5
    },
    "accented_speech": {
        "accent_type": "indian_english",
        "clarity": 0.7,
        "expected_confidence": 0.7
    }
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "stt_latency": {"max_ms": 3000, "target_ms": 1500},
    "tts_latency": {"max_ms": 2000, "target_ms": 1000},
    "conversation_response": {"max_ms": 5000, "target_ms": 3000},
    "cache_hit_rate": {"minimum": 0.7, "target": 0.85}
}

# Error simulation patterns
ERROR_SCENARIOS = [
    {
        "name": "models_service_down",
        "error_type": "connection_error",
        "expected_fallback": "cached_response"
    },
    {
        "name": "invalid_audio_format",
        "error_type": "format_error",
        "expected_response": "format_error_message"
    },
    {
        "name": "unsupported_language",
        "error_type": "language_error",
        "expected_fallback": "english_response"
    }
]

# Multi-modal test data
MULTIMODAL_TEST_DATA = [
    {
        "audio_text": "मुझे बारिश के बारे में बताएं",
        "context": {"location": "Mumbai", "time": "evening"},
        "expected_response_type": "weather_info",
        "response_language": "hi"
    },
    {
        "audio_text": "Play some music",
        "context": {"user_preferences": {"genre": "classical"}},
        "expected_response_type": "music_recommendation",
        "response_language": "en"
    }
]

# Regional dialect variations
REGIONAL_DIALECTS = {
    "hindi": {
        "standard": "मैं घर जा रहा हूँ",
        "haryanvi": "मैं घर जा र्या हूँ",
        "rajasthani": "म्हूं घर जाऊं छूं",
        "bhojpuri": "हम घर जाईत हई"
    },
    "tamil": {
        "standard": "நான் வீட்டிற்கு போகிறேன்",
        "chennai": "நான் வீட்டுக்கு போறேன்",
        "madurai": "நான் வீட்டுக்கு போयிट்டு வरேன்"
    }
}
