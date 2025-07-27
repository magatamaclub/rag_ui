#!/usr/bin/env python3
"""
测试数据库初始化API的脚本
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8001"


def test_database_status():
    """测试数据库状态检查API"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/database/status")
        print(f"Status Check Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None


def test_database_initialization():
    """测试数据库初始化API"""
    try:
        response = requests.post(f"{BASE_URL}/api/v1/database/initialize")
        print(f"Initialize Response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Error: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None


if __name__ == "__main__":
    print("=" * 50)
    print("测试数据库初始化API")
    print("=" * 50)

    print("\n1. 检查数据库状态:")
    status = test_database_status()

    if status and not status.get("is_initialized", True):
        print("\n2. 初始化数据库:")
        init_result = test_database_initialization()

        if init_result and init_result.get("success"):
            print("\n3. 再次检查状态:")
            test_database_status()
    else:
        print("\n数据库已初始化或检查失败")
