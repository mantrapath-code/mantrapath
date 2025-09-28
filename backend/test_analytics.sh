#!/bin/bash

# Test analytics endpoints
echo "=== Testing MantraPath Analytics Endpoints ==="

# Get auth token
echo "Getting authentication token..."
RESPONSE=$(curl -s http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email_or_username": "sa@gmail.com", "password": "Dev@#123"}')

TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Failed to get auth token"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Got auth token: ${TOKEN:0:50}..."

# Test analytics endpoints
endpoints=(
    "/api/v1/analytics/overview"
    "/api/v1/analytics/patterns/weekly"
    "/api/v1/analytics/emotions/trends"
    "/api/v1/analytics/insights"
    "/api/v1/analytics/wellbeing-score"
)

for endpoint in "${endpoints[@]}"; do
    echo ""
    echo "Testing: $endpoint"
    
    response=$(curl -s -w "%{http_code}" \
        -X GET "http://localhost:8000$endpoint" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        echo "✅ $endpoint - HTTP $http_code"
        # Pretty print JSON if it's valid
        if echo "$body" | jq . >/dev/null 2>&1; then
            echo "$body" | jq . | head -10
        else
            echo "$body" | head -5
        fi
    else
        echo "❌ $endpoint - HTTP $http_code"
        echo "Response: $body"
    fi
done

echo ""
echo "=== Test Complete ==="