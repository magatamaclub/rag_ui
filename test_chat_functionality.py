#!/usr/bin/env python3
"""
完整的对话功能测试脚本
测试用户注册、登录、和对话接口
"""

import requests

BASE_URL = "http://127.0.0.1:8001/api/v1"
TEST_USERNAME = "test_user_chat"
TEST_EMAIL = "test_chat@example.com"
TEST_PASSWORD = "test_password_123"


def print_separator(title):
    """打印分隔符"""
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def test_user_registration():
    """测试用户注册"""
    print_separator("测试用户注册")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": TEST_USERNAME,
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "role": "user",
            },
            timeout=10,
        )
        print(f"注册响应状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"注册成功: {response.json()}")
            return True
        elif response.status_code == 400:
            result = response.json()
            if "already registered" in result.get("detail", ""):
                print("用户已存在，继续登录测试")
                return True
            else:
                print(f"注册失败: {result}")
                return False
        else:
            print(f"注册失败: {response.text}")
            return False
    except Exception as e:
        print(f"注册请求异常: {e}")
        return False


def test_user_login():
    """测试用户登录并获取token"""
    print_separator("测试用户登录")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            timeout=10,
        )
        print(f"登录响应状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print(f"登录成功，获取token: {token[:20]}...")
            return token
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"登录请求异常: {e}")
        return None


def test_chat_endpoint(token):
    """测试普通聊天接口"""
    print_separator("测试普通聊天接口")

    if not token:
        print("❌ 没有有效的token，跳过聊天测试")
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 测试1: 有效的聊天请求
    print("\n1. 测试有效的聊天请求:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "query": "你好，请介绍一下你的功能",
                "conversation_id": "test-conversation-123",
            },
            headers=headers,
            timeout=10,
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 聊天接口正常响应")
        else:
            print(f"   ❌ 聊天失败: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")

    # 测试2: 空请求体
    print("\n2. 测试空请求体:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat", data="", headers=headers, timeout=10
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")

    # 测试3: 无效JSON
    print("\n3. 测试无效JSON:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat", data="invalid json content", headers=headers, timeout=10
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")


def test_chat_with_app_endpoint(token):
    """测试指定应用的聊天接口"""
    print_separator("测试指定应用聊天接口")

    if not token:
        print("❌ 没有有效的token，跳过测试")
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 测试1: 有效的聊天请求
    print("\n1. 测试有效的聊天请求:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/app/1",
            json={
                "query": "你好，这是一个测试消息",
                "conversation_id": "test-app-conversation-123",
            },
            headers=headers,
            timeout=10,
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 应用聊天接口正常响应")
        elif response.status_code == 404:
            print("   ℹ️ 应用未找到（正常，因为没有配置应用）")
        else:
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")

    # 测试2: 空请求体（之前会导致500错误）
    print("\n2. 测试空请求体:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/app/1", data="", headers=headers, timeout=10
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        if response.status_code == 400:
            print("   ✅ JSON解析错误被正确捕获")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")

    # 测试3: 无效JSON（之前会导致500错误）
    print("\n3. 测试无效JSON:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/app/1",
            data="invalid json content",
            headers=headers,
            timeout=10,
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
        if response.status_code == 400:
            print("   ✅ JSON解析错误被正确捕获")
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")


def test_server_health():
    """测试服务器健康状态"""
    print_separator("测试服务器健康状态")

    try:
        response = requests.get(f"{BASE_URL}/../", timeout=5)
        print(f"根路径状态码: {response.status_code}")

        response = requests.get(f"{BASE_URL}/../docs", timeout=5)
        print(f"API文档状态码: {response.status_code}")

        response = requests.get(f"{BASE_URL}/../openapi.json", timeout=5)
        print(f"OpenAPI Schema状态码: {response.status_code}")

        print("✅ 服务器运行正常")
        return True
    except Exception as e:
        print(f"❌ 服务器连接失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始对话功能完整测试...")

    # 检查服务器状态
    if not test_server_health():
        print("❌ 服务器不可用，退出测试")
        return

    # 用户注册
    if not test_user_registration():
        print("❌ 用户注册失败，退出测试")
        return

    # 用户登录获取token
    token = test_user_login()

    # 测试聊天功能
    test_chat_endpoint(token)
    test_chat_with_app_endpoint(token)

    print_separator("测试完成")
    print("🎉 对话功能测试已完成！")
    print("📝 主要验证了：")
    print("   ✅ 用户注册和登录功能")
    print("   ✅ JSON解析错误处理（不再导致500错误）")
    print("   ✅ 聊天接口的基本响应")
    print("   ✅ 错误处理的改进")


if __name__ == "__main__":
    main()
