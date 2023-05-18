from pydantic import BaseModel, Field, EmailStr, SecretStr


class RegisterUserRequest(BaseModel):
    email: str = Field(..., description="Email of the user", example="joe.doe@email.com")
    password: SecretStr = Field(
        ..., description="Password of the user", example="supersecret@#password"
    )
    first_name: str = Field(..., description="First name of the user", example="Joe")
    last_name: str = Field(..., description="Last name of the user", example="Doe")
    two_factor_enabled: bool = Field(
        False, description="Two factor authentication enabled", example=True
    )


class RegisterUserResponse(BaseModel):
    id: str = Field(..., description="Id of the user", example="1234567890")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email of the user", example="joe.doe@email.com")
    password: SecretStr = Field(
        ..., description="Password of the user", example="supersecret@#password"
    )


class LoginResponse(BaseModel):
    access_token: str = Field(..., description="Access token of the user")


class OtpRequest(BaseModel):
    otp: str = Field(..., description="OTP of the user", example="123456")
