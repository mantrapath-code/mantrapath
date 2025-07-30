"""
Notification Content Engine - ML component for personalized notification content
Generates contextual, personalized notification messages and insights
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics
import random

logger = logging.getLogger(__name__)

class NotificationContentEngine:
    """Generates personalized notification content based on user context and patterns"""
    
    def __init__(self):
        self.ready = True
        self.content_templates = self._load_content_templates()
        self.insight_generators = self._initialize_insight_generators()
        
    def is_ready(self) -> bool:
        """Check if the content engine is ready"""
        return self.ready
    
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
        Generate personalized notification content
        
        Args:
            notification_type: Type of notification (morning_check, afternoon_support, etc.)
            user_context: User's current context and patterns
            effectiveness_score: Predicted effectiveness of this notification
            
        Returns:
            Dictionary with title, message, and action suggestions
        """
        try:
            templates = self.content_templates.get(notification_type, self.content_templates["morning_check"])
            
            # Select content based on user context
            title = self._select_contextual_content(templates["titles"], user_context)
            message = self._select_contextual_content(templates["messages"], user_context)
            action_suggestions = self._select_action_suggestions(templates["action_suggestions"], user_context)
            
            # Personalize content based on user patterns
            message = self._personalize_message(message, user_context, notification_type)
            
            return {
                "title": title,
                "message": message,
                "action_suggestions": action_suggestions,
                "notification_type": notification_type,
                "effectiveness_score": effectiveness_score,
                "personalization_level": self._calculate_personalization_level(user_context)
            }
            
        except Exception as e:
            logger.error(f"Error generating notification content: {e}")
            return self._get_fallback_content(notification_type)
    
    def _select_contextual_content(self, content_list: List[str], user_context: Dict[str, Any]) -> str:
        """Select content based on user context"""
        # For now, use random selection
        # In future, implement ML-based selection based on user preferences and engagement history
        return random.choice(content_list)
    
    def _select_action_suggestions(self, suggestions: List[str], user_context: Dict[str, Any]) -> List[str]:
        """Select relevant action suggestions based on user context"""
        # Select 2-3 relevant suggestions
        selected_count = min(3, len(suggestions))
        return random.sample(suggestions, selected_count)
    
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
