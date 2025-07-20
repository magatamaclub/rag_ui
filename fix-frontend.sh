#!/bin/bash

echo "🔧 修复前端依赖问题..."

cd frontend

# 清除缓存和依赖
echo "🧹 清除缓存和依赖..."
rm -rf node_modules
rm -rf .umi
rm -f pnpm-lock.yaml
rm -f package-lock.json

# 重新安装依赖
echo "📦 重新安装依赖..."
if command -v pnpm &>/dev/null; then
    pnpm install
else
    npm install
fi

echo "✅ 前端依赖修复完成！"
echo "现在可以运行 ./start-dev.sh 启动项目"
