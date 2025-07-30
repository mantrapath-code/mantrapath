# Start MantraPath Backend

To run the complete MantraPath application with backend services, follow these steps:

## Quick Start

1. **Open a new terminal**
2. **Navigate to backend directory:**
   ```bash
   cd backend
   ```
3. **Run the simple startup script:**
   ```bash
   python3 simple_start.py
   ```

Or start services individually in separate terminals:

## Manual Service Start

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

Once running, you should see:
- ✅ Auth Service: http://localhost:8001/docs
- ✅ Mood Service: http://localhost:8003/docs  
- ✅ API Gateway: http://localhost:8000/docs

## Status

The frontend will automatically detect when the backend is available and switch from mock data to real backend integration.

## Troubleshooting

If you get import errors, make sure the shared module is in your Python path:
```bash
export PYTHONPATH=$PWD/shared:$PYTHONPATH
```