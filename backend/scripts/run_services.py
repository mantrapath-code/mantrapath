#!/usr/bin/env python3
"""
Enhanced startup script for MantraPath backend services.
This version sets up all necessary paths and environment variables.
"""
import os
import sys
import subprocess
import time
import signal
from multiprocessing import Process

# Set up the Python path to include shared modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
shared_dir = os.path.join(backend_dir, "shared")
sys.path.insert(0, shared_dir)

def setup_environment():
    """Set up environment variables for development"""
    env_vars = {
        "DATABASE_URL": "sqlite:///./mantrapath.db",
        "REDIS_URL": "redis://localhost:6379",
        "JWT_SECRET_KEY": "dev-secret-key-change-in-production",
        "AUTH_SERVICE_URL": "http://localhost:8001",
        "PROFILE_SERVICE_URL": "http://localhost:8002",
        "MOOD_SERVICE_URL": "http://localhost:8003",
        "CHATBOT_SERVICE_URL": "http://localhost:8004",
        "CONTENT_SERVICE_URL": "http://localhost:8005",
        "COMMUNITY_SERVICE_URL": "http://localhost:8006",
        "NOTIFICATION_SERVICE_URL": "http://localhost:8007",
        "MEDIA_SERVICE_URL": "http://localhost:8009",
        "OPENAI_API_KEY": "your-openai-api-key-here"
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value

def run_service(service_name, port, service_path):
    """Run a single service"""
    print(f"🚀 Starting {service_name} on port {port}...")
    
    # Update Python path for the service
    env = os.environ.copy()
    env["PYTHONPATH"] = shared_dir
    
    try:
        # Change to service directory and run
        os.chdir(service_path)
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", str(port),
            "--reload"
        ], env=env)
    except KeyboardInterrupt:
        print(f"🛑 Stopping {service_name}")
    finally:
        # Return to backend directory
        os.chdir(backend_dir)

def install_dependencies():
    """Install required dependencies"""
    print("📦 Checking Python dependencies...")
    requirements_file = os.path.join(backend_dir, "requirements.txt")
    
    if os.path.exists(requirements_file):
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", requirements_file
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("⚠️  Some dependencies might be missing, but continuing...")
    else:
        print("⚠️  requirements.txt not found, skipping dependency installation")

def main():
    """Start all services"""
    print("🌟 Starting MantraPath Backend Services...")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Define services to start
    services = [
        ("Auth Service", 8001, "services/auth"),
        ("API Gateway", 8000, "services/gateway"),
        ("Mood Service", 8003, "services/mood"),
    ]
    
    processes = []
    
    print("\n📝 Environment Configuration:")
    print(f"   Database: SQLite (./mantrapath.db)")
    print(f"   Redis: localhost:6379 (optional)")
    print(f"   Backend Directory: {backend_dir}")
    print(f"   Shared Modules: {shared_dir}")
    print()
    
    try:
        for service_name, port, service_path in services:
            full_service_path = os.path.join(backend_dir, service_path)
            
            if os.path.exists(full_service_path):
                process = Process(target=run_service, args=(service_name, port, full_service_path))
                process.start()
                processes.append((process, service_name))
                time.sleep(3)  # Stagger startup
            else:
                print(f"⚠️  Service path not found: {full_service_path}")
        
        print("\n✅ Backend services started successfully!")
        print("\n🌐 Available Services:")
        print("   API Gateway: http://localhost:8000")
        print("   Auth Service: http://localhost:8001") 
        print("   Mood Service: http://localhost:8003")
        print("\n📚 API Documentation:")
        print("   Gateway: http://localhost:8000/docs")
        print("   Auth: http://localhost:8001/docs")
        print("   Mood: http://localhost:8003/docs")
        print("\n💡 Frontend can now connect to: http://localhost:8000")
        print("\nPress Ctrl+C to stop all services...")
        
        # Wait for processes
        for process, _ in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for process, service_name in processes:
            print(f"   Stopping {service_name}...")
            process.terminate()
        print("✅ All services stopped!")

if __name__ == "__main__":
    main()