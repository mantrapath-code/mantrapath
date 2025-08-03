#!/usr/bin/env python3
"""
Community Service Database Migration Script
Creates all necessary tables for the psychology-based community system
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging

# Add the parent directory to Python path for shared imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database import get_database_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_community_tables():
    """Create all community service tables"""
    try:
        # Get database connection
        conn = get_database_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'init_community_tables.sql')
        
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL file not found: {sql_file_path}")
            return False
            
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        
        # Execute the SQL
        logger.info("Creating community service tables...")
        cursor.execute(sql_content)
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE 'community_%'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        logger.info(f"Created {len(tables)} community tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Community database tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating community tables: {e}")
        return False

def verify_tables():
    """Verify all expected tables exist"""
    expected_tables = [
        'community_hubs',
        'community_hub_membership', 
        'community_conversations',
        'community_events',
        'community_challenges',
        'community_feed_items',
        'user_feed_preferences',
        'community_resources',
        'community_mood_analytics'
    ]
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = ANY(%s)
        """, (expected_tables,))
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        missing_tables = set(expected_tables) - set(existing_tables)
        
        cursor.close()
        conn.close()
        
        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables}")
            return False
        else:
            logger.info("✅ All community tables verified!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verifying tables: {e}")
        return False

def main():
    """Main migration function"""
    logger.info("🚀 Starting community service database migration...")
    
    # Create tables
    if not create_community_tables():
        logger.error("Failed to create tables")
        sys.exit(1)
    
    # Verify tables
    if not verify_tables():
        logger.error("Table verification failed")
        sys.exit(1)
    
    logger.info("🎉 Community service database migration completed successfully!")

if __name__ == "__main__":
    main()
