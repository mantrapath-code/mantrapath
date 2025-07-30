#!/usr/bin/env python3
"""
Minimal backend service starter for MantraPath
"""
import os
import sys
import time
import signal
from multiprocessing import Process
import subprocess

def setup_environment():
    """Setup required environment variables"""
    os.environ.update({
        "DATABASE_URL": "sqlite:///./mantrapath.db",
        "JWT_SECRET_KEY": "dev-secret-key-change-in-production-12345",
        "AUTH_SERVICE_URL": "http://localhost:8001",
        "MOOD_SERVICE_URL": "http://localhost:8003",
        "PYTHONPATH": os.path.join(os.path.dirname(__file__), "shared")
    })

def create_database():
    """Create database tables"""
    try:
        # Add shared to path
        shared_dir = os.path.join(os.path.dirname(__file__), "shared")
        sys.path.insert(0, shared_dir)
        
        from database import create_tables
        create_tables()
        print("✅ Database tables created")
        return True
    except Exception as e:
        print(f"⚠️ Database setup warning: {e}")
        return False

def run_service(name, port, path):
    """Run a single service"""
    try:
        print(f"Starting {name} on port {port}...")
        os.chdir(path)
        
        # Simple subprocess call
        result = subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", "--port", str(port), "--reload"
        ], check=False)
        
    except Exception as e:
        print(f"Error starting {name}: {e}")

def main():
    print("🚀 MantraPath Backend Starter")
    print("=" * 40)
    
    # Setup
    setup_environment()
    
    # Create database
    create_database()
    
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    services = [
        ("Auth Service", 8001, os.path.join(backend_dir, "services", "auth")),
        ("Mood Service", 8003, os.path.join(backend_dir, "services", "mood")),
        ("API Gateway", 8000, os.path.join(backend_dir, "services", "gateway"))
    ]
    
    print("\n🔧 Available services:")
    for name, port, path in services:
        status = "✅" if os.path.exists(path) else "❌"
        print(f"   {status} {name} -> {path}")
    
    print(f"\n📁 Backend directory: {backend_dir}")
    print(f"📁 Shared modules: {os.path.join(backend_dir, 'shared')}")
    print(f"🗄️ Database: {os.environ.get('DATABASE_URL')}")
    
    print("\n" + "=" * 40)
    print("To start services manually:")
    print("1. cd backend/services/auth && python3 -m uvicorn main:app --port 8001 --reload")
    print("2. cd backend/services/mood && python3 -m uvicorn main:app --port 8003 --reload") 
    print("3. cd backend/services/gateway && python3 -m uvicorn main:app --port 8000 --reload")
    print("=" * 40)

if __name__ == "__main__":
    main()