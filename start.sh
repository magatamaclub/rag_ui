#!/bin/bash

# RAG UI Project Startup Script

echo "🚀 Starting RAG UI with Dify Integration..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
    echo "📌 Key settings to configure:"
    echo "   - DB_PASSWORD: Database password"
    echo "   - DB_HOST: Use 'db' for Docker, 'localhost' for local development"
    echo ""
fi

# Display current environment settings
echo "🔧 Current environment configuration:"
echo "   DB_HOST: ${DB_HOST:-localhost}"
echo "   DB_PORT: ${DB_PORT:-5432}"
echo "   DB_NAME: ${DB_NAME:-rag_db}"
echo "   APP_PORT: ${APP_PORT:-8000}"
echo ""

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up --build --no-cache

echo "✅ Services started successfully!"
echo "🌐 Access the application at: http://localhost:${APP_PORT:-80}"
echo "📊 Database available at: localhost:${DB_PORT:-5432}"
