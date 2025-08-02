"""
Adaptive Mood Collection Service - Phase 1 Enhancement
Provides intelligent, context-aware mood tracking with personalized follow-up questions
"""
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

# Import shared models and ML service client
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from shared.models import MoodEntry, AdaptiveQuestion, EnvironmentalData
from shared.database import get_db

class AdaptiveQuestionData:
    """Data structure for adaptive questions"""
    def __init__(self, question_type: str, question_text: str, 
                 options: List[Dict] = None, trigger_pattern: str = None):
        self.question_type = question_type
        self.question_text = question_text
        self.options = options or []
        self.trigger_pattern = trigger_pattern

class AdaptiveMoodCollector:
    """Service for adaptive mood collection with intelligent follow-up questions"""
    
    def __init__(self):
        self.question_templates = self._load_question_templates()
        
    def _load_question_templates(self) -> Dict[str, List[Dict]]:
        """Load predefined question templates for different patterns"""
        return {
            "stress_increasing": [
                {
                    "question": "You seem more stressed lately. What's been weighing on your mind?",
                    "options": [
                        {"value": "work", "label": "Work pressures"},
                        {"value": "relationships", "label": "Relationship issues"},
                        {"value": "health", "label": "Health concerns"},
                        {"value": "finances", "label": "Financial stress"},
                        {"value": "family", "label": "Family matters"},
                        {"value": "other", "label": "Something else"}
                    ]
                },
                {
                    "question": "How has this stress been affecting your daily activities?",
                    "scale": True,
                    "scale_type": "impact",
                    "range": [1, 5],
                    "labels": ["Not at all", "Slightly", "Moderately", "Quite a bit", "Extremely"]
                }
            ],
            "energy_low": [
                {
                    "question": "Your energy seems lower than usual. What might be contributing?",
                    "options": [
                        {"value": "sleep", "label": "Poor sleep quality"},
                        {"value": "nutrition", "label": "Diet/eating patterns"},
                        {"value": "exercise", "label": "Lack of physical activity"},
                        {"value": "workload", "label": "Too much on my plate"},
                        {"value": "weather", "label": "Weather/seasonal changes"},
                        {"value": "health", "label": "Not feeling well"}
                    ]
                }
            ],
            "mood_declining": [
                {
                    "question": "I've noticed your mood has been lower recently. Would you like to share what's going on?",
                    "open_text": True,
                    "optional": True
                },
                {
                    "question": "What usually helps when you're feeling this way?",
                    "options": [
                        {"value": "talking", "label": "Talking to someone"},
                        {"value": "exercise", "label": "Physical activity"},
                        {"value": "music", "label": "Music or creative activities"},
                        {"value": "nature", "label": "Time in nature"},
                        {"value": "rest", "label": "Rest and relaxation"},
                        {"value": "nothing", "label": "Nothing seems to help right now"}
                    ]
                }
            ],
            "inconsistent_tracking": [
                {
                    "question": "I notice you haven't been tracking as regularly. What would make it easier?",
                    "options": [
                        {"value": "reminders", "label": "Better reminder timing"},
                        {"value": "quick_entry", "label": "Faster entry process"},
                        {"value": "privacy", "label": "More privacy options"},
                        {"value": "feedback", "label": "More helpful insights"},
                        {"value": "motivation", "label": "Better motivation/rewards"}
                    ]
                }
            ],
            "positive_streak": [
                {
                    "question": "You've been doing great! What's been helping you maintain this positive momentum?",
                    "open_text": True,
                    "celebration": True
                }
            ]
        }
    
    async def analyze_user_patterns(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Analyze user's recent mood patterns to identify adaptive question opportunities"""
        
        # Get recent mood entries (last 14 days)
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        recent_entries = db.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.created_at >= two_weeks_ago
        ).order_by(desc(MoodEntry.created_at)).limit(20).all()
        
        if len(recent_entries) < 3:
            return {"patterns": [], "recommendations": []}
        
        patterns = {}
        
        # Analyze stress trend
        stress_levels = [entry.stress_level for entry in recent_entries[:7] if entry.stress_level]
        if len(stress_levels) >= 3:
            avg_recent_stress = sum(stress_levels[:3]) / 3
            avg_older_stress = sum(stress_levels[3:]) / len(stress_levels[3:]) if len(stress_levels) > 3 else avg_recent_stress
            if avg_recent_stress > avg_older_stress + 1:
                patterns["stress_increasing"] = {
                    "severity": min((avg_recent_stress - avg_older_stress) / 3, 1.0),
                    "recent_avg": avg_recent_stress
                }
        
        # Analyze energy patterns
        energy_levels = [entry.energy_level for entry in recent_entries[:7] if entry.energy_level]
        if len(energy_levels) >= 3:
            avg_energy = sum(energy_levels) / len(energy_levels)
            if avg_energy < 4:  # Low energy on 1-10 scale
                patterns["energy_low"] = {
                    "severity": (4 - avg_energy) / 4,
                    "recent_avg": avg_energy
                }
        
        # Analyze mood trend
        mood_scores = [entry.mood_score for entry in recent_entries[:7]]
        if len(mood_scores) >= 3:
            recent_avg = sum(mood_scores[:3]) / 3
            if recent_avg < 5:  # Declining mood
                patterns["mood_declining"] = {
                    "severity": (5 - recent_avg) / 5,
                    "recent_avg": recent_avg
                }
        
        # Check tracking consistency
        last_week = datetime.utcnow() - timedelta(days=7)
        recent_count = len([e for e in recent_entries if e.created_at >= last_week])
        if recent_count < 3:  # Less than 3 entries in last week
            patterns["inconsistent_tracking"] = {
                "severity": (3 - recent_count) / 3,
                "recent_count": recent_count
            }
        
        # Check for positive streaks
        if len(mood_scores) >= 3 and all(score >= 7 for score in mood_scores[:3]):
            patterns["positive_streak"] = {
                "severity": 1.0,
                "streak_length": len([s for s in mood_scores if s >= 7])
            }
        
        return {
            "patterns": patterns,
            "user_history": {
                "total_entries": len(recent_entries),
                "avg_mood": sum(mood_scores) / len(mood_scores) if mood_scores else 5,
                "tracking_frequency": recent_count
            }
        }
    
    async def generate_adaptive_questions(self, user_id: str, db: Session) -> List[AdaptiveQuestionData]:
        """Generate personalized adaptive questions based on user patterns"""
        
        analysis = await self.analyze_user_patterns(user_id, db)
        patterns = analysis["patterns"]
        
        questions = []
        
        # Prioritize patterns by severity
        sorted_patterns = sorted(patterns.items(), key=lambda x: x[1]["severity"], reverse=True)
        
        for pattern_name, pattern_data in sorted_patterns[:2]:  # Max 2 adaptive questions
            if pattern_name in self.question_templates:
                template_questions = self.question_templates[pattern_name]
                
                for template in template_questions:
                    question_data = AdaptiveQuestionData(
                        question_type=pattern_name,
                        question_text=template["question"],
                        options=template.get("options", []),
                        trigger_pattern=f"severity_{pattern_data['severity']:.2f}"
                    )
                    questions.append(question_data)
                    
                    # Store in database for tracking
                    adaptive_q = AdaptiveQuestion(
                        user_id=user_id,
                        question_type=pattern_name,
                        question_text=template["question"],
                        question_options=template,
                        trigger_pattern=f"severity_{pattern_data['severity']:.2f}"
                    )
                    db.add(adaptive_q)
                    
        db.commit()
        return questions
    
    async def process_adaptive_responses(self, user_id: str, mood_entry_id: str, 
                                       responses: List[Dict], db: Session) -> Dict[str, Any]:
        """Process and store adaptive question responses for learning"""
        
        insights = []
        
        for response in responses:
            question_type = response.get("question_type")
            answer = response.get("answer")
            
            # Generate contextual insights based on responses
            if question_type == "stress_increasing" and answer:
                if answer == "work":
                    insights.append("Consider work-life balance strategies and stress management techniques.")
                elif answer == "relationships":
                    insights.append("Relationship challenges can significantly impact mood. Consider communication strategies or support.")
                elif answer == "health":
                    insights.append("Health concerns affecting your well-being. Consider consulting healthcare providers if needed.")
                    
            elif question_type == "energy_low" and answer:
                if answer == "sleep":
                    insights.append("Sleep quality affects energy levels. Consider sleep hygiene improvements.")
                elif answer == "nutrition":
                    insights.append("Nutrition impacts energy. Consider reviewing eating patterns and timing.")
                elif answer == "exercise":
                    insights.append("Physical activity boosts energy. Consider starting with small, manageable activities.")
        
        # Update question effectiveness scores
        for response in responses:
            question_id = response.get("question_id")
            if question_id:
                question = db.query(AdaptiveQuestion).filter(
                    AdaptiveQuestion.id == question_id
                ).first()
                if question:
                    question.usage_count += 1
                    # Simple effectiveness scoring based on whether user provided detailed response
                    response_quality = 1.0 if len(str(answer)) > 10 else 0.5
                    question.effectiveness_score = (
                        question.effectiveness_score * 0.8 + response_quality * 0.2
                    )
        
        db.commit()
        
        return {
            "insights": insights,
            "learning_data": {
                "response_count": len(responses),
                "user_engagement": sum(1 for r in responses if r.get("answer"))
            }
        }
    
    async def get_environmental_context(self, user_id: str) -> Dict[str, Any]:
        """Collect environmental context for mood correlation (Phase 1 basic version)"""
        
        current_time = datetime.utcnow()
        
        # Basic time-based context
        context = {
            "time_context": {
                "hour": current_time.hour,
                "day_of_week": current_time.weekday(),  # 0 = Monday
                "is_weekend": current_time.weekday() >= 5,
                "season": self._get_season(current_time),
                "time_of_day": self._get_time_of_day(current_time.hour)
            },
            "collection_timestamp": current_time.isoformat()
        }
        
        # TODO: In future phases, add weather API, calendar integration, etc.
        # For Phase 1, we focus on time-based patterns
        
        return context
    
    def _get_season(self, date: datetime) -> str:
        """Determine season based on date (Northern Hemisphere)"""
        month = date.month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _get_time_of_day(self, hour: int) -> str:
        """Categorize time of day"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    async def create_enhanced_mood_entry(self, user_id: str, mood_data: Dict, 
                                       adaptive_responses: List[Dict], db: Session) -> MoodEntry:
        """Create a mood entry with Phase 1 enhancements"""
        
        # Get environmental context
        env_context = await self.get_environmental_context(user_id)
        
        # Process adaptive responses if any
        insights = []
        if adaptive_responses:
            response_data = await self.process_adaptive_responses(
                user_id, None, adaptive_responses, db
            )
            insights = response_data["insights"]
        
        # Create enhanced mood entry
        mood_entry = MoodEntry(
            user_id=user_id,
            mood_score=mood_data["mood_score"],
            energy_level=mood_data.get("energy_level", 5),
            stress_level=mood_data.get("stress_level", 5),
            sleep_quality=mood_data.get("sleep_quality", 5),
            notes=mood_data.get("notes"),
            context_tags=mood_data.get("context_tags", []),
            # Phase 1 enhancements
            emotional_granularity=mood_data.get("emotional_granularity", 3),
            environmental_context=env_context,
            mood_confidence=mood_data.get("mood_confidence", 1.0),
            collection_method="adaptive" if adaptive_responses else "manual",
            follow_up_responses=adaptive_responses,
            celebration_triggers=[]  # Will be populated by celebration detector
        )
        
        db.add(mood_entry)
        db.commit()
        db.refresh(mood_entry)
        
        return mood_entry
