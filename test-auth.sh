#!/bin/bash

echo "🧪 测试用户认证功能"
echo ""

BASE_URL="http://localhost:8000/api/v1"

echo "1. 测试注册用户..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }')

echo "注册响应: $REGISTER_RESPONSE"
echo ""

echo "2. 测试登录..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }')

echo "登录响应: $LOGIN_RESPONSE"
echo ""

# 提取 token
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ ! -z "$TOKEN" ]; then
  echo "3. 测试受保护的端点 (获取当前用户信息)..."
  USER_RESPONSE=$(curl -s -X GET "$BASE_URL/auth/me" \
    -H "Authorization: Bearer $TOKEN")
  
  echo "用户信息响应: $USER_RESPONSE"
  echo ""
  echo "✅ 认证功能测试完成！"
else
  echo "❌ 获取 token 失败，请检查后端服务"
fi
