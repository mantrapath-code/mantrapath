#!/usr/bin/env python3
"""
E3 Achievement System Database Migration Script
Creates user_achievement_progress table for centralized achievement tracking
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from shared.database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Create user_achievement_progress table for E3 Achievement System"""
    
    engine = create_engine(DATABASE_URL)
    
    migrations = [
        # Create user_achievement_progress table
        """
        CREATE TABLE IF NOT EXISTS user_achievement_progress (
            id VARCHAR(36) PRIMARY KEY DEFAULT (gen_random_uuid()::text),
            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            achievement_key VARCHAR(100) NOT NULL,
            current_value INTEGER DEFAULT 0,
            target_value INTEGER NOT NULL,
            unlocked_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, achievement_key)
        );
        """,
        
        # Create index for efficient queries
        "CREATE INDEX IF NOT EXISTS idx_user_achievement_progress_user_id ON user_achievement_progress(user_id);",
        "CREATE INDEX IF NOT EXISTS idx_user_achievement_progress_key ON user_achievement_progress(achievement_key);",
        "CREATE INDEX IF NOT EXISTS idx_user_achievement_progress_unlocked ON user_achievement_progress(unlocked_at) WHERE unlocked_at IS NOT NULL;",
        
        # Insert default achievement definitions for all existing users
        """
        INSERT INTO user_achievement_progress (user_id, achievement_key, current_value, target_value)
        SELECT 
            u.id as user_id,
            achievement_key,
            0 as current_value,
            target_value
        FROM users u
        CROSS JOIN (
            VALUES 
                ('first_mood_entry', 1),
                ('seven_day_streak', 7),
                ('thirty_entries', 30),
                ('celebration_bronze', 1),
                ('celebration_silver', 5),
                ('celebration_gold', 10),
                ('community_posts_count', 5),
                ('challenge_streak', 3)
        ) AS achievements(achievement_key, target_value)
        ON CONFLICT (user_id, achievement_key) DO NOTHING;
        """
    ]
    
    try:
        with engine.connect() as conn:
            for migration in migrations:
                try:
                    logger.info(f"Executing migration...")
                    conn.execute(text(migration))
                    conn.commit()
                    logger.info("✅ Migration executed successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Migration might have already been applied or failed: {e}")
        
        logger.info("🎉 E3 Achievement System database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during E3 achievement migration: {e}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    if not success:
        sys.exit(1)
    print("E3 Achievement System migration completed successfully!")
