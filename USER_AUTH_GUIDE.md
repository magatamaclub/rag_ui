# 🔐 用户登录功能快速指南

## 功能概述

RAG UI系统现已添加完整的用户认证功能，包括：

- ✅ 用户注册/登录
- ✅ JWT令牌认证
- ✅ 路由保护
- ✅ 安全的API访问
- ✅ 用户会话管理

## 🚀 快速开始

### 1. 启动开发环境

```bash
# 克隆项目并进入目录
cd /path/to/rag_ui_ant_design

# 启动开发环境（包含数据库、后端、前端）
./start-dev.sh
```

### 2. 访问应用

- **前端界面**: http://localhost:8001
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 3. 首次使用

1. 打开浏览器访问 http://localhost:8001
2. 系统会自动跳转到登录页面
3. 点击"注册"选项卡创建新账户
4. 填写用户名、邮箱和密码
5. 注册成功后自动切换到登录页面
6. 使用刚创建的账户登录

## 🔑 API端点

### 用户认证

| 端点                    | 方法 | 描述             | 需要认证 |
| ----------------------- | ---- | ---------------- | -------- |
| `/api/v1/auth/register` | POST | 注册新用户       | ❌        |
| `/api/v1/auth/login`    | POST | 用户登录         | ❌        |
| `/api/v1/auth/me`       | GET  | 获取当前用户信息 | ✅        |

### 应用功能（需要登录）

| 端点                  | 方法     | 描述         | 需要认证 |
| --------------------- | -------- | ------------ | -------- |
| `/api/v1/chat`        | POST     | 聊天对话     | ✅        |
| `/api/v1/documents`   | POST     | 上传文档     | ✅        |
| `/api/v1/dify-config` | GET/POST | Dify配置管理 | ✅        |

## 🔧 环境配置

### JWT配置（.env文件）

```bash
# JWT密钥（生产环境请使用强密钥）
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-min-32-chars

# 令牌过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rag_db
DB_USER=user
DB_PASSWORD=password
```

## 🔒 安全特性

1. **密码加密**: 使用bcrypt进行密码哈希
2. **JWT令牌**: 安全的无状态认证
3. **路由保护**: 所有主要功能需要登录
4. **令牌验证**: 每次API请求验证令牌有效性
5. **自动登出**: 令牌过期或无效时自动退出

## 📱 前端功能

### 登录页面特性
- 现代化的响应式设计
- 登录/注册选项卡切换
- 表单验证和错误提示
- 渐变背景和美观UI

### 用户体验
- 自动令牌管理
- 用户信息显示
- 优雅的退出功能
- 路由保护重定向

## 🛠️ 开发说明

### 前端认证工具

```typescript
import { authenticatedRequest, isAuthenticated, logout } from '@/utils/auth';

// 检查登录状态
if (!isAuthenticated()) {
  // 跳转到登录页
}

// 发送认证请求
const response = await authenticatedRequest('/api/v1/some-endpoint', {
  method: 'POST',
  data: { ... }
});

// 退出登录
logout();
```

### 后端保护路由

```python
from .auth import get_current_active_user

@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.username}"}
```

## 🐛 故障排除

### 常见问题

1. **无法注册用户**
   - 检查数据库连接
   - 确认用户名/邮箱未被使用

2. **登录失败**
   - 验证用户名和密码
   - 检查后端服务状态

3. **令牌过期**
   - 重新登录获取新令牌
   - 检查 ACCESS_TOKEN_EXPIRE_MINUTES 设置

4. **API请求失败**
   - 确认已登录
   - 检查令牌是否有效
   - 验证API端点是否正确

### 开发调试

```bash
# 查看后端日志
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 查看前端日志
cd frontend
pnpm dev --port 8001

# 查看数据库
docker exec -it rag_ui_ant_design-db-1 psql -U user -d rag_db
```

## 📊 数据库结构

### users表

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🚀 部署说明

### 生产环境安全

1. **更换JWT密钥**: 使用强随机密钥
2. **HTTPS配置**: 确保使用HTTPS传输
3. **数据库安全**: 配置强密码和访问控制
4. **环境变量**: 不要在代码中硬编码敏感信息

### Docker部署

```bash
# 完整Docker部署
docker-compose up -d

# 仅数据库（推荐开发）
docker-compose up -d db
```

---

## 🎉 功能完成！

用户登录功能已完全集成到RAG UI系统中。现在用户可以：

1. 🔐 安全注册和登录
2. 💬 进行认证聊天对话
3. 📄 上传受保护的文档
4. ⚙️ 管理个人配置
5. 🔒 享受全面的安全保护

**开始使用**: 访问 http://localhost:8001 并创建您的账户！
