#!/usr/bin/env python3
"""
测试JSON解析错误修复的脚本
"""

import requests

BASE_URL = "http://127.0.0.1:8001/api/v1"


def test_json_parsing():
    """测试JSON解析错误的修复"""
    print("🧪 测试JSON解析错误修复...")

    # 测试用例1: 空请求体
    print("\n1. 测试空请求体:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/app/1",
            headers={"Content-Type": "application/json"},
            data="",
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")

    # 测试用例2: 无效JSON
    print("\n2. 测试无效JSON:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/app/1",
            headers={"Content-Type": "application/json"},
            data="invalid json content",
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")

    # 测试用例3: 正确的JSON但缺少认证
    print("\n3. 测试正确JSON格式:")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/app/1",
            headers={"Content-Type": "application/json"},
            json={"query": "test message", "conversation_id": "test-123"},
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   错误: {e}")


def test_server_health():
    """测试服务器健康状态"""
    print("\n🏥 测试服务器健康状态...")
    try:
        response = requests.get(f"{BASE_URL}/../")
        print(f"   根路径状态码: {response.status_code}")

        response = requests.get(f"{BASE_URL}/../docs")
        print(f"   文档页面状态码: {response.status_code}")

    except Exception as e:
        print(f"   错误: {e}")


if __name__ == "__main__":
    print("🚀 开始测试JSON解析错误修复...")
    test_server_health()
    test_json_parsing()
    print("\n✅ 测试完成!")
