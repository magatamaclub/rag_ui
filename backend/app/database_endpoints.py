# 数据库状态检查响应模型
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from pydantic import BaseModel, Field

from .database import get_db, engine, Base
from .models import User, UserRole


# 数据库状态检查响应模型
class DatabaseStatusResponse(BaseModel):
    is_initialized: bool = Field(..., description="数据库是否已初始化")
    has_connection: bool = Field(..., description="数据库连接是否正常")
    has_tables: bool = Field(..., description="数据表是否存在")
    has_admin_user: bool = Field(..., description="管理员用户是否存在")
    message: str = Field(..., description="状态描述")


db_router = APIRouter()


@db_router.get(
    "/database/status",
    response_model=DatabaseStatusResponse,
    summary="检查数据库状态",
    description="检查数据库连接状态、表结构和管理员用户是否存在",
)
async def check_database_status(db: Session = Depends(get_db)):
    """
    检查数据库初始化状态

    返回:
    - is_initialized: 数据库是否完全初始化
    - has_connection: 数据库连接是否正常
    - has_tables: 数据表是否存在
    - has_admin_user: 管理员用户是否存在
    - message: 详细状态描述
    """
    try:
        # 检查数据库连接
        from sqlalchemy import text

        db.execute(text("SELECT 1"))
        has_connection = True

        # 检查表是否存在
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        has_tables = len(tables) > 0 and "users" in tables

        # 检查管理员用户是否存在
        has_admin_user = False
        if has_tables:
            admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
            has_admin_user = admin_user is not None

        is_initialized = has_connection and has_tables and has_admin_user

        if is_initialized:
            message = "数据库已完全初始化"
        elif not has_tables:
            message = "数据库连接正常，但缺少数据表"
        elif not has_admin_user:
            message = "数据表存在，但缺少管理员用户"
        else:
            message = "数据库状态异常"

        return DatabaseStatusResponse(
            is_initialized=is_initialized,
            has_connection=has_connection,
            has_tables=has_tables,
            has_admin_user=has_admin_user,
            message=message,
        )

    except Exception as e:
        return DatabaseStatusResponse(
            is_initialized=False,
            has_connection=False,
            has_tables=False,
            has_admin_user=False,
            message=f"数据库连接失败: {str(e)}",
        )


@db_router.post(
    "/database/initialize",
    summary="初始化数据库",
    description="创建数据表并添加默认管理员用户",
)
async def initialize_database(db: Session = Depends(get_db)):
    """
    初始化数据库

    - 创建所有数据表
    - 创建默认管理员用户 (admin/admin123)
    """
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)

        # 检查是否已存在管理员用户
        existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()

        if not existing_admin:
            # 创建默认管理员用户
            from .auth import get_password_hash

            admin_user = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                email="admin@example.com",
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

        return {
            "success": True,
            "message": "数据库初始化成功",
            "admin_username": "admin",
            "admin_password": "admin123",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库初始化失败: {str(e)}")
