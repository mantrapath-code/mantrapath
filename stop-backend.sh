#!/bin/bash

# MantraPath Backend Stop Script
echo "🛑 Stopping MantraPath Backend Services..."

# Function to stop a service
stop_service() {
    local service_name=$1
    local pid_file="backend/logs/${service_name,,}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "🔄 Stopping $service_name (PID: $pid)..."
            kill $pid
            rm -f "$pid_file"
            echo "✅ $service_name stopped"
        else
            echo "❌ $service_name was not running"
            rm -f "$pid_file"
        fi
    else
        echo "❓ No PID file found for $service_name"
    fi
}

# Stop services
stop_service "Gateway"
stop_service "Auth-Service" 
stop_service "Mood-Service"

# Also try to kill any remaining uvicorn processes
echo "🧹 Cleaning up any remaining uvicorn processes..."
pkill -f "uvicorn.*MantraPath" 2>/dev/null || true

echo "🏁 All services stopped!"