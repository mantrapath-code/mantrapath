"""
Simple backend starter - run each service manually
"""

import os
import sys

# Setup environment
os.environ.update({
    "DATABASE_URL": "sqlite:///./mantrapath.db",
    "JWT_SECRET_KEY": "dev-secret-key-change-in-production",
    "PYTHONPATH": os.path.join(os.getcwd(), "backend", "shared")
})

print("🚀 MantraPath Backend Setup")
print("=" * 30)
print("Environment configured!")
print("DATABASE_URL:", os.environ.get("DATABASE_URL"))
print("PYTHONPATH:", os.environ.get("PYTHONPATH"))
print()
print("To start the services manually, run these commands in separate terminals:")
print()
print("# Terminal 1 - Auth Service")
print("cd backend/services/auth")
print("uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
print()
print("# Terminal 2 - Mood Service") 
print("cd backend/services/mood")
print("uvicorn main:app --host 0.0.0.0 --port 8003 --reload")
print()
print("# Terminal 3 - API Gateway")
print("cd backend/services/gateway")
print("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
print()
print("Once all services are running:")
print("🔐 Auth Service: http://localhost:8001")
print("😊 Mood Service: http://localhost:8003")
print("🌐 API Gateway: http://localhost:8000")
print()
print("Your frontend will automatically detect and use the backend!")