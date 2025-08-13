from __future__ import annotations

"""ML Model Registry for Enhanced Unified Insights (E3)

Pluggable ML model system supporting:
- Sentiment analysis
- Pattern detection  
- Model versioning and A/B testing
- Enhanced aggregation algorithms
"""
import json
import os
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, timezone
from enum import Enum
import numpy as np

# Lightweight model imports
try:
    from textblob import TextBlob  # Lightweight sentiment analysis
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Types of ML models supported"""
    SENTIMENT_ANALYZER = "sentiment_analyzer"
    PATTERN_DETECTOR = "pattern_detector"
    TREND_PREDICTOR = "trend_predictor"
    MOOD_CLASSIFIER = "mood_classifier"
    ANOMALY_DETECTOR = "anomaly_detector"

class ModelVersion(Enum):
    """Model versions for A/B testing"""
    V1_BASELINE = "v1_baseline"
    V2_ENHANCED = "v2_enhanced"
    V3_EXPERIMENTAL = "v3_experimental"

class InsightModel(ABC):
    """Abstract base class for all ML models"""
    
    def __init__(self, model_type: ModelType, version: ModelVersion):
        self.model_type = model_type
        self.version = version
        self.is_loaded = False
        self.confidence_threshold = 0.5
        self.metadata = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "model_type": model_type.value,
            "version": version.value
        }
    
    @abstractmethod
    def load(self) -> bool:
        """Load the model - return True if successful"""
        pass
    
    @abstractmethod
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions on input data"""
        pass
    
    @abstractmethod
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        pass
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self.is_loaded

class SentimentAnalyzer(InsightModel):
    """Lightweight sentiment analysis using TextBlob"""
    
    def __init__(self, version: ModelVersion = ModelVersion.V1_BASELINE):
        super().__init__(ModelType.SENTIMENT_ANALYZER, version)
        self.analyzer = None
    
    def load(self) -> bool:
        """Load the sentiment analyzer"""
        try:
            if not TEXTBLOB_AVAILABLE:
                logger.warning("TextBlob not available, using fallback sentiment analysis")
                self.is_loaded = True  # Use fallback
                return True
            
            # TextBlob doesn't need explicit loading
            self.is_loaded = True
            logger.info(f"Sentiment analyzer {self.version.value} loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load sentiment analyzer: {e}")
            return False
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of text data"""
        if not self.is_loaded:
            return {"error": "Model not loaded"}
        
        text_data = data.get("text", "")
        mood_scores = data.get("mood_scores", [])
        
        try:
            if TEXTBLOB_AVAILABLE and text_data:
                # Use TextBlob for text sentiment
                blob = TextBlob(text_data)
                polarity = blob.sentiment.polarity  # -1 to 1
                subjectivity = blob.sentiment.subjectivity  # 0 to 1
                
                # Convert to 0-10 scale
                sentiment_score = (polarity + 1) * 5  # Convert -1:1 to 0:10
            else:
                # Fallback: derive sentiment from mood scores
                if mood_scores:
                    sentiment_score = np.mean(mood_scores)
                else:
                    sentiment_score = 5.0  # Neutral
                polarity = (sentiment_score - 5) / 5  # Convert to -1:1
                subjectivity = 0.5  # Default
            
            # Determine sentiment label
            if sentiment_score >= 7:
                label = "very_positive"
            elif sentiment_score >= 6:
                label = "positive"
            elif sentiment_score >= 4:
                label = "neutral"
            elif sentiment_score >= 2:
                label = "negative"
            else:
                label = "very_negative"
            
            confidence = min(abs(polarity) + 0.3, 1.0)  # Higher confidence for extreme sentiments
            
            return {
                "sentiment_score": round(sentiment_score, 2),
                "sentiment_label": label,
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "confidence": round(confidence, 3),
                "model_version": self.version.value
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                "sentiment_score": 5.0,
                "sentiment_label": "neutral",
                "confidence": 0.1,
                "error": str(e)
            }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for sentiment analysis"""
        return {
            "text_polarity": 0.7,
            "text_subjectivity": 0.3,
            "mood_scores": 0.5 if not TEXTBLOB_AVAILABLE else 0.2
        }

class PatternDetector(InsightModel):
    """Lightweight pattern detection using clustering"""
    
    def __init__(self, version: ModelVersion = ModelVersion.V1_BASELINE):
        super().__init__(ModelType.PATTERN_DETECTOR, version)
        self.clusterer = None
        self.vectorizer = None
    
    def load(self) -> bool:
        """Load the pattern detector"""
        try:
            if not SKLEARN_AVAILABLE:
                logger.warning("Scikit-learn not available, using fallback pattern detection")
                self.is_loaded = True
                return True
            
            # Initialize lightweight clustering
            self.clusterer = KMeans(n_clusters=3, random_state=42, n_init=10)
            self.vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
            self.is_loaded = True
            logger.info(f"Pattern detector {self.version.value} loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load pattern detector: {e}")
            return False
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect patterns in user behavior/mood data"""
        if not self.is_loaded:
            return {"error": "Model not loaded"}
        
        mood_data = data.get("mood_entries", [])
        time_data = data.get("timestamps", [])
        
        try:
            if not mood_data:
                return {
                    "patterns_detected": [],
                    "pattern_strength": 0.0,
                    "dominant_pattern": "insufficient_data",
                    "confidence": 0.1
                }
            
            # Simple pattern detection based on time and mood
            patterns = []
            
            # Daily pattern detection
            if len(mood_data) >= 7:
                daily_pattern = self._detect_daily_patterns(mood_data, time_data)
                patterns.append(daily_pattern)
            
            # Trend pattern detection
            if len(mood_data) >= 3:
                trend_pattern = self._detect_trend_patterns(mood_data)
                patterns.append(trend_pattern)
            
            # Consistency pattern
            if len(mood_data) >= 5:
                consistency_pattern = self._detect_consistency_patterns(mood_data)
                patterns.append(consistency_pattern)
            
            # Calculate overall pattern strength
            pattern_strength = np.mean([p.get("strength", 0) for p in patterns if p])
            
            # Determine dominant pattern
            dominant = max(patterns, key=lambda x: x.get("strength", 0)) if patterns else None
            
            return {
                "patterns_detected": patterns,
                "pattern_strength": round(pattern_strength, 3),
                "dominant_pattern": dominant.get("type", "none") if dominant else "none",
                "confidence": min(pattern_strength + 0.2, 1.0),
                "model_version": self.version.value
            }
            
        except Exception as e:
            logger.error(f"Pattern detection error: {e}")
            return {
                "patterns_detected": [],
                "pattern_strength": 0.0,
                "dominant_pattern": "error",
                "confidence": 0.1,
                "error": str(e)
            }
    
    def _detect_daily_patterns(self, mood_data: List[float], time_data: List[datetime]) -> Dict[str, Any]:
        """Detect daily patterns in mood data"""
        if not time_data or len(time_data) != len(mood_data):
            return {"type": "daily", "strength": 0.0, "description": "insufficient_time_data"}
        
        # Group by hour of day
        hourly_moods = {}
        for mood, timestamp in zip(mood_data, time_data):
            if timestamp:
                hour = timestamp.hour
                if hour not in hourly_moods:
                    hourly_moods[hour] = []
                hourly_moods[hour].append(mood)
        
        if len(hourly_moods) < 3:
            return {"type": "daily", "strength": 0.0, "description": "insufficient_hourly_data"}
        
        # Calculate variance between hours
        hourly_avgs = {hour: np.mean(moods) for hour, moods in hourly_moods.items()}
        variance = np.var(list(hourly_avgs.values()))
        
        # Pattern strength based on variance
        strength = min(variance / 10.0, 1.0)  # Normalize to 0-1
        
        best_hour = max(hourly_avgs.keys(), key=lambda x: hourly_avgs[x])
        worst_hour = min(hourly_avgs.keys(), key=lambda x: hourly_avgs[x])
        
        return {
            "type": "daily",
            "strength": strength,
            "description": f"mood_varies_by_hour",
            "details": {
                "best_hour": best_hour,
                "worst_hour": worst_hour,
                "variance": round(variance, 2)
            }
        }
    
    def _detect_trend_patterns(self, mood_data: List[float]) -> Dict[str, Any]:
        """Detect trend patterns in mood data"""
        if len(mood_data) < 3:
            return {"type": "trend", "strength": 0.0, "description": "insufficient_data"}
        
        # Simple linear trend calculation
        x = np.arange(len(mood_data))
        slope = np.polyfit(x, mood_data, 1)[0]
        
        # Categorize trend
        if abs(slope) < 0.1:
            trend_type = "stable"
        elif slope > 0:
            trend_type = "improving"
        else:
            trend_type = "declining"
        
        strength = min(abs(slope), 1.0)
        
        return {
            "type": "trend",
            "strength": strength,
            "description": trend_type,
            "details": {
                "slope": round(slope, 3),
                "direction": trend_type
            }
        }
    
    def _detect_consistency_patterns(self, mood_data: List[float]) -> Dict[str, Any]:
        """Detect consistency patterns in mood data"""
        if len(mood_data) < 5:
            return {"type": "consistency", "strength": 0.0, "description": "insufficient_data"}
        
        # Calculate coefficient of variation
        mean_mood = np.mean(mood_data)
        std_mood = np.std(mood_data)
        cv = std_mood / mean_mood if mean_mood > 0 else 1.0
        
        # Consistency strength (lower CV = higher consistency)
        consistency = max(0, 1 - cv)
        
        if consistency > 0.8:
            pattern_type = "very_consistent"
        elif consistency > 0.6:
            pattern_type = "consistent"
        elif consistency > 0.4:
            pattern_type = "somewhat_variable"
        else:
            pattern_type = "highly_variable"
        
        return {
            "type": "consistency",
            "strength": consistency,
            "description": pattern_type,
            "details": {
                "coefficient_of_variation": round(cv, 3),
                "consistency_score": round(consistency, 3)
            }
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance for pattern detection"""
        return {
            "temporal_patterns": 0.4,
            "trend_analysis": 0.3,
            "consistency_analysis": 0.3
        }

class ModelRegistry:
    """Registry for managing ML models with versioning and A/B testing"""
    
    def __init__(self):
        self.models: Dict[str, Dict[str, InsightModel]] = {}
        self.active_versions: Dict[ModelType, ModelVersion] = {}
        self.ab_test_config: Dict[ModelType, Dict[str, float]] = {}
        self.model_performance: Dict[str, Dict[str, float]] = {}
    
    def register_model(self, model: InsightModel) -> bool:
        """Register a new model"""
        try:
            model_key = model.model_type.value
            version_key = model.version.value
            
            if model_key not in self.models:
                self.models[model_key] = {}
            
            self.models[model_key][version_key] = model
            
            # Set as active if first version or marked as default
            if model.model_type not in self.active_versions:
                self.active_versions[model.model_type] = model.version
            
            logger.info(f"Registered model {model_key} version {version_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to register model: {e}")
            return False
    
    def load_models(self) -> Dict[str, bool]:
        """Load all registered models"""
        results = {}
        
        for model_type, versions in self.models.items():
            for version, model in versions.items():
                key = f"{model_type}_{version}"
                results[key] = model.load()
        
        return results
    
    def get_model(self, model_type: ModelType, user_id: Optional[str] = None) -> Optional[InsightModel]:
        """Get model for inference with A/B testing support"""
        try:
            # Check if A/B testing is configured
            if model_type in self.ab_test_config and user_id:
                version = self._select_ab_version(model_type, user_id)
            else:
                version = self.active_versions.get(model_type)
            
            if not version:
                return None
            
            model_key = model_type.value
            version_key = version.value
            
            return self.models.get(model_key, {}).get(version_key)
        except Exception as e:
            logger.error(f"Failed to get model {model_type}: {e}")
            return None
    
    def _select_ab_version(self, model_type: ModelType, user_id: str) -> ModelVersion:
        """Select model version for A/B testing based on user_id"""
        ab_config = self.ab_test_config.get(model_type, {})
        
        # Use user_id hash to consistently assign users to test groups
        user_hash = hash(user_id) % 100
        
        cumulative = 0
        for version_str, percentage in ab_config.items():
            cumulative += percentage * 100
            if user_hash < cumulative:
                return ModelVersion(version_str)
        
        # Fallback to active version
        return self.active_versions.get(model_type, ModelVersion.V1_BASELINE)
    
    def configure_ab_test(self, model_type: ModelType, version_distribution: Dict[str, float]):
        """Configure A/B testing for a model type"""
        # Validate percentages sum to 1.0
        total = sum(version_distribution.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Version percentages must sum to 1.0, got {total}")
        
        self.ab_test_config[model_type] = version_distribution
        logger.info(f"Configured A/B test for {model_type.value}: {version_distribution}")
    
    def record_performance(self, model_type: ModelType, version: ModelVersion, 
                          metrics: Dict[str, float]):
        """Record model performance metrics"""
        key = f"{model_type.value}_{version.value}"
        
        if key not in self.model_performance:
            self.model_performance[key] = {}
        
        self.model_performance[key].update(metrics)
        self.model_performance[key]["last_updated"] = datetime.now(timezone.utc).timestamp()
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all registered models"""
        status = {
            "registered_models": {},
            "active_versions": {mt.value: mv.value for mt, mv in self.active_versions.items()},
            "ab_tests": {mt.value: config for mt, config in self.ab_test_config.items()},
            "model_count": sum(len(versions) for versions in self.models.values())
        }
        
        for model_type, versions in self.models.items():
            status["registered_models"][model_type] = {}
            for version, model in versions.items():
                status["registered_models"][model_type][version] = {
                    "is_ready": model.is_ready(),
                    "metadata": model.metadata,
                    "performance": self.model_performance.get(f"{model_type}_{version}", {})
                }
        
        return status

# Global model registry instance
model_registry = ModelRegistry()

def initialize_default_models():
    """Initialize default lightweight models"""
    try:
        # Register sentiment analyzer
        sentiment_v1 = SentimentAnalyzer(ModelVersion.V1_BASELINE)
        model_registry.register_model(sentiment_v1)
        
        # Register pattern detector
        pattern_v1 = PatternDetector(ModelVersion.V1_BASELINE)
        model_registry.register_model(pattern_v1)
        
        # Load all models
        results = model_registry.load_models()
        
        logger.info(f"Initialized ML models: {results}")
        return results
    except Exception as e:
        logger.error(f"Failed to initialize default models: {e}")
        return {}
