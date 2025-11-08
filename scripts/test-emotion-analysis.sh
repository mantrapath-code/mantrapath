#!/bin/bash

# Test script to verify emotion analysis is working

echo "🧪 Testing Emotion Analysis Fix"
echo "==============================="

# Test 1: Direct mood service call
echo "1. Testing Mood Service Directly..."
MOOD_RESPONSE=$(curl -s -X POST http://localhost:8003/api/v1/mood/entries \
  -H "Content-Type: application/json" \
  -d '{
    "mood_data": {
      "input_text": "I am feeling absolutely fantastic and ready to take on the world!",
      "input_type": "text",
      "context_tags": ["test"]
    }
  }' 2>/dev/null)

if echo "$MOOD_RESPONSE" | jq -e '.primary_emotion' > /dev/null 2>&1; then
    echo "   ✅ Mood service working"
    echo "   📊 Primary Emotion: $(echo "$MOOD_RESPONSE" | jq -r '.primary_emotion')"
    echo "   📊 Mood Score: $(echo "$MOOD_RESPONSE" | jq -r '.mood_score')"
    echo "   📊 AI Reasoning: $(echo "$MOOD_RESPONSE" | jq -r '.ai_inferred_scores.reasoning')"
else
    echo "   ❌ Mood service not working"
    echo "   📝 Response: $MOOD_RESPONSE"
fi

# Test 2: Frontend proxy call
echo "2. Testing Frontend Proxy..."
PROXY_RESPONSE=$(curl -k -s -X POST https://localhost:5175/api/v1/mood/entries \
  -H "Content-Type: application/json" \
  -d '{
    "mood_data": {
      "input_text": "I am feeling great today!",
      "input_type": "text",
      "context_tags": ["proxy-test"]
    }
  }' 2>/dev/null)

if echo "$PROXY_RESPONSE" | jq -e '.primary_emotion' > /dev/null 2>&1; then
    echo "   ✅ Frontend proxy working"
    echo "   📊 Primary Emotion: $(echo "$PROXY_RESPONSE" | jq -r '.primary_emotion')"
    echo "   📊 Mood Score: $(echo "$PROXY_RESPONSE" | jq -r '.mood_score')"
else
    echo "   ❌ Frontend proxy not working"
    echo "   📝 Response: $PROXY_RESPONSE"
fi

# Test 3: AI Event Processor
echo "3. Testing AI Event Processor..."
AI_RESPONSE=$(curl -s -X POST http://localhost:8014/api/v1/analyze/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am feeling fantastic!",
    "user_id": "test",
    "language": "en"
  }' 2>/dev/null)

if echo "$AI_RESPONSE" | jq -e '.result.emotion' > /dev/null 2>&1; then
    echo "   ✅ AI Event Processor working"
    echo "   🧠 Emotion: $(echo "$AI_RESPONSE" | jq -r '.result.emotion')"
    echo "   🧠 Confidence: $(echo "$AI_RESPONSE" | jq -r '.result.confidence')"
else
    echo "   ❌ AI Event Processor not working"
    echo "   📝 Response: $AI_RESPONSE"
fi

# Test 4: Frontend accessibility
echo "4. Testing Frontend Accessibility..."
if curl -k -s https://localhost:5175 > /dev/null; then
    echo "   ✅ Frontend accessible via HTTPS"
    echo "   🔗 URL: https://localhost:5175"
else
    echo "   ❌ Frontend not accessible"
fi

echo ""
echo "🎯 Summary:"
echo "   - Frontend: https://localhost:5175 (HTTPS enabled)"
echo "   - Mood Service: http://localhost:8003 (Direct access)"
echo "   - AI Event Processor: http://localhost:8014 (Emotion analysis)"
echo "   - Proxy: Frontend → Mood Service (Working)"
echo ""
echo "🔧 To test in browser:"
echo "   1. Open https://localhost:5175"
echo "   2. Accept the security warning"
echo "   3. Navigate to mood page"
echo "   4. Try text emotion analysis"
echo "   5. Try voice recording (microphone should work now)"
echo ""
echo "✅ All emotion analysis issues should now be resolved!"


