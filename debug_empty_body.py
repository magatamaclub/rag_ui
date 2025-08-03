#!/usr/bin/env python3
"""
诊断 /api/v1/chat/app/1 接口空请求体问题的工具
"""

import requests
import json

BASE_URL = "http://localhost:8001"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
CHAT_APP_URL = f"{BASE_URL}/api/v1/chat/app/1"


def test_different_request_methods():
    """测试不同的请求方式，找出空请求体的原因"""

    print("🔍 诊断空请求体问题...")

    # 先登录获取token
    print("\n1. 获取认证token...")
    login_data = {"username": "test_json_user", "password": "test123"}

    try:
        response = requests.post(LOGIN_URL, json=login_data, timeout=10)
        if response.status_code != 200:
            print(f"❌ 登录失败: {response.status_code}")
            return

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"✅ 获取token成功: {token[:20]}...")

    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return

    # 测试不同的请求方式
    test_cases = [
        {
            "name": "错误方式1: 使用GET方法",
            "method": "GET",
            "data": None,
            "headers": headers,
        },
        {
            "name": "错误方式2: 使用URL参数",
            "method": "POST",
            "url_params": "?query=测试消息&conversation_id=test-123",
            "data": None,
            "headers": headers,
        },
        {
            "name": "错误方式3: 使用form-data格式",
            "method": "POST",
            "data": "query=测试消息&conversation_id=test-123",
            "headers": {**headers, "Content-Type": "application/x-www-form-urlencoded"},
        },
        {
            "name": "错误方式4: 发送空字符串",
            "method": "POST",
            "data": "",
            "headers": {**headers, "Content-Type": "application/json"},
        },
        {
            "name": "错误方式5: 不设置Content-Type",
            "method": "POST",
            "data": json.dumps({"query": "测试消息"}),
            "headers": headers,  # 没有Content-Type
        },
        {
            "name": "✅ 正确方式: 使用requests.post(json=...)",
            "method": "POST",
            "json_data": {"query": "测试消息", "conversation_id": "test-conv-123"},
            "headers": headers,
        },
        {
            "name": "✅ 正确方式: 手动设置JSON数据和头部",
            "method": "POST",
            "data": json.dumps(
                {"query": "测试消息", "conversation_id": "test-conv-123"}
            ),
            "headers": {**headers, "Content-Type": "application/json"},
        },
    ]

    print("\n2. 测试不同的请求方式...")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")

        try:
            # 构建URL
            url = CHAT_APP_URL + test_case.get("url_params", "")

            # 发送请求
            if test_case["method"] == "GET":
                response = requests.get(url, headers=test_case["headers"], timeout=5)
            elif "json_data" in test_case:
                # 使用requests的json参数
                response = requests.post(
                    url,
                    json=test_case["json_data"],
                    headers=test_case["headers"],
                    timeout=5,
                )
            else:
                # 使用data参数
                response = requests.post(
                    url, data=test_case["data"], headers=test_case["headers"], timeout=5
                )

            print(f"  状态码: {response.status_code}")

            if response.status_code == 400:
                try:
                    error_detail = response.json()
                    print(f"  错误详情: {error_detail.get('detail', 'Unknown error')}")
                except:
                    print(f"  错误内容: {response.text[:100]}...")
            elif response.status_code == 200:
                print("  ✅ 请求成功!")
            elif response.status_code == 405:
                print("  ❌ 方法不允许 (Method Not Allowed)")
            else:
                print(f"  状态: {response.status_code} - {response.reason}")

        except requests.exceptions.Timeout:
            print("  ⏰ 请求超时 (可能是流式响应)")
        except Exception as e:
            print(f"  ❌ 请求异常: {e}")


def show_correct_usage_examples():
    """显示正确的API调用示例"""

    print("\n" + "=" * 60)
    print("📚 正确的API调用示例")
    print("=" * 60)

    print("\n🟢 JavaScript/TypeScript (前端):")
    print("""
// 使用fetch API
const response = await fetch('/api/v1/chat/app/1', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        query: '你好，请介绍一下自己',
        conversation_id: 'uuid-or-leave-empty'  // 可选
    })
});

// 使用axios
const response = await axios.post('/api/v1/chat/app/1', {
    query: '你好，请介绍一下自己',
    conversation_id: 'uuid-or-leave-empty'  // 可选
}, {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
""")

    print("\n🟢 Python requests:")
    print("""
import requests

headers = {'Authorization': f'Bearer {token}'}
data = {
    'query': '你好，请介绍一下自己',
    'conversation_id': 'uuid-or-leave-empty'  # 可选
}

# 方式1: 使用json参数（推荐）
response = requests.post('/api/v1/chat/app/1', json=data, headers=headers)

# 方式2: 手动设置
headers['Content-Type'] = 'application/json'
response = requests.post('/api/v1/chat/app/1', 
                        data=json.dumps(data), 
                        headers=headers)
""")

    print("\n🟢 cURL 命令:")
    print("""
curl -X POST http://localhost:8001/api/v1/chat/app/1 \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -d '{
    "query": "你好，请介绍一下自己",
    "conversation_id": "optional-uuid"
  }'
""")


if __name__ == "__main__":
    test_different_request_methods()
    show_correct_usage_examples()
