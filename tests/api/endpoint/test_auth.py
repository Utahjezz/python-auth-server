import json
from typing import List

from app.model.user import User
from app.repository.postgres.user import get_user_repository


class MockUserRepository:
    def __init__(self, initial_state: List[User] = None):
        self.data = initial_state or [
            User(
                id="1234",
                email="joe.doe@email.com",
                password="supersecret@#password",
                first_name="Joe",
                last_name="Doe",
                two_factor_enabled=False,
            ),
        ]

    async def insert_user(
        self, email: str, password: str, first_name: str, last_name: str, two_factor_enabled: bool
    ):
        return "1234"

    async def get_user_by_email(self, email: str):
        return self.data[0]


def test_register(fastapi_app, fastapi_test_client, create_user_request):
    fastapi_app.dependency_overrides[get_user_repository] = MockUserRepository
    response = fastapi_test_client.post(
        "/api/v1/register",
        json=create_user_request,
    )
    assert response.status_code == 201
    assert response.json() == {"id": "1234"}


def test_simple_login(fastapi_app, fastapi_test_client):
    fastapi_app.dependency_overrides[get_user_repository] = MockUserRepository
    response = fastapi_test_client.post(
        "/api/v1/login",
        content=json.dumps(
            {
                "email": "joe.doe@email.com",
                "password": "supersecret@#password",
            }
        ),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
