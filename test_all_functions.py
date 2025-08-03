#!/usr/bin/env python3
"""
功能测试脚本 - 测试项目的所有功能
"""

import requests

BASE_URL = "http://127.0.0.1:8001"


def test_health_check():
    """测试后端健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"✅ 后端连接: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False


def test_login():
    """测试登录功能"""
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login", json=login_data, timeout=10
        )
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ 登录成功: {token_data}")
            return token_data.get("access_token")
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None


def test_dify_apps(token):
    """测试 Dify 应用列表"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/dify-apps", headers=headers, timeout=10
        )
        if response.status_code == 200:
            apps = response.json()
            print(f"✅ Dify应用列表: {len(apps)} 个应用")
            for app in apps:
                print(f"   - {app['name']} ({app['app_type']})")
            return apps
        else:
            print(f"❌ 获取Dify应用失败: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Dify应用列表异常: {e}")
        return []


def test_create_dify_app(token):
    """测试创建 Dify 应用"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        app_data = {
            "name": "测试应用",
            "app_type": "chatbot",
            "api_url": "https://api.dify.ai/v1",
            "api_key": "test-key-123",
            "description": "这是一个测试应用",
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/dify-apps", headers=headers, json=app_data, timeout=10
        )
        if response.status_code == 200:
            app = response.json()
            print(f"✅ 创建Dify应用成功: {app['name']} (ID: {app['id']})")
            return app
        else:
            print(f"❌ 创建Dify应用失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建Dify应用异常: {e}")
        return None


def test_users(token):
    """测试用户管理功能"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/users", headers=headers, timeout=10)
        if response.status_code == 200:
            users_data = response.json()
            print(f"✅ 用户列表: {users_data['total']} 个用户")
            for user in users_data["users"]:
                print(f"   - {user['username']} ({user['role']}) - {user['email']}")
            return users_data["users"]
        else:
            print(f"❌ 获取用户列表失败: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ 用户列表异常: {e}")
        return []


def test_chat_with_app(token, app_id):
    """测试聊天功能"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        chat_data = {"query": "你好，请介绍一下自己", "conversation_id": "test-conv-1"}
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/app/{app_id}",
            headers=headers,
            json=chat_data,
            stream=True,
            timeout=30,
        )
        if response.status_code == 200:
            print("✅ 聊天功能测试成功")
            # 读取前几行响应
            for i, line in enumerate(response.iter_lines(decode_unicode=True)):
                if i < 5:  # 只显示前5行
                    print(f"   Response: {line}")
                else:
                    break
            return True
        else:
            print(f"❌ 聊天功能失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ 聊天功能异常: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始功能测试...")
    print("=" * 50)

    # 1. 健康检查
    if not test_health_check():
        print("❌ 后端服务不可用，停止测试")
        return

    # 2. 登录测试
    token = test_login()
    if not token:
        print("❌ 登录失败，停止测试")
        return

    # 3. Dify应用测试
    print("\n📱 测试 Dify 应用功能...")
    apps = test_dify_apps(token)

    # 4. 创建测试应用（如果没有应用）
    if len(apps) == 0:
        print("\n🔧 创建测试应用...")
        new_app = test_create_dify_app(token)
        if new_app:
            apps = [new_app]

    # 5. 用户管理测试
    print("\n👥 测试用户管理功能...")
    users = test_users(token)

    # 6. 聊天功能测试（如果有应用）
    if apps:
        print(f"\n💬 测试聊天功能 (使用应用: {apps[0]['name']})...")
        test_chat_with_app(token, apps[0]["id"])

    print("\n" + "=" * 50)
    print("🎉 功能测试完成!")

    # 总结
    print("\n📊 测试总结:")
    print("   - 后端服务: 正常")
    print("   - 用户认证: 正常")
    print(f"   - Dify应用: {len(apps)} 个")
    print(f"   - 用户管理: {len(users)} 个用户")


if __name__ == "__main__":
    main()
