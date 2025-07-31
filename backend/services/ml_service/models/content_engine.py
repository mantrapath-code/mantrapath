"""
Advanced ML Notification Content Engine with NLP and Sentiment Analysis
Generates highly personalized notification content using machine learning,
natural language processing, and sentiment analysis techniques.
"""

import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics
import random
import numpy as np
import pandas as pd
from collections import defaultdict, Counter

# Configure logging
import logging
logger = logging.getLogger(__name__)

# ML and NLP libraries
try:
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation, NMF
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    import nltk
    from textblob import TextBlob
    from wordcloud import WordCloud
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some ML/NLP libraries not available: {e}")
    ML_AVAILABLE = False

# Download required NLTK data
if ML_AVAILABLE:
    try:
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        from nltk.sentiment import SentimentIntensityAnalyzer
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize, sent_tokenize
        from nltk.stem import WordNetLemmatizer
        NLTK_AVAILABLE = True
    except Exception as e:
        logger.warning(f"NLTK data not fully available: {e}")
        NLTK_AVAILABLE = False
else:
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)

class NotificationContentEngine:
    """Advanced ML-powered notification content generator with NLP and sentiment analysis"""
    
    def __init__(self):
        self.ready = ML_AVAILABLE and NLTK_AVAILABLE
        self.model_version = "2.0.0-ml"
        self.model_dir = os.path.join(os.path.dirname(__file__), '..', 'trained_models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # NLP and sentiment analysis components
        self.sentiment_analyzer = SentimentIntensityAnalyzer() if NLTK_AVAILABLE else None
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        self.stop_words = set(stopwords.words('english')) if NLTK_AVAILABLE else set()
        
        # ML models for content generation
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.topic_model = LatentDirichletAllocation(n_components=10, random_state=42)
        self.content_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.sentiment_scaler = StandardScaler()
        
        # Content personalization models
        self.user_preference_model = KMeans(n_clusters=5, random_state=42)
        self.engagement_predictor = LogisticRegression(random_state=42)
        
        # Content databases and templates
        self.content_templates = self._load_advanced_templates()
        self.therapeutic_phrases = self._load_therapeutic_phrases()
        self.emotional_keywords = self._load_emotional_keywords()
        self.content_corpus = []
        
        # Performance tracking
        self.performance_metrics = {
            'content_generated': 0,
            'sentiment_accuracy': 0.0,
            'engagement_rate': 0.0,
            'personalization_score': 0.0,
            'model_confidence': 0.0
        }
        
        # Load pre-trained models if available
        self._load_ml_models()
        
        # Initialize fallback templates for when ML is unavailable
        if not self.ready:
            logger.warning("ML/NLP libraries not available, falling back to template-based content")
            self.content_templates = self._load_content_templates()
            self.insight_generators = self._initialize_insight_generators()
        
    def is_ready(self) -> bool:
        """Check if the content engine is ready"""
        return self.ready
    
    def _load_ml_models(self):
        """Load pre-trained ML models for content generation"""
        try:
            model_files = {
                'tfidf_vectorizer.joblib': 'tfidf_vectorizer',
                'topic_model.joblib': 'topic_model',
                'content_classifier.joblib': 'content_classifier',
                'user_preference_model.joblib': 'user_preference_model',
                'engagement_predictor.joblib': 'engagement_predictor',
                'sentiment_scaler.joblib': 'sentiment_scaler'
            }
            
            for filename, attr_name in model_files.items():
                file_path = os.path.join(self.model_dir, filename)
                if os.path.exists(file_path):
                    setattr(self, attr_name, joblib.load(file_path))
                    logger.info(f"Loaded {attr_name} from {filename}")
            
            # Load performance metrics
            metrics_path = os.path.join(self.model_dir, 'content_metrics.json')
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.performance_metrics.update(json.load(f))
                    
        except Exception as e:
            logger.warning(f"Could not load pre-trained content models: {e}")
    
    def _save_ml_models(self):
        """Save trained ML models"""
        try:
            model_files = {
                'tfidf_vectorizer.joblib': self.tfidf_vectorizer,
                'topic_model.joblib': self.topic_model,
                'content_classifier.joblib': self.content_classifier,
                'user_preference_model.joblib': self.user_preference_model,
                'engagement_predictor.joblib': self.engagement_predictor,
                'sentiment_scaler.joblib': self.sentiment_scaler
            }
            
            for filename, model in model_files.items():
                if hasattr(model, 'fit'):  # Only save fitted models
                    file_path = os.path.join(self.model_dir, filename)
                    joblib.dump(model, file_path)
            
            # Save performance metrics
            metrics_path = os.path.join(self.model_dir, 'content_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(self.performance_metrics, f, default=str)
                
            logger.info("Content ML models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save content ML models: {e}")
    
    def _load_advanced_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load advanced content templates with therapeutic language patterns"""
        return {
            "therapeutic_frameworks": {
                "cognitive_reframing": [
                    "What evidence supports this thought?",
                    "How might you view this situation differently?",
                    "What would you tell a friend in this situation?"
                ],
                "mindfulness_prompts": [
                    "Notice what you're feeling right now without judgment",
                    "Take three conscious breaths and observe your present moment",
                    "What physical sensations are you aware of?"
                ],
                "behavioral_activation": [
                    "What small action could improve your mood right now?",
                    "Which activity usually brings you joy?",
                    "How can you add one meaningful activity to your day?"
                ]
            },
            "emotional_validation": {
                "acknowledgment": [
                    "Your feelings are completely valid",
                    "It makes sense that you're feeling this way",
                    "You're doing the best you can with what you have"
                ],
                "normalization": [
                    "Many people experience similar feelings",
                    "These emotions are a normal part of the human experience",
                    "You're not alone in feeling this way"
                ]
            },
            "motivational_content": {
                "growth_mindset": [
                    "Every challenge is an opportunity to grow",
                    "Your potential is not determined by your current circumstances",
                    "Small steps lead to significant changes"
                ],
                "resilience_building": [
                    "You've overcome difficulties before",
                    "Your strength is greater than your struggles",
                    "This feeling is temporary, your resilience is permanent"
                ]
            }
        }
    
    def _load_therapeutic_phrases(self) -> Dict[str, List[str]]:
        """Load evidence-based therapeutic phrases and interventions"""
        return {
            "validation": [
                "Your experience matters", "You are heard", "Your feelings make sense",
                "It's okay to feel this way", "You're doing your best"
            ],
            "reframing": [
                "What if we looked at this differently?", "Another perspective might be...",
                "Consider this possibility...", "What would change if..."
            ],
            "grounding": [
                "Focus on your breath", "Notice your surroundings", "Feel your feet on the ground",
                "Name five things you can see", "What sounds do you hear?"
            ],
            "encouragement": [
                "You are stronger than you know", "This too shall pass", "One step at a time",
                "You've got this", "Progress, not perfection"
            ],
            "action_oriented": [
                "What's one small step you could take?", "How can you care for yourself today?",
                "What would help you feel a bit better?", "Who could you reach out to?"
            ]
        }
    
    def _load_emotional_keywords(self) -> Dict[str, List[str]]:
        """Load emotional keyword mappings for sentiment analysis"""
        return {
            "anxiety": ["worried", "anxious", "nervous", "stressed", "overwhelmed", "panic", "tense"],
            "depression": ["sad", "empty", "hopeless", "worthless", "tired", "unmotivated", "heavy"],
            "anger": ["frustrated", "angry", "irritated", "annoyed", "furious", "rage", "mad"],
            "joy": ["happy", "excited", "joyful", "content", "pleased", "delighted", "cheerful"],
            "fear": ["scared", "afraid", "fearful", "terrified", "worried", "nervous", "anxious"],
            "loneliness": ["lonely", "isolated", "alone", "disconnected", "abandoned", "empty"],
            "gratitude": ["grateful", "thankful", "appreciative", "blessed", "fortunate"],
            "confidence": ["confident", "strong", "capable", "empowered", "secure", "self-assured"]
        }
    
    def _load_content_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load notification content templates"""
        return {
            "morning_check": {
                "titles": [
                    "Good Morning! 🌅",
                    "Start Your Day Right ☀️",
                    "Morning Check-in 🌤️",
                    "Rise and Shine! ✨"
                ],
                "messages": [
                    "How are you feeling this morning? A quick mood check can set a positive tone for your day.",
                    "Take a moment to notice how you're starting your day. Your morning mood matters!",
                    "Good morning! Your mental wellness journey continues today. How are you feeling?",
                    "Starting the day with awareness. Take a moment to check in with yourself."
                ],
                "action_suggestions": [
                    "Log your morning mood",
                    "Set a positive intention",
                    "Practice gratitude",
                    "Take three deep breaths"
                ]
            },
            "afternoon_support": {
                "titles": [
                    "Afternoon Check-in 🌞",
                    "Midday Boost 💪",
                    "Energy Reset 🔄",
                    "Afternoon Wellness 🌻"
                ],
                "messages": [
                    "Afternoon energy dip? It's completely normal. Take a moment to check in with yourself.",
                    "How's your day going so far? Sometimes a quick pause can refresh your perspective.",
                    "Midday check-in: You're doing great! How are you feeling right now?",
                    "Afternoon support: Remember, every moment is a chance for a fresh start."
                ],
                "action_suggestions": [
                    "Try a breathing exercise",
                    "Take a short walk",
                    "Practice mindfulness",
                    "Connect with your support network"
                ]
            },
            "evening_reflection": {
                "titles": [
                    "Evening Reflection 🌙",
                    "Day's End Check-in 🌅",
                    "Nighttime Wellness 🌟",
                    "Peaceful Evening 🕊️"
                ],
                "messages": [
                    "As the day winds down, take a moment to reflect. How did today go for you?",
                    "Evening reflection: What went well today? What can you appreciate about yourself?",
                    "Time to process the day. Your thoughts and feelings are valid and important.",
                    "Before you rest, acknowledge today's journey. You made it through another day."
                ],
                "action_suggestions": [
                    "Journal about your day",
                    "Practice gratitude",
                    "Set tomorrow's intention",
                    "Relax with deep breathing"
                ]
            },
            "intervention": {
                "titles": [
                    "You're Not Alone 💙",
                    "Gentle Support 🤗",
                    "Caring Check-in 💜",
                    "We're Here for You 🫶"
                ],
                "messages": [
                    "It seems like you might be going through a tough time. Remember, you're not alone in this.",
                    "Your feelings are valid. Take things one moment at a time, and be gentle with yourself.",
                    "Difficult moments pass. You've overcome challenges before, and you can do it again.",
                    "You matter, and your wellbeing is important. Consider reaching out for support if you need it."
                ],
                "action_suggestions": [
                    "Talk to someone you trust",
                    "Use the chatbot for support",
                    "Try grounding techniques",
                    "Consider professional help"
                ]
            },
            "day_preparation": {
                "titles": [
                    "Gentle Day Prep 🌱",
                    "Starting Strong 💪",
                    "Day Ahead Support 🌈",
                    "You've Got This! ✨"
                ],
                "messages": [
                    "Today might feel challenging, but remember: you have tools and strength to handle whatever comes.",
                    "Preparing for the day ahead. You're resilient and capable of navigating today's challenges.",
                    "Some days are harder than others, and that's okay. You're prepared to face today with courage.",
                    "Your past experiences have built your resilience. Trust in your ability to handle today."
                ],
                "action_suggestions": [
                    "Review your coping strategies",
                    "Set small, achievable goals",
                    "Plan self-care moments",
                    "Remember your support network"
                ]
            },
            "motivation": {
                "titles": [
                    "You're Amazing! 🌟",
                    "Keep Going! 💫",
                    "Believe in Yourself ✨",
                    "Progress Recognition 🏆"
                ],
                "messages": [
                    "Your commitment to wellness is inspiring. Every small step counts!",
                    "You're making progress, even when it doesn't feel like it. Keep going!",
                    "Your journey matters. You're building resilience and strength every day.",
                    "Celebrating your dedication to mental wellness. You're doing great work!"
                ],
                "action_suggestions": [
                    "Acknowledge your progress",
                    "Share your success",
                    "Set new wellness goals",
                    "Practice self-compassion"
                ]
            }
        }
    
    def _initialize_insight_generators(self) -> Dict[str, Any]:
        """Initialize insight generation functions"""
        return {
            "weekly_summary": self._generate_weekly_summary,
            "pattern_insights": self._generate_pattern_insights,
            "improvement_suggestions": self._generate_improvement_suggestions,
            "celebration_insights": self._generate_celebration_insights,
            "predictive_insights": self._generate_predictive_insights
        }
    
    def generate_personalized_notification(
        self, 
        notification_type: str, 
        user_context: Dict[str, Any],
        effectiveness_score: float = 7.0
    ) -> Dict[str, Any]:
        """
        Generate AI-powered personalized notification content with NLP and sentiment analysis
        
        Args:
            notification_type: Type of notification (morning_check, afternoon_support, etc.)
            user_context: User's current context and patterns
            effectiveness_score: Predicted effectiveness of this notification
            
        Returns:
            ML-generated personalized notification content
        """
        try:
            if not self.ready:
                return self._fallback_generate_notification(notification_type, user_context, effectiveness_score)
            
            # Analyze user's emotional state and context with NLP
            emotional_analysis = self._analyze_user_emotional_state(user_context)
            sentiment_profile = self._build_sentiment_profile(user_context)
            
            # Generate content using ML and therapeutic frameworks
            ml_content = self._generate_ml_content(
                notification_type, 
                emotional_analysis, 
                sentiment_profile, 
                effectiveness_score
            )
            
            # Apply NLP-based personalization
            personalized_content = self._apply_nlp_personalization(
                ml_content, user_context, emotional_analysis
            )
            
            # Validate and enhance content using therapeutic guidelines
            enhanced_content = self._enhance_with_therapeutic_framework(
                personalized_content, emotional_analysis
            )
            
            # Calculate confidence and personalization metrics
            confidence_score = self._calculate_content_confidence(enhanced_content, user_context)
            personalization_level = self._calculate_ml_personalization_level(user_context, emotional_analysis)
            
            # Update performance metrics
            self.performance_metrics['content_generated'] += 1
            self.performance_metrics['model_confidence'] = confidence_score
            self.performance_metrics['personalization_score'] = personalization_level
            
            return {
                "title": enhanced_content.get("title", "Wellness Check-in 💙"),
                "message": enhanced_content["message"],
                "action_suggestions": enhanced_content.get("action_suggestions", [])[:3],
                "notification_type": notification_type,
                "effectiveness_score": effectiveness_score,
                "personalization_level": personalization_level,
                "confidence_score": confidence_score,
                "emotional_theme": emotional_analysis.get("primary_emotion", "neutral"),
                "therapeutic_approach": enhanced_content.get("therapeutic_approach", "general_support"),
                "ml_method": "nlp_sentiment_analysis",
                "model_version": self.model_version
            }
            
        except Exception as e:
            logger.error(f"Error in ML content generation: {e}")
            return self._get_fallback_content(notification_type)
    
    def _analyze_user_emotional_state(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced NLP analysis of user's emotional state"""
        try:
            mood_entries = user_context.get("mood_entries", [])
            journal_entries = user_context.get("journal_entries", [])
            
            # Extract text data from journal entries for NLP analysis
            text_data = []
            if journal_entries:
                for entry in journal_entries[-5:]:  # Last 5 entries
                    if entry.get('content'):
                        text_data.append(entry['content'])
            
            # Simple emotional analysis based on recent mood scores
            avg_mood = 5.0  # Default neutral mood
            if mood_entries:
                recent_moods = [entry.get('mood_score', 5) for entry in mood_entries[-7:]]
                avg_mood = sum(recent_moods) / len(recent_moods)
                
                if avg_mood <= 3:
                    primary_emotion = "distressed"
                    therapeutic_needs = ["validation", "reframing"]
                elif avg_mood <= 5:
                    primary_emotion = "low_mood"
                    therapeutic_needs = ["encouragement", "behavioral_activation"]
                elif avg_mood >= 8:
                    primary_emotion = "positive"
                    therapeutic_needs = ["reinforcement", "growth_mindset"]
                else:
                    primary_emotion = "neutral"
                    therapeutic_needs = ["general_support", "mindfulness"]
            else:
                primary_emotion = "neutral"
                therapeutic_needs = ["general_support"]
            
            # Initialize emotional analysis with basic mood data
            emotional_analysis = {
                "sentiment_scores": [],
                "emotional_keywords": [],
                "primary_emotion": primary_emotion,
                "emotion_intensity": abs(avg_mood - 5) / 5 if mood_entries else 0.5,
                "emotional_trend": "stable",
                "therapeutic_needs": therapeutic_needs
            }
            
            # Enhanced NLP analysis if NLTK is available and we have text data
            if text_data and self.sentiment_analyzer and NLTK_AVAILABLE:
                for text in text_data:
                    # VADER sentiment analysis
                    vader_scores = self.sentiment_analyzer.polarity_scores(text)
                    
                    # TextBlob sentiment analysis
                    blob = TextBlob(text)
                    textblob_sentiment = blob.sentiment.polarity
                    
                    # Combine scores
                    combined_score = {
                        'compound': vader_scores['compound'],
                        'positive': vader_scores['pos'],
                        'negative': vader_scores['neg'],
                        'neutral': vader_scores['neu'],
                        'textblob_polarity': textblob_sentiment,
                        'textblob_subjectivity': blob.sentiment.subjectivity
                    }
                    emotional_analysis["sentiment_scores"].append(combined_score)
                    
                    # Extract emotional keywords
                    keywords = self._extract_emotional_keywords(text)
                    emotional_analysis["emotional_keywords"].extend(keywords)
                
                # Update primary emotion based on sentiment analysis
                if emotional_analysis["sentiment_scores"]:
                    avg_compound = np.mean([s['compound'] for s in emotional_analysis["sentiment_scores"]])
                    
                    if avg_compound <= -0.5:
                        emotional_analysis["primary_emotion"] = "distressed"
                        emotional_analysis["emotion_intensity"] = abs(avg_compound)
                        emotional_analysis["therapeutic_needs"] = ["validation", "reframing", "grounding"]
                    elif avg_compound <= -0.1:
                        emotional_analysis["primary_emotion"] = "low_mood"
                        emotional_analysis["emotion_intensity"] = abs(avg_compound)
                        emotional_analysis["therapeutic_needs"] = ["encouragement", "behavioral_activation"]
                    elif avg_compound >= 0.5:
                        emotional_analysis["primary_emotion"] = "positive"
                        emotional_analysis["emotion_intensity"] = avg_compound
                        emotional_analysis["therapeutic_needs"] = ["reinforcement", "growth_mindset"]
                    else:
                        emotional_analysis["primary_emotion"] = "neutral"
                        emotional_analysis["emotion_intensity"] = 0.5
                        emotional_analysis["therapeutic_needs"] = ["general_support", "mindfulness"]
            
            # Analyze mood score trends if available
            if mood_entries:
                recent_moods = [entry.get('mood_score', 5) for entry in mood_entries[-7:]]  # Last week
                if len(recent_moods) >= 3:
                    trend = np.polyfit(range(len(recent_moods)), recent_moods, 1)[0]
                    if trend > 0.3:
                        emotional_analysis["emotional_trend"] = "improving"
                    elif trend < -0.3:
                        emotional_analysis["emotional_trend"] = "declining"
                    else:
                        emotional_analysis["emotional_trend"] = "stable"
            
            return emotional_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing emotional state: {e}")
            return {
                "primary_emotion": "neutral",
                "emotion_intensity": 0.5,
                "emotional_trend": "stable",
                "therapeutic_needs": ["general_support"]
            }
    
    def _extract_emotional_keywords(self, text: str) -> List[str]:
        """Extract emotional keywords from text using NLP"""
        try:
            if not NLTK_AVAILABLE or not self.lemmatizer:
                # Fallback to simple keyword matching
                emotional_keywords = []
                text_lower = text.lower()
                for emotion_category, keywords in self.emotional_keywords.items():
                    for keyword in keywords:
                        if keyword in text_lower:
                            emotional_keywords.append((emotion_category, keyword))
                return emotional_keywords
            
            # Tokenize and lemmatize
            tokens = word_tokenize(text.lower())
            lemmatized = [self.lemmatizer.lemmatize(token) for token in tokens if token.isalpha()]
            
            # Find emotional keywords
            emotional_keywords = []
            for emotion_category, keywords in self.emotional_keywords.items():
                for keyword in keywords:
                    if keyword in lemmatized:
                        emotional_keywords.append((emotion_category, keyword))
            
            return emotional_keywords
            
        except Exception as e:
            logger.error(f"Error extracting emotional keywords: {e}")
            return []

    def _build_sentiment_profile(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive sentiment profile using ML"""
        try:
            mood_entries = user_context.get("mood_entries", [])
            
            if len(mood_entries) < 5:
                return {"profile_type": "insufficient_data", "confidence": 0.2}
            
            # Create feature vector from mood data
            features = self._extract_mood_features(mood_entries)
            
            # Use clustering to identify user's emotional profile
            if hasattr(self.user_preference_model, 'cluster_centers_'):
                features_scaled = self.sentiment_scaler.transform([features])
                cluster = self.user_preference_model.predict(features_scaled)[0]
                
                profile_types = {
                    0: "analytical_responder",
                    1: "emotional_processor", 
                    2: "action_oriented",
                    3: "mindfulness_seeker",
                    4: "social_connector"
                }
                
                return {
                    "profile_type": profile_types.get(cluster, "general"),
                    "cluster_id": cluster,
                    "confidence": 0.8,
                    "features": features
                }
            
            return {"profile_type": "general", "confidence": 0.5}
            
        except Exception as e:
            logger.error(f"Error building sentiment profile: {e}")
            return {"profile_type": "general", "confidence": 0.3}
    
    def _extract_mood_features(self, mood_entries: List[Dict[str, Any]]) -> List[float]:
        """Extract numerical features from mood entries for ML analysis"""
        try:
            if not mood_entries:
                return [5.0, 0.0, 0.0, 0.0]  # Default neutral features
            
            # Extract mood scores
            mood_scores = [entry.get('mood_score', 5) for entry in mood_entries[-14:]]  # Last 2 weeks
            
            # Calculate features
            avg_mood = np.mean(mood_scores) if mood_scores else 5.0
            mood_variance = np.var(mood_scores) if len(mood_scores) > 1 else 0.0
            mood_trend = np.polyfit(range(len(mood_scores)), mood_scores, 1)[0] if len(mood_scores) > 2 else 0.0
            mood_stability = 1.0 / (1.0 + mood_variance)  # Higher = more stable
            
            return [avg_mood, mood_variance, mood_trend, mood_stability]
            
        except Exception as e:
            logger.error(f"Error extracting mood features: {e}")
            return [5.0, 0.0, 0.0, 0.0]
    
    def _generate_ml_content(
        self, 
        notification_type: str, 
        emotional_analysis: Dict[str, Any], 
        sentiment_profile: Dict[str, Any], 
        effectiveness_score: float
    ) -> Dict[str, Any]:
        """Generate content using ML models and emotional analysis"""
        try:
            primary_emotion = emotional_analysis.get("primary_emotion", "neutral")
            therapeutic_needs = emotional_analysis.get("therapeutic_needs", ["general_support"])
            
            # Select base content template based on emotional state
            if primary_emotion == "distressed":
                base_template = self.content_templates.get("intervention", {})
            elif primary_emotion == "low_mood":
                base_template = self.content_templates.get("afternoon_support", {})
            elif primary_emotion == "positive":
                base_template = self.content_templates.get("motivation", {})
            else:
                base_template = self.content_templates.get(notification_type, {})
            
            # Generate content based on therapeutic needs
            therapeutic_framework = None
            if "validation" in therapeutic_needs:
                therapeutic_framework = self.therapeutic_phrases.get("validation", [])
            elif "reframing" in therapeutic_needs:
                therapeutic_framework = self.therapeutic_phrases.get("reframing", [])
            elif "encouragement" in therapeutic_needs:
                therapeutic_framework = self.therapeutic_phrases.get("encouragement", [])
            else:
                therapeutic_framework = self.therapeutic_phrases.get("grounding", [])
            
            # Select appropriate content
            title = random.choice(base_template.get("titles", ["Wellness Check-in 💙"]))
            message = random.choice(base_template.get("messages", ["Take a moment to check in with yourself."]))
            actions = base_template.get("action_suggestions", ["Log your mood", "Practice mindfulness"])
            
            # Add therapeutic element
            if therapeutic_framework:
                therapeutic_phrase = random.choice(therapeutic_framework)
                message += f" {therapeutic_phrase}"
            
            return {
                "title": title,
                "message": message,
                "action_suggestions": actions,
                "therapeutic_approach": therapeutic_needs[0] if therapeutic_needs else "general_support"
            }
            
        except Exception as e:
            logger.error(f"Error generating ML content: {e}")
            return self._get_fallback_content(notification_type)
    
    def _apply_nlp_personalization(
        self, 
        base_content: Dict[str, Any], 
        user_context: Dict[str, Any], 
        emotional_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply NLP-based personalization to content"""
        try:
            personalized_content = base_content.copy()
            
            # Personalize based on emotional trend
            emotional_trend = emotional_analysis.get("emotional_trend", "stable")
            if emotional_trend == "improving":
                personalized_content["message"] += " You're making great progress!"
            elif emotional_trend == "declining":
                personalized_content["message"] += " Remember, challenging times are temporary."
            
            # Add context-specific elements
            recent_activities = user_context.get("recent_activities", [])
            if "journaling" in recent_activities:
                personalized_content["action_suggestions"].append("Continue your journaling practice")
            if "meditation" in recent_activities:
                personalized_content["action_suggestions"].append("Try another mindfulness session")
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Error applying NLP personalization: {e}")
            return base_content
    
    def _enhance_with_therapeutic_framework(
        self, 
        content: Dict[str, Any], 
        emotional_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance content with evidence-based therapeutic frameworks"""
        try:
            enhanced_content = content.copy()
            therapeutic_needs = emotional_analysis.get("therapeutic_needs", [])
            
            # Apply cognitive behavioral therapy principles
            if "reframing" in therapeutic_needs:
                enhanced_content["action_suggestions"].append("Challenge negative thoughts")
                enhanced_content["therapeutic_approach"] = "cognitive_reframing"
            
            # Apply mindfulness-based interventions
            elif "mindfulness" in therapeutic_needs:
                enhanced_content["action_suggestions"].append("Practice present moment awareness")
                enhanced_content["therapeutic_approach"] = "mindfulness_based"
            
            # Apply behavioral activation
            elif "behavioral_activation" in therapeutic_needs:
                enhanced_content["action_suggestions"].append("Engage in a meaningful activity")
                enhanced_content["therapeutic_approach"] = "behavioral_activation"
            
            # Apply validation therapy
            elif "validation" in therapeutic_needs:
                enhanced_content["action_suggestions"].append("Acknowledge your feelings without judgment")
                enhanced_content["therapeutic_approach"] = "validation_therapy"
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Error enhancing with therapeutic framework: {e}")
            return content
    
    def _calculate_content_confidence(self, content: Dict[str, Any], user_context: Dict[str, Any]) -> float:
        """Calculate confidence score for generated content"""
        try:
            confidence = 0.5  # Base confidence
            
            # Increase confidence based on available data
            if user_context.get("mood_entries"):
                confidence += 0.2
            if user_context.get("journal_entries"):
                confidence += 0.2
            if user_context.get("notification_response_history"):
                confidence += 0.1
            
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating content confidence: {e}")
            return 0.5
    
    def _calculate_ml_personalization_level(
        self, 
        user_context: Dict[str, Any], 
        emotional_analysis: Dict[str, Any]
    ) -> float:
        """Calculate ML-based personalization level"""
        try:
            personalization_score = 0.0
            
            # Data availability factor
            if user_context.get("mood_entries"):
                personalization_score += 0.3
            if user_context.get("journal_entries"):
                personalization_score += 0.3
            if user_context.get("notification_response_history"):
                personalization_score += 0.2
            
            # Emotional analysis depth
            if emotional_analysis.get("sentiment_scores"):
                personalization_score += 0.2
            
            return min(personalization_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating ML personalization level: {e}")
            return 0.3
    
    def _fallback_generate_notification(
        self, 
        notification_type: str, 
        user_context: Dict[str, Any], 
        effectiveness_score: float
    ) -> Dict[str, Any]:
        """Fallback method when ML is not available"""
        try:
            # Use template-based approach
            template = self.content_templates.get(notification_type, self.content_templates.get("morning_check", {}))
            
            title = random.choice(template.get("titles", ["Wellness Check-in 💙"]))
            message = random.choice(template.get("messages", ["Take a moment to check in with yourself."]))
            actions = template.get("action_suggestions", ["Log your mood", "Practice mindfulness"])
            
            # Simple personalization based on context
            message = self._personalize_message(message, user_context, notification_type)
            personalization_level = self._calculate_personalization_level(user_context)
            
            return {
                "title": title,
                "message": message,
                "action_suggestions": random.sample(actions, min(3, len(actions))),
                "notification_type": notification_type,
                "effectiveness_score": effectiveness_score,
                "personalization_level": personalization_level,
                "confidence_score": 0.6,
                "emotional_theme": "neutral",
                "therapeutic_approach": "general_support",
                "ml_method": "template_based",
                "model_version": self.model_version
            }
            
        except Exception as e:
            logger.error(f"Error in fallback content generation: {e}")
            return self._get_fallback_content(notification_type)
    
    def _personalize_message(self, base_message: str, user_context: Dict[str, Any], notification_type: str) -> str:
        """Personalize message based on user context and patterns"""
        # Add context-specific personalization
        current_mood_trend = user_context.get("current_mood_trend", "stable")
        recent_activity = user_context.get("recent_activity", "general")
        
        if notification_type == "afternoon_support" and current_mood_trend == "declining":
            base_message += " Remember, mood dips are temporary and you have the strength to get through this."
        elif notification_type == "morning_check" and recent_activity == "journaling":
            base_message += " Your recent reflections show great self-awareness!"
        elif notification_type == "evening_reflection" and current_mood_trend == "improving":
            base_message += " It looks like you've been making positive progress lately!"
        
        return base_message
    
    def _calculate_personalization_level(self, user_context: Dict[str, Any]) -> str:
        """Calculate the level of personalization possible with current context"""
        context_factors = [
            user_context.get("mood_history_length", 0) > 10,
            user_context.get("journal_entries_count", 0) > 5,
            user_context.get("notification_response_history", []),
            user_context.get("identified_patterns", {})
        ]
        
        personalization_score = sum(1 for factor in context_factors if factor)
        
        if personalization_score >= 3:
            return "high"
        elif personalization_score >= 2:
            return "moderate"
        else:
            return "low"
    
    def generate_personalized_insights(self, user_data: Dict[str, Any], insight_type: str = "weekly_summary") -> List[Dict[str, Any]]:
        """
        Generate AI-powered personalized insights
        
        Args:
            user_data: User's mood and behavior data
            insight_type: Type of insights to generate
            
        Returns:
            List of personalized insights
        """
        try:
            generator_func = self.insight_generators.get(insight_type, self._generate_weekly_summary)
            insights = generator_func(user_data)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return self._get_fallback_insights()
    
    def _generate_weekly_summary(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate weekly mood summary insights"""
        mood_entries = user_data.get("mood_entries", [])
        journal_entries = user_data.get("journal_entries", [])
        
        if not mood_entries:
            return self._get_fallback_insights()
        
        insights = []
        
        # Calculate weekly stats
        mood_scores = [entry["mood_score"] for entry in mood_entries]
        avg_mood = statistics.mean(mood_scores)
        mood_trend = self._calculate_trend(mood_scores)
        
        # Main summary insight
        insights.append({
            "insight_type": "weekly_summary",
            "title": "Your Week in Perspective",
            "content": self._generate_weekly_summary_text(avg_mood, mood_trend, len(mood_entries)),
            "action_suggestions": self._get_weekly_action_suggestions(avg_mood, mood_trend),
            "confidence_score": 0.8,
            "priority": "high"
        })
        
        # Pattern insights
        if len(mood_entries) >= 7:
            pattern_insight = self._identify_weekly_patterns(mood_entries)
            if pattern_insight:
                insights.append(pattern_insight)
        
        # Journaling insights
        if journal_entries:
            journal_insight = self._analyze_journaling_impact(mood_entries, journal_entries)
            if journal_insight:
                insights.append(journal_insight)
        
        return insights
    
    def _generate_weekly_summary_text(self, avg_mood: float, trend: str, entry_count: int) -> str:
        """Generate weekly summary text"""
        mood_descriptor = self._get_mood_descriptor(avg_mood)
        
        base_text = f"This week, your average mood was {mood_descriptor} ({avg_mood:.1f}/10)"
        
        if trend == "improving":
            base_text += " and showing positive improvement! 📈"
        elif trend == "declining":
            base_text += ". You've faced some challenges, which is completely normal. 💙"
        else:
            base_text += " and remained relatively stable. 📊"
        
        base_text += f" You checked in {entry_count} times this week, showing great commitment to your wellness journey."
        
        return base_text
    
    def _get_mood_descriptor(self, avg_mood: float) -> str:
        """Get descriptive text for mood score"""
        if avg_mood >= 8:
            return "excellent"
        elif avg_mood >= 7:
            return "good"
        elif avg_mood >= 6:
            return "okay"
        elif avg_mood >= 5:
            return "challenging"
        else:
            return "difficult"
    
    def _calculate_trend(self, mood_scores: List[float]) -> str:
        """Calculate mood trend direction"""
        if len(mood_scores) < 3:
            return "stable"
        
        # Simple trend calculation using first vs last half
        mid_point = len(mood_scores) // 2
        first_half_avg = statistics.mean(mood_scores[:mid_point])
        second_half_avg = statistics.mean(mood_scores[mid_point:])
        
        diff = second_half_avg - first_half_avg
        
        if diff > 0.5:
            return "improving"
        elif diff < -0.5:
            return "declining"
        else:
            return "stable"
    
    def _get_weekly_action_suggestions(self, avg_mood: float, trend: str) -> List[str]:
        """Get action suggestions based on weekly patterns"""
        suggestions = []
        
        if trend == "improving":
            suggestions.extend([
                "Keep up the great momentum!",
                "Identify what's working well",
                "Share your success with others"
            ])
        elif trend == "declining":
            suggestions.extend([
                "Consider extra self-care this week",
                "Reach out to your support network",
                "Review your coping strategies"
            ])
        else:
            suggestions.extend([
                "Maintain your current wellness practices",
                "Explore new activities",
                "Set a small goal for next week"
            ])
        
        if avg_mood < 6:
            suggestions.append("Consider professional support if feelings persist")
        
        return suggestions[:3]  # Return top 3
    
    def _identify_weekly_patterns(self, mood_entries: List[Dict]) -> Optional[Dict[str, Any]]:
        """Identify notable patterns in weekly mood data"""
        # Analyze by day of week
        daily_moods = {i: [] for i in range(7)}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for entry in mood_entries:
            day = entry["timestamp"].weekday()
            daily_moods[day].append(entry["mood_score"])
        
        # Find patterns
        daily_averages = {}
        for day, moods in daily_moods.items():
            if len(moods) >= 2:
                daily_averages[day] = statistics.mean(moods)
        
        if not daily_averages:
            return None
        
        # Find best and worst days
        best_day = max(daily_averages.keys(), key=lambda d: daily_averages[d])
        worst_day = min(daily_averages.keys(), key=lambda d: daily_averages[d])
        
        content = f"Your mood patterns show {day_names[best_day]}s tend to be your strongest days "
        content += f"(avg: {daily_averages[best_day]:.1f}), while {day_names[worst_day]}s "
        content += f"are more challenging (avg: {daily_averages[worst_day]:.1f}). "
        content += "Knowing this can help you plan support strategies!"
        
        return {
            "insight_type": "pattern_insight",
            "title": "Weekly Pattern Discovery",
            "content": content,
            "action_suggestions": [
                f"Plan extra self-care for {day_names[worst_day]}s",
                f"Leverage your energy on {day_names[best_day]}s",
                "Track what makes good days great"
            ],
            "confidence_score": 0.7,
            "priority": "medium"
        }
    
    def _analyze_journaling_impact(self, mood_entries: List[Dict], journal_entries: List[Dict]) -> Optional[Dict[str, Any]]:
        """Analyze the impact of journaling on mood"""
        if not journal_entries or len(mood_entries) < 5:
            return None
        
        # Simple analysis: look for mood improvements after journaling
        journaling_days = {entry["timestamp"].date() for entry in journal_entries}
        
        mood_improvements = []
        for date in journaling_days:
            day_moods = [
                entry for entry in mood_entries
                if entry["timestamp"].date() == date
            ]
            if len(day_moods) >= 2:
                day_moods.sort(key=lambda x: x["timestamp"])
                improvement = day_moods[-1]["mood_score"] - day_moods[0]["mood_score"]
                mood_improvements.append(improvement)
        
        if mood_improvements:
            avg_improvement = statistics.mean(mood_improvements)
            if avg_improvement > 0.3:
                return {
                    "insight_type": "journaling_impact",
                    "title": "Journaling Benefits",
                    "content": f"Great news! Your mood tends to improve by an average of {avg_improvement:.1f} points on days when you journal. This suggests journaling is a valuable tool for your mental wellness.",
                    "action_suggestions": [
                        "Continue your journaling practice",
                        "Try journaling during challenging moments",
                        "Experiment with different journaling styles"
                    ],
                    "confidence_score": 0.8,
                    "priority": "high"
                }
        
        return None
    
    def _generate_pattern_insights(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights about user patterns"""
        # This would contain more sophisticated pattern analysis
        return []
    
    def _generate_improvement_suggestions(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized improvement suggestions"""
        # This would analyze user data to suggest specific improvements
        return []
    
    def _generate_celebration_insights(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights celebrating user progress"""
        # This would identify positive changes and progress to celebrate
        return []
    
    def _generate_predictive_insights(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate predictive insights about future patterns"""
        # This would use ML to predict future mood patterns and risks
        return []
    
    def _get_fallback_content(self, notification_type: str) -> Dict[str, Any]:
        """Get fallback content when personalization fails"""
        return {
            "title": "Wellness Check-in 💙",
            "message": "Take a moment to check in with yourself. Your mental wellness matters.",
            "action_suggestions": ["Log your mood", "Take deep breaths", "Practice self-compassion"],
            "notification_type": notification_type,
            "effectiveness_score": 6.0,
            "personalization_level": "low"
        }
    
    def _get_fallback_insights(self) -> List[Dict[str, Any]]:
        """Get fallback insights when generation fails"""
        return [
            {
                "insight_type": "general",
                "title": "Your Wellness Journey",
                "content": "Every step you take toward mental wellness matters. Keep going!",
                "action_suggestions": ["Continue tracking your mood", "Practice self-care", "Stay connected"],
                "confidence_score": 0.5,
                "priority": "medium"
            }
        ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the content engine"""
        return {
            "model_type": "template_based_generator",
            "content_templates_loaded": len(self.content_templates),
            "insight_generators_available": len(self.insight_generators),
            "personalization_levels": ["low", "moderate", "high"],
            "supported_notification_types": list(self.content_templates.keys()),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def retrain_model(self) -> bool:
        """Retrain the content model (placeholder for future ML)"""
        logger.info("Content engine model retrain completed (template-based system)")
        return True
