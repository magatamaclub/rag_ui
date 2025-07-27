"""
Swagger UI Configuration
配置Swagger UI的自定义样式和功能
"""

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def custom_openapi_schema(app: FastAPI):
    """
    自定义OpenAPI模式，增强Swagger文档
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="RAG UI Backend API",
        version="1.0.0",
        description="""
        # RAG UI Backend API 文档
        
        这是一个功能完整的RAG（检索增强生成）应用后端服务，集成了Dify AI平台。
        
        ## 🚀 主要功能
        
        ### 用户认证系统
        - **JWT认证**: 安全的令牌认证机制
        - **角色管理**: 支持USER和ADMIN角色
        - **权限控制**: 基于角色的访问控制
        
        ### Dify平台集成
        - **配置管理**: Dify API配置和密钥管理
        - **应用管理**: 支持多个Dify应用实例
        - **实时聊天**: 与AI模型的流式对话
        
        ### 文件处理
        - **文档上传**: 支持多种格式文档
        - **内容解析**: 自动文档内容提取
        - **知识库**: 文档向量化和检索
        
        ## 📚 使用指南
        
        ### 1. 获取访问令牌
        ```bash
        curl -X POST "http://localhost:8001/api/v1/auth/login" \\
             -H "Content-Type: application/json" \\
             -d '{"username": "your_username", "password": "your_password"}'
        ```
        
        ### 2. 使用令牌访问API
        ```bash
        curl -X GET "http://localhost:8001/api/v1/auth/me" \\
             -H "Authorization: Bearer YOUR_TOKEN_HERE"
        ```
        
        ### 3. 配置Dify集成
        ```bash
        curl -X POST "http://localhost:8001/api/v1/dify-config" \\
             -H "Authorization: Bearer YOUR_TOKEN_HERE" \\
             -H "Content-Type: application/json" \\
             -d '{"api_url": "https://api.dify.ai/v1", "api_key": "your_dify_key"}'
        ```
        
        ## 🔧 开发环境设置
        
        1. **后端启动**:
           ```bash
           cd backend
           python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
           ```
        
        2. **前端启动**:
           ```bash
           cd frontend
           npm run dev
           ```
        
        ## 📞 联系支持
        
        - **邮箱**: support@ragui.com
        - **文档**: http://localhost:8001/docs
        - **ReDoc**: http://localhost:8001/redoc
        
        ## 🔐 安全说明
        
        - 所有API端点都使用HTTPS（生产环境）
        - JWT令牌有效期为24小时
        - 密码使用BCrypt加密存储
        - API密钥安全存储，支持掩码显示
        
        ---
        *本API文档自动生成，实时更新*
        """,
        routes=app.routes,
    )

    # 添加自定义配置
    openapi_schema["info"]["x-logo"] = {
        "url": "https://raw.githubusercontent.com/langgenius/dify/main/web/public/logo/logo.svg",
        "altText": "RAG UI Logo",
    }

    # 添加服务器信息
    openapi_schema["servers"] = [
        {"url": "http://localhost:8001", "description": "开发环境"},
        {"url": "https://api.ragui.com", "description": "生产环境"},
    ]

    # 添加安全方案
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT认证令牌。格式：Bearer <token>",
        }
    }

    # 添加全局安全要求
    openapi_schema["security"] = [{"bearerAuth": []}]

    # 添加API分组标签的详细描述
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "🔐 **用户认证和授权**\n\n管理用户注册、登录、JWT令牌验证等认证相关功能。",
            "externalDocs": {
                "description": "JWT认证文档",
                "url": "https://jwt.io/introduction/",
            },
        },
        {
            "name": "users",
            "description": "👥 **用户管理**\n\n用户账户管理、角色权限控制、用户信息维护等功能。",
        },
        {
            "name": "dify",
            "description": "🤖 **Dify平台集成**\n\n与Dify AI平台的配置管理、连接验证、参数设置等功能。",
            "externalDocs": {
                "description": "Dify官方文档",
                "url": "https://docs.dify.ai/",
            },
        },
        {
            "name": "apps",
            "description": "📱 **Dify应用管理**\n\n管理多个Dify应用实例，支持聊天机器人、工作流、智能体等应用类型。",
        },
        {
            "name": "chat",
            "description": "💬 **AI聊天对话**\n\n与AI模型进行实时对话，支持流式响应、对话历史、上下文保持等功能。",
        },
        {
            "name": "files",
            "description": "📁 **文件上传和管理**\n\n文档上传、内容解析、知识库管理、文件元数据处理等功能。",
        },
        {
            "name": "health",
            "description": "❤️ **系统健康检查**\n\n服务状态监控、性能指标、系统信息查看等功能。",
        },
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def configure_swagger_ui():
    """
    配置Swagger UI的自定义参数
    """
    return {
        "swagger_ui_parameters": {
            "deepLinking": True,
            "displayRequestDuration": True,
            "docExpansion": "list",
            "filter": True,
            "showExtensions": True,
            "showCommonExtensions": True,
            "syntaxHighlight.theme": "arta",
            "tryItOutEnabled": True,
            "requestSnippetsEnabled": True,
            "defaultModelsExpandDepth": 2,
            "defaultModelExpandDepth": 2,
            "displayOperationId": False,
            "supportedSubmitMethods": ["get", "post", "put", "delete", "patch"],
        }
    }


# API示例数据
API_EXAMPLES = {
    "user_register": {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "securePassword123",
        "role": "user",
    },
    "user_login": {"username": "john_doe", "password": "securePassword123"},
    "dify_config": {
        "api_url": "https://api.dify.ai/v1",
        "api_key": "app-xxxxxxxxxxxxxxxxxx",
    },
    "dify_app": {
        "name": "客服聊天机器人",
        "app_type": "chatbot",
        "api_key": "app-xxxxxxxxxxxxxxxxxx",
        "api_url": "https://api.dify.ai/v1",
        "description": "用于客户服务的智能聊天机器人",
    },
    "chat_message": {
        "query": "你好，请介绍一下你的功能",
        "conversation_id": "conv_123456789",
    },
}
