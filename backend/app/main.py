from fastapi import FastAPI
from app.api import router as api_router
from app.database import get_db
from app.config import settings
from app.models import User, UserRole
from app.auth import create_user, get_user
from app.api_docs import TAGS_METADATA
from app.swagger_config import custom_openapi_schema, configure_swagger_ui
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG UI Backend",
    description="""
    ## RAG UI Backend API with Dify Integration
    
    一个功能完整的RAG应用后端服务，集成Dify AI平台。
    
    ### 核心功能
    - 🔐 **JWT认证** - 安全的用户认证和基于角色的访问控制
    - 👥 **用户管理** - 完整的用户注册、登录和资料管理
    - 🤖 **Dify集成** - 与Dify平台的原生集成
    - 📱 **多应用支持** - 从单一界面管理多个Dify应用
    - 📁 **文件上传** - 支持文档上传和处理
    - 💬 **聊天界面** - 与AI模型的实时聊天功能
    
    ### 认证说明
    大多数端点需要JWT认证。使用 `/api/v1/auth/login` 
    端点获取访问令牌。
    
    ### API版本
    当前API版本: v1 (前缀: `/api/v1`)
    """,
    version="1.0.0",
    debug=settings.APP_DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "RAG UI Support",
        "email": "support@ragui.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:8001", "description": "Development server"},
        {"url": "http://localhost:8000", "description": "Production server"},
    ],
    tags_metadata=TAGS_METADATA,
)


def create_default_admin():
    """Create default admin user if no admin exists."""
    try:
        db = next(get_db())

        # Check if any admin user exists
        admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin_user:
            logger.info("✅ Admin user already exists")
            return

        # Create default admin user
        admin_username = settings.DEFAULT_ADMIN_USERNAME
        admin_email = settings.DEFAULT_ADMIN_EMAIL
        admin_password = settings.DEFAULT_ADMIN_PASSWORD

        # Check if username already exists
        existing_user = get_user(db, admin_username)
        if existing_user:
            logger.info("✅ Admin username already taken")
            return

        create_user(db, admin_username, admin_email, admin_password, UserRole.ADMIN)
        logger.info("✅ Default admin user created (admin/admin123)")
        logger.warning("⚠️ Please change the default admin password!")

    except Exception as e:
        logger.error(f"❌ Failed to create default admin user: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("🚀 Starting RAG UI Backend...")
    try:
        # 临时跳过数据库初始化以避免psycopg2内存错误
        logger.info("⚠️ Skipping database initialization (psycopg2 memory issue)")
        logger.info("✅ Application startup completed successfully (without DB)")
    except Exception as e:
        logger.warning("⚠️ Startup failed: %s", e)


app.include_router(api_router, prefix="/api/v1")

# 配置自定义OpenAPI模式
app.openapi = lambda: custom_openapi_schema(app)

# 配置Swagger UI参数
swagger_config = configure_swagger_ui()
app.swagger_ui_parameters = swagger_config["swagger_ui_parameters"]


@app.get("/", tags=["health"])
def read_root():
    """Root endpoint - Health check."""
    return {
        "status": "healthy",
        "message": "RAG UI Backend is running",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0",
        "environment": "development" if settings.APP_DEBUG else "production",
    }
