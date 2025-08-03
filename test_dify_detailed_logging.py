#!/usr/bin/env python3
"""
测试 Dify API 详细日志记录功能
"""

import requests
import json
import time

def test_detailed_dify_logging():
    """测试详细的 Dify API 日志记录"""
    
    BASE_URL = "http://localhost:8001"
    
    print("🧪 测试 Dify API 详细日志记录功能...")
    
    # 1. 登录获取token
    print("\n1. 获取认证token...")
    try:
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
            "username": "test_json_user",
            "password": "test123"
        }, timeout=10)
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            print(f"✅ 登录成功，token: {token[:20]}...")
        else:
            print(f"❌ 登录失败: {login_response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 测试通用聊天接口的详细日志
    print("\n2. 测试通用聊天接口 (/api/v1/chat) 的详细日志...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    chat_data = {
        "query": "测试详细日志记录功能 - 通用聊天接口",
        "conversation_id": "detailed-log-test-general"
    }
    
    try:
        print("📤 发送请求到通用聊天接口...")
        print("🔍 请查看服务器日志中的详细请求和响应信息")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            headers=headers,
            json=chat_data,
            timeout=10,
            stream=True
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 通用聊天接口请求成功！")
            # 读取几行流式响应
            lines_read = 0
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    lines_read += 1
                    if lines_read <= 2:
                        print(f"📦 接收数据: {line[:80]}...")
                    if lines_read >= 2:
                        break
        else:
            error_detail = response.json()
            print(f"❌ 通用聊天接口错误: {error_detail.get('detail', 'Unknown error')}")
            
    except requests.exceptions.Timeout:
        print("⏰ 通用聊天接口超时 (可能是流式响应，属正常)")
    except Exception as e:
        print(f"❌ 通用聊天接口异常: {e}")
    
    # 3. 等待一下，让日志输出完整
    print("\n⏳ 等待日志输出完整...")
    time.sleep(2)
    
    # 4. 测试应用特定聊天接口的详细日志
    print("\n3. 测试应用特定聊天接口 (/api/v1/chat/app/1) 的详细日志...")
    
    app_chat_data = {
        "query": "测试详细日志记录功能 - 应用特定聊天接口",
        "conversation_id": "detailed-log-test-app"
    }
    
    try:
        print("📤 发送请求到应用特定聊天接口...")
        print("🔍 请查看服务器日志中的详细请求和响应信息")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/app/1",
            headers=headers,
            json=app_chat_data,
            timeout=10,
            stream=True
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 应用特定聊天接口请求成功！")
            # 读取几行流式响应
            lines_read = 0
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    lines_read += 1
                    if lines_read <= 2:
                        print(f"📦 接收数据: {line[:80]}...")
                    if lines_read >= 2:
                        break
        else:
            error_detail = response.json()
            print(f"❌ 应用特定聊天接口错误: {error_detail.get('detail', 'Unknown error')}")
            
    except requests.exceptions.Timeout:
        print("⏰ 应用特定聊天接口超时 (可能是流式响应，属正常)")
    except Exception as e:
        print(f"❌ 应用特定聊天接口异常: {e}")

def show_logging_features():
    """显示详细日志功能说明"""
    
    print(f"\n" + "="*60)
    print("📋 Dify API 详细日志功能说明")
    print("="*60)
    
    print("""
🔍 新增的详细日志功能:

1. 📤 请求详情记录:
   ✅ 完整的请求URL
   ✅ 请求方法 (POST)
   ✅ 请求头部 (隐藏敏感信息)
   ✅ 请求载荷的详细结构
   ✅ 请求载荷大小

2. 📥 响应详情记录:
   ✅ 响应时间统计
   ✅ HTTP状态码和状态文本
   ✅ 完整的响应头部
   ✅ 流式传输模式信息
   ✅ Content-Type信息

3. 🔄 流式响应处理记录:
   ✅ 数据块计数和进度报告
   ✅ 重要事件类型识别
   ✅ 答案预览 (仅前几个块)
   ✅ 非JSON数据警告
   ✅ SSE头部信息

4. ❌ 错误处理增强:
   ✅ 详细的错误状态码
   ✅ 完整的错误响应内容
   ✅ 错误内容长度统计

5. 📊 性能统计:
   ✅ 总响应时间
   ✅ 处理的数据块总数
   ✅ 接收的数据总大小

6. 🔒 安全性考虑:
   ✅ API密钥自动脱敏显示
   ✅ 敏感信息保护

🎯 日志查看方式:
- 在后端服务器控制台查看实时日志
- 日志级别: INFO (正常操作), ERROR (错误), WARNING (警告)
- 使用表情符号便于快速识别不同类型的信息

💡 建议:
- 生产环境可以调整日志级别以减少输出
- 可以将详细日志输出到文件进行持久化存储
- 根据需要调整进度报告的频率 (当前每10个块报告一次)
""")

if __name__ == "__main__":
    test_detailed_dify_logging()
    show_logging_features()
