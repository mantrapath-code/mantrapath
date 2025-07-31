#!/usr/bin/env python3
"""
Crisis Dashboard Data Generator
Generates realistic crisis predictions to populate the dashboard with real data
"""

import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test user data for generating realistic predictions
SAMPLE_USER_DATA = [
    {
        "user_id": "test_user_1",
        "mood_entries": [
            {"timestamp": "2025-07-31T06:00:00", "mood_score": 3, "notes": "Feeling a bit down today"},
            {"timestamp": "2025-07-31T05:30:00", "mood_score": 2, "notes": "Stressed about work"},
            {"timestamp": "2025-07-31T05:00:00", "mood_score": 4, "notes": "Morning was okay"}
        ],
        "journal_entries": [
            {"timestamp": "2025-07-31T06:15:00", "content": "Having trouble sleeping. Work stress is getting to me."},
            {"timestamp": "2025-07-31T05:45:00", "content": "Feeling overwhelmed with everything going on."}
        ],
        "activity_data": {"steps": 1200, "sleep_hours": 4.5, "heart_rate": 85},
        "sleep_data": {"quality": 2, "duration": 4.5, "interruptions": 3},
        "demographic_info": {"age": 28, "location": "urban", "support_network": "limited"}
    },
    {
        "user_id": "test_user_2",
        "mood_entries": [
            {"timestamp": "2025-07-31T06:30:00", "mood_score": 6, "notes": "Feeling better today"},
            {"timestamp": "2025-07-31T06:00:00", "mood_score": 7, "notes": "Good morning!"},
            {"timestamp": "2025-07-31T05:30:00", "mood_score": 5, "notes": "Neutral mood"}
        ],
        "journal_entries": [
            {"timestamp": "2025-07-31T06:20:00", "content": "Had a good workout this morning. Feeling energized."}
        ],
        "activity_data": {"steps": 8500, "sleep_hours": 7.5, "heart_rate": 72},
        "sleep_data": {"quality": 8, "duration": 7.5, "interruptions": 1},
        "demographic_info": {"age": 32, "location": "suburban", "support_network": "strong"}
    },
    {
        "user_id": "test_user_3",
        "mood_entries": [
            {"timestamp": "2025-07-31T06:45:00", "mood_score": 1, "notes": "Really struggling today"},
            {"timestamp": "2025-07-31T06:15:00", "mood_score": 2, "notes": "Can't seem to shake this feeling"},
            {"timestamp": "2025-07-31T05:45:00", "mood_score": 1, "notes": "Everything feels hopeless"}
        ],
        "journal_entries": [
            {"timestamp": "2025-07-31T06:30:00", "content": "I don't know how much longer I can keep this up. Everything feels pointless."},
            {"timestamp": "2025-07-31T06:00:00", "content": "Another sleepless night. The thoughts won't stop."}
        ],
        "activity_data": {"steps": 300, "sleep_hours": 2.0, "heart_rate": 95},
        "sleep_data": {"quality": 1, "duration": 2.0, "interruptions": 8},
        "demographic_info": {"age": 24, "location": "urban", "support_network": "very_limited"}
    },
    {
        "user_id": "test_user_4",
        "mood_entries": [
            {"timestamp": "2025-07-31T06:50:00", "mood_score": 8, "notes": "Great day ahead!"},
            {"timestamp": "2025-07-31T06:20:00", "mood_score": 9, "notes": "Feeling fantastic"},
            {"timestamp": "2025-07-31T05:50:00", "mood_score": 7, "notes": "Positive vibes"}
        ],
        "journal_entries": [
            {"timestamp": "2025-07-31T06:40:00", "content": "Excited about the new project at work. Life is good!"}
        ],
        "activity_data": {"steps": 12000, "sleep_hours": 8.0, "heart_rate": 68},
        "sleep_data": {"quality": 9, "duration": 8.0, "interruptions": 0},
        "demographic_info": {"age": 29, "location": "suburban", "support_network": "excellent"}
    },
    {
        "user_id": "test_user_5",
        "mood_entries": [
            {"timestamp": "2025-07-31T06:55:00", "mood_score": 4, "notes": "Mixed feelings today"},
            {"timestamp": "2025-07-31T06:25:00", "mood_score": 3, "notes": "Anxious about presentation"},
            {"timestamp": "2025-07-31T05:55:00", "mood_score": 5, "notes": "Okay morning"}
        ],
        "journal_entries": [
            {"timestamp": "2025-07-31T06:45:00", "content": "Nervous about the big presentation today. Hope it goes well."}
        ],
        "activity_data": {"steps": 4500, "sleep_hours": 6.0, "heart_rate": 78},
        "sleep_data": {"quality": 5, "duration": 6.0, "interruptions": 2},
        "demographic_info": {"age": 35, "location": "urban", "support_network": "moderate"}
    }
]

async def make_crisis_prediction(session, user_data):
    """Make a crisis prediction for a user"""
    try:
        url = "http://localhost:8000/api/ml/crisis/predict-risk"
        
        async with session.post(url, json=user_data) as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"✅ Prediction for {user_data['user_id']}: {result.get('risk_level', 'UNKNOWN')} risk")
                return result
            else:
                response_text = await response.text()
                logger.error(f"❌ Prediction failed for {user_data['user_id']}: {response.status} - {response_text}")
                return None
                
    except Exception as e:
        logger.error(f"Error making prediction for {user_data['user_id']}: {e}")
        return None

async def check_dashboard_metrics(session):
    """Check the current dashboard metrics"""
    try:
        url = "http://localhost:8000/api/ml/dashboard/test"
        
        async with session.get(url) as response:
            if response.status == 200:
                result = await response.json()
                logger.info(f"📊 Dashboard test: {result}")
                return result
            else:
                logger.error(f"❌ Dashboard test failed: {response.status}")
                return None
                
    except Exception as e:
        logger.error(f"Error checking dashboard: {e}")
        return None

async def generate_dashboard_data():
    """Generate realistic data for the crisis dashboard"""
    logger.info("🚀 Starting Crisis Dashboard Data Generation")
    
    async with aiohttp.ClientSession() as session:
        # First, check if the dashboard is responding
        await check_dashboard_metrics(session)
        
        # Generate predictions for all sample users
        logger.info("📈 Generating crisis predictions...")
        
        predictions = []
        for user_data in SAMPLE_USER_DATA:
            result = await make_crisis_prediction(session, user_data)
            if result:
                predictions.append(result)
            
            # Small delay between predictions
            await asyncio.sleep(0.5)
        
        logger.info(f"✅ Generated {len(predictions)} predictions")
        
        # Generate additional varied predictions over time
        logger.info("🔄 Generating additional varied predictions...")
        
        for i in range(10):
            # Create varied mood patterns
            base_user = random.choice(SAMPLE_USER_DATA)
            varied_user = base_user.copy()
            varied_user["user_id"] = f"varied_user_{i}"
            
            # Vary the mood scores to create different risk levels
            mood_variance = random.uniform(-2, 2)
            for mood in varied_user["mood_entries"]:
                mood["mood_score"] = max(1, min(10, mood["mood_score"] + mood_variance))
            
            # Vary sleep and activity data
            varied_user["activity_data"]["steps"] = max(0, base_user["activity_data"]["steps"] + random.randint(-3000, 3000))
            varied_user["sleep_data"]["quality"] = max(1, min(10, base_user["sleep_data"]["quality"] + random.randint(-3, 3)))
            
            result = await make_crisis_prediction(session, varied_user)
            if result:
                predictions.append(result)
            
            await asyncio.sleep(0.3)
        
        logger.info(f"✅ Total predictions generated: {len(predictions)}")
        
        # Check dashboard again to see updated metrics
        await check_dashboard_metrics(session)

if __name__ == "__main__":
    asyncio.run(generate_dashboard_data())
