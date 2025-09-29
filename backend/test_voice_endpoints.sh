#!/bin/bash

# End-to-end test script for voice service endpoints
echo "🎤 Testing Voice Service Endpoints Through API Gateway"

BASE_URL="http://localhost:8000"
VOICE_SERVICE_URL="http://localhost:8011"

echo ""
echo "1. Testing API Gateway Health"
curl -s "$BASE_URL/health" | jq .

echo ""
echo "2. Testing Voice Service Health (direct)"
curl -s "$VOICE_SERVICE_URL/health" | jq .

echo ""
echo "3. Testing Session Start (frontend compatibility endpoint)"
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/session/start" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "language": "en"}')
echo "$SESSION_RESPONSE" | jq .

echo ""
echo "4. Testing Text-to-Speech (legacy endpoint)"
curl -s -X POST "$BASE_URL/api/v1/voice/text-to-speech" \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing MantraPath voice service", "language": "en"}' \
  --output /tmp/test_tts_legacy.wav --max-time 15

if [ -f "/tmp/test_tts_legacy.wav" ]; then
  FILESIZE=$(wc -c < /tmp/test_tts_legacy.wav)
  echo "✅ TTS Legacy endpoint: Generated audio file ($FILESIZE bytes)"
  file /tmp/test_tts_legacy.wav
else
  echo "❌ TTS Legacy endpoint: Failed to generate audio"
fi

echo ""
echo "5. Testing Text-to-Speech (regular endpoint)"
curl -s -X POST "$BASE_URL/api/v1/voice/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "Testing MantraPath voice service", "language": "en"}' \
  --output /tmp/test_tts_regular.wav --max-time 15

if [ -f "/tmp/test_tts_regular.wav" ]; then
  FILESIZE=$(wc -c < /tmp/test_tts_regular.wav)
  echo "✅ TTS Regular endpoint: Generated audio file ($FILESIZE bytes)"
  file /tmp/test_tts_regular.wav
else
  echo "❌ TTS Regular endpoint: Failed to generate audio"
fi

echo ""
echo "6. Testing Voice Service Status"
curl -s "$BASE_URL/api/v1/voice/status" | jq .

echo ""
echo "7. Testing Chatbot Session (should require auth)"
curl -s -X POST "$BASE_URL/api/chatbot/chat/session" \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

echo ""
echo "🎯 Voice Service End-to-End Test Complete!"
echo ""
echo "Summary of fixes applied:"
echo "✅ Added /api/v1/session/start endpoint for frontend compatibility"
echo "✅ Added /api/v1/voice/text-to-speech legacy endpoint"
echo "✅ Fixed API Gateway routing for /api/v1/voice/* and /api/v1/session/*"
echo "✅ Removed auth requirement for voice endpoints"
echo "✅ Fixed proxy response handling to return proper FastAPI responses"
echo "✅ Added streaming support for large audio files"
echo "✅ Chatbot endpoints still require auth (as designed)"