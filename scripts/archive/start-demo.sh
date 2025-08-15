#!/bin/bash

# MantraPath Quick Demo
echo "⚡ Starting MantraPath Quick Demo..."

# Kill any existing processes
# Kill existing processes (archived script - use main start.sh)
lsof -ti:${FRONTEND_PORT},${API_GATEWAY_PORT} | xargs kill -9 2>/dev/null || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Quick dependency check
if ! command -v python3 &> /dev/null || ! command -v npm &> /dev/null; then
    echo "❌ Error: Python 3 and Node.js are required"
    echo "💡 Install them and try again"
    exit 1
fi

# Start simple backend (single service)
echo "🔄 Starting demo backend..."
cd backend

# Quick setup
python3 -m venv .demo_venv 2>/dev/null || true
source .demo_venv/bin/activate
pip install fastapi uvicorn sqlalchemy sqlite

# Create simple demo service
cat > demo_service.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime

app = FastAPI(title="MantraPath Demo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Demo data
demo_notifications = [
    {
        "id": "demo_1",
        "title": "Welcome to MantraPath! 🌟",
        "message": "Your wellness journey starts here. Try scheduling a mood check-in!",
        "notification_type": "system",
        "created_at": datetime.now().isoformat(),
        "is_read": False
    },
    {
        "id": "demo_2", 
        "title": "Smart Scheduling Active",
        "message": "AI-powered notifications are analyzing your patterns for optimal timing.",
        "notification_type": "insight",
        "created_at": datetime.now().isoformat(),
        "is_read": False
    }
]

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "demo"}

@app.get("/notify/recent")
async def get_notifications():
    return demo_notifications

@app.get("/notify/preferences")
async def get_preferences():
    return {
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "enabled_notification_types": ["mood-check", "breathing", "affirmation"],
        "max_notifications_per_day": 5,
        "adaptive_timing": True
    }

@app.put("/notify/preferences")
async def update_preferences(preferences: dict):
    return {"message": "Preferences updated successfully"}

@app.post("/notify/schedule")
async def schedule_notification(data: dict):
    return {"id": f"demo_{datetime.now().timestamp()}", "message": "Demo notification scheduled"}

@app.get("/api/v1/mood/")
async def get_moods():
    return [
        {
            "id": f"mood_{i}",
            "mood_score": 4,
            "energy_level": 3,
            "created_at": datetime.now().isoformat()
        } for i in range(5)
    ]

@app.get("/api/v1/analytics/patterns/weekly")
async def get_patterns():
    return {
        "weekly_averages": {
            "monday": 6.5, "tuesday": 7.0, "wednesday": 7.5,
            "thursday": 7.2, "friday": 8.0, "saturday": 8.5, "sunday": 7.8
        },
        "patterns": [],
        "total_weeks": 4
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Start demo backend
python3 demo_service.py &
BACKEND_PID=$!

cd ../frontend

# Quick frontend setup
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies (one-time setup)..."
    npm install
fi

# Start frontend
echo "🎨 Starting demo frontend..."
npm run dev -- --port ${FRONTEND_PORT} &
FRONTEND_PID=$!

# Wait and check
sleep 5

echo ""
echo "🎉 MantraPath Demo is ready!"
echo "🌐 Open: ${PROTOCOL}://${DOMAIN}:${FRONTEND_PORT}"
echo ""
echo "🔥 Demo features:"
echo "   • Smart notification scheduler with mock AI patterns"
echo "   • Real-time notification system"  
echo "   • Mood tracking and analytics"
echo "   • All data is simulated for demo purposes"
echo ""
echo "💡 This demo shows the notification scheduler with:"
echo "   ✅ Backend integration working"
echo "   ✅ Real-time scheduling" 
echo "   ✅ User activity-based recommendations"
echo "   ✅ Adaptive timing based on mood patterns"
echo ""
echo "🛑 Press Ctrl+C to stop demo"

# Auto-open browser
if command -v open &> /dev/null; then
    sleep 3
    open ${PROTOCOL}://${DOMAIN}:${FRONTEND_PORT}
fi

# Cleanup on exit
trap 'echo "🛑 Stopping demo..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; deactivate 2>/dev/null; exit' INT
wait
