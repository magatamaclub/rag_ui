# 项目更新说明

## 最新更新内容

### 1. UI界面优化
- ✅ **移除左侧会话栏**: 简化了界面，去除了左侧的会话历史列表
- ✅ **优化Header布局**: 在Header中添加了新对话按钮和Dify应用选择器
- ✅ **响应式设计**: 界面更加简洁，专注于聊天功能

### 2. 用户角色系统
- ✅ **管理员角色**: 新增管理员和普通用户角色区分
- ✅ **权限控制**: 管理员可以管理Dify应用，普通用户只能使用
- ✅ **自动初始化**: 启动时自动创建默认管理员账户

### 3. Dify应用管理系统
- ✅ **多应用支持**: 支持管理多个Dify应用(WorkFlow, ChatFlow, ChatBot, Agent, Text Generator)
- ✅ **应用类型**: 支持5种Dify应用类型
- ✅ **应用选择**: 用户可以在聊天时选择不同的Dify应用
- ✅ **管理界面**: 管理员可以通过专门的管理页面添加、编辑、删除Dify应用

## 新增的数据库表

### 1. Users表扩展
```sql
- role: 用户角色 (user/admin)
```

### 2. DifyApp表 (新增)
```sql
- id: 主键
- name: 应用名称
- app_type: 应用类型 (workflow/chatflow/chatbot/agent/text_generator)
- api_key: API密钥
- api_url: API地址
- description: 应用描述
- is_active: 是否启用
- created_at: 创建时间
- updated_at: 更新时间
```

## 新增的API端点

### Dify应用管理 (管理员权限)
- `POST /api/v1/dify-apps` - 创建Dify应用
- `GET /api/v1/dify-apps` - 获取所有应用列表
- `GET /api/v1/dify-apps/{app_id}` - 获取特定应用
- `PUT /api/v1/dify-apps/{app_id}` - 更新应用
- `DELETE /api/v1/dify-apps/{app_id}` - 删除应用

### 增强的聊天功能
- `POST /api/v1/chat/app/{app_id}` - 使用指定Dify应用进行聊天

## 新增的前端页面

### Dify应用管理页面 (`/dify-app-manage`)
- 仅管理员可访问
- 应用列表展示
- 创建/编辑/删除应用功能
- 应用状态管理

## 默认账户信息

系统启动时会自动创建默认管理员账户：
- **用户名**: `admin`
- **密码**: `admin123`
- **邮箱**: `admin@example.com`
- **角色**: 管理员

⚠️ **重要**: 请在首次登录后立即修改默认密码！

## 部署和初始化

### 1. 数据库初始化
```bash
cd backend
python init_db.py
```

### 2. 启动后端服务
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端服务
```bash
cd frontend
pnpm install
pnpm dev
```

## 使用流程

### 管理员首次使用
1. 使用默认账户(`admin`/`admin123`)登录
2. 修改默认密码
3. 访问`/dify-app-manage`页面
4. 添加实际的Dify应用配置
5. 配置正确的API URL和API Key

### 普通用户使用
1. 注册或由管理员创建账户
2. 登录系统
3. 在聊天页面选择可用的Dify应用
4. 开始聊天

## 技术特性

### 后端新增功能
- 基于SQLAlchemy的多表关联
- JWT token认证和角色权限控制
- 管理员权限装饰器
- 动态Dify应用配置
- 数据库自动初始化

### 前端新增功能
- 角色基于的UI显示
- Dify应用选择器
- 管理员专用管理界面
- 优化的聊天界面布局

## 配置说明

### 环境变量
确保`.env`文件包含正确的数据库配置：
```env
DB_HOST=your_db_host
DB_PORT=5435
DB_NAME=rag_ui_db
DB_USER=your_username
DB_PASSWORD=your_password
```

### Dify应用配置
在管理界面中需要配置：
- API URL: Dify实例的API地址
- API Key: 对应应用的API密钥
- 应用类型: 选择正确的应用类型

## 问题排查

### 1. 数据库连接问题
- 检查`.env`文件中的数据库配置
- 确保PostgreSQL服务正在运行
- 验证网络连接和防火墙设置

### 2. 权限问题
- 确保使用管理员账户访问管理功能
- 检查JWT token是否有效

### 3. Dify API调用失败
- 验证API URL和API Key的正确性
- 检查Dify应用是否正常运行
- 查看后端日志获取详细错误信息
