#!/bin/bash

# MantraPath API Gateway - Test Runner Script

set -e

echo "🧪 Running MantraPath API Gateway Test Suite..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install pytest pytest-asyncio pytest-cov httpx

# Run linting
echo "🔍 Running code quality checks..."
echo "  - Black (formatting)..."
black --check src/ tests/ || echo "⚠️ Code formatting issues found. Run 'black src/ tests/' to fix."

echo "  - isort (import sorting)..."
isort --check-only src/ tests/ || echo "⚠️ Import sorting issues found. Run 'isort src/ tests/' to fix."

echo "  - flake8 (linting)..."
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 || echo "⚠️ Linting issues found."

# Run tests with coverage
echo "🧪 Running tests with coverage..."
pytest tests/ \
    --cov=src \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=70 \
    -v

echo "📊 Coverage report generated in htmlcov/"

# Run specific test categories
echo "🔧 Running integration tests..."
pytest tests/test_gateway.py -v

echo "⚡ Running performance tests..."
# Add performance tests here when available

echo "✅ All tests completed!"
echo "📈 Check htmlcov/index.html for detailed coverage report"
