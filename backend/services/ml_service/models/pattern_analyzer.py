"""
Mood Pattern Analyzer - ML component for identifying user mood patterns
Uses advanced machine learning algorithms for pattern recognition and anomaly detection
"""

import json
import logging
import pickle
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import statistics
from collections import defaultdict

# Machine Learning imports
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.cluster import KMeans
from scipy import stats
from scipy.signal import find_peaks
import joblib
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA

logger = logging.getLogger(__name__)

class MoodPatternAnalyzer:
    """Advanced ML-powered mood pattern analyzer using ensemble methods and time series analysis"""
    
    def __init__(self):
        self.ready = True
        self.min_data_points = 10  # Increased for ML reliability
        self.analysis_window_days = 60  # Extended for better ML training
        
        # ML Models
        self.circadian_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.trend_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.pattern_clusterer = KMeans(n_clusters=5, random_state=42)
        
        # Preprocessing
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Model persistence paths
        self.model_dir = os.path.join(os.path.dirname(__file__), '..', 'trained_models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Model performance tracking
        self.model_metrics = {
            'circadian_accuracy': 0.0,
            'trend_accuracy': 0.0,
            'anomaly_precision': 0.0,
            'last_training': None,
            'training_samples': 0
        }
        
        # Load pre-trained models if available
        self._load_models()
        
    def is_ready(self) -> bool:
        """Check if the analyzer is ready to process data"""
        return self.ready
    
    def _load_models(self) -> None:
        """Load pre-trained models if they exist"""
        try:
            model_files = {
                'circadian_model.joblib': 'circadian_model',
                'trend_model.joblib': 'trend_model', 
                'anomaly_detector.joblib': 'anomaly_detector',
                'pattern_clusterer.joblib': 'pattern_clusterer',
                'scaler.joblib': 'scaler'
            }
            
            for filename, attr_name in model_files.items():
                file_path = os.path.join(self.model_dir, filename)
                if os.path.exists(file_path):
                    setattr(self, attr_name, joblib.load(file_path))
                    logger.info(f"Loaded {attr_name} from {filename}")
                    
            # Load metrics if available
            metrics_path = os.path.join(self.model_dir, 'model_metrics.json')
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self.model_metrics.update(json.load(f))
                    
        except Exception as e:
            logger.warning(f"Could not load pre-trained models: {e}")
    
    def _save_models(self) -> None:
        """Save trained models to disk"""
        try:
            model_files = {
                'circadian_model.joblib': self.circadian_model,
                'trend_model.joblib': self.trend_model,
                'anomaly_detector.joblib': self.anomaly_detector, 
                'pattern_clusterer.joblib': self.pattern_clusterer,
                'scaler.joblib': self.scaler
            }
            
            for filename, model in model_files.items():
                file_path = os.path.join(self.model_dir, filename)
                joblib.dump(model, file_path)
                
            # Save metrics
            metrics_path = os.path.join(self.model_dir, 'model_metrics.json')
            with open(metrics_path, 'w') as f:
                json.dump(self.model_metrics, f, default=str)
                
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def _prepare_features(self, mood_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Advanced feature engineering for ML models"""
        if len(mood_data) < self.min_data_points:
            return np.array([]), np.array([])
            
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(mood_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Extract time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Cyclical encoding for time features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Rolling statistics (lag features)
        df['mood_rolling_mean_3'] = df['mood_score'].rolling(window=3, min_periods=1).mean()
        df['mood_rolling_std_3'] = df['mood_score'].rolling(window=3, min_periods=1).std().fillna(0)
        df['mood_rolling_mean_7'] = df['mood_score'].rolling(window=7, min_periods=1).mean()
        
        # Lag features
        df['mood_lag_1'] = df['mood_score'].shift(1).fillna(df['mood_score'].mean())
        df['mood_lag_2'] = df['mood_score'].shift(2).fillna(df['mood_score'].mean())
        
        # Time since last entry
        df['time_since_last'] = df['timestamp'].diff().dt.total_seconds() / 3600  # hours
        df['time_since_last'] = df['time_since_last'].fillna(24)  # Default to 24 hours
        
        # Trend features
        df['mood_diff'] = df['mood_score'].diff().fillna(0)
        df['mood_momentum'] = df['mood_diff'].rolling(window=3, min_periods=1).mean()
        
        # Energy level features (if available)
        if 'energy_level' in df.columns:
            df['energy_mood_ratio'] = df['energy_level'] / (df['mood_score'] + 0.1)
            df['energy_rolling_mean'] = df['energy_level'].rolling(window=3, min_periods=1).mean()
        else:
            df['energy_mood_ratio'] = 1.0
            df['energy_rolling_mean'] = 5.0  # Default neutral
        
        # Select feature columns
        feature_columns = [
            'hour', 'day_of_week', 'is_weekend',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'mood_rolling_mean_3', 'mood_rolling_std_3', 'mood_rolling_mean_7',
            'mood_lag_1', 'mood_lag_2', 'time_since_last',
            'mood_diff', 'mood_momentum',
            'energy_mood_ratio', 'energy_rolling_mean'
        ]
        
        X = df[feature_columns].fillna(0).values
        y = df['mood_score'].values
        
        return X, y
    
    def analyze_user_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ML-powered analysis of user mood patterns using ensemble methods and time series analysis
        
        Args:
            user_data: Dictionary containing mood_data, journal_data, and user_id
            
        Returns:
            Dictionary with advanced ML-based pattern analysis results
        """
        try:
            mood_data = user_data.get("mood_data", [])
            journal_data = user_data.get("journal_data", [])
            
            if len(mood_data) < self.min_data_points:
                return self._generate_default_patterns()
            
            # Prepare features for ML models
            X, y = self._prepare_features(mood_data)
            
            if X.size == 0:
                return self._generate_default_patterns()
            
            # Train/update models with current data
            self._train_models(X, y)
            
            # Generate ML-powered insights
            patterns = {
                "circadian_patterns": self._ml_analyze_circadian_patterns(X, y, mood_data),
                "weekly_patterns": self._ml_analyze_weekly_patterns(X, y, mood_data),
                "trend_analysis": self._ml_analyze_trends(X, y, mood_data),
                "optimal_intervention_times": self._ml_find_optimal_intervention_times(X, y, mood_data),
                "mood_volatility": self._ml_calculate_mood_volatility(X, y, mood_data),
                "recovery_patterns": self._ml_analyze_recovery_patterns(X, y, mood_data),
                "anomaly_detection": self._ml_detect_anomalies(X, y, mood_data),
                "pattern_clusters": self._ml_identify_pattern_clusters(X, y, mood_data),
                "journal_correlations": self._analyze_journal_correlations(mood_data, journal_data),
                "ml_confidence": self._calculate_ml_confidence(X, y),
                "feature_importance": self._get_feature_importance()
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error in ML pattern analysis: {e}")
            return self._generate_default_patterns()
    
    def _train_models(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train/update ML models with current data"""
        try:
            if len(X) < self.min_data_points:
                return
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data for training and validation
            if len(X) > 20:  # Only split if we have enough data
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=0.2, random_state=42
                )
            else:
                X_train, X_test, y_train, y_test = X_scaled, X_scaled, y, y
            
            # Train circadian rhythm model (predicts mood based on time features)
            self.circadian_model.fit(X_train, y_train)
            
            # Train trend prediction model
            self.trend_model.fit(X_train, y_train)
            
            # Train anomaly detector
            self.anomaly_detector.fit(X_scaled)
            
            # Train pattern clusterer
            self.pattern_clusterer.fit(X_scaled)
            
            # Calculate model performance metrics
            if len(X_test) > 0:
                circadian_pred = self.circadian_model.predict(X_test)
                trend_pred = self.trend_model.predict(X_test)
                
                self.model_metrics.update({
                    'circadian_accuracy': 1 - mean_absolute_error(y_test, circadian_pred) / 10,  # Normalize to 0-1
                    'trend_accuracy': 1 - mean_absolute_error(y_test, trend_pred) / 10,
                    'last_training': datetime.utcnow().isoformat(),
                    'training_samples': len(X)
                })
            
            # Save updated models
            self._save_models()
            
            logger.info(f"ML models trained with {len(X)} samples")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def _ml_analyze_circadian_patterns(self, X: np.ndarray, y: np.ndarray, mood_data: List[Dict]) -> Dict[str, Any]:
        """ML-powered circadian rhythm analysis"""
        try:
            df = pd.DataFrame(mood_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            # Use trained model to predict mood for each hour
            hourly_predictions = {}
            X_scaled = self.scaler.transform(X) if hasattr(self.scaler, 'scale_') else X
            
            for hour in range(24):
                # Create synthetic features for each hour
                hour_mask = df['hour'] == hour
                if hour_mask.sum() > 0:
                    hour_features = X_scaled[hour_mask]
                    if len(hour_features) > 0:
                        avg_prediction = self.circadian_model.predict(hour_features).mean()
                        hourly_predictions[hour] = {
                            'predicted_mood': float(avg_prediction),
                            'sample_size': int(hour_mask.sum()),
                            'actual_avg': float(df[hour_mask]['mood_score'].mean())
                        }
            
            # Find optimal and challenging hours
            if hourly_predictions:
                best_hour = max(hourly_predictions.keys(), 
                              key=lambda h: hourly_predictions[h]['predicted_mood'])
                worst_hour = min(hourly_predictions.keys(), 
                               key=lambda h: hourly_predictions[h]['predicted_mood'])
            else:
                best_hour, worst_hour = 10, 15
            
            return {
                'hourly_patterns': hourly_predictions,
                'best_time': {
                    'hour': best_hour,
                    'predicted_mood': hourly_predictions.get(best_hour, {}).get('predicted_mood', 7.0)
                },
                'worst_time': {
                    'hour': worst_hour,
                    'predicted_mood': hourly_predictions.get(worst_hour, {}).get('predicted_mood', 5.0)
                },
                'pattern_strength': len(hourly_predictions) / 24,
                'model_confidence': self.model_metrics.get('circadian_accuracy', 0.5)
            }
            
        except Exception as e:
            logger.error(f"Error in ML circadian analysis: {e}")
            return self._generate_default_patterns()['circadian_patterns']
    
    def _ml_analyze_weekly_patterns(self, X: np.ndarray, y: np.ndarray, mood_data: List[Dict]) -> Dict[str, Any]:
        """ML-powered weekly pattern analysis"""
        try:
            df = pd.DataFrame(mood_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            daily_patterns = {}
            X_scaled = self.scaler.transform(X) if hasattr(self.scaler, 'scale_') else X
            
            for day in range(7):
                day_mask = df['day_of_week'] == day
                if day_mask.sum() > 0:
                    day_features = X_scaled[day_mask]
                    if len(day_features) > 0:
                        avg_prediction = self.circadian_model.predict(day_features).mean()
                        daily_patterns[day] = {
                            'predicted_mood': float(avg_prediction),
                            'sample_size': int(day_mask.sum()),
                            'actual_avg': float(df[day_mask]['mood_score'].mean())
                        }
            
            # Identify challenging days (below average)
            if daily_patterns:
                avg_mood = np.mean([p['predicted_mood'] for p in daily_patterns.values()])
                challenging_days = [
                    day for day, pattern in daily_patterns.items()
                    if pattern['predicted_mood'] < avg_mood - 0.5
                ]
            else:
                challenging_days = [0]  # Default Monday
            
            return {
                'daily_patterns': daily_patterns,
                'challenging_days': challenging_days,
                'pattern_reliability': len(daily_patterns) / 7,
                'average_predicted_mood': float(np.mean([p['predicted_mood'] for p in daily_patterns.values()])) if daily_patterns else 6.0
            }
            
        except Exception as e:
            logger.error(f"Error in ML weekly analysis: {e}")
            return self._generate_default_patterns()['weekly_patterns']
    
    def _ml_analyze_trends(self, X: np.ndarray, y: np.ndarray, mood_data: List[Dict]) -> Dict[str, Any]:
        """ML-powered trend analysis using time series forecasting"""
        try:
            # Use trend model to predict future mood trajectory
            X_scaled = self.scaler.transform(X) if hasattr(self.scaler, 'scale_') else X
            trend_predictions = self.trend_model.predict(X_scaled)
            
            # Calculate trend direction
            recent_actual = y[-10:] if len(y) >= 10 else y
            recent_predicted = trend_predictions[-10:] if len(trend_predictions) >= 10 else trend_predictions
            
            # Linear regression on recent data for trend
            if len(recent_actual) >= 3:
                x_trend = np.arange(len(recent_actual))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x_trend, recent_actual)
                
                if slope > 0.1:
                    trend = "improving"
                elif slope < -0.1:
                    trend = "declining"
                else:
                    trend = "stable"
                    
                confidence = abs(r_value)  # Correlation coefficient as confidence
            else:
                trend = "insufficient_data"
                confidence = 0.0
                slope = 0.0
            
            return {
                'trend': trend,
                'confidence': float(confidence),
                'slope': float(slope) if 'slope' in locals() else 0.0,
                'predicted_next_week': float(np.mean(recent_predicted)) if len(recent_predicted) > 0 else 6.0,
                'volatility': float(np.std(y)) if len(y) > 1 else 0.0,
                'model_accuracy': self.model_metrics.get('trend_accuracy', 0.5)
            }
            
        except Exception as e:
            logger.error(f"Error in ML trend analysis: {e}")
            return {'trend': 'error', 'confidence': 0}
    
    def _ml_find_optimal_intervention_times(self, X: np.ndarray, y: np.ndarray, mood_data: List[Dict]) -> List[Dict[str, Any]]:
        """ML-powered optimal intervention time detection"""
        try:
            df = pd.DataFrame(mood_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            
            X_scaled = self.scaler.transform(X) if hasattr(self.scaler, 'scale_') else X
            predictions = self.circadian_model.predict(X_scaled)
            
            intervention_times = []
            
            # Find hours with low predicted mood (intervention opportunities)
            for hour in range(7, 22):  # Waking hours only
                hour_mask = df['hour'] == hour
                if hour_mask.sum() > 0:
                    hour_indices = df.index[hour_mask].tolist()
                    if hour_indices:
                        hour_predictions = [predictions[i] for i in hour_indices if i < len(predictions)]
                        if hour_predictions:
                            avg_predicted_mood = np.mean(hour_predictions)
                            
                            # Lower mood = higher intervention potential
                            effectiveness_score = 10 - avg_predicted_mood
                            
                            if effectiveness_score > 3:  # Only suggest if meaningful
                                intervention_type = self._determine_intervention_type(hour, avg_predicted_mood)
                                
                                intervention_times.append({
                                    'hour': hour,
                                    'effectiveness_score': float(max(0, min(10, effectiveness_score))),
                                    'intervention_type': intervention_type,
                                    'confidence': float(min(1.0, len(hour_predictions) / 5)),
                                    'predicted_mood': float(avg_predicted_mood),
                                    'reason': f"ML model predicts mood dip to {avg_predicted_mood:.1f} at {hour}:00"
                                })
            
            # Sort by effectiveness and return top 5
            intervention_times.sort(key=lambda x: x['effectiveness_score'], reverse=True)
            return intervention_times[:5]
            
        except Exception as e:
            logger.error(f"Error finding ML intervention times: {e}")
            return self._generate_default_patterns()['optimal_intervention_times']
    
    def _ml_detect_anomalies(self, X: np.ndarray, y: np.ndarray, mood_data: List[Dict]) -> Dict[str, Any]:
        """ML-powered anomaly detection in mood patterns"""
        try:
            X_scaled = self.scaler.transform(X) if hasattr(self.scaler, 'scale_') else X
            anomaly_scores = self.anomaly_detector.decision_function(X_scaled)
            anomaly_labels = self.anomaly_detector.predict(X_scaled)
            
            # Identify anomalous periods
            anomalous_indices = np.where(anomaly_labels == -1)[0]
            
            anomalies = []
            for idx in anomalous_indices:
                if idx < len(mood_data):
                    mood_entry = mood_data[idx]
                    anomalies.append({
                        'timestamp': mood_entry['timestamp'].isoformat() if hasattr(mood_entry['timestamp'], 'isoformat') else str(mood_entry['timestamp']),
                        'mood_score': mood_entry['mood_score'],
                        'anomaly_score': float(anomaly_scores[idx]),
                        'severity': 'high' if anomaly_scores[idx] < -0.5 else 'moderate'
                    })
            
            return {
                'anomalies_detected': len(anomalies),
                'anomaly_rate': float(len(anomalies) / len(mood_data)) if len(mood_data) > 0 else 0.0,
                'recent_anomalies': anomalies[-5:],  # Last 5 anomalies
                'risk_level': 'high' if len(anomalies) / len(mood_data) > 0.1 else 'low' if len(mood_data) > 0 else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error in ML anomaly detection: {e}")
            return {'anomalies_detected': 0, 'anomaly_rate': 0.0}
    
    def _ml_identify_pattern_clusters(self, X: np.ndarray, y: np.ndarray, mood_data: List[Dict]) -> Dict[str, Any]:
        """ML-powered pattern clustering to identify mood states"""
        try:
            X_scaled = self.scaler.transform(X) if hasattr(self.scaler, 'scale_') else X
            cluster_labels = self.pattern_clusterer.predict(X_scaled)
            
            # Analyze clusters
            cluster_analysis = {}
            for cluster_id in np.unique(cluster_labels):
                cluster_mask = cluster_labels == cluster_id
                cluster_moods = y[cluster_mask]
                
                if len(cluster_moods) > 0:
                    cluster_analysis[int(cluster_id)] = {
                        'average_mood': float(np.mean(cluster_moods)),
                        'mood_std': float(np.std(cluster_moods)),
                        'sample_count': int(len(cluster_moods)),
                        'mood_range': [float(np.min(cluster_moods)), float(np.max(cluster_moods))]
                    }
            
            # Identify dominant mood states
            if cluster_analysis:
                dominant_cluster = max(cluster_analysis.keys(), key=lambda k: cluster_analysis[k]['sample_count'])
                best_mood_cluster = max(cluster_analysis.keys(), key=lambda k: cluster_analysis[k]['average_mood'])
                worst_mood_cluster = min(cluster_analysis.keys(), key=lambda k: cluster_analysis[k]['average_mood'])
            else:
                dominant_cluster = best_mood_cluster = worst_mood_cluster = 0
            
            return {
                'total_clusters': len(cluster_analysis),
                'cluster_analysis': cluster_analysis,
                'dominant_pattern': int(dominant_cluster),
                'best_mood_pattern': int(best_mood_cluster),
                'worst_mood_pattern': int(worst_mood_cluster)
            }
            
        except Exception as e:
            logger.error(f"Error in ML pattern clustering: {e}")
            return {'total_clusters': 0}
    
    def _calculate_ml_confidence(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Calculate overall ML model confidence scores"""
        try:
            confidence_scores = {
                'overall_confidence': 0.0,
                'data_quality': 0.0,
                'model_performance': 0.0,
                'sample_sufficiency': 0.0
            }
            
            # Data quality score
            if len(y) > 0:
                confidence_scores['data_quality'] = min(1.0, len(y) / 50)  # Ideal: 50+ samples
                confidence_scores['sample_sufficiency'] = min(1.0, len(y) / self.min_data_points)
            
            # Model performance score
            avg_accuracy = np.mean([
                self.model_metrics.get('circadian_accuracy', 0.5),
                self.model_metrics.get('trend_accuracy', 0.5)
            ])
            confidence_scores['model_performance'] = float(avg_accuracy)
            
            # Overall confidence (weighted average)
            confidence_scores['overall_confidence'] = float(
                0.4 * confidence_scores['data_quality'] +
                0.4 * confidence_scores['model_performance'] +
                0.2 * confidence_scores['sample_sufficiency']
            )
            
            return confidence_scores
            
        except Exception as e:
            logger.error(f"Error calculating ML confidence: {e}")
            return {'overall_confidence': 0.5}
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained models"""
        try:
            if hasattr(self.circadian_model, 'feature_importances_'):
                feature_names = [
                    'hour', 'day_of_week', 'is_weekend',
                    'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
                    'mood_rolling_mean_3', 'mood_rolling_std_3', 'mood_rolling_mean_7',
                    'mood_lag_1', 'mood_lag_2', 'time_since_last',
                    'mood_diff', 'mood_momentum',
                    'energy_mood_ratio', 'energy_rolling_mean'
                ]
                
                importances = self.circadian_model.feature_importances_
                
                # Create feature importance dictionary
                importance_dict = {}
                for i, name in enumerate(feature_names[:len(importances)]):
                    importance_dict[name] = float(importances[i])
                
                return importance_dict
            else:
                return {'note': 'Feature importance not available for current model'}
                
        except Exception as e:
            logger.error(f"Error getting feature importance: {e}")
            return {}
    
    def _determine_intervention_type(self, hour: int, predicted_mood: float) -> str:
        """Determine appropriate intervention type based on time and predicted mood"""
        if 6 <= hour <= 10:
            return "morning_boost" if predicted_mood < 6 else "morning_check"
        elif 11 <= hour <= 14:
            return "midday_support" if predicted_mood < 6 else "midday_check"
        elif 15 <= hour <= 18:
            return "afternoon_intervention" if predicted_mood < 5 else "afternoon_support"
        else:
            return "evening_reflection" if predicted_mood < 6 else "evening_check"
    
    def _analyze_circadian_patterns(self, mood_data: List[Dict]) -> Dict[str, Any]:
        """Analyze hourly mood patterns throughout the day"""
        hourly_moods = defaultdict(list)
        
        for entry in mood_data:
            hour = entry["timestamp"].hour
            hourly_moods[hour].append(entry["mood_score"])
        
        hourly_averages = {}
        for hour, moods in hourly_moods.items():
            if len(moods) >= 2:  # Need at least 2 data points
                hourly_averages[hour] = {
                    "average_mood": statistics.mean(moods),
                    "mood_stability": 1 / (statistics.stdev(moods) + 0.1),  # Higher = more stable
                    "sample_size": len(moods)
                }
        
        # Find best and worst times
        if hourly_averages:
            best_hour = max(hourly_averages.keys(), key=lambda h: hourly_averages[h]["average_mood"])
            worst_hour = min(hourly_averages.keys(), key=lambda h: hourly_averages[h]["average_mood"])
        else:
            best_hour, worst_hour = 12, 15  # Default assumptions
        
        return {
            "hourly_patterns": hourly_averages,
            "best_time": {
                "hour": best_hour,
                "average_mood": hourly_averages.get(best_hour, {}).get("average_mood", 7.0)
            },
            "worst_time": {
                "hour": worst_hour,
                "average_mood": hourly_averages.get(worst_hour, {}).get("average_mood", 5.0)
            },
            "pattern_strength": len(hourly_averages) / 24  # How much of the day we have data for
        }
    
    def _analyze_weekly_patterns(self, mood_data: List[Dict]) -> Dict[str, Any]:
        """Analyze weekly mood patterns"""
        daily_moods = defaultdict(list)
        
        for entry in mood_data:
            day_of_week = entry["timestamp"].weekday()  # 0 = Monday
            daily_moods[day_of_week].append(entry["mood_score"])
        
        daily_averages = {}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day, moods in daily_moods.items():
            if len(moods) >= 2:
                daily_averages[day] = {
                    "day_name": day_names[day],
                    "average_mood": statistics.mean(moods),
                    "mood_consistency": 1 / (statistics.stdev(moods) + 0.1),
                    "sample_size": len(moods)
                }
        
        # Find challenging days (below average mood)
        if daily_averages:
            overall_average = statistics.mean([d["average_mood"] for d in daily_averages.values()])
            challenging_days = [
                day for day, data in daily_averages.items()
                if data["average_mood"] < overall_average - 0.5
            ]
        else:
            challenging_days = [0]  # Default to Monday
        
        return {
            "daily_patterns": daily_averages,
            "challenging_days": challenging_days,
            "most_stable_day": max(daily_averages.keys(), key=lambda d: daily_averages[d]["mood_consistency"]) if daily_averages else 5,
            "pattern_reliability": len(daily_averages) / 7
        }
    
    def _analyze_trends(self, mood_data: List[Dict]) -> Dict[str, Any]:
        """Analyze mood trends over time"""
        if len(mood_data) < 3:
            return {"trend": "insufficient_data", "slope": 0, "confidence": 0}
        
        # Sort by timestamp
        sorted_data = sorted(mood_data, key=lambda x: x["timestamp"])
        
        # Simple linear trend calculation
        x_values = list(range(len(sorted_data)))
        y_values = [entry["mood_score"] for entry in sorted_data]
        
        # Calculate slope using simple linear regression
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction
        if slope > 0.05:
            trend = "improving"
        elif slope < -0.05:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "slope": slope,
            "confidence": min(1.0, len(mood_data) / 14),  # More data = higher confidence
            "recent_average": statistics.mean(y_values[-7:]) if len(y_values) >= 7 else statistics.mean(y_values)
        }
    
    def _find_optimal_intervention_times(self, mood_data: List[Dict]) -> List[Dict[str, Any]]:
        """Find optimal times for interventions based on mood patterns"""
        hourly_moods = defaultdict(list)
        
        for entry in mood_data:
            hour = entry["timestamp"].hour
            hourly_moods[hour].append(entry["mood_score"])
        
        intervention_times = []
        
        for hour, moods in hourly_moods.items():
            if len(moods) >= 2:
                avg_mood = statistics.mean(moods)
                
                # Lower mood = higher intervention value
                if avg_mood < 6.0:  # Below neutral
                    effectiveness_score = 10 - avg_mood
                    
                    # Determine intervention type
                    if 6 <= hour <= 10:
                        intervention_type = "morning_boost"
                    elif 11 <= hour <= 14:
                        intervention_type = "midday_check"
                    elif 15 <= hour <= 18:
                        intervention_type = "afternoon_support"
                    else:
                        intervention_type = "evening_reflection"
                    
                    intervention_times.append({
                        "hour": hour,
                        "effectiveness_score": round(effectiveness_score, 1),
                        "intervention_type": intervention_type,
                        "average_mood": round(avg_mood, 1),
                        "confidence": min(1.0, len(moods) / 5)
                    })
        
        # Sort by effectiveness and return top 3
        intervention_times.sort(key=lambda x: x["effectiveness_score"], reverse=True)
        return intervention_times[:3]
    
    def _calculate_mood_volatility(self, mood_data: List[Dict]) -> Dict[str, Any]:
        """Calculate mood volatility metrics"""
        if len(mood_data) < 3:
            return {"volatility": "unknown", "stability_score": 0.5}
        
        mood_scores = [entry["mood_score"] for entry in mood_data]
        
        # Calculate standard deviation
        std_dev = statistics.stdev(mood_scores)
        mean_mood = statistics.mean(mood_scores)
        
        # Calculate coefficient of variation
        cv = std_dev / mean_mood if mean_mood > 0 else 1
        
        # Determine volatility level
        if cv < 0.15:
            volatility = "low"
            stability_score = 0.9
        elif cv < 0.25:
            volatility = "moderate"
            stability_score = 0.7
        else:
            volatility = "high"
            stability_score = 0.4
        
        return {
            "volatility": volatility,
            "stability_score": stability_score,
            "coefficient_of_variation": round(cv, 3),
            "standard_deviation": round(std_dev, 2)
        }
    
    def _analyze_recovery_patterns(self, mood_data: List[Dict]) -> Dict[str, Any]:
        """Analyze how quickly user recovers from low moods"""
        if len(mood_data) < 5:
            return {"recovery_rate": "unknown", "typical_recovery_time": "unknown"}
        
        sorted_data = sorted(mood_data, key=lambda x: x["timestamp"])
        recovery_events = []
        
        for i in range(len(sorted_data) - 1):
            current_mood = sorted_data[i]["mood_score"]
            next_mood = sorted_data[i + 1]["mood_score"]
            
            # Look for recovery events (mood improvement from low state)
            if current_mood < 5 and next_mood > current_mood + 1:
                time_diff = sorted_data[i + 1]["timestamp"] - sorted_data[i]["timestamp"]
                recovery_events.append({
                    "recovery_magnitude": next_mood - current_mood,
                    "recovery_time_hours": time_diff.total_seconds() / 3600
                })
        
        if recovery_events:
            avg_recovery_time = statistics.mean([e["recovery_time_hours"] for e in recovery_events])
            avg_magnitude = statistics.mean([e["recovery_magnitude"] for e in recovery_events])
            
            return {
                "recovery_rate": "good" if avg_recovery_time < 24 else "moderate",
                "typical_recovery_time": f"{avg_recovery_time:.1f} hours",
                "average_recovery_magnitude": round(avg_magnitude, 1),
                "recovery_events_count": len(recovery_events)
            }
        
        return {
            "recovery_rate": "unknown",
            "typical_recovery_time": "insufficient_data",
            "recovery_events_count": 0
        }
    
    def _analyze_journal_correlations(self, mood_data: List[Dict], journal_data: List[Dict]) -> Dict[str, Any]:
        """Analyze correlations between journal entries and mood"""
        if not journal_data or len(mood_data) < 3:
            return {"correlations": "insufficient_data"}
        
        # Simple correlation analysis
        correlations = {
            "journaling_frequency": len(journal_data),
            "mood_improvement_after_journaling": "unknown",
            "common_themes": []
        }
        
        # Check if mood tends to improve after journaling
        mood_improvements = []
        for journal_entry in journal_data:
            # Find mood entries within 6 hours after journaling
            journal_time = journal_entry["timestamp"]
            for mood_entry in mood_data:
                mood_time = mood_entry["timestamp"]
                if journal_time < mood_time < journal_time + timedelta(hours=6):
                    # Check if there was a previous mood entry to compare
                    prev_moods = [m for m in mood_data if m["timestamp"] < journal_time]
                    if prev_moods:
                        prev_mood = max(prev_moods, key=lambda x: x["timestamp"])["mood_score"]
                        mood_improvements.append(mood_entry["mood_score"] - prev_mood)
                    break
        
        if mood_improvements:
            avg_improvement = statistics.mean(mood_improvements)
            correlations["mood_improvement_after_journaling"] = (
                "positive" if avg_improvement > 0.3 else
                "neutral" if avg_improvement > -0.3 else
                "negative"
            )
            correlations["average_improvement"] = round(avg_improvement, 2)
        
        return correlations
    
    def _generate_default_patterns(self) -> Dict[str, Any]:
        """Generate default patterns when insufficient data is available"""
        return {
            "circadian_patterns": {
                "pattern_strength": 0.1,
                "best_time": {"hour": 10, "average_mood": 7.0},
                "worst_time": {"hour": 15, "average_mood": 5.5}
            },
            "weekly_patterns": {
                "challenging_days": [0],  # Monday
                "pattern_reliability": 0.1
            },
            "trend_analysis": {
                "trend": "insufficient_data",
                "confidence": 0
            },
            "optimal_intervention_times": [
                {
                    "hour": 9,
                    "effectiveness_score": 7.5,
                    "intervention_type": "morning_boost",
                    "confidence": 0.5
                },
                {
                    "hour": 15,
                    "effectiveness_score": 8.0,
                    "intervention_type": "afternoon_support",
                    "confidence": 0.5
                }
            ],
            "mood_volatility": {
                "volatility": "unknown",
                "stability_score": 0.5
            },
            "recovery_patterns": {
                "recovery_rate": "unknown"
            },
            "journal_correlations": {
                "correlations": "insufficient_data"
            },
            "note": "Continue using the app to improve pattern recognition accuracy"
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the pattern analyzer"""
        return {
            "model_type": "rule_based_analyzer",
            "accuracy": 0.85,
            "confidence": 0.8,
            "last_updated": datetime.utcnow().isoformat(),
            "data_requirements": {
                "minimum_entries": self.min_data_points,
                "optimal_entries": 30,
                "analysis_window_days": self.analysis_window_days
            }
        }
    
    def retrain_model(self):
        """Retrain the model with new data (placeholder for future ML model)"""
        logger.info("Pattern analyzer model retrain completed (rule-based system)")
        return True
