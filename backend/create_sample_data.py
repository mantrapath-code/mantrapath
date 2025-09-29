#!/usr/bin/env python3
"""
Script to create sample mood entries for testing analytics
"""
import sys
import os
import json
import requests
from datetime import datetime, timedelta
import random

# Add the backend path to sys.path
sys.path.append('/home/sachin/mantrapath/backend')

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        "http://localhost:8000/auth/login",
        headers={"Content-Type": "application/json"},
        json={"email_or_username": "sa@gmail.com", "password": "Dev@#123"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to authenticate: {response.status_code}")
        print(response.text)
        return None

def create_mood_entry(token, mood_data):
    """Create a mood entry"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/mood/entries",
        headers=headers,
        json=mood_data
    )
    
    return response.status_code == 200

def generate_sample_entries():
    """Generate diverse mood entries over the past few weeks"""
    entries = []
    base_date = datetime.now()
    
    # Create entries for the past 4 weeks with realistic patterns
    for weeks_ago in range(4):
        for day in range(7):
            # Skip some days to make it realistic
            if random.random() < 0.3:
                continue
                
            entry_date = base_date - timedelta(weeks=weeks_ago, days=day)
            
            # Create mood patterns (weekends generally better, mid-week stress)
            if day in [5, 6]:  # Weekend
                mood_base = random.randint(6, 9)
                stress_base = random.randint(2, 5)
                energy_base = random.randint(6, 8)
            elif day in [1, 2]:  # Monday/Tuesday (harder days)
                mood_base = random.randint(4, 7)
                stress_base = random.randint(5, 8)
                energy_base = random.randint(3, 6)
            else:  # Mid-week
                mood_base = random.randint(5, 8)
                stress_base = random.randint(4, 7)
                energy_base = random.randint(4, 7)
            
            # Add some randomness but keep it realistic
            mood_score = max(1, min(10, mood_base + random.randint(-1, 1)))
            stress_level = max(1, min(10, stress_base + random.randint(-1, 1)))
            energy_level = max(1, min(10, energy_base + random.randint(-1, 1)))
            
            # Create realistic descriptions and emotions based on mood
            descriptions = {
                "low": [
                    "Feeling quite down today, struggling with motivation",
                    "Had a difficult day, feeling overwhelmed",
                    "Not my best day, feeling a bit anxious"
                ],
                "medium": [
                    "Feeling okay today, some ups and downs",
                    "Average day, managing well enough",
                    "Doing alright, staying positive"
                ],
                "high": [
                    "Great day! Feeling really positive and energetic",
                    "Excellent mood today, accomplished a lot",
                    "Feeling fantastic and grateful for everything"
                ]
            }
            
            emotions = {
                "low": {"sadness": 0.7, "anxiety": 0.6, "frustration": 0.5},
                "medium": {"neutral": 0.6, "hope": 0.4, "contentment": 0.3},
                "high": {"joy": 0.8, "gratitude": 0.7, "excitement": 0.6}
            }
            
            if mood_score <= 4:
                category = "low"
            elif mood_score <= 7:
                category = "medium"
            else:
                category = "high"
            
            entry = {
                "mood_score": mood_score,
                "stress_level": stress_level,
                "energy_level": energy_level,
                "description": random.choice(descriptions[category]),
                "context_tags": ["daily_check"] if day < 5 else ["weekend"],
                "location": "home" if random.random() > 0.3 else "work",
                "activity": random.choice(["work", "exercise", "relaxing", "socializing", "studying"])
            }
            
            # Add emotion analysis in the format expected by analytics
            entry_with_timestamp = {
                **entry,
                "timestamp": entry_date.isoformat(),
                "emotion_analysis": json.dumps({
                    "top_emotions": [
                        {"emotion": emotion, "confidence": confidence}
                        for emotion, confidence in emotions[category].items()
                    ],
                    "primary_emotion": list(emotions[category].keys())[0],
                    "primary_sentiment": "positive" if category == "high" else "negative" if category == "low" else "neutral"
                })
            }
            
            entries.append(entry_with_timestamp)
    
    return entries

def main():
    print("🎭 Creating sample mood entries for analytics testing...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return
    
    print("✅ Authentication successful")
    
    # Generate sample entries
    entries = generate_sample_entries()
    print(f"📊 Generated {len(entries)} sample mood entries")
    
    # Create entries
    success_count = 0
    for i, entry in enumerate(entries):
        # Remove timestamp as the API will set it
        api_entry = {k: v for k, v in entry.items() if k != 'timestamp'}
        
        if create_mood_entry(token, api_entry):
            success_count += 1
            if i % 5 == 0:
                print(f"  Created {i+1}/{len(entries)} entries...")
        else:
            print(f"❌ Failed to create entry {i+1}")
    
    print(f"✅ Successfully created {success_count}/{len(entries)} mood entries")
    print("🎉 Sample data creation complete!")
    
    # Test analytics
    print("\n📈 Testing analytics endpoints...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test overview
    response = requests.get("http://localhost:8000/api/v1/analytics/overview", headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ Analytics Overview:")
        print(f"  Total entries: {data.get('total_entries', 0)}")
        print(f"  Average mood: {data.get('average_mood', 0)}")
        print(f"  Mood trend: {data.get('mood_trend', 'unknown')}")
        print(f"  Improvement trend: {data.get('improvement_trend', 0)}")
    else:
        print(f"❌ Analytics failed: {response.status_code}")

if __name__ == "__main__":
    main()