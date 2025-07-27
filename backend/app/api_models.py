"""
API Response Models and Examples
API响应模型和示例数据
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ErrorResponse(BaseModel):
    """标准错误响应模型"""

    detail: str = Field(description="错误详细信息")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: Optional[datetime] = Field(None, description="错误发生时间")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Username already registered",
                "error_code": "USER_EXISTS",
                "timestamp": "2024-01-01T10:00:00Z",
            }
        }


class SuccessResponse(BaseModel):
    """标准成功响应模型"""

    message: str = Field(description="成功消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "data": {"id": 1, "status": "active"},
            }
        }


class PaginationResponse(BaseModel):
    """分页响应模型"""

    items: List[Dict[str, Any]] = Field(description="数据项列表")
    total: int = Field(description="总数量")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [{"id": 1, "name": "item1"}],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "total_pages": 10,
            }
        }


# API响应示例
RESPONSE_EXAMPLES = {
    # 认证相关响应
    "auth_success": {
        "summary": "认证成功",
        "description": "用户认证成功，返回JWT令牌",
        "value": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsImV4cCI6MTY0MjY4NjQwMH0.signature",
            "token_type": "bearer",
            "expires_in": 1440,
        },
    },
    "user_info": {
        "summary": "用户信息",
        "description": "当前登录用户的详细信息",
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
    # Dify相关响应
    "dify_config": {
        "summary": "Dify配置信息",
        "description": "当前Dify平台配置",
        "value": {
            "api_url": "https://api.dify.ai/v1",
            "api_key": "app-****xxxx",
            "status": "connected",
            "last_updated": "2024-01-01T10:00:00Z",
        },
    },
    "dify_app": {
        "summary": "Dify应用信息",
        "description": "Dify应用的详细配置",
        "value": {
            "id": 1,
            "name": "客服聊天机器人",
            "app_type": "chatbot",
            "api_key": "app-****xxxx",
            "api_url": "https://api.dify.ai/v1",
            "description": "用于客户服务的智能聊天机器人",
            "is_active": True,
            "created_at": "2024-01-01T10:00:00Z",
            "updated_at": "2024-01-01T10:00:00Z",
        },
    },
    # 聊天相关响应
    "chat_response": {
        "summary": "聊天响应",
        "description": "AI助手的流式响应数据",
        "value": {
            "event": "message",
            "conversation_id": "conv_123456789",
            "message_id": "msg_987654321",
            "answer": "你好！我是AI助手，可以帮助您解答问题和处理文档。",
            "metadata": {
                "model": "gpt-3.5-turbo",
                "tokens_used": 25,
                "response_time": 1.2,
            },
        },
    },
    # 文件相关响应
    "file_upload": {
        "summary": "文件上传成功",
        "description": "文档上传到Dify平台的响应",
        "value": {
            "file_id": "file_123456789",
            "filename": "document.pdf",
            "size": 1024000,
            "status": "processed",
            "content_type": "application/pdf",
            "upload_time": "2024-01-01T10:00:00Z",
            "processing_info": {"pages": 10, "words": 5000, "indexed": True},
        },
    },
    # 健康检查响应
    "health_check": {
        "summary": "系统健康状态",
        "description": "服务健康状态和系统信息",
        "value": {
            "status": "healthy",
            "timestamp": "2024-01-01T10:00:00Z",
            "version": "1.0.0",
            "environment": "development",
            "services": {
                "database": "connected",
                "dify_api": "connected",
                "redis": "connected",
            },
            "metrics": {"uptime": "24h 30m", "memory_usage": "45%", "cpu_usage": "12%"},
        },
    },
}

# 错误响应示例
ERROR_EXAMPLES = {
    "400_bad_request": {
        "summary": "请求参数错误",
        "description": "请求包含无效或缺失的参数",
        "value": {
            "detail": "Username already registered",
            "error_code": "VALIDATION_ERROR",
            "timestamp": "2024-01-01T10:00:00Z",
        },
    },
    "401_unauthorized": {
        "summary": "未认证",
        "description": "请求需要用户认证",
        "value": {
            "detail": "Not authenticated",
            "error_code": "AUTH_REQUIRED",
            "timestamp": "2024-01-01T10:00:00Z",
        },
    },
    "403_forbidden": {
        "summary": "权限不足",
        "description": "用户没有访问资源的权限",
        "value": {
            "detail": "Insufficient permissions",
            "error_code": "PERMISSION_DENIED",
            "timestamp": "2024-01-01T10:00:00Z",
        },
    },
    "404_not_found": {
        "summary": "资源未找到",
        "description": "请求的资源不存在",
        "value": {
            "detail": "Resource not found",
            "error_code": "NOT_FOUND",
            "timestamp": "2024-01-01T10:00:00Z",
        },
    },
    "500_internal_error": {
        "summary": "服务器内部错误",
        "description": "服务器处理请求时发生错误",
        "value": {
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": "2024-01-01T10:00:00Z",
        },
    },
}

# HTTP状态码和描述
HTTP_STATUS_CODES = {
    200: "请求成功",
    201: "资源创建成功",
    400: "请求参数错误",
    401: "未认证或认证失败",
    403: "权限不足",
    404: "资源未找到",
    422: "请求参数验证失败",
    500: "服务器内部错误",
    503: "服务暂时不可用",
}

# API标签和分组
API_TAGS = {
    "authentication": {
        "name": "authentication",
        "description": "🔐 用户认证和授权",
        "endpoints": [
            "POST /auth/register",
            "POST /auth/login",
            "GET /auth/me",
            "GET /auth/protected",
        ],
    },
    "dify": {
        "name": "dify",
        "description": "🤖 Dify平台集成",
        "endpoints": ["POST /dify-config", "GET /dify-config"],
    },
    "apps": {
        "name": "apps",
        "description": "📱 Dify应用管理",
        "endpoints": [
            "POST /dify-apps",
            "GET /dify-apps",
            "GET /dify-apps/{app_id}",
            "PUT /dify-apps/{app_id}",
            "DELETE /dify-apps/{app_id}",
        ],
    },
    "chat": {
        "name": "chat",
        "description": "💬 AI聊天对话",
        "endpoints": ["POST /chat", "POST /chat/app/{app_id}"],
    },
    "files": {
        "name": "files",
        "description": "📁 文件上传和管理",
        "endpoints": ["POST /documents"],
    },
    "health": {
        "name": "health",
        "description": "❤️ 系统健康检查",
        "endpoints": ["GET /", "GET /health"],
    },
}
