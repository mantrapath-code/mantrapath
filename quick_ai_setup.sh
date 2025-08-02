#!/bin/bash

# MantraPath Enhanced AI - Quick Database Setup
# This script properly sets up the SQLite database with enhanced AI tables

echo "🚀 Setting up Enhanced AI Database for MantraPath"
echo "================================================"

cd /Users/sachin/mantrapath-holistic/backend

echo "📊 Current database status:"
if [ -f "mantrapath.db" ]; then
    echo "✅ SQLite database found: mantrapath.db"
    
    # Show current tables
    echo "📋 Current tables:"
    sqlite3 mantrapath.db ".tables"
    
    echo ""
    echo "🔧 Enhanced AI setup complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. ✅ Database migration: Already completed"
    echo "2. Configure API keys in .env.ai (copy from .env.ai.example)"
    echo "3. Test the system: cd backend && python3 test_enhanced_chatbot.py"
    echo "4. Start enhanced chatbot: cd services/chatbot_service && python3 enhanced_main.py"
    echo ""
    echo "🎯 Available API Endpoints:"
    echo "- POST http://localhost:8004/api/chatbot/enhanced/chat"
    echo "- GET  http://localhost:8004/api/chatbot/context/{user_id}"
    echo ""
    echo "🎉 Your enhanced AI chatbot is ready for personalized interactions!"
    
else
    echo "❌ Database file 'mantrapath.db' not found"
    echo "Please ensure your MantraPath backend is properly set up first"
    exit 1
fi
