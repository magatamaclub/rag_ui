# RAG UI 系统 - 用户认证功能

## 🔐 新增功能

本项目已成功添加了完整的用户认证系统，包括：

- 用户注册和登录
- JWT Token 认证
- 密码加密存储
- 前端登录页面
- 路由保护

## 🚀 快速启动

### 方法一：使用一键启动脚本
```bash
./start-with-auth.sh
```

### 方法二：分别启动各服务
```bash
# 1. 启动数据库
docker-compose up -d

# 2. 启动后端 (新终端)
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 启动前端 (新终端)
cd frontend
pnpm run dev
```

## 📍 访问地址

- **前端应用**: http://localhost:8001
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 🔑 认证功能使用说明

### 1. 用户注册
- 访问 http://localhost:8001/login
- 点击"注册"选项卡
- 填写用户名、邮箱、密码
- 点击"注册"按钮

### 2. 用户登录
- 在登录页面的"登录"选项卡
- 输入用户名和密码
- 点击"登录"按钮
- 登录成功后将跳转到聊天页面

### 3. 自动跳转
- 未登录用户访问任何页面都会自动跳转到登录页面
- 登录成功后会跳转到原来要访问的页面

## 🧪 测试认证功能

### 使用测试脚本
```bash
./test-auth.sh
```

### 手动测试 API
```bash
# 注册用户
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123"
  }'

# 登录获取 token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# 使用 token 访问受保护端点
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📁 新增文件结构

```
backend/
├── app/
│   ├── auth.py          # JWT 认证逻辑
│   ├── schemas.py       # Pydantic 数据模型
│   └── models.py        # 数据库用户模型 (已更新)

frontend/
├── src/
│   ├── pages/
│   │   └── LoginPage.tsx    # 登录注册页面
│   ├── components/
│   │   └── ProtectedRoute.tsx # 路由保护组件
│   └── utils/
│       ├── auth.ts          # 认证工具函数
│       └── request.ts       # HTTP 请求工具

# 启动和测试脚本
├── start-with-auth.sh   # 一键启动脚本
└── test-auth.sh         # 认证功能测试脚本
```

## ⚙️ 技术实现细节

### 后端 (FastAPI)
- **JWT Token**: 使用 `python-jose` 生成和验证 JWT
- **密码加密**: 使用 `bcrypt` 进行密码哈希
- **数据库**: PostgreSQL 存储用户信息
- **依赖注入**: FastAPI 依赖系统进行认证检查

### 前端 (React + Umi)
- **状态管理**: localStorage 存储 JWT token
- **路由保护**: `ProtectedRoute` 组件检查认证状态
- **UI 组件**: Ant Design 提供美观的登录界面
- **HTTP 请求**: 自定义 request 工具自动添加认证头

## 🔧 配置选项

### JWT 配置 (backend/app/auth.py)
```python
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境请更改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token 过期时间
```

### 数据库配置 (docker-compose.yml)
```yaml
POSTGRES_USER: rag_user
POSTGRES_PASSWORD: rag_password
POSTGRES_DB: rag_database
```

## 📝 注意事项

1. **生产环境**: 请更改 JWT SECRET_KEY
2. **HTTPS**: 生产环境建议使用 HTTPS
3. **Token 存储**: 目前使用 localStorage，可考虑更安全的存储方式
4. **密码策略**: 可添加更强的密码复杂度要求

## 🎯 下一步功能

- [ ] 用户角色和权限管理
- [ ] 密码重置功能
- [ ] 社交登录集成
- [ ] 用户个人资料管理
- [ ] 登录日志和安全审计

## 🐛 故障排除

### 前端编译错误
```bash
# 清理并重新安装依赖
cd frontend
rm -rf node_modules .umi .cache
pnpm install
```

### 后端认证错误
检查：
1. 数据库连接是否正常
2. JWT SECRET_KEY 是否配置
3. Token 是否正确传递

### 数据库连接问题
```bash
# 重启数据库容器
docker-compose down
docker-compose up -d
```

---

🎉 **用户登录功能已完整实现！** 现在您可以：
1. 运行 `./start-with-auth.sh` 启动系统
2. 访问 http://localhost:8001/login 体验登录功能
3. 使用 `./test-auth.sh` 测试 API 功能
