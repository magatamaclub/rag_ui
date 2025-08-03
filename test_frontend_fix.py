#!/usr/bin/env python3
"""
测试前端修复后的聊天功能
"""

import requests
import json


def test_chat_endpoint():
    """测试聊天端点是否能正确接收请求体"""

    BASE_URL = "http://localhost:8001"

    print("🧪 测试前端修复后的聊天功能...")

    # 1. 登录获取token
    print("\n1. 登录获取token...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "test_json_user", "password": "test123"},
            timeout=10,
        )

        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print(f"✅ 登录成功，token: {token[:20]}...")
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return

    # 2. 测试聊天接口 - 模拟前端修复后的请求
    print("\n2. 测试修复后的聊天请求...")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    chat_data = {
        "query": "你好，这是前端修复后的测试消息",
        "conversation_id": "frontend-fix-test-123",
    }

    try:
        print("📤 发送请求到: /api/v1/chat/app/1")
        print(f"📋 请求头: {headers}")
        print(f"📦 请求体: {json.dumps(chat_data, ensure_ascii=False)}")

        response = requests.post(
            f"{BASE_URL}/api/v1/chat/app/1",
            headers=headers,
            json=chat_data,  # 使用 json 参数确保正确序列化
            timeout=30,
        )

        print(f"\n📡 响应状态码: {response.status_code}")

        if response.status_code == 200:
            print("✅ 请求成功！开始接收流式响应...")

            # 读取前几行流式响应
            lines_read = 0
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    lines_read += 1
                    print(f"📦 接收到数据 #{lines_read}: {line[:100]}...")
                    if lines_read >= 3:  # 只读取前3行作为示例
                        print("📝 (只显示前3行，实际会有更多数据...)")
                        break

        elif response.status_code == 400:
            try:
                error_detail = response.json()
                print(f"❌ 400错误详情: {error_detail.get('detail', 'Unknown error')}")
            except:
                print(f"❌ 400错误，响应内容: {response.text[:200]}...")
        else:
            print(f"❌ 其他错误: {response.status_code} - {response.text[:200]}...")

    except requests.exceptions.Timeout:
        print("⏰ 请求超时 (这可能是正常的，因为是流式响应)")
    except Exception as e:
        print(f"❌ 请求异常: {e}")


def show_fix_summary():
    """显示修复总结"""

    print("\n" + "=" * 60)
    print("🎯 前端问题修复总结")
    print("=" * 60)

    print("""
🔍 发现的问题:
1. 前端 ChatPage.tsx 使用了错误的参数格式
2. 使用了 `body` 参数而不是 `data` 参数
3. 通过 authenticatedRequest 包装器传递了不兼容的参数
4. request.ts 函数不支持流式响应

🛠️ 修复措施:
1. ✅ 修改 ChatPage.tsx 直接使用 fetch API
2. ✅ 正确设置 Content-Type 和 Authorization 头部
3. ✅ 使用 JSON.stringify 正确序列化请求体
4. ✅ 保持流式响应处理逻辑不变

📝 修复后的前端代码:
```typescript
const response = await fetch(`/api/v1/chat/app/\${selectedAppId}`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer \${token}`,
  },
  body: JSON.stringify({
    query: newMessage.text,
    conversation_id: currentConversationId,
  }),
});
```

✅ 现在前端应该能正确发送JSON数据到后端了！
""")


if __name__ == "__main__":
    test_chat_endpoint()
    show_fix_summary()
