# 开发指南

## 开发环境设置

### 前置要求
- Python 3.9+
- Node.js 18+
- pnpm 8+
- Poetry 1.4+
- PostgreSQL 13+ (或Docker)
- Git 2.0+

### 工具推荐
- **IDE**: VS Code, PyCharm Professional
- **API测试**: Postman, Insomnia, curl
- **数据库管理**: pgAdmin, DBeaver
- **版本控制**: Git, GitHub Desktop

### 快速开始
```bash
# 克隆项目
git clone https://github.com/magatamaclub/rag_ui.git
cd rag_ui_ant_design

# 一键启动开发环境
./start-dev.sh

# 或者手动启动各服务
cd backend && poetry install && poetry run uvicorn app.main:app --reload
cd frontend && pnpm install && pnpm dev
```

## 后端开发

### 环境设置
```bash
cd backend

# 创建虚拟环境（可选，Poetry会自动管理）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# 安装Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -
# 或使用pip: pip install poetry

# 安装项目依赖
poetry install

# 配置开发环境变量
cp .env.example .env
vim .env
```

### 项目结构详解
```
backend/
├── app/                    # 主应用包
│   ├── __init__.py        # 包初始化
│   ├── main.py            # FastAPI应用入口和生命周期
│   ├── api.py             # API路由定义和业务逻辑
│   ├── models.py          # SQLAlchemy数据模型
│   ├── schemas.py         # Pydantic请求/响应模型
│   ├── database.py        # 数据库连接和会话管理
│   ├── config.py          # 应用配置和环境变量
│   ├── auth.py            # JWT认证和授权工具
│   └── utils.py           # 通用工具函数
├── tests/                 # 测试代码
│   ├── __init__.py
│   ├── conftest.py        # pytest配置和fixtures
│   ├── test_auth.py       # 认证相关测试
│   ├── test_api.py        # API接口测试
│   └── test_models.py     # 数据模型测试
├── migrations/            # 数据库迁移文件（Alembic）
├── static/                # 静态文件
├── uploads/               # 文件上传目录
├── logs/                  # 日志文件
├── Dockerfile             # 容器化配置
├── pyproject.toml         # Poetry项目配置
├── poetry.lock            # 依赖锁定文件
├── alembic.ini            # Alembic配置
└── pytest.ini            # pytest配置
```

### 核心模块说明

#### main.py - 应用入口
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.database import init_database
import logging

# 创建FastAPI应用实例
app = FastAPI(
    title="RAG UI Backend",
    description="AI-powered document QA system with Dify integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001", "http://127.0.0.1:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router)

# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting RAG UI Backend...")
    try:
        init_database()
        logger.info("✅ Application startup completed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed: {e}")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Shutting down RAG UI Backend...")
```

#### models.py - 数据模型
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    chat_sessions = relationship("ChatSession", back_populates="user")

class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")
```

#### schemas.py - 数据验证
```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()
```

### 添加新功能

#### 1. 创建新的API端点
```python
# 在 api.py 中添加
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

@router.post("/api/v1/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新文档"""
    try:
        # 业务逻辑
        db_document = Document(
            title=document.title,
            content=document.content,
            user_id=current_user.id
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create document: {str(e)}"
        )
```

#### 2. 创建数据模型
```python
# 在 models.py 中添加
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(500))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
```

#### 3. 创建验证模式
```python
# 在 schemas.py 中添加
class DocumentBase(BaseModel):
    title: str
    content: str

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 数据库操作

#### 配置Alembic迁移
```bash
# 初始化Alembic（如果未初始化）
cd backend
poetry run alembic init migrations

# 创建迁移
poetry run alembic revision --autogenerate -m "Add document model"

# 应用迁移
poetry run alembic upgrade head

# 查看迁移历史
poetry run alembic history

# 回滚迁移
poetry run alembic downgrade -1
```

#### 数据库查询优化
```python
from sqlalchemy.orm import joinedload, selectinload

# 预加载关联数据，避免N+1查询
users_with_sessions = session.query(User).options(
    joinedload(User.chat_sessions)
).all()

# 批量插入
session.bulk_insert_mappings(Document, document_data_list)
session.commit()

# 分页查询
from sqlalchemy import func

def get_documents_paginated(db: Session, skip: int = 0, limit: int = 10):
    total = db.query(func.count(Document.id)).scalar()
    documents = db.query(Document).offset(skip).limit(limit).all()
    return {"total": total, "documents": documents}
```

### 认证和授权

#### JWT令牌管理
```python
# auth.py 中的核心函数
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception
```

#### 权限控制
```python
from functools import wraps
from fastapi import Depends, HTTPException, status

def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# 使用装饰器
@router.delete("/api/v1/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    # 只有管理员可以删除用户
    pass
```

### 测试开发

#### 测试配置
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
```

#### API测试示例
```python
# tests/test_api.py
def test_create_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "access_token" in data

def test_login(client, db):
    # 先创建用户
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # 测试登录
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint(client, db):
    # 创建用户并获取token
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    token = response.json()["access_token"]
    
    # 访问受保护的端点
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

### 运行测试
```bash
# 运行所有测试
poetry run pytest

# 运行特定测试文件
poetry run pytest tests/test_api.py

# 运行特定测试函数
poetry run pytest tests/test_api.py::test_login

# 生成覆盖率报告
poetry run pytest --cov=app --cov-report=html

# 并行运行测试
poetry run pytest -n auto
```

## 前端开发

### 环境设置
```bash
cd frontend

# 安装pnpm（如果未安装）
npm install -g pnpm

# 安装项目依赖
pnpm install

# 启动开发服务器
pnpm dev

# 或者使用yarn/npm
yarn install && yarn dev
npm install && npm run dev
```

### 项目结构详解
```
frontend/
├── src/                   # 源代码目录
│   ├── pages/            # 页面组件
│   │   ├── ChatPage.tsx  # 聊天页面
│   │   ├── LoginPage.tsx # 登录页面
│   │   ├── IndexPage.tsx # 首页
│   │   └── UploadPage.tsx# 上传页面
│   ├── components/       # 可复用组件
│   │   ├── Layout/       # 布局组件
│   │   ├── Chat/         # 聊天相关组件
│   │   └── Common/       # 通用组件
│   ├── services/         # API服务层
│   │   ├── api.ts        # API基础配置
│   │   ├── auth.ts       # 认证服务
│   │   └── chat.ts       # 聊天服务
│   ├── utils/            # 工具函数
│   │   ├── request.ts    # HTTP请求工具
│   │   ├── storage.ts    # 本地存储工具
│   │   └── constants.ts  # 常量定义
│   ├── types/            # TypeScript类型定义
│   │   ├── api.ts        # API类型
│   │   ├── user.ts       # 用户类型
│   │   └── chat.ts       # 聊天类型
│   ├── hooks/            # 自定义React Hooks
│   │   ├── useAuth.ts    # 认证Hook
│   │   ├── useChat.ts    # 聊天Hook
│   │   └── useApi.ts     # API Hook
│   └── styles/           # 样式文件
│       ├── global.css    # 全局样式
│       └── variables.css # CSS变量
├── public/               # 静态资源
├── .umirc.ts            # UmiJS配置
├── package.json         # 项目配置和依赖
├── tsconfig.json        # TypeScript配置
└── Dockerfile           # 容器化配置
```

### 核心组件开发

#### 1. API服务层
```typescript
// src/services/api.ts
import { extend } from 'umi-request';
import { message } from 'antd';

const request = extend({
  prefix: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
request.interceptors.request.use((url, options) => {
  const token = localStorage.getItem('token');
  if (token) {
    options.headers = {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return {
    url,
    options,
  };
});

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const { response } = error;
    if (response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    } else if (response?.status >= 500) {
      message.error('服务器错误，请稍后重试');
    }
    throw error;
  }
);

export default request;
```

#### 2. 认证Hook
```typescript
// src/hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { message } from 'antd';
import request from '@/services/api';

interface User {
  id: number;
  username: string;
  email: string;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  token: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    token: localStorage.getItem('token'),
  });

  // 登录
  const login = async (username: string, password: string) => {
    try {
      const response = await request.post('/auth/login', {
        data: { username, password },
      });
      
      const { access_token, user } = response;
      localStorage.setItem('token', access_token);
      setAuthState({
        user,
        loading: false,
        token: access_token,
      });
      
      message.success('登录成功');
      return true;
    } catch (error) {
      message.error('登录失败');
      return false;
    }
  };

  // 注销
  const logout = () => {
    localStorage.removeItem('token');
    setAuthState({
      user: null,
      loading: false,
      token: null,
    });
    window.location.href = '/login';
  };

  // 获取当前用户信息
  const getCurrentUser = async () => {
    if (!authState.token) {
      setAuthState(prev => ({ ...prev, loading: false }));
      return;
    }

    try {
      const user = await request.get('/auth/me');
      setAuthState(prev => ({
        ...prev,
        user,
        loading: false,
      }));
    } catch (error) {
      logout();
    }
  };

  useEffect(() => {
    getCurrentUser();
  }, [authState.token]);

  return {
    ...authState,
    login,
    logout,
    getCurrentUser,
  };
};
```

#### 3. 聊天组件
```typescript
// src/components/Chat/ChatInput.tsx
import React, { useState, useRef } from 'react';
import { Input, Button, Upload, message } from 'antd';
import { SendOutlined, PaperClipOutlined } from '@ant-design/icons';

const { TextArea } = Input;

interface ChatInputProps {
  onSendMessage: (message: string, files?: File[]) => void;
  loading?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, loading }) => {
  const [message, setMessage] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const inputRef = useRef<any>(null);

  const handleSend = () => {
    if (!message.trim() && files.length === 0) {
      message.warning('请输入消息或选择文件');
      return;
    }

    onSendMessage(message.trim(), files);
    setMessage('');
    setFiles([]);
    inputRef.current?.focus();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const uploadProps = {
    beforeUpload: (file: File) => {
      setFiles(prev => [...prev, file]);
      return false; // 阻止自动上传
    },
    onRemove: (file: File) => {
      setFiles(prev => prev.filter(f => f !== file));
    },
    fileList: files.map(file => ({
      uid: file.name,
      name: file.name,
      status: 'done' as const,
    })),
  };

  return (
    <div className="chat-input">
      <div className="input-container">
        <TextArea
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="输入您的问题..."
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={loading}
        />
        <div className="actions">
          <Upload {...uploadProps} showUploadList={false}>
            <Button
              icon={<PaperClipOutlined />}
              type="text"
              disabled={loading}
            />
          </Upload>
          <Button
            icon={<SendOutlined />}
            type="primary"
            onClick={handleSend}
            loading={loading}
          />
        </div>
      </div>
      {files.length > 0 && (
        <div className="file-list">
          {files.map(file => (
            <div key={file.name} className="file-item">
              {file.name}
              <Button
                type="text"
                size="small"
                onClick={() => setFiles(prev => prev.filter(f => f !== file))}
              >
                ×
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatInput;
```

### 状态管理

#### 使用Context API
```typescript
// src/contexts/ChatContext.tsx
import React, { createContext, useContext, useReducer, ReactNode } from 'react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: string[];
}

interface ChatState {
  messages: Message[];
  loading: boolean;
  currentSession: string | null;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: Message }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_SESSION'; payload: string }
  | { type: 'CLEAR_MESSAGES' };

const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_SESSION':
      return {
        ...state,
        currentSession: action.payload,
      };
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [],
      };
    default:
      return state;
  }
};

const ChatContext = createContext<{
  state: ChatState;
  dispatch: React.Dispatch<ChatAction>;
} | null>(null);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, {
    messages: [],
    loading: false,
    currentSession: null,
  });

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};
```

### 路由配置
```typescript
// .umirc.ts
import { defineConfig } from 'umi';

export default defineConfig({
  nodeModulesTransform: {
    type: 'none',
  },
  routes: [
    {
      path: '/login',
      component: '@/pages/LoginPage',
    },
    {
      path: '/',
      component: '@/layouts/BasicLayout',
      routes: [
        { path: '/', redirect: '/chat' },
        { path: '/chat', component: '@/pages/ChatPage' },
        { path: '/upload', component: '@/pages/UploadPage' },
        { path: '/config', component: '@/pages/DifyConfigPage' },
      ],
    },
  ],
  fastRefresh: {},
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      pathRewrite: { '^/api': '/api' },
    },
  },
  antd: {},
  layout: false,
  title: 'RAG UI',
});
```

## 代码规范和最佳实践

### Python代码规范

#### 代码格式化工具配置
```bash
# 安装开发工具
poetry add --group dev black isort flake8 mypy pytest pytest-cov

# 创建配置文件
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=app --cov-report=html"
EOF
```

#### 使用格式化工具
```bash
# 格式化代码
poetry run black .
poetry run isort .

# 检查代码质量
poetry run flake8 .
poetry run mypy app/

# 运行测试
poetry run pytest
```

### TypeScript代码规范

#### ESLint和Prettier配置
```json
// .eslintrc.js
module.exports = {
  extends: [
    '@umijs/eslint-config-umi',
    'prettier',
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'no-console': 'warn',
  },
};

// .prettierrc
{
  "singleQuote": true,
  "trailingComma": "es5",
  "printWidth": 80,
  "tabWidth": 2,
  "semi": true
}
```

#### 使用格式化工具
```bash
# 格式化代码
pnpm prettier --write "src/**/*.{ts,tsx}"

# 检查代码质量
pnpm eslint "src/**/*.{ts,tsx}"

# 修复可自动修复的问题
pnpm eslint "src/**/*.{ts,tsx}" --fix
```

### Git工作流

#### 提交消息规范
```bash
# 提交消息格式
type(scope): description

# 类型说明
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式化
refactor: 重构代码
test: 添加测试
chore: 构建工具或辅助工具的变动

# 示例
git commit -m "feat(auth): add JWT token refresh functionality"
git commit -m "fix(chat): resolve message duplication issue"
git commit -m "docs(api): update authentication documentation"
```

#### 分支管理
```bash
# 功能开发流程
git checkout -b feature/user-authentication
# 开发完成后
git add .
git commit -m "feat(auth): implement user login and registration"
git push origin feature/user-authentication
# 创建Pull Request

# 热修复流程
git checkout -b hotfix/fix-login-bug
# 修复完成后
git add .
git commit -m "fix(auth): resolve login token validation issue"
git push origin hotfix/fix-login-bug
```

### 性能优化

#### 后端性能优化
```python
# 使用异步处理
from fastapi import BackgroundTasks

@router.post("/send-email")
async def send_email(
    email_data: EmailSchema,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email_task, email_data)
    return {"message": "Email will be sent"}

# 数据库连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True
)

# 缓存配置
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_permissions(user_id: int):
    # 缓存用户权限查询
    return db.query(Permission).filter(Permission.user_id == user_id).all()
```

#### 前端性能优化
```typescript
// 使用React.memo减少重渲染
const ChatMessage = React.memo<ChatMessageProps>(({ message }) => {
  return <div>{message.content}</div>;
});

// 使用useMemo缓存计算结果
const expensiveValue = useMemo(() => {
  return processLargeData(data);
}, [data]);

// 使用useCallback缓存函数
const handleClick = useCallback((id: string) => {
  onItemClick(id);
}, [onItemClick]);

// 懒加载组件
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// 虚拟滚动处理大量数据
import { FixedSizeList as List } from 'react-window';

const MessageList = ({ messages }) => (
  <List
    height={600}
    itemCount={messages.length}
    itemSize={60}
    itemData={messages}
  >
    {MessageItem}
  </List>
);
```

## 调试和故障排除

### 后端调试

#### 日志配置
```python
# app/config.py
import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger(__name__)
```

#### 使用pdb调试
```python
import pdb

@router.post("/debug-endpoint")
async def debug_endpoint(data: dict):
    pdb.set_trace()  # 设置断点
    # 调试代码
    return {"result": "debug"}
```

### 前端调试

#### 使用React DevTools
```typescript
// 开发环境下启用React严格模式
const App = () => (
  <React.StrictMode>
    <ChatProvider>
      <Router />
    </ChatProvider>
  </React.StrictMode>
);

// 使用useEffect调试状态变化
useEffect(() => {
  console.log('Messages updated:', messages);
}, [messages]);
```

#### 网络请求调试
```typescript
// 添加请求日志
request.interceptors.request.use((url, options) => {
  console.log(`Request: ${options.method} ${url}`, options);
  return { url, options };
});

request.interceptors.response.use((response) => {
  console.log('Response:', response);
  return response;
});
```

### 常见问题解决

#### CORS问题
```python
# 后端CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 数据库连接问题
```python
# 数据库健康检查
@router.get("/health")
async def health_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": f"error: {e}"}
```

---

*开发指南版本: v1.0 | 最后更新: 2025-07-27*
