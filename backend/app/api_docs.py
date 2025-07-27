"""
API Documentation Configuration and Examples
为Swagger文档提供详细的配置、示例和元数据
"""

# API Tags Metadata with enhanced descriptions
TAGS_METADATA = [
    {
        "name": "authentication",
        "description": """
        ## 用户认证和授权
        
        提供完整的用户认证功能，包括：
        - 🔐 用户注册和登录
        - 🎫 JWT令牌生成和验证
        - 👤 用户信息获取
        - 🛡️ 权限验证
        
        ### 认证流程
        1. 用户注册 (`/auth/register`)
        2. 用户登录 (`/auth/login`) 获取JWT令牌
        3. 在请求头中包含 `Authorization: Bearer <token>`
        4. 访问受保护的API端点
        """,
        "externalDocs": {
            "description": "JWT认证最佳实践",
            "url": "https://jwt.io/introduction/",
        },
    },
    {
        "name": "users",
        "description": """
        ## 用户管理
        
        用户账户管理功能：
        - 👥 用户信息管理
        - 🔒 角色权限控制 (USER/ADMIN)
        - ✅ 账户状态管理
        - 📊 用户数据统计
        """,
    },
    {
        "name": "dify",
        "description": """
        ## Dify平台集成
        
        与Dify AI平台的核心集成：
        - ⚙️ Dify API配置管理
        - 🔑 API密钥配置
        - 🌐 多环境支持
        - 📡 连接状态监控
        
        ### 配置说明
        Dify是一个开源的LLM应用开发平台，支持多种AI模型和工作流。
        """,
        "externalDocs": {
            "description": "Dify官方文档",
            "url": "https://docs.dify.ai/",
        },
    },
    {
        "name": "apps",
        "description": """
        ## Dify应用管理
        
        管理多个Dify应用实例：
        - 🚀 应用创建和配置
        - 📱 多应用类型支持 (聊天机器人、工作流、智能体等)
        - 🔧 应用参数配置
        - 📈 应用状态监控
        
        ### 支持的应用类型
        - **CHATBOT**: 对话机器人
        - **WORKFLOW**: 工作流应用
        - **CHATFLOW**: 对话流
        - **AGENT**: 智能体
        - **TEXT_GENERATOR**: 文本生成器
        """,
    },
    {
        "name": "chat",
        "description": """
        ## 聊天和对话
        
        实时AI对话功能：
        - 💬 流式对话响应
        - 🔄 对话历史管理
        - 🎯 多应用选择
        - 📝 对话上下文保持
        
        ### 特性
        - 支持Server-Sent Events (SSE) 流式响应
        - 自动对话ID管理
        - 用户会话隔离
        """,
    },
    {
        "name": "files",
        "description": """
        ## 文件上传和管理
        
        文档处理和知识库管理：
        - 📄 多格式文档上传
        - 🔍 文档内容解析
        - 📚 知识库集成
        - 🏷️ 文件标签管理
        
        ### 支持格式
        - PDF, DOC, DOCX
        - TXT, MD
        - JSON, CSV
        """,
    },
    {
        "name": "health",
        "description": """
        ## 系统健康检查
        
        服务状态监控：
        - ❤️ 系统健康状态
        - 📊 性能指标
        - 🔍 服务可用性检查
        - 📈 系统信息
        """,
    },
]

# API Examples for different endpoints
API_EXAMPLES = {
    "auth_register": {
        "summary": "注册新用户",
        "description": "创建新的用户账户，支持普通用户和管理员角色",
        "value": {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "securePassword123",
            "role": "user",
        },
    },
    "auth_login": {
        "summary": "用户登录",
        "description": "使用用户名和密码进行身份验证",
        "value": {"username": "john_doe", "password": "securePassword123"},
    },
    "dify_config": {
        "summary": "配置Dify API",
        "description": "设置Dify平台的API地址和访问密钥",
        "value": {
            "api_url": "https://api.dify.ai/v1",
            "api_key": "app-xxxxxxxxxxxxxxxxxx",
        },
    },
    "dify_app_create": {
        "summary": "创建Dify应用",
        "description": "配置新的Dify应用实例",
        "value": {
            "name": "客服聊天机器人",
            "app_type": "chatbot",
            "api_key": "app-xxxxxxxxxxxxxxxxxx",
            "api_url": "https://api.dify.ai/v1",
            "description": "用于客户服务的智能聊天机器人",
        },
    },
    "chat_message": {
        "summary": "发送聊天消息",
        "description": "与AI助手进行对话",
        "value": {
            "query": "你好，请介绍一下你的功能",
            "conversation_id": "conv_123456789",
        },
    },
}

# Response Examples
RESPONSE_EXAMPLES = {
    "user_response": {
        "summary": "用户信息响应",
        "value": {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "role": "user",
            "is_active": True,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
        },
    },
    "token_response": {
        "summary": "认证令牌响应",
        "value": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
        },
    },
    "dify_app_response": {
        "summary": "Dify应用信息",
        "value": {
            "id": 1,
            "name": "客服聊天机器人",
            "app_type": "chatbot",
            "api_key": "app-xxxxxxxxxxxxxxxxxx",
            "api_url": "https://api.dify.ai/v1",
            "description": "用于客户服务的智能聊天机器人",
            "is_active": True,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
        },
    },
}

# Error Response Examples
ERROR_EXAMPLES = {
    "400": {
        "description": "请求参数错误",
        "content": {
            "application/json": {"example": {"detail": "Username already registered"}}
        },
    },
    "401": {
        "description": "认证失败",
        "content": {
            "application/json": {
                "example": {"detail": "Incorrect username or password"}
            }
        },
    },
    "403": {
        "description": "权限不足",
        "content": {
            "application/json": {"example": {"detail": "Insufficient permissions"}}
        },
    },
    "404": {
        "description": "资源未找到",
        "content": {"application/json": {"example": {"detail": "Resource not found"}}},
    },
    "500": {
        "description": "服务器内部错误",
        "content": {
            "application/json": {"example": {"detail": "Internal server error"}}
        },
    },
}

# OpenAPI Schema Extensions
OPENAPI_EXTENSIONS = {
    "info": {
        "x-logo": {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
            "altText": "RAG UI Backend",
        }
    }
}
