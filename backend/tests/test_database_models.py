"""
Database operations test suite
Tests database models, CRUD operations, and data integrity
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.models import User, UserRole, DifyApp, DifyAppType, DifyConfig
from app.auth import get_password_hash, verify_password, create_user, get_user


# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown database for each test"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provide database session for tests"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestUserModel:
    """Test User model and related operations"""

    def test_create_user_basic(self, db_session):
        """Test creating a basic user"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.created_at is not None

    def test_create_admin_user(self, db_session):
        """Test creating an admin user"""
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)

        assert admin.role == UserRole.ADMIN

    def test_user_unique_constraints(self, db_session):
        """Test that username and email are unique"""
        # Create first user
        user1 = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user1)
        db_session.commit()

        # Try to create user with same username
        user2 = User(
            username="testuser",
            email="different@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
        )
        db_session.add(user2)

        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "my_secret_password"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_create_user_function(self, db_session):
        """Test the create_user helper function"""
        user = create_user(
            db_session, "testuser", "test@example.com", "password123", UserRole.USER
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert verify_password("password123", user.hashed_password)

    def test_get_user_function(self, db_session):
        """Test the get_user helper function"""
        # Create a user first
        create_user(
            db_session, "testuser", "test@example.com", "password123", UserRole.USER
        )

        # Test getting existing user
        user = get_user(db_session, "testuser")
        assert user is not None
        assert user.username == "testuser"

        # Test getting non-existent user
        non_existent = get_user(db_session, "nonexistent")
        assert non_existent is None


class TestDifyAppModel:
    """Test DifyApp model and operations"""

    def test_create_dify_app(self, db_session):
        """Test creating a Dify app"""
        app = DifyApp(
            name="Test Chatbot",
            app_type=DifyAppType.CHATBOT,
            api_key="test-api-key",
            api_url="https://api.dify.ai/v1",
            description="Test application",
            is_active=True,
        )
        db_session.add(app)
        db_session.commit()
        db_session.refresh(app)

        assert app.id is not None
        assert app.name == "Test Chatbot"
        assert app.app_type == DifyAppType.CHATBOT
        assert app.api_key == "test-api-key"
        assert app.is_active is True
        assert app.created_at is not None

    def test_all_app_types(self, db_session):
        """Test creating apps with different types"""
        app_types = [
            DifyAppType.WORKFLOW,
            DifyAppType.CHATFLOW,
            DifyAppType.CHATBOT,
            DifyAppType.AGENT,
            DifyAppType.TEXT_GENERATOR,
        ]

        for i, app_type in enumerate(app_types):
            app = DifyApp(
                name=f"Test {app_type.value}",
                app_type=app_type,
                api_key=f"api-key-{i}",
                api_url="https://api.dify.ai/v1",
                is_active=True,
            )
            db_session.add(app)

        db_session.commit()

        # Verify all apps were created
        apps = db_session.query(DifyApp).all()
        assert len(apps) == len(app_types)

    def test_dify_app_filtering(self, db_session):
        """Test filtering active/inactive Dify apps"""
        # Create active app
        active_app = DifyApp(
            name="Active App",
            app_type=DifyAppType.CHATBOT,
            api_key="active-key",
            api_url="https://api.dify.ai/v1",
            is_active=True,
        )
        # Create inactive app
        inactive_app = DifyApp(
            name="Inactive App",
            app_type=DifyAppType.WORKFLOW,
            api_key="inactive-key",
            api_url="https://api.dify.ai/v1",
            is_active=False,
        )

        db_session.add_all([active_app, inactive_app])
        db_session.commit()

        # Test filtering active apps
        active_apps = (
            db_session.query(DifyApp).filter(DifyApp.is_active.is_(True)).all()
        )
        assert len(active_apps) == 1
        assert active_apps[0].name == "Active App"

        # Test filtering inactive apps
        inactive_apps = (
            db_session.query(DifyApp).filter(DifyApp.is_active.is_(False)).all()
        )
        assert len(inactive_apps) == 1
        assert inactive_apps[0].name == "Inactive App"

    def test_dify_app_update(self, db_session):
        """Test updating Dify app properties"""
        app = DifyApp(
            name="Original Name",
            app_type=DifyAppType.CHATBOT,
            api_key="original-key",
            api_url="https://api.dify.ai/v1",
            description="Original description",
            is_active=True,
        )
        db_session.add(app)
        db_session.commit()
        db_session.refresh(app)

        # Update app properties
        app.name = "Updated Name"
        app.description = "Updated description"
        app.api_key = "updated-key"
        db_session.commit()

        # Verify updates
        updated_app = db_session.query(DifyApp).filter(DifyApp.id == app.id).first()
        assert updated_app.name == "Updated Name"
        assert updated_app.description == "Updated description"
        assert updated_app.api_key == "updated-key"


class TestDifyConfigModel:
    """Test DifyConfig model and operations"""

    def test_create_dify_config(self, db_session):
        """Test creating Dify configuration"""
        config = DifyConfig(
            api_url="https://api.dify.ai/v1", api_key="test-api-key-123"
        )
        db_session.add(config)
        db_session.commit()
        db_session.refresh(config)

        assert config.id is not None
        assert config.api_url == "https://api.dify.ai/v1"
        assert config.api_key == "test-api-key-123"

    def test_update_dify_config(self, db_session):
        """Test updating Dify configuration"""
        # Create initial config
        config = DifyConfig(api_url="https://api.dify.ai/v1", api_key="original-key")
        db_session.add(config)
        db_session.commit()

        # Update config
        config.api_url = "https://new-api.dify.ai/v1"
        config.api_key = "new-key"
        db_session.commit()

        # Verify update
        updated_config = db_session.query(DifyConfig).first()
        assert updated_config.api_url == "https://new-api.dify.ai/v1"
        assert updated_config.api_key == "new-key"

    def test_single_config_constraint(self, db_session):
        """Test that only one config should exist (business logic)"""
        # Create first config
        config1 = DifyConfig(api_url="https://api1.dify.ai/v1", api_key="key1")
        db_session.add(config1)
        db_session.commit()

        # In practice, the API should update existing config
        # rather than create multiple configs
        configs = db_session.query(DifyConfig).all()
        assert len(configs) == 1


class TestRelationshipsAndIntegrity:
    """Test relationships between models and data integrity"""

    def test_user_role_enum(self, db_session):
        """Test UserRole enum values"""
        # Test creating users with different roles
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.USER,
        )
        admin = User(
            username="testadmin",
            email="admin@example.com",
            hashed_password=get_password_hash("password"),
            role=UserRole.ADMIN,
        )

        db_session.add_all([user, admin])
        db_session.commit()

        # Verify roles
        assert user.role == UserRole.USER
        assert admin.role == UserRole.ADMIN
        assert user.role != admin.role

    def test_app_type_enum(self, db_session):
        """Test DifyAppType enum values"""
        app_types = [
            DifyAppType.WORKFLOW,
            DifyAppType.CHATFLOW,
            DifyAppType.CHATBOT,
            DifyAppType.AGENT,
            DifyAppType.TEXT_GENERATOR,
        ]

        for app_type in app_types:
            app = DifyApp(
                name=f"Test {app_type.value}",
                app_type=app_type,
                api_key="test-key",
                api_url="https://api.dify.ai/v1",
            )
            db_session.add(app)

        db_session.commit()

        # Verify all types were stored correctly
        apps = db_session.query(DifyApp).all()
        stored_types = [app.app_type for app in apps]
        assert set(stored_types) == set(app_types)

    def test_database_constraints(self, db_session):
        """Test database constraints and validations"""
        # Test required fields
        with pytest.raises(Exception):
            # Missing required username
            user = User(
                email="test@example.com",
                hashed_password="hash",
                role=UserRole.USER,
            )
            db_session.add(user)
            db_session.commit()

        db_session.rollback()

        # Test valid creation
        user = User(
            username="validuser",
            email="valid@example.com",
            hashed_password="hash",
            role=UserRole.USER,
        )
        db_session.add(user)
        db_session.commit()  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__])
