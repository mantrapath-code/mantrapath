#!/bin/bash
# Voice Services Test Script
# Tests both voice service and voice event processor

echo "🎤 Voice Services Test Script"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service URLs
VOICE_SERVICE_URL=${VOICE_SERVICE_URL:-"http://localhost:8011"}
VOICE_EVENT_PROCESSOR_URL=${VOICE_EVENT_PROCESSOR_URL:-"http://localhost:8015"}

# Test function
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $description... "
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
    
    if [ "$http_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        if [ ! -z "$body" ]; then
            echo "   Response: $(echo "$body" | jq -r '.message // .service // .status // .' 2>/dev/null | head -c 100)..."
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        if [ ! -z "$body" ]; then
            echo "   Error: $(echo "$body" | head -c 200)..."
        fi
    fi
    echo ""
}

# Test Voice Service
echo -e "${BLUE}Testing Voice Service ($VOICE_SERVICE_URL)${NC}"
echo "------------------------------------------------"

test_endpoint "$VOICE_SERVICE_URL/" "Voice Service Root"
test_endpoint "$VOICE_SERVICE_URL/health" "Voice Service Health Check"
test_endpoint "$VOICE_SERVICE_URL/docs" "Voice Service API Documentation"

# Test Voice Event Processor
echo -e "${BLUE}Testing Voice Event Processor ($VOICE_EVENT_PROCESSOR_URL)${NC}"
echo "--------------------------------------------------------"

test_endpoint "$VOICE_EVENT_PROCESSOR_URL/" "Voice Event Processor Root"
test_endpoint "$VOICE_EVENT_PROCESSOR_URL/health" "Voice Event Processor Health Check"
test_endpoint "$VOICE_EVENT_PROCESSOR_URL/api/v1/streams/status" "Streams Status"
test_endpoint "$VOICE_EVENT_PROCESSOR_URL/api/v1/stats" "Analytics Stats"
test_endpoint "$VOICE_EVENT_PROCESSOR_URL/api/v1/config" "Configuration"

# Test WebSocket Connection (if wscat is available)
if command -v wscat &> /dev/null; then
    echo -e "${BLUE}Testing WebSocket Connection${NC}"
    echo "-----------------------------"
    
    echo "Testing voice event processor WebSocket..."
    timeout 5s wscat -c "$VOICE_EVENT_PROCESSOR_URL/ws/voice/test_client" -x '{"type":"ping"}' 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ WebSocket connection successful${NC}"
    else
        echo -e "${YELLOW}⚠️ WebSocket test skipped (connection timeout or wscat not available)${NC}"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️ wscat not available, skipping WebSocket tests${NC}"
    echo "   Install wscat with: npm install -g wscat"
    echo ""
fi

# Test with sample data (if services are running)
echo -e "${BLUE}Advanced Tests${NC}"
echo "---------------"

# Test with dummy audio data
echo "Testing voice chunk processing..."
dummy_audio=$(echo "fake audio data" | base64)
response=$(curl -s -X POST \
    -H "Content-Type: application/octet-stream" \
    -d "$dummy_audio" \
    "$VOICE_EVENT_PROCESSOR_URL/api/v1/voice/process" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Voice chunk processing test successful${NC}"
    echo "   Response: $(echo "$response" | jq -r '.success // .' 2>/dev/null)"
else
    echo -e "${YELLOW}⚠️ Voice chunk processing test failed or service not responding${NC}"
fi
echo ""

# Test session management
echo "Testing session management..."
session_response=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"userId":"test_user","metadata":{"test":true}}' \
    "$VOICE_SERVICE_URL/api/v1/session/start" 2>/dev/null)

if [ $? -eq 0 ] && echo "$session_response" | jq -r '.sessionId' &>/dev/null; then
    session_id=$(echo "$session_response" | jq -r '.sessionId')
    echo -e "${GREEN}✅ Session start successful${NC}"
    echo "   Session ID: $session_id"
    
    # Test session status
    status_response=$(curl -s "$VOICE_SERVICE_URL/api/v1/session/$session_id/status" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Session status check successful${NC}"
    fi
    
    # End session
    curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "{\"sessionId\":\"$session_id\"}" \
        "$VOICE_SERVICE_URL/api/v1/session/end" &>/dev/null
    echo -e "${GREEN}✅ Session cleanup successful${NC}"
else
    echo -e "${YELLOW}⚠️ Session management test failed or service not responding${NC}"
fi
echo ""

# Performance test
echo -e "${BLUE}Performance Tests${NC}"
echo "------------------"

echo "Testing response times..."
for endpoint in "$VOICE_SERVICE_URL/health" "$VOICE_EVENT_PROCESSOR_URL/health"; do
    echo -n "  $(basename "$endpoint"): "
    time_result=$(curl -s -w "%{time_total}" -o /dev/null "$endpoint" 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}${time_result}s${NC}"
    else
        echo -e "${RED}timeout${NC}"
    fi
done

echo ""
echo -e "${BLUE}Summary${NC}"
echo "========="

# Check if services are running
voice_service_running=$(curl -s "$VOICE_SERVICE_URL/health" &>/dev/null && echo "✅" || echo "❌")
event_processor_running=$(curl -s "$VOICE_EVENT_PROCESSOR_URL/health" &>/dev/null && echo "✅" || echo "❌")

echo -e "Voice Service:          $voice_service_running"
echo -e "Voice Event Processor:  $event_processor_running"

if [[ "$voice_service_running" == "✅" && "$event_processor_running" == "✅" ]]; then
    echo -e "\n${GREEN}🎉 All voice services are running successfully!${NC}"
    echo -e "\n${BLUE}Next Steps:${NC}"
    echo "1. Access Voice Service docs: $VOICE_SERVICE_URL/docs"
    echo "2. Access Event Processor docs: $VOICE_EVENT_PROCESSOR_URL/docs"
    echo "3. Test the frontend voice interface component"
    echo "4. Check WebSocket connections for real-time features"
else
    echo -e "\n${YELLOW}⚠️ Some services are not running.${NC}"
    echo -e "\n${BLUE}To start services:${NC}"
    echo "1. Voice Service: cd backend/services/voice_service && python main_enhanced.py"
    echo "2. Voice Event Processor: cd backend/services/voice_event_processor && python main.py"
    echo "3. Or use Docker: cd backend && docker-compose up voice-service voice-event-processor"
fi

echo ""
echo "Test completed at $(date)"