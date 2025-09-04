# Voice Service Testing Guide

This directory contains comprehensive test suites for the Voice Service, with special focus on Indian regional languages and interactive scenarios.

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── fixtures/
│   └── test_data.py        # Test data for Indian languages and scenarios
├── unit/
│   ├── test_models_client.py       # Models service client tests
│   ├── test_language_detector.py   # Language detection tests
│   └── test_conversation_manager.py # Conversation flow tests
├── integration/
│   └── test_voice_service_integration.py # End-to-end integration tests
├── test_runner.py          # Simple test runner script
└── run_tests.py           # Comprehensive test runner
```

## Test Coverage

### Indian Regional Languages Covered
- **Hindi** (हिंदी) - Devanagari script
- **Bengali** (বাংলা) - Bengali script 
- **Tamil** (தமிழ்) - Tamil script
- **Telugu** (తెలుగు) - Telugu script
- **Marathi** (मराठी) - Devanagari script
- **Gujarati** (ગુજરાતી) - Gujarati script
- **Kannada** (ಕನ್ನಡ) - Kannada script
- **Malayalam** (മലയാളം) - Malayalam script
- **Punjabi** (ਪੰਜਾਬੀ) - Gurmukhi script
- **Urdu** (اردو) - Arabic script

### Code-Switching Scenarios
- Hindi-English intra-sentential switching
- Hindi-English inter-sentential switching
- Regional dialect variations

### Interactive Scenarios Tested
1. **Medical Consultation** - Healthcare domain interactions
2. **Banking Inquiry** - Financial services conversations
3. **Educational Support** - Learning and tutoring sessions
4. **Customer Service** - General support conversations

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install -r requirements.txt
```

### Quick Testing

Run basic unit tests:
```bash
python tests/test_runner.py basic
```

Run Indian language specific tests:
```bash
python tests/test_runner.py indian
```

Run integration tests (requires running voice service):
```bash
python tests/test_runner.py integration
```

Run all tests:
```bash
python tests/test_runner.py all
```

### Detailed Testing

For comprehensive testing with detailed reports:
```bash
python tests/run_tests.py
```

This will generate a detailed JSON report with:
- Test coverage analysis
- Performance benchmarks
- Language support validation
- Recommendations for improvements

### Running Specific Test Patterns

Run tests for specific languages:
```bash
pytest -k "hindi" -v
pytest -k "bengali" -v
pytest -k "code_switching" -v
```

Run performance tests:
```bash
pytest -k "performance" -v
```

Run conversation flow tests:
```bash
pytest -k "conversation" -v
```

## Test Data

### Indian Language Test Samples
The test suite includes authentic text samples in all supported Indian languages, including:
- Common greetings and phrases
- Regional variations and dialects
- Mixed-language (code-switching) examples
- Domain-specific vocabulary (medical, banking, education)

### Performance Benchmarks
- STT Latency: Target < 1.5s, Max < 3s
- TTS Latency: Target < 1s, Max < 2s  
- Conversation Response: Target < 3s, Max < 5s
- Cache Hit Rate: Target > 85%, Minimum > 70%

## Integration Testing

### Prerequisites for Integration Tests
1. Voice Service running on `localhost:8010`
2. Models Service running on `localhost:8085`
3. Redis running on `localhost:6379`

### Starting Services for Testing

Start the voice service:
```bash
cd /path/to/voice_service
python main.py
```

The integration tests will automatically check service health before running.

## Test Results Analysis

### Understanding Test Output

- ✅ **PASSED** - Test executed successfully
- ❌ **FAILED** - Test failed, check error details
- ⏭️ **SKIPPED** - Test skipped (usually due to missing dependencies)
- ⚠️ **WARNING** - Test passed but with warnings

### Common Issues and Solutions

1. **Service Not Running**
   ```
   Error: Voice service not accessible
   Solution: Start the voice service on localhost:8010
   ```

2. **Missing Dependencies**
   ```
   Error: Missing test dependencies
   Solution: pip install pytest pytest-asyncio aiohttp requests
   ```

3. **Language Detection Failures**
   ```
   Error: Language detection confidence too low
   Solution: Check if language models are properly loaded
   ```

4. **Performance Issues**
   ```
   Error: Response time exceeds benchmark
   Solution: Check system resources and optimize caching
   ```

## Contributing Tests

### Adding New Language Tests
1. Add language data to `fixtures/test_data.py`
2. Create test cases in relevant test files
3. Include both unit and integration tests
4. Test with authentic language samples

### Adding New Conversation Scenarios
1. Define scenario in `CONVERSATION_SCENARIOS`
2. Include context, expected responses, and flow
3. Test multi-turn conversations
4. Validate context awareness

### Best Practices
- Use authentic language samples
- Test edge cases and error conditions
- Include performance validation
- Document expected behavior
- Test both positive and negative scenarios

## Automated Testing

### CI/CD Integration
The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Voice Service Tests
  run: |
    pip install -r requirements.txt
    python tests/test_runner.py all
```

### Test Reports
Detailed test reports are generated in JSON format and include:
- Test execution summary
- Performance metrics
- Language support matrix
- Failure analysis
- Recommendations for improvements

## Troubleshooting

### Debug Mode
Run tests with verbose output:
```bash
pytest -v -s --tb=long
```

### Test Specific Components
```bash
# Test only language detection
pytest tests/unit/test_language_detector.py -v

# Test only conversation management  
pytest tests/unit/test_conversation_manager.py -v

# Test only models service integration
pytest tests/unit/test_models_client.py -v
```

### Performance Profiling
Run tests with performance profiling:
```bash
pytest --cov=app --cov-report=term-missing
```

For questions or issues with testing, please refer to the main Voice Service documentation or create an issue in the repository.
