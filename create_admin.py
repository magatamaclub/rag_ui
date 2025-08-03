#!/usr/bin/env python3
"""
RAG UI 管理员账户创建脚本
用于创建管理员账户以访问 Dify 应用管理功能
"""

import sys
import hashlib
import getpass
import psycopg2
from datetime import datetime

# 添加项目路径
project_path = "/Users/hiyenwong/projects/ai_projects/rag_ui_ant_design/backend"
sys.path.append(project_path)


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_admin_user():
    """创建管理员用户"""

    print("🔐 RAG UI 管理员账户创建工具")
    print("=" * 40)

    # 获取用户输入
    username = input("请输入管理员用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return False

    email = input("请输入管理员邮箱: ").strip()
    if not email:
        print("❌ 邮箱不能为空")
        return False

    password = getpass.getpass("请输入密码: ")
    if not password:
        print("❌ 密码不能为空")
        return False

    confirm_password = getpass.getpass("请确认密码: ")
    if password != confirm_password:
        print("❌ 密码不匹配")
        return False

    # 数据库连接参数
    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "rag_db",
        "user": "user",
        "password": "password",
    }

    try:
        # 连接数据库
        print("\n📡 连接数据库...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # 检查用户是否已存在
        cursor.execute(
            "SELECT id FROM users WHERE username = %s OR email = %s", (username, email)
        )
        if cursor.fetchone():
            print("❌ 用户名或邮箱已存在")
            return False

        # 创建用户
        hashed_password = hash_password(password)
        now = datetime.now()

        cursor.execute(
            """
            INSERT INTO users (username, email, hashed_password, role, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """,
            (username, email, hashed_password, "admin", True, now, now),
        )

        user_id = cursor.fetchone()[0]
        conn.commit()

        print("✅ 管理员账户创建成功!")
        print(f"   用户ID: {user_id}")
        print(f"   用户名: {username}")
        print(f"   邮箱: {email}")
        print("   权限: 管理员")
        print()
        print("🌐 现在您可以使用此账户登录系统并访问:")
        print("   - Dify 配置: http://localhost:8001/dify-config")
        print("   - Dify 应用管理: http://localhost:8001/dify-app-manage")
        print("   - 用户管理: http://localhost:8001/user-manage")

        return True

    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def list_users():
    """列出现有用户"""

    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "rag_db",
        "user": "user",
        "password": "password",
    }

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, email, role, is_active, created_at FROM users ORDER BY created_at"
        )
        users = cursor.fetchall()

        print("\n👥 现有用户列表:")
        print("-" * 80)
        print(
            f"{'ID':<4} {'用户名':<15} {'邮箱':<25} {'权限':<8} {'状态':<6} {'创建时间'}"
        )
        print("-" * 80)

        for user in users:
            user_id, username, email, role, is_active, created_at = user
            status = "激活" if is_active else "禁用"
            role_cn = "管理员" if role == "admin" else "用户"
            created_str = created_at.strftime("%Y-%m-%d %H:%M")

            print(
                f"{user_id:<4} {username:<15} {email:<25} {role_cn:<8} {status:<6} {created_str}"
            )

        print("-" * 80)
        print(f"总计: {len(users)} 个用户")

    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
    except Exception as e:
        print(f"❌ 查询失败: {e}")
    finally:
        if "conn" in locals():
            conn.close()


def promote_user():
    """提升用户为管理员"""

    print("\n🔝 提升用户为管理员")
    print("-" * 30)

    # 先显示用户列表
    list_users()

    try:
        user_id = int(input("\n请输入要提升的用户ID: "))
    except ValueError:
        print("❌ 请输入有效的用户ID")
        return False

    db_config = {
        "host": "localhost",
        "port": 5432,
        "database": "rag_db",
        "user": "user",
        "password": "password",
    }

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT username, role FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            print("❌ 用户不存在")
            return False

        username, current_role = result

        if current_role == "admin":
            print(f"ℹ️  用户 {username} 已经是管理员")
            return True

        # 提升权限
        cursor.execute(
            "UPDATE users SET role = 'admin', updated_at = %s WHERE id = %s",
            (datetime.now(), user_id),
        )
        conn.commit()

        print(f"✅ 用户 {username} 已提升为管理员")
        return True

    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def main():
    """主函数"""

    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        print("🔐 RAG UI 用户管理工具")
        print("=" * 30)
        print("1. 创建管理员账户")
        print("2. 查看用户列表")
        print("3. 提升用户为管理员")
        print("4. 退出")

        choice = input("\n请选择操作 (1-4): ").strip()

        if choice == "1":
            action = "create"
        elif choice == "2":
            action = "list"
        elif choice == "3":
            action = "promote"
        elif choice == "4":
            action = "exit"
        else:
            print("❌ 无效选择")
            return

    if action == "create":
        create_admin_user()
    elif action == "list":
        list_users()
    elif action == "promote":
        promote_user()
    elif action == "exit":
        print("👋 再见!")
    else:
        print("❌ 未知操作")
        print("用法: python3 create_admin.py [create|list|promote]")


if __name__ == "__main__":
    main()
