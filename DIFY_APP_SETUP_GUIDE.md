# Dify 应用配置指南

## 问题描述
您在寻找 Dify 应用配置功能，但在界面中找不到相关选项。

## 解决方案

### 1. 系统架构说明
您的 RAG UI 系统包含两个级别的 Dify 配置：

#### A. 基础配置 (DifyConfig)
- 路径: `/dify-config`
- 功能: 配置全局的 Dify API URL 和 API Key
- 权限: 所有用户

#### B. 应用管理 (DifyApp)
- 路径: `/dify-app-manage`
- 功能: 管理多个 Dify 应用，每个应用有自己的配置
- 权限: **仅管理员**

### 2. 访问 Dify 应用管理

#### 前提条件
1. 系统正在运行
2. 您需要有管理员权限的账户

#### 访问步骤

1. **启动系统**
   ```bash
   cd /Users/hiyenwong/projects/ai_projects/rag_ui_ant_design
   ./start-dev.sh
   ```

2. **访问前端**
   - 打开浏览器访问: http://localhost:8001
   - 如果前端无法启动（Node.js版本问题），请参考下方的修复方案

3. **登录系统**
   - 如果没有账户，先注册
   - 登录后检查您的权限

4. **访问应用管理**
   - 方法1: 直接访问 http://localhost:8001/dify-app-manage
   - 方法2: 在聊天页面，点击用户菜单中的"应用管理"选项

### 3. 创建管理员账户

如果您需要管理员权限，需要：

1. **注册普通账户**
2. **通过数据库修改权限** 或 **使用管理员功能提升权限**

#### 方法1: 直接数据库修改
```sql
-- 连接到数据库
psql -h localhost -p 5432 -U user -d rag_db

-- 查看用户列表
SELECT id, username, email, role FROM users;

-- 将用户设置为管理员
UPDATE users SET role = 'admin' WHERE username = 'your_username';
```

#### 方法2: 使用 API（如果有初始管理员）
```bash
# 获取用户列表（需要管理员权限）
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/admin/users

# 提升用户权限
curl -X PUT -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"role": "admin"}' \
     http://localhost:8000/api/v1/admin/users/{user_id}
```

### 4. 使用 Dify 应用管理

一旦您有了管理员权限并访问了应用管理页面，您可以：

1. **创建新的 Dify 应用**
   - 点击"添加应用"按钮
   - 填写应用信息：
     - 应用名称
     - 应用类型（工作流、聊天流、聊天机器人、智能代理、文本生成器）
     - API URL
     - API Key
     - 描述（可选）

2. **管理现有应用**
   - 查看应用列表
   - 编辑应用配置
   - 删除应用

3. **应用类型说明**
   - **workflow**: 工作流应用
   - **chatflow**: 聊天流应用
   - **chatbot**: 聊天机器人
   - **agent**: 智能代理
   - **text_generator**: 文本生成器

### 5. 前端启动问题修复

如果遇到 Node.js 版本问题，使用以下解决方案：

#### 选项1: 使用 nvm 切换版本
```bash
# 安装 nvm（如果未安装）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载终端
source ~/.zshrc

# 安装并使用正确的 Node.js 版本
nvm install 20.19.4
nvm use 20.19.4

# 重新启动项目
./start-dev.sh
```

#### 选项2: 修改 package.json
临时移除版本限制：
```bash
cd frontend
# 备份原文件
cp package.json package.json.backup

# 删除 engines 字段
sed -i '' '/"engines"/,/},/d' package.json

# 重新安装依赖
pnpm install

# 启动前端
pnpm dev
```

### 6. 测试 API 端点

您可以通过以下方式测试 Dify 应用相关的 API：

1. **访问 API 文档**: http://localhost:8000/docs
2. **查看可用端点**:
   - `GET /api/v1/dify-apps` - 获取应用列表
   - `POST /api/v1/dify-apps` - 创建新应用（管理员）
   - `GET /api/v1/dify-apps/{app_id}` - 获取特定应用
   - `PUT /api/v1/dify-apps/{app_id}` - 更新应用（管理员）
   - `DELETE /api/v1/dify-apps/{app_id}` - 删除应用（管理员）

### 7. 故障排除

如果仍然找不到 Dify 应用配置：

1. **检查权限**: 确保您的账户有管理员权限
2. **检查服务状态**: 确保后端和前端都在运行
3. **清除缓存**: 清除浏览器缓存并重新加载
4. **检查控制台**: 查看浏览器开发者工具中的错误信息

### 8. 联系支持

如果问题仍然存在，请提供：
- 您的用户名和权限级别
- 浏览器控制台的错误信息
- 后端日志信息

---

## 快速操作清单

✅ 启动系统: `./start-dev.sh`
✅ 访问前端: http://localhost:8001
✅ 登录系统
✅ 检查管理员权限
✅ 访问应用管理: http://localhost:8001/dify-app-manage
✅ 创建/管理 Dify 应用

---

*此指南覆盖了 Dify 应用配置的所有方面。如果您需要更多帮助，请参考项目文档或联系技术支持。*
