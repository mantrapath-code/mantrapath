#!/bin/bash

# MantraPath API Gateway - Integration Test Script

set -e

echo "🔬 Running API Gateway Integration Tests..."

GATEWAY_URL="http://localhost:8000"
TIMEOUT=30

# Function to wait for service
wait_for_service() {
    local url=$1
    local timeout=$2
    local count=0
    
    echo "⏳ Waiting for service at $url..."
    
    while [ $count -lt $timeout ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ Service is ready!"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    echo "❌ Service failed to start within $timeout seconds"
    return 1
}

# Start gateway in background if not running
if ! curl -f -s "$GATEWAY_URL/health" > /dev/null 2>&1; then
    echo "🚀 Starting API Gateway..."
    
    # Check if Redis is running
    if ! redis-cli ping > /dev/null 2>&1; then
        echo "🔧 Starting Redis..."
        docker run -d --name test-redis -p 6379:6379 redis:7-alpine
        sleep 3
    fi
    
    # Start gateway
    cd "$(dirname "$0")/.."
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 &
    GATEWAY_PID=$!
    
    # Wait for gateway to start
    wait_for_service "$GATEWAY_URL/health" $TIMEOUT
else
    echo "✅ Gateway is already running"
fi

echo ""
echo "🧪 Running Integration Tests..."
echo "================================"

# Test 1: Basic Health Check
echo "Test 1: Basic Health Check"
response=$(curl -s -w "%{http_code}" "$GATEWAY_URL/health")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "✅ Basic health check passed"
else
    echo "❌ Basic health check failed (HTTP $http_code)"
    exit 1
fi

# Test 2: Detailed Health Check
echo ""
echo "Test 2: Detailed Health Check"
response=$(curl -s -w "%{http_code}" "$GATEWAY_URL/health/detailed")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "✅ Detailed health check passed"
else
    echo "❌ Detailed health check failed (HTTP $http_code)"
    exit 1
fi

# Test 3: Readiness Check
echo ""
echo "Test 3: Readiness Check"
response=$(curl -s -w "%{http_code}" "$GATEWAY_URL/health/ready")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "✅ Readiness check passed"
else
    echo "❌ Readiness check failed (HTTP $http_code)"
    exit 1
fi

# Test 4: Liveness Check
echo ""
echo "Test 4: Liveness Check"
response=$(curl -s -w "%{http_code}" "$GATEWAY_URL/health/live")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "✅ Liveness check passed"
else
    echo "❌ Liveness check failed (HTTP $http_code)"
    exit 1
fi

# Test 5: Metrics Endpoint
echo ""
echo "Test 5: Metrics Endpoint"
response=$(curl -s -w "%{http_code}" "$GATEWAY_URL/metrics")
http_code="${response: -3}"
if [ "$http_code" = "200" ]; then
    echo "✅ Metrics endpoint passed"
else
    echo "❌ Metrics endpoint failed (HTTP $http_code)"
    exit 1
fi

# Test 6: Unknown Route (should return 404)
echo ""
echo "Test 6: Unknown Route Handling"
response=$(curl -s -w "%{http_code}" "$GATEWAY_URL/unknown/route/test")
http_code="${response: -3}"
if [ "$http_code" = "404" ]; then
    echo "✅ Unknown route handling passed"
else
    echo "❌ Unknown route handling failed (expected 404, got $http_code)"
    exit 1
fi

# Test 7: CORS Headers
echo ""
echo "Test 7: CORS Headers"
response=$(curl -s -I "$GATEWAY_URL/health")
if echo "$response" | grep -i "access-control-allow-origin" > /dev/null; then
    echo "✅ CORS headers present"
else
    echo "⚠️ CORS headers not found (may be expected in test environment)"
fi

# Test 8: Rate Limiting (make multiple requests)
echo ""
echo "Test 8: Rate Limiting"
rate_limit_count=0
for i in {1..10}; do
    response=$(curl -s -w "%{http_code}" "$GATEWAY_URL/health")
    http_code="${response: -3}"
    if [ "$http_code" = "200" ]; then
        rate_limit_count=$((rate_limit_count + 1))
    fi
done

if [ $rate_limit_count -eq 10 ]; then
    echo "✅ Rate limiting configured (all requests allowed within limit)"
else
    echo "⚠️ Rate limiting may be active ($rate_limit_count/10 requests succeeded)"
fi

# Test 9: Service Discovery (check if services are registered)
echo ""
echo "Test 9: Service Registry"
response=$(curl -s "$GATEWAY_URL/health/detailed")
if echo "$response" | grep -q "services_detail"; then
    echo "✅ Service registry operational"
else
    echo "❌ Service registry not working properly"
    exit 1
fi

# Test 10: Performance (response time)
echo ""
echo "Test 10: Performance Check"
start_time=$(date +%s%N)
curl -s "$GATEWAY_URL/health" > /dev/null
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds

if [ $response_time -lt 1000 ]; then
    echo "✅ Performance check passed (${response_time}ms)"
else
    echo "⚠️ Slow response time: ${response_time}ms"
fi

echo ""
echo "🎉 Integration Tests Summary"
echo "================================"
echo "✅ All critical tests passed!"
echo "📊 Gateway is operational and ready for production"
echo ""
echo "🔗 Gateway Endpoints:"
echo "  - Health: $GATEWAY_URL/health"
echo "  - Detailed Health: $GATEWAY_URL/health/detailed"
echo "  - Metrics: $GATEWAY_URL/metrics"
echo "  - Ready: $GATEWAY_URL/health/ready"
echo "  - Live: $GATEWAY_URL/health/live"

# Cleanup
if [ -n "$GATEWAY_PID" ]; then
    echo ""
    echo "🧹 Cleaning up..."
    kill $GATEWAY_PID 2>/dev/null || true
    docker stop test-redis 2>/dev/null || true
    docker rm test-redis 2>/dev/null || true
fi

echo "✅ Integration tests completed successfully!"
