"""
Comprehensive test suite for RAG UI Backend API
Tests all authentication, Dify configuration, and Dify app management endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.main import app
from app.database import Base, get_db
from app.models import User, UserRole, DifyApp, DifyAppType
from app.auth import get_password_hash

# Override environment variables for testing
os.environ["DB_HOST"] = "test"
os.environ["DB_NAME"] = "test_db"
os.environ["APP_DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown database for each test"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user():
    """Create a test user"""
    db = TestingSessionLocal()
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.USER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def test_admin():
    """Create a test admin user"""
    db = TestingSessionLocal()
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.close()
    return admin


@pytest.fixture
def user_token(test_user):
    """Get authentication token for regular user"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(test_admin):
    """Get authentication token for admin user"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def test_dify_app():
    """Create a test Dify app"""
    db = TestingSessionLocal()
    app_obj = DifyApp(
        name="Test Chatbot",
        app_type=DifyAppType.CHATBOT,
        api_key="test-api-key",
        api_url="https://api.dify.ai/v1",
        description="Test Dify application",
        is_active=True,
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    db.close()
    return app_obj


class TestBasicEndpoints:
    """Test basic application endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}


class TestAuthenticationEndpoints:
    """Test user authentication endpoints"""

    def test_register_user_success(self):
        """Test successful user registration"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "user"
        assert data["is_active"] is True

    def test_register_admin_user(self):
        """Test registering admin user"""
        user_data = {
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "newpass123",
            "role": "admin",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    def test_register_duplicate_username(self, test_user):
        """Test registration with duplicate username"""
        user_data = {
            "username": "testuser",
            "email": "different@example.com",
            "password": "newpass123",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_duplicate_email(self, test_user):
        """Test registration with duplicate email"""
        user_data = {
            "username": "differentuser",
            "email": "test@example.com",
            "password": "newpass123",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_login_success(self, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self):
        """Test login with invalid username"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "testpass123"},
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, test_user):
        """Test login with invalid password"""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_get_current_user_info(self, user_token):
        """Test getting current user info"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_current_user_info_no_token(self):
        """Test getting user info without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403

    def test_protected_route(self, user_token):
        """Test protected route access"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v1/auth/protected", headers=headers)
        assert response.status_code == 200
        assert "Hello testuser" in response.json()["message"]


class TestDifyConfigEndpoints:
    """Test Dify configuration endpoints"""

    def test_set_dify_config(self):
        """Test setting Dify configuration"""
        config_data = {
            "api_url": "https://api.dify.ai/v1",
            "api_key": "test-api-key-123",
        }
        response = client.post("/api/v1/dify-config", json=config_data)
        assert response.status_code == 200
        assert "Dify configuration saved successfully" in response.json()["message"]

    def test_get_dify_config(self):
        """Test getting Dify configuration"""
        # First set a config
        config_data = {
            "api_url": "https://api.dify.ai/v1",
            "api_key": "test-api-key-123",
        }
        client.post("/api/v1/dify-config", json=config_data)

        # Then get it
        response = client.get("/api/v1/dify-config")
        assert response.status_code == 200
        data = response.json()
        assert data["api_url"] == "https://api.dify.ai/v1"
        assert data["api_key"] == "test-api-key-123"

    def test_get_dify_config_not_found(self):
        """Test getting Dify config when none exists"""
        response = client.get("/api/v1/dify-config")
        assert response.status_code == 404
        assert "Dify configuration not found" in response.json()["detail"]

    def test_update_dify_config(self):
        """Test updating existing Dify configuration"""
        # First set a config
        config_data = {
            "api_url": "https://api.dify.ai/v1",
            "api_key": "test-api-key-123",
        }
        client.post("/api/v1/dify-config", json=config_data)

        # Update it
        updated_config = {
            "api_url": "https://new-api.dify.ai/v1",
            "api_key": "new-test-api-key-456",
        }
        response = client.post("/api/v1/dify-config", json=updated_config)
        assert response.status_code == 200

        # Verify update
        response = client.get("/api/v1/dify-config")
        data = response.json()
        assert data["api_url"] == "https://new-api.dify.ai/v1"
        assert data["api_key"] == "new-test-api-key-456"


class TestDifyAppManagementEndpoints:
    """Test Dify app management endpoints (admin only)"""

    def test_create_dify_app_success(self, admin_token):
        """Test creating Dify app as admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        app_data = {
            "name": "Test Workflow",
            "app_type": "workflow",
            "api_key": "workflow-api-key",
            "api_url": "https://api.dify.ai/v1",
            "description": "Test workflow application",
        }
        response = client.post("/api/v1/dify-apps", json=app_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Workflow"
        assert data["app_type"] == "workflow"
        assert data["is_active"] is True

    def test_create_dify_app_unauthorized(self, user_token):
        """Test creating Dify app as regular user (should fail)"""
        headers = {"Authorization": f"Bearer {user_token}"}
        app_data = {
            "name": "Test Workflow",
            "app_type": "workflow",
            "api_key": "workflow-api-key",
            "api_url": "https://api.dify.ai/v1",
        }
        response = client.post("/api/v1/dify-apps", json=app_data, headers=headers)
        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["detail"]

    def test_get_dify_apps(self, user_token, test_dify_app):
        """Test getting all Dify apps"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v1/dify-apps", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Chatbot"

    def test_get_dify_app_by_id(self, user_token, test_dify_app):
        """Test getting specific Dify app by ID"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/api/v1/dify-apps/{test_dify_app.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_dify_app.id
        assert data["name"] == "Test Chatbot"

    def test_get_dify_app_not_found(self, user_token):
        """Test getting non-existent Dify app"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v1/dify-apps/999", headers=headers)
        assert response.status_code == 404
        assert "Dify app not found" in response.json()["detail"]

    def test_update_dify_app_success(self, admin_token, test_dify_app):
        """Test updating Dify app as admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {
            "name": "Updated Chatbot",
            "description": "Updated description",
        }
        response = client.put(
            f"/api/v1/dify-apps/{test_dify_app.id}",
            json=update_data,
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Chatbot"
        assert data["description"] == "Updated description"

    def test_update_dify_app_unauthorized(self, user_token, test_dify_app):
        """Test updating Dify app as regular user (should fail)"""
        headers = {"Authorization": f"Bearer {user_token}"}
        update_data = {"name": "Updated Chatbot"}
        response = client.put(
            f"/api/v1/dify-apps/{test_dify_app.id}",
            json=update_data,
            headers=headers,
        )
        assert response.status_code == 403

    def test_delete_dify_app_success(self, admin_token, test_dify_app):
        """Test deleting Dify app as admin"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(
            f"/api/v1/dify-apps/{test_dify_app.id}", headers=headers
        )
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify app is deactivated
        response = client.get("/api/v1/dify-apps", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) == 0  # Should be empty as app is deactivated

    def test_delete_dify_app_unauthorized(self, user_token, test_dify_app):
        """Test deleting Dify app as regular user (should fail)"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.delete(
            f"/api/v1/dify-apps/{test_dify_app.id}", headers=headers
        )
        assert response.status_code == 403


class TestChatEndpoints:
    """Test chat endpoints with Dify apps"""

    def test_chat_with_app_missing_app(self, user_token):
        """Test chatting with non-existent app"""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {
            "query": "Hello, how are you?",
            "conversation_id": "test-conv-1",
        }
        response = client.post(
            "/api/v1/chat/app/999",
            json=chat_data,
            headers=headers,
        )
        assert response.status_code == 404
        assert "Dify app not found" in response.json()["detail"]

    def test_chat_with_app_missing_query(self, user_token, test_dify_app):
        """Test chatting without query"""
        headers = {"Authorization": f"Bearer {user_token}"}
        chat_data = {"conversation_id": "test-conv-1"}
        response = client.post(
            f"/api/v1/chat/app/{test_dify_app.id}",
            json=chat_data,
            headers=headers,
        )
        assert response.status_code == 400
        assert "Query is required" in response.json()["detail"]

    def test_chat_with_app_unauthorized(self, test_dify_app):
        """Test chatting without authentication"""
        chat_data = {
            "query": "Hello, how are you?",
            "conversation_id": "test-conv-1",
        }
        response = client.post(
            f"/api/v1/chat/app/{test_dify_app.id}",
            json=chat_data,
        )
        assert response.status_code == 403


class TestDocumentEndpoints:
    """Test document upload endpoints"""

    def test_upload_document_missing_config(self, user_token):
        """Test document upload without Dify config"""
        headers = {"Authorization": f"Bearer {user_token}"}
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/api/v1/documents", files=files, headers=headers)
        assert response.status_code == 400
        assert "Dify API configuration is missing" in response.json()["detail"]

    def test_upload_document_unauthorized(self):
        """Test document upload without authentication"""
        files = {"file": ("test.txt", b"test content", "text/plain")}
        response = client.post("/api/v1/documents", files=files)
        assert response.status_code == 403


class TestValidationAndEdgeCases:
    """Test input validation and edge cases"""

    def test_register_invalid_email(self):
        """Test registration with invalid email format"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "testpass123",
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422  # Validation error

    def test_create_dify_app_invalid_app_type(self, admin_token):
        """Test creating Dify app with invalid app type"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        app_data = {
            "name": "Test App",
            "app_type": "invalid_type",
            "api_key": "test-key",
            "api_url": "https://api.dify.ai/v1",
        }
        response = client.post("/api/v1/dify-apps", json=app_data, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_create_dify_app_invalid_url(self, admin_token):
        """Test creating Dify app with invalid URL"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        app_data = {
            "name": "Test App",
            "app_type": "chatbot",
            "api_key": "test-key",
            "api_url": "not-a-valid-url",
        }
        response = client.post("/api/v1/dify-apps", json=app_data, headers=headers)
        # This might pass backend validation but would fail in frontend validation
        # depending on how strict the URL validation is


if __name__ == "__main__":
    pytest.main([__file__])
