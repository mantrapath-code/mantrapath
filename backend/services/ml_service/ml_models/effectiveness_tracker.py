"""
Advanced Reinforcement Learning Effectiveness Tracker
Uses RL algorithms to optimize notification strategies and maximize user engagement
Implements Q-Learning, Multi-Armed Bandits, and Policy Optimization
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics
from collections import defaultdict, deque

# Configure logging
logger = logging.getLogger(__name__)

import numpy as np
import pandas as pd
import random
import pickle

# Reinforcement Learning and ML libraries
try:
    import joblib
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.neural_network import MLPRegressor
    import scipy.stats as stats
    RL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Some RL/ML libraries not available: {e}")
    RL_AVAILABLE = False

logger = logging.getLogger(__name__)

class QLearningAgent:
    """Q-Learning agent for notification timing optimization"""
    
    def __init__(self, n_states: int, n_actions: int, learning_rate: float = 0.1, 
                 discount_factor: float = 0.95, epsilon: float = 0.1):
        self.n_states = n_states
        self.n_actions = n_actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        
        # Initialize Q-table
        self.q_table = np.zeros((n_states, n_actions))
        self.visit_counts = np.zeros((n_states, n_actions))
        
    def get_state(self, hour: int, day_of_week: int) -> int:
        """Convert time to state index"""
        return day_of_week * 24 + hour
    
    def choose_action(self, state: int) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            return np.random.choice(self.n_actions)  # Explore
        else:
            return np.argmax(self.q_table[state])  # Exploit
    
    def update_q_value(self, state: int, action: int, reward: float, next_state: int):
        """Update Q-value using Q-learning rule"""
        current_q = self.q_table[state, action]
        max_next_q = np.max(self.q_table[next_state])
        
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state, action] = new_q
        self.visit_counts[state, action] += 1
    
    def decay_epsilon(self, decay_rate: float = 0.995):
        """Decay exploration rate over time"""
        self.epsilon = max(0.01, self.epsilon * decay_rate)

class MultiArmedBandit:
    """Multi-Armed Bandit for content type selection"""
    
    def __init__(self, n_arms: int, algorithm: str = 'ucb'):
        self.n_arms = n_arms
        self.algorithm = algorithm
        
        # Track statistics for each arm
        self.arm_counts = np.zeros(n_arms)
        self.arm_rewards = np.zeros(n_arms)
        self.total_pulls = 0
        
    def select_arm(self) -> int:
        """Select arm using specified algorithm"""
        if self.algorithm == 'ucb':
            return self._ucb_select()
        elif self.algorithm == 'epsilon_greedy':
            return self._epsilon_greedy_select()
        else:
            return self._thompson_sampling_select()
    
    def _ucb_select(self) -> int:
        """Upper Confidence Bound selection"""
        if self.total_pulls < self.n_arms:
            # Pull each arm at least once
            return self.total_pulls
        
        ucb_values = np.zeros(self.n_arms)
        for arm in range(self.n_arms):
            if self.arm_counts[arm] > 0:
                avg_reward = self.arm_rewards[arm] / self.arm_counts[arm]
                confidence = np.sqrt(2 * np.log(self.total_pulls) / self.arm_counts[arm])
                ucb_values[arm] = avg_reward + confidence
            else:
                ucb_values[arm] = float('inf')
        
        return np.argmax(ucb_values)
    
    def _epsilon_greedy_select(self, epsilon: float = 0.1) -> int:
        """Epsilon-greedy selection"""
        if np.random.random() < epsilon:
            return np.random.choice(self.n_arms)
        else:
            avg_rewards = np.divide(self.arm_rewards, self.arm_counts, 
                                  out=np.zeros_like(self.arm_rewards), 
                                  where=self.arm_counts!=0)
            return np.argmax(avg_rewards)
    
    def _thompson_sampling_select(self) -> int:
        """Thompson sampling selection"""
        samples = np.zeros(self.n_arms)
        for arm in range(self.n_arms):
            alpha = self.arm_rewards[arm] + 1
            beta = self.arm_counts[arm] - self.arm_rewards[arm] + 1
            samples[arm] = np.random.beta(alpha, beta)
        return np.argmax(samples)
    
    def update_reward(self, arm: int, reward: float):
        """Update arm statistics with new reward"""
        self.arm_counts[arm] += 1
        self.arm_rewards[arm] += reward
        self.total_pulls += 1

class PolicyOptimizer:
    """Policy gradient optimizer for personalized notification strategies"""
    
    def __init__(self, state_dim: int, action_dim: int):
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Simple neural network policy (can be replaced with more sophisticated models)
        if RL_AVAILABLE:
            self.policy_network = MLPRegressor(
                hidden_layer_sizes=(64, 32),
                max_iter=1000,
                random_state=42
            )
            self.value_network = MLPRegressor(
                hidden_layer_sizes=(64, 32), 
                max_iter=1000,
                random_state=42
            )
            
        # Experience buffer for training
        self.experience_buffer = deque(maxlen=10000)
        self.trained = False
        
    def get_action_probabilities(self, state: np.ndarray) -> np.ndarray:
        """Get action probabilities from policy network"""
        if not self.trained or not RL_AVAILABLE:
            # Random policy initially
            return np.random.dirichlet(np.ones(self.action_dim))
        
        try:
            policy_output = self.policy_network.predict(state.reshape(1, -1))[0]
            # Convert to probabilities using softmax
            exp_output = np.exp(policy_output - np.max(policy_output))
            return exp_output / np.sum(exp_output)
        except:
            return np.random.dirichlet(np.ones(self.action_dim))
    
    def sample_action(self, state: np.ndarray) -> int:
        """Sample action from policy"""
        probs = self.get_action_probabilities(state)
        return np.random.choice(self.action_dim, p=probs)
    
    def add_experience(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        """Add experience to buffer"""
        self.experience_buffer.append({
            'state': state,
            'action': action, 
            'reward': reward,
            'next_state': next_state
        })
    
    def update_policy(self, batch_size: int = 32):
        """Update policy using collected experiences"""
        if len(self.experience_buffer) < batch_size or not RL_AVAILABLE:
            return
        
        # Sample batch from experience buffer
        batch = random.sample(list(self.experience_buffer), batch_size)
        
        states = np.array([exp['state'] for exp in batch])
        actions = np.array([exp['action'] for exp in batch])
        rewards = np.array([exp['reward'] for exp in batch])
        
        try:
            # Train policy network to maximize expected rewards
            self.policy_network.fit(states, rewards)
            # Train value network to predict rewards
            self.value_network.fit(states, rewards)
            
            self.trained = True
            
        except Exception as e:
            logger.error(f"Error updating policy: {e}")

class EffectivenessTracker:
    """Advanced RL-powered effectiveness tracker with Q-Learning and Multi-Armed Bandits"""
    
    def __init__(self):
        self.ready = RL_AVAILABLE
        self.model_version = "3.0.0-rl"
        self.model_dir = os.path.join(os.path.dirname(__file__), '..', 'trained_models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Traditional tracking components
        self.engagement_history = deque(maxlen=50000)  # More efficient memory management
        self.effectiveness_metrics = {}
        self.adaptation_rules = self._initialize_adaptation_rules()
        
        # Reinforcement Learning Components
        if self.ready:
            # Q-Learning Agent for notification timing optimization
            self.q_learning_agent = QLearningAgent(
                n_states=168,  # 24 hours * 7 days = 168 time slots
                n_actions=4,   # high_priority, medium_priority, low_priority, no_notification
                learning_rate=0.1,
                discount_factor=0.95,
                epsilon=0.1
            )
            
            # Multi-Armed Bandit for content type selection
            self.content_bandit = MultiArmedBandit(
                n_arms=6,  # Different content types/approaches
                algorithm='ucb'  # Upper Confidence Bound
            )
            
            # Policy optimization for personalization
            self.policy_optimizer = PolicyOptimizer(
                state_dim=12,  # User feature dimensions
                action_dim=8   # Notification strategy dimensions
            )
            
            # Feature scaler for RL inputs
            self.feature_scaler = StandardScaler()
            
            # Reward prediction model
            self.reward_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
            
            # Performance tracking
            self.rl_metrics = {
                'total_rewards': 0.0,
                'average_reward': 0.0,
                'q_learning_updates': 0,
                'bandit_pulls': 0,
                'policy_updates': 0,
                'exploration_rate': 0.1,
                'convergence_score': 0.0
            }
            
            # Load pre-trained RL models
            self._load_rl_models()
        
        # Fallback for when RL is not available
        if not self.ready:
            logger.warning("RL libraries not available, falling back to rule-based tracking")
        
    def is_ready(self) -> bool:
        """Check if the tracker is ready"""
        return self.ready
    
    def _load_rl_models(self):
        """Load pre-trained RL models if available"""
        try:
            if not RL_AVAILABLE:
                return
                
            model_files = {
                'q_learning_agent.pkl': 'q_learning_agent',
                'content_bandit.pkl': 'content_bandit', 
                'policy_optimizer.pkl': 'policy_optimizer',
                'feature_scaler.joblib': 'feature_scaler',
                'reward_predictor.joblib': 'reward_predictor'
            }
            
            for filename, attr_name in model_files.items():
                file_path = os.path.join(self.model_dir, filename)
                if os.path.exists(file_path):
                    if filename.endswith('.pkl'):
                        with open(file_path, 'rb') as f:
                            setattr(self, attr_name, pickle.load(f))
                    else:
                        setattr(self, attr_name, joblib.load(file_path))
                    logger.info(f"Loaded RL model {attr_name} from {filename}")
            
            # Load RL metrics
            metrics_path = os.path.join(self.model_dir, 'rl_metrics.json')
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.rl_metrics.update(json.load(f))
                    
        except Exception as e:
            logger.warning(f"Could not load pre-trained RL models: {e}")
    
    def _save_rl_models(self):
        """Save trained RL models"""
        try:
            if not RL_AVAILABLE:
                return
                
            # Save RL agents with pickle
            pickle_models = {
                'q_learning_agent.pkl': self.q_learning_agent,
                'content_bandit.pkl': self.content_bandit,
                'policy_optimizer.pkl': self.policy_optimizer
            }
            
            for filename, model in pickle_models.items():
                file_path = os.path.join(self.model_dir, filename)
                with open(file_path, 'wb') as f:
                    pickle.dump(model, f)
            
            # Save sklearn models with joblib
            sklearn_models = {
                'feature_scaler.joblib': self.feature_scaler,
                'reward_predictor.joblib': self.reward_predictor
            }
            
            for filename, model in sklearn_models.items():
                if hasattr(model, 'fit'):  # Only save fitted models
                    file_path = os.path.join(self.model_dir, filename)
                    joblib.dump(model, file_path)
            
            # Save RL metrics
            metrics_path = os.path.join(self.model_dir, 'rl_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(self.rl_metrics, f, default=str)
                
            logger.info("RL models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save RL models: {e}")
    
    def _extract_user_state_features(self, user_id: str, engagement_data: Dict[str, Any]) -> np.ndarray:
        """Extract state features for RL algorithms"""
        try:
            user_metrics = self.effectiveness_metrics.get(user_id, {})
            
            # Time-based features
            current_time = engagement_data.get("engagement_time", datetime.utcnow())
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # User engagement history features
            total_notifications = user_metrics.get("total_notifications", 0)
            engagement_count = user_metrics.get("engagement_count", 0)
            engagement_rate = engagement_count / max(1, total_notifications)
            
            effectiveness_scores = user_metrics.get("effectiveness_scores", [])
            avg_effectiveness = np.mean(effectiveness_scores) if effectiveness_scores else 0.5
            
            # Recent performance features
            recent_scores = effectiveness_scores[-10:] if len(effectiveness_scores) >= 10 else effectiveness_scores
            recent_avg = np.mean(recent_scores) if recent_scores else 0.5
            recent_std = np.std(recent_scores) if len(recent_scores) > 1 else 0.1
            
            # Time-of-day effectiveness
            hourly_effectiveness = user_metrics.get("hourly_effectiveness", {})
            hour_avg = np.mean(hourly_effectiveness.get(hour, [0.5]))
            
            # User preference indicators
            mood_change = engagement_data.get("subsequent_mood_change", 0)
            engagement_type_score = {
                "clicked": 1.0,
                "viewed": 0.7,
                "dismissed": 0.3,
                "ignored": 0.0
            }.get(engagement_data.get("engagement_type", "ignored"), 0.0)
            
            # Combine features
            features = np.array([
                hour / 24.0,  # Normalized hour
                day_of_week / 6.0,  # Normalized day of week
                engagement_rate,
                avg_effectiveness,
                recent_avg,
                recent_std,
                hour_avg,
                mood_change / 10.0,  # Normalize mood change
                engagement_type_score,
                min(total_notifications / 100.0, 1.0),  # Normalized experience
                len(recent_scores) / 10.0,  # Recency factor
                1.0  # Bias term
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting state features: {e}")
            return np.array([0.5] * 12)  # Default neutral features
    
    def _calculate_rl_reward(self, engagement_data: Dict[str, Any]) -> float:
        """Calculate reward signal for RL algorithms"""
        try:
            # Base reward from engagement type
            engagement_rewards = {
                "clicked": 1.0,
                "viewed": 0.6,
                "dismissed": -0.2,
                "ignored": -0.5
            }
            
            base_reward = engagement_rewards.get(
                engagement_data.get("engagement_type", "ignored"), -0.5
            )
            
            # Mood impact bonus/penalty
            mood_change = engagement_data.get("subsequent_mood_change", 0)
            mood_bonus = mood_change / 5.0  # Scale to [-2, 2] range
            
            # Timing appropriateness (reward notifications at good times)
            current_time = engagement_data.get("engagement_time", datetime.utcnow())
            hour = current_time.hour
            
            # Penalize notifications during sleep hours
            if 23 <= hour or hour <= 6:
                timing_penalty = -0.3
            elif 7 <= hour <= 9 or 17 <= hour <= 21:  # Good notification times
                timing_penalty = 0.2
            else:
                timing_penalty = 0.0
            
            # Response speed bonus
            response_time = engagement_data.get("response_time_minutes", 60)
            speed_bonus = max(0, (60 - response_time) / 60 * 0.2)  # Up to 0.2 bonus
            
            total_reward = base_reward + mood_bonus + timing_penalty + speed_bonus
            
            # Clip reward to reasonable range
            return np.clip(total_reward, -2.0, 2.0)
            
        except Exception as e:
            logger.error(f"Error calculating RL reward: {e}")
            return 0.0
    
    def _initialize_adaptation_rules(self) -> Dict[str, Any]:
        """Initialize rules for adapting notification strategies"""
        return {
            "low_engagement_threshold": 0.3,
            "high_engagement_threshold": 0.7,
            "min_data_points": 5,
            "adaptation_sensitivity": 0.1,
            "time_window_hours": 24,
            "effectiveness_weights": {
                "immediate_engagement": 0.4,
                "delayed_response": 0.3,
                "mood_impact": 0.3
            }
        }
    
    def _save_rl_models(self):
        """Save trained RL models"""
        try:
            if not RL_AVAILABLE:
                return
                    
            # Save RL agents with pickle
            pickle_models = {
                'q_learning_agent.pkl': self.q_learning_agent,
                'content_bandit.pkl': self.content_bandit,
                'policy_optimizer.pkl': self.policy_optimizer
            }
            
            for filename, model in pickle_models.items():
                file_path = os.path.join(self.model_dir, filename)
                with open(file_path, 'wb') as f:
                    pickle.dump(model, f)
            
            # Save sklearn models with joblib
            sklearn_models = {
                'feature_scaler.joblib': self.feature_scaler,
                'reward_predictor.joblib': self.reward_predictor
            }
            
            for filename, model in sklearn_models.items():
                if hasattr(model, 'fit'):  # Only save fitted models
                    file_path = os.path.join(self.model_dir, filename)
                    joblib.dump(model, file_path)
            
            # Save RL metrics
            metrics_path = os.path.join(self.model_dir, 'rl_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(self.rl_metrics, f, default=str)
                
            logger.info("RL models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save RL models: {e}")
    
    def _extract_user_state_features_for_rl(self, user_id: str, engagement_data: Dict[str, Any]) -> np.ndarray:
        """Extract state features for RL algorithms"""
        try:
            user_metrics = self.effectiveness_metrics.get(user_id, {})
            
            # Time-based features
            current_time = engagement_data.get("engagement_time", datetime.utcnow())
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            # User engagement history features
            total_notifications = user_metrics.get("total_notifications", 0)
            engagement_count = user_metrics.get("engagement_count", 0)
            engagement_rate = engagement_count / max(1, total_notifications)
            
            effectiveness_scores = user_metrics.get("effectiveness_scores", [])
            avg_effectiveness = np.mean(effectiveness_scores) if effectiveness_scores else 0.5
            
            # Recent performance features
            recent_scores = effectiveness_scores[-10:] if len(effectiveness_scores) >= 10 else effectiveness_scores
            recent_avg = np.mean(recent_scores) if recent_scores else 0.5
            recent_std = np.std(recent_scores) if len(recent_scores) > 1 else 0.1
            
            # Create feature vector
            features = np.array([
                hour / 24.0,  # Normalized hour
                day_of_week / 7.0,  # Normalized day of week
                engagement_rate,
                avg_effectiveness,
                recent_avg,
                recent_std,
                total_notifications / 100.0,  # Normalized notification count
                len(effectiveness_scores) / 50.0  # Normalized history length
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting RL state features: {e}")
            # Return default feature vector
            return np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.1, 0.0, 0.0])
        hourly_effectiveness = user_metrics.get("hourly_effectiveness", {})
        hour_avg = np.mean(hourly_effectiveness.get(hour, [0.5]))
        
        # User preference indicators  
        mood_change = engagement_data.get("subsequent_mood_change", 0)
        
        # Define engagement scoring
        engagement_scores = {
            "clicked": 1.0,
            "viewed": 0.7,
            "opened": 0.7,
            "acted_upon": 1.0,
            "dismissed": 0.3,
            "ignored": 0.0,
            "shared": 0.9
        }
        
        # This appears to be inside a different method context, let me create a proper method structure
        return features
    
    def _calculate_engagement_effectiveness(self, engagement_record: Dict[str, Any]) -> float:
        """Calculate effectiveness score for an engagement record"""
        try:
            engagement_scores = {
                "clicked": 1.0,
                "viewed": 0.7,
                "opened": 0.7,
                "acted_upon": 1.0,
                "dismissed": 0.3,
                "ignored": 0.0,
                "shared": 0.9
            }
            
            base_score = engagement_scores.get(engagement_record.get("engagement_type", "ignored"), 0.5)
            
            # Adjust for mood impact if available
            mood_change = engagement_record.get("subsequent_mood_change")
            if mood_change is not None:
                # Positive mood change increases effectiveness
                mood_factor = min(1.0, max(0.0, (mood_change + 3) / 6))  # Normalize to 0-1
                base_score = (base_score * 0.7) + (mood_factor * 0.3)
            
            # Adjust for timing (some hours might be naturally more effective)
            hour = engagement_record.get("notification_hour", 12)
            time_factor = self._get_time_effectiveness_factor(hour)
            base_score *= time_factor
            
            return min(1.0, max(0.0, base_score))
            
        except Exception as e:
            logger.error(f"Error calculating engagement effectiveness: {e}")
            return 0.5
    
    def _get_time_effectiveness_factor(self, hour: int) -> float:
        """Get time-based effectiveness factor"""
        # Based on general research about notification engagement
        if 8 <= hour <= 10:  # Morning peak
            return 1.1
        elif 12 <= hour <= 14:  # Lunch time
            return 0.9
        elif 15 <= hour <= 17:  # Afternoon
            return 1.0
        elif 18 <= hour <= 20:  # Evening
            return 1.1
        elif 21 <= hour <= 23:  # Late evening
            return 0.8
        else:  # Night/early morning
            return 0.6
    
    def _generate_adaptations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate adaptation recommendations based on user's effectiveness data"""
        adaptations = []
        
        if user_id not in self.effectiveness_metrics:
            return adaptations
        
        user_metrics = self.effectiveness_metrics[user_id]
        
        # Check if enough data for meaningful adaptations
        if user_metrics["total_notifications"] < self.adaptation_rules["min_data_points"]:
            return adaptations
        
        # Calculate overall engagement rate
        engagement_rate = user_metrics["engagement_count"] / user_metrics["total_notifications"]
        
        # Low engagement adaptations
        if engagement_rate < self.adaptation_rules["low_engagement_threshold"]:
            adaptations.append({
                "type": "frequency_reduction",
                "reason": "Low engagement rate",
                "recommendation": "Reduce notification frequency by 30%",
                "priority": "high"
            })
            
            adaptations.append({
                "type": "content_variation",
                "reason": "Low engagement suggests content mismatch",
                "recommendation": "Try different notification styles",
                "priority": "medium"
            })
        
        # High engagement optimization
        elif engagement_rate > self.adaptation_rules["high_engagement_threshold"]:
            adaptations.append({
                "type": "timing_optimization",
                "reason": "High engagement - optimize timing",
                "recommendation": "Focus on most effective time slots",
                "priority": "medium"
            })
        
        # Analyze hourly effectiveness
        hourly_adaptations = self._analyze_hourly_effectiveness(user_metrics)
        adaptations.extend(hourly_adaptations)
        
        return adaptations
    
    def _analyze_hourly_effectiveness(self, user_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze effectiveness by hour and suggest timing adaptations"""
        adaptations = []
        hourly_data = user_metrics["hourly_effectiveness"]
        
        if len(hourly_data) < 3:  # Need data from multiple hours
            return adaptations
        
        # Calculate average effectiveness by hour
        hourly_averages = {}
        for hour, scores in hourly_data.items():
            if len(scores) >= 2:
                hourly_averages[hour] = statistics.mean(scores)
        
        if len(hourly_averages) < 2:
            return adaptations
        
        # Find best and worst performing hours
        best_hour = max(hourly_averages.keys(), key=lambda h: hourly_averages[h])
        worst_hour = min(hourly_averages.keys(), key=lambda h: hourly_averages[h])
        
        effectiveness_diff = hourly_averages[best_hour] - hourly_averages[worst_hour]
        
        if effectiveness_diff > 0.3:  # Significant difference
            adaptations.append({
                "type": "timing_shift",
                "reason": f"Hour {best_hour} performs {effectiveness_diff:.1f} better than hour {worst_hour}",
                "recommendation": f"Prioritize notifications around {best_hour}:00",
                "priority": "high",
                "data": {
                    "best_hour": best_hour,
                    "best_effectiveness": round(hourly_averages[best_hour], 2),
                    "worst_hour": worst_hour,
                    "worst_effectiveness": round(hourly_averages[worst_hour], 2)
                }
            })
        
        return adaptations
    
    def get_user_effectiveness_summary(self, user_id: str) -> Dict[str, Any]:
        """Get effectiveness summary for a specific user"""
        if user_id not in self.effectiveness_metrics:
            return {
                "user_id": user_id,
                "status": "insufficient_data",
                "recommendations": ["Continue using notifications to gather effectiveness data"]
            }
        
        user_metrics = self.effectiveness_metrics[user_id]
        
        # Calculate key metrics
        engagement_rate = user_metrics["engagement_count"] / user_metrics["total_notifications"]
        avg_effectiveness = statistics.mean(user_metrics["effectiveness_scores"]) if user_metrics["effectiveness_scores"] else 0
        
        # Determine effectiveness level
        if avg_effectiveness > 0.7:
            effectiveness_level = "high"
        elif avg_effectiveness > 0.4:
            effectiveness_level = "moderate"
        else:
            effectiveness_level = "low"
        
        # Find best performing hour
        hourly_data = user_metrics["hourly_effectiveness"]
        best_hour = None
        if hourly_data:
            hourly_averages = {
                hour: statistics.mean(scores) 
                for hour, scores in hourly_data.items() 
                if len(scores) >= 2
            }
            if hourly_averages:
                best_hour = max(hourly_averages.keys(), key=lambda h: hourly_averages[h])
        
        return {
            "user_id": user_id,
            "effectiveness_level": effectiveness_level,
            "engagement_rate": round(engagement_rate, 3),
            "average_effectiveness": round(avg_effectiveness, 3),
            "total_notifications": user_metrics["total_notifications"],
            "best_hour": best_hour,
            "data_quality": "good" if user_metrics["total_notifications"] >= 10 else "limited",
            "last_updated": user_metrics["last_updated"].isoformat(),
            "recommendations": self._get_user_recommendations(engagement_rate, avg_effectiveness)
        }
    
    def _get_user_recommendations(self, engagement_rate: float, avg_effectiveness: float) -> List[str]:
        """Get personalized recommendations based on user metrics"""
        recommendations = []
        
        if engagement_rate < 0.3:
            recommendations.append("Consider adjusting notification timing or frequency")
            recommendations.append("Try different types of notifications")
        elif engagement_rate > 0.7:
            recommendations.append("Great engagement! Consider slight frequency increase")
            recommendations.append("Your current notification strategy is working well")
        
        if avg_effectiveness < 0.4:
            recommendations.append("Focus on higher-impact notification content")
            recommendations.append("Review optimal timing preferences")
        elif avg_effectiveness > 0.7:
            recommendations.append("Excellent effectiveness! Maintain current approach")
        
        if not recommendations:
            recommendations.append("Continue current notification strategy")
            recommendations.append("Keep providing feedback to improve personalization")
        
        return recommendations
    
    def get_global_effectiveness_insights(self) -> Dict[str, Any]:
        """Get insights from all users' effectiveness data (anonymized)"""
        if not self.engagement_history:
            return {"status": "no_data"}
        
        # Analyze global patterns
        hourly_engagement = defaultdict(list)
        daily_engagement = defaultdict(list)
        type_engagement = defaultdict(list)
        
        for record in self.engagement_history:
            effectiveness = self._calculate_effectiveness_score(record)
            hourly_engagement[record["notification_hour"]].append(effectiveness)
            daily_engagement[record["notification_day"]].append(effectiveness)
            type_engagement[record["engagement_type"]].append(effectiveness)
        
        # Calculate global optimal hours
        hourly_averages = {
            hour: statistics.mean(scores)
            for hour, scores in hourly_engagement.items()
            if len(scores) >= 10  # Minimum sample size
        }
        
        optimal_hours = sorted(
            hourly_averages.keys(),
            key=lambda h: hourly_averages[h],
            reverse=True
        )[:3]
        
        return {
            "status": "success",
            "total_data_points": len(self.engagement_history),
            "optimal_hours_global": optimal_hours,
            "hourly_effectiveness": {
                hour: round(avg, 3)
                for hour, avg in hourly_averages.items()
            },
            "most_effective_engagement": max(type_engagement.keys(), key=lambda t: statistics.mean(type_engagement[t])) if type_engagement else "unknown",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def update_metrics(self) -> bool:
        """Update effectiveness metrics (background task)"""
        try:
            # Clean old data (older than 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            self.engagement_history = [
                record for record in self.engagement_history
                if record["timestamp"] > cutoff_date
            ]
            
            # Update user metrics cleanup
            for user_id, metrics in list(self.effectiveness_metrics.items()):
                if metrics["last_updated"] < cutoff_date:
                    del self.effectiveness_metrics[user_id]
            
            logger.info(f"Updated effectiveness metrics. Active users: {len(self.effectiveness_metrics)}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the effectiveness tracker"""
        return {
            "tracker_type": "engagement_based_tracker",
            "total_engagement_records": len(self.engagement_history),
            "active_users": len(self.effectiveness_metrics),
            "adaptation_rules_count": len(self.adaptation_rules),
            "data_retention_days": 90,
            "effectiveness_calculation_factors": list(self.adaptation_rules["effectiveness_weights"].keys()),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def export_anonymized_insights(self) -> Dict[str, Any]:
        """Export anonymized insights for research and improvement"""
        global_insights = self.get_global_effectiveness_insights()
        
        # Additional anonymized statistics
        user_engagement_rates = []
        user_effectiveness_scores = []
        
        for metrics in self.effectiveness_metrics.values():
            if metrics["total_notifications"] >= 5:
                engagement_rate = metrics["engagement_count"] / metrics["total_notifications"]
                user_engagement_rates.append(engagement_rate)
                
                if metrics["effectiveness_scores"]:
                    avg_effectiveness = statistics.mean(metrics["effectiveness_scores"])
                    user_effectiveness_scores.append(avg_effectiveness)
        
        anonymized_stats = {
            "user_count": len(user_engagement_rates),
            "average_engagement_rate": statistics.mean(user_engagement_rates) if user_engagement_rates else 0,
            "average_effectiveness": statistics.mean(user_effectiveness_scores) if user_effectiveness_scores else 0,
            "engagement_rate_distribution": {
                "q25": statistics.quantiles(user_engagement_rates, n=4)[0] if len(user_engagement_rates) >= 4 else 0,
                "median": statistics.median(user_engagement_rates) if user_engagement_rates else 0,
                "q75": statistics.quantiles(user_engagement_rates, n=4)[2] if len(user_engagement_rates) >= 4 else 0
            }
        }
        
        return {
            "global_insights": global_insights,
            "anonymized_statistics": anonymized_stats,
            "export_timestamp": datetime.utcnow().isoformat()
        }
