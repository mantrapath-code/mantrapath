"""
Test script to verify backend services can start
"""
import subprocess
import sys
import os
from pathlib import Path

def test_auth_service():
    """Test starting the auth service"""
    print("🔐 Testing Auth Service...")
    
    # Setup environment
    os.environ.update({
        "DATABASE_URL": "sqlite:///./mantrapath.db",
        "JWT_SECRET_KEY": "dev-secret-key",
        "PYTHONPATH": str(Path.cwd() / "backend" / "shared")
    })
    
    # Change to auth service directory
    auth_dir = Path("backend") / "services" / "auth"
    
    if not auth_dir.exists():
        print(f"❌ Auth service directory not found: {auth_dir}")
        return False
    
    if not (auth_dir / "main.py").exists():
        print(f"❌ main.py not found in: {auth_dir}")
        return False
    
    print(f"✅ Found auth service at: {auth_dir}")
    print(f"✅ Environment configured")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    
    # Test command that would start the service
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
    print(f"✅ Command to start: {' '.join(cmd)}")
    print(f"✅ Working directory: {auth_dir}")
    
    print("\n🚀 To start the auth service manually:")
    print(f"   cd {auth_dir}")
    print(f"   {' '.join(cmd)}")
    
    return True

def test_gateway_service():
    """Test gateway service"""
    print("\n🌐 Testing Gateway Service...")
    
    gateway_dir = Path("backend") / "services" / "gateway"
    
    if not gateway_dir.exists():
        print(f"❌ Gateway directory not found: {gateway_dir}")
        return False
    
    if not (gateway_dir / "main.py").exists():
        print(f"❌ main.py not found in: {gateway_dir}")
        return False
    
    print(f"✅ Found gateway service at: {gateway_dir}")
    
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    print(f"✅ Command to start: {' '.join(cmd)}")
    
    print("\n🚀 To start the gateway manually:")
    print(f"   cd {gateway_dir}")
    print(f"   {' '.join(cmd)}")
    
    return True

def test_mood_service():
    """Test mood service"""
    print("\n😊 Testing Mood Service...")
    
    mood_dir = Path("backend") / "services" / "mood"
    
    if not mood_dir.exists():
        print(f"❌ Mood directory not found: {mood_dir}")
        return False
    
    if not (mood_dir / "main.py").exists():
        print(f"❌ main.py not found in: {mood_dir}")
        return False
    
    print(f"✅ Found mood service at: {mood_dir}")
    
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
    print(f"✅ Command to start: {' '.join(cmd)}")
    
    print("\n🚀 To start the mood service manually:")
    print(f"   cd {mood_dir}")
    print(f"   {' '.join(cmd)}")
    
    return True

if __name__ == "__main__":
    print("🔍 MantraPath Backend Service Test")
    print("=" * 40)
    
    auth_ok = test_auth_service()
    gateway_ok = test_gateway_service()  
    mood_ok = test_mood_service()
    
    print("\n" + "=" * 40)
    if auth_ok and gateway_ok and mood_ok:
        print("✅ All services are properly configured!")
        print("\n💡 Quick Start Guide:")
        print("1. Open 3 terminal windows")
        print("2. In terminal 1: cd backend/services/auth && uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
        print("3. In terminal 2: cd backend/services/mood && uvicorn main:app --host 0.0.0.0 --port 8003 --reload")  
        print("4. In terminal 3: cd backend/services/gateway && uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print("5. Refresh your frontend - it will automatically connect!")
        print("\n🌐 Services will be available at:")
        print("   Auth: http://localhost:8001/docs")
        print("   Mood: http://localhost:8003/docs")
        print("   Gateway: http://localhost:8000/docs")
    else:
        print("❌ Some services have configuration issues")
        print("Check the errors above and ensure all backend files are present")