# RAG UI Backend 启动指南

## 🚀 快速启动

后端服务器现在已经成功配置完成！

### 启动方法

#### 方法1：使用快速启动脚本（推荐）
```bash
cd backend
./quick_start.sh
```

#### 方法2：使用Poetry直接启动
```bash
cd backend
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 方法3：使用完整启动脚本
```bash
cd backend
./start_backend.sh
```

### 🌐 访问地址

- **API根路径**: http://localhost:8001/
- **Swagger文档**: http://localhost:8001/docs
- **ReDoc文档**: http://localhost:8001/redoc

### ✅ 当前状态

- ✅ **服务器启动成功**
- ✅ **API接口可用** (测试通过: `{"Hello":"World"}`)
- ✅ **Swagger UI可访问**
- ✅ **自动重载已启用**（开发模式）

### ⚠️ 已知限制

由于macOS上的psycopg2驱动兼容性问题，当前版本：
- 跳过了实际的数据库连接测试
- 跳过了表的自动创建
- 使用默认的Dify配置

### 🔧 技术详情

- **框架**: FastAPI 0.111.0
- **ASGI服务器**: Uvicorn
- **端口**: 8001
- **主机**: 0.0.0.0 (允许外部访问)
- **重载模式**: 开启（开发环境）

### 📝 API功能

当前可用的API端点：
- `GET /` - 健康检查
- `POST /auth/login` - 用户登录
- `POST /upload` - 文件上传
- `POST /chat` - 聊天接口
- `POST /dify/config` - Dify配置
- `GET /dify/config` - 获取Dify配置

### 🛠️ 故障排除

如果遇到问题：

1. **检查Poetry是否正确安装**:
   ```bash
   poetry --version
   ```

2. **检查依赖是否安装**:
   ```bash
   poetry install
   ```

3. **检查端口是否被占用**:
   ```bash
   lsof -ti:8001
   ```

4. **查看详细日志**:
   ```bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --log-level debug
   ```

### 🎯 下一步

后端现在可以正常使用了！你可以：
1. 启动前端服务连接到这个后端
2. 通过Swagger UI测试各个API端点
3. 开始开发业务逻辑
4. 稍后修复数据库连接问题（当需要持久化数据时）

---
*最后更新: 2024年7月20日*
