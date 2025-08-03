#!/usr/bin/env python3
"""RAG UI 管理员账户创建脚本"""

import hashlib
import getpass
import psycopg2
from datetime import datetime


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
        query = "SELECT id FROM users WHERE username = %s OR email = %s"
        cursor.execute(query, (username, email))
        if cursor.fetchone():
            print("❌ 用户名或邮箱已存在")
            return False

        # 创建用户
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        now = datetime.now()

        insert_query = """
            INSERT INTO users (username, email, hashed_password, role, 
                             is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        cursor.execute(
            insert_query, (username, email, hashed_password, "admin", True, now, now)
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
    except KeyboardInterrupt:
        print("\n❌ 操作被取消")
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

        query = """SELECT id, username, email, role, is_active, created_at 
                   FROM users ORDER BY created_at"""
        cursor.execute(query)
        users = cursor.fetchall()

        print("\n👥 现有用户列表:")
        print("-" * 70)
        print("ID   用户名           邮箱                     权限     状态")
        print("-" * 70)

        for user in users:
            user_id, username, email, role, is_active, created_at = user
            status = "激活" if is_active else "禁用"
            role_cn = "管理员" if role == "admin" else "用户"

            print(f"{user_id:<4} {username:<15} {email:<25} {role_cn:<8} {status}")

        print("-" * 70)
        print(f"总计: {len(users)} 个用户")

    except psycopg2.Error as e:
        print(f"❌ 数据库错误: {e}")
    finally:
        if "conn" in locals():
            conn.close()


def main():
    """主函数"""

    print("🔐 RAG UI 用户管理工具")
    print("=" * 30)
    print("1. 创建管理员账户")
    print("2. 查看用户列表")
    print("3. 退出")

    choice = input("\n请选择操作 (1-3): ").strip()

    if choice == "1":
        create_admin_user()
    elif choice == "2":
        list_users()
    elif choice == "3":
        print("👋 再见!")
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    main()
