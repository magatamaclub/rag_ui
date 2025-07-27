#!/bin/bash

# RAG UI Backend 启动脚本 (修复版)
# 解决了psycopg2内存错误问题

echo "🚀 启动 RAG UI Backend..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 检查端口是否被占用
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ 端口8001已被占用，正在清理..."
    kill -9 $(lsof -Pi :8001 -sTCP:LISTEN -t) 2>/dev/null || true
    sleep 1
fi

# 激活虚拟环境并启动服务
echo "✅ 启动FastAPI服务..."
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

echo "🎉 服务启动完成！"
echo "📚 API文档: http://127.0.0.1:8001/docs"
echo "📖 ReDoc: http://127.0.0.1:8001/redoc"
echo "❤️ 健康检查: http://127.0.0.1:8001/health"
