# Swagger API文档使用指南

## 📚 概述

本项目已经成功配置了完整的Swagger API文档，提供了丰富的API说明、示例和交互功能。

## 🌐 访问地址

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **OpenAPI Schema**: http://localhost:8001/openapi.json

## 🚀 主要功能

### 1. 完整的API文档
- ✅ 所有API端点的详细说明
- ✅ 请求/响应模型定义
- ✅ 参数说明和示例
- ✅ 错误代码和处理

### 2. 中文文档支持
- ✅ 中文接口描述
- ✅ 详细的使用说明
- ✅ 功能特性介绍
- ✅ 错误信息说明

### 3. 交互式测试
- ✅ 在线API测试
- ✅ 认证令牌集成
- ✅ 实时响应查看
- ✅ 错误调试支持

### 4. 代码示例
- ✅ cURL命令示例
- ✅ 请求体示例
- ✅ 响应数据示例
- ✅ 认证流程示例

## 📋 API分组说明

### 🔐 认证模块 (authentication)
- **POST /auth/register** - 用户注册
- **POST /auth/login** - 用户登录
- **GET /auth/me** - 获取当前用户信息
- **GET /auth/protected** - 受保护的示例端点

### 🤖 Dify集成 (dify)
- **POST /dify-config** - 配置Dify API
- **GET /dify-config** - 获取Dify配置

### 📱 应用管理 (apps)
- **POST /dify-apps** - 创建Dify应用
- **GET /dify-apps** - 获取应用列表
- **GET /dify-apps/{app_id}** - 获取应用详情
- **PUT /dify-apps/{app_id}** - 更新应用
- **DELETE /dify-apps/{app_id}** - 删除应用

### 💬 聊天对话 (chat)
- **POST /chat** - AI聊天对话
- **POST /chat/app/{app_id}** - 指定应用聊天

### 📁 文件管理 (files)
- **POST /documents** - 上传文档

### ❤️ 系统监控 (health)
- **GET /** - 根路径健康检查
- **GET /health** - 详细健康检查

## 🔧 使用步骤

### 1. 启动服务
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 2. 访问文档
打开浏览器访问: http://localhost:8001/docs

### 3. 测试API
1. 点击任意API端点
2. 点击"Try it out"按钮
3. 填写请求参数
4. 点击"Execute"执行

### 4. 认证流程
1. 使用 `/auth/register` 注册用户
2. 使用 `/auth/login` 获取令牌
3. 点击页面右上角"Authorize"按钮
4. 输入令牌格式：`Bearer YOUR_TOKEN_HERE`
5. 现在可以访问需要认证的API

## 📝 示例用法

### 用户注册
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "password123",
    "role": "user"
  }'
```

### 用户登录
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 配置Dify
```bash
curl -X POST "http://localhost:8001/api/v1/dify-config" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "api_url": "https://api.dify.ai/v1",
    "api_key": "your-dify-api-key"
  }'
```

### AI聊天
```bash
curl -X POST "http://localhost:8001/api/v1/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "你好，请介绍一下你的功能",
    "conversation_id": "conv_123"
  }'
```

## 🎨 文档特性

### 响应示例
每个API端点都包含：
- 成功响应示例
- 错误响应示例
- 数据模型定义
- 参数说明

### 错误处理
标准化的错误响应格式：
```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 认证说明
- JWT Bearer令牌认证
- 令牌有效期24小时
- 自动令牌验证
- 权限级别控制

## 🔍 高级功能

### 1. 搜索过滤
- 使用顶部搜索框快速查找API
- 支持端点名称和描述搜索
- 实时搜索结果

### 2. 模型展开
- 点击模型名称查看完整结构
- 支持嵌套模型展开
- 字段类型和约束说明

### 3. 代码生成
- 自动生成多种语言的代码示例
- 支持cURL、Python、JavaScript等
- 复制粘贴即可使用

### 4. 深度链接
- 每个API端点都有唯一URL
- 支持直接分享特定API文档
- 浏览器书签支持

## 📊 开发调试

### 日志查看
Swagger文档包含完整的请求/响应日志，方便调试：
- 请求头和参数
- 响应状态码
- 响应时间
- 错误详情

### 性能监控
- 请求响应时间显示
- API调用次数统计
- 错误率监控

## 🛠️ 自定义配置

项目使用了以下文件来配置Swagger文档：

- `app/api_docs.py` - API标签和描述定义
- `app/swagger_config.py` - Swagger UI自定义配置
- `app/api_models.py` - 响应模型和示例
- `app/main.py` - FastAPI应用配置

### 添加新的API文档
1. 在相应的路由函数上添加装饰器参数
2. 定义清晰的summary和description
3. 添加请求/响应示例
4. 更新API标签分组

### 自定义主题
可以在`swagger_config.py`中修改UI参数：
- 主题颜色
- 布局设置
- 功能开关
- 显示选项

## 📞 技术支持

如有问题，请查看：
- 项目README文档
- API错误响应说明
- 开发者控制台日志
- 项目GitHub Issues

---

**注意**: 确保后端服务正在运行在8001端口，否则无法访问文档。
