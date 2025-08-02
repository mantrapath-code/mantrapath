# 🚀 MantraPath Enhanced AI - Quick Start Guide

## Prerequisites
1. MySQL database running
2. Python 3.8+ with required packages
3. OpenAI API key (optional but recommended)

## Setup Steps

### 1. Database Migration
```bash
cd backend
mysql -u root -p mantrapath < database/migrations/001_enhanced_ai_context_tables.sql
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
