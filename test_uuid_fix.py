#!/usr/bin/env python3
"""
测试UUID格式修复的验证脚本
"""

import requests
import uuid

# API配置
BASE_URL = "http://127.0.0.1:8001/api/v1"


def test_uuid_conversation():
    """测试使用有效UUID的对话功能"""
    print("🧪 测试UUID conversation_id修复...")

    # 注册用户（如果不存在）
    register_data = {
        "username": "uuid_test_user",
        "email": "uuid_test@example.com",
        "password": "test123",
    }

    register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if register_response.status_code == 200:
        print("✅ 用户注册成功")
    else:
        print("ℹ️ 用户已存在，继续登录")

    # 用户登录
    login_data = {"username": "uuid_test_user", "password": "test123"}

    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return

    print("✅ 登录成功")
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 测试1: 使用空的conversation_id（应该自动生成UUID）
    print("\n📝 测试1: 空conversation_id（自动生成UUID）")
    chat_data = {"query": "测试自动生成UUID", "conversation_id": ""}

    response = requests.post(
        f"{BASE_URL}/chat/app/1", json=chat_data, headers=headers, stream=True
    )
    print(f"   状态码: {response.status_code}")

    # 测试2: 使用无效的conversation_id（应该替换为UUID）
    print("\n📝 测试2: 无效conversation_id（应该替换为UUID）")
    chat_data = {
        "query": "测试无效UUID替换",
        "conversation_id": "invalid-conversation-id",
    }

    response = requests.post(
        f"{BASE_URL}/chat/app/1", json=chat_data, headers=headers, stream=True
    )
    print(f"   状态码: {response.status_code}")

    # 测试3: 使用有效的UUID（应该保持不变）
    print("\n📝 测试3: 有效UUID（应该保持不变）")
    valid_uuid = str(uuid.uuid4())
    chat_data = {"query": "测试有效UUID", "conversation_id": valid_uuid}

    response = requests.post(
        f"{BASE_URL}/chat/app/1", json=chat_data, headers=headers, stream=True
    )
    print(f"   状态码: {response.status_code}")
    print(f"   使用的UUID: {valid_uuid}")

    print("\n✅ UUID测试完成！检查服务器日志查看详细信息。")


if __name__ == "__main__":
    test_uuid_conversation()
