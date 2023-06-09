import logging
import math
import random
from datetime import timedelta, datetime
from typing import Optional, Dict

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.config.settings import Settings, get_settings
from app.hash import get_password_hash, verify_password, get_otp_hash, verify_otp
from app.model.user import User
from app.repository import UserNotFoundError
from app.repository.postgres.user import UserRepository, get_user_repository
from app.service import InvalidCredentialsError
from app.service.otp import OTPSenderService, LogOTPSenderService

OTP_TOKEN_TYPE = "otp_temp_token"
ACCESS_TOKEN_TYPE = "access_token"


class AuthService:
    def __init__(
        self, user_repository: UserRepository, app_settings: Settings, otp_service: OTPSenderService
    ):
        self.user_repository = user_repository
        self.app_settings = app_settings
        self.otp_service = otp_service

    async def register_user(
        self, email: str, password: str, first_name: str, last_name: str, two_factor_enabled: bool
    ) -> str:
        # hash the password before storing it
        hashed_pass = get_password_hash(password)
        return await self.user_repository.insert_user(
            email=email,
            password=hashed_pass,
            first_name=first_name,
            last_name=last_name,
            two_factor_enabled=two_factor_enabled,
        )

    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        # try to get the user from the database
        try:
            user = await self.user_repository.get_user_by_email(email=email)
            logging.debug(f"User found: {user}")
        except UserNotFoundError:
            raise InvalidCredentialsError("Invalid credentials")
        # verify the password against the stored hash
        if verify_password(password, user.password.get_secret_value()):
            logging.debug("Password verified")
            if not user.two_factor_enabled:
                logging.debug("2FA not enabled, returning access token")
                return self.generate_jwt_token(data={"sub": user.id, "type": ACCESS_TOKEN_TYPE})
            else:
                logging.debug("2FA enabled, sending OTP")
                random_otp = self.generate_otp()
                self.otp_service.send_otp(user.email, random_otp)
                # after generating the OTP, we return a temporary token that contains the OTP hash
                logging.debug("Returning temporary token")
                return self.generate_jwt_token(
                    data={"sub": user.id, "type": OTP_TOKEN_TYPE, "otp": get_otp_hash(random_otp)},
                    expires_delta=timedelta(
                        seconds=self.app_settings.jwt.otp_token_expiration_seconds
                    ),
                )
        else:
            raise InvalidCredentialsError("Invalid credentials")

    async def verify_otp(
        self, credentials: HTTPAuthorizationCredentials, otp: str
    ) -> Optional[str]:
        logging.debug("Verifying OTP")
        if credentials.scheme != "Bearer":
            raise InvalidCredentialsError("Invalid authentication scheme")

        jwt_token = credentials.credentials
        try:
            logging.debug("Decoding JWT token")
            payload = jwt.decode(
                jwt_token,
                self.app_settings.jwt.secret_key,
                algorithms=[self.app_settings.jwt.crypto_algorithm],
            )
            logging.debug(f"Valid signed JWT, payload: {payload}")
            if payload["type"] == OTP_TOKEN_TYPE and verify_otp(otp, payload["otp"]):
                logging.debug("OTP verified, returning access token")
                return self.generate_jwt_token(
                    data={"sub": payload["sub"], "type": ACCESS_TOKEN_TYPE}
                )
            else:
                raise InvalidCredentialsError("Invalid credentials")
        except jwt.JWTError:
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

    def decode_jwt_token(self, jwt_token: str) -> Dict:
        jwt_settings = self.app_settings.jwt
        decoded_jwt = jwt.decode(
            jwt_token, jwt_settings.secret_key, algorithms=[jwt_settings.crypto_algorithm]
        )
        return decoded_jwt

    async def verify_jwt_token(self, credentials: HTTPAuthorizationCredentials) -> User:
        if credentials.scheme != "Bearer":
            raise InvalidCredentialsError("Invalid authentication scheme")

        jwt_token = credentials.credentials
        try:
            payload = jwt.decode(
                jwt_token,
                self.app_settings.jwt.secret_key,
                algorithms=[self.app_settings.jwt.crypto_algorithm],
            )
            if payload["type"] == ACCESS_TOKEN_TYPE and payload:
                return await self.user_repository.get_user_by_id(payload["sub"])
            else:
                raise InvalidCredentialsError("Invalid credentials")
        except InvalidCredentialsError:
            raise
        except jwt.JWTError:
            raise InvalidCredentialsError("Invalid credentials")
        except UserNotFoundError:
            raise InvalidCredentialsError("Invalid credentials")

    def generate_otp(self) -> str:
        """
        Generates a random OTP using a random digits generator,
        could be replaced with a more secure one
        :return: the generated OTP
        """
        digits = self.app_settings.otp.digits
        OTP = ""

        for i in range(self.app_settings.otp.length):
            OTP += digits[math.floor(random.random() * 10)]

        return OTP


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    app_settings: Settings = Depends(get_settings),
    otp_service: OTPSenderService = Depends(LogOTPSenderService),
) -> AuthService:
    return AuthService(
        user_repository=user_repository, app_settings=app_settings, otp_service=otp_service
    )
