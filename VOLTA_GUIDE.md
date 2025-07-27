# Volta Node.js 版本管理指南

## 概述

本项目使用 [Volta](https://volta.sh/) 来管理 Node.js 版本，确保所有开发者使用相同的 Node.js 和 npm 版本，避免版本不兼容问题。

## 安装 Volta

如果您还没有安装 Volta，请按照以下步骤安装：

### macOS/Linux
```bash
curl https://get.volta.sh | bash
```

### Windows
```bash
# 使用 Scoop (推荐)
scoop install volta

# 或者下载安装程序
# 访问 https://docs.volta.sh/guide/getting-started
```

安装完成后，重启终端或运行：
```bash
source ~/.bashrc  # 或 ~/.zshrc，取决于您的 shell
```

## 项目配置

本项目已经配置了 Volta，固定了以下版本：

- **Node.js**: 20.19.4
- **npm**: 10.8.2

配置信息可以在以下文件中找到：
- `package.json` (根目录)
- `frontend/package.json`
- `.nvmrc` (用于其他版本管理器的兼容性)

## 使用方法

### 1. 自动版本切换

当您进入项目目录时，Volta 会自动检测并使用项目配置的 Node.js 版本：

```bash
cd /path/to/rag-ui-ant-design
node --version  # 应该显示 v20.19.4
```

### 2. 验证版本

确认您正在使用正确的版本：

```bash
# 检查 Node.js 版本
node --version

# 检查 npm 版本  
npm --version

# 检查 Volta 状态
volta list
```

### 3. 运行项目

现在您可以安全地运行项目：

```bash
# 启动前端开发服务器
cd frontend
npm run dev

# 或者从根目录
npm run dev
```

### 4. 手动使用 Volta

如果自动切换不工作，您可以手动使用 Volta：

```bash
# 使用 volta run 运行命令
volta run node --version
volta run npm --version

# 使用特定版本运行命令
volta run --node 20 npm install
```

## 常见问题

### Q: Volta 版本切换不生效？

**A**: 尝试以下解决方案：

1. 重启终端
2. 确保 Volta 已正确安装：`volta --version`
3. 手动使用：`volta run node --version`
4. 检查 PATH 环境变量

### Q: 如何更新 Node.js 版本？

**A**: 使用 volta pin 命令：

```bash
# 更新到最新的 Node 20.x
volta pin node@20

# 更新到特定版本
volta pin node@20.19.4

# 同时更新 npm
volta pin npm@10.8.2
```

### Q: 团队成员版本不一致？

**A**: 确保所有成员：

1. 安装了 Volta
2. 使用项目目录下的 package.json
3. 运行 `volta pin` 同步版本

### Q: CI/CD 环境如何配置？

**A**: 在 CI/CD 配置中：

```yaml
# GitHub Actions 示例
- name: Install Volta
  run: |
    curl https://get.volta.sh | bash
    echo "$HOME/.volta/bin" >> $GITHUB_PATH

- name: Install Node.js
  run: volta install node@20

# 或者直接指定版本
- uses: actions/setup-node@v3
  with:
    node-version: '20.19.4'
```

## 其他版本管理器兼容性

本项目也提供了 `.nvmrc` 文件，支持其他版本管理器：

### nvm 用户
```bash
nvm use
```

### fnm 用户  
```bash
fnm use
```

### 手动切换
```bash
# 使用 Node.js 20.19.4
nvm install 20.19.4
nvm use 20.19.4
```

## Docker 环境

Docker 环境已经配置使用 Node.js 20：

```dockerfile
FROM node:20-alpine AS build-stage
```

这确保了开发和生产环境的一致性。

## 最佳实践

1. **总是使用项目配置的版本**：避免使用全局 Node.js 版本
2. **定期更新**：定期检查并更新 Node.js 版本
3. **团队同步**：确保团队成员使用相同的工具和版本
4. **CI/CD 一致性**：确保 CI/CD 环境使用相同的 Node.js 版本

## 故障排除

如果遇到任何问题，请尝试：

1. **清理缓存**：
   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **重置 Volta**：
   ```bash
   volta install node@20.19.4
   volta install npm@10.8.2
   ```

3. **检查环境**：
   ```bash
   echo $PATH
   which node
   which npm
   volta list
   ```

## 获取帮助

- [Volta 官方文档](https://docs.volta.sh/)
- [Volta GitHub](https://github.com/volta-cli/volta)
- 项目 Issue 或联系团队成员
