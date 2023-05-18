import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def fastapi_app():
    return app


@pytest.fixture
def fastapi_test_client(fastapi_app):
    return TestClient(fastapi_app)


@pytest.fixture
def create_user_request():
    return {
        "email": "john.doe@email.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
        "two_factor_enabled": False,
    }
