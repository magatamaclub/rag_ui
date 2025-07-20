#!/bin/bash

# Local Development Setup Script

echo "🚀 Setting up RAG UI for local development..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
fi

# Start PostgreSQL database only
echo "🐘 Starting PostgreSQL database..."
docker-compose up -d db

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Setup backend
echo "🔧 Setting up backend..."
cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Poetry if not exists
if ! command -v poetry &>/dev/null; then
    echo "📦 Installing Poetry..."
    pip install poetry==1.8.2
fi

# Install dependencies
echo "📦 Installing backend dependencies..."
poetry install

# Start backend
echo "🚀 Starting backend server..."
echo "Backend will be available at: http://localhost:8000"
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Setup frontend
cd ../frontend
echo "🔧 Setting up frontend..."

# Install dependencies
if command -v pnpm &>/dev/null; then
    echo "📦 Installing frontend dependencies with pnpm..."
    pnpm install
    echo "🚀 Starting frontend server..."
    echo "Frontend will be available at: http://localhost:8001"
    pnpm dev --port 8001 &
    FRONTEND_PID=$!
else
    echo "📦 Installing frontend dependencies with npm..."
    npm install
    echo "🚀 Starting frontend server..."
    echo "Frontend will be available at: http://localhost:8001"
    npm run dev -- --port 8001 &
    FRONTEND_PID=$!
fi

# Create cleanup function
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    docker-compose stop db
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

echo ""
echo "✅ Development environment is ready!"
echo "📊 Database: localhost:5432"
echo "🔧 Backend API: http://localhost:8000"
echo "🌐 Frontend: http://localhost:8001"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user to stop
wait
