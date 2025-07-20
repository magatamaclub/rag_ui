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
    try:
        db = TestingSessionLocal()
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
    assert response.json() == {"message": "Dify configuration saved successfully"}

    config = db_session.query(DifyConfig).first()
    assert config.api_url == "http://test-dify.com/v1"
    assert config.api_key == "test-api-key"


def test_get_dify_config(db_session):
    client.post(
        "/api/v1/dify-config",
        json={"api_url": "http://test-dify.com/v1", "api_key": "test-api-key"},
    )
    response = client.get("/api/v1/dify-config")
    assert response.status_code == 200
    assert response.json() == {
        "api_url": "http://test-dify.com/v1",
        "api_key": "test-api-key",
    }


def test_upload_document_no_config(mocker):
    # Ensure DIFY_API_URL and DIFY_API_KEY are None for this test
    mocker.patch("app.api.DIFY_API_URL", None)
    mocker.patch("app.api.DIFY_API_KEY", None)

    response = client.post(
        "/api/v1/documents", files={"file": ("test.txt", b"hello world", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Dify API configuration is missing. Please set it via /api/v1/dify-config."
    }


def test_upload_document(mocker, db_session):
    # Set Dify config in DB for this test
    client.post(
        "/api/v1/dify-config",
        json={"api_url": "http://test-dify.com/v1", "api_key": "test-api-key"},
    )
    # Mock the requests.post call for document upload
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "id": "dify-file-id",
        "name": "test.txt",
        "size": 11,
        "type": "text/plain",
        "created_by": "gemini-user",
        "created_at": "2025-07-15T12:00:00Z",
    }

    response = client.post(
        "/api/v1/documents", files={"file": ("test.txt", b"hello world", "text/plain")}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "test.txt"
    assert response.json()["id"] == "dify-file-id"

    # Assert that requests.post was called with the correct arguments
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "http://test-dify.com/v1/files/upload"
    assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"


def test_chat_streaming_no_config(mocker):
    # Ensure DIFY_API_URL and DIFY_API_KEY are None for this test
    mocker.patch("app.api.DIFY_API_URL", None)
    mocker.patch("app.api.DIFY_API_KEY", None)

    response = client.post(
        "/api/v1/chat",
        json={"query": "Hello Dify", "conversation_id": "test-conversation-id"},
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Dify API configuration is missing. Please set it via /api/v1/dify-config."
    }


def test_chat_streaming(mocker, db_session):
    # Set Dify config in DB for this test
    client.post(
        "/api/v1/dify-config",
        json={"api_url": "http://test-dify.com/v1", "api_key": "test-api-key"},
    )
    # Mock the requests.post call for chat streaming
    mock_response_iter = mocker.MagicMock()
    mock_response_iter.iter_content.return_value = [
        b'data: {"event": "llm_start", "id": "123"}\n\n',
        b'data: {"event": "text_chunk", "answer": "Hello"}\n\n',
        b'data: {"event": "text_chunk", "answer": " world"}\n\n',
        b'data: {"event": "llm_end", "id": "123"}\n\n',
    ]
    mock_response_iter.status_code = 200
    mock_response_iter.__enter__.return_value = mock_response_iter
    mock_response_iter.__exit__.return_value = None

    mock_requests_post = mocker.patch("requests.post", return_value=mock_response_iter)

    response = client.post(
        "/api/v1/chat",
        json={"query": "Hello Dify", "conversation_id": "test-conversation-id"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Read the streaming response and verify content
    received_chunks = []
    for chunk in response.iter_lines():
        received_chunks.append(chunk)

    expected_chunks = [
        'data: {"event": "llm_start", "id": "123"}',
        'data: {"event": "text_chunk", "answer": "Hello"}',
        'data: {"event": "text_chunk", "answer": " world"}',
        'data: {"event": "llm_end", "id": "123"}',
    ]
    # Filter out empty strings that iter_lines() might produce from double newlines
    received_chunks = [chunk for chunk in received_chunks if chunk]
    assert received_chunks == expected_chunks

    # Verify the Dify API call
    args, kwargs = mock_requests_post.call_args
    assert args[0] == "http://test-dify.com/v1/chat-messages"
    assert kwargs["headers"]["Authorization"] == "Bearer test-api-key"
    assert kwargs["json"]["query"] == "Hello Dify"
    assert kwargs["json"]["response_mode"] == "streaming"
    assert kwargs["json"]["conversation_id"] == "test-conversation-id"
