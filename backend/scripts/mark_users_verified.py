#!/usr/bin/env python3
"""
Script to mark all existing users as verified when bypassing email verification
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shared.database import DATABASE_URL
from shared.models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def mark_users_as_verified():
    """Mark all existing unverified users as verified"""
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        db = SessionLocal()
        
        # Find all unverified users
        unverified_users = db.query(User).filter(User.is_verified == False).all()
        
        if not unverified_users:
            logger.info("✅ No unverified users found")
            return True
            
        logger.info(f"🔄 Found {len(unverified_users)} unverified users")
        
        # Mark them as verified
        for user in unverified_users:
            user.is_verified = True
            user.verification_token = None
            user.verification_token_expires = None
            logger.info(f"✅ Marked user {user.email} as verified")
        
        db.commit()
        logger.info(f"🎉 Successfully marked {len(unverified_users)} users as verified")
        
    except Exception as e:
        logger.error(f"❌ Error marking users as verified: {e}")
        db.rollback()
        return False
    finally:
        db.close()
        
    return True

if __name__ == "__main__":
    success = mark_users_as_verified()
    if not success:
        sys.exit(1)
    print("✅ All users are now verified!")
