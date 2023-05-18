from datetime import timedelta, datetime
from typing import Optional, Dict

from fastapi import Depends
from jose import jwt

from app.config.settings import Settings, get_settings
from app.hash import get_password_hash, verify_password
from app.repository.postgres.user import UserRepository, get_user_repository
from app.service import InvalidCredentialsError


class AuthService:
    def __init__(self, user_repository: UserRepository, app_settings: Settings):
        self.user_repository = user_repository
        self.app_settings = app_settings

    async def register_user(
        self, email: str, password: str, first_name: str, last_name: str, two_factor_enabled: bool
    ) -> str:
        hashed_pass = get_password_hash(password)
        return await self.user_repository.insert_user(
            email=email,
            password=hashed_pass,
            first_name=first_name,
            last_name=last_name,
            two_factor_enabled=two_factor_enabled,
        )

    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        user = await self.user_repository.get_user_by_email(email=email)
        if not user.two_factor_enabled:
            if user and verify_password(password, user.password.get_secret_value()):
                return self.generate_jwt_token(data={"sub": user.id})
            else:
                raise InvalidCredentialsError("Invalid credentials")
        else:
            raise InvalidCredentialsError("Invalid credentials")

    def generate_jwt_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        jwt_settings = self.app_settings.jwt
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=jwt_settings.expiration_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, jwt_settings.secret_key, algorithm=jwt_settings.crypto_algorithm
        )
        return encoded_jwt


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    app_settings: Settings = Depends(get_settings),
) -> AuthService:
    return AuthService(user_repository=user_repository, app_settings=app_settings)
