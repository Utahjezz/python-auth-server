import pytest

from app.config.settings import Settings
from app.repository import UserAlreadyExistsError
from app.repository.postgres.user import UserRepository
from app.service.auth import AuthService


@pytest.mark.asyncio
async def test_register_user_success(mocker):
    mocker.patch("app.hash.pwd_context.hash", return_value="wonderful_hash")
    mocker.patch("app.repository.postgres.user.UserRepository.__init__", return_value=None)
    insert_user_mock = mocker.patch(
        "app.repository.postgres.user.UserRepository.insert_user", return_value="1"
    )
    mocker.patch("app.config.settings.Settings.__init__", return_value=None)

    _input = {
        "email": "joe.doe@mail.com",
        "password": "password",
        "first_name": "Joe",
        "last_name": "Doe",
        "two_factor_enabled": False,
    }
    auth_service = AuthService(UserRepository(None), Settings())
    id = await auth_service.register_user(**_input)
    assert id == "1"
    insert_user_mock.assert_called_once_with(
        email="joe.doe@mail.com",
        password="wonderful_hash",
        first_name="Joe",
        last_name="Doe",
        two_factor_enabled=False,
    )


@pytest.mark.asyncio
async def test_register_user_already_exists(mocker):
    mocker.patch("app.hash.pwd_context.hash", return_value="wonderful_hash")
    mocker.patch("app.repository.postgres.user.UserRepository.__init__", return_value=None)
    mocker.patch(
        "app.repository.postgres.user.UserRepository.insert_user",
        side_effect=UserAlreadyExistsError("User already exists"),
    )
    mocker.patch("app.config.settings.Settings.__init__", return_value=None)

    _input = {
        "email": "joe.doe@mail.com",
        "password": "password",
        "first_name": "Joe",
        "last_name": "Doe",
        "two_factor_enabled": False,
    }
    auth_service = AuthService(UserRepository(None), Settings())

    with pytest.raises(UserAlreadyExistsError):
        await auth_service.register_user(**_input)
