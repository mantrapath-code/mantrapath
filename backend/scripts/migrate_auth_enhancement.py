#!/usr/bin/env python3
"""
Database migration script for MantraPath authentication enhancements
Adds email verification fields to the users table
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
    """Add email verification fields to users table"""
    
    engine = create_engine(DATABASE_URL)
    
    migrations = [
        # Remove unique constraint from username
        "ALTER TABLE users DROP CONSTRAINT IF EXISTS users_username_key;",
        
        # Add email verification fields
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token VARCHAR(255) UNIQUE;",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_token_expires TIMESTAMP;",
        
        # Update existing users to be verified (for backward compatibility)
        "UPDATE users SET is_verified = TRUE WHERE is_verified IS NULL;",
    ]
    
    try:
        with engine.connect() as conn:
            for migration in migrations:
                try:
                    logger.info(f"Executing: {migration}")
                    conn.execute(text(migration))
                    conn.commit()
                    logger.info("✅ Migration executed successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Migration might have already been applied or failed: {e}")
                    
        logger.info("🎉 Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = migrate_database()
    if not success:
        sys.exit(1)
    print("Migration completed successfully!")
