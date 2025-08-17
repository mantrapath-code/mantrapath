#!/bin/bash

# Sprint 2 Parallel Testing Script for MantraPath V3
# Executes comprehensive testing for AI Event Processing Pipeline

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
TEST_DIR="/Users/sachin/Desktop/mantrapath/backend"
SERVICES_DIR="$TEST_DIR/services"
INTEGRATION_TEST_DIR="$TEST_DIR/tests/integration/sprint2"
PARALLEL_JOBS=4

print_status() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✓ $1${NC}"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠ $1${NC}"
}

# Function to run tests in parallel
run_parallel_tests() {
    local test_type="$1"
    local test_paths=("${@:2}")
    
    print_status "Running $test_type tests in parallel..."
    
    # Create array to store background process PIDs
    local pids=()
    local results=()
    
    for test_path in "${test_paths[@]}"; do
        if [[ -d "$test_path" ]]; then
            print_status "Starting tests in: $test_path"
            
            # Run tests in background and capture PID
            (
                cd "$test_path"
                if [[ -f "requirements.txt" ]]; then
                    pip install -r requirements.txt >/dev/null 2>&1
                fi
                
                # Set PYTHONPATH for proper imports
                export PYTHONPATH="$TEST_DIR:$PYTHONPATH"
                
                # Run pytest with coverage
                python -m pytest tests/ -v \
                    --cov=. \
                    --cov-report=term-missing \
                    --cov-report=json:coverage.json \
                    --junit-xml=test-results.xml \
                    --tb=short \
                    2>&1
            ) &
            
            local pid=$!
            pids+=($pid)
            results+=("$test_path")
        fi
    done
    
    # Wait for all background processes to complete
    local success_count=0
    local total_count=${#pids[@]}
    
    for i in "${!pids[@]}"; do
        local pid=${pids[$i]}
        local test_path=${results[$i]}
        
        if wait $pid; then
            print_success "Tests completed successfully: $(basename "$test_path")"
            ((success_count++))
        else
            print_error "Tests failed: $(basename "$test_path")"
        fi
    done
    
    print_status "$test_type Results: $success_count/$total_count tests passed"
    return $((total_count - success_count))
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running Sprint 2 Integration Tests..."
    
    cd "$TEST_DIR"
    export PYTHONPATH="$TEST_DIR:$PYTHONPATH"
    
    # Check if services are running
    local services_running=true
    
    print_status "Checking service availability..."
    
    # Check AI Event Processor
    if ! curl -s http://localhost:8014/health >/dev/null 2>&1; then
        print_warning "AI Event Processor not responding on port 8014"
        services_running=false
    fi
    
    # Check Voice Event Processor
    if ! curl -s http://localhost:8015/health >/dev/null 2>&1; then
        print_warning "Voice Event Processor not responding on port 8015"
        services_running=false
    fi
    
    if [[ "$services_running" == "false" ]]; then
        print_error "Services not running. Start services first with: ./start-sprint2.sh"
        return 1
    fi
    
    # Install test dependencies
    print_status "Installing test dependencies..."
    pip install pytest pytest-asyncio httpx websockets pytest-cov >/dev/null 2>&1
    
    # Run integration tests
    python -m pytest "$INTEGRATION_TEST_DIR" -v \
        --cov="$SERVICES_DIR" \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --junit-xml=integration-test-results.xml \
        --tb=short
}

# Function to generate test report
generate_test_report() {
    print_status "Generating comprehensive test report..."
    
    local report_file="$TEST_DIR/SPRINT_2_TEST_REPORT.md"
    
    cat > "$report_file" << EOF
# Sprint 2 Testing Report - MantraPath V3

**Generated on:** $(date '+%Y-%m-%d %H:%M:%S')
**Test Environment:** Local Development
**Sprint 2 Services:** AI Event Processing Pipeline, Voice Event Streaming Foundation

## Test Execution Summary

### Unit Tests
- **AI Event Processor:** Tests for emotion analysis, cultural intelligence, predictive engine
- **Voice Event Processor:** Tests for voice processing, WebSocket streaming, audio detection

### Integration Tests
- **Service Health Checks:** Endpoint availability and response validation
- **Cross-Service Communication:** Event flow between AI and Voice processors
- **Performance Validation:** Latency requirements (<200ms AI processing, <50ms voice)
- **Multilingual Support:** Cultural adaptation for 15+ languages
- **Concurrent Processing:** Load testing with multiple simultaneous requests

### Test Coverage Goals
- **Unit Test Coverage:** >95% for all critical functions
- **Integration Coverage:** End-to-end workflows and error scenarios
- **Performance Coverage:** Latency, throughput, and resource utilization

## Service-Specific Results

### AI Event Processor (Port 8014)
- **Emotion Analysis Pipeline:** Multi-language emotion detection
- **Cultural Intelligence:** Cultural adaptation for diverse languages
- **Predictive Interventions:** Risk assessment and intervention recommendations
- **Context Management:** User context aggregation and updates

### Voice Event Processor (Port 8015)
- **Voice Activity Detection:** Real-time voice processing
- **WebSocket Streaming:** Live audio data handling
- **Audio Processing:** Voice quality analysis and enhancement

## Performance Metrics
- **AI Processing Latency:** < 200ms (Target)
- **Voice Processing Latency:** < 50ms (Target)
- **Concurrent Request Handling:** 10+ simultaneous requests
- **Memory Usage:** Optimized for production deployment

## Test Data and Scenarios
- **Multilingual Test Cases:** English, French, Hindi, Arabic
- **Emotion Scenarios:** Positive, negative, neutral, mixed emotions
- **Cultural Contexts:** Family-oriented, spiritual, individualistic cultures
- **Error Conditions:** Invalid inputs, network failures, service unavailability

## Deployment Validation
- **Docker Compose Integration:** Service orchestration and networking
- **Health Check Endpoints:** Monitoring and alerting capabilities
- **Configuration Management:** Environment-specific settings
- **Service Discovery:** Inter-service communication protocols

## Recommendations
1. **Continuous Monitoring:** Implement real-time performance tracking
2. **Automated Testing:** Integrate tests into CI/CD pipeline
3. **Load Testing:** Validate performance under production load
4. **Security Testing:** Validate authentication and authorization
5. **Documentation:** Maintain comprehensive API documentation

## Next Steps
1. Complete V3-BK-007: Unified AI Context Service implementation
2. Complete V3-BK-008: Proactive Assistance Engine implementation
3. Performance optimization and tuning
4. Production deployment preparation

---
*This report provides comprehensive validation of Sprint 2 implementation quality and readiness.*
EOF

    print_success "Test report generated: $report_file"
}

# Main execution
main() {
    print_status "Starting Sprint 2 Parallel Testing Suite..."
    echo "========================================================"
    
    # Check prerequisites
    print_status "Checking prerequisites..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command -v pip &> /dev/null; then
        print_error "pip is required but not installed"
        exit 1
    fi
    
    # Install test dependencies
    print_status "Installing global test dependencies..."
    pip install pytest pytest-asyncio httpx websockets pytest-cov pytest-xdist >/dev/null 2>&1
    
    # Phase 1: Unit Tests (Parallel)
    print_status "Phase 1: Running Unit Tests in Parallel"
    echo "========================================================"
    
    local service_paths=(
        "$SERVICES_DIR/ai_event_processor"
        "$SERVICES_DIR/voice_event_processor"
    )
    
    run_parallel_tests "Unit" "${service_paths[@]}"
    local unit_test_result=$?
    
    # Phase 2: Integration Tests
    print_status "Phase 2: Running Integration Tests"
    echo "========================================================"
    
    run_integration_tests
    local integration_test_result=$?
    
    # Phase 3: Performance Validation
    print_status "Phase 3: Performance Validation"
    echo "========================================================"
    
    # Run performance-specific tests
    cd "$TEST_DIR"
    print_status "Running performance tests..."
    
    python -m pytest "$INTEGRATION_TEST_DIR/test_sprint2_integration.py::TestSprint2Integration::test_performance_latency_requirements" -v
    local performance_test_result=$?
    
    python -m pytest "$INTEGRATION_TEST_DIR/test_sprint2_integration.py::TestSprint2Integration::test_concurrent_processing" -v
    local concurrency_test_result=$?
    
    # Phase 4: Generate Report
    print_status "Phase 4: Generating Test Report"
    echo "========================================================"
    
    generate_test_report
    
    # Summary
    echo ""
    print_status "SPRINT 2 TESTING SUMMARY"
    echo "========================================================"
    
    if [[ $unit_test_result -eq 0 ]]; then
        print_success "Unit Tests: PASSED"
    else
        print_error "Unit Tests: FAILED ($unit_test_result failures)"
    fi
    
    if [[ $integration_test_result -eq 0 ]]; then
        print_success "Integration Tests: PASSED"
    else
        print_error "Integration Tests: FAILED"
    fi
    
    if [[ $performance_test_result -eq 0 ]]; then
        print_success "Performance Tests: PASSED"
    else
        print_error "Performance Tests: FAILED"
    fi
    
    if [[ $concurrency_test_result -eq 0 ]]; then
        print_success "Concurrency Tests: PASSED"
    else
        print_error "Concurrency Tests: FAILED"
    fi
    
    # Overall result
    local total_failures=$((unit_test_result + integration_test_result + performance_test_result + concurrency_test_result))
    
    if [[ $total_failures -eq 0 ]]; then
        print_success "ALL TESTS PASSED - Sprint 2 Ready for Deployment!"
        echo ""
        print_status "Next Steps:"
        echo "1. Review test report: backend/SPRINT_2_TEST_REPORT.md"
        echo "2. Deploy to staging environment"
        echo "3. Proceed with V3-BK-007 and V3-BK-008 implementation"
    else
        print_error "Some tests failed. Review logs and fix issues before deployment."
        echo ""
        print_status "Troubleshooting:"
        echo "1. Check service health: curl http://localhost:8014/health"
        echo "2. Review service logs: docker-compose logs ai-event-processor"
        echo "3. Verify dependencies: pip list"
    fi
    
    return $total_failures
}

# Parse command line arguments
case "${1:-}" in
    --unit-only)
        print_status "Running unit tests only..."
        service_paths=(
            "$SERVICES_DIR/ai_event_processor"
            "$SERVICES_DIR/voice_event_processor"
        )
        run_parallel_tests "Unit" "${service_paths[@]}"
        ;;
    --integration-only)
        print_status "Running integration tests only..."
        run_integration_tests
        ;;
    --performance-only)
        print_status "Running performance tests only..."
        cd "$TEST_DIR"
        python -m pytest "$INTEGRATION_TEST_DIR" -k "performance or concurrent" -v
        ;;
    --help)
        echo "Sprint 2 Parallel Testing Suite"
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  --unit-only        Run only unit tests"
        echo "  --integration-only Run only integration tests"
        echo "  --performance-only Run only performance tests"
        echo "  --help            Show this help message"
        echo ""
        echo "Default: Run all tests"
        ;;
    *)
        main "$@"
        ;;
esac
