#!/usr/bin/env python3
"""
Test script to verify backend services can start
"""
import os
import sys

def test_imports():
    """Test if we can import shared modules"""
    # Add shared directory to path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    shared_dir = os.path.join(backend_dir, "shared")
    sys.path.insert(0, shared_dir)
    
    print(f"Backend directory: {backend_dir}")
    print(f"Shared directory: {shared_dir}")
    print(f"Shared directory exists: {os.path.exists(shared_dir)}")
    
    try:
        from database import get_db, create_tables
        print("✅ Database module imported successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
        
    try:
        from auth import hash_password, verify_password
        print("✅ Auth module imported successfully")
    except Exception as e:
        print(f"❌ Auth import failed: {e}")
        return False
        
    try:
        from models import User, MoodEntry
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    return True

def test_database():
    """Test database creation"""
    try:
        # Set environment for SQLite
        os.environ["DATABASE_URL"] = "sqlite:///./test_mantrapath.db"
        
        # Import after setting environment
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        shared_dir = os.path.join(backend_dir, "shared")
        sys.path.insert(0, shared_dir)
        
        from database import create_tables
        create_tables()
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def main():
    print("🧪 Testing MantraPath Backend Components...")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return
    
    # Test database
    if not test_database():
        print("\n❌ Database tests failed")
        return
        
    print("\n✅ All tests passed! Backend components are ready.")
    print("\nTo start the backend services:")
    print("  Option 1: python3 simple_start.py")
    print("  Option 2: ./start_backend.sh")

if __name__ == "__main__":
    main()