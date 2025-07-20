from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import DifyConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
import os

# Override environment variables for testing
os.environ["DB_HOST"] = "test"
os.environ["DB_NAME"] = "test_db"
os.environ["APP_DEBUG"] = "true"

# Setup a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


def test_set_dify_config(db_session):
    response = client.post(
        "/api/v1/dify-config",
        json={"api_url": "http://test-dify.com/v1", "api_key": "test-api-key"},
    )
    assert response.status_code == 200
    expected_message = "Dify configuration saved successfully"
    assert response.json() == {"message": expected_message}

    # Verify it was actually saved in the database
    config = db_session.query(DifyConfig).first()
    assert config is not None
    assert config.api_url == "http://test-dify.com/v1"
    assert config.api_key == "test-api-key"


def test_get_dify_config(db_session):
    # First, create a config
    config = DifyConfig(api_url="http://test-dify.com/v1", api_key="test-api-key")
    db_session.add(config)
    db_session.commit()

    response = client.get("/api/v1/dify-config")
    assert response.status_code == 200
    expected_response = {
        "api_url": "http://test-dify.com/v1",
        "api_key": "test-api-key",
    }
    assert response.json() == expected_response


def test_upload_document_no_config(mocker):
    # Mock the global variables to be None (no config)
    with mocker.patch("app.api.DIFY_API_URL", None):
        with mocker.patch("app.api.DIFY_API_KEY", None):
            response = client.post(
                "/api/v1/documents",
                files={"file": ("test.txt", b"test content", "text/plain")},
            )
            assert response.status_code == 400
            error_detail = (
                "Dify API configuration is missing. "
                "Please set it via /api/v1/dify-config."
            )
            assert response.json() == {"detail": error_detail}
