#!/bin/bash

# RAG UI Backend API Test Runner
# Runs comprehensive test suite for all backend API endpoints

set -e  # Exit on any error

echo "🧪 RAG UI Backend API Test Suite"
echo "=================================="

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found. Please create one first:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install test dependencies if not already installed
echo "📦 Installing test dependencies..."
pip install pytest pytest-mock pytest-asyncio httpx psutil

# Set environment variables for testing
export APP_DEBUG=true
export DB_HOST=test
export DB_NAME=test_db
export SECRET_KEY=test_secret_key_for_testing_only

echo ""
echo "🏃 Running Test Suite..."
echo "========================"

# Run comprehensive API tests
echo "1️⃣ Running Comprehensive API Tests..."
python -m pytest tests/test_comprehensive_api.py -v --tb=short

echo ""
echo "2️⃣ Running Database Model Tests..."
python -m pytest tests/test_database_models.py -v --tb=short

echo ""
echo "3️⃣ Running Performance Tests..."
python -m pytest tests/test_performance.py -v --tb=short

echo ""
echo "4️⃣ Running Original API Tests..."
if [ -f "tests/test_api.py" ]; then
    python -m pytest tests/test_api.py -v --tb=short
else
    echo "⏭️  Skipping original API tests (file not found)"
fi

echo ""
echo "📊 Generating Test Coverage Report..."
pip install pytest-cov
python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

echo ""
echo "✅ Test Suite Completed!"
echo "========================"
echo "📄 Coverage report generated in htmlcov/index.html"
echo "🔗 Open with: open htmlcov/index.html"

# Run database initialization test
echo ""
echo "🗄️  Testing Database Initialization..."
python init_db.py

echo ""
echo "🎉 All tests completed successfully!"
echo "📋 Test Summary:"
echo "   - ✅ Comprehensive API Tests"
echo "   - ✅ Database Model Tests" 
echo "   - ✅ Performance Tests"
echo "   - ✅ Database Initialization"
echo "   - ✅ Test Coverage Report"
