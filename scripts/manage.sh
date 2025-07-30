#!/bin/bash

# MantraPath Script Manager
echo "🔧 MantraPath Development Scripts"
echo "=================================="
echo ""

show_menu() {
    echo "Available startup options:"
    echo ""
    echo "  1) 🚀 Full Development (Backend + Frontend)"
    echo "     └─ Starts all services with hot reload"
    echo ""
    echo "  2) 🔧 Backend Only"
    echo "     └─ API services only (for backend development)"
    echo ""
    echo "  3) ⚡ Quick Demo"
    echo "     └─ Simplified setup with mock data"
    echo ""
    echo "  4) 🔄 Legacy Backend Services"
    echo "     └─ Original notification + mood services"
    echo ""
    echo "  5) ❓ Help & Info"
    echo ""
    echo "  0) Exit"
    echo ""
}

show_help() {
    echo "📚 MantraPath Scripts Documentation"
    echo "=================================="
    echo ""
    echo "Script Purposes:"
    echo ""
    echo "🚀 start-dev.sh"
    echo "   • Complete development environment"
    echo "   • Starts: Backend services + Frontend dev server"
    echo "   • Ports: 8000 (gateway), 8002 (notifications), 8003 (mood), 5173 (frontend)"
    echo "   • Features: Auto-reload, health checks, browser auto-open"
    echo ""
    echo "🔧 start-backend.sh"
    echo "   • Backend services only"
    echo "   • For backend development or API testing"
    echo "   • Includes database initialization"
    echo "   • Health check validation"
    echo ""
    echo "⚡ start-demo.sh"
    echo "   • Quick demo with minimal setup"
    echo "   • Single backend service + frontend"
    echo "   • Pre-loaded with demo data"
    echo "   • Auto-opens browser"
    echo ""
    echo "🔄 start-backend-services.sh"
    echo "   • Legacy script (existing)"
    echo "   • Notification + Mood services only"
    echo "   • No API gateway"
    echo ""
    echo "Notification Scheduler Features:"
    echo "• ✅ Real-time backend integration (not mock data)"
    echo "• ✅ User activity-based scheduling"
    echo "• ✅ Mood pattern analysis for optimal timing"
    echo "• ✅ WebSocket real-time notifications"
    echo "• ✅ Persistent notification preferences"
    echo ""
}

while true; do
    show_menu
    read -p "Choose an option (0-5): " choice
    echo ""
    
    case $choice in
        1)
            echo "🚀 Starting Full Development Environment..."
            ./start-dev.sh
            ;;
        2)
            echo "🔧 Starting Backend Services Only..."
            ./start-backend.sh
            ;;
        3)
            echo "⚡ Starting Quick Demo..."
            ./start-demo.sh
            ;;
        4)
            echo "🔄 Starting Legacy Backend Services..."
            ./start-backend-services.sh
            ;;
        5)
            show_help
            echo ""
            read -p "Press Enter to continue..."
            echo ""
            ;;
        0)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please choose 0-5."
            echo ""
            ;;
    esac
done
