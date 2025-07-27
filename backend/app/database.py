from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create engine with connection pool settings
# Create engine with connection pool settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    echo=settings.APP_DEBUG,  # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """检查数据库连接是否正常"""
    try:
        logger.info("🔍 Checking database connection...")

        # 测试数据库连接
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True

    except Exception as e:
        logger.error(f"❌ Database connection check failed: {e}")
        return False


def check_tables_exist() -> bool:
    """检查数据库表是否存在"""
    try:
        logger.info("🔍 Checking if database tables exist...")

        # 检查用户表是否存在
        with engine.connect() as connection:
            query = text(
                "SELECT EXISTS (SELECT FROM information_schema.tables "
                "WHERE table_name = 'users')"
            )
            result = connection.execute(query)
            exists = result.scalar()

            if exists:
                logger.info("✅ Database tables exist")
                return True
            else:
                logger.info("ℹ️ Database tables do not exist, will create them")
                return False

    except Exception as e:
        logger.error(f"❌ Error checking tables: {e}")
        return False


def create_admin_user():
    """创建默认管理员用户（如果不存在）"""
    try:
        from .models import User, UserRole
        from .auth import get_password_hash

        db = SessionLocal()
        try:
            # 检查是否已存在管理员用户
            admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if admin_user:
                logger.info("✅ Admin user already exists")
                return

            # 使用配置文件中的默认管理员设置
            admin_username = settings.DEFAULT_ADMIN_USERNAME
            admin_email = settings.DEFAULT_ADMIN_EMAIL
            admin_password = settings.DEFAULT_ADMIN_PASSWORD

            hashed_password = get_password_hash(admin_password)
            admin_user = User(
                username=admin_username,
                email=admin_email,
                hashed_password=hashed_password,
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            logger.info("✅ Default admin user created successfully")
            logger.info(f"   Username: {admin_username}")
            logger.info(f"   Email: {admin_email}")
            logger.info("   Please change the default password after login!")

        finally:
            db.close()

    except Exception as e:
        logger.error(f"❌ Error creating admin user: {e}")
        raise


def init_database():
    """初始化数据库，创建表结构"""
    try:
        logger.info("🏗️ Creating missing tables...")

        # 检查数据库连接
        if not check_database_connection():
            raise Exception("Database connection failed")

        # 检查表是否存在，如果不存在则创建
        if not check_tables_exist():
            # 导入模型以确保它们被注册
            from . import models  # noqa: F401

            # 创建所有表
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")

        # 创建管理员用户
        create_admin_user()

        logger.info("🎉 Database initialization completed successfully")

    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise
