import json

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from jose import jws, jwt

from app.config.settings import Settings
from app.model.user import User
from app.repository import UserAlreadyExistsError, UserNotFoundError
from app.repository.postgres.user import UserRepository
from app.service import InvalidCredentialsError
from app.service.auth import AuthService, ACCESS_TOKEN_TYPE, OTP_TOKEN_TYPE
from app.service.otp import OTPSenderService


@pytest.fixture()
def otp_service(mocker):
    mock = mocker.Mock(spec=OTPSenderService)
    return mock


@pytest.fixture()
def auth_service(mocker, otp_service):
    mocker.patch("app.repository.postgres.user.UserRepository.__init__", return_value=None)
    return AuthService(UserRepository(None), Settings(), otp_service)


@pytest.mark.asyncio
async def test_register_user_success(mocker, create_user_request, auth_service):
    mocker.patch("app.hash.pwd_context.hash", return_value="wonderful_hash")
    insert_user_mock = mocker.patch(
        "app.repository.postgres.user.UserRepository.insert_user", return_value="1"
    )

    _input = create_user_request

    id = await auth_service.register_user(**_input)
    assert id == "1"
    insert_user_mock.assert_called_once_with(
        email="john.doe@email.com",
        password="wonderful_hash",
        first_name="John",
        last_name="Doe",
        two_factor_enabled=False,
    )


@pytest.mark.asyncio
async def test_register_user_already_exists(mocker, create_user_request, auth_service):
    mocker.patch("app.hash.pwd_context.hash", return_value="wonderful_hash")
    mocker.patch(
        "app.repository.postgres.user.UserRepository.insert_user",
        side_effect=UserAlreadyExistsError("User already exists"),
    )

    _input = create_user_request

    with pytest.raises(UserAlreadyExistsError):
        await auth_service.register_user(**_input)


@pytest.mark.asyncio
async def test_authenticate_user_success(mocker, auth_service):
    mocker.patch(
        "app.repository.postgres.user.UserRepository.get_user_by_email",
        return_value=User(
            id="1",
            email="john.doe@email.com",
            password="wonderful_hash",
            first_name="John",
            last_name="Doe",
            two_factor_enabled=False,
        ),
    )
    mocker.patch("app.hash.pwd_context.verify", return_value=True)

    _input = {"email": "john.doe@email.com", "password": "password"}

    token = await auth_service.authenticate_user(**_input)
    assert token is not None
    payload = json.loads(jws.get_unverified_claims(token))
    assert payload["sub"] == "1"
    assert payload["type"] == ACCESS_TOKEN_TYPE


@pytest.mark.asyncio
async def test_authenticate_user_wrong_pass(mocker, auth_service):
    mocker.patch(
        "app.repository.postgres.user.UserRepository.get_user_by_email",
        return_value=User(
            id="1",
            email="john.doe@email.com",
            password="wonderful_hash",
            first_name="John",
            last_name="Doe",
            two_factor_enabled=False,
        ),
    )
    mocker.patch("app.hash.pwd_context.verify", return_value=False)

    _input = {
        "email": "john.doe@email.com",
        "password": "verywrongpass",
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(**_input)


@pytest.mark.asyncio
async def test_authenticate_user_not_found(mocker, auth_service):
    mocker.patch(
        "app.repository.postgres.user.UserRepository.get_user_by_email",
        return_value=None,
    )
    mocker.patch("app.hash.pwd_context.verify", return_value=False)

    _input = {
        "email": "mark.doe@email.com",
        "password": "wonderful_hash",
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.authenticate_user(**_input)


@pytest.mark.asyncio
async def test_authenticate_user_with_2fa_success(mocker, auth_service, otp_service):
    mocker.patch(
        "app.repository.postgres.user.UserRepository.get_user_by_email",
        return_value=User(
            id="1",
            email="john.doe@email.com",
            password="wonderful_hash",
            first_name="John",
            last_name="Doe",
            two_factor_enabled=True,
        ),
    )
    mocker.patch("app.hash.pwd_context.verify", return_value=True)
    mocker.patch("app.service.auth.AuthService.generate_otp", return_value="001100")
    mocker.patch("app.hash.otp_context.hash", return_value="123456")

    _input = {
        "email": "john.doe@email.com",
        "password": "wonderful_hash",
    }

    token = await auth_service.authenticate_user(**_input)
    assert token is not None
    payload = json.loads(jws.get_unverified_claims(token))
    assert payload["sub"] == "1"
    assert payload["type"] == OTP_TOKEN_TYPE
    assert payload["otp"] == "123456"
    otp_service.send_otp.assert_called_once_with("john.doe@email.com", "001100")


@pytest.mark.asyncio
async def test_verify_otp(mocker, auth_service):
    mocker.patch("app.hash.otp_context.verify", return_value=True)
    mocker.patch(
        "jose.jwt.decode",
        return_value={"sub": "1", "type": OTP_TOKEN_TYPE, "otp": "wonderful_hash"},
    )

    _input = {
        "credentials": HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token"),
        "otp": "123456",
    }

    token = await auth_service.verify_otp(**_input)
    assert token is not None
    payload = json.loads(jws.get_unverified_claims(token))
    assert payload["sub"] == "1"
    assert payload["type"] == ACCESS_TOKEN_TYPE


@pytest.mark.asyncio
async def test_verify_otp_invalid(mocker, auth_service):
    mocker.patch("app.hash.otp_context.verify", return_value=False)
    mocker.patch(
        "jose.jwt.decode",
        return_value={"sub": "1", "type": OTP_TOKEN_TYPE, "otp": "wonderful_hash"},
    )

    _input = {
        "credentials": HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token"),
        "otp": "wrong_otp",
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_otp(**_input)

    mocker.patch(
        "jose.jwt.decode",
        return_value={"sub": "1", "type": ACCESS_TOKEN_TYPE, "otp": "wonderful_hash"},
    )

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_otp(**_input)

    mocker.patch(
        "jose.jwt.decode",
        return_value={"sub": "1", "type": OTP_TOKEN_TYPE, "otp": "wonderful_hash"},
    )
    mocker.patch("app.hash.otp_context.verify", return_value=True)
    _input = {
        "credentials": HTTPAuthorizationCredentials(
            scheme="WrongScheme", credentials="valid_token"
        ),
        "otp": "wrong_otp",
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_otp(**_input)

    mocker.patch("jose.jwt.decode", side_effect=jwt.JWTError)

    _input = {
        "credentials": HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token"),
        "otp": "wrong_otp",
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_otp(**_input)


@pytest.mark.asyncio
async def test_verify_jwt_token_success(mocker, auth_service):
    _expected_user = User(
        id="1",
        email="john.doe@email.com",
        password="wonderful_hash",
        first_name="John",
        last_name="Doe",
        two_factor_enabled=True,
    )
    get_user_by_id_mock = mocker.patch(
        "app.repository.postgres.user.UserRepository.get_user_by_id",
        return_value=_expected_user,
    )
    mocker.patch("jose.jwt.decode", return_value={"sub": "1", "type": ACCESS_TOKEN_TYPE})

    _input = {
        "credentials": HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token"),
    }

    user = await auth_service.verify_jwt_token(**_input)
    get_user_by_id_mock.assert_called_once_with("1")
    assert user == _expected_user


@pytest.mark.asyncio
async def test_verify_jwt_token_invalid(mocker, auth_service):
    _expected_user = User(
        id="1",
        email="john.doe@email.com",
        password="wonderful_hash",
        first_name="John",
        last_name="Doe",
        two_factor_enabled=True,
    )
    mocker.patch("jose.jwt.decode", return_value={"sub": "1", "type": OTP_TOKEN_TYPE})

    _input = {
        "credentials": HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token"),
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_jwt_token(**_input)

    _ = mocker.patch(
        "app.repository.postgres.user.UserRepository.get_user_by_id",
        side_effect=InvalidCredentialsError,
    )
    mocker.patch("jose.jwt.decode", return_value={"sub": "1", "type": ACCESS_TOKEN_TYPE})

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_jwt_token(**_input)

    _input = {
        "credentials": HTTPAuthorizationCredentials(
            scheme="WrongScheme", credentials="invalid_token"
        ),
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_jwt_token(**_input)

    mocker.patch("jose.jwt.decode", side_effect=jwt.JWTError)
    _input = {
        "credentials": HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token"),
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_jwt_token(**_input)

    mocker.patch("jose.jwt.decode", return_value={"sub": "1", "type": ACCESS_TOKEN_TYPE})
    mocker.patch(
        "app.repository.postgres.user.UserRepository.get_user_by_id", side_effect=UserNotFoundError
    )
    _input = {
        "credentials": HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid_token"),
    }

    with pytest.raises(InvalidCredentialsError):
        await auth_service.verify_jwt_token(**_input)


def test_generate_otp(auth_service):
    otp = auth_service.generate_otp()
    assert otp is not None
    assert len(otp) == 6
    assert otp.isdigit()
