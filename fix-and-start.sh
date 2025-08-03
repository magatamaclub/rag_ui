#!/bin/bash

# RAG UI 快速修复脚本
# 解决 Node.js 版本兼容性问题并启动系统

echo "🔧 RAG UI 快速修复和启动脚本"
echo "=================================="

# 检查当前 Node.js 版本
current_node_version=$(node --version)
echo "📋 当前 Node.js 版本: $current_node_version"

# 项目根目录
PROJECT_ROOT="/Users/hiyenwong/projects/ai_projects/rag_ui_ant_design"
cd "$PROJECT_ROOT"

echo ""
echo "🛠️  修复选项:"
echo "1. 使用 nvm 切换到兼容版本 (推荐)"
echo "2. 临时修改 package.json 移除版本限制"
echo "3. 跳过前端，仅启动后端"
echo ""

read -p "请选择修复方案 (1-3): " choice

case $choice in
    1)
        echo "🔄 使用 nvm 切换 Node.js 版本..."
        
        # 检查 nvm 是否安装
        if ! command -v nvm &> /dev/null; then
            echo "📦 安装 nvm..."
            curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
            [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
        fi
        
        # 安装并使用兼容版本
        nvm install 20.19.4
        nvm use 20.19.4
        
        echo "✅ Node.js 版本已切换到 20.19.4"
        ;;
        
    2)
        echo "⚠️  临时修改 package.json..."
        
        # 备份原始文件
        cp frontend/package.json frontend/package.json.backup
        echo "📋 已备份 frontend/package.json"
        
        # 移除 engines 限制
        cd frontend
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' '/"engines"/,/},/d' package.json
        else
            # Linux
            sed -i '/"engines"/,/},/d' package.json
        fi
        
        echo "✅ 已移除 Node.js 版本限制"
        cd ..
        ;;
        
    3)
        echo "🚀 仅启动后端服务..."
        
        # 启动数据库
        echo "🐘 启动数据库..."
        docker-compose up -d db
        
        # 等待数据库启动
        echo "⏳ 等待数据库就绪..."
        sleep 5
        
        # 启动后端
        echo "🔧 启动后端..."
        cd backend
        poetry install
        poetry run python -m app.main &
        
        echo "✅ 后端已启动在 http://localhost:8000"
        echo "📖 API 文档: http://localhost:8000/docs"
        echo ""
        echo "⚠️  前端未启动，您可以直接使用 API 文档进行操作"
        exit 0
        ;;
        
    *)
        echo "❌ 无效选择，退出"
        exit 1
        ;;
esac

echo ""
echo "🚀 启动完整服务..."

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "umi" 2>/dev/null || true

# 启动数据库
echo "🐘 启动数据库..."
docker-compose up -d db

# 等待数据库启动
echo "⏳ 等待数据库就绪..."
sleep 8

# 启动后端
echo "🔧 启动后端..."
cd backend
poetry install > /dev/null 2>&1
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 5

# 启动前端
echo "🌐 启动前端..."
cd ../frontend
pnpm install > /dev/null 2>&1
pnpm dev &
FRONTEND_PID=$!

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 10

echo ""
echo "✅ 系统启动完成!"
echo "=================================="
echo "🌐 前端应用: http://localhost:8001"
echo "🔧 后端 API: http://localhost:8000"
echo "📖 API 文档: http://localhost:8000/docs"
echo "🐘 数据库: localhost:5432"
echo ""
echo "📋 Dify 应用管理路径:"
echo "   - 基础配置: /dify-config"
echo "   - 应用管理: /dify-app-manage (需要管理员权限)"
echo ""
echo "💡 使用提示:"
echo "   1. 访问 http://localhost:8001"
echo "   2. 注册账户并登录"
echo "   3. 如需管理员权限，请参考 DIFY_APP_SETUP_GUIDE.md"
echo ""
echo "🛑 按 Ctrl+C 停止所有服务"

# 等待用户中断
trap 'echo ""; echo "🛑 停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker-compose down; exit 0' INT
wait
