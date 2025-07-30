#!/usr/bin/env python3
"""
Development startup script for MantraPath backend services
"""
import subprocess
import os
import sys
import time
import signal
from multiprocessing import Process

def run_service(service_name, port, service_path):
    """Run a single service"""
    print(f"🚀 Starting {service_name} on port {port}...")
    
    env = os.environ.copy()
    env.update({
        "DATABASE_URL": "sqlite:///./mantrapath.db",  # Use SQLite for development
        "REDIS_URL": "redis://localhost:6379",
        "JWT_SECRET_KEY": "dev-secret-key-change-in-production"
    })
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ], cwd=service_path, env=env)
    except KeyboardInterrupt:
        print(f"🛑 Stopping {service_name}")

def main():
    """Start all services"""
    services = [
        ("API Gateway", 8000, "services/gateway"),
        ("Auth Service", 8001, "services/auth"),
        ("Mood Service", 8003, "services/mood"),
    ]
    
    processes = []
    
    print("🌟 Starting MantraPath Backend Services...")
    print("📝 Note: Make sure Redis is running on localhost:6379")
    print("📝 Using SQLite database for development")
    print()
    
    try:
        for service_name, port, service_path in services:
            if os.path.exists(service_path):
                process = Process(target=run_service, args=(service_name, port, service_path))
                process.start()
                processes.append(process)
                time.sleep(2)  # Stagger startup
            else:
                print(f"⚠️  Service path not found: {service_path}")
        
        print()
        print("✅ All services started!")
        print("🌐 API Gateway: http://localhost:8000")
        print("🔐 Auth Service: http://localhost:8001") 
        print("😊 Mood Service: http://localhost:8003")
        print()
        print("📚 API Documentation:")
        print("   Gateway: http://localhost:8000/docs")
        print("   Auth: http://localhost:8001/docs")
        print("   Mood: http://localhost:8003/docs")
        print()
        print("Press Ctrl+C to stop all services...")
        
        # Wait for processes
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for process in processes:
            process.terminate()
        print("✅ All services stopped!")

if __name__ == "__main__":
    main()