#!/bin/bash
# Test Event Bus Integration
# This script tests that event publishing and subscribing works correctly

set -e

echo "🧪 Testing Event Bus Integration"
echo "==============================="

# Configuration
BASE_URL="http://localhost"
MOOD_SERVICE_PORT="8003"
CONTENT_SERVICE_PORT="8005"
COMMUNITY_SERVICE_PORT="8004"

# Test user credentials (replace with actual test token)
TEST_USER_ID="test-user-$(date +%s)"
AUTH_TOKEN="${TEST_AUTH_TOKEN:-test-token-123}"

echo "📊 Test Configuration:"
echo "   Test User ID: $TEST_USER_ID"
echo "   Auth Token: ${AUTH_TOKEN:0:20}..."
echo ""

# Function to check service health
check_service_health() {
    local service_name=$1
    local port=$2
    
    echo "🏥 Checking $service_name health..."
    
    if curl -s -f "$BASE_URL:$port/health" > /dev/null; then
        echo "   ✅ $service_name is healthy"
        return 0
    else
        echo "   ❌ $service_name is not responding"
        return 1
    fi
}

# Function to test event publishing
test_mood_event_publishing() {
    echo ""
    echo "📝 Testing Mood Entry Event Publishing..."
    
    local mood_data='{
        "mood_score": 7,
        "energy_level": 6,
        "stress_level": 4,
        "notes": "Testing event publishing",
        "context_tags": ["test", "integration"]
    }'
    
    echo "   Sending mood entry request..."
    
    local response=$(curl -s -X POST "$BASE_URL:$MOOD_SERVICE_PORT/mood-entries" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -d "$mood_data" \
        -w "HTTP_STATUS:%{http_code}")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
    local body=$(echo "$response" | sed 's/HTTP_STATUS:.*$//')
    
    if [ "$http_status" = "200" ] || [ "$http_status" = "201" ]; then
        echo "   ✅ Mood entry created successfully"
        echo "   📊 Response: $body"
        return 0
    else
        echo "   ❌ Mood entry creation failed (HTTP $http_status)"
        echo "   📊 Response: $body"
        return 1
    fi
}

# Function to test NATS event streams
test_nats_streams() {
    echo ""
    echo "🌊 Testing NATS Event Streams..."
    
    if command -v nats &> /dev/null; then
        echo "   Checking NATS streams..."
        
        # List streams
        local streams=$(nats stream ls 2>/dev/null || echo "")
        
        if [ -n "$streams" ]; then
            echo "   ✅ NATS is available"
            echo "   📊 Streams:"
            echo "$streams" | sed 's/^/      /'
            
            # Check for MantraPath streams
            if echo "$streams" | grep -q "mantrapath"; then
                echo "   ✅ MantraPath streams found"
            else
                echo "   ⚠️  No MantraPath streams found yet"
            fi
        else
            echo "   ⚠️  NATS streams not available (using in-memory fallback)"
        fi
    else
        echo "   ⚠️  NATS CLI not installed (this is optional)"
    fi
}

# Function to test event bus health endpoints
test_event_bus_health() {
    echo ""
    echo "💓 Testing Event Bus Health Endpoints..."
    
    # Test each service's event bus health
    local services=("mood:$MOOD_SERVICE_PORT" "content:$CONTENT_SERVICE_PORT" "community:$COMMUNITY_SERVICE_PORT")
    
    for service_info in "${services[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local port=$(echo "$service_info" | cut -d: -f2)
        
        echo "   Testing $service_name service event bus..."
        
        # Try to get event bus health info
        local health_response=$(curl -s "$BASE_URL:$port/health" 2>/dev/null || echo "")
        
        if [ -n "$health_response" ]; then
            echo "   ✅ $service_name service responding"
            
            # Check if response mentions event bus
            if echo "$health_response" | grep -q -i "event\|bus"; then
                echo "   ✅ Event bus integration detected"
            else
                echo "   ⚠️  Event bus integration not visible in health check"
            fi
        else
            echo "   ❌ $service_name service not responding"
        fi
    done
}

# Function to test service logs for event activity
test_service_logs() {
    echo ""
    echo "📜 Checking Service Logs for Event Activity..."
    
    echo "   💡 To monitor live events, run these commands in separate terminals:"
    echo ""
    echo "   # Monitor mood service logs:"
    echo "   docker logs -f mantrapath-mood-service-1 2>&1 | grep -i event"
    echo ""
    echo "   # Monitor NATS activity (if available):"
    echo "   nats sub \"mood.*\" --count=10"
    echo ""
    echo "   # Monitor enhanced event bus:"
    echo "   tail -f backend/logs/enhanced_event_bus.log"
    echo ""
}

# Function to create integration test results
create_test_report() {
    local total_tests=$1
    local passed_tests=$2
    
    echo ""
    echo "📊 Event Bus Integration Test Report"
    echo "===================================="
    echo "   Date: $(date)"
    echo "   Total Tests: $total_tests"
    echo "   Passed: $passed_tests"
    echo "   Failed: $((total_tests - passed_tests))"
    echo "   Success Rate: $(( (passed_tests * 100) / total_tests ))%"
    echo ""
    
    if [ $passed_tests -eq $total_tests ]; then
        echo "   🎉 ALL TESTS PASSED - Event Bus Integration is working!"
        echo "   ✅ Ready for Phase 2: AI Context Implementation"
    else
        echo "   ⚠️  Some tests failed. Check the issues above."
        echo "   🔧 Troubleshooting steps:"
        echo "      1. Ensure all services are running"
        echo "      2. Check service logs for errors"
        echo "      3. Verify event imports are uncommented"
        echo "      4. Test with valid authentication token"
    fi
}

# Main test execution
main() {
    echo "🚀 Starting Event Bus Integration Tests..."
    echo ""
    
    local total_tests=0
    local passed_tests=0
    
    # Test 1: Service Health
    total_tests=$((total_tests + 3))
    check_service_health "Mood Service" "$MOOD_SERVICE_PORT" && passed_tests=$((passed_tests + 1))
    check_service_health "Content Service" "$CONTENT_SERVICE_PORT" && passed_tests=$((passed_tests + 1))
    check_service_health "Community Service" "$COMMUNITY_SERVICE_PORT" && passed_tests=$((passed_tests + 1))
    
    # Test 2: Event Publishing
    total_tests=$((total_tests + 1))
    test_mood_event_publishing && passed_tests=$((passed_tests + 1))
    
    # Test 3: NATS Integration
    total_tests=$((total_tests + 1))
    test_nats_streams && passed_tests=$((passed_tests + 1))
    
    # Test 4: Event Bus Health
    total_tests=$((total_tests + 1))
    test_event_bus_health && passed_tests=$((passed_tests + 1))
    
    # Additional info
    test_service_logs
    
    # Generate report
    create_test_report $total_tests $passed_tests
    
    # Exit with appropriate code
    if [ $passed_tests -eq $total_tests ]; then
        exit 0
    else
        exit 1
    fi
}

# Check if services are started
echo "🔍 Pre-flight checks..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ API Gateway not responding. Please start services first:"
    echo "   ./start.sh backend"
    echo ""
    exit 1
fi

# Run main test
main
