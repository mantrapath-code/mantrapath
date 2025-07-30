#!/bin/bash
"""
API Gateway Management Script
Choose between basic and enhanced API Gateway
"""

GATEWAY_DIR="/Users/sachin/mantrapath-holistic/backend/services/api_gateway"
CURRENT_GATEWAY="$GATEWAY_DIR/main.py"
ENHANCED_GATEWAY="$GATEWAY_DIR/main_enhanced.py"

echo "🌐 MantraPath API Gateway Management"
echo "=================================="
echo ""
echo "Current gateway: $(basename "$CURRENT_GATEWAY")"
echo ""
echo "Available options:"
echo "1. Use Enhanced Gateway (Recommended - with request tracking, rate limiting, user data management)"
echo "2. Use Basic Gateway (Simple proxy)"
echo "3. View Gateway Status"
echo "4. Exit"
echo ""

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        echo "🚀 Switching to Enhanced API Gateway..."
        
        # Backup current gateway
        if [[ -f "$CURRENT_GATEWAY" ]]; then
            cp "$CURRENT_GATEWAY" "$GATEWAY_DIR/main_basic_backup.py"
            echo "✅ Backed up current gateway to main_basic_backup.py"
        fi
        
        # Copy enhanced gateway
        cp "$ENHANCED_GATEWAY" "$CURRENT_GATEWAY"
        echo "✅ Enhanced gateway activated"
        
        # Stop current gateway if running
        pkill -f "api_gateway.*main.py" 2>/dev/null || true
        
        # Start enhanced gateway
        echo "🔄 Starting enhanced API gateway..."
        cd "$GATEWAY_DIR"
        python3 main.py &
        GATEWAY_PID=$!
        
        sleep 3
        
        # Check if it started successfully
        if kill -0 $GATEWAY_PID 2>/dev/null; then
            echo "✅ Enhanced API Gateway started successfully (PID: $GATEWAY_PID)"
            echo "📋 Features enabled:"
            echo "   • Request tracking and analytics"
            echo "   • Rate limiting"
            echo "   • Service health monitoring"
            echo "   • User data management (export/delete)"
            echo "   • WebSocket support"
            echo "   • Enhanced error handling"
            echo ""
            echo "🔗 Gateway running at: http://localhost:8000"
            echo "📖 Documentation: http://localhost:8000/docs"
            echo "📊 Metrics: http://localhost:8000/metrics (requires auth)"
        else
            echo "❌ Failed to start enhanced gateway"
            # Restore backup
            if [[ -f "$GATEWAY_DIR/main_basic_backup.py" ]]; then
                cp "$GATEWAY_DIR/main_basic_backup.py" "$CURRENT_GATEWAY"
                echo "🔄 Restored basic gateway"
            fi
        fi
        ;;
        
    2)
        echo "🔄 Switching to Basic API Gateway..."
        
        # Stop current gateway if running
        pkill -f "api_gateway.*main.py" 2>/dev/null || true
        
        # Restore basic gateway if backup exists
        if [[ -f "$GATEWAY_DIR/main_basic_backup.py" ]]; then
            cp "$GATEWAY_DIR/main_basic_backup.py" "$CURRENT_GATEWAY"
            echo "✅ Basic gateway restored from backup"
        else
            echo "⚠️  No backup found. Using current main.py"
        fi
        
        # Start basic gateway
        echo "🔄 Starting basic API gateway..."
        cd "$GATEWAY_DIR"
        python3 main.py &
        GATEWAY_PID=$!
        
        sleep 3
        
        if kill -0 $GATEWAY_PID 2>/dev/null; then
            echo "✅ Basic API Gateway started successfully (PID: $GATEWAY_PID)"
        else
            echo "❌ Failed to start basic gateway"
        fi
        ;;
        
    3)
        echo "📊 Gateway Status:"
        echo "=================="
        
        # Check if gateway is running
        GATEWAY_PIDS=$(pgrep -f "api_gateway.*main.py" || true)
        
        if [[ -n "$GATEWAY_PIDS" ]]; then
            echo "✅ API Gateway is running (PIDs: $GATEWAY_PIDS)"
            
            # Test connectivity
            echo "🔍 Testing connectivity..."
            if curl -s http://localhost:8000/health > /dev/null; then
                echo "✅ Gateway is responding"
                
                # Get gateway info
                GATEWAY_INFO=$(curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Could not parse response")
                echo "📋 Gateway Info:"
                echo "$GATEWAY_INFO"
            else
                echo "❌ Gateway is not responding"
            fi
        else
            echo "❌ API Gateway is not running"
        fi
        
        # Check which gateway is active
        if grep -q "Enhanced API Gateway" "$CURRENT_GATEWAY" 2>/dev/null; then
            echo "🚀 Type: Enhanced Gateway"
        else
            echo "🔧 Type: Basic Gateway"
        fi
        ;;
        
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
        
    *)
        echo "❌ Invalid option. Please choose 1-4."
        exit 1
        ;;
esac
