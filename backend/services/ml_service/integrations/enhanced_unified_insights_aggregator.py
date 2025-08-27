from __future__ import annotations

"""Enhanced Unified Insights Aggregator (E3)

Advanced aggregation with pluggable ML models:
- Sentiment analysis
- Pattern detection  
- Model versioning and A/B testing
- Enhanced aggregation algorithms
"""
import sys
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import logging
import numpy as np

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.models import MoodEntry
from .unified_insights_cache import get_cache
from .ml_model_registry import model_registry, ModelType, initialize_default_models

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 120

cache = get_cache()

class EnhancedUnifiedInsightsAggregator:
    """Enhanced aggregator with ML model integration"""
    
    def __init__(self):
        self.models_initialized = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models on first use"""
        if not self.models_initialized:
            try:
                results = initialize_default_models()
                self.models_initialized = True
                logger.info(f"ML models initialized: {results}")
            except Exception as e:
                logger.error(f"Failed to initialize ML models: {e}")
                self.models_initialized = False

    def clear_cache(self):
        """Clear cache for testing"""
        cache.clear()

    def _cache_key(self, user_id: str) -> str:
        return f"unified_insights:enhanced:{user_id}:v2"

    def get_unified_insights(self, db: Session, user_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Get enhanced unified insights with ML analysis"""
        start_time = datetime.now(timezone.utc)
        key = self._cache_key(user_id)
        subcall_count = 0
        
        if not force_refresh:
            cached = cache.get(key)
            if cached:
                latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                logger.info(
                    "Enhanced unified insights cache hit",
                    extra={
                        "event": "enhanced_unified_insights_cache",
                        "status": "hit",
                        "user_id": user_id,
                        "latency_ms": latency_ms,
                        "subcall_count": 0
                    }
                )
                cached['cache_info']['hit'] = True
                return cached
        
        # Ensure models are initialized
        if not self.models_initialized:
            self._initialize_models()
        
        # Collect base mood statistics
        mood_stats = self._gather_mood_stats(db, user_id)
        subcall_count += 1
        
        # Collect raw mood entries for ML analysis
        mood_entries = self._get_mood_entries(db, user_id)
        subcall_count += 1
        
        # Run ML analysis
        ml_insights = self._run_ml_analysis(user_id, mood_entries, mood_stats)
        subcall_count += 1
        
        # Build enhanced response
        response = self._build_enhanced_response(user_id, mood_stats, ml_insights)
        cache.set(key, response, CACHE_TTL_SECONDS)
        
        latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        logger.info(
            "Enhanced unified insights aggregated",
            extra={
                "event": "enhanced_unified_insights_cache",
                "status": "miss",
                "user_id": user_id,
                "latency_ms": latency_ms,
                "subcall_count": subcall_count,
                "ml_models_used": len(ml_insights.get("models_used", [])),
                "data_quality": response['aggregated_insights']['insights_summary']['data_quality'],
                "confidence_score": response['aggregated_insights']['insights_summary']['confidence_score']
            }
        )
        
        response['cache_info']['hit'] = False
        return response
    
    def _get_mood_entries(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Get mood entries for ML analysis"""
        try:
            entries: List[MoodEntry] = list(
                db.query(MoodEntry)
                .filter(MoodEntry.user_id == user_id)
                .order_by(MoodEntry.created_at.desc())
                .limit(100)
                .all()
            )
            
            # Convert to plain Python objects for ML processing
            processed_entries = []
            for e in entries:
                # Handle both real objects and mocks robustly
                mood_score = getattr(e, 'mood_score', 0)
                if hasattr(mood_score, '__call__'):  # Mock object
                    mood_score = 0
                mood_score = float(mood_score or 0)
                
                energy_level = getattr(e, 'energy_level', 5)
                if hasattr(energy_level, '__call__'):  # Mock object
                    energy_level = 5
                energy_level = float(energy_level or 5)
                
                stress_level = getattr(e, 'stress_level', 5)
                if hasattr(stress_level, '__call__'):  # Mock object
                    stress_level = 5
                stress_level = float(stress_level or 5)
                
                notes = getattr(e, 'notes', '')
                if hasattr(notes, '__call__'):  # Mock object
                    notes = ''
                notes = str(notes or '')
                
                created_at = getattr(e, 'created_at', None)
                
                processed_entries.append({
                    'mood_score': mood_score,
                    'energy_level': energy_level,
                    'stress_level': stress_level,
                    'notes': notes,
                    'created_at': created_at
                })
            
            return processed_entries
        except Exception as e:
            logger.error(f"Failed to get mood entries for ML analysis: {e}")
            return []
    
    def _run_ml_analysis(self, user_id: str, mood_entries: List[Dict[str, Any]], 
                        mood_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Run ML analysis on mood data"""
        ml_insights = {
            "sentiment_analysis": {},
            "pattern_detection": {},
            "models_used": [],
            "analysis_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if not mood_entries:
            return ml_insights
        
        try:
            # Prepare data for ML models
            mood_scores = [entry['mood_score'] for entry in mood_entries]
            energy_scores = [entry['energy_level'] for entry in mood_entries]
            stress_scores = [entry['stress_level'] for entry in mood_entries]
            notes_text = " ".join([entry['notes'] for entry in mood_entries if entry['notes']])
            timestamps = [entry['created_at'] for entry in mood_entries if entry['created_at']]
            
            # Run sentiment analysis
            sentiment_model = model_registry.get_model(ModelType.SENTIMENT_ANALYZER, user_id)
            if sentiment_model and sentiment_model.is_ready():
                sentiment_data = {
                    "text": notes_text,
                    "mood_scores": mood_scores
                }
                sentiment_result = sentiment_model.predict(sentiment_data)
                ml_insights["sentiment_analysis"] = sentiment_result
                ml_insights["models_used"].append("sentiment_analyzer")
            
            # Run pattern detection
            pattern_model = model_registry.get_model(ModelType.PATTERN_DETECTOR, user_id)
            if pattern_model and pattern_model.is_ready():
                pattern_data = {
                    "mood_entries": mood_scores,
                    "timestamps": timestamps,
                    "energy_levels": energy_scores,
                    "stress_levels": stress_scores
                }
                pattern_result = pattern_model.predict(pattern_data)
                ml_insights["pattern_detection"] = pattern_result
                ml_insights["models_used"].append("pattern_detector")
            
            # Enhanced trend analysis using multiple signals
            enhanced_trends = self._analyze_enhanced_trends(mood_scores, energy_scores, stress_scores)
            ml_insights["enhanced_trends"] = enhanced_trends
            ml_insights["models_used"].append("enhanced_trend_analyzer")
            
        except Exception as e:
            logger.error(f"ML analysis failed: {e}")
            ml_insights["error"] = str(e)
        
        return ml_insights
    
    def _analyze_enhanced_trends(self, mood_scores: List[float], energy_scores: List[float], 
                               stress_scores: List[float]) -> Dict[str, Any]:
        """Enhanced trend analysis using multiple signals"""
        try:
            if len(mood_scores) < 3:
                return {
                    "trend_direction": "insufficient_data",
                    "trend_strength": 0.0,
                    "multi_signal_analysis": {}
                }
            
            # Multi-signal trend analysis
            signals = {
                "mood": mood_scores,
                "energy": energy_scores,
                "stress": stress_scores
            }
            
            trends = {}
            overall_scores = []
            
            for signal_name, scores in signals.items():
                if len(scores) >= 3:
                    # Calculate trend using linear regression
                    x = np.arange(len(scores))
                    slope = np.polyfit(x, scores, 1)[0]
                    
                    # Calculate trend strength (R-squared)
                    y_pred = np.polyval([slope, np.mean(scores)], x)
                    ss_res = np.sum((scores - y_pred) ** 2)
                    ss_tot = np.sum((scores - np.mean(scores)) ** 2)
                    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                    
                    # Categorize trend
                    if abs(slope) < 0.1:
                        direction = "stable"
                    elif slope > 0:
                        direction = "improving"
                    else:
                        direction = "declining"
                    
                    trends[signal_name] = {
                        "slope": round(slope, 4),
                        "direction": direction,
                        "strength": round(abs(slope), 3),
                        "confidence": round(r_squared, 3)
                    }
                    
                    # Adjust for stress (inverse relationship)
                    if signal_name == "stress":
                        adjusted_slope = -slope  # Inverse stress trend
                    else:
                        adjusted_slope = slope
                    
                    overall_scores.append(adjusted_slope)
            
            # Overall trend calculation
            if overall_scores:
                overall_slope = np.mean(overall_scores)
                overall_strength = np.mean([abs(score) for score in overall_scores])
                
                if abs(overall_slope) < 0.1:
                    overall_direction = "stable"
                elif overall_slope > 0:
                    overall_direction = "improving"
                else:
                    overall_direction = "declining"
            else:
                overall_direction = "insufficient_data"
                overall_strength = 0.0
            
            # Calculate weekly and monthly changes if enough data
            weekly_change = 0
            monthly_change = 0
            
            if len(mood_scores) >= 7:
                recent_week = mood_scores[:7]
                previous_week = mood_scores[7:14] if len(mood_scores) >= 14 else mood_scores[7:]
                if previous_week:
                    weekly_change = np.mean(recent_week) - np.mean(previous_week)
            
            if len(mood_scores) >= 30:
                recent_month = mood_scores[:30]
                previous_month = mood_scores[30:60] if len(mood_scores) >= 60 else mood_scores[30:]
                if previous_month:
                    monthly_change = np.mean(recent_month) - np.mean(previous_month)
            
            return {
                "trend_direction": overall_direction,
                "trend_strength": round(overall_strength, 3),
                "multi_signal_analysis": trends,
                "weekly_change": round(weekly_change, 2),
                "monthly_change": round(monthly_change, 2),
                "confidence": round(np.mean([t.get("confidence", 0) for t in trends.values()]), 3) if trends else 0.0
            }
            
        except Exception as e:
            logger.error(f"Enhanced trend analysis failed: {e}")
            return {
                "trend_direction": "error",
                "trend_strength": 0.0,
                "error": str(e)
            }
    
    def _gather_mood_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Gather basic mood statistics (from original aggregator)"""
        entries: List[MoodEntry] = list(
            db.query(MoodEntry)
            .filter(MoodEntry.user_id == user_id)
            .order_by(MoodEntry.created_at.desc())
            .limit(100)
            .all()
        )
        
        # Force load attributes to plain Python objects to avoid analyzer confusion
        py_entries: List[Dict[str, Any]] = []
        for e in entries:
            # More robust attribute extraction for both real objects and mocks
            mood_score = getattr(e, 'mood_score', 0)
            if hasattr(mood_score, '__call__'):  # Mock object
                mood_score = 0
            mood_score = int(mood_score or 0)
            
            energy_level = getattr(e, 'energy_level', 5)
            if hasattr(energy_level, '__call__'):  # Mock object
                energy_level = 5
            energy_level = int(energy_level or 5)
            
            created_at = getattr(e, 'created_at', None)
            
            py_entries.append({
                'created_at': created_at,
                'mood_score': mood_score,
                'energy_level': energy_level
            })
        
        if not py_entries:
            return {
                'average_mood': 0,
                'mood_variability': 0,
                'best_day': '',
                'energy_peak': '',
                'mood_streak': 0,
                'total_entries': 0,
                'days_tracked': 0
            }
        
        scores = [e['mood_score'] for e in py_entries]
        avg = sum(scores) / len(scores) if scores else 0
        variance = sum((s - avg) ** 2 for s in scores) / len(scores) if scores else 0
        unique_dates = {e['created_at'].date() for e in py_entries if e['created_at']}
        
        # Streak calculation
        sorted_by_date = sorted(py_entries, key=lambda e: e['created_at'])
        daily: Dict[Any, List[int]] = {}
        for e in sorted_by_date:
            created = e['created_at']
            if not created:
                continue
            d = created.date()
            daily.setdefault(d, []).append(e['mood_score'])
        
        daily_avg: Dict[Any, float] = {d: (sum(v)/len(v) if v else 0) for d, v in daily.items()}
        streak = 0
        for d in sorted(daily_avg.keys(), reverse=True):
            if daily_avg[d] >= avg:
                streak += 1
            else:
                break
        
        # Best day of week
        day_moods: Dict[int, List[int]] = {}
        for e in py_entries:
            created = e['created_at']
            if not created:
                continue
            day_moods.setdefault(created.weekday(), []).append(e['mood_score'])
        
        day_names = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        best_day = ''
        if day_moods:
            best_idx = max(day_moods.keys(), key=lambda k: sum(day_moods[k])/len(day_moods[k]) if day_moods[k] else 0)
            best_day = day_names[best_idx]
        
        # Energy peak
        hour_energy: Dict[int, List[int]] = {}
        for e in py_entries:
            created = e['created_at']
            if not created:
                continue
            hour_energy.setdefault(created.hour, []).append(e['energy_level'])
        
        energy_peak = ''
        if hour_energy:
            peak_hour = max(hour_energy.keys(), key=lambda h: sum(hour_energy[h])/len(hour_energy[h]) if hour_energy[h] else 0)
            energy_peak = f"{peak_hour:02d}:00"
        
        return {
            'average_mood': round(avg,1),
            'mood_variability': round(variance ** 0.5, 1) if variance else 0,
            'best_day': best_day,
            'energy_peak': energy_peak,
            'mood_streak': streak,
            'total_entries': len(py_entries),
            'days_tracked': len(unique_dates)
        }
    
    def _build_enhanced_response(self, user_id: str, mood_stats: Dict[str, Any], 
                               ml_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Build enhanced response with ML insights"""
        # Enhanced data quality calculation
        data_quality = self._calculate_enhanced_data_quality(mood_stats, ml_insights)
        
        # Enhanced confidence calculation
        confidence = self._calculate_enhanced_confidence(mood_stats, ml_insights)
        
        # Get sentiment insights
        sentiment = ml_insights.get("sentiment_analysis", {})
        
        # Get pattern insights  
        patterns = ml_insights.get("pattern_detection", {})
        
        # Get enhanced trends
        enhanced_trends = ml_insights.get("enhanced_trends", {})
        
        # Build the enhanced unified insights response
        response: Dict[str, Any] = {
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'aggregated_insights': {
                'mood': {
                    'current_score': int(mood_stats['average_mood'] * 10) if mood_stats['average_mood'] else 0,
                    'average_score': round(mood_stats['average_mood'], 1) if mood_stats['average_mood'] else 0,
                    'total_entries': mood_stats['total_entries'],
                    'days_tracked': mood_stats.get('days_tracked', 0),
                    'mood_streak': mood_stats['mood_streak'],
                    'best_day': mood_stats['best_day'],
                    'energy_peak': mood_stats['energy_peak'],
                    'mood_variability': mood_stats['mood_variability'],
                    # Enhanced mood insights
                    'sentiment_score': sentiment.get('sentiment_score', 5.0),
                    'sentiment_label': sentiment.get('sentiment_label', 'neutral'),
                    'dominant_pattern': patterns.get('dominant_pattern', 'unknown')
                },
                'trends': {
                    'direction': enhanced_trends.get('trend_direction', 'stable'),
                    'weekly_change': enhanced_trends.get('weekly_change', 0),
                    'monthly_change': enhanced_trends.get('monthly_change', 0),
                    'trend_strength': enhanced_trends.get('trend_strength', 0.0),
                    'trend_confidence': enhanced_trends.get('confidence', 0.0)
                },
                'patterns': {
                    'detected_patterns': patterns.get('patterns_detected', []),
                    'pattern_strength': patterns.get('pattern_strength', 0.0),
                    'pattern_confidence': patterns.get('confidence', 0.0)
                },
                'sentiment': {
                    'overall_sentiment': sentiment.get('sentiment_label', 'neutral'),
                    'sentiment_score': sentiment.get('sentiment_score', 5.0),
                    'sentiment_confidence': sentiment.get('confidence', 0.1),
                    'polarity': sentiment.get('polarity', 0.0),
                    'subjectivity': sentiment.get('subjectivity', 0.5)
                },
                'insights_summary': {
                    'total_insights': len([x for x in [sentiment, patterns, enhanced_trends] if x]),
                    'confidence_score': confidence,
                    'data_quality': data_quality,
                    'dominant_mood': self._dominant_label(mood_stats['average_mood']),
                    'ml_models_used': ml_insights.get('models_used', []),
                    'analysis_version': 'v2_enhanced'
                }
            },
            'ml_insights': {
                'sentiment_analysis': sentiment,
                'pattern_detection': patterns,
                'enhanced_trends': enhanced_trends,
                'models_used': ml_insights.get('models_used', []),
                'analysis_timestamp': ml_insights.get('analysis_timestamp')
            },
            'cache_info': {
                'hit': False,  # Will be updated by caller
                'ttl_seconds': CACHE_TTL_SECONDS,
                'last_updated': datetime.now(timezone.utc).isoformat()
            },
            'version': 'v2_enhanced'
        }
        
        return response
    
    def _calculate_enhanced_data_quality(self, mood_stats: Dict[str, Any], 
                                       ml_insights: Dict[str, Any]) -> int:
        """Calculate enhanced data quality score"""
        base_quality = 0
        
        # Base score from entry count
        if mood_stats['total_entries'] >= 5:
            base_quality = min(int((mood_stats['total_entries']/30)*70), 70)
        
        # Bonus for ML model availability
        ml_bonus = len(ml_insights.get('models_used', [])) * 10
        
        # Bonus for pattern detection
        if ml_insights.get('pattern_detection', {}).get('pattern_strength', 0) > 0.3:
            ml_bonus += 10
        
        # Bonus for sentiment analysis
        if ml_insights.get('sentiment_analysis', {}).get('confidence', 0) > 0.5:
            ml_bonus += 10
        
        return min(base_quality + ml_bonus, 100)
    
    def _calculate_enhanced_confidence(self, mood_stats: Dict[str, Any], 
                                     ml_insights: Dict[str, Any]) -> float:
        """Calculate enhanced confidence score"""
        base_confidence = 0.4 if mood_stats['total_entries'] >= 5 else 0.1
        
        # Average ML model confidences
        ml_confidences = []
        
        sentiment_conf = ml_insights.get('sentiment_analysis', {}).get('confidence', 0)
        if sentiment_conf > 0:
            ml_confidences.append(sentiment_conf)
        
        pattern_conf = ml_insights.get('pattern_detection', {}).get('confidence', 0)
        if pattern_conf > 0:
            ml_confidences.append(pattern_conf)
        
        trend_conf = ml_insights.get('enhanced_trends', {}).get('confidence', 0)
        if trend_conf > 0:
            ml_confidences.append(trend_conf)
        
        if ml_confidences:
            ml_avg_confidence = np.mean(ml_confidences)
            # Weighted average of base and ML confidence
            enhanced_confidence = (base_confidence * 0.3) + (ml_avg_confidence * 0.7)
        else:
            enhanced_confidence = base_confidence
        
        return round(min(enhanced_confidence, 1.0), 3)
    
    def _dominant_label(self, avg: float) -> str:
        """Get dominant mood label"""
        if not avg:
            return ''
        if avg >= 7: return 'great'
        if avg >= 6: return 'good'
        if avg >= 5: return 'okay'
        if avg >= 4: return 'low'
        return 'struggling'
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of ML models"""
        return model_registry.get_model_status()

# Create enhanced aggregator instance
enhanced_aggregator = EnhancedUnifiedInsightsAggregator()
