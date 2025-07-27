# API文档

## 认证接口

### 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  }
}
```

### 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=string&password=string
```

**响应**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string"
  }
}
```

### 获取当前用户信息
```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

**响应**:
```json
{
  "id": 1,
  "username": "string",
  "email": "string"
}
```

## 核心功能接口

### 获取Dify配置
```http
GET /api/v1/dify-config
Authorization: Bearer {token}
```

**响应**:
```json
{
  "api_url": "string",
  "api_key": "string"
}
```

### 保存Dify配置
```http
POST /api/v1/dify-config
Authorization: Bearer {token}
Content-Type: application/json

{
  "api_url": "string",
  "api_key": "string"
}
```

**响应**:
```json
{
  "message": "Configuration saved successfully"
}
```

### 聊天接口
```http
POST /api/v1/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "string",
  "conversation_id": "string (optional)"
}
```

**响应** (Server-Sent Events):
```
data: {"type": "message", "content": "partial response"}
data: {"type": "message", "content": " continues..."}
data: {"type": "citation", "source": "document.pdf", "page": 1}
data: {"type": "end"}
```

### 文件上传
```http
POST /api/v1/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

files: File[]
```

**响应**:
```json
{
  "uploaded_files": [
    {
      "filename": "document.pdf",
      "size": 1024000,
      "status": "success"
    }
  ]
}
```

## 健康检查接口

### 根路径检查
```http
GET /
```

**响应**:
```json
{
  "Hello": "World"
}
```

### 健康状态检查
```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-07-27T10:00:00Z",
  "database": "connected",
  "dify": "configured"
}
```

## 错误响应格式

### 标准错误响应
```json
{
  "detail": "错误信息描述"
}
```

### 验证错误响应
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 认证错误响应
```json
{
  "detail": "Could not validate credentials"
}
```

## 状态码说明

- `200 OK` - 请求成功
- `201 Created` - 资源创建成功
- `400 Bad Request` - 请求参数错误
- `401 Unauthorized` - 未授权访问
- `403 Forbidden` - 禁止访问
- `404 Not Found` - 资源未找到
- `422 Unprocessable Entity` - 数据验证错误
- `429 Too Many Requests` - 请求频率限制
- `500 Internal Server Error` - 服务器内部错误

## 请求限制

### 速率限制
- 登录接口: 每分钟5次尝试
- 聊天接口: 每分钟60次请求
- 文件上传: 每小时100次上传

### 文件上传限制
- 单文件最大: 10MB
- 总大小限制: 100MB
- 支持格式: PDF, DOCX, TXT, MD

### 请求头要求
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
User-Agent: RAG-UI-Client/1.0
```

## 示例代码

### JavaScript/TypeScript
```typescript
// 认证请求
const login = async (username: string, password: string) => {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({ username, password }),
  });
  return response.json();
};

// 聊天请求
const sendMessage = async (message: string, token: string) => {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });
  return response.body; // ReadableStream for SSE
};
```

### Python
```python
import requests

# 认证请求
def login(username: str, password: str):
    response = requests.post(
        '/api/v1/auth/login',
        data={'username': username, 'password': password}
    )
    return response.json()

# 聊天请求
def send_message(message: str, token: str):
    response = requests.post(
        '/api/v1/chat',
        headers={'Authorization': f'Bearer {token}'},
        json={'message': message},
        stream=True
    )
    return response.iter_lines()
```

### cURL
```bash
# 用户登录
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# 发送聊天消息
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'

# 上传文件
curl -X POST http://localhost:8001/api/v1/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document.pdf"
```

## WebSocket支持

### 实时聊天连接
```http
GET /ws/chat
Authorization: Bearer {token}
```

**消息格式**:
```json
{
  "type": "message",
  "data": {
    "text": "用户消息内容",
    "conversation_id": "optional"
  }
}
```

**服务器响应**:
```json
{
  "type": "response",
  "data": {
    "text": "AI回复内容",
    "citations": ["document1.pdf", "document2.txt"]
  }
}
```

---

*API文档版本: v1.0 | 最后更新: 2025-07-27*
