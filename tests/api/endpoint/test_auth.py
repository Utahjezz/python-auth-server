import json
from typing import List

from app.model.user import User
from app.repository.postgres.user import get_user_repository


class MockUserRepository:
    def __init__(self, initial_state: List[User] = None):
        self.data = initial_state or []

    async def insert_user(
        self, email: str, password: str, first_name: str, last_name: str, two_factor_enabled: bool
    ):
        return "1234"


def test_register(fastapi_app, fastapi_test_client, create_user_request):
    fastapi_app.dependency_overrides[get_user_repository] = MockUserRepository
    response = fastapi_test_client.post(
        "/api/v1/register",
        data=json.dumps(create_user_request),
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 201
    assert response.json() == {"id": "1234"}
