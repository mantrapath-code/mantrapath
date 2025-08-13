"""
E3 Achievement Database Migration Script
Creates the achievement tables and sets up the unified achievement system
"""

import sqlite3
import os
from datetime import datetime

def create_achievement_tables(db_path: str):
    """Create achievement-related tables for E3 implementation"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create celebration_moments table (if it doesn't exist)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS celebration_moments (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                celebration_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                achievement_level TEXT DEFAULT 'bronze',
                reward_type TEXT,
                reward_data TEXT,
                is_shown BOOLEAN DEFAULT FALSE,
                shown_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # 2. Create user_achievement_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievement_progress (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                current_progress INTEGER DEFAULT 0,
                max_progress INTEGER NOT NULL,
                is_unlocked BOOLEAN DEFAULT FALSE,
                unlocked_at TIMESTAMP,
                achievement_title TEXT NOT NULL,
                achievement_description TEXT,
                achievement_category TEXT NOT NULL,
                achievement_level TEXT DEFAULT 'bronze',
                achievement_icon TEXT DEFAULT '🎯',
                progress_metadata TEXT,
                last_progress_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                celebration_triggered BOOLEAN DEFAULT FALSE,
                celebration_moment_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (celebration_moment_id) REFERENCES celebration_moments (id)
            )
        """)
        
        # 3. Create achievement_definition_cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS achievement_definition_cache (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                level TEXT DEFAULT 'bronze',
                max_progress INTEGER DEFAULT 1,
                icon TEXT DEFAULT '🎯',
                criteria_function TEXT,
                celebration_type TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. Create user_achievement_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievement_events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                achievement_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                trigger_source TEXT,
                progress_before INTEGER DEFAULT 0,
                progress_after INTEGER DEFAULT 0,
                was_unlocked_before BOOLEAN DEFAULT FALSE,
                was_unlocked_after BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # 5. Create indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_achievement_lookup ON user_achievement_progress(user_id, achievement_id)",
            "CREATE INDEX IF NOT EXISTS idx_achievement_category ON user_achievement_progress(achievement_category, achievement_level)",
            "CREATE INDEX IF NOT EXISTS idx_user_unlocked ON user_achievement_progress(user_id, is_unlocked, unlocked_at)",
            "CREATE INDEX IF NOT EXISTS idx_progress_updates ON user_achievement_progress(user_id, last_progress_update)",
            "CREATE INDEX IF NOT EXISTS idx_achievement_category_level ON achievement_definition_cache(category, level)",
            "CREATE INDEX IF NOT EXISTS idx_active_achievements ON achievement_definition_cache(is_active, category)",
            "CREATE INDEX IF NOT EXISTS idx_user_achievement_events ON user_achievement_events(user_id, achievement_id, event_type)",
            "CREATE INDEX IF NOT EXISTS idx_event_timeline ON user_achievement_events(user_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_trigger_analysis ON user_achievement_events(trigger_source, event_type)",
            "CREATE INDEX IF NOT EXISTS idx_celebration_user ON celebration_moments(user_id, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_celebration_shown ON celebration_moments(user_id, is_shown)"
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        conn.commit()
        print("✅ Achievement tables created successfully")
        
        # 6. Populate achievement definition cache
        populate_achievement_definitions(cursor)
        conn.commit()
        print("✅ Achievement definitions cached")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating achievement tables: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def populate_achievement_definitions(cursor):
    """Populate the achievement definition cache with default achievements"""
    
    achievements = [
        # Mood tracking achievements
        ("first_steps", "First Steps", "Log your first mood entry", "getting-started", "bronze", 1, "🎯", "check_first_mood_entry", None),
        ("week_warrior", "Week Warrior", "Log moods for 7 consecutive days", "consistency", "silver", 7, "🔥", "check_mood_streak", None),
        ("mood_master", "Mood Master", "Reach 30 total mood entries", "milestone", "gold", 30, "👑", "check_mood_milestone", None),
        ("positive_vibes", "Positive Vibes", "Log 5 excellent moods in a row", "streak", "silver", 5, "✨", "check_positive_streak", None),
        
        # Improvement achievements
        ("improvement_streak_3", "3-Day Improvement Streak! 🌟", "Amazing! You've had 3 days of improving mood.", "improvement_streaks", "bronze", 3, "🌟", "check_improvement_streak", "improvement_streak"),
        ("improvement_streak_7", "Week-Long Improvement Streak! ✨", "Incredible! A full week of mood improvement.", "improvement_streaks", "silver", 7, "✨", "check_improvement_streak", "improvement_streak"),
        
        # Consistency achievements  
        ("consistency_streak_3", "3-Day Tracking Streak! 📊", "Great start! You're building a healthy habit.", "consistency_milestones", "bronze", 3, "📊", "check_consistency_streak", "consistency"),
        ("consistency_streak_30", "Monthly Master! 👑", "30 days of consistent tracking!", "consistency_milestones", "gold", 30, "👑", "check_consistency_streak", "consistency"),
        
        # Meta achievements
        ("bronze_collector", "Bronze Achiever", "Earn 3 bronze level achievements", "celebration", "bronze", 3, "🥉", "check_celebration_collection", None),
        ("silver_collector", "Silver Achiever", "Earn 3 silver level achievements", "celebration", "silver", 3, "🥈", "check_celebration_collection", None),
        ("gold_collector", "Gold Achiever", "Earn 3 gold level achievements", "celebration", "gold", 3, "🥇", "check_celebration_collection", None),
    ]
    
    for achievement in achievements:
        cursor.execute("""
            INSERT OR REPLACE INTO achievement_definition_cache 
            (id, title, description, category, level, max_progress, icon, criteria_function, celebration_type, is_active, last_updated, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, achievement)

def run_migration():
    """Run the E3 achievement migration"""
    
    print("🚀 Starting E3 Achievement & Engagement Cohesion Migration")
    print("=" * 60)
    
    # Get database path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    db_path = os.path.join(backend_dir, "mantrapath.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"📁 Database: {db_path}")
    
    # Create tables
    success = create_achievement_tables(db_path)
    
    if success:
        print("=" * 60)
        print("✅ E3 Achievement & Engagement Cohesion Migration Complete!")
        print("")
        print("🎯 New Features Available:")
        print("  • Unified achievement engine")
        print("  • Server-side achievement calculations") 
        print("  • Achievement progress tracking")
        print("  • Celebration system integration")
        print("  • Analytics and event logging")
        print("")
        print("📍 Next Steps:")
        print("  1. Start backend server")
        print("  2. Test /api/v1/achievements endpoint")
        print("  3. Verify frontend integration")
        
    return success

if __name__ == "__main__":
    run_migration()
