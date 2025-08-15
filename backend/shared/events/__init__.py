"""
Enhanced Event System for MantraPath V3
Supporting Voice, AI, and Cultural Intelligence Events
"""

try:
    from .voice_events import (
        VoiceActivityEvent,
        VoiceIntentEvent,
        VoiceEventType,
        VoiceIntentType
    )
    VOICE_EVENTS_AVAILABLE = True
except ImportError:
    VOICE_EVENTS_AVAILABLE = False

try:
    from .ai_events import (
        AIProcessingEvent,
        CrossServiceIntelligenceEvent,
        AIEventType,
        IntelligenceEventType
    )
    AI_EVENTS_AVAILABLE = True
except ImportError:
    AI_EVENTS_AVAILABLE = False

try:
    from .cultural_events import (
        CulturalContextEvent,
        RegionalIntelligenceEvent,
        CulturalEventType,
        RegionalEventType
    )
    CULTURAL_EVENTS_AVAILABLE = True
except ImportError:
    CULTURAL_EVENTS_AVAILABLE = False

try:
    from .enhanced_bus import (
        EnhancedEventBus,
        get_enhanced_event_bus,
        cleanup_enhanced_event_bus,
        V3EventChannels
    )
    ENHANCED_BUS_AVAILABLE = True
except ImportError:
    ENHANCED_BUS_AVAILABLE = False

# Export available components
__all__ = []

if VOICE_EVENTS_AVAILABLE:
    __all__.extend([
        'VoiceActivityEvent',
        'VoiceIntentEvent', 
        'VoiceEventType',
        'VoiceIntentType'
    ])

if AI_EVENTS_AVAILABLE:
    __all__.extend([
        'AIProcessingEvent',
        'CrossServiceIntelligenceEvent',
        'AIEventType',
        'IntelligenceEventType'
    ])

if CULTURAL_EVENTS_AVAILABLE:
    __all__.extend([
        'CulturalContextEvent',
        'RegionalIntelligenceEvent',
        'CulturalEventType',
        'RegionalEventType'
    ])

if ENHANCED_BUS_AVAILABLE:
    __all__.extend([
        'EnhancedEventBus',
        'get_enhanced_event_bus',
        'cleanup_enhanced_event_bus',
        'V3EventChannels'
    ])
