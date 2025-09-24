import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import os

import structlog
import numpy as np
from redis import Redis

from models.ai_models import PredictiveAnalysisResult, AIMetrics

logger = structlog.get_logger(__name__)

class PredictiveInterventionEngine:
    """
    Predictive Intervention Engine for Proactive Mental Health Support
    
    Features:
    - Early intervention detection (>85% accuracy target)
    - Optimal timing prediction for assistance
    - Cross-service behavioral pattern analysis
    - Cultural sensitivity in intervention approaches
    - Real-time risk assessment
    """
    
    def __init__(self):
        self.redis_client = None
        self.is_initialized = False
        self.metrics = AIMetrics()
        
        # Intervention thresholds
        self.risk_thresholds = {
            'critical': 0.9,
            'high': 0.7,
            'medium': 0.5,
            'low': 0.3
        }
        
        # Behavioral indicators
        self.risk_indicators = {
            'mood_decline': {
                'weight': 0.3,
                'pattern': 'decreasing_trend'
            },
            'social_withdrawal': {
                'weight': 0.25,
                'pattern': 'activity_decrease'
            },
            'sleep_disruption': {
                'weight': 0.2,
                'pattern': 'irregular_patterns'
            },
            'negative_sentiment': {
                'weight': 0.15,
                'pattern': 'increasing_negativity'
            },
            'crisis_language': {
                'weight': 0.4,
                'pattern': 'immediate_risk'
            }
        }
        
    async def start(self):
        """Initialize predictive intervention engine"""
        try:
            logger.info("Starting Predictive Intervention Engine")
            
            # Allow disabling via env var for lightweight runs
            if os.getenv("ENABLE_PREDICTIVE_ENGINE", "true").lower() != "true":
                logger.info("Predictive engine disabled via ENABLE_PREDICTIVE_ENGINE=false")
                self.is_initialized = True
                return
            
            # Initialize Redis connection (configurable)
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379/4")
            self.redis_client = Redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.ping
            )
            
            self.is_initialized = True
            logger.info("Predictive Intervention Engine started successfully")
            
        except Exception as e:
            logger.error("Failed to start Predictive Intervention Engine", error=str(e))
            # Don't crash the whole service if Redis is unavailable in lightweight mode
            if os.getenv("PREDICTIVE_OPTIONAL", "true").lower() == "true":
                logger.warning("Continuing without predictive engine (optional mode)")
                self.redis_client = None
                self.is_initialized = True
            else:
                raise
    
    async def stop(self):
        """Stop predictive intervention engine"""
        try:
            logger.info("Stopping Predictive Intervention Engine")
            
            if self.redis_client:
                self.redis_client.close()
            
            self.is_initialized = False
            logger.info("Predictive Intervention Engine stopped")
            
        except Exception as e:
            logger.error("Error stopping Predictive Intervention Engine", error=str(e))
    
    async def analyze_intervention_needs(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze user's intervention needs based on behavioral patterns
        
        Args:
            user_id: User ID to analyze
            
        Returns:
            Predictive analysis result with intervention recommendations
        """
        try:
            start_time = time.time()
            
            if not self.is_initialized:
                raise RuntimeError("Predictive engine not initialized")
            
            # Gather user behavioral data
            behavioral_data = await self._gather_behavioral_data(user_id)
            
            # Analyze risk factors
            risk_analysis = await self._analyze_risk_factors(user_id, behavioral_data)
            
            # Determine intervention needs
            intervention_analysis = await self._determine_intervention_needs(
                user_id, risk_analysis
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                user_id, intervention_analysis
            )
            
            # Calculate timing optimization
            optimal_timing = await self._calculate_optimal_timing(user_id, behavioral_data)
            
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                "intervention_needed": intervention_analysis["intervention_needed"],
                "confidence": intervention_analysis["confidence"],
                "intervention_type": intervention_analysis["intervention_type"],
                "urgency_level": intervention_analysis["urgency_level"],
                "recommended_actions": recommendations,
                "cultural_considerations": intervention_analysis.get("cultural_considerations"),
                "risk_factors": risk_analysis["risk_factors"],
                "optimal_timing": optimal_timing,
                "processing_time_ms": processing_time
            }
            
            # Store analysis for future reference
            await self._store_analysis_result(user_id, result)
            
            # Update metrics
            self.metrics.predictive_analyses += 1
            
            logger.debug(
                "Intervention analysis completed",
                user_id=user_id,
                intervention_needed=result["intervention_needed"],
                urgency=result["urgency_level"],
                confidence=result["confidence"]
            )
            
            return result
            
        except Exception as e:
            logger.error("Intervention analysis failed", error=str(e), user_id=user_id)
            return self._create_fallback_analysis()
    
    async def _gather_behavioral_data(self, user_id: str) -> Dict[str, Any]:
        """Gather behavioral data from various sources"""
        try:
            behavioral_data = {
                "mood_history": [],
                "activity_patterns": [],
                "sentiment_history": [],
                "interaction_frequency": {},
                "voice_patterns": [],
                "journal_analysis": []
            }
            
            # Get mood history (last 7 days)
            mood_key = f"mood_history:{user_id}"
            mood_data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.lrange, mood_key, 0, 50
            )
            
            for mood_entry in mood_data:
                try:
                    behavioral_data["mood_history"].append(json.loads(mood_entry))
                except:
                    continue
            
            # Get AI context data
            context_key = f"ai_context:{user_id}"
            context_data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.get, context_key
            )
            
            if context_data:
                try:
                    context = json.loads(context_data)
                    sources = context.get("sources", {})
                    
                    # Extract sentiment history
                    for source, data in sources.items():
                        analysis = data.get("analysis", {})
                        if "sentiment" in analysis:
                            behavioral_data["sentiment_history"].append({
                                "source": source,
                                "sentiment": analysis["sentiment"],
                                "timestamp": data.get("timestamp")
                            })
                except:
                    pass
            
            # Get activity patterns
            activity_key = f"behavior_context:{user_id}"
            activity_data = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.lrange, activity_key, 0, 100
            )
            
            for activity_entry in activity_data:
                try:
                    behavioral_data["activity_patterns"].append(json.loads(activity_entry))
                except:
                    continue
            
            return behavioral_data
            
        except Exception as e:
            logger.error("Error gathering behavioral data", error=str(e), user_id=user_id)
            return {}
    
    async def _analyze_risk_factors(
        self, 
        user_id: str, 
        behavioral_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze risk factors from behavioral data"""
        try:
            risk_factors = {}
            overall_risk_score = 0.0
            
            # Analyze mood decline
            mood_risk = await self._analyze_mood_patterns(behavioral_data.get("mood_history", []))
            risk_factors["mood_decline"] = mood_risk
            overall_risk_score += mood_risk["score"] * self.risk_indicators["mood_decline"]["weight"]
            
            # Analyze social withdrawal
            activity_risk = await self._analyze_activity_patterns(behavioral_data.get("activity_patterns", []))
            risk_factors["social_withdrawal"] = activity_risk
            overall_risk_score += activity_risk["score"] * self.risk_indicators["social_withdrawal"]["weight"]
            
            # Analyze sentiment trends
            sentiment_risk = await self._analyze_sentiment_trends(behavioral_data.get("sentiment_history", []))
            risk_factors["negative_sentiment"] = sentiment_risk
            overall_risk_score += sentiment_risk["score"] * self.risk_indicators["negative_sentiment"]["weight"]
            
            # Check for crisis language
            crisis_risk = await self._detect_crisis_indicators(behavioral_data)
            risk_factors["crisis_language"] = crisis_risk
            if crisis_risk["detected"]:
                overall_risk_score = max(overall_risk_score, 0.9)  # Override for crisis
            
            return {
                "risk_factors": risk_factors,
                "overall_risk_score": min(overall_risk_score, 1.0),
                "primary_concerns": self._identify_primary_concerns(risk_factors)
            }
            
        except Exception as e:
            logger.error("Risk factor analysis failed", error=str(e), user_id=user_id)
            return {
                "risk_factors": {},
                "overall_risk_score": 0.3,
                "primary_concerns": []
            }
    
    async def _analyze_mood_patterns(self, mood_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze mood patterns for decline indicators"""
        if not mood_history:
            return {"score": 0.0, "trend": "insufficient_data", "confidence": 0.0}
        
        try:
            # Extract mood scores
            scores = []
            timestamps = []
            
            for entry in mood_history[-14:]:  # Last 14 entries
                if "mood_score" in entry:
                    scores.append(entry["mood_score"])
                    timestamps.append(entry.get("timestamp", time.time()))
            
            if len(scores) < 3:
                return {"score": 0.0, "trend": "insufficient_data", "confidence": 0.0}
            
            # Calculate trend
            recent_avg = np.mean(scores[-5:]) if len(scores) >= 5 else np.mean(scores[-3:])
            older_avg = np.mean(scores[:-5]) if len(scores) >= 8 else np.mean(scores[:-3])
            
            trend_direction = recent_avg - older_avg
            
            # Determine risk score
            if recent_avg < 3:  # Low mood scores
                risk_score = 0.8
            elif recent_avg < 4 and trend_direction < -0.5:  # Declining trend
                risk_score = 0.6
            elif trend_direction < -1:  # Significant decline
                risk_score = 0.7
            else:
                risk_score = max(0.0, (5 - recent_avg) / 5)  # Normalize to 0-1
            
            return {
                "score": risk_score,
                "trend": "declining" if trend_direction < -0.3 else "stable" if abs(trend_direction) < 0.3 else "improving",
                "recent_average": recent_avg,
                "trend_value": trend_direction,
                "confidence": min(len(scores) / 10, 1.0)
            }
            
        except Exception as e:
            logger.error("Mood pattern analysis failed", error=str(e))
            return {"score": 0.0, "trend": "error", "confidence": 0.0}
    
    async def _analyze_activity_patterns(self, activity_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze activity patterns for social withdrawal"""
        if not activity_patterns:
            return {"score": 0.0, "pattern": "insufficient_data", "confidence": 0.0}
        
        try:
            # Group activities by day
            daily_activity = {}
            
            for activity in activity_patterns[-50:]:  # Last 50 activities
                timestamp = activity.get("timestamp", time.time())
                day = datetime.fromtimestamp(timestamp).date()
                
                if day not in daily_activity:
                    daily_activity[day] = 0
                daily_activity[day] += 1
            
            if len(daily_activity) < 3:
                return {"score": 0.0, "pattern": "insufficient_data", "confidence": 0.0}
            
            # Calculate activity trend
            sorted_days = sorted(daily_activity.keys())
            recent_days = sorted_days[-3:]
            older_days = sorted_days[:-3] if len(sorted_days) > 3 else sorted_days[:3]
            
            recent_avg = np.mean([daily_activity[day] for day in recent_days])
            older_avg = np.mean([daily_activity[day] for day in older_days])
            
            # Determine withdrawal risk
            if recent_avg < 2:  # Very low activity
                risk_score = 0.7
            elif recent_avg < older_avg * 0.5:  # Significant decrease
                risk_score = 0.6
            elif recent_avg < older_avg * 0.7:  # Moderate decrease
                risk_score = 0.4
            else:
                risk_score = max(0.0, (10 - recent_avg) / 20)  # Low baseline risk
            
            return {
                "score": risk_score,
                "pattern": "withdrawal" if recent_avg < older_avg * 0.7 else "normal",
                "recent_activity": recent_avg,
                "activity_change": recent_avg - older_avg,
                "confidence": min(len(daily_activity) / 7, 1.0)
            }
            
        except Exception as e:
            logger.error("Activity pattern analysis failed", error=str(e))
            return {"score": 0.0, "pattern": "error", "confidence": 0.0}
    
    async def _analyze_sentiment_trends(self, sentiment_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment trends for negativity increase"""
        if not sentiment_history:
            return {"score": 0.0, "trend": "insufficient_data", "confidence": 0.0}
        
        try:
            # Convert sentiments to scores
            sentiment_scores = []
            
            for entry in sentiment_history[-20:]:  # Last 20 entries
                sentiment = entry.get("sentiment", "neutral")
                if sentiment == "positive":
                    score = 1.0
                elif sentiment == "negative":
                    score = -1.0
                else:
                    score = 0.0
                sentiment_scores.append(score)
            
            if len(sentiment_scores) < 3:
                return {"score": 0.0, "trend": "insufficient_data", "confidence": 0.0}
            
            # Calculate negativity trend
            recent_avg = np.mean(sentiment_scores[-5:]) if len(sentiment_scores) >= 5 else np.mean(sentiment_scores[-3:])
            overall_avg = np.mean(sentiment_scores)
            
            negative_ratio = sum(1 for score in sentiment_scores if score < 0) / len(sentiment_scores)
            
            # Determine risk score
            if negative_ratio > 0.7:  # Predominantly negative
                risk_score = 0.8
            elif negative_ratio > 0.5 and recent_avg < -0.3:  # Recent negativity
                risk_score = 0.6
            elif recent_avg < overall_avg - 0.3:  # Declining sentiment
                risk_score = 0.4
            else:
                risk_score = negative_ratio * 0.5  # Baseline based on negative ratio
            
            return {
                "score": risk_score,
                "trend": "declining" if recent_avg < overall_avg - 0.2 else "stable",
                "negative_ratio": negative_ratio,
                "recent_sentiment": recent_avg,
                "confidence": min(len(sentiment_scores) / 10, 1.0)
            }
            
        except Exception as e:
            logger.error("Sentiment trend analysis failed", error=str(e))
            return {"score": 0.0, "trend": "error", "confidence": 0.0}
    
    async def _detect_crisis_indicators(self, behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect immediate crisis indicators"""
        try:
            crisis_keywords = [
                "want to die", "kill myself", "end it all", "can't go on",
                "hopeless", "worthless", "burden", "better off dead",
                "suicide", "self-harm", "hurt myself", "no point"
            ]
            
            crisis_detected = False
            crisis_sources = []
            
            # Check sentiment history for crisis language
            for sentiment_entry in behavioral_data.get("sentiment_history", []):
                # This would normally check the actual text content
                # For now, we'll use a simplified approach
                if sentiment_entry.get("sentiment") == "crisis":
                    crisis_detected = True
                    crisis_sources.append(sentiment_entry.get("source", "unknown"))
            
            # Check mood history for extreme low scores
            for mood_entry in behavioral_data.get("mood_history", []):
                mood_score = mood_entry.get("mood_score", 5)
                if mood_score <= 1:
                    crisis_detected = True
                    crisis_sources.append("extreme_low_mood")
            
            return {
                "detected": crisis_detected,
                "sources": crisis_sources,
                "confidence": 0.9 if crisis_detected else 0.0,
                "urgency": "critical" if crisis_detected else "none"
            }
            
        except Exception as e:
            logger.error("Crisis detection failed", error=str(e))
            return {"detected": False, "sources": [], "confidence": 0.0, "urgency": "none"}
    
    def _identify_primary_concerns(self, risk_factors: Dict[str, Any]) -> List[str]:
        """Identify primary concerns from risk factors"""
        concerns = []
        
        for factor_name, factor_data in risk_factors.items():
            score = factor_data.get("score", 0.0)
            
            if score > 0.6:
                if factor_name == "mood_decline":
                    concerns.append("Declining mood patterns")
                elif factor_name == "social_withdrawal":
                    concerns.append("Decreased social engagement")
                elif factor_name == "negative_sentiment":
                    concerns.append("Increasing negativity in expressions")
                elif factor_name == "crisis_language":
                    concerns.append("Crisis indicators detected")
        
        return concerns
    
    async def _determine_intervention_needs(
        self, 
        user_id: str, 
        risk_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine intervention needs based on risk analysis"""
        try:
            overall_risk = risk_analysis["overall_risk_score"]
            risk_factors = risk_analysis["risk_factors"]
            
            # Check for crisis situations first
            if risk_factors.get("crisis_language", {}).get("detected", False):
                return {
                    "intervention_needed": True,
                    "intervention_type": "crisis_intervention",
                    "urgency_level": "critical",
                    "confidence": 0.95,
                    "reasoning": "Crisis indicators detected"
                }
            
            # Determine intervention based on risk score
            if overall_risk >= self.risk_thresholds["high"]:
                intervention_type = "proactive_support"
                urgency = "high"
                confidence = 0.85
            elif overall_risk >= self.risk_thresholds["medium"]:
                intervention_type = "gentle_check_in"
                urgency = "medium"
                confidence = 0.75
            elif overall_risk >= self.risk_thresholds["low"]:
                intervention_type = "wellness_reminder"
                urgency = "low"
                confidence = 0.65
            else:
                return {
                    "intervention_needed": False,
                    "intervention_type": None,
                    "urgency_level": "none",
                    "confidence": 0.7,
                    "reasoning": "Risk levels are within normal range"
                }
            
            return {
                "intervention_needed": True,
                "intervention_type": intervention_type,
                "urgency_level": urgency,
                "confidence": confidence,
                "reasoning": f"Risk score {overall_risk:.2f} indicates {urgency} intervention needs"
            }
            
        except Exception as e:
            logger.error("Intervention determination failed", error=str(e), user_id=user_id)
            return {
                "intervention_needed": False,
                "intervention_type": None,
                "urgency_level": "unknown",
                "confidence": 0.0,
                "reasoning": "Analysis failed"
            }
    
    async def _generate_recommendations(
        self, 
        user_id: str, 
        intervention_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate intervention recommendations"""
        try:
            intervention_type = intervention_analysis.get("intervention_type")
            urgency = intervention_analysis.get("urgency_level")
            
            if intervention_type == "crisis_intervention":
                return [
                    "Immediate crisis support notification",
                    "Professional counselor escalation",
                    "Emergency contact notification (if configured)",
                    "Crisis hotline resources",
                    "Safety planning assistance"
                ]
            
            elif intervention_type == "proactive_support":
                return [
                    "Personalized check-in message",
                    "Suggest scheduling therapy session",
                    "Recommend mindfulness exercise",
                    "Offer peer support connection",
                    "Provide mood tracking insights"
                ]
            
            elif intervention_type == "gentle_check_in":
                return [
                    "Friendly wellness check-in",
                    "Suggest journaling prompt",
                    "Recommend self-care activity",
                    "Share inspirational content",
                    "Invite to community discussion"
                ]
            
            elif intervention_type == "wellness_reminder":
                return [
                    "Daily wellness tip",
                    "Meditation reminder",
                    "Gratitude practice suggestion",
                    "Physical activity encouragement",
                    "Sleep hygiene reminder"
                ]
            
            else:
                return ["Continue monitoring wellness patterns"]
            
        except Exception as e:
            logger.error("Recommendation generation failed", error=str(e), user_id=user_id)
            return ["General wellness support"]
    
    async def _calculate_optimal_timing(
        self, 
        user_id: str, 
        behavioral_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate optimal timing for interventions"""
        try:
            # Analyze activity patterns to find optimal times
            activity_patterns = behavioral_data.get("activity_patterns", [])
            
            if not activity_patterns:
                return {
                    "best_time": "afternoon",
                    "confidence": 0.3,
                    "reasoning": "No activity data available"
                }
            
            # Group by hour of day
            hourly_activity = {}
            for activity in activity_patterns[-100:]:  # Last 100 activities
                timestamp = activity.get("timestamp", time.time())
                hour = datetime.fromtimestamp(timestamp).hour
                hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
            
            if not hourly_activity:
                return {
                    "best_time": "afternoon",
                    "confidence": 0.3,
                    "reasoning": "No time pattern data"
                }
            
            # Find peak activity hours
            peak_hour = max(hourly_activity, key=hourly_activity.get)
            
            # Convert to time period
            if 6 <= peak_hour < 12:
                best_time = "morning"
            elif 12 <= peak_hour < 17:
                best_time = "afternoon"
            elif 17 <= peak_hour < 21:
                best_time = "evening"
            else:
                best_time = "night"
            
            confidence = min(hourly_activity[peak_hour] / 20, 1.0)
            
            return {
                "best_time": best_time,
                "peak_hour": peak_hour,
                "confidence": confidence,
                "reasoning": f"Most active during {best_time} hours"
            }
            
        except Exception as e:
            logger.error("Optimal timing calculation failed", error=str(e), user_id=user_id)
            return {
                "best_time": "afternoon",
                "confidence": 0.3,
                "reasoning": "Default timing due to analysis error"
            }
    
    async def _store_analysis_result(self, user_id: str, result: Dict[str, Any]):
        """Store analysis result for future reference"""
        try:
            analysis_key = f"intervention_analysis:{user_id}"
            
            # Store with timestamp
            timestamped_result = {
                **result,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id
            }
            
            # Store latest analysis
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self.redis_client.setex,
                analysis_key,
                3600,  # 1 hour TTL
                json.dumps(timestamped_result)
            )
            
            # Store in history (keep last 10 analyses)
            history_key = f"intervention_history:{user_id}"
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.redis_client.lpush,
                history_key,
                json.dumps(timestamped_result)
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.redis_client.ltrim,
                history_key,
                0, 9
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.redis_client.expire,
                history_key,
                86400 * 7  # 7 days
            )
            
        except Exception as e:
            logger.error("Error storing analysis result", error=str(e), user_id=user_id)
    
    def _create_fallback_analysis(self) -> Dict[str, Any]:
        """Create fallback analysis when processing fails"""
        return {
            "intervention_needed": False,
            "confidence": 0.0,
            "intervention_type": None,
            "urgency_level": "unknown",
            "recommended_actions": ["Monitor user wellness"],
            "cultural_considerations": None,
            "risk_factors": {},
            "optimal_timing": {"best_time": "afternoon", "confidence": 0.0},
            "processing_time_ms": 0.0
        }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get predictive engine metrics"""
        return {
            "total_analyses": self.metrics.predictive_analyses,
            "is_initialized": self.is_initialized,
            "risk_thresholds": self.risk_thresholds
        }
    
    def health_check(self) -> bool:
        """Check if predictive engine is healthy"""
        return self.is_initialized and self.redis_client is not None
