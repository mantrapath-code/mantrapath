#!/usr/bin/env python3
"""
Test script to verify analytics data calculations
"""
import sys
import os

# Add paths
sys.path.append('/home/sachin/mantrapath/backend')

from shared.database import get_db, SessionLocal
from shared.models import MoodEntry
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def test_analytics_data():
    """Test analytics calculations directly from database"""
    print("🔍 Testing analytics data calculations...")
    
    # Get database session
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Query all mood entries
        mood_entries = db.query(MoodEntry).all()
        
        print(f"📊 Total mood entries in database: {len(mood_entries)}")
        
        if not mood_entries:
            print("❌ No mood entries found!")
            return
        
        # Group by user
        users = {}
        for entry in mood_entries:
            if entry.user_id not in users:
                users[entry.user_id] = []
            users[entry.user_id].append(entry)
        
        print(f"👥 Found {len(users)} users with mood data")
        
        for user_id, user_entries in users.items():
            print(f"\n👤 User: {user_id}")
            print(f"   Entries: {len(user_entries)}")
            
            # Calculate basic stats
            mood_scores = [e.mood_score for e in user_entries if e.mood_score is not None]
            stress_levels = [e.stress_level for e in user_entries if e.stress_level is not None]
            energy_levels = [e.energy_level for e in user_entries if e.energy_level is not None]
            
            if mood_scores:
                avg_mood = sum(mood_scores) / len(mood_scores)
                print(f"   Average mood: {avg_mood:.2f}")
                
                # Test improvement trend
                if len(mood_scores) >= 4:
                    sorted_entries = sorted(user_entries, key=lambda x: x.created_at)
                    sorted_scores = [e.mood_score for e in sorted_entries if e.mood_score is not None]
                    
                    mid_point = len(sorted_scores) // 2
                    first_half = sorted_scores[:mid_point]
                    second_half = sorted_scores[mid_point:]
                    
                    first_avg = sum(first_half) / len(first_half)
                    second_avg = sum(second_half) / len(second_half)
                    improvement = ((second_avg - first_avg) / first_avg) * 100 if first_avg != 0 else 0
                    
                    print(f"   Improvement trend: {improvement:.1f}%")
                    print(f"     First half avg: {first_avg:.2f}")
                    print(f"     Second half avg: {second_avg:.2f}")
                else:
                    print("   Not enough entries for improvement trend")
            
            if stress_levels:
                avg_stress = sum(stress_levels) / len(stress_levels)
                print(f"   Average stress: {avg_stress:.2f}")
                
            if energy_levels:
                avg_energy = sum(energy_levels) / len(energy_levels)
                print(f"   Average energy: {avg_energy:.2f}")
                
            # Check emotion analysis data
            emotion_entries = [e for e in user_entries if e.emotion_analysis]
            print(f"   Entries with emotion analysis: {len(emotion_entries)}")
            
            if emotion_entries:
                print("   Sample emotion analysis:")
                for i, entry in enumerate(emotion_entries[:3]):  # Show first 3
                    print(f"     {i+1}. {entry.emotion_analysis}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_analytics_data()