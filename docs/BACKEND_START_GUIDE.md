# MantraPath Backend Quick Start Guide

This guide helps you start the MantraPath backend services for full functionality.

## Quick Start (Recommended)

1. **Open a new terminal**
2. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

3. **Run the setup script:**
   ```bash
   python3 setup_backend.py
   ```

4. **Start services manually in separate terminals:**

   **Terminal 1 - Auth Service:**
   ```bash
   cd backend/services/auth
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

   **Terminal 2 - Mood Service:**
   ```bash
   cd backend/services/mood  
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8003 --reload
   ```

   **Terminal 3 - API Gateway:**
   ```bash
   cd backend/services/gateway
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Verification

Once all services are running, you should see:

- ✅ Auth Service: http://localhost:8001/docs
- ✅ Mood Service: http://localhost:8003/docs  
- ✅ API Gateway: http://localhost:8000/docs
- ✅ Frontend connects to: http://localhost:8000

## Troubleshooting

### Import Errors
If you see import errors, make sure to set the Python path:
```bash
export PYTHONPATH="/workspaces/spark-template/backend/shared:$PYTHONPATH"
```

### Database Issues
The services use SQLite by default. Database files will be created automatically.

### Port Conflicts
If ports are in use, you can change them by editing the port numbers in the uvicorn commands.

## Environment Variables

The backend uses these environment variables (automatically set):

```bash
DATABASE_URL=sqlite:///./mantrapath.db
JWT_SECRET_KEY=dev-secret-key-change-in-production-12345
AUTH_SERVICE_URL=http://localhost:8001
MOOD_SERVICE_URL=http://localhost:8003
```

## Features When Backend is Connected

With the backend running, you get:
- ✅ Real user authentication & registration
- ✅ Persistent mood tracking data
- ✅ Journal entries saved to database
- ✅ Real-time mood analytics
- ✅ User session management
- ✅ Secure API endpoints

## Mock Data Mode

If backend is not running, the frontend automatically uses mock data:
- ❓ Simulated authentication
- ❓ Temporary mood entries (lost on refresh)
- ❓ Sample analytics data

**To get full functionality, please start the backend services as described above.**