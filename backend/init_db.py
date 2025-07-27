#!/usr/bin/env python3
"""
Database initialization script for RAG UI Backend.
This script can be run independently to initialize the database.
- Creates all tables
- Creates default admin user
- Creates sample Dify app
"""

import sys
import logging
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_database, get_db
from app.config import settings
from app.models import User, UserRole, DifyApp, DifyAppType
from app.auth import create_user, get_user

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "admin123"  # Should be changed in production

        # Check if username already exists
        existing_user = get_user(db, admin_username)
        if existing_user:
            logger.info("✅ Admin username already taken")
            return

        create_user(db, admin_username, admin_email, admin_password, UserRole.ADMIN)
        logger.info("✅ Default admin user created")
        logger.info(f"   Username: {admin_username}")
        logger.info(f"   Password: {admin_password}")
        logger.warning("⚠️ Please change the default admin password!")

    except Exception as e:
        logger.error(f"❌ Failed to create default admin user: {e}")


def create_sample_dify_app():
    """Create a sample Dify app for testing."""
    try:
        db = next(get_db())

        # Check if any Dify app exists
        existing_app = db.query(DifyApp).first()
        if existing_app:
            logger.info("✅ Dify app already exists")
            return

        # Create sample app
        sample_app = DifyApp(
            name="示例聊天机器人",
            app_type=DifyAppType.CHATBOT,
            api_key="your-dify-api-key-here",
            api_url="https://api.dify.ai/v1",
            description="这是一个示例Dify聊天机器人应用，请在管理页面修改配置",
            is_active=True,
        )
        db.add(sample_app)
        db.commit()
        db.refresh(sample_app)
        logger.info("✅ Sample Dify app created")

    except Exception as e:
        logger.error(f"❌ Failed to create sample Dify app: {e}")


def main():
    """Main initialization function."""
    logger.info("🔧 RAG UI Database Initialization Tool")

    # Hide password in logs
    db_url_safe = settings.DATABASE_URL
    if settings.DB_PASSWORD:
        db_url_safe = db_url_safe.replace(settings.DB_PASSWORD, "****")
    logger.info(f"Database URL: {db_url_safe}")

    try:
        # Initialize database tables
        logger.info("📊 Initializing database tables...")
        init_database()
        logger.info("✅ Database tables initialized successfully")

        # Create default admin user
        logger.info("👤 Creating default admin user...")
        create_default_admin()

        # Create sample Dify app
        logger.info("🤖 Creating sample Dify app...")
        create_sample_dify_app()

        logger.info("🎉 Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
