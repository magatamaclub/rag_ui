# 快速启动指南

## 🚀 方式一：本地开发启动（推荐）

这是最稳定的启动方式，避免Docker网络问题：

```bash
# 克隆并进入项目目录
cd rag_ui_ant_design

# 使用本地开发脚本
./start-dev.sh
```

该脚本会自动：
1. 启动PostgreSQL数据库容器
2. 设置Python虚拟环境
3. 安装后端依赖
4. 启动后端API服务（端口8000）
5. 安装前端依赖
6. 启动前端开发服务器（端口8001）

### 访问地址：
- 🌐 **前端界面**: http://localhost:8001
- 🔧 **后端API**: http://localhost:8000
- 📊 **数据库**: localhost:5432

### 停止服务：
按 `Ctrl+C` 停止所有服务

---

## 🐳 方式二：完整Docker部署

如果网络环境稳定，可以使用Docker Compose：

```bash
# 基础启动
docker-compose up --build

# 或者使用启动脚本
./start.sh
```

### 访问地址：
- 🌐 **前端界面**: http://localhost
- 🔧 **后端API**: http://localhost:8000
- 📊 **数据库**: localhost:5432

---

## 🔧 方式三：仅数据库Docker + 手动启动

如果遇到前端构建问题，可以只用Docker启动数据库：

```bash
# 仅启动数据库
docker-compose -f docker-compose.dev.yml up -d

# 手动启动后端
cd backend
source .venv/bin/activate
poetry install
poetry run uvicorn app.main:app --reload

# 手动启动前端
cd frontend
pnpm install  # 或 npm install
pnpm dev      # 或 npm run dev
```

---

## 📋 首次使用配置

1. **配置Dify API**:
   - 访问前端界面
   - 点击"Dify Config"
   - 输入Dify API URL和密钥
   - 保存配置

2. **上传文档**（可选）:
   - 点击"Upload Documents"
   - 上传文档到Dify知识库

3. **开始聊天**:
   - 点击"Chat"
   - 开始与AI对话

---

## 🛠️ 故障排除

### Docker网络问题
- 使用方式一（本地开发）
- 检查网络连接
- 使用国内镜像源

### 端口冲突
- 修改`.env`文件中的端口配置
- 或停止占用端口的服务

### 依赖安装失败
- 检查Node.js和Python版本
- 清理缓存：`npm cache clean --force`
- 重新安装：`rm -rf node_modules && npm install`
