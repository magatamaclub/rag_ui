# 数据库初始化功能说明

## 功能概述

为了解决新环境下数据库初始化的问题，我们添加了自动检测和初始化数据库的功能。

## 新增API接口

### 1. 数据库状态检查
```
GET /api/v1/database/status
```

**响应示例:**
```json
{
  "is_initialized": false,
  "has_connection": true,
  "has_tables": false,
  "has_admin_user": false,
  "message": "数据库连接正常，但缺少数据表"
}
```

### 2. 数据库初始化
```
POST /api/v1/database/initialize
```

**响应示例:**
```json
{
  "success": true,
  "message": "数据库初始化成功",
  "admin_username": "admin",
  "admin_password": "admin123"
}
```

## 前端流程

### 1. 自动检测
- 应用启动时自动检查数据库状态
- 如果数据库未初始化，自动跳转到初始化页面

### 2. 初始化页面
- 路径: `/initialize`
- 显示初始化进度
- 提供一键初始化功能
- 初始化完成后自动跳转到登录页面

### 3. 数据库守卫组件
- `DatabaseGuard` 组件负责检查数据库状态
- 只对非初始化页面进行检查
- 确保用户在数据库未准备好时不会访问其他页面

## 使用场景

### 首次部署
1. 启动后端服务
2. 访问前端应用
3. 自动跳转到初始化页面
4. 点击"开始初始化"
5. 等待初始化完成
6. 跳转到登录页面

### 默认管理员账户
- **用户名:** admin
- **密码:** admin123
- **建议:** 首次登录后立即修改密码

## 技术实现

### 后端 (FastAPI)
- `database_endpoints.py`: 数据库相关API端点
- 集成到 `main.py` 的路由中
- 支持数据库连接检查、表结构检查、用户检查

### 前端 (React + UmiJS)
- `InitializePage.tsx`: 初始化页面组件
- `DatabaseGuard.tsx`: 数据库状态守卫组件
- `app.tsx`: 全局配置和守卫集成

## 错误处理

- 数据库连接失败时显示相应错误信息
- 初始化失败时提供重试功能
- 网络错误时自动跳转到初始化页面

## 安全考虑

- 初始化API不需要认证（仅在数据库为空时有效）
- 创建管理员用户后，相关功能自动禁用
- 建议在生产环境中修改默认密码

## 测试方法

1. 清空数据库
2. 启动后端服务
3. 访问前端应用
4. 验证自动跳转和初始化流程
5. 确认初始化后可以正常登录

## 文件清单

### 后端新增/修改文件
- `backend/app/database_endpoints.py` (新增)
- `backend/app/main.py` (修改 - 添加路由)
- `backend/app/api.py` (修改 - 添加导入)

### 前端新增/修改文件
- `frontend/src/pages/InitializePage.tsx` (新增)
- `frontend/src/components/DatabaseGuard.tsx` (新增)
- `frontend/src/app.tsx` (新增)
- `frontend/.umirc.ts` (修改 - 添加路由)

### 测试文件
- `test_db_init.py` (新增 - API测试脚本)
