# RAG UI with Dify Integration

## 1. 项目简介

本项目旨在开发一个基于检索增强生成 (RAG) 技术的交互式用户界面 (UI) 产品。它允许用户上传文档作为知识库，并通过聊天界面与 AI 进行交互，AI 的回答将基于检索到的相关文档内容。后端集成了 Dify 平台，利用其强大的 RAG 和 LLM 应用编排能力。

## 2. 项目需求与演进

### 初始需求

*   **RAG UI 产品:** 提供一个用户友好的界面，用于与 RAG 系统交互。
*   **数据库:** 使用 PostgreSQL 作为数据存储。
*   **后端接口:** 后端能够配置并对接 OpenAI 接口标准的 Key。

### 需求演进

在开发过程中，需求进一步细化和扩展：

*   **前端 UI 布局:** 采用三栏式布局：
    *   左侧：用户会话管理（历史聊天记录）。
    *   中间：对话内容显示区域。
    *   右侧：PDF 相关出处/知识源显示。
*   **前端 UI 框架:** 使用 Ant Design Pro 作为前端 UI 框架，以提供企业级美观和功能。
*   **Dify API 对接:** 后端不再自行实现 RAG 逻辑，而是直接对接 Dify 平台的 API，利用 Dify 的知识库管理和聊天能力。
*   **前端会话持久化:** 聊天会话记录在前端通过 `localStorage` 进行持久化，刷新页面后不丢失。
*   **前端知识源显示:** 当 Dify 返回 `retriever_result` 时，前端能够解析并显示相关的知识源片段。
*   **后端 Dify 配置管理:** Dify 的 API URL 和 API Key 不再硬编码，而是通过后端接口进行配置和存储在 PostgreSQL 数据库中。
*   **容器化部署:** 使用 Docker 和 Docker Compose 实现整个应用（前端、后端、数据库）的一键部署。
*   **测试用例:** 前后端代码均需包含测试用例，确保功能正确性和代码质量。

## 3. 功能描述

### 核心功能

*   **文件上传:** 用户可以通过前端界面上传文档（如 PDF、TXT），这些文档将通过后端接口上传至 Dify 平台，作为其知识库的一部分。
*   **智能聊天:** 用户在聊天界面输入问题，后端将问题转发至 Dify 聊天 API。Dify 根据其知识库进行检索和生成，并将流式响应返回给前端，实现实时打字机效果。
*   **知识源追溯:** 当 AI 回答中引用了知识库内容时，右侧边栏会显示相关的文档片段，提供答案的出处和依据。
*   **会话管理:** 用户可以创建新的聊天会话，切换到历史会话，并查看会话内容。会话记录在浏览器本地持久化。
*   **Dify 配置:** 提供专门的界面和后端接口，允许用户配置 Dify 平台的 API URL 和 API Key，这些配置将安全地存储在后端数据库中。

### 技术亮点

*   **前后端分离:** 清晰的职责划分，便于独立开发和部署。
*   **流式响应:** 聊天功能采用流式传输，提升用户体验。
*   **模块化设计:** 后端 API 结构清晰，易于扩展。
*   **测试覆盖:** 关键后端功能均有 `pytest` 测试用例，确保代码质量。
*   **容器化:** 通过 Docker Compose 实现快速、一致的开发和生产环境部署。

## 4. 技术栈

*   **前端:**
    *   **框架:** React (TypeScript)
    *   **UI 库:** Ant Design Pro (基于 Ant Design)
    *   **构建工具/框架:** UmiJS
    *   **包管理:** pnpm
*   **后端:**
    *   **语言:** Python
    *   **Web 框架:** FastAPI
    *   **ORM:** SQLAlchemy
    *   **数据库驱动:** psycopg2-binary
    *   **HTTP 客户端:** requests
    *   **测试框架:** pytest, pytest-mock
*   **数据库:**
    *   PostgreSQL
*   **RAG/LLM 平台:**
    *   Dify (通过其 API 进行集成)
*   **容器化:**
    *   Docker
    *   Docker Compose

## 5. 项目结构

```
rag_ui_ant_design/
├── backend/                      # 后端服务目录
│   ├── app/                      # FastAPI 应用代码
│   │   ├── __init__.py
│   │   ├── api.py                # API 路由定义 (文件上传, 聊天, Dify配置)
│   │   ├── database.py           # 数据库连接和会话管理
│   │   ├── main.py               # FastAPI 主应用入口, 包含路由和数据库初始化
│   │   └── models.py             # SQLAlchemy 数据库模型 (DifyConfig)
│   ├── tests/                    # 后端测试用例
│   │   └── test_api.py           # API 接口测试
│   ├── .venv/                    # Python 虚拟环境
│   ├── Dockerfile                # 后端 Docker 构建文件
│   ├── pyproject.toml            # Poetry 项目配置和依赖管理
│   └── poetry.lock               # Poetry 依赖锁定文件
├── frontend/                     # 前端应用目录
│   ├── public/                   # 静态资源
│   ├── src/                      # React 源代码
│   │   ├── pages/                # 页面组件
│   │   │   ├── ChatPage.tsx      # 聊天界面
│   │   │   ├── DifyConfigPage.tsx# Dify 配置界面
│   │   │   ├── IndexPage.tsx     # 首页
│   │   │   └── UploadPage.tsx    # 文件上传页面
│   │   └── app.ts                # UmiJS 运行时配置 (可选)
│   ├── .umirc.ts                 # UmiJS 配置文件 (路由, 插件, 代理)
│   ├── Dockerfile                # 前端 Docker 构建文件
│   ├── nginx.conf                # Nginx 配置文件 (用于服务前端静态文件和代理API请求)
│   ├── package.json              # Node.js 项目配置和依赖管理
│   ├── pnpm-lock.yaml            # pnpm 依赖锁定文件
│   └── tsconfig.json             # TypeScript 配置文件
├── docker-compose.yml            # Docker Compose 编排文件
└── README.md                     # 项目说明文档 (当前文件)
```

## 6. 环境变量配置

项目支持通过环境变量进行配置，便于不同环境的部署。

### 环境变量说明

创建 `.env` 文件来配置应用参数：

```bash
# 数据库配置
DB_HOST=localhost          # 数据库主机地址
DB_PORT=5432              # 数据库端口
DB_NAME=rag_db            # 数据库名称
DB_USER=user              # 数据库用户名
DB_PASSWORD=password      # 数据库密码

# 应用配置
APP_HOST=0.0.0.0          # 应用监听地址
APP_PORT=8000             # 应用端口
APP_DEBUG=false           # 调试模式开关
```

### Docker 环境变量

在 Docker Compose 中，您可以通过以下方式传入环境变量：

1. **使用 .env 文件**（推荐）：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件中的配置
   docker-compose up --build
   ```

2. **通过命令行传入**：
   ```bash
   DB_PASSWORD=mypassword APP_PORT=9000 docker-compose up --build
   ```

3. **设置环境变量**：
   ```bash
   export DB_PASSWORD=mypassword
   export APP_PORT=9000
   docker-compose up --build
   ```

## 7. 快速启动 (使用 Docker Compose)

1.  **停止所有正在运行的开发服务器**（如果之前有启动的话，例如 `pnpm dev` 和 `uvicorn`）。
2.  在项目根目录 `rag_ui_ant_design` 下，打开终端并运行：
    ```bash
    docker-compose up --build --no-cache
    ```
    *   `--build`: 强制重新构建所有服务镜像。
    *   `--no-cache`: 禁用构建缓存，确保所有依赖和代码都是最新的。
3.  等待所有服务启动。这可能需要一些时间，特别是首次构建时。
4.  在浏览器中访问 `http://localhost`。

## 8. 使用指南

1.  **配置 Dify API:**
    *   访问 `http://localhost` 后，点击左侧菜单栏的 **"Dify Config"**。
    *   输入您的 Dify API URL (例如 `http://dify.go3daddy.com/v1`) 和 API Key。
    *   点击 **"Save Configuration"**。
2.  **上传文档 (可选):**
    *   点击左侧菜单栏的 **"Upload Documents"**。
    *   拖放或选择您想要上传的文档。这些文档将上传到您配置的 Dify 平台。
    *   **重要:** 上传后，您需要在 Dify 平台中将这些文档关联到您的应用知识库，以便 AI 进行检索。
3.  **开始聊天:**
    *   点击左侧菜单栏的 **"Chat"**。
    *   在聊天输入框中输入您的问题，然后发送。
    *   观察 AI 的流式回复，以及右侧边栏可能出现的知识源。
4.  **会话管理:**
    *   点击左侧的 **"New Chat"** 按钮创建新会话。
    *   点击左侧列表中的会话标题可以切换会话。

## 9. 测试

### 后端测试

在 `backend` 目录下，确保您已激活虚拟环境并安装了 Poetry 依赖，然后运行：

```bash
cd backend
. .venv/bin/activate
PYTHONPATH=. pytest
```

### 前端测试 (待实现)

目前前端尚未编写 Jest/React Testing Library 测试用例。

## 10. 未来增强

*   **后端会话持久化:** 将聊天会话记录存储在后端数据库中，实现更可靠的会话管理和跨设备同步。
*   **用户认证/授权:** 引入用户管理系统，保护 API 接口和数据。
*   **更丰富的 Dify 集成:** 支持 Dify 的更多功能，如数据集管理、模型选择等。
*   **前端优化:** 提升 UI/UX，增加更多交互细节和动画。
*   **错误处理和日志:** 完善前后端的错误处理机制和日志记录。
*   **部署自动化:** 集成 CI/CD 流程，实现自动化测试和部署。
