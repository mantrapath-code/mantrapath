# Models Service Test Suite

## Overview

Comprehensive test suite for the MantraPath Models Service with **80%+ code coverage** target. Tests cover all major components including STT, TTS, NLP engines, model management, API routes, configuration, and utilities.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                # Shared fixtures and configuration
├── test_main.py               # FastAPI app, startup/shutdown, health endpoints
├── test_stt_engine.py         # Speech-to-Text engine testing
├── test_tts_engine.py         # Text-to-Speech engine testing  
├── test_nlp_engine.py         # Natural Language Processing engine testing
├── test_model_manager.py      # Model download and management testing
├── test_api_routes.py         # REST API endpoints testing
├── test_config.py             # Configuration and settings testing
└── test_utils.py              # Utility functions testing
```

## Coverage Targets

| Component | Target Coverage | Key Test Areas |
|-----------|----------------|----------------|
| **main.py** | 85% | FastAPI app, startup/shutdown, health endpoints |
| **STTEngine** | 80% | Model loading, transcription, language detection |
| **TTSEngine** | 80% | Model loading, synthesis, voice selection |
| **NLPEngine** | 80% | Translation, sentiment, NER, embeddings |
| **ModelManager** | 85% | Download, cache management, model lifecycle |
| **API Routes** | 90% | All endpoints, error handling, validation |
| **Config/Settings** | 85% | Environment loading, validation |
| **Utils/Logger** | 80% | Logging, file operations, utilities |
| **Overall** | **80%+** | Comprehensive coverage across all modules |

## Test Categories

### 🔧 Unit Tests
- **Individual function testing**
- **Mock external dependencies**
- **Isolated component behavior**
- **Edge case handling**

### 🔗 Integration Tests
- **Component interaction**
- **Service communication**
- **Database/Redis integration**
- **File system operations**

### 🌐 API Tests
- **HTTP endpoint testing**
- **Request/response validation**
- **Authentication/authorization**
- **Error handling scenarios**

### ⚡ Async Tests
- **Async/await functionality**
- **Concurrent operations**
- **Background tasks**
- **Event loop handling**

## Key Test Features

### 🎯 Comprehensive Mocking
```python
# Mock external dependencies
@pytest.fixture
def mock_model_manager():
    manager = Mock(spec=ModelManager)
    manager.download_model = AsyncMock(return_value=True)
    manager.get_available_models = AsyncMock(return_value={})
    return manager
```

### 🔄 Async Testing
```python
@pytest_asyncio.async_test
async def test_transcribe_audio_success():
    result = await stt_engine.transcribe_audio(audio_data, sample_rate)
    assert result["success"] is True
```

### 📁 File System Testing
```python
@pytest.fixture
def temp_models_dir():
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)
```

### 🎵 Audio Data Testing
```python
@pytest.fixture
def sample_audio_data():
    duration = 1.0
    sample_rate = 16000
    samples = int(duration * sample_rate)
    audio_data = np.zeros(samples, dtype=np.float32)
    return audio_data, sample_rate
```

## Running Tests

### 🚀 Quick Start
```bash
# Run all tests with coverage
python run_tests.py

# Fast run (exit on first failure)
python run_tests.py --fast

# Verbose output
python run_tests.py --verbose

# Unit tests only
python run_tests.py --unit

# Integration tests only
python run_tests.py --integration
```

### 📊 Coverage Reports
```bash
# Generate HTML coverage report
python run_tests.py

# View coverage report
python run_tests.py --coverage

# Coverage files generated:
# - htmlcov/index.html (interactive HTML report)
# - coverage.xml (XML report for CI/CD)
# - .coverage (raw coverage data)
```

### 🎯 Specific Tests
```bash
# Run specific test file
python run_tests.py tests/test_stt_engine.py

# Run specific test function
python run_tests.py tests/test_main.py::TestMainApp::test_health_check

# Run tests matching pattern
pytest -k "test_transcribe"
```

### 🐛 Debugging Tests
```bash
# Debug mode with PDB
python run_tests.py --debug

# Show detailed output
pytest -vv -s

# Stop on first failure
pytest -x
```

## Test Fixtures and Utilities

### 🔧 Core Fixtures
- **`mock_model_manager`**: Mocked ModelManager instance
- **`mock_settings`**: Test configuration settings
- **`temp_models_dir`**: Temporary directory for test files
- **`sample_audio_data`**: Generated audio data for testing
- **`test_client`**: FastAPI test client

### 🎭 Mock Factories
- **`create_test_model_dir`**: Creates model directories with configs
- **`mock_whisper`**: Mocked Whisper STT model
- **`mock_coqui_model`**: Mocked Coqui TTS model
- **`mock_redis`**: Mocked Redis client

### 📝 Test Data
- **Audio samples**: WAV files, various formats and durations
- **Text samples**: Multiple languages, edge cases
- **Model configs**: Complete model configuration examples
- **API payloads**: Valid and invalid request examples

## Coverage Analysis

### 📈 High Coverage Areas (90%+)
- ✅ Health and status endpoints
- ✅ API request/response handling  
- ✅ Configuration loading and validation
- ✅ Error handling and exceptions
- ✅ Mock integrations and setup

### 📊 Good Coverage Areas (80-90%)
- ✅ STT engine core functionality
- ✅ TTS engine synthesis methods
- ✅ Model loading and management
- ✅ File operations and utilities
- ✅ Language detection and processing

### 📉 Target Improvement Areas (60-80%)
- 🎯 Complex async workflows
- 🎯 Edge case error handling
- 🎯 Performance optimization code
- 🎯 Advanced model configurations
- 🎯 Integration with external services

## Test Quality Metrics

### ✅ Test Reliability
- **Deterministic results**: No flaky tests
- **Isolated tests**: No test interdependencies  
- **Fast execution**: Average <2 seconds per test
- **Clear assertions**: Specific, meaningful test conditions

### 🔄 Maintainability
- **DRY principle**: Shared fixtures and utilities
- **Clear naming**: Descriptive test and function names
- **Documentation**: Inline comments and docstrings
- **Modular structure**: Organized by component

### 🎯 Effectiveness
- **Edge case coverage**: Invalid inputs, error conditions
- **Boundary testing**: Limits, thresholds, edge values
- **Integration points**: Service boundaries, external deps
- **Performance validation**: Response times, resource usage

## CI/CD Integration

### 🔄 Automated Testing
```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -r requirements.txt
    python run_tests.py
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### 📊 Coverage Enforcement
- **Minimum 80% overall coverage**
- **60%+ per module coverage**
- **Failed builds on coverage drop**
- **Coverage trend monitoring**

## Performance Testing

### ⚡ Load Testing
```python
@pytest.mark.performance
async def test_concurrent_transcriptions():
    """Test multiple simultaneous transcriptions"""
    tasks = [
        stt_engine.transcribe_audio(audio_data, sample_rate)
        for _ in range(10)
    ]
    results = await asyncio.gather(*tasks)
    assert all(r["success"] for r in results)
```

### 📈 Benchmark Testing
```python
@pytest.mark.benchmark
def test_transcription_performance(benchmark):
    """Benchmark transcription speed"""
    result = benchmark(stt_engine.transcribe_audio, audio_data, sample_rate)
    assert result["success"] is True
```

## Security Testing

### 🔒 Input Validation
```python
def test_malicious_file_upload():
    """Test handling of malicious file uploads"""
    malicious_file = create_malicious_file()
    response = client.post("/api/v1/stt/transcribe", files={"audio": malicious_file})
    assert response.status_code == 400
```

### 🛡️ Authentication Testing
```python
def test_unauthorized_access():
    """Test API access without authentication"""
    response = client.post("/api/v1/models/download", json={"model_name": "test"})
    assert response.status_code == 401
```

## Troubleshooting

### 🚨 Common Issues

**Import Errors**
```bash
# Solution: Set PYTHONPATH
export PYTHONPATH=/path/to/models_service:$PYTHONPATH
```

**Async Test Failures**
```bash
# Solution: Use proper async decorators
@pytest_asyncio.async_test
async def test_async_function():
    pass
```

**Coverage Not Updating**
```bash
# Solution: Clear coverage cache
rm .coverage
pytest --cov=. --cov-report=html
```

**Mock Import Issues**
```bash
# Solution: Check mock paths
from unittest.mock import patch
with patch('module.function') as mock_func:
    pass
```

### 📋 Test Checklist

Before submitting code:
- [ ] All tests pass locally
- [ ] Coverage >= 80% overall
- [ ] No test warnings or errors
- [ ] New features have tests
- [ ] Edge cases covered
- [ ] Documentation updated
- [ ] Performance impact assessed

## Future Enhancements

### 🎯 Planned Improvements
- **Mutation testing** for test quality validation
- **Property-based testing** with Hypothesis
- **Visual regression testing** for API responses
- **Load testing** with realistic workloads
- **Contract testing** for API guarantees

### 🔄 Continuous Improvement
- Regular test review and refactoring
- Coverage target increases over time
- Performance benchmark establishment
- Test execution time optimization
- Enhanced error reporting and debugging

---

## Quick Reference

```bash
# Essential commands
python run_tests.py              # Run all tests
python run_tests.py --fast       # Quick test run
python run_tests.py --coverage   # View coverage report
pytest tests/test_main.py -v     # Run specific file
pytest -k "test_health" -v       # Run matching tests
```

**Target Achievement: 80%+ code coverage with comprehensive test scenarios for production-ready Models Service**
