"""
用户认证API测试

这个脚本测试所有用户认证相关的API端点
运行前确保后端服务在 http://localhost:8000 运行
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"


def test_user_registration():
    """测试用户注册"""
    print("🔐 测试用户注册...")

    url = f"{BASE_URL}/auth/register"
    data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpassword123",
    }

    response = requests.post(url, json=data)
    if response.status_code == 200:
        user = response.json()
        print(f"✅ 注册成功: 用户ID {user['id']}, 用户名 {user['username']}")
        return data["username"], data["password"]
    else:
        print(f"❌ 注册失败: {response.status_code} - {response.text}")
        return None, None


def test_user_login(username, password):
    """测试用户登录"""
    print("🔑 测试用户登录...")

    url = f"{BASE_URL}/auth/login"
    data = {"username": username, "password": password}

    response = requests.post(url, json=data)
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ 登录成功: 令牌类型 {token_data['token_type']}")
        return token_data["access_token"]
    else:
        print(f"❌ 登录失败: {response.status_code} - {response.text}")
        return None


def test_get_current_user(token):
    """测试获取当前用户信息"""
    print("👤 测试获取用户信息...")

    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user = response.json()
        print(f"✅ 获取用户信息成功: {user['username']} ({user['email']})")
        return True
    else:
        print(f"❌ 获取用户信息失败: {response.status_code} - {response.text}")
        return False


def test_protected_route(token):
    """测试受保护的路由"""
    print("🛡️ 测试受保护的路由...")

    url = f"{BASE_URL}/auth/protected"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 访问受保护路由成功: {result['message']}")
        return True
    else:
        print(f"❌ 访问受保护路由失败: {response.status_code} - {response.text}")
        return False


def test_unauthorized_access():
    """测试未授权访问"""
    print("🚫 测试未授权访问...")

    url = f"{BASE_URL}/auth/me"

    response = requests.get(url)
    if response.status_code == 401:
        print("✅ 未授权访问正确返回401")
        return True
    else:
        print(f"❌ 未授权访问测试失败: {response.status_code}")
        return False


def test_invalid_token():
    """测试无效令牌"""
    print("🔒 测试无效令牌...")

    url = f"{BASE_URL}/auth/me"
    headers = {"Authorization": "Bearer invalid_token_here"}

    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        print("✅ 无效令牌正确返回401")
        return True
    else:
        print(f"❌ 无效令牌测试失败: {response.status_code}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始用户认证API测试\n")

    # 测试结果统计
    tests_passed = 0
    total_tests = 6

    try:
        # 1. 测试用户注册
        username, password = test_user_registration()
        if username and password:
            tests_passed += 1

            # 2. 测试用户登录
            token = test_user_login(username, password)
            if token:
                tests_passed += 1

                # 3. 测试获取用户信息
                if test_get_current_user(token):
                    tests_passed += 1

                # 4. 测试受保护路由
                if test_protected_route(token):
                    tests_passed += 1

        # 5. 测试未授权访问
        if test_unauthorized_access():
            tests_passed += 1

        # 6. 测试无效令牌
        if test_invalid_token():
            tests_passed += 1

    except requests.exceptions.ConnectionError:
        print("❌ 连接失败：请确保后端服务运行在 http://localhost:8000")
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

    # 输出测试结果
    print(f"\n📊 测试完成: {tests_passed}/{total_tests} 个测试通过")

    if tests_passed == total_tests:
        print("🎉 所有测试通过！用户认证功能运行正常。")
    else:
        print("⚠️ 部分测试失败，请检查服务状态和配置。")


if __name__ == "__main__":
    main()
