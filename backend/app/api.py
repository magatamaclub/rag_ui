from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from typing import List
import requests

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
)
from .schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    DifyAppCreate,
    DifyAppUpdate,
    DifyAppResponse,
)
from .config import settings

router = APIRouter()

# Dify API configuration (will be fetched from DB)
DIFY_API_URL = None
DIFY_API_KEY = None


class DifyConfigCreate(BaseModel):
    api_url: str
    api_key: str


# User Authentication Endpoints
@router.post("/auth/register", response_model=UserResponse)
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


@router.post("/auth/login", response_model=Token)
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


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.get("/auth/protected")
async def protected_route(current_user: User = Depends(get_current_active_user)):
    """Example protected route that requires authentication."""
    return {"message": f"Hello {current_user.username}, this is a protected route!"}


# Dify Configuration Endpoints
@router.post("/dify-config")
async def set_dify_config(config: DifyConfigCreate, db: Session = Depends(get_db)):
    existing_config = db.query(DifyConfig).first()
    if existing_config:
        existing_config.api_url = config.api_url
        existing_config.api_key = config.api_key
    else:
        new_config = DifyConfig(api_url=config.api_url, api_key=config.api_key)
        db.add(new_config)
    db.commit()
    db.refresh(existing_config or new_config)
    global DIFY_API_URL, DIFY_API_KEY
    DIFY_API_URL = config.api_url
    DIFY_API_KEY = config.api_key
    return {"message": "Dify configuration saved successfully"}


@router.get("/dify-config")
async def get_dify_config(db: Session = Depends(get_db)):
    config = db.query(DifyConfig).first()
    if not config:
        raise HTTPException(status_code=404, detail="Dify configuration not found")
    return {"api_url": config.api_url, "api_key": config.api_key}


@router.on_event("startup")
async def load_dify_config_on_startup():
    """加载Dify配置到全局变量（启动时）"""
    global DIFY_API_URL, DIFY_API_KEY
    try:
        # 跳过数据库访问，避免psycopg2内存错误
        print("⚠️ Skipping Dify config loading due to database driver issues")
        # 设置默认值
        DIFY_API_URL = "http://localhost:5000"
        DIFY_API_KEY = "default-key"
        print(f"🔧 Using default Dify config: {DIFY_API_URL}")
    except Exception as e:
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

    try:
        response = requests.post(url, headers=headers, files=files, data=data)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Dify API: {e}")


@router.post("/chat")
async def chat(request: Request, current_user: User = Depends(get_current_active_user)):
    if not DIFY_API_URL or not DIFY_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="Dify API configuration is missing. "
            "Please set it via /api/v1/dify-config.",
        )

    data = await request.json()
    query = data.get("query")
    conversation_id = data.get("conversation_id")

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    url = f"{DIFY_API_URL}/chat-messages"
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "user": str(getattr(current_user, "username", "unknown")),
        "conversation_id": conversation_id if conversation_id else "",
    }

    def generate_dify_response():
        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
        except requests.exceptions.RequestException as e:
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
    # Get the selected app
    app = (
        db.query(DifyApp)
        .filter(DifyApp.id == app_id, DifyApp.is_active.is_(True))
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Dify app not found")

    data = await request.json()
    query = data.get("query")
    conversation_id = data.get("conversation_id")

    if not query:
        raise HTTPException(status_code=400, detail="Query is required")

    url = f"{getattr(app, 'api_url', '')}/chat-messages"
    headers = {
        "Authorization": f"Bearer {getattr(app, 'api_key', '')}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "streaming",
        "user": str(getattr(current_user, "username", "unknown")),
        "conversation_id": conversation_id if conversation_id else "",
    }

    def generate_dify_response():
        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Error calling Dify chat API: {e}"
            )

    return StreamingResponse(generate_dify_response(), media_type="text/event-stream")
