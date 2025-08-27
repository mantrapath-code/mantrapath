"""Unified Insights Aggregator (E2)

Collects and merges multiple insight sources into the unified contract consumed by
frontend unifiedInsightService. Initial scope: mood + basic statistics.
Future enrichment: ML personalized insights, correlations, community metrics.
"""
from __future__ import annotations
import sys
import os
from typing import Any, Dict, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from shared.models import MoodEntry  # later extend: JournalEntry
from .unified_insights_cache import get_cache
import logging

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 120

cache = get_cache()

class UnifiedInsightsAggregator:
    def __init__(self):
        pass

    def clear_cache(self):
        """Clear cache for testing"""
        cache.clear()

    def _cache_key(self, user_id: str) -> str:
        return f"unified:{user_id}:v1"

    def get_unified_insights(self, db: Session, user_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        key = self._cache_key(user_id)
        subcall_count = 0
        
        if not force_refresh:
            cached = cache.get(key)
            if cached:
                latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                logger.info(
                    "Unified insights cache hit",
                    extra={
                        "event": "unified_insights_cache",
                        "status": "hit",
                        "user_id": user_id,
                        "latency_ms": latency_ms,
                        "subcall_count": 0
                    }
                )
                cached['cache_info']['hit'] = True
                return cached
        
        # Collect sources (incrementally add more)
        mood_stats = self._gather_mood_stats(db, user_id)
        subcall_count += 1
        
        # Build response
        response = self._build_response(user_id, mood_stats)
        cache.set(key, response, CACHE_TTL_SECONDS)
        
        latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        logger.info(
            "Unified insights aggregated",
            extra={
                "event": "unified_insights_cache",
                "status": "miss",
                "user_id": user_id,
                "latency_ms": latency_ms,
                "subcall_count": subcall_count,
                "data_quality": response['aggregated_insights']['insights_summary']['data_quality'],
                "confidence_score": response['aggregated_insights']['insights_summary']['confidence_score']
            }
        )
        
        response['cache_info']['hit'] = False
        return response

    def _gather_mood_stats(self, db: Session, user_id: str) -> Dict[str, Any]:
        entries: List[MoodEntry] = list(db.query(MoodEntry).filter(MoodEntry.user_id == user_id).order_by(MoodEntry.created_at.desc()).limit(100).all())
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
        # Streak calc
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

    def _build_response(self, user_id: str, mood: Dict[str, Any]) -> Dict[str, Any]:
        # Data quality heuristic (simple phase 1)
        data_quality = 0
        if mood['total_entries'] >= 5:
            data_quality = min(int((mood['total_entries']/30)*100), 100)
        confidence = 0.4 if mood['total_entries'] >= 5 else 0.1
        
        # Build the unified insights response format
        response: Dict[str, Any] = {
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'aggregated_insights': {
                'mood': {
                    'current_score': int(mood['average_mood'] * 10) if mood['average_mood'] else 0,
                    'average_score': round(mood['average_mood'], 1) if mood['average_mood'] else 0,
                    'total_entries': mood['total_entries'],
                    'days_tracked': mood.get('days_tracked', 0),
                    'mood_streak': mood['mood_streak'],
                    'best_day': mood['best_day'],
                    'energy_peak': mood['energy_peak'],
                    'mood_variability': mood['mood_variability']
                },
                'trends': {
                    'direction': 'stable',  # TODO: calculate actual trend
                    'weekly_change': 0,      # TODO: calculate weekly change
                    'monthly_change': 0      # TODO: calculate monthly change
                },
                'insights_summary': {
                    'total_insights': 1 if mood['total_entries'] > 0 else 0,
                    'confidence_score': confidence,
                    'data_quality': data_quality,
                    'dominant_mood': self._dominant_label(mood['average_mood'])
                }
            },
            'cache_info': {
                'hit': False,  # Will be updated by caller
                'ttl_seconds': CACHE_TTL_SECONDS,
                'last_updated': datetime.now(timezone.utc).isoformat()
            }
        }
        return response

    def _dominant_label(self, avg: float) -> str:
        if not avg:
            return ''
        if avg >= 7: return 'great'
        if avg >= 6: return 'good'
        if avg >= 5: return 'okay'
        if avg >= 4: return 'low'
        return 'struggling'

aggregator = UnifiedInsightsAggregator()
