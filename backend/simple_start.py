#!/usr/bin/env python3
"""
Simple backend runner for development
"""
import os
import sys
import subprocess
import threading
import time

def run_auth_service():
    """Run the auth service"""
    print("🔐 Starting Auth Service on port 8001...")
    
    # Setup environment
    env = os.environ.copy()
    env.update({
        "DATABASE_URL": "sqlite:///./mantrapath.db",
        "JWT_SECRET_KEY": "dev-secret-key-change-in-production"
    })
    
    # Change to auth service directory
    auth_dir = os.path.join(os.path.dirname(__file__), "services", "auth")
    
    # Add shared directory to Python path
    shared_dir = os.path.join(os.path.dirname(__file__), "shared")
    env["PYTHONPATH"] = shared_dir
    
    try:
        subprocess.call([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", "--port", "8001", "--reload"
        ], cwd=auth_dir, env=env)
    except KeyboardInterrupt:
        print("🛑 Auth service stopped")

def run_gateway():
    """Run the API gateway"""
    print("🌐 Starting API Gateway on port 8000...")
    
    # Setup environment
    env = os.environ.copy()
    env.update({
        "AUTH_SERVICE_URL": "http://localhost:8001",
        "MOOD_SERVICE_URL": "http://localhost:8003"
    })
    
    # Change to gateway directory
    gateway_dir = os.path.join(os.path.dirname(__file__), "services", "gateway")
    
    try:
        subprocess.call([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=gateway_dir, env=env)
    except KeyboardInterrupt:
        print("🛑 Gateway stopped")

def run_mood_service():
    """Run the mood service"""
    print("😊 Starting Mood Service on port 8003...")
    
    # Setup environment
    env = os.environ.copy()
    env.update({
        "DATABASE_URL": "sqlite:///./mantrapath.db"
    })
    
    # Change to mood service directory
    mood_dir = os.path.join(os.path.dirname(__file__), "services", "mood")
    
    # Add shared directory to Python path
    shared_dir = os.path.join(os.path.dirname(__file__), "shared")
    env["PYTHONPATH"] = shared_dir
    
    try:
        subprocess.call([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0", "--port", "8003", "--reload"
        ], cwd=mood_dir, env=env)
    except KeyboardInterrupt:
        print("🛑 Mood service stopped")

def main():
    print("🚀 Starting MantraPath Backend Services...")
    print("=" * 50)
    
    # Start services in separate threads
    auth_thread = threading.Thread(target=run_auth_service, daemon=True)
    gateway_thread = threading.Thread(target=run_gateway, daemon=True)
    mood_thread = threading.Thread(target=run_mood_service, daemon=True)
    
    # Start auth service first
    auth_thread.start()
    time.sleep(3)
    
    # Start mood service
    mood_thread.start()
    time.sleep(3)
    
    # Start gateway last
    gateway_thread.start()
    time.sleep(2)
    
    print("\n✅ Backend services started!")
    print("🌐 API Gateway: http://localhost:8000")
    print("🔐 Auth Service: http://localhost:8001")
    print("😊 Mood Service: http://localhost:8003")
    print("\nPress Ctrl+C to stop...")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")

if __name__ == "__main__":
    main()