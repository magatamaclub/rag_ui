# Database Management API Endpoints
# 数据库管理相关的API接口

from fastapi import HTTPException
from sqlalchemy import inspect
from .database import engine, get_db
from .models import User, UserRole


# 添加到 api.py 的数据库状态检测接口
def add_database_endpoints(router):
    @router.get(
        "/database/status",
        tags=["database"],
        summary="检查数据库状态",
        description="""
        ## 检查数据库连接和初始化状态
        
        返回数据库的详细状态信息：
        - 🔗 数据库连接状态
        - 📊 数据表是否存在
        - 👤 是否有管理员用户
        - 🏗️ 是否需要初始化
        """,
        responses={
            200: {
                "description": "数据库状态检查成功",
                "content": {
                    "application/json": {
                        "example": {
                            "connected": True,
                            "tables_exist": True,
                            "admin_exists": True,
                            "initialized": True,
                            "requires_setup": False,
                        }
                    }
                },
            },
            500: {"description": "数据库连接失败"},
        },
    )
    async def check_database_status():
        """检查数据库状态"""
        try:
            # 检查数据库连接
            with engine.connect() as conn:
                # 检查表是否存在
                inspector = inspect(engine)
                existing_tables = inspector.get_table_names()

                required_tables = ["users", "dify_configs", "dify_apps"]
                tables_exist = all(
                    table in existing_tables for table in required_tables
                )

                # 检查是否有管理员用户
                admin_exists = False
                if tables_exist:
                    try:
                        db = next(get_db())
                        admin_user = (
                            db.query(User).filter(User.role == UserRole.ADMIN).first()
                        )
                        admin_exists = admin_user is not None
                    except Exception:
                        pass

                initialized = tables_exist and admin_exists

                return {
                    "connected": True,
                    "tables_exist": tables_exist,
                    "admin_exists": admin_exists,
                    "initialized": initialized,
                    "requires_setup": not initialized,
                    "existing_tables": existing_tables,
                }

        except Exception as e:
            # 数据库连接失败或其他错误
            return {
                "connected": False,
                "tables_exist": False,
                "admin_exists": False,
                "initialized": False,
                "requires_setup": True,
                "error": str(e),
            }

    @router.post(
        "/database/initialize",
        tags=["database"],
        summary="初始化数据库",
        description="""
        ## 初始化数据库和创建管理员用户
        
        执行以下操作：
        - 🏗️ 创建所有必要的数据表
        - 👤 创建默认管理员用户
        - ⚙️ 设置基础配置
        """,
        responses={
            200: {
                "description": "数据库初始化成功",
                "content": {
                    "application/json": {
                        "example": {
                            "success": True,
                            "message": "Database initialized successfully",
                            "admin_created": True,
                        }
                    }
                },
            },
            500: {"description": "初始化失败"},
        },
    )
    async def initialize_database():
        """初始化数据库"""
        try:
            from .database import init_database
            from .main import create_default_admin

            # 创建数据表
            init_database()

            # 创建默认管理员用户
            try:
                create_default_admin()
                admin_created = True
            except Exception:
                admin_created = False

            return {
                "success": True,
                "message": "Database initialized successfully",
                "admin_created": admin_created,
                "timestamp": "2024-01-01T10:00:00Z",
            }

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database initialization failed: {str(e)}"
            )

    return router
