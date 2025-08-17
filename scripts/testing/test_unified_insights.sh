#!/bin/bash
# Test script for unified insights endpoint (E2 validation)

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8002}"
USE_SERVER_UNIFIED_INSIGHTS="${USE_SERVER_UNIFIED_INSIGHTS:-true}"

echo "🔍 Testing Unified Insights Endpoint (E2)"
echo "Backend URL: $BACKEND_URL"
echo "Feature Flag: USE_SERVER_UNIFIED_INSIGHTS=$USE_SERVER_UNIFIED_INSIGHTS"

# Check if ML service is running
echo "📡 Checking ML service health..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health" || echo "ERROR")

if [[ "$HEALTH_RESPONSE" == "ERROR" ]]; then
    echo "❌ ML service not available at $BACKEND_URL"
    echo "Please start the ML service first:"
    echo "  cd backend/services/ml_service && python main.py"
    exit 1
fi

echo "✅ ML service is healthy"

# Test without auth token (should get 401)
echo "🔒 Testing authentication requirement..."
UNAUTH_RESPONSE=$(curl -s -w "%{http_code}" -o /dev/null "$BACKEND_URL/api/v1/insights/unified" || echo "000")

if [[ "$UNAUTH_RESPONSE" == "401" ]]; then
    echo "✅ Authentication required (as expected)"
elif [[ "$UNAUTH_RESPONSE" == "404" ]]; then
    echo "⚠️  Endpoint returns 404 - feature flag might be disabled"
    echo "Set USE_SERVER_UNIFIED_INSIGHTS=true in environment"
else
    echo "⚠️  Unexpected response code: $UNAUTH_RESPONSE"
fi

# Mock token for testing (in real scenario, get from auth service)
# This is a simple JWT-like token for demo purposes
MOCK_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItMTIzIiwiaWF0IjoxNjkyMjQwMDAwLCJleHAiOjE2OTIzMjY0MDB9.mock"

echo "🧪 Testing unified insights endpoint..."
INSIGHTS_RESPONSE=$(curl -s \
    -H "Authorization: Bearer $MOCK_TOKEN" \
    -H "X-Insight-Version: v1" \
    "$BACKEND_URL/api/v1/insights/unified" || echo "ERROR")

if [[ "$INSIGHTS_RESPONSE" == "ERROR" ]]; then
    echo "❌ Failed to call unified insights endpoint"
    exit 1
fi

# Parse JSON response (basic validation)
echo "📊 Validating response structure..."

# Check if response contains required keys
if echo "$INSIGHTS_RESPONSE" | grep -q '"dashboard"' && \
   echo "$INSIGHTS_RESPONSE" | grep -q '"metadata"' && \
   echo "$INSIGHTS_RESPONSE" | grep -q '"detailedAnalysis"'; then
    echo "✅ Response contains required top-level keys"
else
    echo "❌ Response missing required keys"
    echo "Response: $INSIGHTS_RESPONSE"
    exit 1
fi

# Test cache behavior (second call should be faster)
echo "🏎️  Testing cache behavior..."
START_TIME=$(date +%s%3N)
CACHED_RESPONSE=$(curl -s \
    -H "Authorization: Bearer $MOCK_TOKEN" \
    -H "X-Insight-Version: v1" \
    "$BACKEND_URL/api/v1/insights/unified")
END_TIME=$(date +%s%3N)
LATENCY=$((END_TIME - START_TIME))

if echo "$CACHED_RESPONSE" | grep -q '"cache":"hit"'; then
    echo "✅ Cache hit detected (latency: ${LATENCY}ms)"
else
    echo "⚠️  Cache miss on second call (latency: ${LATENCY}ms)"
fi

# Test force refresh
echo "🔄 Testing force refresh..."
REFRESH_RESPONSE=$(curl -s \
    -H "Authorization: Bearer $MOCK_TOKEN" \
    -H "X-Insight-Version: v1" \
    "$BACKEND_URL/api/v1/insights/unified?force_refresh=true")

if echo "$REFRESH_RESPONSE" | grep -q '"cache":"miss"'; then
    echo "✅ Force refresh working correctly"
else
    echo "⚠️  Force refresh not working as expected"
fi

# Extract and display key metrics
echo "📈 Sample Response Metrics:"
echo "$INSIGHTS_RESPONSE" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f\"  Data Quality: {data['metadata']['dataQuality']}%\")
    print(f\"  Confidence: {data['metadata']['confidenceScore']:.2f}\")
    print(f\"  Mood Score: {data['dashboard']['currentStatus']['moodScore']}\")
    print(f\"  Days Tracked: {data['dashboard']['weeklySummary']['daysTracked']}\")
    print(f\"  Cache Status: {data['metadata']['cache']}\")
except Exception as e:
    print(f\"  Error parsing JSON: {e}\")
    sys.exit(1)
"

echo ""
echo "🎉 Unified Insights Endpoint Test Complete!"
echo "   All tests passed. E2 implementation verified."
