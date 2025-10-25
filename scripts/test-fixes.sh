#!/bin/bash

# Test script to verify microphone access and emotion analysis fixes

echo "🧪 Testing MantraPath Fixes"
echo "=========================="

# Test 1: Check if frontend is running with HTTPS
echo "1. Testing HTTPS Frontend..."
if curl -k -s https://localhost:5173 > /dev/null; then
    echo "   ✅ Frontend running with HTTPS"
else
    echo "   ❌ Frontend not accessible via HTTPS"
fi

# Test 2: Check if mood service is working
echo "2. Testing Mood Service..."
MOOD_RESPONSE=$(curl -s -X POST http://localhost:8003/api/v1/mood/entries \
  -H "Content-Type: application/json" \
  -d '{
    "mood_data": {
      "input_text": "I am feeling great today!",
      "input_type": "text",
      "context_tags": ["test"]
    }
  }' 2>/dev/null)

if echo "$MOOD_RESPONSE" | jq -e '.mood_score' > /dev/null 2>&1; then
    echo "   ✅ Mood service working"
    echo "   📊 Response: $(echo "$MOOD_RESPONSE" | jq '.mood_score, .primary_emotion')"
else
    echo "   ❌ Mood service not working"
    echo "   📝 Response: $MOOD_RESPONSE"
fi

# Test 3: Check if AI Event Processor is accessible
echo "3. Testing AI Event Processor..."
AI_RESPONSE=$(curl -s -X POST http://localhost:8014/api/v1/analyze/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am feeling fantastic!",
    "user_id": "test",
    "language": "en"
  }' 2>/dev/null)

if echo "$AI_RESPONSE" | jq -e '.result' > /dev/null 2>&1; then
    echo "   ✅ AI Event Processor working"
    echo "   🧠 Emotion: $(echo "$AI_RESPONSE" | jq -r '.result.emotion')"
else
    echo "   ❌ AI Event Processor not working"
    echo "   📝 Response: $AI_RESPONSE"
fi

# Test 4: Check data persistence
echo "4. Testing Data Persistence..."
if [ -d "/home/sachin/mantrapath/data/postgres" ] && [ -d "/home/sachin/mantrapath/data/redis" ]; then
    echo "   ✅ Data directories exist"
    echo "   📁 PostgreSQL: $(du -sh /home/sachin/mantrapath/data/postgres 2>/dev/null | cut -f1)"
    echo "   📁 Redis: $(du -sh /home/sachin/mantrapath/data/redis 2>/dev/null | cut -f1)"
else
    echo "   ❌ Data directories missing"
fi

echo ""
echo "🎯 Summary:"
echo "   - Frontend: https://localhost:5173 (HTTPS enabled for microphone access)"
echo "   - Backend: http://localhost:8003 (Mood service)"
echo "   - AI Processor: http://localhost:8014 (Emotion analysis)"
echo "   - Data: /home/sachin/mantrapath/data/ (Persistent storage)"
echo ""
echo "🔧 To test microphone access:"
echo "   1. Open https://localhost:5173 in your browser"
echo "   2. Accept the security warning (self-signed certificate)"
echo "   3. Navigate to the mood page"
echo "   4. Try the voice recording feature"
echo ""
echo "📝 Note: You may need to accept the self-signed certificate in your browser"

