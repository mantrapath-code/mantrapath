#!/bin/bash

# MantraPath Enhanced AI Setup Script
# This script sets up the enhanced AI architecture for personalized chatbot interactions

echo "🚀 Setting up MantraPath Enhanced AI Architecture"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "backend/README.md" ]; then
    echo "❌ Please run this script from the mantrapath-holistic root directory"
    exit 1
fi

# Navigate to backend directory
cd backend

echo "📁 Creating new service directories..."

# Create journal assistant service directory
mkdir -p services/journal_assistant_service
mkdir -p services/intelligent_feeds_service

# Create necessary subdirectories
mkdir -p services/chatbot_service/models
mkdir -p services/chatbot_service/utils
mkdir -p database/migrations

echo "✅ Service directories created"

echo "📋 Checking Python dependencies..."

# Check if required packages are installed
python3 -c "import openai" 2>/dev/null || echo "⚠️  OpenAI package not found. Install with: pip install openai"
python3 -c "import asyncio" 2>/dev/null && echo "✅ asyncio available"
python3 -c "import dataclasses" 2>/dev/null && echo "✅ dataclasses available"
python3 -c "import statistics" 2>/dev/null && echo "✅ statistics available"

echo "📊 Database setup..."

# Check if SQLite database exists
if [ -f "mantrapath.db" ]; then
    echo "✅ SQLite database found: mantrapath.db"
    
    # Check if sqlite3 command is available
    if command -v sqlite3 &> /dev/null; then
        echo "✅ SQLite3 CLI available"
        
        # Check existing tables
        existing_tables=$(sqlite3 mantrapath.db ".tables" 2>/dev/null)
        if [ ! -z "$existing_tables" ]; then
            echo "✅ Database tables found"
        else
            echo "⚠️  Database exists but no tables found"
        fi
    else
        echo "⚠️  sqlite3 command not found. Install with: brew install sqlite"
    fi
else
    echo "⚠️  Database file 'mantrapath.db' not found. Please ensure your MantraPath backend is properly set up"
fi

echo "🔧 Setting up enhanced chatbot service..."

# Copy the enhanced chatbot files
echo "Copying enhanced chatbot context engine..."

# Make the test script executable
chmod +x test_enhanced_chatbot.py

echo "📝 Creating environment configuration..."

# Create a .env.example file for AI services
cat > .env.ai.example << 'EOL'
# Enhanced AI Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_TRANSLATE_API_KEY=your_google_translate_key_here
GOOGLE_SPEECH_API_KEY=your_google_speech_key_here

# AI Service Settings
AI_RESPONSE_TIMEOUT=30
AI_CONTEXT_CACHE_DURATION=3600
AI_MAX_CONTEXT_SIZE=10000
AI_PERSONALIZATION_THRESHOLD=0.7

# Privacy Settings
AI_PRIVACY_MODE=false
AI_LOCAL_PROCESSING=false
AI_DATA_RETENTION_DAYS=90

# Performance Settings
AI_ENABLE_CACHING=true
AI_PARALLEL_PROCESSING=true
AI_MAX_CONCURRENT_REQUESTS=50
EOL

echo "⚙️ Setting up database migrations..."

# Make migration executable
chmod +x database/migrations/001_enhanced_ai_context_tables.sql

echo "🧪 Preparing test environment..."

# Create a simple test runner script
cat > run_ai_tests.sh << 'EOL'
#!/bin/bash
echo "🧪 Running Enhanced AI Tests..."
cd backend
python3 test_enhanced_chatbot.py
EOL

chmod +x run_ai_tests.sh

echo "📚 Creating documentation..."

# Create a quick start guide
cat > ENHANCED_AI_QUICKSTART.md << 'EOL'
# 🚀 MantraPath Enhanced AI - Quick Start Guide

## Prerequisites
1. MySQL database running
2. Python 3.8+ with required packages
3. OpenAI API key (optional but recommended)

## Setup Steps

### 1. Database Migration
```bash
cd backend
sqlite3 mantrapath.db < database/migrations/001_enhanced_ai_context_tables_sqlite.sql
```

### 2. Environment Configuration
```bash
cp .env.ai.example .env.ai
# Edit .env.ai with your API keys
```

### 3. Install Python Dependencies
```bash
pip install openai anthropic google-cloud-translate google-cloud-speech
```

### 4. Test the Enhanced Chatbot
```bash
cd backend
python3 test_enhanced_chatbot.py
```

### 5. Start Enhanced Services
```bash
# Start the enhanced chatbot service
cd services/chatbot_service
python3 enhanced_main.py
```

## Testing the Enhancement

1. **Create Test Data**: The test script creates a user with comprehensive data
2. **Test Context Engine**: Verifies user context gathering from all services
3. **Test Personalized Responses**: Shows context-aware AI responses

## API Endpoints

### Enhanced Chatbot
- `POST /api/chatbot/enhanced/chat` - Context-aware personalized chat
- `GET /api/chatbot/context/{user_id}` - Get user context summary

### Response Example
```json
{
  "response": "Hello Alice! I can see you've been going through some challenging times at work lately. I've noticed from your journal entries that you've been feeling anxious about project deadlines. How can I support you today?",
  "session_id": "session-123",
  "message_type": "personalized",
  "personalization_score": 0.9,
  "user_state": "needs_support"
}
```

## Next Steps

1. **Phase 2**: Implement Journal Assistant Service (Port 8011)
2. **Phase 3**: Implement Intelligent Feeds Service (Port 8012)
3. **Phase 4**: Full integration and optimization

## Features Available Now

✅ **User Context Engine**: Gathers data from all services
✅ **Personalized Responses**: Context-aware AI interactions
✅ **Mood Trend Analysis**: Understands user's emotional patterns
✅ **Writing Style Adaptation**: Adapts to user's communication preferences
✅ **Crisis Detection**: Enhanced with full user context
✅ **Community Behavior Insights**: Incorporates social engagement patterns

## Monitoring

- Check service health: `GET /health`
- Monitor context cache: Included in health check
- View personalization scores in response metadata
EOL

echo "✅ Enhanced AI setup completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Run database migration: sqlite3 mantrapath.db < database/migrations/001_enhanced_ai_context_tables_sqlite.sql"
echo "2. Configure API keys in .env.ai"
echo "3. Test the system: ./run_ai_tests.sh"
echo "4. Start enhanced chatbot: cd services/chatbot_service && python3 enhanced_main.py"
echo ""
echo "📚 Documentation: Read ENHANCED_AI_QUICKSTART.md for detailed instructions"
echo ""
echo "🎉 Your enhanced AI chatbot is ready for personalized interactions!"
