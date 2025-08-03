# Volta Node.js 版本管理指南

## 概述

本项目使用 [Volta](https://volta.sh/) 来管理 Node.js 版本，确保所有开发者使用相同的 Node.js 和 npm 版本，避免版本不兼容问题。

## 安装 Volta

如果您还没有安装 Volta，请按照以下步骤安装：

### macOS/Linux
```bash
curl https://get.volta.sh | bash
```

# NVM Node.js 版本管理指南

## 概述

本项目使用 [NVM (Node Version Manager)](https://github.com/nvm-sh/nvm) 来管理 Node.js 版本，确保所有开发者使用相同的 Node.js 版本，避免版本不兼容问题。

## 安装 NVM

### macOS/Linux
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# 或者
wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# 重新加载 shell
source ~/.bashrc
# 或者
source ~/.zshrc
```

### Windows
使用 [nvm-windows](https://github.com/coreybutler/nvm-windows)：
```bash
# 下载并安装 nvm-setup.exe
# 从 https://github.com/coreybutler/nvm-windows/releases
```

## 项目 Node.js 版本

本项目固定使用以下版本：
- **Node.js**: 20.19.4  
- **npm**: 10.8.2

版本信息存储在以下文件中：
- 根目录: `.nvmrc` 
- 前端目录: `frontend/.nvmrc`
- package.json: `engines` 字段

## 使用方法

### 1. 自动版本切换

当您进入项目目录时，NVM 可以自动检测并使用项目配置的 Node.js 版本：

```bash
cd /path/to/rag_ui_ant_design

# 自动检测并使用 .nvmrc 中的版本
nvm use

# 检查版本
node --version  # 应显示 v20.19.4
npm --version   # 应显示 10.8.2
```

### 2. 安装项目所需的 Node.js 版本

```bash
# 安装 .nvmrc 中指定的版本
nvm install

# 或者手动安装特定版本
nvm install 20.19.4

# 使用该版本
nvm use 20.19.4

# 设置为默认版本（可选）
nvm alias default 20.19.4
```

### 3. 验证安装

```bash
# 检查 NVM 状态
nvm list

# 检查当前版本
node --version
npm --version

# 检查已安装的版本
nvm ls
```

### 4. 项目开发工作流

```bash
# 1. 进入项目目录
cd rag_ui_ant_design

# 2. 使用项目指定的 Node.js 版本
nvm use

# 3. 安装前端依赖
cd frontend
npm install

# 4. 启动开发服务器
npm run dev
```

## 自动版本切换配置

### Bash (.bashrc)
```bash
# 添加到 ~/.bashrc
cdnvm() {
    command cd "$@" || return $?
    nvm_path=$(nvm_find_up .nvmrc | tr -d '\n')

    # If there are no .nvmrc file, use the default nvm version
    if [[ ! $nvm_path = *[^[:space:]]* ]]; then

        declare default_version;
        default_version=$(nvm version default);

        # If there is no default version, set it to `node`
        if [[ $default_version == "N/A" ]]; then
            nvm alias default node;
            default_version=$(nvm version default);
        fi

        # If the current version is not the default version, set it to use the default version
        if [[ $(nvm current) != "$default_version" ]]; then
            nvm use default;
        fi

    elif [[ -s $nvm_path/.nvmrc && -r $nvm_path/.nvmrc ]]; then
        declare nvm_version
        nvm_version=$(<"$nvm_path"/.nvmrc)

        declare locally_resolved_nvm_version
        # `nvm ls` will check all locally-available versions
        # If there are multiple matching versions, take the latest one
        # Remove the `->` and `*` characters and spaces
        # `locally_resolved_nvm_version` will be `N/A` if no local versions are found
        locally_resolved_nvm_version=$(nvm ls --no-colors "$nvm_version" | tail -1 | tr -d '\->*' | tr -d '[:space:]')

        # If it is not already installed, install it
        # `nvm install` will implicitly use the newly-installed version
        if [[ "$locally_resolved_nvm_version" == "N/A" ]]; then
            nvm install "$nvm_version";
        elif [[ $(nvm current) != "$locally_resolved_nvm_version" ]]; then
            nvm use "$nvm_version";
        fi
    fi
}
alias cd='cdnvm'
cd "$PWD"
```

### Zsh (.zshrc)
```bash
# 添加到 ~/.zshrc
autoload -U add-zsh-hook
load-nvmrc() {
  local node_version="$(nvm version)"
  local nvmrc_path="$(nvm_find_nvmrc)"

  if [ -n "$nvmrc_path" ]; then
    local nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

    if [ "$nvmrc_node_version" = "N/A" ]; then
      nvm install
    elif [ "$nvmrc_node_version" != "$node_version" ]; then
      nvm use
    fi
  elif [ "$node_version" != "$(nvm version default)" ]; then
    echo "Reverting to nvm default version"
    nvm use default
  fi
}
add-zsh-hook chpwd load-nvmrc
load-nvmrc
```

## 常见问题

### Q: NVM 版本切换不生效？

**A**: 检查以下几点：
1. 确保在项目根目录：`pwd`
2. 确保 NVM 已正确安装：`nvm --version`
3. 手动切换：`nvm use`
4. 重新加载 shell：`source ~/.zshrc` 或 `source ~/.bashrc`

### Q: 如何更新项目的 Node.js 版本？

**A**: 更新以下文件：
1. 更新 `.nvmrc` 文件
2. 更新 `frontend/.nvmrc` 文件  
3. 更新 `frontend/package.json` 的 `engines` 字段

```bash
# 更新到新版本
echo "20.20.0" > .nvmrc
echo "20.20.0" > frontend/.nvmrc

# 安装新版本
nvm install 20.20.0
nvm use 20.20.0
```

### Q: 多个项目使用不同 Node.js 版本？

**A**: NVM 会根据每个项目的 `.nvmrc` 文件自动切换版本，无需手动管理。

## 开发环境设置检查清单

在开始开发前，请确认：

1. ✅ 安装了 NVM
2. ✅ 项目目录下存在 `.nvmrc` 文件
3. ✅ 运行 `nvm use` 切换到项目版本
4. ✅ 验证版本：`node --version` 和 `npm --version`

## CI/CD 配置

### GitHub Actions 示例

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version-file: '.nvmrc'
    cache: 'npm'
    cache-dependency-path: frontend/package-lock.json

- name: Install dependencies
  working-directory: ./frontend
  run: npm ci

- name: Build
  working-directory: ./frontend  
  run: npm run build
```

### Docker 配置示例

```dockerfile
# 从 .nvmrc 读取版本
FROM node:20.19.4-alpine

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production
```

## 故障排除

### 常见错误及解决方案

1. **`nvm: command not found`**：
   ```bash
   # 重新安装 NVM 或检查 PATH
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
   source ~/.bashrc
   ```

2. **版本不匹配**：
   ```bash
   # 清理并重新安装
   nvm uninstall 20.19.4
   nvm install 20.19.4
   nvm use 20.19.4
   ```

3. **npm 版本不匹配**：
   ```bash
   # 安装正确的 npm 版本
   npm install -g npm@10.8.2
   ```

4. **权限问题**：
   ```bash
   # 检查 NVM 目录权限
   ls -la ~/.nvm
   # 重新设置权限（如果需要）
   chmod -R 755 ~/.nvm
   ```

## 资源链接

- [NVM 官方文档](https://github.com/nvm-sh/nvm)
- [NVM Windows 版本](https://github.com/coreybutler/nvm-windows)
- [Node.js 版本发布计划](https://nodejs.org/en/about/releases/)
- [NPM 文档](https://docs.npmjs.com/)

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
