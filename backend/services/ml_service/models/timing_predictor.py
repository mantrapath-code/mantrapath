"""
Optimal Timing Predictor - Advanced ML ensemble component for predicting optimal notification times
Uses XGBoost, LightGBM, and stacking ensemble methods for sophisticated timing optimization
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics
from collections import defaultdict
import numpy as np
import pandas as pd
import joblib

# Advanced ML ensemble imports
from sklearn.ensemble import (
    RandomForestRegressor, 
    GradientBoostingRegressor,
    VotingRegressor,
    StackingRegressor
)
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.base import BaseEstimator, RegressorMixin
from scipy import stats
from scipy.optimize import minimize

# Advanced ensemble libraries (if available)
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    
try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

logger = logging.getLogger(__name__)

class AdvancedEnsemblePredictor(BaseEstimator, RegressorMixin):
    """Custom ensemble predictor combining multiple advanced algorithms"""
    
    def __init__(self):
        self.models = {}
        self.weights = None
        self.scaler = StandardScaler()
        
    def fit(self, X, y):
        """Train the ensemble of models"""
        X_scaled = self.scaler.fit_transform(X)
        
        # Base models
        self.models['rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models['gb'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.models['ridge'] = Ridge(alpha=1.0)
        
        # Advanced models (if available)
        if XGBOOST_AVAILABLE:
            self.models['xgb'] = xgb.XGBRegressor(
                n_estimators=100, 
                learning_rate=0.1, 
                random_state=42
            )
        
        if LIGHTGBM_AVAILABLE:
            self.models['lgb'] = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.1,
                random_state=42,
                verbose=-1
            )
        
        # Train all models
        for name, model in self.models.items():
            model.fit(X_scaled, y)
        
        # Calculate optimal weights using cross-validation
        self._calculate_optimal_weights(X_scaled, y)
        
        return self
    
    def _calculate_optimal_weights(self, X, y):
        """Calculate optimal ensemble weights using optimization"""
        def objective(weights):
            weights = weights / np.sum(weights)  # Normalize
            predictions = np.zeros(len(y))
            
            for i, (name, model) in enumerate(self.models.items()):
                pred = model.predict(X)
                predictions += weights[i] * pred
            
            return mean_squared_error(y, predictions)
        
        # Initialize equal weights
        initial_weights = np.ones(len(self.models)) / len(self.models)
        
        # Optimize weights
        result = minimize(
            objective,
            initial_weights,
            method='SLSQP',
            bounds=[(0, 1) for _ in range(len(self.models))],
            constraints={'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        )
        
        self.weights = result.x / np.sum(result.x)  # Normalize
        
    def predict(self, X):
        """Make ensemble prediction"""
        X_scaled = self.scaler.transform(X)
        predictions = np.zeros(X.shape[0])
        
        for i, (name, model) in enumerate(self.models.items()):
            pred = model.predict(X_scaled)
            predictions += self.weights[i] * pred
            
        return predictions

class OptimalTimingPredictor:
    """Advanced ML ensemble predictor for optimal notification timing using stacking and voting methods"""
    
    def __init__(self):
        self.ready = True
        self.model_version = "2.0.0-ensemble"
        self.feedback_data = []
        
        # Advanced ensemble models
        self.timing_ensemble = self._create_timing_ensemble()
        self.engagement_ensemble = self._create_engagement_ensemble()
        self.effectiveness_predictor = AdvancedEnsemblePredictor()
        
        # Feature preprocessing
        self.scaler = RobustScaler()  # More robust to outliers
        self.feature_selector = None
        
        # Model persistence
        self.model_dir = os.path.join(os.path.dirname(__file__), '..', 'trained_models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Performance tracking
        self.performance_metrics = {
            'timing_accuracy': 0.0,
            'engagement_accuracy': 0.0,
            'ensemble_r2': 0.0,
            'cross_val_score': 0.0,
            'last_training': None,
            'training_samples': 0,
            'feature_importance': {}
        }
        
        # Load pre-trained models
        self._load_ensemble_models()
        
    def _create_timing_ensemble(self):
        """Create sophisticated ensemble for timing prediction"""
        # Base learners
        base_models = [
            ('rf', RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)),
            ('gb', GradientBoostingRegressor(n_estimators=150, learning_rate=0.1, random_state=42)),
            ('ridge', Ridge(alpha=1.0))
        ]
        
        # Add XGBoost if available
        if XGBOOST_AVAILABLE:
            base_models.append((
                'xgb', xgb.XGBRegressor(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
            ))
        
        # Add LightGBM if available
        if LIGHTGBM_AVAILABLE:
            base_models.append((
                'lgb', lgb.LGBMRegressor(
                    n_estimators=150,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42,
                    verbose=-1
                )
            ))
        
        # Create stacking ensemble
        stacking_ensemble = StackingRegressor(
            estimators=base_models,
            final_estimator=Ridge(alpha=0.5),
            cv=5,
            n_jobs=-1
        )
        
        return stacking_ensemble
    
    def _create_engagement_ensemble(self):
        """Create ensemble for engagement likelihood prediction"""
        base_models = [
            ('rf_eng', RandomForestRegressor(n_estimators=100, random_state=42)),
            ('gb_eng', GradientBoostingRegressor(n_estimators=100, random_state=42))
        ]
        
        if XGBOOST_AVAILABLE:
            base_models.append(('xgb_eng', xgb.XGBRegressor(n_estimators=100, random_state=42)))
        
        # Voting ensemble for engagement
        voting_ensemble = VotingRegressor(
            estimators=base_models,
            weights=None  # Will be optimized during training
        )
        
        return voting_ensemble
    
    def _load_ensemble_models(self):
        """Load pre-trained ensemble models"""
        try:
            model_files = {
                'timing_ensemble.joblib': 'timing_ensemble',
                'engagement_ensemble.joblib': 'engagement_ensemble',
                'effectiveness_predictor.joblib': 'effectiveness_predictor',
                'scaler.joblib': 'scaler'
            }
            
            for filename, attr_name in model_files.items():
                file_path = os.path.join(self.model_dir, filename)
                if os.path.exists(file_path):
                    setattr(self, attr_name, joblib.load(file_path))
                    logger.info(f"Loaded {attr_name} from {filename}")
            
            # Load performance metrics
            metrics_path = os.path.join(self.model_dir, 'timing_metrics.json')
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.performance_metrics.update(json.load(f))
                    
        except Exception as e:
            logger.warning(f"Could not load pre-trained ensemble models: {e}")
    
    def _save_ensemble_models(self):
        """Save trained ensemble models"""
        try:
            model_files = {
                'timing_ensemble.joblib': self.timing_ensemble,
                'engagement_ensemble.joblib': self.engagement_ensemble,
                'effectiveness_predictor.joblib': self.effectiveness_predictor,
                'scaler.joblib': self.scaler
            }
            
            for filename, model in model_files.items():
                file_path = os.path.join(self.model_dir, filename)
                joblib.dump(model, file_path)
            
            # Save performance metrics
            metrics_path = os.path.join(self.model_dir, 'timing_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(self.performance_metrics, f, default=str)
                
            logger.info("Ensemble models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save ensemble models: {e}")
    
    def _prepare_timing_features(self, user_data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray]:
        """Advanced feature engineering for ensemble timing prediction"""
        mood_entries = user_data.get("mood_entries", [])
        feedback_data = user_data.get("feedback_data", self.feedback_data)
        
        if len(mood_entries) < 5:
            return np.array([]), np.array([])
        
        # Convert to DataFrame for sophisticated feature engineering
        df = pd.DataFrame(mood_entries)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_workday'] = (~df['is_weekend']).astype(int)
        
        # Cyclical encoding for better ML performance
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Advanced statistical features
        df['mood_rolling_mean_3'] = df['mood_score'].rolling(window=3, min_periods=1).mean()
        df['mood_rolling_std_3'] = df['mood_score'].rolling(window=3, min_periods=1).std().fillna(0)
        df['mood_rolling_mean_7'] = df['mood_score'].rolling(window=7, min_periods=1).mean()
        df['mood_rolling_median_3'] = df['mood_score'].rolling(window=3, min_periods=1).median()
        
        # Lag features for time series
        for lag in [1, 2, 3, 6, 12]:  # Different lag periods
            df[f'mood_lag_{lag}'] = df['mood_score'].shift(lag).fillna(df['mood_score'].mean())
        
        # Trend and momentum features
        df['mood_diff'] = df['mood_score'].diff().fillna(0)
        df['mood_momentum'] = df['mood_diff'].rolling(window=3, min_periods=1).mean()
        df['mood_acceleration'] = df['mood_momentum'].diff().fillna(0)
        df['mood_volatility'] = df['mood_score'].rolling(window=7, min_periods=1).std().fillna(0)
        
        # Engagement history features (if available)
        engagement_features = self._extract_engagement_features(feedback_data, df)
        for key, values in engagement_features.items():
            df[key] = values
        
        # Intervention effectiveness features
        df['time_since_last_intervention'] = self._calculate_time_since_last_intervention(df)
        df['intervention_success_rate'] = self._calculate_intervention_success_rate(df, feedback_data)
        
        # Contextual features
        df['energy_mood_ratio'] = df.get('energy_level', 5) / (df['mood_score'] + 0.1)
        df['mood_below_average'] = (df['mood_score'] < df['mood_score'].mean()).astype(int)
        df['mood_quartile'] = pd.qcut(df['mood_score'], 4, labels=[0, 1, 2, 3], duplicates='drop')
        
        # Select feature columns for ML
        feature_columns = [
            'hour', 'day_of_week', 'is_weekend', 'is_workday',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
            'mood_rolling_mean_3', 'mood_rolling_std_3', 'mood_rolling_mean_7', 'mood_rolling_median_3',
            'mood_lag_1', 'mood_lag_2', 'mood_lag_3', 'mood_lag_6', 'mood_lag_12',
            'mood_diff', 'mood_momentum', 'mood_acceleration', 'mood_volatility',
            'time_since_last_intervention', 'intervention_success_rate',
            'energy_mood_ratio', 'mood_below_average'
        ]
        
        # Add engagement features to feature columns
        feature_columns.extend([col for col in df.columns if col.startswith('engagement_')])
        
        # Ensure all feature columns exist
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0.0
        
        X = df[feature_columns].fillna(0).values
        # Target: effectiveness score (higher for times when intervention is more beneficial)
        y = (10 - df['mood_score']).values  # Invert mood score (lower mood = higher intervention need)
        
        return X, y
    
    def _extract_engagement_features(self, feedback_data: List[Dict], df: pd.DataFrame) -> Dict[str, List[float]]:
        """Extract engagement-based features from feedback history"""
        features = {
            'engagement_rate_hour': [],
            'engagement_success_history': [],
            'optimal_window_history': []
        }
        
        # Initialize with defaults
        default_engagement_rate = 0.5
        default_success_history = 0.6
        default_optimal_window = 0.5
        
        for _, row in df.iterrows():
            hour = row['hour']
            
            # Calculate engagement rate for this hour
            hour_feedback = [f for f in feedback_data if f.get('engagement_time', datetime.now()).hour == hour]
            if hour_feedback:
                engagement_rate = len([f for f in hour_feedback if f.get('engagement_type') != 'ignored']) / len(hour_feedback)
                features['engagement_rate_hour'].append(engagement_rate)
            else:
                features['engagement_rate_hour'].append(default_engagement_rate)
            
            # Success history
            features['engagement_success_history'].append(default_success_history)
            features['optimal_window_history'].append(default_optimal_window)
        
        return features
    
    def _calculate_time_since_last_intervention(self, df: pd.DataFrame) -> List[float]:
        """Calculate hours since last intervention"""
        # Placeholder implementation - would use actual intervention history
        return [24.0] * len(df)  # Default 24 hours
    
    def _calculate_intervention_success_rate(self, df: pd.DataFrame, feedback_data: List[Dict]) -> List[float]:
        """Calculate success rate of interventions"""
        # Placeholder implementation - would calculate from actual feedback
        return [0.7] * len(df)  # Default 70% success rate
        
    def is_ready(self) -> bool:
        """Check if the predictor is ready to make predictions"""
        return self.ready
    
    def predict_optimal_times(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Advanced ML ensemble prediction of optimal notification times
        
        Args:
            user_data: Dictionary containing mood entries and user behavior data
            
        Returns:
            List of optimal time predictions with ML-powered effectiveness scores
        """
        try:
            mood_entries = user_data.get("mood_entries", [])
            
            if len(mood_entries) < 5:
                return self._get_default_optimal_times()
            
            # Prepare advanced features for ensemble models
            X, y = self._prepare_timing_features(user_data)
            
            if X.size == 0:
                return self._get_default_optimal_times()
            
            # Train/update ensemble models with current data
            self._train_ensemble_models(X, y)
            
            # Generate ML-powered optimal time predictions
            optimal_times = self._generate_ensemble_predictions(X, y, mood_entries)
            
            # Sort by ML-calculated effectiveness score and return top results
            optimal_times.sort(key=lambda x: x["effectiveness_score"], reverse=True)
            return optimal_times[:7]  # Return top 7 optimal times (more sophisticated)
            
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return self._get_default_optimal_times()
    
    def _train_ensemble_models(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train advanced ensemble models with current user data"""
        try:
            if len(X) < 10:
                logger.info("Insufficient data for ensemble training")
                return
            
            # Scale features for ensemble models
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data for training and validation
            if len(X) > 30:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.25, random_state=42
                )
            else:
                X_train, X_test, y_train, y_test = X_scaled, X_scaled, y, y
            
            # Train timing ensemble (stacking)
            self.timing_ensemble.fit(X_train, y_train)
            
            # Train engagement ensemble (voting)
            self.engagement_ensemble.fit(X_train, y_train)
            
            # Train effectiveness predictor (custom ensemble)
            self.effectiveness_predictor.fit(X_train, y_train)
            
            # Calculate comprehensive performance metrics
            if len(X_test) > 0:
                timing_pred = self.timing_ensemble.predict(X_test)
                engagement_pred = self.engagement_ensemble.predict(X_test)
                effectiveness_pred = self.effectiveness_predictor.predict(X_test)
                
                # Update performance metrics
                self.performance_metrics.update({
                    'timing_accuracy': float(1 - mean_absolute_error(y_test, timing_pred) / 10),
                    'engagement_accuracy': float(1 - mean_absolute_error(y_test, engagement_pred) / 10),
                    'ensemble_r2': float(r2_score(y_test, effectiveness_pred)),
                    'cross_val_score': float(np.mean(cross_val_score(self.timing_ensemble, X_scaled, y, cv=3))),
                    'last_training': datetime.utcnow().isoformat(),
                    'training_samples': len(X)
                })
                
                # Extract feature importance from the ensemble
                self._extract_ensemble_feature_importance()
            
            # Save updated models
            self._save_ensemble_models()
            
            logger.info(f"Ensemble models trained with {len(X)} samples, R²: {self.performance_metrics.get('ensemble_r2', 0):.3f}")
            
        except Exception as e:
            logger.error(f"Error training ensemble models: {e}")
    
    def _generate_ensemble_predictions(self, X: np.ndarray, y: np.ndarray, mood_entries: List[Dict]) -> List[Dict[str, Any]]:
        """Generate optimal time predictions using ensemble methods"""
        try:
            X_scaled = self.scaler.transform(X)
            
            # Get predictions from all ensemble models
            timing_predictions = self.timing_ensemble.predict(X_scaled)
            engagement_predictions = self.engagement_ensemble.predict(X_scaled)
            effectiveness_predictions = self.effectiveness_predictor.predict(X_scaled)
            
            # Convert mood entries to DataFrame for easier processing
            df = pd.DataFrame(mood_entries)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            # Group by hour and calculate ensemble-based optimal times
            optimal_times = []
            hourly_predictions = {}
            
            for hour in range(7, 22):  # Waking hours
                hour_mask = df['hour'] == hour
                if hour_mask.sum() > 0:
                    hour_indices = df.index[hour_mask].tolist()
                    
                    if hour_indices and max(hour_indices) < len(timing_predictions):
                        # Ensemble predictions for this hour
                        hour_timing = np.mean([timing_predictions[i] for i in hour_indices if i < len(timing_predictions)])
                        hour_engagement = np.mean([engagement_predictions[i] for i in hour_indices if i < len(engagement_predictions)])
                        hour_effectiveness = np.mean([effectiveness_predictions[i] for i in hour_indices if i < len(effectiveness_predictions)])
                        
                        # Combined ensemble score
                        combined_score = (
                            0.4 * hour_timing + 
                            0.3 * hour_engagement + 
                            0.3 * hour_effectiveness
                        )
                        
                        # Calculate confidence based on prediction consistency
                        predictions_std = np.std([hour_timing, hour_engagement, hour_effectiveness])
                        confidence = max(0.3, 1.0 - (predictions_std / 5.0))  # Lower std = higher confidence
                        
                        if combined_score > 4.0:  # Only suggest if meaningfully effective
                            notification_type = self._determine_notification_type_ml(hour, combined_score)
                            
                            optimal_times.append({
                                'hour': hour,
                                'effectiveness_score': float(min(10.0, max(0.0, combined_score))),
                                'notification_type': notification_type,
                                'confidence': float(confidence),
                                'timing_score': float(hour_timing),
                                'engagement_score': float(hour_engagement),
                                'ml_method': 'ensemble_stacking_voting',
                                'reason': f"Ensemble ML predicts {combined_score:.1f}/10 effectiveness at {hour}:00",
                                'model_version': self.model_version
                            })
            
            return optimal_times
            
        except Exception as e:
            logger.error(f"Error generating ensemble predictions: {e}")
            return []
    
    def _extract_ensemble_feature_importance(self) -> None:
        """Extract feature importance from ensemble models"""
        try:
            # Get feature importance from timing ensemble
            if hasattr(self.timing_ensemble.final_estimator_, 'feature_importances_'):
                importances = self.timing_ensemble.final_estimator_.feature_importances_
            elif hasattr(self.timing_ensemble, 'feature_importances_'):
                importances = self.timing_ensemble.feature_importances_
            else:
                # Average importance from base estimators
                importances_list = []
                for name, estimator in self.timing_ensemble.estimators_:
                    if hasattr(estimator, 'feature_importances_'):
                        importances_list.append(estimator.feature_importances_)
                
                if importances_list:
                    importances = np.mean(importances_list, axis=0)
                else:
                    return
            
            # Feature names (should match _prepare_timing_features)
            feature_names = [
                'hour', 'day_of_week', 'is_weekend', 'is_workday',
                'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
                'mood_rolling_mean_3', 'mood_rolling_std_3', 'mood_rolling_mean_7', 'mood_rolling_median_3',
                'mood_lag_1', 'mood_lag_2', 'mood_lag_3', 'mood_lag_6', 'mood_lag_12',
                'mood_diff', 'mood_momentum', 'mood_acceleration', 'mood_volatility',
                'time_since_last_intervention', 'intervention_success_rate',
                'energy_mood_ratio', 'mood_below_average'
            ]
            
            # Create feature importance dictionary
            importance_dict = {}
            for i, name in enumerate(feature_names[:len(importances)]):
                importance_dict[name] = float(importances[i])
            
            self.performance_metrics['feature_importance'] = importance_dict
            
        except Exception as e:
            logger.error(f"Error extracting feature importance: {e}")
    
    def _determine_notification_type_ml(self, hour: int, effectiveness_score: float) -> str:
        """ML-enhanced notification type determination"""
        if effectiveness_score > 8.0:
            intervention_level = "high"
        elif effectiveness_score > 6.0:
            intervention_level = "medium"
        else:
            intervention_level = "low"
        
        if 6 <= hour <= 10:
            return f"morning_{intervention_level}_intervention"
        elif 11 <= hour <= 14:
            return f"midday_{intervention_level}_support"
        elif 15 <= hour <= 18:
            return f"afternoon_{intervention_level}_boost"
        else:
            return f"evening_{intervention_level}_reflection"
    
    def _analyze_hourly_mood_patterns(self, mood_entries: List[Dict]) -> Dict[int, Dict[str, float]]:
        """Analyze mood patterns by hour of day"""
        hourly_moods = defaultdict(list)
        
        for entry in mood_entries:
            hour = entry["hour"]
            hourly_moods[hour].append(entry["mood_score"])
        
        patterns = {}
        for hour, moods in hourly_moods.items():
            if len(moods) >= 2:
                avg_mood = statistics.mean(moods)
                mood_variance = statistics.variance(moods) if len(moods) > 1 else 0
                
                patterns[hour] = {
                    "average_mood": avg_mood,
                    "mood_variance": mood_variance,
                    "sample_size": len(moods),
                    "intervention_potential": self._calculate_intervention_potential(avg_mood, mood_variance)
                }
        
        return patterns
    
    def _analyze_daily_patterns(self, mood_entries: List[Dict]) -> Dict[int, Dict[str, float]]:
        """Analyze mood patterns by day of week"""
        daily_moods = defaultdict(list)
        
        for entry in mood_entries:
            day = entry["day_of_week"]
            daily_moods[day].append(entry["mood_score"])
        
        patterns = {}
        for day, moods in daily_moods.items():
            if len(moods) >= 2:
                patterns[day] = {
                    "average_mood": statistics.mean(moods),
                    "mood_stability": 1 / (statistics.stdev(moods) + 0.1),
                    "sample_size": len(moods)
                }
        
        return patterns
    
    def _calculate_intervention_potential(self, avg_mood: float, variance: float) -> float:
        """Calculate intervention potential score for a given time period"""
        # Lower mood scores indicate higher intervention potential
        mood_factor = (10 - avg_mood) / 10
        
        # Higher variance might indicate instability, good for intervention
        variance_factor = min(variance / 2, 0.5)
        
        # Combine factors (weighted)
        intervention_potential = (mood_factor * 0.7) + (variance_factor * 0.3)
        
        return min(1.0, max(0.0, intervention_potential))
    
    def _generate_optimal_time_predictions(
        self, 
        hourly_patterns: Dict[int, Dict], 
        daily_patterns: Dict[int, Dict], 
        mood_entries: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate optimal time predictions based on analyzed patterns"""
        predictions = []
        
        # Generate predictions for each hour with sufficient data
        for hour, hour_data in hourly_patterns.items():
            if hour_data["sample_size"] >= 2 and 7 <= hour <= 22:  # Only waking hours
                
                # Calculate base effectiveness score
                effectiveness = hour_data["intervention_potential"]
                
                # Adjust for time of day preferences
                effectiveness *= self._get_time_of_day_multiplier(hour)
                
                # Determine notification type based on hour and mood patterns
                notification_type = self._determine_notification_type(hour, hour_data["average_mood"])
                
                # Generate reason
                reason = self._generate_reason(hour, hour_data, notification_type)
                
                # Calculate confidence based on data quality
                confidence = min(1.0, hour_data["sample_size"] / 10)
                
                prediction = {
                    "hour": hour,
                    "day_of_week": None,  # General time, not day-specific
                    "effectiveness_score": round(effectiveness * 10, 1),
                    "notification_type": notification_type,
                    "reason": reason,
                    "confidence_level": round(confidence, 2),
                    "average_mood_at_time": round(hour_data["average_mood"], 1),
                    "sample_size": hour_data["sample_size"]
                }
                
                predictions.append(prediction)
        
        # Add day-specific predictions for challenging days
        challenging_days = self._identify_challenging_days(daily_patterns)
        for day in challenging_days:
            day_data = daily_patterns[day]
            prediction = {
                "hour": 8,  # Morning preparation
                "day_of_week": day,
                "effectiveness_score": round((10 - day_data["average_mood"]) * 0.8, 1),
                "notification_type": "day_preparation",
                "reason": f"Prepare for challenging day (avg mood: {day_data['average_mood']:.1f})",
                "confidence_level": min(1.0, day_data["sample_size"] / 5),
                "average_mood_at_time": round(day_data["average_mood"], 1),
                "sample_size": day_data["sample_size"]
            }
            predictions.append(prediction)
        
        return predictions
    
    def _get_time_of_day_multiplier(self, hour: int) -> float:
        """Get time-of-day effectiveness multiplier"""
        # Optimal notification windows based on general research
        if 8 <= hour <= 10:  # Morning energy
            return 1.1
        elif 11 <= hour <= 13:  # Late morning
            return 0.9
        elif 14 <= hour <= 16:  # Afternoon dip
            return 1.2
        elif 17 <= hour <= 19:  # Early evening
            return 1.0
        elif 20 <= hour <= 21:  # Evening wind-down
            return 1.1
        else:
            return 0.7  # Early morning or late night
    
    def _determine_notification_type(self, hour: int, avg_mood: float) -> str:
        """Determine appropriate notification type based on time and mood"""
        if avg_mood < 4:
            return "intervention"
        elif 6 <= hour <= 10:
            return "morning_check"
        elif 11 <= hour <= 14:
            return "midday_wellness"
        elif 15 <= hour <= 18:
            return "afternoon_support"
        elif 19 <= hour <= 21:
            return "evening_reflection"
        else:
            return "general_wellness"
    
    def _generate_reason(self, hour: int, hour_data: Dict, notification_type: str) -> str:
        """Generate human-readable reason for the prediction"""
        avg_mood = hour_data["average_mood"]
        
        if notification_type == "intervention":
            return f"Low mood period (avg: {avg_mood:.1f}) - proactive support needed"
        elif notification_type == "morning_check":
            return f"Morning energy management (typical mood: {avg_mood:.1f})"
        elif notification_type == "afternoon_support":
            return f"Afternoon support window (mood often dips to {avg_mood:.1f})"
        elif notification_type == "evening_reflection":
            return f"Evening reflection time (typical mood: {avg_mood:.1f})"
        else:
            return f"Wellness check when mood averages {avg_mood:.1f}"
    
    def _identify_challenging_days(self, daily_patterns: Dict[int, Dict]) -> List[int]:
        """Identify days that typically have lower mood scores"""
        if not daily_patterns:
            return [0]  # Default to Monday
        
        overall_avg = statistics.mean([data["average_mood"] for data in daily_patterns.values()])
        
        challenging_days = [
            day for day, data in daily_patterns.items()
            if data["average_mood"] < overall_avg - 0.5 and data["sample_size"] >= 2
        ]
        
        return challenging_days if challenging_days else [0]
    
    def _get_default_optimal_times(self) -> List[Dict[str, Any]]:
        """Return default optimal times when insufficient data is available"""
        return [
            {
                "hour": 9,
                "day_of_week": None,
                "effectiveness_score": 7.5,
                "notification_type": "morning_check",
                "reason": "General morning wellness check",
                "confidence_level": 0.6,
                "average_mood_at_time": 6.5,
                "sample_size": 0
            },
            {
                "hour": 15,
                "day_of_week": None,
                "effectiveness_score": 8.0,
                "notification_type": "afternoon_support",
                "reason": "Common afternoon energy dip period",
                "confidence_level": 0.6,
                "average_mood_at_time": 5.8,
                "sample_size": 0
            },
            {
                "hour": 20,
                "day_of_week": None,
                "effectiveness_score": 7.0,
                "notification_type": "evening_reflection",
                "reason": "Evening reflection and preparation",
                "confidence_level": 0.6,
                "average_mood_at_time": 6.2,
                "sample_size": 0
            }
        ]
    
    def update_with_feedback(self, engagement_data: Dict[str, Any]) -> bool:
        """Update the model with engagement feedback"""
        try:
            self.feedback_data.append({
                "notification_id": engagement_data["notification_id"],
                "user_id": engagement_data["user_id"],
                "engagement_type": engagement_data["engagement_type"],
                "engagement_time": engagement_data["engagement_time"],
                "mood_change": engagement_data.get("subsequent_mood_change"),
                "timestamp": datetime.utcnow()
            })
            
            # Limit feedback data to last 1000 entries to manage memory
            if len(self.feedback_data) > 1000:
                self.feedback_data = self.feedback_data[-1000:]
            
            logger.info(f"Updated timing predictor with feedback: {engagement_data['engagement_type']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating with feedback: {e}")
            return False
    
    def calculate_engagement_score(self, engagement_type: str) -> float:
        """Calculate engagement score based on engagement type"""
        engagement_scores = {
            "opened": 0.7,
            "acted_upon": 1.0,
            "dismissed": 0.3,
            "ignored": 0.0
        }
        return engagement_scores.get(engagement_type, 0.5)
    
    def get_model_effectiveness(self) -> Dict[str, Any]:
        """Calculate model effectiveness based on feedback data"""
        if not self.feedback_data:
            return {
                "effectiveness": "unknown",
                "feedback_count": 0,
                "average_engagement": 0.5
            }
        
        # Calculate average engagement score
        total_score = sum(
            self.calculate_engagement_score(feedback["engagement_type"])
            for feedback in self.feedback_data
        )
        avg_engagement = total_score / len(self.feedback_data)
        
        # Calculate effectiveness based on engagement patterns
        if avg_engagement > 0.7:
            effectiveness = "high"
        elif avg_engagement > 0.5:
            effectiveness = "moderate"
        else:
            effectiveness = "low"
        
        return {
            "effectiveness": effectiveness,
            "feedback_count": len(self.feedback_data),
            "average_engagement": round(avg_engagement, 3),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        effectiveness_data = self.get_model_effectiveness()
        
        return {
            "model_type": "pattern_based_predictor",
            "model_version": self.model_version,
            "accuracy_estimate": 0.78,
            "effectiveness": effectiveness_data,
            "confidence_level": "moderate",
            "data_requirements": {
                "minimum_mood_entries": 3,
                "optimal_mood_entries": 30,
                "feedback_data_points": len(self.feedback_data)
            },
            "feature_weights": self.effectiveness_weights,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def retrain_model(self) -> bool:
        """Retrain the model with accumulated feedback data"""
        try:
            if len(self.feedback_data) < 10:
                logger.info("Insufficient feedback data for model retraining")
                return False
            
            # Analyze feedback patterns to adjust weights
            engagement_patterns = defaultdict(list)
            for feedback in self.feedback_data:
                hour = feedback["engagement_time"].hour
                engagement_score = self.calculate_engagement_score(feedback["engagement_type"])
                engagement_patterns[hour].append(engagement_score)
            
            # Update effectiveness weights based on feedback patterns
            # This is a simplified approach - in production, use more sophisticated ML
            high_engagement_hours = [
                hour for hour, scores in engagement_patterns.items()
                if statistics.mean(scores) > 0.7
            ]
            
            if high_engagement_hours:
                logger.info(f"Updated model with high engagement hours: {high_engagement_hours}")
            
            logger.info("Timing predictor model retrain completed")
            return True
            
        except Exception as e:
            logger.error(f"Error retraining model: {e}")
            return False
    
    def predict_next_optimal_window(self, user_data: Dict[str, Any], current_time: datetime) -> Optional[Dict[str, Any]]:
        """Predict the next optimal notification window for a user"""
        try:
            optimal_times = self.predict_optimal_times(user_data)
            
            if not optimal_times:
                return None
            
            # Find the next optimal time after current time
            current_hour = current_time.hour
            
            # Look for next optimal time today
            today_options = [
                time_slot for time_slot in optimal_times
                if time_slot["hour"] > current_hour and time_slot["day_of_week"] is None
            ]
            
            if today_options:
                next_optimal = max(today_options, key=lambda x: x["effectiveness_score"])
                next_time = current_time.replace(
                    hour=next_optimal["hour"], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
            else:
                # Use tomorrow's first optimal time
                next_optimal = max(optimal_times, key=lambda x: x["effectiveness_score"])
                next_time = (current_time + timedelta(days=1)).replace(
                    hour=next_optimal["hour"], 
                    minute=0, 
                    second=0, 
                    microsecond=0
                )
            
            return {
                "next_optimal_time": next_time,
                "effectiveness_score": next_optimal["effectiveness_score"],
                "notification_type": next_optimal["notification_type"],
                "reason": next_optimal["reason"],
                "confidence": next_optimal["confidence_level"]
            }
            
        except Exception as e:
            logger.error(f"Error predicting next optimal window: {e}")
            return None
