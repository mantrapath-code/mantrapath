"""
Community Service Configuration
Psychology-based settings and theme configurations
"""
from typing import Dict, List

# Psychology-based color system
WELLNESS_COLORS = {
    "calm_blue": "#4A90E2",      # Trust, stability, peace
    "sage_green": "#87A96B",     # Growth, harmony, balance  
    "soft_purple": "#9B8CE8",    # Creativity, mindfulness
    "warm_beige": "#F5F1E8",     # Comfort, grounding
    "gentle_teal": "#5DADE2",    # Clarity, refreshing
    "sunset_orange": "#F39C12",  # Warmth, optimism (used sparingly)
    "forest_green": "#27AE60",   # Nature, healing
    "lavender": "#BB8FCE",       # Relaxation, tranquility
    "soft_pink": "#F8BBD9",      # Nurturing, compassion
    "warm_yellow": "#F7DC6F"     # Hope, gentle energy
}

# Mood-responsive color adjustments
MOOD_COLOR_MAPPING = {
    "anxious": ["calm_blue", "sage_green", "lavender"],
    "depressed": ["warm_beige", "sunset_orange", "gentle_teal"],
    "stressed": ["forest_green", "soft_purple", "calm_blue"],
    "happy": ["gentle_teal", "sage_green", "sunset_orange"],
    "neutral": ["calm_blue", "sage_green", "warm_beige"],
    "excited": ["soft_pink", "warm_yellow", "gentle_teal"],
    "sad": ["lavender", "warm_beige", "soft_purple"],
    "angry": ["forest_green", "calm_blue", "lavender"]
}

# Community psychological focus areas
PSYCHOLOGICAL_FOCUS_AREAS = [
    "anxiety_support",
    "depression_help", 
    "mindfulness_practice",
    "stress_management",
    "grief_support",
    "addiction_recovery",
    "general_wellness",
    "crisis_support"
]

# Default calming theme configuration
DEFAULT_CALMING_THEME = {
    "primary": WELLNESS_COLORS["calm_blue"],
    "secondary": WELLNESS_COLORS["sage_green"],
    "accent": WELLNESS_COLORS["soft_purple"],
    "background": WELLNESS_COLORS["warm_beige"],
    "text": "#2C3E50",
    "text_secondary": "#7F8C8D",
    "border": "#E8F4FD",
    "success": WELLNESS_COLORS["forest_green"],
    "warning": WELLNESS_COLORS["sunset_orange"],
    "error": "#E74C3C",  # Kept minimal red for critical alerts
    "info": WELLNESS_COLORS["gentle_teal"]
}

# Community interaction guidelines for psychological wellness
INTERACTION_GUIDELINES = {
    "supportive_language": {
        "encouraged": ["I understand", "Thank you for sharing", "You're not alone", "That takes courage"],
        "discouraged": ["You should", "Just think positive", "It could be worse", "Get over it"]
    },
    "crisis_keywords": ["suicide", "self-harm", "hurt myself", "end it all", "no point", "give up"],
    "calming_prompts": [
        "Take a deep breath with me",
        "Let's pause for a moment",
        "You're safe here",
        "One step at a time"
    ]
}

# Feed algorithm weights for psychological wellness
FEED_ALGORITHM_WEIGHTS = {
    "psychological_relevance": 0.4,
    "calming_effect": 0.3,
    "community_engagement": 0.2,
    "recency": 0.1
}
