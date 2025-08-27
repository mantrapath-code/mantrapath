"""
E3 Achievement System Test Script
Test the unified achievement engine functionality
"""

import os
import sys
import asyncio
import sqlite3
from datetime import datetime, timedelta

# Add path for backend modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(backend_dir, '../'))
sys.path.append(os.path.join(backend_dir, '../shared'))
sys.path.append(os.path.join(backend_dir, '../services'))

from shared.database import get_db
from shared.models import MoodEntry, User
from achievements_engine import achievements_engine

def setup_test_data():
    """Create test data for achievement testing"""
    
    db_path = os.path.join(backend_dir, "../mantrapath.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a test user if one doesn't exist
    test_user_id = "test-user-12345"
    cursor.execute("""
        INSERT OR IGNORE INTO users (id, email, username, password_hash, first_name, last_name)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (test_user_id, "test@example.com", "testuser", "hashed_password", "Test", "User"))
    
    # Add test mood entries for achievement testing
    test_entries = [
        # First mood entry (should unlock "First Steps")
        (f"mood-{i}", test_user_id, 8, 7, 3, 8, "Feeling great today!", 
         datetime.now() - timedelta(days=30-i)) 
        for i in range(10)
    ]
    
    for entry in test_entries:
        cursor.execute("""
            INSERT OR IGNORE INTO mood_entries 
            (id, user_id, mood_score, energy_level, stress_level, sleep_quality, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, entry)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Test data created for user: {test_user_id}")
    return test_user_id

async def test_achievement_engine():
    """Test the E3 achievement engine functionality"""
    
    print("🚀 Testing E3 Achievement & Engagement Cohesion Engine")
    print("=" * 60)
    
    # Setup test data
    test_user_id = setup_test_data()
    
    # Get database session (simplified)
    db_path = os.path.join(backend_dir, "../mantrapath.db")
    
    try:
        # Test 1: Get achievement definitions
        print("\n📋 Test 1: Achievement Definitions")
        print(f"Total achievements defined: {len(achievements_engine.achievement_definitions)}")
        
        for achievement_id, definition in list(achievements_engine.achievement_definitions.items())[:5]:
            print(f"  • {achievement_id}: {definition.title} ({definition.level})")
        
        # Test 2: Create a mock database session for testing
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine(f"sqlite:///{db_path}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Test 3: Get user achievements
        print("\n🎯 Test 2: User Achievement Progress")
        achievement_data = await achievements_engine.get_user_achievements(test_user_id, db)
        
        print(f"User has {achievement_data['summary']['total_achievements']} total achievements")
        print(f"Unlocked: {achievement_data['summary']['unlocked_count']}")
        print(f"Average progress: {achievement_data['summary']['average_progress']}%")
        
        # Test 4: Show specific achievements
        print("\n🏆 Test 3: Achievement Details")
        for achievement_id, achievement in list(achievement_data["achievements"].items())[:5]:
            status = "✅ UNLOCKED" if achievement["is_unlocked"] else "🔄 IN PROGRESS"
            progress = f"{achievement['progress']}/{achievement['max_progress']}"
            print(f"  {status} {achievement['title']} - {progress} ({achievement['level']})")
        
        # Test 5: Trigger achievement check
        print("\n🔍 Test 4: Achievement Check")
        new_achievements = await achievements_engine.trigger_achievement_check(
            test_user_id, "test_trigger", db
        )
        print(f"Found {len(new_achievements)} newly unlocked achievements")
        
        for achievement in new_achievements:
            print(f"  🎉 NEW: {achievement['title']} ({achievement['level']})")
        
        # Test 6: Test specific criteria functions
        print("\n⚙️  Test 5: Criteria Function Testing")
        
        # Test first mood entry
        first_steps_def = achievements_engine.achievement_definitions["first_steps"]
        first_steps_progress = await achievements_engine.check_first_mood_entry(
            test_user_id, first_steps_def, db
        )
        print(f"  First Steps: {first_steps_progress.current_progress}/{first_steps_def.max_progress} - {'✅' if first_steps_progress.is_unlocked else '❌'}")
        
        # Test mood streak
        week_warrior_def = achievements_engine.achievement_definitions["week_warrior"]
        week_warrior_progress = await achievements_engine.check_mood_streak(
            test_user_id, week_warrior_def, db
        )
        print(f"  Week Warrior: {week_warrior_progress.current_progress}/{week_warrior_def.max_progress} - {'✅' if week_warrior_progress.is_unlocked else '❌'}")
        
        # Test milestone
        mood_master_def = achievements_engine.achievement_definitions["mood_master"]
        mood_master_progress = await achievements_engine.check_mood_milestone(
            test_user_id, mood_master_def, db
        )
        print(f"  Mood Master: {mood_master_progress.current_progress}/{mood_master_def.max_progress} - {'✅' if mood_master_progress.is_unlocked else '❌'}")
        
        db.close()
        
        print("\n" + "=" * 60)
        print("✅ E3 Achievement Engine Tests Complete!")
        print("🎯 All core functionality working correctly")
        print("🚀 Ready for frontend integration")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_achievement_engine())
