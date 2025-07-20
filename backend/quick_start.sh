#!/bin/bash

echo "🚀 Quick Start - RAG UI Backend"
echo "================================"

# 检查Poetry是否安装
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install Poetry first."
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")"

# 检查.env文件
if [ -f ".env" ]; then
    echo "✅ Environment file found"
else
    echo "⚠️  No .env file found"
fi

# 启动服务器
echo "🌐 Starting server on http://localhost:8001"
echo "📝 API documentation available at: http://localhost:8001/docs"
echo "🔍 Health check: http://localhost:8001/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"

poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
