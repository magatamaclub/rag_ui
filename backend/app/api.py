from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import timedelta
from typing import List, Optional
import requests
import logging
import json
import uuid

from .database import get_db
from .models import DifyConfig, User, DifyApp, UserRole
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_admin_user,
    create_user,
    get_user,
    get_user_by_email,
    get_all_users,
    get_users_count,
    update_user,
    delete_user,
    get_user_by_id,
)
from .schemas import (
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse,
    UserListResponse,
    Token,
    DifyAppCreate,
    DifyAppUpdate,
    DifyAppResponse,
)
from .config import settings

router = APIRouter()

# 设置日志配置
logger = logging.getLogger(__name__)

# Dify API configuration (will be fetched from DB)
DIFY_API_URL = None
DIFY_API_KEY = None


class DifyConfigCreate(BaseModel):
    """Dify配置创建模型"""

    api_url: str = Field(
        ..., description="Dify API地址", example="https://api.dify.ai/v1"
    )
    api_key: str = Field(
        ..., description="Dify API密钥", example="app-xxxxxxxxxxxxxxxxxx"
    )


class ChatRequest(BaseModel):
    """聊天请求模型"""

    query: str = Field(
        ..., description="用户的问题或消息", example="你好，请介绍一下你的功能"
    )
    conversation_id: Optional[str] = Field(
        None, description="对话ID，用于维持对话上下文", example="conv_123456789"
    )


# User Authentication Endpoints
@router.post(
    "/auth/register",
    response_model=UserResponse,
    tags=["authentication"],
    summary="用户注册",
    description="""
    创建新的用户账户。支持以下功能：
    - 用户名和邮箱唯一性验证
    - 密码安全存储（BCrypt加密）
    - 角色分配（USER/ADMIN）
    - 账户激活状态设置
    """,
    responses={
        201: {"description": "用户创建成功"},
        400: {"description": "用户名或邮箱已存在"},
    },
)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    role = user.role or UserRole.USER
    db_user = create_user(db, user.username, user.email, user.password, role)
    return db_user


@router.post(
    "/auth/login",
    response_model=Token,
    tags=["authentication"],
    summary="用户登录",
    description="""
    验证用户凭据并返回JWT访问令牌。
    
    使用说明：
    1. 提供有效的用户名和密码
    2. 获取JWT访问令牌
    3. 在后续请求中携带令牌：Authorization: Bearer <token>
    """,
    responses={
        200: {"description": "登录成功，返回访问令牌"},
        401: {"description": "用户名或密码错误"},
    },
)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user or user is False:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(getattr(user, "username", ""))},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/auth/me",
    response_model=UserResponse,
    tags=["authentication"],
    summary="获取当前用户信息",
    description="""
    获取当前登录用户的详细信息。
    
    返回包括：
    - 用户基本信息
    - 用户角色和权限
    - 账户创建和更新时间
    - 账户状态
    """,
    responses={
        200: {"description": "用户信息获取成功"},
        401: {"description": "未认证 - 需要有效的JWT令牌"},
    },
)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.get("/auth/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    """Example protected route that requires authentication."""
    return {"message": f"Hello {current_user.username}, this is a protected route!"}


# User Management Endpoints (Admin Only)
@router.get(
    "/users",
    response_model=UserListResponse,
    tags=["user_management"],
    summary="获取用户列表",
    description="""
    获取所有用户的列表（仅管理员）。
    
    支持分页参数：
    - page: 页码，从1开始
    - size: 每页数量，默认20
    """,
)
async def get_users(
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get all users with pagination (Admin only)."""
    skip = (page - 1) * size
    users = get_all_users(db, skip=skip, limit=size)
    total = get_users_count(db)

    return UserListResponse(users=users, total=total, page=page, size=size)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["user_management"],
    summary="获取用户详情",
    description="获取指定用户的详细信息（仅管理员）",
)
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get user details by ID (Admin only)."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post(
    "/users",
    response_model=UserResponse,
    tags=["user_management"],
    summary="创建新用户",
    description="""
    创建新用户（仅管理员）。
    
    注意：
    - 邮箱是必填项且必须是有效的邮箱格式
    - 用户名必须唯一
    - 邮箱必须唯一
    """,
)
async def create_user_admin(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a new user (Admin only)."""
    # Check if user already exists
    existing_user = get_user(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = get_user_by_email(db, user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    role = user.role or UserRole.USER
    db_user = create_user(db, user.username, user.email, user.password, role)
    return db_user


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    tags=["user_management"],
    summary="更新用户信息",
    description="更新指定用户的信息（仅管理员）",
)
async def update_user_admin(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update user information (Admin only)."""
    # Check if user exists
    existing_user = get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check username uniqueness if updating username
    if user_update.username and user_update.username != existing_user.username:
        username_exists = get_user(db, user_update.username)
        if username_exists:
            raise HTTPException(status_code=400, detail="Username already taken")

    # Check email uniqueness if updating email
    if user_update.email and user_update.email != existing_user.email:
        email_exists = get_user_by_email(db, user_update.email)
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already taken")

    # Update user
    updated_user = update_user(
        db,
        user_id,
        username=user_update.username,
        email=user_update.email,
        role=user_update.role,
        is_active=user_update.is_active,
    )

    return updated_user


@router.delete(
    "/users/{user_id}",
    tags=["user_management"],
    summary="删除用户",
    description="""
    删除指定用户（仅管理员）。
    
    注意：管理员不能删除自己的账户。
    """,
)
async def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Delete a user (Admin only)."""
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    # Check if user exists
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete user
    success = delete_user(db, user_id)
    if success:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete user")


# Dify Configuration Endpoints
@router.post("/dify-config")
async def set_dify_config(config: DifyConfigCreate, db: Session = Depends(get_db)):
    logger.info("⚙️ Setting Dify configuration")
    logger.info(f"🔗 API URL: {config.api_url}")
    logger.info(f"🔑 API Key: {config.api_key[:10]}...")

    existing_config = db.query(DifyConfig).first()
    if existing_config:
        logger.info("📝 Updating existing Dify configuration")
        existing_config.api_url = config.api_url
        existing_config.api_key = config.api_key
    else:
        logger.info("✨ Creating new Dify configuration")
        new_config = DifyConfig(api_url=config.api_url, api_key=config.api_key)
        db.add(new_config)
    db.commit()
    db.refresh(existing_config or new_config)
    global DIFY_API_URL, DIFY_API_KEY
    DIFY_API_URL = config.api_url
    DIFY_API_KEY = config.api_key
    logger.info("✅ Dify configuration saved successfully")
    return {"message": "Dify configuration saved successfully"}


@router.get("/dify-config")
async def get_dify_config(db: Session = Depends(get_db)):
    logger.info("📖 Retrieving Dify configuration")
    config = db.query(DifyConfig).first()
    if not config:
        logger.error("❌ Dify configuration not found")
        raise HTTPException(status_code=404, detail="Dify configuration not found")

    logger.info(f"✅ Found Dify config - URL: {config.api_url}")
    return {"api_url": config.api_url, "api_key": config.api_key}


@router.on_event("startup")
async def load_dify_config_on_startup():
    """加载Dify配置到全局变量（启动时）"""
    global DIFY_API_URL, DIFY_API_KEY
    try:
        logger.info("🚀 Starting Dify configuration loading...")
        # 跳过数据库访问，避免psycopg2内存错误
        logger.warning("⚠️ Skipping Dify config loading due to database driver issues")
        # 设置默认值
        DIFY_API_URL = "http://localhost:5000"
        DIFY_API_KEY = "default-key"
        logger.info(f"🔧 Using default Dify config: {DIFY_API_URL}")
        logger.info("✅ Dify configuration initialization completed")
    except Exception as e:
        logger.error(f"❌ Could not load Dify config: {e}")
        print(f"⚠️ Could not load Dify config: {e}")


# Document and Chat Endpoints (Protected)
@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...), current_user: User = Depends(get_current_active_user)
):
    if not DIFY_API_URL or not DIFY_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="Dify API configuration is missing. "
            "Please set it via /api/v1/dify-config.",
        )

    url = f"{DIFY_API_URL}/files/upload"
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}"}

    file_content = await file.read()
    files = {"file": (file.filename, file_content, file.content_type)}
    data = {"user": str(getattr(current_user, "username", "unknown"))}

    logger.info("📤 Uploading document to Dify API")
    logger.info(f"🔗 URL: {url}")
    logger.info(f"📄 File: {file.filename} ({file.content_type})")
    logger.info(f"👤 User: {getattr(current_user, 'username', 'unknown')}")

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        logger.info(f"📡 Dify API Response Status: {response.status_code}")
        logger.info(f"📡 Dify API Response Headers: {dict(response.headers)}")

        if response.status_code >= 400:
            logger.error(f"❌ Dify API Error Response: {response.text}")

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        response_data = response.json()
        logger.info(f"✅ Document upload successful: {response_data}")
        return response_data
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error calling Dify API: {e}")
        raise HTTPException(status_code=500, detail=f"Error calling Dify API: {e}")


@router.post("/chat")
async def chat(request: Request, current_user: User = Depends(get_current_active_user)):
    if not DIFY_API_URL or not DIFY_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="Dify API configuration is missing. "
            "Please set it via /api/v1/dify-config.",
        )

    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"❌ JSON parsing error: {e}")
        raise HTTPException(
            status_code=400, detail=f"Invalid JSON in request body: {str(e)}"
        )

    query = data.get("query")
    conversation_id = data.get("conversation_id")

    if not query:
        logger.error("❌ Missing query parameter")
        raise HTTPException(status_code=400, detail="Query is required")

    # Dify API conversation_id 处理逻辑：
    # - 第一次对话：不传递 conversation_id，让 Dify 自动生成
    # - 后续对话：传递前一次对话返回的 conversation_id
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "user": str(getattr(current_user, "username", "unknown")),
    }

    # 只有当conversation_id存在且有效时才添加到payload中
    if conversation_id:
        try:
            # 验证conversation_id是否为有效的UUID格式
            uuid.UUID(conversation_id)
            payload["conversation_id"] = conversation_id
            logger.info(f"🔄 Using existing conversation ID: {conversation_id}")
        except ValueError:
            logger.warning(
                f"⚠️ Invalid conversation_id format, ignoring: {conversation_id}"
            )
            logger.info("🆔 Starting new conversation (no conversation_id)")
    else:
        logger.info("🆔 Starting new conversation (no conversation_id)")

    url = f"{DIFY_API_URL}/chat-messages"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info("💬 Starting Dify chat API call")
    logger.info(f"🔗 URL: {url}")
    logger.info(f"👤 User: {getattr(current_user, 'username', 'unknown')}")
    logger.info(f"💭 Query: {query}")
    if "conversation_id" in payload:
        logger.info(f"🔄 Conversation ID: {payload['conversation_id']}")
    else:
        logger.info("🆔 New conversation (no ID provided)")
    
    # 详细的请求日志 (通用聊天接口)
    logger.info("📤 === DIFY CHAT API REQUEST DETAILS ===")
    logger.info("🌐 Request Method: POST")
    logger.info(f"� Request URL: {url}")
    logger.info("📋 Request Headers:")
    for header_key, header_value in headers.items():
        if header_key.lower() == 'authorization':
            # 隐藏API密钥的敏感部分
            masked_value = (
                f"{header_value[:20]}...{header_value[-10:]}" 
                if len(header_value) > 30 else header_value
            )
            logger.info(f"    {header_key}: {masked_value}")
        else:
            logger.info(f"    {header_key}: {header_value}")
    
    logger.info("�📦 Request Payload (JSON):")
    logger.info(f"    inputs: {payload.get('inputs', {})}")
    logger.info(f"    query: {payload.get('query', 'N/A')}")
    logger.info(f"    response_mode: {payload.get('response_mode', 'N/A')}")
    logger.info(f"    user: {payload.get('user', 'N/A')}")
    logger.info(f"    conversation_id: {payload.get('conversation_id', 'N/A')[:36]}")
    logger.info(f"📏 Payload Size: {len(json.dumps(payload))} bytes")
    logger.info("=" * 50)

    def generate_dify_response():
        try:
            logger.info("📡 Initiating streaming request to Dify API...")
            
            # 记录请求开始时间
            import time
            request_start_time = time.time()
            
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=30
            ) as response:
                # 记录响应时间
                response_time = time.time() - request_start_time
                
                logger.info("� === DIFY CHAT API RESPONSE DETAILS ===")
                logger.info(f"⏱️ Response Time: {response_time:.3f} seconds")
                logger.info(f"📡 Status Code: {response.status_code}")
                logger.info(f"� Status Text: {response.reason}")
                logger.info("📋 Response Headers:")
                for header_key, header_value in response.headers.items():
                    logger.info(f"    {header_key}: {header_value}")
                logger.info(
                    f"🔄 Stream Mode: {response.headers.get('Transfer-Encoding', 'N/A')}"
                )
                logger.info(
                    f"📏 Content-Type: {response.headers.get('Content-Type', 'N/A')}"
                )
                logger.info("=" * 50)

                if response.status_code >= 400:
                    error_text = response.text
                    logger.error("❌ === DIFY CHAT API ERROR RESPONSE ===")
                    logger.error(f"💥 Error Status: {response.status_code}")
                    logger.error(f"📄 Error Content: {error_text}")
                    logger.error(
                        f"📏 Error Content Length: {len(error_text)} bytes"
                    )
                    logger.error("=" * 50)

                response.raise_for_status()

                chunk_count = 0
                total_data_size = 0
                logger.info("🔄 Starting to process streaming response...")
                
                for line in response.iter_lines(decode_unicode=True):
                    if line.strip():
                        chunk_count += 1
                        total_data_size += len(line)
                        
                        if chunk_count == 1:
                            logger.info("✅ Receiving first chunk from Dify API")
                        elif chunk_count % 10 == 0:  # 每10个chunk记录一次
                            logger.info(
                                f"📊 Progress: {chunk_count} chunks, "
                                f"{total_data_size} bytes received"
                            )

                        # 处理SSE格式的数据
                        if line.startswith("data: "):
                            data_content = line[6:]  # 移除 "data: " 前缀
                            try:
                                # 解析JSON数据
                                event_data = json.loads(data_content)
                                event_type = event_data.get('event', 'unknown')
                                
                                # 详细记录重要事件
                                important_events = ['text_chunk', 'llm_end', 'message_end']
                                if event_type in important_events:
                                    logger.info(
                                        f"📦 Event: {event_type} (chunk #{chunk_count})"
                                    )
                                    if event_type == 'text_chunk' and chunk_count <= 3:
                                        # 只记录前几个text_chunk的部分内容
                                        answer_preview = event_data.get('answer', '')[:50]
                                        logger.info(
                                            f"💬 Answer preview: {answer_preview}..."
                                        )

                                # 转发原始数据
                                yield f"data: {data_content}\n\n"
                            except json.JSONDecodeError:
                                # 如果不是JSON格式，直接转发
                                logger.warning(
                                    f"⚠️ Non-JSON chunk: {line[:100]}..."
                                )
                                yield f"{line}\n"
                        else:
                            # 转发非data行（如event:等）
                            logger.info(f"📋 SSE Header: {line}")
                            yield f"{line}\n"

                logger.info("🏁 === DIFY CHAT API RESPONSE SUMMARY ===")
                logger.info("✅ Streaming completed successfully")
                logger.info(f"📊 Total chunks processed: {chunk_count}")
                logger.info(f"📏 Total data received: {total_data_size} bytes")
                response_time_total = time.time() - request_start_time
                logger.info(f"⏱️ Total response time: {response_time_total:.3f}s")
                logger.info("=" * 50)
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error calling Dify chat API: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error calling Dify chat API: {e}"
            )

    return StreamingResponse(generate_dify_response(), media_type="text/event-stream")


# Dify App Management Endpoints (Admin Only)
@router.post("/dify-apps", response_model=DifyAppResponse)
async def create_dify_app(
    app: DifyAppCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Create a new Dify app (Admin only)."""
    db_app = DifyApp(
        name=app.name,
        app_type=app.app_type,
        api_key=app.api_key,
        api_url=app.api_url,
        description=app.description,
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app


@router.get("/dify-apps", response_model=List[DifyAppResponse])
async def get_dify_apps(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all active Dify apps."""
    apps = db.query(DifyApp).filter(DifyApp.is_active.is_(True)).all()
    return apps


@router.get("/dify-apps/{app_id}", response_model=DifyAppResponse)
async def get_dify_app(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific Dify app."""
    app = db.query(DifyApp).filter(DifyApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Dify app not found")
    return app


@router.put("/dify-apps/{app_id}", response_model=DifyAppResponse)
async def update_dify_app(
    app_id: int,
    app_update: DifyAppUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Update a Dify app (Admin only)."""
    app = db.query(DifyApp).filter(DifyApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Dify app not found")

    update_data = app_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(app, field, value)

    db.commit()
    db.refresh(app)
    return app


@router.delete("/dify-apps/{app_id}")
async def delete_dify_app(
    app_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Delete a Dify app (Admin only)."""
    app = db.query(DifyApp).filter(DifyApp.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Dify app not found")

    setattr(app, "is_active", False)
    db.commit()
    return {"message": "Dify app deleted successfully"}


# Enhanced chat endpoint with app selection
@router.post("/chat/app/{app_id}")
async def chat_with_app(
    app_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Chat using a specific Dify app."""
    logger.info(f"🎯 Chat with specific app request - App ID: {app_id}")

    # Get the selected app
    app = (
        db.query(DifyApp)
        .filter(DifyApp.id == app_id, DifyApp.is_active.is_(True))
        .first()
    )
    if not app:
        logger.error(f"❌ Dify app not found - App ID: {app_id}")
        raise HTTPException(status_code=404, detail="Dify app not found")

    logger.info(f"✅ Found Dify app: {getattr(app, 'name', 'Unknown')}")
    logger.info(f"🔗 App API URL: {getattr(app, 'api_url', '')}")
    logger.info(f"🔑 App API Key: {getattr(app, 'api_key', '')[:10]}...")

    # 增强的JSON解析错误处理
    try:
        # 检查Content-Type
        content_type = request.headers.get("content-type", "").lower()
        logger.info(f"📋 Request Content-Type: {content_type}")

        # 获取原始请求体
        body = await request.body()
        logger.info(f"📄 Request body length: {len(body)} bytes")

        if len(body) == 0:
            logger.error("❌ Empty request body")
            raise HTTPException(
                status_code=400,
                detail="Request body is empty. Please provide JSON data with 'query' field.",
            )

        # 尝试解析JSON
        try:
            data = json.loads(body.decode("utf-8"))
            logger.info(
                f"✅ Successfully parsed JSON data: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}"
            )
        except json.JSONDecodeError as json_err:
            logger.error(f"❌ JSON decode error: {json_err}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(json_err)}. Please ensure request body contains valid JSON.",
            )
        except UnicodeDecodeError as decode_err:
            logger.error(f"❌ Unicode decode error: {decode_err}")
            raise HTTPException(
                status_code=400,
                detail="Request body contains invalid UTF-8 characters.",
            )

    except HTTPException:
        # 重新抛出我们自己的HTTPException
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during request parsing: {e}")
        raise HTTPException(
            status_code=400, detail=f"Error processing request: {str(e)}"
        )

    query = data.get("query")
    conversation_id = data.get("conversation_id")

    if not query:
        logger.error("❌ Missing query parameter")
        raise HTTPException(status_code=400, detail="Query is required")

    # Dify API conversation_id 处理逻辑：
    # - 第一次对话：不传递 conversation_id，让 Dify 自动生成
    # - 后续对话：传递前一次对话返回的 conversation_id
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "user": str(getattr(current_user, "username", "unknown")),
    }

    # 只有当conversation_id存在且有效时才添加到payload中
    if conversation_id:
        try:
            # 验证conversation_id是否为有效的UUID格式
            uuid.UUID(conversation_id)
            payload["conversation_id"] = conversation_id
            logger.info(f"🔄 Using existing conversation ID: {conversation_id}")
        except ValueError:
            logger.warning(
                f"⚠️ Invalid conversation_id format, ignoring: {conversation_id}"
            )
            logger.info("🆔 Starting new conversation (no conversation_id)")
    else:
        logger.info("🆔 Starting new conversation (no conversation_id)")

    url = f"{getattr(app, 'api_url', '')}/chat-messages"
    headers = {
        "Authorization": f"Bearer {getattr(app, 'api_key', '')}",
        "Content-Type": "application/json",
    }

    logger.info("💬 Starting Dify app chat API call")
    logger.info(f"🔗 URL: {url}")
    logger.info(f"👤 User: {getattr(current_user, 'username', 'unknown')}")
    logger.info(f"💭 Query: {query}")
    if "conversation_id" in payload:
        logger.info(f"🔄 Conversation ID: {payload['conversation_id']}")
    else:
        logger.info("🆔 New conversation (no ID provided)")
    
    # 详细的请求日志
    logger.info("📤 === DIFY API REQUEST DETAILS ===")
    logger.info(f"🌐 Request Method: POST")
    logger.info(f"🔗 Request URL: {url}")
    logger.info(f"📋 Request Headers:")
    for header_key, header_value in headers.items():
        if header_key.lower() == 'authorization':
            # 隐藏API密钥的敏感部分
            masked_value = f"{header_value[:20]}...{header_value[-10:]}" if len(header_value) > 30 else header_value
            logger.info(f"    {header_key}: {masked_value}")
        else:
            logger.info(f"    {header_key}: {header_value}")
    
    logger.info(f"📦 Request Payload (JSON):")
    logger.info(f"    inputs: {payload.get('inputs', {})}")
    logger.info(f"    query: {payload.get('query', 'N/A')}")
    logger.info(f"    response_mode: {payload.get('response_mode', 'N/A')}")
    logger.info(f"    user: {payload.get('user', 'N/A')}")
    logger.info(f"    conversation_id: {payload.get('conversation_id', 'N/A')}")
    logger.info(f"📏 Payload Size: {len(json.dumps(payload))} bytes")
    logger.info("=" * 50)

    def generate_dify_response():
        try:
            logger.info("📡 Initiating streaming request to Dify app API...")
            
            # 记录请求开始时间
            import time
            request_start_time = time.time()
            
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=30
            ) as response:
                # 记录响应时间
                response_time = time.time() - request_start_time
                
                logger.info("� === DIFY API RESPONSE DETAILS ===")
                logger.info(f"⏱️ Response Time: {response_time:.3f} seconds")
                logger.info(f"📡 Status Code: {response.status_code}")
                logger.info(f"📊 Status Text: {response.reason}")
                logger.info(f"� Response Headers:")
                for header_key, header_value in response.headers.items():
                    logger.info(f"    {header_key}: {header_value}")
                logger.info(f"🔄 Stream Mode: {response.headers.get('Transfer-Encoding', 'N/A')}")
                logger.info(f"📏 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                logger.info("=" * 50)

                if response.status_code >= 400:
                    error_text = response.text
                    logger.error("❌ === DIFY API ERROR RESPONSE ===")
                    logger.error(f"💥 Error Status: {response.status_code}")
                    logger.error(f"📄 Error Content: {error_text}")
                    logger.error(f"📏 Error Content Length: {len(error_text)} bytes")
                    logger.error("=" * 50)

                response.raise_for_status()

                chunk_count = 0
                total_data_size = 0
                logger.info("🔄 Starting to process streaming response...")
                
                for line in response.iter_lines(decode_unicode=True):
                    if line.strip():
                        chunk_count += 1
                        total_data_size += len(line)
                        
                        if chunk_count == 1:
                            logger.info(
                                "✅ Receiving first chunk from Dify app API"
                            )
                        elif chunk_count % 10 == 0:  # 每10个chunk记录一次
                            logger.info(
                                f"📊 Progress: {chunk_count} chunks, "
                                f"{total_data_size} bytes received"
                            )

                        # 处理SSE格式的数据
                        if line.startswith("data: "):
                            data_content = line[6:]  # 移除 "data: " 前缀
                            try:
                                # 解析JSON数据
                                event_data = json.loads(data_content)
                                event_type = event_data.get('event', 'unknown')
                                
                                # 详细记录重要事件
                                if event_type in ['text_chunk', 'llm_end', 'message_end']:
                                    logger.info(
                                        f"📦 Event: {event_type} "
                                        f"(chunk #{chunk_count})"
                                    )
                                    if event_type == 'text_chunk' and chunk_count <= 3:
                                        # 只记录前几个text_chunk的部分内容
                                        answer_preview = event_data.get('answer', '')[:50]
                                        logger.info(f"💬 Answer preview: {answer_preview}...")

                                # 转发原始数据
                                yield f"data: {data_content}\n\n"
                            except json.JSONDecodeError:
                                # 如果不是JSON格式，直接转发
                                logger.warning(f"⚠️ Non-JSON chunk: {line[:100]}...")
                                yield f"{line}\n"
                        else:
                            # 转发非data行（如event:等）
                            logger.info(f"📋 SSE Header: {line}")
                            yield f"{line}\n"

                logger.info("🏁 === DIFY API RESPONSE SUMMARY ===")
                logger.info(f"✅ Streaming completed successfully")
                logger.info(f"📊 Total chunks processed: {chunk_count}")
                logger.info(f"📏 Total data received: {total_data_size} bytes")
                logger.info(f"⏱️ Total response time: {time.time() - request_start_time:.3f}s")
                logger.info("=" * 50)
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error calling Dify app chat API: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error calling Dify chat API: {e}"
            )

    return StreamingResponse(generate_dify_response(), media_type="text/event-stream")
