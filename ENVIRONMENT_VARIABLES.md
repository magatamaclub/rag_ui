# 环境变量配置指南

## 概述

本文档说明了 RAG UI 项目中所有可配置的环境变量。

## 快速开始

1. 复制根目录的 `.env.example` 为 `.env`
2. 复制前端目录的 `.env.example` 为 `.env`（可选）
3. 根据您的环境修改配置值

```bash
# 后端环境变量
cp .env.example .env

# 前端环境变量 (可选)
cp frontend/.env.example frontend/.env
```

## 后端环境变量

### 数据库配置

| 变量名         | 默认值      | 说明                                 |
| -------------- | ----------- | ------------------------------------ |
| `DB_HOST`      | `localhost` | 数据库主机地址                       |
| `DB_PORT`      | `5432`      | 数据库端口                           |
| `DB_NAME`      | `rag_db`    | 数据库名称                           |
| `DB_USER`      | `user`      | 数据库用户名                         |
| `DB_PASSWORD`  | `password`  | 数据库密码                           |
| `DATABASE_URL` | -           | 完整数据库 URL（可替代上述单独配置） |

**Docker 环境注意事项**：
- 使用 Docker Compose 时，设置 `DB_HOST=db`
- 其他配置保持不变

### 应用配置

| 变量名      | 默认值    | 说明                                   |
| ----------- | --------- | -------------------------------------- |
| `APP_HOST`  | `0.0.0.0` | 应用监听地址                           |
| `APP_PORT`  | `8000`    | 应用监听端口                           |
| `APP_DEBUG` | `false`   | 是否启用调试模式                       |
| `LOG_LEVEL` | `INFO`    | 日志级别 (DEBUG, INFO, WARNING, ERROR) |

### JWT 认证配置

| 变量名                        | 默认值                         | 说明                            |
| ----------------------------- | ------------------------------ | ------------------------------- |
| `SECRET_KEY`                  | `your-super-secret-jwt-key...` | JWT 签名密钥 ⚠️ 生产环境必须修改 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                           | JWT Token 过期时间（分钟）      |

**安全提示**：
- 生产环境中必须设置强密钥（至少32字符）
- 可以使用以下命令生成安全密钥：
  ```bash
  openssl rand -hex 32
  ```

### 默认管理员配置

| 变量名                   | 默认值              | 说明                              |
| ------------------------ | ------------------- | --------------------------------- |
| `DEFAULT_ADMIN_USERNAME` | `admin`             | 默认管理员用户名                  |
| `DEFAULT_ADMIN_EMAIL`    | `admin@example.com` | 默认管理员邮箱                    |
| `DEFAULT_ADMIN_PASSWORD` | `admin123`          | 默认管理员密码 ⚠️ 生产环境必须修改 |

**重要说明**：
- 这些配置仅在首次启动时创建管理员账户时使用
- 生产环境部署前请务必修改默认密码
- 管理员创建后，可以通过管理界面修改信息

### CORS 配置

| 变量名         | 默认值 | 说明                     |
| -------------- | ------ | ------------------------ |
| `CORS_ORIGINS` | -      | 允许的跨域源，用逗号分隔 |

**示例**：
```bash
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 前端环境变量

### API 配置

| 变量名                   | 默认值                  | 说明              |
| ------------------------ | ----------------------- | ----------------- |
| `REACT_APP_API_BASE_URL` | `http://localhost:8000` | 后端 API 基础 URL |

### 应用配置

| 变量名               | 默认值               | 说明     |
| -------------------- | -------------------- | -------- |
| `REACT_APP_APP_NAME` | `RAG UI Chat System` | 应用名称 |
| `REACT_APP_VERSION`  | `1.0.0`              | 应用版本 |

### 开发配置

| 变量名               | 默认值        | 说明             |
| -------------------- | ------------- | ---------------- |
| `NODE_ENV`           | `development` | Node.js 环境     |
| `GENERATE_SOURCEMAP` | `true`        | 是否生成源码映射 |

## 部署环境配置

### 开发环境

```bash
# .env
DB_HOST=localhost
DB_PORT=5432
APP_DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 生产环境

```bash
# .env
DB_HOST=your-db-host
DB_NAME=rag_production
DB_USER=rag_user
DB_PASSWORD=your-secure-password
SECRET_KEY=your-very-long-and-random-secret-key-at-least-32-characters
DEFAULT_ADMIN_PASSWORD=your-secure-admin-password
APP_DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
```

### Docker 环境

使用 Docker Compose 时，大部分配置可以保持默认值，只需修改敏感信息：

```bash
# .env
DB_PASSWORD=your-secure-db-password
SECRET_KEY=your-secure-jwt-secret
DEFAULT_ADMIN_PASSWORD=your-secure-admin-password
```

## 配置验证

启动应用后，可以通过以下方式验证配置：

1. **查看日志输出**：检查应用启动日志中的配置信息
2. **访问健康检查端点**：`GET /api/health`
3. **测试数据库连接**：成功启动表示数据库配置正确
4. **登录管理员账户**：验证默认管理员配置

## 常见问题

### Q: 忘记了管理员密码怎么办？

A: 可以通过以下方式重置：
1. 修改 `DEFAULT_ADMIN_PASSWORD` 环境变量
2. 删除数据库中的管理员用户记录
3. 重启应用，系统会使用新密码重新创建管理员

### Q: 如何在生产环境中安全地管理环境变量？

A: 推荐方案：
1. 使用容器编排工具的密钥管理（如 Kubernetes Secrets）
2. 使用云服务提供商的密钥管理服务
3. 使用工具如 HashiCorp Vault
4. 确保 `.env` 文件不提交到版本控制系统

### Q: 前端环境变量不生效？

A: 检查以下几点：
1. 变量名必须以 `REACT_APP_` 开头
2. 修改环境变量后需要重新构建前端
3. 确保 `.env` 文件位于 `frontend/` 目录下

### Q: 数据库连接失败？

A: 检查配置：
1. 确保数据库服务已启动
2. 验证数据库连接参数
3. 检查网络连通性
4. 确认数据库用户权限

## 安全建议

1. **永远不要**将包含敏感信息的 `.env` 文件提交到版本控制系统
2. **定期轮换**JWT 密钥和数据库密码
3. **使用强密码**，特别是生产环境
4. **限制 CORS 源**到必要的域名
5. **启用 HTTPS**在生产环境中
6. **定期审查**和更新环境变量配置
