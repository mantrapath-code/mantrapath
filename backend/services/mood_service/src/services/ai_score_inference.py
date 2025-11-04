"""AI Score Inference Service for mood/stress/energy score calculation from emotions."""

import logging
from typing import List, Dict, Any, Optional
from src.models.schemas import EmotionAnalysis, SentimentType

logger = logging.getLogger(__name__)


class AIScoreInferenceService:
    """Infer mood/stress/energy scores from text and voice emotions."""
    
    def __init__(self):
        """Initialize the AI score inference service."""
        # Emotion to score mapping weights
        self.emotion_weights = {
            # Mood Score (1-10) - based on sentiment and specific emotions
            "mood_positive": {
                "joy": 0.9, "love": 0.9, "optimism": 0.8, "gratitude": 0.8,
                "excitement": 0.85, "pride": 0.8, "relief": 0.7, "amusement": 0.75,
                "admiration": 0.7, "caring": 0.75, "desire": 0.6, "approval": 0.6
            },
            "mood_negative": {
                "sadness": 0.2, "anger": 0.3, "fear": 0.25, "disappointment": 0.3,
                "disgust": 0.2, "embarrassment": 0.3, "grief": 0.15, "nervousness": 0.3,
                "remorse": 0.25, "annoyance": 0.4, "disapproval": 0.35
            },
            "mood_neutral": {
                "neutral": 0.5, "confusion": 0.4, "curiosity": 0.5, "realization": 0.5,
                "surprise": 0.5
            },
            
            # Stress Level (1-10) - based on anxiety and pressure indicators
            "stress_high": {
                "nervousness": 0.9, "fear": 0.8, "anxiety": 0.9, "overwhelmed": 0.85,
                "pressure": 0.8, "worry": 0.8, "tension": 0.85, "panic": 0.95
            },
            "stress_low": {
                "calm": 0.2, "peaceful": 0.15, "relaxed": 0.2, "serene": 0.1,
                "tranquil": 0.1, "content": 0.3, "satisfied": 0.3
            },
            
            # Energy Level (1-10) - based on activity and vitality indicators
            "energy_high": {
                "excitement": 0.9, "joy": 0.8, "enthusiasm": 0.9, "energetic": 0.95,
                "motivated": 0.8, "inspired": 0.8, "eager": 0.85, "vibrant": 0.9
            },
            "energy_low": {
                "tired": 0.2, "exhausted": 0.1, "fatigued": 0.15, "drained": 0.1,
                "lethargic": 0.2, "sluggish": 0.25, "weary": 0.2, "depleted": 0.15
            }
        }
        
        # Text sentiment to score mapping
        self.sentiment_scores = {
            SentimentType.POSITIVE: {"mood": 7.5, "stress": 3.0, "energy": 7.0},
            SentimentType.NEGATIVE: {"mood": 3.0, "stress": 7.0, "energy": 3.0},
            SentimentType.NEUTRAL: {"mood": 5.0, "stress": 5.0, "energy": 5.0},
            SentimentType.AMBIGUOUS: {"mood": 5.5, "stress": 5.5, "energy": 5.5}
        }
    
    async def infer_scores_from_emotions(
        self,
        text_emotions: List[EmotionAnalysis],
        voice_emotions: Optional[List[Dict]] = None,
        input_text: str = ""
    ) -> Dict[str, Any]:
        """
        Combine text emotions and voice tone to infer mood/stress/energy scores.
        
        Args:
            text_emotions: List of emotions from GoEmotions analysis
            voice_emotions: Optional voice tone emotions from audio analysis
            input_text: Original user input text for additional context
            
        Returns:
            Dict containing mood_score, stress_level, energy_level, confidence, reasoning
        """
        try:
            # Calculate base scores from text emotions
            text_scores = self._calculate_text_scores(text_emotions, input_text)
            
            # Calculate voice scores if available
            voice_scores = None
            if voice_emotions:
                voice_scores = self._calculate_voice_scores(voice_emotions)
            
            # Combine scores with weights
            final_scores = self._combine_scores(text_scores, voice_scores)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(text_emotions, voice_emotions, final_scores)
            
            return {
                "mood_score": int(round(final_scores["mood"])),
                "stress_level": int(round(final_scores["stress"])),
                "energy_level": int(round(final_scores["energy"])),
                "confidence": final_scores["confidence"],
                "reasoning": reasoning,
                "text_emotion_count": len(text_emotions),
                "voice_emotion_count": len(voice_emotions) if voice_emotions else 0
            }
            
        except Exception as e:
            logger.error(f"Error in AI score inference: {e}")
            # Return neutral scores as fallback
            return {
                "mood_score": 5,
                "stress_level": 5,
                "energy_level": 5,
                "confidence": 0.3,
                "reasoning": f"Error in analysis: {str(e)}. Using neutral scores.",
                "text_emotion_count": 0,
                "voice_emotion_count": 0
            }
    
    def _calculate_text_scores(self, emotions: List[EmotionAnalysis], input_text: str) -> Dict[str, float]:
        """Calculate scores based on text emotions."""
        if not emotions:
            return {"mood": 5.0, "stress": 5.0, "energy": 5.0, "confidence": 0.3}
        
        # Start with sentiment-based scores
        primary_sentiment = emotions[0].sentiment
        base_scores = self.sentiment_scores.get(primary_sentiment, {"mood": 5.0, "stress": 5.0, "energy": 5.0})
        
        # Adjust based on specific emotions
        mood_adjustment = 0.0
        stress_adjustment = 0.0
        energy_adjustment = 0.0
        total_confidence = 0.0
        
        for emotion in emotions:
            confidence_weight = emotion.confidence / 100.0
            total_confidence += confidence_weight
            
            emotion_name = emotion.emotion.lower()
            
            # Mood adjustments
            if emotion_name in self.emotion_weights["mood_positive"]:
                mood_adjustment += self.emotion_weights["mood_positive"][emotion_name] * confidence_weight
            elif emotion_name in self.emotion_weights["mood_negative"]:
                mood_adjustment += self.emotion_weights["mood_negative"][emotion_name] * confidence_weight
            elif emotion_name in self.emotion_weights["mood_neutral"]:
                mood_adjustment += self.emotion_weights["mood_neutral"][emotion_name] * confidence_weight
            
            # Stress adjustments
            if emotion_name in self.emotion_weights["stress_high"]:
                stress_adjustment += self.emotion_weights["stress_high"][emotion_name] * confidence_weight
            elif emotion_name in self.emotion_weights["stress_low"]:
                stress_adjustment += self.emotion_weights["stress_low"][emotion_name] * confidence_weight
            
            # Energy adjustments
            if emotion_name in self.emotion_weights["energy_high"]:
                energy_adjustment += self.emotion_weights["energy_high"][emotion_name] * confidence_weight
            elif emotion_name in self.emotion_weights["energy_low"]:
                energy_adjustment += self.emotion_weights["energy_low"][emotion_name] * confidence_weight
        
        # Apply adjustments (scale to 1-10 range)
        mood_score = max(1, min(10, base_scores["mood"] + (mood_adjustment - 0.5) * 4))
        stress_score = max(1, min(10, base_scores["stress"] + (stress_adjustment - 0.5) * 4))
        energy_score = max(1, min(10, base_scores["energy"] + (energy_adjustment - 0.5) * 4))
        
        # Calculate confidence based on emotion strength and count
        avg_confidence = total_confidence / len(emotions) if emotions else 0.3
        confidence = min(0.95, avg_confidence + (len(emotions) * 0.05))
        
        return {
            "mood": mood_score,
            "stress": stress_score,
            "energy": energy_score,
            "confidence": confidence
        }
    
    def _calculate_voice_scores(self, voice_emotions: List[Dict]) -> Dict[str, float]:
        """Calculate scores based on voice tone emotions."""
        if not voice_emotions:
            return {"mood": 5.0, "stress": 5.0, "energy": 5.0, "confidence": 0.3}
        
        # Voice emotions typically come as intensity/valence/arousal
        # Map these to our mood/stress/energy dimensions
        total_valence = 0.0
        total_arousal = 0.0
        total_intensity = 0.0
        count = 0
        
        for voice_emotion in voice_emotions:
            if "valence" in voice_emotion:
                total_valence += voice_emotion["valence"]
            if "arousal" in voice_emotion:
                total_arousal += voice_emotion["arousal"]
            if "intensity" in voice_emotion:
                total_intensity += voice_emotion["intensity"]
            count += 1
        
        if count == 0:
            return {"mood": 5.0, "stress": 5.0, "energy": 5.0, "confidence": 0.3}
        
        # Normalize to 1-10 scale
        avg_valence = total_valence / count  # -1 to 1 -> 1 to 10
        avg_arousal = total_arousal / count  # -1 to 1 -> 1 to 10
        avg_intensity = total_intensity / count  # 0 to 1 -> 1 to 10
        
        mood_score = max(1, min(10, (avg_valence + 1) * 5))  # -1,1 -> 1,10
        stress_score = max(1, min(10, (avg_arousal + 1) * 5))  # High arousal = high stress
        energy_score = max(1, min(10, avg_intensity * 10))  # 0,1 -> 1,10
        
        confidence = min(0.9, avg_intensity + 0.3)  # Higher intensity = higher confidence
        
        return {
            "mood": mood_score,
            "stress": stress_score,
            "energy": energy_score,
            "confidence": confidence
        }
    
    def _combine_scores(self, text_scores: Dict[str, float], voice_scores: Optional[Dict[str, float]]) -> Dict[str, float]:
        """Combine text and voice scores with appropriate weights."""
        if voice_scores is None:
            return text_scores
        
        # Weight: 70% text, 30% voice
        text_weight = 0.7
        voice_weight = 0.3
        
        combined_scores = {}
        for key in ["mood", "stress", "energy"]:
            combined_scores[key] = (
                text_scores[key] * text_weight + 
                voice_scores[key] * voice_weight
            )
        
        # Combined confidence (weighted average)
        combined_scores["confidence"] = (
            text_scores["confidence"] * text_weight + 
            voice_scores["confidence"] * voice_weight
        )
        
        return combined_scores
    
    def _generate_reasoning(self, text_emotions: List[EmotionAnalysis], voice_emotions: Optional[List[Dict]], scores: Dict[str, float]) -> str:
        """Generate human-readable reasoning for the scores."""
        reasoning_parts = []
        
        # Text emotion reasoning
        if text_emotions:
            primary_emotion = text_emotions[0].emotion
            primary_sentiment = text_emotions[0].sentiment.value
            confidence = text_emotions[0].confidence
            
            reasoning_parts.append(
                f"Detected {primary_sentiment} emotion '{primary_emotion}' "
                f"with {confidence:.1f}% confidence from text analysis"
            )
            
            # Add secondary emotions if significant
            if len(text_emotions) > 1 and text_emotions[1].confidence > 30:
                secondary_emotion = text_emotions[1].emotion
                secondary_confidence = text_emotions[1].confidence
                reasoning_parts.append(f"and secondary emotion '{secondary_emotion}' ({secondary_confidence:.1f}%)")
        
        # Voice emotion reasoning
        if voice_emotions:
            reasoning_parts.append("combined with voice tone analysis")
        
        # Score interpretation
        mood_score = int(round(scores["mood"]))
        stress_score = int(round(scores["stress"]))
        energy_score = int(round(scores["energy"]))
        
        mood_desc = self._get_score_description(mood_score, "mood")
        stress_desc = self._get_score_description(stress_score, "stress")
        energy_desc = self._get_score_description(energy_score, "energy")
        
        reasoning_parts.append(f"resulting in {mood_desc} mood, {stress_desc} stress, and {energy_desc} energy levels")
        
        return ". ".join(reasoning_parts) + "."
    
    def _get_score_description(self, score: int, dimension: str) -> str:
        """Get human-readable description for a score."""
        if dimension == "mood":
            if score >= 8:
                return "very positive"
            elif score >= 6:
                return "positive"
            elif score >= 4:
                return "neutral"
            else:
                return "negative"
        elif dimension == "stress":
            if score >= 8:
                return "high"
            elif score >= 6:
                return "moderate"
            elif score >= 4:
                return "low"
            else:
                return "very low"
        elif dimension == "energy":
            if score >= 8:
                return "high"
            elif score >= 6:
                return "moderate"
            elif score >= 4:
                return "low"
            else:
                return "very low"
        else:
            return "moderate"


# Global instance
ai_score_service = AIScoreInferenceService()


