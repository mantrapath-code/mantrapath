#!/bin/bash

# Test Voice Service STT through API Gateway
# This script tests the complete flow that the frontend should be using

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MTlmZGY1Yi1hOWFmLTRlNmYtYTNiNC1iODY0MWQ0ZTQ0Y2QiLCJlbWFpbCI6InZvaWNldGVzdEBleGFtcGxlLmNvbSIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzU1MzQwMzY0LCJ0eXBlIjoiYWNjZXNzIn0.x3Z1Lh9jpuWKMbgzqQHvQP73yg9lYXMQFssEEQK2G64"

echo "Testing Voice Service STT through API Gateway..."
echo "================================================"

# Create a dummy audio file for testing
echo "Creating test audio file..."
echo "Hello world test audio" > /tmp/test_audio.txt

echo "Testing STT endpoint with authentication..."
curl -X POST http://localhost:8000/voice/stt \
  -H "Authorization: Bearer $TOKEN" \
  -F "audio=@/tmp/test_audio.txt;type=audio/wav" \
  -F "language=en" \
  -v

echo ""
echo "Test completed."

# Cleanup
rm -f /tmp/test_audio.txt
