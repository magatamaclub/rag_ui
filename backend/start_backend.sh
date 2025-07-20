#!/bin/bash

echo "🚀 Starting RAG UI Backend..."

# Load environment variables from .env file
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded"
    echo "   DB_HOST: $DB_HOST"
    echo "   DB_PORT: $DB_PORT" 
    echo "   DB_NAME: $DB_NAME"
    echo "   DB_USER: $DB_USER"
else
    echo "⚠️  .env file not found, using default values"
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the server (database initialization will happen automatically)
echo "🌐 Starting server on http://localhost:8001"
echo "📊 Database initialization will be attempted during startup"
poetry run python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
