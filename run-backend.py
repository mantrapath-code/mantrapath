#!/usr/bin/env python3
"""
Simple backend starter for MantraPath
This script starts the essential services needed for the frontend
"""

import subprocess
import os
import sys
import time
import signal
import threading
from pathlib import Path

def setup_environment():
    """Setup environment variables for development"""
    os.environ.update({
        "DATABASE_URL": "sqlite:///./mantrapath.db",
        "JWT_SECRET_KEY": "dev-secret-key-change-in-production-please",
        "AUTH_SERVICE_URL": "http://localhost:8001",
        "MOOD_SERVICE_URL": "http://localhost:8003",
        "PYTHONPATH": os.path.join(os.getcwd(), "backend", "shared")
    })

def run_service(name, port, service_dir):
    """Run a single service"""
    print(f"🔄 Starting {name} on port {port}...")
    
    # Change to service directory
    service_path = Path("backend") / "services" / service_dir
    
    if not service_path.exists():
        print(f"❌ Service directory not found: {service_path}")
        return None
    
    # Start uvicorn
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ], cwd=service_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ {name} started with PID {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def check_service_health(port, service_name):
    """Check if service is responding"""
    import urllib.request
    import urllib.error
    
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/health", timeout=5) as response:
            if response.status == 200:
                print(f"✅ {service_name} is healthy")
                return True
    except urllib.error.URLError:
        print(f"⚠️  {service_name} not responding yet")
    except Exception as e:
        print(f"⚠️  {service_name} health check failed: {e}")
    
    return False

def main():
    """Main startup routine"""
    print("🚀 Starting MantraPath Backend Services...")
    print("=" * 50)
    
    setup_environment()
    
    # Services to start
    services = [
        ("Auth Service", 8001, "auth"),
        ("Mood Service", 8003, "mood"),
        ("API Gateway", 8000, "gateway")
    ]
    
    processes = []
    
    # Start services
    for name, port, service_dir in services:
        process = run_service(name, port, service_dir)
        if process:
            processes.append((name, port, process))
            time.sleep(2)  # Wait between services
    
    if not processes:
        print("❌ No services started successfully")
        return
    
    print(f"\n🌟 Started {len(processes)} services")
    
    # Wait a bit for services to fully initialize
    print("⏳ Waiting for services to initialize...")
    time.sleep(5)
    
    # Check service health
    print("\n🔍 Checking service health...")
    for name, port, process in processes:
        if process.poll() is None:  # Process still running
            check_service_health(port, name)
        else:
            print(f"❌ {name} process terminated")
    
    print("\n🌐 Backend Services:")
    print("   🔐 Auth Service: http://localhost:8001")
    print("   😊 Mood Service: http://localhost:8003")
    print("   🌐 API Gateway: http://localhost:8000")
    print("\n📚 API Documentation:")
    print("   Auth: http://localhost:8001/docs")
    print("   Mood: http://localhost:8003/docs") 
    print("   Gateway: http://localhost:8000/docs")
    print("\n✨ Your frontend should now connect to the real backend!")
    print("💡 Refresh your browser to see the backend connection")
    print("\nPress Ctrl+C to stop all services...")
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down services...")
        for name, port, process in processes:
            if process.poll() is None:
                print(f"🔄 Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print("✅ All services stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
            # Check if any process died
            active_processes = [(n, p, pr) for n, p, pr in processes if pr.poll() is None]
            if len(active_processes) != len(processes):
                print("⚠️  Some services stopped unexpectedly")
                break
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()