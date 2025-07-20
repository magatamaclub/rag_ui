#!/bin/bash

echo "🧹 清理项目中不需要提交的文件"

# 清理 Python 缓存
echo "清理 Python __pycache__ 目录..."
find . -name "__pycache__" -type d -not -path "./backend/.venv/*" -exec rm -rf {} + 2>/dev/null || true

# 清理 Python 编译文件
echo "清理 Python .pyc 文件..."
find . -name "*.pyc" -not -path "./backend/.venv/*" -delete 2>/dev/null || true
find . -name "*.pyo" -not -path "./backend/.venv/*" -delete 2>/dev/null || true

# 清理前端构建缓存
echo "清理前端缓存..."
rm -rf frontend/.umi/
rm -rf frontend/.cache/
rm -rf frontend/dist/
rm -rf frontend/build/
rm -rf frontend/.umi-production/
rm -rf frontend/.umi-test/

# 清理 macOS 系统文件
echo "清理 macOS 系统文件..."
find . -name ".DS_Store" -delete 2>/dev/null || true

# 清理临时文件
echo "清理临时文件..."
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.log" -not -path "./backend/.venv/*" -delete 2>/dev/null || true

# 清理编辑器临时文件
echo "清理编辑器临时文件..."
find . -name "*.swp" -delete 2>/dev/null || true
find . -name "*.swo" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true

echo "✅ 清理完成！"

echo ""
echo "📋 建议检查以下文件是否应该提交："
echo "- .env 文件 (包含敏感信息，通常不提交)"
echo "- poetry.lock (建议提交以确保依赖版本一致)"
echo "- pnpm-lock.yaml (建议提交以确保依赖版本一致)"

echo ""
echo "🔍 当前 git 状态："
git status --porcelain
