"""
Performance and load testing for RAG UI Backend
Tests API performance, concurrent requests, and stress testing
"""

import pytest
import time
import concurrent.futures
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, UserRole, DifyApp, DifyAppType
from app.auth import get_password_hash


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
def test_data():
    """Create test data for performance tests"""
    db = TestingSessionLocal()

    # Create admin user
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
    )

    # Create regular user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.USER,
        is_active=True,
    )

    # Create test Dify app
    app_obj = DifyApp(
        name="Performance Test App",
        app_type=DifyAppType.CHATBOT,
        api_key="perf-test-key",
        api_url="https://api.dify.ai/v1",
        description="App for performance testing",
        is_active=True,
    )

    db.add_all([admin, user, app_obj])
    db.commit()

    db.close()
    return {
        "admin": {"username": "admin", "password": "admin123"},
        "user": {"username": "testuser", "password": "testpass123"},
    }


class TestPerformanceBasics:
    """Basic performance tests for API endpoints"""

    def test_login_performance(self, test_data):
        """Test login endpoint performance"""
        login_data = test_data["user"]

        start_time = time.time()
        response = client.post("/api/v1/auth/login", json=login_data)
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Should complete within 1 second

    def test_user_registration_performance(self):
        """Test user registration performance"""
        user_data = {
            "username": "perfuser",
            "email": "perf@example.com",
            "password": "perfpass123",
        }

        start_time = time.time()
        response = client.post("/api/v1/auth/register", json=user_data)
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0  # Registration might take longer due to hashing

    def test_get_dify_apps_performance(self, test_data):
        """Test Dify apps retrieval performance"""
        # Login first
        login_response = client.post("/api/v1/auth/login", json=test_data["user"])
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        start_time = time.time()
        response = client.get("/api/v1/dify-apps", headers=headers)
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 0.5  # Should be very fast for simple queries


class TestConcurrentRequests:
    """Test concurrent request handling"""

    def test_concurrent_logins(self, test_data):
        """Test handling multiple concurrent login requests"""
        login_data = test_data["user"]
        num_requests = 10

        def make_login_request():
            return client.post("/api/v1/auth/login", json=login_data)

        start_time = time.time()

        # Use ThreadPoolExecutor for concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_login_request) for _ in range(num_requests)]
            responses = [future.result() for future in futures]

        end_time = time.time()

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            assert "access_token" in response.json()

        # Total time should be reasonable (less than sequential execution)
        total_time = end_time - start_time
        assert total_time < num_requests * 0.5  # Should be faster than sequential

    def test_concurrent_app_retrieval(self, test_data):
        """Test concurrent Dify app retrieval"""
        # Login first
        login_response = client.post("/api/v1/auth/login", json=test_data["user"])
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        num_requests = 15

        def make_apps_request():
            return client.get("/api/v1/dify-apps", headers=headers)

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_apps_request) for _ in range(num_requests)]
            responses = [future.result() for future in futures]

        end_time = time.time()

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            assert isinstance(response.json(), list)

        total_time = end_time - start_time
        assert total_time < 5.0  # Should complete within reasonable time

    def test_mixed_concurrent_requests(self, test_data):
        """Test mixed types of concurrent requests"""
        # Login first to get token
        login_response = client.post("/api/v1/auth/login", json=test_data["admin"])
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        def make_login_request():
            return client.post("/api/v1/auth/login", json=test_data["user"])

        def make_apps_request():
            return client.get("/api/v1/dify-apps", headers=headers)

        def make_user_info_request():
            return client.get("/api/v1/auth/me", headers=headers)

        # Mix different types of requests
        tasks = []
        tasks.extend([make_login_request for _ in range(5)])
        tasks.extend([make_apps_request for _ in range(5)])
        tasks.extend([make_user_info_request for _ in range(5)])

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(task) for task in tasks]
            responses = [future.result() for future in futures]

        end_time = time.time()

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

        total_time = end_time - start_time
        assert total_time < 10.0


class TestStressTests:
    """Stress testing with higher loads"""

    def test_high_volume_user_creation(self):
        """Test creating many users rapidly"""
        num_users = 50

        def create_user(index):
            user_data = {
                "username": f"stressuser{index}",
                "email": f"stress{index}@example.com",
                "password": "stresspass123",
            }
            return client.post("/api/v1/auth/register", json=user_data)

        start_time = time.time()

        # Create users with limited concurrency to avoid overwhelming SQLite
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(create_user, i) for i in range(num_users)]
            responses = [future.result() for future in futures]

        end_time = time.time()

        # Check that most requests succeeded
        successful = sum(1 for r in responses if r.status_code == 200)
        assert successful >= num_users * 0.8  # At least 80% should succeed

        total_time = end_time - start_time
        print(f"Created {successful}/{num_users} users in {total_time:.2f} seconds")

    def test_rapid_dify_app_creation(self, test_data):
        """Test creating many Dify apps rapidly (admin only)"""
        # Login as admin
        login_response = client.post("/api/v1/auth/login", json=test_data["admin"])
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        num_apps = 20

        def create_app(index):
            app_data = {
                "name": f"Stress Test App {index}",
                "app_type": "chatbot",
                "api_key": f"stress-key-{index}",
                "api_url": "https://api.dify.ai/v1",
                "description": f"Stress test application {index}",
            }
            return client.post("/api/v1/dify-apps", json=app_data, headers=headers)

        start_time = time.time()

        # Limited concurrency for SQLite
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(create_app, i) for i in range(num_apps)]
            responses = [future.result() for future in futures]

        end_time = time.time()

        # Check success rate
        successful = sum(1 for r in responses if r.status_code == 200)
        assert successful >= num_apps * 0.8

        total_time = end_time - start_time
        print(f"Created {successful}/{num_apps} apps in {total_time:.2f} seconds")


class TestMemoryAndResource:
    """Test memory usage and resource consumption"""

    def test_memory_usage_during_load(self, test_data):
        """Test memory usage during high load"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Login to get token
        login_response = client.post("/api/v1/auth/login", json=test_data["user"])
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Make many requests
        for i in range(100):
            response = client.get("/api/v1/dify-apps", headers=headers)
            assert response.status_code == 200

            # Check memory periodically
            if i % 25 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_increase = current_memory - initial_memory
                # Memory shouldn't increase too much (< 50MB increase)
                assert memory_increase < 50

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        print(f"Memory increase during test: {memory_increase:.2f} MB")

    def test_response_time_consistency(self, test_data):
        """Test that response times remain consistent under load"""
        login_response = client.post("/api/v1/auth/login", json=test_data["user"])
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response_times = []

        for _ in range(50):
            start_time = time.time()
            response = client.get("/api/v1/dify-apps", headers=headers)
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        # Response times should be consistent
        assert max_time < avg_time * 3  # Max shouldn't be more than 3x average
        assert avg_time < 0.1  # Average should be under 100ms

        print(
            f"Response time stats: avg={avg_time:.3f}s, "
            f"min={min_time:.3f}s, max={max_time:.3f}s"
        )


class TestErrorHandlingUnderLoad:
    """Test error handling under high load conditions"""

    def test_invalid_requests_under_load(self):
        """Test handling many invalid requests"""
        num_requests = 30

        def make_invalid_login():
            return client.post(
                "/api/v1/auth/login", json={"username": "invalid", "password": "wrong"}
            )

        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_invalid_login) for _ in range(num_requests)]
            responses = [future.result() for future in futures]

        end_time = time.time()

        # All should return 401 Unauthorized
        for response in responses:
            assert response.status_code == 401

        # Should handle errors quickly
        total_time = end_time - start_time
        assert total_time < 10.0

    def test_rate_limiting_behavior(self, test_data):
        """Test behavior under rapid successive requests"""
        login_data = test_data["user"]

        # Make rapid successive requests
        response_codes = []
        for _ in range(20):
            response = client.post("/api/v1/auth/login", json=login_data)
            response_codes.append(response.status_code)
            time.sleep(0.01)  # Small delay between requests

        # Most should succeed (no built-in rate limiting in test)
        successful = sum(1 for code in response_codes if code == 200)
        assert successful >= 15  # At least 75% should succeed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
