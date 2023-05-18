import pytest


@pytest.fixture
def create_user_request():
    return {
        "email": "john.doe@email.com",
        "password": "password",
        "first_name": "John",
        "last_name": "Doe",
        "two_factor_enabled": False,
    }
