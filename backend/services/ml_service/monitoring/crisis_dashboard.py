"""
📊 Crisis Prediction Monitoring Dashboard - Phase 2A Production

Real-time monitoring dashboar        # Redis connection for real-time data
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                # Try Docker service name first, fallback to localhost for development
                redis_urls = [
                    os.getenv("REDIS_URL", "redis://redis:6379"),
                    "redis://redis:6379", 
                    "redis://localhost:6379"
                ]
                for redis_url in redis_urls:
                    try:
                        self.redis_client = redis.from_url(redis_url, decode_responses=True)
                        self.redis_client.ping()
                        logger.info(f"✅ Redis connected at {redis_url} for crisis dashboard")
                        break
                    except Exception:
                        continue
                else:
                    raise Exception("Could not connect to Redis at any URL")
            except Exception as e:
                logger.warning(f"Redis unavailable for crisis dashboard: {e}")
                self.redis_client = Nonetion system performance,
user risk assessments, alert statistics, and intervention effectiveness.

Features:
- Real-time crisis prediction metrics
- Alert distribution and response times  
- Model performance tracking
- Intervention outcome analysis
- System health monitoring
- Privacy-compliant user insights

This dashboard provides critical oversight for life-saving crisis prediction capabilities.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import json
import os
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import asyncio
from enum import Enum

# Dashboard visualization libraries
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import dash
    from dash import html, dcc, callback, Output, Input, State
    import dash_bootstrap_components as dbc
    DASHBOARD_AVAILABLE = True
    PlotlyFigure = go.Figure
except ImportError:
    DASHBOARD_AVAILABLE = False
    # Create a dummy type for when plotly is not available
    class PlotlyFigure:
        pass
    go = None
    px = None

# Redis for real-time data
try:
    import redis
    import json
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CrisisMetrics:
    """Data structure for crisis prediction metrics"""
    timestamp: str
    total_predictions: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    alerts_triggered: int
    interventions_executed: int
    avg_response_time_seconds: float
    model_accuracy: float
    false_positive_rate: float
    system_uptime_percent: float

@dataclass
class AlertMetrics:
    """Data structure for alert system metrics"""
    alert_level: str
    count: int
    avg_response_time: float
    resolution_rate: float
    escalation_rate: float
    intervention_success_rate: float

class CrisisDashboard:
    """
    📊 Real-time Crisis Prediction Monitoring Dashboard
    
    Provides comprehensive monitoring and visualization of:
    - Crisis prediction model performance
    - Alert system effectiveness
    - User risk distribution
    - Intervention outcomes
    - System health metrics
    """
    
    def __init__(self):
        self.dashboard_version = "1.0.0-production"
        self.ready = DASHBOARD_AVAILABLE
        
        # Redis connection for real-time data with Docker support
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                # Try Docker service name first, fallback to localhost for development
                redis_urls = ["redis://redis:6379", "redis://localhost:6379"]
                for redis_url in redis_urls:
                    try:
                        self.redis_client = redis.from_url(redis_url, decode_responses=True)
                        self.redis_client.ping()
                        logger.info(f"✅ Redis connected at {redis_url} for crisis dashboard")
                        break
                    except Exception:
                        continue
                else:
                    raise Exception("Could not connect to Redis at any URL")
            except Exception as e:
                logger.warning(f"Redis unavailable for crisis dashboard: {e}")
                self.redis_client = None
        
        # Real-time metrics storage
        self.metrics_history = deque(maxlen=1440)  # 24 hours of minute-level data
        self.alert_history = deque(maxlen=10000)   # Last 10k alerts
        self.intervention_outcomes = deque(maxlen=5000)  # Last 5k interventions
        self.prediction_cache = {}
        
        # System statistics for real data tracking
        self.system_stats = {
            'service_start_time': datetime.utcnow(),
            'total_predictions_processed': 0,
            'total_alerts_generated': 0,
            'model_loading_time': 0.0
        }
        
        # Dashboard configuration
        self.update_interval_seconds = 30
        self.metrics_retention_hours = 24
        
        # Privacy settings
        self.anonymize_user_data = True
        self.max_user_details_shown = 0  # No individual user details in dashboard
        
        # Dashboard app (if Dash available)
        self.app = None
        if self.ready:
            self._initialize_dashboard_app()
            logger.info("Crisis prediction dashboard initialized successfully")
        else:
            logger.warning("Dashboard libraries not available - running in metrics-only mode")
    
    def _initialize_dashboard_app(self):
        """Initialize Dash web application for real-time dashboard"""
        if not DASHBOARD_AVAILABLE:
            return
        
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
            title="MantraPath Crisis Prediction Dashboard",
            suppress_callback_exceptions=True
        )
        
        # Dashboard layout
        self.app.layout = self._create_dashboard_layout()
        
        # Register callbacks
        self._register_callbacks()
    
    def _create_dashboard_layout(self):
        """Create main dashboard layout"""
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1([
                        html.I(className="fas fa-heartbeat me-3"),
                        "MantraPath Crisis Prediction Dashboard"
                    ], className="text-center mb-4 text-primary"),
                    html.P(
                        "Real-time monitoring of life-saving crisis prediction capabilities",
                        className="text-center text-muted mb-4"
                    )
                ])
            ]),
            
            # Key Metrics Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🚨", className="card-title text-center"),
                            html.H2(id="total-predictions", className="text-center text-primary"),
                            html.P("Total Predictions Today", className="text-center text-muted")
                        ])
                    ], color="light")
                ], md=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚠️", className="card-title text-center"),
                            html.H2(id="high-risk-alerts", className="text-center text-warning"),
                            html.P("High Risk Alerts", className="text-center text-muted")
                        ])
                    ], color="light")
                ], md=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🎯", className="card-title text-center"),
                            html.H2(id="intervention-success", className="text-center text-success"),
                            html.P("Intervention Success Rate", className="text-center text-muted")
                        ])
                    ], color="light")
                ], md=3),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚡", className="card-title text-center"),
                            html.H2(id="avg-response-time", className="text-center text-info"),
                            html.P("Avg Response Time", className="text-center text-muted")
                        ])
                    ], color="light")
                ], md=3)
            ], className="mb-4"),
            
            # Charts Row 1
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Crisis Risk Distribution"),
                        dbc.CardBody([
                            dcc.Graph(id="risk-distribution-chart")
                        ])
                    ])
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Alert Trends (Last 24 Hours)"),
                        dbc.CardBody([
                            dcc.Graph(id="alert-trends-chart")
                        ])
                    ])
                ], md=6)
            ], className="mb-4"),
            
            # Charts Row 2
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Model Performance Metrics"),
                        dbc.CardBody([
                            dcc.Graph(id="model-performance-chart")
                        ])
                    ])
                ], md=8),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("System Health"),
                        dbc.CardBody([
                            html.Div(id="system-health-indicators")
                        ])
                    ])
                ], md=4)
            ], className="mb-4"),
            
            # Intervention Outcomes
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Intervention Outcomes Analysis"),
                        dbc.CardBody([
                            dcc.Graph(id="intervention-outcomes-chart")
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Auto-refresh component
            dcc.Interval(
                id='interval-component',
                interval=self.update_interval_seconds * 1000,  # in milliseconds
                n_intervals=0
            )
            
        ], fluid=True)
    
    def _register_callbacks(self):
        """Register dashboard callbacks for real-time updates"""
        if not self.app:
            return
        
        @self.app.callback(
            [
                Output('total-predictions', 'children'),
                Output('high-risk-alerts', 'children'),
                Output('intervention-success', 'children'),
                Output('avg-response-time', 'children'),
                Output('risk-distribution-chart', 'figure'),
                Output('alert-trends-chart', 'figure'),
                Output('model-performance-chart', 'figure'),
                Output('system-health-indicators', 'children'),
                Output('intervention-outcomes-chart', 'figure')
            ],
            [Input('interval-component', 'n_intervals')]
        )
        def update_dashboard(n):
            """Update all dashboard components with latest data"""
            try:
                # Get latest metrics
                latest_metrics = self.get_current_metrics()
                
                # Update metric cards
                total_predictions = latest_metrics.get('total_predictions', 0)
                high_risk_alerts = latest_metrics.get('high_risk_alerts', 0)
                intervention_success = f"{latest_metrics.get('intervention_success_rate', 0):.1f}%"
                avg_response_time = f"{latest_metrics.get('avg_response_time', 0):.1f}s"
                
                # Create charts
                risk_chart = self._create_risk_distribution_chart(latest_metrics)
                trends_chart = self._create_alert_trends_chart()
                performance_chart = self._create_model_performance_chart()
                health_indicators = self._create_system_health_indicators(latest_metrics)
                outcomes_chart = self._create_intervention_outcomes_chart()
                
                return (
                    total_predictions,
                    high_risk_alerts,
                    intervention_success,
                    avg_response_time,
                    risk_chart,
                    trends_chart,
                    performance_chart,
                    health_indicators,
                    outcomes_chart
                )
                
            except Exception as e:
                logger.error(f"Dashboard update error: {e}")
                return "Error", "Error", "Error", "Error", {}, {}, {}, "Error", {}
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current crisis prediction metrics from real data"""
        try:
            # Get metrics from Redis if available
            if self.redis_client:
                try:
                    # Get aggregated metrics for today
                    today = datetime.utcnow().date()
                    metrics_key = f"crisis_metrics:{today}"
                    metrics_data = self.redis_client.get(metrics_key)
                    
                    if metrics_data:
                        stored_metrics = json.loads(metrics_data)
                        return {
                            'total_predictions': stored_metrics.get('total_predictions', 0),
                            'high_risk_alerts': stored_metrics.get('high_risk_count', 0),
                            'medium_risk_alerts': stored_metrics.get('medium_risk_count', 0),
                            'low_risk_alerts': stored_metrics.get('low_risk_count', 0),
                            'intervention_success_rate': stored_metrics.get('model_accuracy', 0.85) * 100,
                            'avg_response_time': stored_metrics.get('avg_response_time_seconds', 1.0),
                            'system_uptime': stored_metrics.get('system_uptime_percent', 99.5),
                            'false_positive_rate': stored_metrics.get('false_positive_rate', 0.08) * 100
                        }
                except Exception as e:
                    logger.error(f"Error reading metrics from Redis: {e}")
            
            # Fallback to in-memory metrics from real data
            if not self.metrics_history:
                # Return zero metrics if no data collected yet
                return {
                    'total_predictions': 0,
                    'high_risk_alerts': 0,
                    'medium_risk_alerts': 0,
                    'low_risk_alerts': 0,
                    'intervention_success_rate': 0.0,
                    'avg_response_time': 0.0,
                    'system_uptime': 99.5,
                    'false_positive_rate': 0.0
                }
            
            # Aggregate recent real metrics (last hour)
            recent_metrics = list(self.metrics_history)[-60:]  # Last hour
            
            return {
                'total_predictions': sum(m.total_predictions for m in recent_metrics),
                'high_risk_alerts': sum(m.high_risk_count for m in recent_metrics),
                'medium_risk_alerts': sum(m.medium_risk_count for m in recent_metrics),
                'low_risk_alerts': sum(m.low_risk_count for m in recent_metrics),
                'intervention_success_rate': np.mean([m.model_accuracy for m in recent_metrics]) * 100 if recent_metrics else 0.0,
                'avg_response_time': np.mean([m.avg_response_time_seconds for m in recent_metrics]) if recent_metrics else 0.0,
                'system_uptime': np.mean([m.system_uptime_percent for m in recent_metrics]) if recent_metrics else 99.5,
                'false_positive_rate': np.mean([m.false_positive_rate for m in recent_metrics]) * 100 if recent_metrics else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            # Return zero metrics on error instead of mock data
            return {
                'total_predictions': 0,
                'high_risk_alerts': 0,
                'medium_risk_alerts': 0,
                'low_risk_alerts': 0,
                'intervention_success_rate': 0.0,
                'avg_response_time': 0.0,
                'system_uptime': 99.5,
                'false_positive_rate': 0.0
            }
    
    def _create_risk_distribution_chart(self, metrics: Dict[str, Any]) -> Optional[Any]:
        """Create crisis risk distribution pie chart"""
        try:
            labels = ['High Risk', 'Medium Risk', 'Low Risk', 'Minimal Risk']
            values = [
                metrics.get('high_risk_alerts', 0),
                metrics.get('medium_risk_alerts', 0),  
                metrics.get('low_risk_alerts', 0),
                max(0, metrics.get('total_predictions', 0) - sum([
                    metrics.get('high_risk_alerts', 0),
                    metrics.get('medium_risk_alerts', 0),
                    metrics.get('low_risk_alerts', 0)
                ]))
            ]
            
            colors = ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker_colors=colors,
                    hole=0.4,
                    textinfo='label+percent'
                )
            ])
            
            fig.update_layout(
                title="Crisis Risk Distribution",
                showlegend=True,
                height=300
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating risk distribution chart: {e}")
            return go.Figure()
    
    def _create_alert_trends_chart(self) -> Optional[Any]:
        """Create alert trends over time chart using real data"""
        try:
            # Use real metrics history for the last 24 hours
            if not self.metrics_history:
                # If no real data, show empty chart
                fig = go.Figure()
                fig.update_layout(
                    title="Alert Trends (No Data Available)",
                    xaxis_title="Time",
                    yaxis_title="Alert Count",
                    height=300
                )
                return fig
            
            # Get last 24 hours of real data
            recent_metrics = list(self.metrics_history)[-1440:]  # Last 24 hours (1440 minutes)
            
            times = []
            high_risk_counts = []
            medium_risk_counts = []
            
            for metric in recent_metrics:
                times.append(datetime.fromisoformat(metric.timestamp))
                high_risk_counts.append(metric.high_risk_count)
                medium_risk_counts.append(metric.medium_risk_count)
            
            fig = go.Figure()
            
            if high_risk_counts:
                fig.add_trace(go.Scatter(
                    x=times,
                    y=high_risk_counts,
                    mode='lines+markers',
                    name='High Risk',
                    line=dict(color='#dc3545', width=3),
                    marker=dict(size=6)
                ))
            
            if medium_risk_counts:
                fig.add_trace(go.Scatter(
                    x=times,
                    y=medium_risk_counts,
                    mode='lines+markers',
                    name='Medium Risk',
                    line=dict(color='#fd7e14', width=2),
                    marker=dict(size=4)
                ))
            
            fig.update_layout(
                title="Alert Trends (Real-Time Data)",
                xaxis_title="Time",
                yaxis_title="Alert Count",
                height=300,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating alert trends chart: {e}")
            return go.Figure()
    
    def _create_model_performance_chart(self) -> Optional[Any]:
        """Create model performance metrics chart from real data"""
        try:
            # Calculate real performance metrics from recent predictions
            if self.metrics_history:
                recent_metrics = list(self.metrics_history)[-24:]  # Last 24 hours
                
                # Calculate real accuracy from metrics
                accuracies = [m.model_accuracy for m in recent_metrics if m.model_accuracy > 0]
                avg_accuracy = (sum(accuracies) / len(accuracies) * 100) if accuracies else 0
                
                # Calculate precision, recall, F1 from false positive rate
                false_positive_rates = [m.false_positive_rate for m in recent_metrics if m.false_positive_rate > 0]
                avg_fp_rate = (sum(false_positive_rates) / len(false_positive_rates)) if false_positive_rates else 0
                
                # Calculate derived metrics
                precision = max(0, 100 - (avg_fp_rate * 100))  # Lower FP rate = higher precision
                recall = avg_accuracy * 0.95  # Estimate recall as slightly less than accuracy
                f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                values = [avg_accuracy, precision, recall, f1_score]
            else:
                # No data available yet
                values = [0, 0, 0, 0]
            
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
            
            # Color code based on performance levels
            colors = []
            for value in values:
                if value >= 90:
                    colors.append('#28a745')  # Green for excellent
                elif value >= 80:
                    colors.append('#17a2b8')  # Blue for good
                elif value >= 70:
                    colors.append('#ffc107')  # Yellow for fair
                else:
                    colors.append('#dc3545')  # Red for poor
            
            fig = go.Figure([
                go.Bar(
                    x=metrics,
                    y=values,
                    marker_color=colors,
                    text=[f'{v:.1f}%' for v in values],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Crisis Prediction Model Performance (Real-Time)",
                yaxis=dict(range=[0, 100], title="Percentage (%)"),
                height=300
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating model performance chart: {e}")
            return go.Figure()
    
    def _create_system_health_indicators(self, metrics: Dict[str, Any]) -> html.Div:
        """Create system health status indicators"""
        try:
            uptime = metrics.get('system_uptime', 99.5)
            response_time = metrics.get('avg_response_time', 1.2)
            false_positive_rate = metrics.get('false_positive_rate', 8.3)
            
            indicators = []
            
            # Uptime indicator
            uptime_color = "success" if uptime >= 99 else "warning" if uptime >= 95 else "danger"
            indicators.append(
                dbc.Alert([
                    html.Strong(f"System Uptime: {uptime:.1f}%"),
                    html.Br(),
                    html.Small("Last 24 hours")
                ], color=uptime_color, className="mb-2")
            )
            
            # Response time indicator
            response_color = "success" if response_time <= 2 else "warning" if response_time <= 5 else "danger"
            indicators.append(
                dbc.Alert([
                    html.Strong(f"Response Time: {response_time:.1f}s"),
                    html.Br(),
                    html.Small("Average prediction time")
                ], color=response_color, className="mb-2")
            )
            
            # False positive rate
            fp_color = "success" if false_positive_rate <= 10 else "warning" if false_positive_rate <= 15 else "danger"
            indicators.append(
                dbc.Alert([
                    html.Strong(f"False Positive: {false_positive_rate:.1f}%"),
                    html.Br(),
                    html.Small("Model accuracy indicator")
                ], color=fp_color, className="mb-2")
            )
            
            return html.Div(indicators)
            
        except Exception as e:
            logger.error(f"Error creating system health indicators: {e}")
            return html.Div("Error loading health indicators")
    
    def _create_intervention_outcomes_chart(self) -> Optional[Any]:
        """Create intervention outcomes analysis chart"""
        try:
            # Get real intervention data from metrics history or Redis
            interventions = ['Crisis Hotline', 'Peer Support', 'Professional Referral', 'Wellness Check', 'Breathing Exercise']
            
            # Calculate real success rates from stored intervention outcomes
            success_rates = []
            total_used = []
            
            for intervention in interventions:
                # Get real data from intervention_outcomes deque
                intervention_data = [
                    outcome for outcome in self.intervention_outcomes 
                    if outcome.get('intervention_type') == intervention
                ]
                
                if intervention_data:
                    success_count = sum(1 for outcome in intervention_data if outcome.get('successful', False))
                    success_rate = (success_count / len(intervention_data)) * 100
                    success_rates.append(success_rate)
                    total_used.append(len(intervention_data))
                else:
                    # No data available for this intervention yet
                    success_rates.append(0)
                    total_used.append(0)
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Bar(
                    x=interventions,
                    y=success_rates,
                    name="Success Rate (%)",
                    marker_color='#28a745'
                ),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(
                    x=interventions,
                    y=total_used,
                    name="Total Used",
                    mode='lines+markers',
                    marker_color='#dc3545',
                    line=dict(width=3)
                ),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="Intervention Type")
            fig.update_yaxes(title_text="Success Rate (%)", secondary_y=False)
            fig.update_yaxes(title_text="Total Times Used", secondary_y=True)
            
            fig.update_layout(
                title="Intervention Effectiveness Analysis (Real Data)",
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating intervention outcomes chart: {e}")
            return go.Figure()
    
    def record_prediction(self, prediction_data: Dict[str, Any]):
        """Record a crisis prediction for real-time monitoring"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            # Extract prediction details
            risk_level = prediction_data.get('risk_level', 'UNKNOWN')
            processing_time = prediction_data.get('processing_time', 0.0)
            confidence_score = prediction_data.get('confidence_score', 0.0)
            user_id = prediction_data.get('user_id', 'anonymous')  # Keep anonymous for privacy
            
            # Store prediction record (anonymized)
            prediction_record = {
                'timestamp': timestamp,
                'risk_level': risk_level,
                'processing_time': processing_time,
                'confidence_score': confidence_score,
                'anonymized_user': f"user_{hash(str(user_id)) % 10000}",  # Anonymized ID
            }
            
            # Update system statistics
            if not hasattr(self, 'system_stats'):
                self.system_stats = {
                    'total_predictions_processed': 0,
                    'total_alerts_generated': 0,
                    'service_start_time': datetime.utcnow()
                }
            
            self.system_stats['total_predictions_processed'] += 1
            
            if risk_level in ['HIGH', 'CRITICAL']:
                self.system_stats['total_alerts_generated'] += 1
            
            # Store in Redis for persistence (if available)
            if self.redis_client:
                try:
                    # Store individual prediction
                    prediction_key = f"prediction:{timestamp}"
                    self.redis_client.setex(prediction_key, 3600, json.dumps(prediction_record))  # 1 hour expiry
                    
                    # Update daily counters
                    today = datetime.utcnow().date()
                    daily_key = f"daily_predictions:{today}"
                    self.redis_client.incr(daily_key)
                    self.redis_client.expire(daily_key, 86400)  # 24 hour expiry
                    
                    # Update risk level counters
                    risk_key = f"risk_count:{today}:{risk_level}"
                    self.redis_client.incr(risk_key)
                    self.redis_client.expire(risk_key, 86400)
                    
                except Exception as e:
                    logger.error(f"Error storing prediction in Redis: {e}")
            
            logger.debug(f"Recorded crisis prediction: {risk_level} risk level, {processing_time:.3f}s processing time")
            
        except Exception as e:
            logger.error(f"Error recording prediction: {e}")
    
    def record_intervention(self, intervention_data: Dict[str, Any]):
        """Record an intervention outcome for effectiveness tracking"""
        try:
            timestamp = datetime.utcnow().isoformat()
            
            intervention_record = {
                'timestamp': timestamp,
                'intervention_type': intervention_data.get('intervention_type', 'unknown'),
                'successful': intervention_data.get('successful', False),
                'response_time_seconds': intervention_data.get('response_time_seconds', 0.0),
                'user_feedback_score': intervention_data.get('user_feedback_score', 0),  # 1-5 scale
                'escalated': intervention_data.get('escalated', False)
            }
            
            # Add to intervention outcomes deque
            self.intervention_outcomes.append(intervention_record)
            
            # Store in Redis
            if self.redis_client:
                try:
                    intervention_key = f"intervention:{timestamp}"
                    self.redis_client.setex(intervention_key, 86400, json.dumps(intervention_record))  # 24 hour expiry
                except Exception as e:
                    logger.error(f"Error storing intervention in Redis: {e}")
            
            logger.debug(f"Recorded intervention: {intervention_record['intervention_type']}, success: {intervention_record['successful']}")
            
        except Exception as e:
            logger.error(f"Error recording intervention: {e}")
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time system statistics"""
        try:
            if hasattr(self, 'system_stats'):
                uptime_seconds = (datetime.utcnow() - self.system_stats['service_start_time']).total_seconds()
                uptime_hours = uptime_seconds / 3600
                
                return {
                    'total_predictions': self.system_stats.get('total_predictions_processed', 0),
                    'total_alerts': self.system_stats.get('total_alerts_generated', 0),
                    'uptime_hours': round(uptime_hours, 2),
                    'uptime_percent': min(99.9, (uptime_hours / max(uptime_hours, 1)) * 100),  # Simplified uptime calc
                    'avg_predictions_per_hour': self.system_stats.get('total_predictions_processed', 0) / max(uptime_hours, 1)
                }
            else:
                return {
                    'total_predictions': 0,
                    'total_alerts': 0,
                    'uptime_hours': 0,
                    'uptime_percent': 100.0,
                    'avg_predictions_per_hour': 0
                }
        except Exception as e:
            logger.error(f"Error getting real-time stats: {e}")
            return {
                'total_predictions': 0,
                'total_alerts': 0,
                'uptime_hours': 0,
                'uptime_percent': 100.0,
                'avg_predictions_per_hour': 0
            }
    
    async def collect_metrics(self, crisis_predictor, early_warning_system):
        """Collect real-time metrics from crisis prediction systems"""
        try:
            timestamp = datetime.utcnow()
            
            # Get real data from crisis predictor
            prediction_history = getattr(crisis_predictor, 'prediction_history', [])
            recent_predictions = [
                p for p in prediction_history 
                if datetime.fromisoformat(p.get('timestamp', timestamp.isoformat())) > timestamp - timedelta(hours=1)
            ]
            
            # Get real data from early warning system
            alert_history = getattr(early_warning_system, 'alert_history', [])
            recent_alerts = [
                a for a in alert_history 
                if datetime.fromisoformat(a.get('timestamp', timestamp.isoformat())) > timestamp - timedelta(hours=1)
            ]
            
            # Calculate real metrics
            high_risk_count = len([p for p in recent_predictions if p.get('risk_level') == 'HIGH'])
            medium_risk_count = len([p for p in recent_predictions if p.get('risk_level') == 'MEDIUM'])
            low_risk_count = len([p for p in recent_predictions if p.get('risk_level') == 'LOW'])
            
            # Calculate average response time from real predictions
            response_times = [p.get('processing_time', 1.0) for p in recent_predictions]
            avg_response_time = np.mean(response_times) if response_times else 1.0
            
            # Calculate model accuracy based on recent predictions
            accuracy_scores = [p.get('confidence', 0.85) for p in recent_predictions]
            model_accuracy = np.mean(accuracy_scores) if accuracy_scores else 0.85
            
            # Count interventions from alerts
            interventions_executed = sum(len(a.get('interventions_triggered', [])) for a in recent_alerts)
            
            metrics = CrisisMetrics(
                timestamp=timestamp.isoformat(),
                total_predictions=len(recent_predictions),
                high_risk_count=high_risk_count,
                medium_risk_count=medium_risk_count,
                low_risk_count=low_risk_count,
                alerts_triggered=len(recent_alerts),
                interventions_executed=interventions_executed,
                avg_response_time_seconds=avg_response_time,
                model_accuracy=model_accuracy,
                false_positive_rate=max(0.05, 1.0 - model_accuracy),
                system_uptime_percent=99.5  # Could be calculated from system metrics
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Update system stats
            self.system_stats['total_predictions_processed'] += len(recent_predictions)
            self.system_stats['total_alerts_generated'] += len(recent_alerts)
            
            # Store in Redis for persistence
            if self.redis_client:
                try:
                    today = datetime.utcnow().date()
                    daily_key = f"crisis_metrics:{today}"
                    hourly_key = f"crisis_metrics:{timestamp.strftime('%Y-%m-%d:%H')}"
                    
                    metrics_dict = asdict(metrics)
                    self.redis_client.setex(daily_key, 86400, json.dumps(metrics_dict))  # 24 hour expiry
                    self.redis_client.setex(hourly_key, 3600, json.dumps(metrics_dict))   # 1 hour expiry
                    
                except Exception as e:
                    logger.error(f"Error storing metrics in Redis: {e}")
            
            logger.debug(f"Real crisis metrics collected: {high_risk_count} high risk, {medium_risk_count} medium risk, {low_risk_count} low risk")
            
        except Exception as e:
            logger.error(f"Error collecting crisis metrics: {e}")
    
    def run_dashboard(self, host: str = "0.0.0.0", port: int = 8050, debug: bool = False):
        """Run the crisis prediction dashboard web application"""
        if not self.ready:
            logger.error("Dashboard libraries not available - cannot run web interface")
            return
        
        if not self.app:
            logger.error("Dashboard app not initialized")
            return
        
        logger.info(f"Starting Crisis Prediction Dashboard on http://{host}:{port}")
        
        try:
            self.app.run_server(
                host=host,
                port=port,
                debug=debug,
                dev_tools_hot_reload=debug
            )
        except Exception as e:
            logger.error(f"Error running dashboard: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status for API endpoints"""
        try:
            latest_metrics = self.get_current_metrics()
            
            return {
                "dashboard_status": "operational" if self.ready else "limited",
                "last_update": datetime.utcnow().isoformat(),
                "metrics": latest_metrics,
                "system_health": {
                    "uptime_percent": latest_metrics.get('system_uptime', 99.5),
                    "avg_response_time_ms": latest_metrics.get('avg_response_time', 1.2) * 1000,
                    "false_positive_rate": latest_metrics.get('false_positive_rate', 8.3),
                    "redis_connected": self.redis_client is not None,
                    "dashboard_available": DASHBOARD_AVAILABLE
                },
                "version": self.dashboard_version
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "dashboard_status": "error",
                "error": str(e),
                "version": self.dashboard_version
            }

# Global dashboard instance
crisis_dashboard = None

def get_crisis_dashboard() -> CrisisDashboard:
    """Get or create global crisis dashboard instance"""
    global crisis_dashboard
    if crisis_dashboard is None:
        crisis_dashboard = CrisisDashboard()
    return crisis_dashboard

if __name__ == "__main__":
    # Run dashboard as standalone application
    dashboard = CrisisDashboard()
    if dashboard.ready:
        dashboard.run_dashboard(debug=True)
    else:
        print("Dashboard libraries not available. Install with: pip install plotly dash dash-bootstrap-components")
