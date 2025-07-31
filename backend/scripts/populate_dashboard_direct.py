#!/usr/bin/env python3
"""
Dashboard Data Populator - Direct Method
Directly populates the dashboard with sample data without going through the API
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

# Add the ML service path
sys.path.append('/Users/sachin/mantrapath-holistic/backend/services/ml_service')

from monitoring.api_crisis_dashboard import get_crisis_dashboard

async def populate_dashboard_data():
    """Populate the dashboard with sample realistic data"""
    print("🚀 Populating Crisis Dashboard with sample data...")
    
    dashboard = get_crisis_dashboard()
    
    # Generate sample predictions over the last 24 hours
    now = datetime.utcnow()
    
    # Sample data for the last 24 hours
    for hour in range(24):
        timestamp = now - timedelta(hours=23-hour)
        
        # Generate realistic predictions for this hour
        predictions_this_hour = max(1, int(15 + hour * 0.5 + (hour % 7) * 2))  # Vary by hour
        
        for i in range(predictions_this_hour):
            # Determine risk level based on time and patterns
            if hour < 6 or hour > 22:  # Late night/early morning higher risk
                risk_weights = [0.15, 0.25, 0.40, 0.20]  # [HIGH, MEDIUM, LOW, MINIMAL]
            elif hour < 12:  # Morning
                risk_weights = [0.05, 0.15, 0.50, 0.30]
            else:  # Afternoon/evening
                risk_weights = [0.08, 0.20, 0.45, 0.27]
            
            import random
            risk_level = random.choices(['HIGH', 'MEDIUM', 'LOW', 'MINIMAL'], weights=risk_weights)[0]
            
            # Record the prediction
            dashboard.record_prediction({
                'user_id': f'user_{random.randint(1000, 9999)}',
                'risk_level': risk_level,
                'confidence_score': random.uniform(0.6, 0.95),
                'processing_time': random.uniform(0.5, 2.5),
                'timestamp': timestamp.isoformat()
            })
    
    # Generate sample interventions
    for i in range(50):
        intervention_types = ['Crisis Hotline', 'Peer Support', 'Professional Referral', 'Wellness Check', 'Breathing Exercise']
        intervention_type = random.choice(intervention_types)
        
        # Success rates vary by intervention type
        success_rates = {
            'Crisis Hotline': 0.92,
            'Peer Support': 0.78,
            'Professional Referral': 0.95,
            'Wellness Check': 0.86,
            'Breathing Exercise': 0.71
        }
        
        successful = random.random() < success_rates[intervention_type]
        
        dashboard.record_intervention({
            'intervention_type': intervention_type,
            'successful': successful,
            'response_time_seconds': random.uniform(30, 300),
            'user_feedback_score': random.randint(1, 5) if successful else random.randint(1, 3),
            'escalated': not successful and random.random() < 0.3
        })
    
    print("✅ Dashboard populated with sample data")
    
    # Show current metrics
    metrics = dashboard.get_current_metrics()
    print(f"📊 Current Metrics:")
    print(f"   Total Predictions: {metrics['total_predictions']}")
    print(f"   High Risk Alerts: {metrics['high_risk_alerts']}")
    print(f"   Medium Risk Alerts: {metrics['medium_risk_alerts']}")
    print(f"   Low Risk Alerts: {metrics['low_risk_alerts']}")
    print(f"   Intervention Success Rate: {metrics['intervention_success_rate']:.1f}%")
    
    # Show system status
    status = dashboard.get_system_status()
    print(f"🏥 System Status: {status['dashboard_status']}")

if __name__ == "__main__":
    asyncio.run(populate_dashboard_data())
