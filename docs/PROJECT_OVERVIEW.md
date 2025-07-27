# RAG UI with Dify Integration - 项目文档

## 项目概述

这是一个基于检索增强生成（RAG）技术的交互式Web应用，集成了Dify平台，提供智能聊天和文档知识库功能。项目采用前后端分离架构，具备完整的用户认证系统。

## 技术架构

### 前端架构
- **技术栈**: React + TypeScript + UmiJS + Ant Design Pro
- **端口**: 8001
- **主要功能**:
  - 流式聊天界面
  - 用户登录/注册
  - Dify配置管理
  - 文档上传功能
  - 会话管理和持久化

### 后端架构
- **技术栈**: Python + FastAPI + SQLAlchemy + PostgreSQL
- **端口**: 8001
- **主要功能**:
  - JWT用户认证
  - Dify API集成
  - 文件上传处理
  - 数据库管理
  - 自动表初始化

## 项目结构

```
rag_ui_ant_design/
├── backend/                 # FastAPI后端
│   ├── app/                # 核心应用代码
│   │   ├── main.py         # 应用入口
│   │   ├── api.py          # API路由
│   │   ├── models.py       # 数据库模型
│   │   ├── database.py     # 数据库连接
│   │   ├── config.py       # 配置管理
│   │   ├── auth.py         # 认证工具
│   │   └── schemas.py      # Pydantic模型
│   ├── tests/              # 后端测试
│   ├── Dockerfile          # 后端容器化
│   ├── pyproject.toml      # Poetry配置
│   └── quick_start.sh      # 快速启动脚本
├── frontend/               # React前端
│   ├── src/
│   │   ├── pages/          # 页面组件
│   │   │   ├── ChatPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── DifyConfigPage.tsx
│   │   │   └── UploadPage.tsx
│   │   └── utils/          # 工具函数
│   │       ├── request.ts
│   │       └── auth.ts
│   ├── .umirc.ts          # UmiJS配置
│   └── Dockerfile          # 前端容器化
├── docs/                   # 项目文档
├── docker-compose.yml      # 容器编排
├── .env                    # 环境配置
├── .gitignore             # Git忽略规则
└── start-dev.sh           # 本地开发启动脚本
```

## 环境配置

### 必需的环境变量

```env
# 数据库配置
DB_HOST=115.190.34.179      # 数据库主机地址
DB_PORT=5435                # 数据库端口
DB_NAME=rag_ui_db           # 数据库名称
DB_USER=hyanwang            # 数据库用户名
DB_PASSWORD=Tingo123.       # 数据库密码

# 应用配置
APP_HOST=0.0.0.0            # 应用监听地址
APP_PORT=8000               # 应用端口
APP_DEBUG=false             # 调试模式

# JWT认证配置
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 核心功能

### 1. 用户认证系统
- 用户注册和登录
- JWT令牌管理
- 路由保护
- 密码加密存储

### 2. 聊天功能
- 实时流式对话
- 会话管理和切换
- 知识源追溯显示
- 前端会话持久化

### 3. Dify集成
- 动态配置Dify API
- 支持流式聊天响应
- 文档上传到知识库
- 检索结果展示

### 4. 数据管理
- 自动数据库表初始化
- 配置信息持久化
- 用户数据管理

## 启动方式

### 本地开发（推荐）
```bash
# 一键启动开发环境
./start-dev.sh
```

### Docker容器化
```bash
# 使用Docker Compose启动完整环境
docker-compose up --build
```

### 手动启动后端
```bash
cd backend
./quick_start.sh
```

### 手动启动前端
```bash
cd frontend
pnpm install
pnpm dev
```

## API端点

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息

### 核心功能
- `GET /api/v1/dify-config` - 获取Dify配置
- `POST /api/v1/dify-config` - 保存Dify配置
- `POST /api/v1/chat` - 聊天接口
- `POST /api/v1/upload` - 文件上传

## 访问地址

- **前端应用**: http://localhost:8001
- **后端API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs
- **ReDoc文档**: http://localhost:8001/redoc

## 开发注意事项

### 前端开发
- 使用UmiJS框架进行开发
- 代理配置自动转发API请求到后端
- 支持热重载开发

### 后端开发
- 使用Poetry管理Python依赖
- FastAPI自动生成API文档
- 支持热重载开发

### 数据库
- 使用PostgreSQL作为主数据库
- 支持自动表初始化
- 环境变量配置连接参数

## 部署建议

### 开发环境
使用本地开发模式获得最佳开发体验

### 生产环境
1. 使用Docker Compose部署
2. 配置正确的环境变量
3. 使用反向代理（如Nginx）
4. 配置HTTPS证书

## 故障排除

### 常见问题
1. **端口占用**: 确保8001端口未被占用
2. **数据库连接**: 检查数据库配置和网络连接
3. **依赖安装**: 使用Poetry和pnpm管理依赖
4. **环境变量**: 确保.env文件配置正确

### 调试技巧
1. 查看服务器日志获取错误信息
2. 使用API文档测试接口
3. 检查浏览器开发者工具的网络请求
4. 验证环境变量是否正确加载

## 扩展功能

### 已实现
- ✅ 用户认证系统
- ✅ 流式聊天功能
- ✅ 文档上传功能
- ✅ Dify平台集成
- ✅ 容器化部署

### 可扩展
- 📋 多语言支持
- 📋 文件类型扩展
- 📋 聊天记录导出
- 📋 用户权限管理
- 📋 监控和日志系统

---

*此文档作为项目的核心参考，包含了所有重要的技术细节和使用指南。*
