from fastapi import FastAPI
from app.api import router as api_router
from app.database import init_database, get_db
from app.config import settings
from app.models import User, UserRole
from app.auth import create_user, get_user
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG UI Backend",
    description="Backend API for RAG UI with Dify Integration",
    version="1.0.0",
    debug=settings.APP_DEBUG,
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
        # Initialize database tables
        init_database()
        logger.info("✅ Database initialized successfully")

        # Create default admin user
        create_default_admin()

        logger.info("✅ Application startup completed successfully")
    except Exception as e:
        logger.warning("⚠️ Database initialization failed: %s", e)
        logger.warning("🔄 Application will continue without database tables")
        logger.warning("📝 You may need to initialize the database manually")


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"Hello": "World"}
