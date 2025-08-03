#!/usr/bin/env python3
"""Dify 应用创建脚本"""

import requests
import getpass


def login_and_get_token():
    """登录获取 token"""

    print("🔐 请登录管理员账户")
    username = input("用户名: ").strip()
    password = getpass.getpass("密码: ")

    login_data = {"username": username, "password": password}

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ 登录成功! 用户: {username}")
            return token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None

    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return None


def create_dify_app(token):
    """创建 Dify 应用"""

    print("\n📝 创建新的 Dify 应用")
    print("-" * 30)

    # 获取应用信息
    name = input("应用名称: ").strip()
    if not name:
        print("❌ 应用名称不能为空")
        return False

    print("\n选择应用类型:")
    print("1. workflow - 工作流")
    print("2. chatflow - 聊天流")
    print("3. chatbot - 聊天机器人")
    print("4. agent - 智能代理")
    print("5. text_generator - 文本生成器")

    type_choice = input("请选择 (1-5): ").strip()
    type_map = {
        "1": "workflow",
        "2": "chatflow",
        "3": "chatbot",
        "4": "agent",
        "5": "text_generator",
    }

    app_type = type_map.get(type_choice)
    if not app_type:
        print("❌ 无效的应用类型选择")
        return False

    api_url = input("Dify API URL (例如: https://api.dify.ai/v1): ").strip()
    if not api_url:
        print("❌ API URL 不能为空")
        return False

    api_key = getpass.getpass("Dify API Key: ")
    if not api_key:
        print("❌ API Key 不能为空")
        return False

    description = input("应用描述 (可选): ").strip()

    # 创建应用数据
    app_data = {
        "name": name,
        "app_type": app_type,
        "api_url": api_url,
        "api_key": api_key,
        "description": description or None,
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/v1/dify-apps",
            json=app_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code == 200:
            data = response.json()
            print("\n✅ Dify 应用创建成功!")
            print(f"   应用ID: {data.get('id')}")
            print(f"   应用名称: {data.get('name')}")
            print(f"   应用类型: {data.get('app_type')}")
            print(f"   API URL: {data.get('api_url')}")
            print("\n🌐 现在您可以在前端的'选择应用'下拉菜单中看到这个应用了!")
            return True
        else:
            print(f"❌ 创建应用失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 创建应用错误: {e}")
        return False


def list_dify_apps(token):
    """列出现有的 Dify 应用"""

    try:
        response = requests.get(
            "http://localhost:8000/api/v1/dify-apps",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 200:
            apps = response.json()
            print(f"\n📋 现有 Dify 应用 (共 {len(apps)} 个):")
            print("-" * 80)
            print("ID   名称              类型           API URL")
            print("-" * 80)

            for app in apps:
                app_id = app.get("id", "N/A")
                name = app.get("name", "N/A")[:15]
                app_type = app.get("app_type", "N/A")[:12]
                api_url = app.get("api_url", "N/A")[:40]

                print(f"{app_id:<4} {name:<15} {app_type:<12} {api_url}")

            print("-" * 80)
            return True
        else:
            print(f"❌ 获取应用列表失败: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 获取应用列表错误: {e}")
        return False


def main():
    """主函数"""

    print("🚀 Dify 应用管理工具")
    print("=" * 40)

    # 登录获取 token
    token = login_and_get_token()
    if not token:
        print("❌ 无法获取认证令牌，退出")
        return

    while True:
        print("\n📋 选择操作:")
        print("1. 创建新的 Dify 应用")
        print("2. 查看现有应用列表")
        print("3. 退出")

        choice = input("\n请选择 (1-3): ").strip()

        if choice == "1":
            create_dify_app(token)
        elif choice == "2":
            list_dify_apps(token)
        elif choice == "3":
            print("👋 再见!")
            break
        else:
            print("❌ 无效选择")


if __name__ == "__main__":
    main()
