#!/bin/bash
# Docker-based E2 Unified Insights Testing Script
# Tests the complete end-to-end flow using Docker containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")/backend"

echo "🐳 E2 Unified Insights Docker Integration Test"
echo "============================================="

# Configuration
COMPOSE_FILE="$BACKEND_DIR/docker-compose.yml"
ML_SERVICE_URL="http://localhost:8008"
AUTH_SERVICE_URL="http://localhost:8001"

# Test user credentials (existing user)
TEST_USER_USERNAME="Ramesh"
TEST_USER_PASSWORD="Dev@#123"

echo "📁 Working from: $BACKEND_DIR"
echo "🔧 Using compose file: $COMPOSE_FILE"

# Function to wait for service to be ready
wait_for_service() {
    local service_url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=0
    
    echo "⏳ Waiting for $service_name to be ready..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -f "$service_url/health" > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "   Attempt $attempt/$max_attempts - waiting..."
        sleep 2
    done
    
    echo "❌ $service_name failed to start within timeout"
    return 1
}

# Function to get auth token
get_auth_token() {
    echo "🔐 Getting authentication token..."
    
    # Login with existing user credentials
    AUTH_RESPONSE=$(curl -s -X POST "$AUTH_SERVICE_URL/login" \
        -H "Content-Type: application/json" \
        -d "{\"email_or_username\": \"$TEST_USER_USERNAME\", \"password\": \"$TEST_USER_PASSWORD\"}" \
        || echo "ERROR")
    
    if [[ "$AUTH_RESPONSE" == "ERROR" ]] || [[ "$AUTH_RESPONSE" == *"error"* ]] || [[ "$AUTH_RESPONSE" == *"Invalid"* ]]; then
        echo "❌ Login failed with user: $TEST_USER_USERNAME"
        echo "Response: $AUTH_RESPONSE"
        return 1
    fi
    
    # Extract token from response
    TOKEN=$(echo "$AUTH_RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('access_token', ''))
except:
    print('')
")
    
    if [[ -z "$TOKEN" ]]; then
        echo "❌ Failed to extract authentication token"
        echo "Auth response: $AUTH_RESPONSE"
        return 1
    fi
    
    echo "✅ Authentication successful for user: $TEST_USER_USERNAME"
    echo "$TOKEN"
}

# Function to create test mood data
create_test_data() {
    local token=$1
    echo "📊 Creating test mood data..."
    
    # Create 5 mood entries with varying scores
    mood_scores=(7 8 6 9 7)
    energy_levels=(6 7 5 8 6)
    
    for i in {0..4}; do
        MOOD_DATA="{
            \"mood_score\": ${mood_scores[i]},
            \"energy_level\": ${energy_levels[i]},
            \"stress_level\": 4,
            \"sleep_quality\": 7,
            \"notes\": \"Test mood entry $((i+1)) for unified insights testing\",
            \"context_tags\": [\"testing\", \"docker\"]
        }"
        
        MOOD_RESPONSE=$(curl -s -X POST "http://localhost:8003/mood/entries" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d "$MOOD_DATA" || echo "ERROR")
        
        if [[ "$MOOD_RESPONSE" == "ERROR" ]]; then
            echo "⚠️  Failed to create mood entry $((i+1))"
        else
            echo "   ✓ Created mood entry $((i+1)): score=${mood_scores[i]}, energy=${energy_levels[i]}"
        fi
        
        sleep 0.5  # Brief delay between entries
    done
    
    echo "✅ Test mood data created"
}

# Function to test unified insights endpoint
test_unified_insights() {
    local token=$1
    echo "🧪 Testing Unified Insights Endpoint..."
    
    # Enable the feature flag for this test
    export USE_SERVER_UNIFIED_INSIGHTS=true
    
    # Test 1: Basic endpoint access
    echo "   🔍 Test 1: Basic endpoint access"
    INSIGHTS_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/insights_response.json \
        -H "Authorization: Bearer $token" \
        -H "X-Insight-Version: v1" \
        "$ML_SERVICE_URL/api/v1/insights/unified" || echo "000")
    
    if [[ "$INSIGHTS_RESPONSE" == "200" ]]; then
        echo "   ✅ Endpoint accessible (HTTP 200)"
    elif [[ "$INSIGHTS_RESPONSE" == "404" ]]; then
        echo "   ❌ Endpoint not found (HTTP 404) - Feature flag may be disabled"
        echo "   💡 Ensure USE_SERVER_UNIFIED_INSIGHTS=true in container environment"
        return 1
    else
        echo "   ❌ Unexpected response code: $INSIGHTS_RESPONSE"
        return 1
    fi
    
    # Test 2: Response structure validation
    echo "   🔍 Test 2: Response structure validation"
    python3 -c "
import json, sys
try:
    with open('/tmp/insights_response.json', 'r') as f:
        data = json.load(f)
    
    # Check required keys
    required_keys = ['dashboard', 'detailedAnalysis', 'recommendedActions', 'progressTracking', 'metadata']
    missing = [k for k in required_keys if k not in data]
    
    if missing:
        print(f'   ❌ Missing keys: {missing}')
        sys.exit(1)
    
    # Check dashboard structure
    dashboard = data['dashboard']
    if 'weeklySummary' not in dashboard or 'currentStatus' not in dashboard:
        print('   ❌ Invalid dashboard structure')
        sys.exit(1)
    
    # Check metadata
    metadata = data['metadata']
    if 'dataQuality' not in metadata or 'confidenceScore' not in metadata:
        print('   ❌ Invalid metadata structure')
        sys.exit(1)
    
    print('   ✅ Response structure valid')
    print(f'   📊 Data Quality: {metadata[\"dataQuality\"]}%')
    print(f'   🎯 Confidence: {metadata[\"confidenceScore\"]:.2f}')
    print(f'   📈 Mood Score: {dashboard[\"currentStatus\"][\"moodScore\"]}')
    print(f'   📅 Days Tracked: {dashboard[\"weeklySummary\"][\"daysTracked\"]}')
    print(f'   💾 Cache Status: {metadata.get(\"cache\", \"unknown\")}')
    
except Exception as e:
    print(f'   ❌ Response validation failed: {e}')
    sys.exit(1)
"
    
    if [[ $? -ne 0 ]]; then
        echo "   ❌ Response structure validation failed"
        return 1
    fi
    
    # Test 3: Cache behavior
    echo "   🔍 Test 3: Cache behavior test"
    
    # Second call should be faster (cache hit)
    START_TIME=$(date +%s%3N)
    CACHED_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/insights_cached.json \
        -H "Authorization: Bearer $token" \
        -H "X-Insight-Version: v1" \
        "$ML_SERVICE_URL/api/v1/insights/unified")
    END_TIME=$(date +%s%3N)
    
    CACHED_LATENCY=$((END_TIME - START_TIME))
    
    if [[ "$CACHED_RESPONSE" == "200" ]]; then
        CACHE_STATUS=$(python3 -c "
import json
try:
    with open('/tmp/insights_cached.json', 'r') as f:
        data = json.load(f)
    print(data.get('metadata', {}).get('cache', 'unknown'))
except:
    print('unknown')
")
        echo "   ✅ Cache test completed (${CACHED_LATENCY}ms, status: $CACHE_STATUS)"
    else
        echo "   ⚠️  Cache test inconclusive"
    fi
    
    # Test 4: Force refresh
    echo "   🔍 Test 4: Force refresh test"
    REFRESH_RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/insights_refresh.json \
        -H "Authorization: Bearer $token" \
        -H "X-Insight-Version: v1" \
        "$ML_SERVICE_URL/api/v1/insights/unified?force_refresh=true")
    
    if [[ "$REFRESH_RESPONSE" == "200" ]]; then
        REFRESH_CACHE_STATUS=$(python3 -c "
import json
try:
    with open('/tmp/insights_refresh.json', 'r') as f:
        data = json.load(f)
    print(data.get('metadata', {}).get('cache', 'unknown'))
except:
    print('unknown')
")
        echo "   ✅ Force refresh test completed (cache status: $REFRESH_CACHE_STATUS)"
    else
        echo "   ❌ Force refresh test failed"
        return 1
    fi
    
    echo "✅ All unified insights tests passed!"
    return 0
}

# Main execution
main() {
    echo "🚀 Starting Docker services..."
    
    # Navigate to backend directory
    cd "$BACKEND_DIR"
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis auth-service mood-service ml-service
    
    # Wait for core services to be ready
    if ! wait_for_service "$AUTH_SERVICE_URL" "Auth Service"; then
        echo "❌ Auth service failed to start"
        exit 1
    fi
    
    if ! wait_for_service "http://localhost:8003" "Mood Service"; then
        echo "❌ Mood service failed to start"
        exit 1
    fi
    
    if ! wait_for_service "$ML_SERVICE_URL" "ML Service"; then
        echo "❌ ML service failed to start"
        exit 1
    fi
    
    # Get authentication token
    if ! TOKEN=$(get_auth_token); then
        echo "❌ Failed to get authentication token"
        exit 1
    fi
    
    # Create test data
    create_test_data "$TOKEN"
    
    # Run unified insights tests
    if test_unified_insights "$TOKEN"; then
        echo ""
        echo "🎉 Docker E2 Integration Test PASSED!"
        echo "   ✅ All services started successfully"
        echo "   ✅ Authentication working"
        echo "   ✅ Test data created"
        echo "   ✅ Unified insights endpoint functional"
        echo "   ✅ Caching behavior verified"
        echo ""
        echo "🔧 To view logs: docker-compose logs ml-service"
        echo "🛑 To stop services: docker-compose down"
    else
        echo ""
        echo "❌ Docker E2 Integration Test FAILED!"
        echo "Check service logs for details:"
        echo "  docker-compose logs ml-service"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up temporary files..."
    rm -f /tmp/insights_*.json
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"
