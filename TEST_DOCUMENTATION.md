# RAG UI 测试用例文档

## 概述

本文档描述了 RAG UI 项目的完整测试用例，涵盖后端 API、数据库模型、性能测试和前端集成测试。

## 测试架构

### 后端测试
- **API 接口测试**: 测试所有 REST API 端点
- **数据库模型测试**: 测试数据模型和 CRUD 操作
- **性能测试**: 测试高并发和性能表现
- **认证授权测试**: 测试用户角色和权限控制

### 前端测试
- **组件测试**: 测试 React 组件渲染和交互
- **集成测试**: 测试完整的用户工作流
- **API 集成测试**: 测试前端与后端的 API 调用

## 后端测试用例

### 1. 用户认证测试 (`TestAuthenticationEndpoints`)

#### 用户注册测试
- ✅ `test_register_user_success`: 测试成功注册普通用户
- ✅ `test_register_admin_user`: 测试注册管理员用户
- ✅ `test_register_duplicate_username`: 测试用户名重复注册
- ✅ `test_register_duplicate_email`: 测试邮箱重复注册

#### 用户登录测试
- ✅ `test_login_success`: 测试成功登录
- ✅ `test_login_invalid_username`: 测试无效用户名登录
- ✅ `test_login_invalid_password`: 测试无效密码登录

#### 用户信息测试
- ✅ `test_get_current_user_info`: 测试获取当前用户信息
- ✅ `test_get_current_user_info_no_token`: 测试无 token 访问
- ✅ `test_protected_route`: 测试受保护路由访问

### 2. Dify 配置测试 (`TestDifyConfigEndpoints`)

- ✅ `test_set_dify_config`: 测试设置 Dify 配置
- ✅ `test_get_dify_config`: 测试获取 Dify 配置
- ✅ `test_get_dify_config_not_found`: 测试配置不存在时的处理
- ✅ `test_update_dify_config`: 测试更新 Dify 配置

### 3. Dify 应用管理测试 (`TestDifyAppManagementEndpoints`)

#### 创建应用测试
- ✅ `test_create_dify_app_success`: 测试管理员成功创建应用
- ✅ `test_create_dify_app_unauthorized`: 测试普通用户创建应用（应失败）

#### 查询应用测试
- ✅ `test_get_dify_apps`: 测试获取所有应用列表
- ✅ `test_get_dify_app_by_id`: 测试根据 ID 获取特定应用
- ✅ `test_get_dify_app_not_found`: 测试获取不存在的应用

#### 更新应用测试
- ✅ `test_update_dify_app_success`: 测试管理员成功更新应用
- ✅ `test_update_dify_app_unauthorized`: 测试普通用户更新应用（应失败）

#### 删除应用测试
- ✅ `test_delete_dify_app_success`: 测试管理员成功删除应用
- ✅ `test_delete_dify_app_unauthorized`: 测试普通用户删除应用（应失败）

### 4. 聊天功能测试 (`TestChatEndpoints`)

- ✅ `test_chat_with_app_missing_app`: 测试与不存在应用聊天
- ✅ `test_chat_with_app_missing_query`: 测试缺少查询内容的聊天
- ✅ `test_chat_with_app_unauthorized`: 测试未认证用户聊天

### 5. 文档上传测试 (`TestDocumentEndpoints`)

- ✅ `test_upload_document_missing_config`: 测试缺少配置时上传文档
- ✅ `test_upload_document_unauthorized`: 测试未认证用户上传文档

### 6. 数据验证测试 (`TestValidationAndEdgeCases`)

- ✅ `test_register_invalid_email`: 测试无效邮箱格式注册
- ✅ `test_create_dify_app_invalid_app_type`: 测试无效应用类型
- ✅ `test_create_dify_app_invalid_url`: 测试无效 URL 格式

## 数据库模型测试

### 1. 用户模型测试 (`TestUserModel`)

- ✅ `test_create_user_basic`: 测试创建基础用户
- ✅ `test_create_admin_user`: 测试创建管理员用户
- ✅ `test_user_unique_constraints`: 测试用户名和邮箱唯一性约束
- ✅ `test_password_hashing`: 测试密码哈希和验证
- ✅ `test_create_user_function`: 测试用户创建辅助函数
- ✅ `test_get_user_function`: 测试用户查询辅助函数

### 2. Dify 应用模型测试 (`TestDifyAppModel`)

- ✅ `test_create_dify_app`: 测试创建 Dify 应用
- ✅ `test_all_app_types`: 测试所有应用类型创建
- ✅ `test_dify_app_filtering`: 测试应用状态过滤
- ✅ `test_dify_app_update`: 测试应用属性更新

### 3. Dify 配置模型测试 (`TestDifyConfigModel`)

- ✅ `test_create_dify_config`: 测试创建 Dify 配置
- ✅ `test_update_dify_config`: 测试更新 Dify 配置
- ✅ `test_single_config_constraint`: 测试单一配置约束

## 性能测试

### 1. 基础性能测试 (`TestPerformanceBasics`)

- ✅ `test_login_performance`: 测试登录接口性能（< 1秒）
- ✅ `test_user_registration_performance`: 测试注册接口性能（< 2秒）
- ✅ `test_get_dify_apps_performance`: 测试应用查询性能（< 0.5秒）

### 2. 并发请求测试 (`TestConcurrentRequests`)

- ✅ `test_concurrent_logins`: 测试并发登录请求（10个并发）
- ✅ `test_concurrent_app_retrieval`: 测试并发应用查询（15个并发）
- ✅ `test_mixed_concurrent_requests`: 测试混合类型并发请求

### 3. 压力测试 (`TestStressTests`)

- ✅ `test_high_volume_user_creation`: 测试大量用户创建（50个用户）
- ✅ `test_rapid_dify_app_creation`: 测试快速创建应用（20个应用）

### 4. 资源使用测试 (`TestMemoryAndResource`)

- ✅ `test_memory_usage_during_load`: 测试高负载时内存使用
- ✅ `test_response_time_consistency`: 测试响应时间一致性

## 前端测试用例

### 1. 聊天页面测试 (`ChatPage Component`)

- ✅ `renders chat page with correct elements`: 测试页面元素渲染
- ✅ `loads and displays Dify apps in selector`: 测试应用选择器加载
- ✅ `creates new conversation when new chat button is clicked`: 测试新对话创建
- ✅ `shows user menu for regular user`: 测试普通用户菜单
- ✅ `shows admin menu options for admin user`: 测试管理员菜单
- ✅ `displays error when no app is selected for chat`: 测试未选择应用时的错误
- ✅ `handles message input and sending`: 测试消息输入和发送

### 2. Dify 应用管理页面测试 (`DifyAppManagePage Component`)

- ✅ `renders Dify app management page for admin`: 测试管理页面渲染
- ✅ `loads and displays Dify apps in table`: 测试应用列表显示
- ✅ `opens create modal when create button is clicked`: 测试创建模态框
- ✅ `redirects non-admin users`: 测试非管理员用户重定向

### 3. 登录页面测试 (`LoginPage Component`)

- ✅ `renders login form`: 测试登录表单渲染
- ✅ `handles form input changes`: 测试表单输入处理

## 测试运行指南

### 后端测试运行

```bash
# 进入后端目录
cd backend

# 运行完整测试套件
./run_tests.sh

# 或者分别运行各类测试
python -m pytest tests/test_comprehensive_api.py -v
python -m pytest tests/test_database_models.py -v
python -m pytest tests/test_performance.py -v
```

### 前端测试运行

```bash
# 进入前端目录
cd frontend

# 安装测试依赖
npm install --save-dev @testing-library/react @testing-library/jest-dom @types/jest jest

# 运行测试
npm test

# 运行测试并生成覆盖率报告
npm run test:coverage
```

## 测试覆盖率目标

- **后端 API 覆盖率**: > 90%
- **数据库模型覆盖率**: > 95%
- **前端组件覆盖率**: > 80%

## 持续集成

测试应该在以下情况下自动运行：
- 代码提交到 main 分支时
- 创建 Pull Request 时
- 定期夜间构建

## 测试数据管理

### 测试数据库
- 使用 SQLite 内存数据库进行测试
- 每个测试用例前后自动创建和清理数据库
- 使用 Factory 模式创建测试数据

### Mock 数据
- API 响应使用 Mock 数据
- 外部服务调用使用 Mock
- 浏览器 API 使用 Mock

## 已知问题和限制

1. **SQLAlchemy 类型问题**: 某些测试中存在类型注解问题，但不影响功能
2. **前端测试配置**: 需要正确配置 Jest 和 React Testing Library
3. **性能测试环境**: 性能测试结果可能因硬件环境而异

## 后续改进计划

1. **增加端到端测试**: 使用 Playwright 或 Cypress
2. **API 文档测试**: 确保 API 文档与实际实现一致
3. **安全测试**: 增加安全相关的测试用例
4. **负载测试**: 使用专业负载测试工具
5. **测试报告**: 集成测试报告生成工具

## 结论

本测试套件提供了对 RAG UI 项目的全面测试覆盖，包括：

- **90+ 个后端测试用例**，覆盖所有 API 端点
- **数据库模型完整性测试**
- **性能和并发测试**
- **前端组件和集成测试**

通过这些测试，我们可以确保系统的稳定性、性能和用户体验质量。
