#!/usr/bin/env python3
"""
测试 /api/v1/chat/app/1 接口的 400 Bad Request 问题
"""

import requests
import json

# 测试配置
BASE_URL = "http://localhost:8001"
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
CHAT_APP_URL = f"{BASE_URL}/api/v1/chat/app/1"


def test_json_parsing_issue():
    """测试不同的请求体格式"""

    print("🧪 测试 JSON 解析问题...")

    # 先注册和登录用户
    print("\n1. 用户注册...")
    register_data = {
        "username": "test_json_user",
        "email": "test_json@example.com",
        "password": "test123",
    }

    response = requests.post(REGISTER_URL, json=register_data)
    print(f"注册状态: {response.status_code}")

    # 登录获取token
    print("\n2. 用户登录...")
    login_data = {"username": "test_json_user", "password": "test123"}

    response = requests.post(LOGIN_URL, json=login_data)
    print(f"登录状态: {response.status_code}")

    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"获取到token: {token[:20]}...")

        # 测试不同的请求体格式
        test_cases = [
            {"name": "空请求体", "data": None, "content_type": "application/json"},
            {"name": "空字符串", "data": "", "content_type": "application/json"},
            {
                "name": "无效JSON",
                "data": "{invalid json",
                "content_type": "application/json",
            },
            {
                "name": "正确的JSON - 缺少query",
                "data": json.dumps({}),
                "content_type": "application/json",
            },
            {
                "name": "正确的JSON - 完整数据",
                "data": json.dumps(
                    {"query": "你好，测试消息", "conversation_id": "test-conv-123"}
                ),
                "content_type": "application/json",
            },
        ]

        print("\n3. 测试不同的请求体格式...")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n测试 {i}: {test_case['name']}")

            # 准备headers
            test_headers = headers.copy()
            test_headers["Content-Type"] = test_case["content_type"]

            try:
                if test_case["data"] is None:
                    # 不发送请求体
                    response = requests.post(CHAT_APP_URL, headers=headers)
                elif isinstance(test_case["data"], str):
                    # 发送字符串数据
                    response = requests.post(
                        CHAT_APP_URL, data=test_case["data"], headers=test_headers
                    )
                else:
                    # 发送JSON数据
                    response = requests.post(
                        CHAT_APP_URL, json=test_case["data"], headers=headers
                    )

                print(f"  状态码: {response.status_code}")

                if response.status_code == 400:
                    try:
                        error_detail = response.json()
                        print(f"  错误详情: {error_detail}")
                    except:
                        print(f"  错误内容: {response.text}")
                elif response.status_code == 200:
                    print("  成功: 开始接收流式响应")

            except Exception as e:
                print(f"  请求异常: {e}")

    else:
        print("❌ 登录失败，无法继续测试")


if __name__ == "__main__":
    test_json_parsing_issue()
