#!/bin/bash

echo "🚀 启动 RAG UI 系统"

# 启动数据库
echo "🐘 启动 PostgreSQL 数据库..."
docker-compose up -d

# 等待数据库启动
echo "⏳ 等待数据库就绪..."
sleep 5

# 启动后端
echo "🔧 启动后端服务..."
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
pnpm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 系统启动完成！"
echo ""
echo "📍 服务地址："
echo "  前端: http://localhost:8001"
echo "  后端: http://localhost:8000"
echo "  数据库: localhost:5432"
echo ""
echo "🔐 用户登录功能已就绪！"
echo "  - 注册新用户或使用现有账户登录"
echo "  - JWT token 认证已配置完成"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户终止
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose down; exit" SIGINT SIGTERM

wait
