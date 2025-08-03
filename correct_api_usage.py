#!/usr/bin/env python3
"""
正确调用 /api/v1/chat/app/1 接口的示例代码
"""

import requests
import json


def correct_api_call_example():
    """演示正确的API调用方式"""

    BASE_URL = "http://localhost:8001"

    # 1. 先登录获取 token
    print("🔐 Step 1: 登录获取token")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": "test_json_user", "password": "test123"},
    )

    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        return

    token = login_response.json()["access_token"]
    print(f"✅ 登录成功，获取token: {token[:20]}...")

    # 2. 设置正确的请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",  # 这个很重要！
    }

    # 3. 准备请求数据
    chat_data = {
        "query": "你好，请介绍一下你的功能",
        "conversation_id": "test-conversation-123",  # 可选
    }

    # 4. 发送请求 - 方式1：使用 requests.post(json=...)
    print("\n💬 Step 2: 发送聊天请求（方式1 - 推荐）")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/app/1",
            json=chat_data,  # 使用 json 参数，自动设置 Content-Type
            headers={"Authorization": f"Bearer {token}"},  # 只需要认证头
            timeout=30,
        )

        print(f"📡 响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 请求成功！开始接收流式响应...")
            # 处理流式响应
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    print(f"📦 收到数据: {line[:100]}...")
                    if "data: " in line:
                        break  # 只显示第一条数据作为示例
        else:
            print(f"❌ 请求失败: {response.text}")

    except Exception as e:
        print(f"❌ 请求异常: {e}")

    # 5. 发送请求 - 方式2：手动设置 JSON 数据
    print("\n💬 Step 3: 发送聊天请求（方式2 - 手动JSON）")
    try:
        headers_with_content_type = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",  # 手动设置
        }

        response = requests.post(
            f"{BASE_URL}/api/v1/chat/app/1",
            data=json.dumps(chat_data),  # 手动序列化JSON
            headers=headers_with_content_type,
            timeout=30,
        )

        print(f"📡 响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 方式2也成功！")
        else:
            print(f"❌ 方式2失败: {response.text}")

    except Exception as e:
        print(f"❌ 方式2异常: {e}")


def show_frontend_examples():
    """显示前端调用示例"""

    print("\n" + "=" * 60)
    print("🌐 前端调用示例")
    print("=" * 60)

    print("""
// ✅ JavaScript/TypeScript - 使用 fetch
async function chatWithApp(query, conversationId = null) {
    const token = localStorage.getItem('authToken'); // 假设token存储在localStorage
    
    const response = await fetch('/api/v1/chat/app/1', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            query: query,
            conversation_id: conversationId
        })
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(`API Error: ${error.detail}`);
    }
    
    // 处理流式响应
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        console.log('Received:', chunk);
    }
}

// ✅ JavaScript/TypeScript - 使用 axios
import axios from 'axios';

async function chatWithAppAxios(query, conversationId = null) {
    const token = localStorage.getItem('authToken');
    
    const response = await axios.post('/api/v1/chat/app/1', {
        query: query,
        conversation_id: conversationId
    }, {
        headers: {
            'Authorization': `Bearer ${token}`
        },
        responseType: 'stream' // 对于流式响应
    });
    
    return response.data;
}

// ✅ React 示例
import React, { useState } from 'react';

function ChatComponent() {
    const [message, setMessage] = useState('');
    const [response, setResponse] = useState('');
    
    const handleSendMessage = async () => {
        try {
            const token = localStorage.getItem('authToken');
            
            const res = await fetch('/api/v1/chat/app/1', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    query: message
                })
            });
            
            if (!res.ok) {
                const error = await res.json();
                console.error('API Error:', error.detail);
                return;
            }
            
            // 处理流式响应...
            console.log('Message sent successfully');
            
        } catch (error) {
            console.error('Request failed:', error);
        }
    };
    
    return (
        <div>
            <input 
                value={message} 
                onChange={(e) => setMessage(e.target.value)}
                placeholder="输入消息..."
            />
            <button onClick={handleSendMessage}>发送</button>
        </div>
    );
}
""")


if __name__ == "__main__":
    correct_api_call_example()
    show_frontend_examples()
