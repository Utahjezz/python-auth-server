from fastapi import APIRouter, Depends, HTTPException

from app.repository import UserAlreadyExistsError
from app.schema.user import RegisterUserRequest, RegisterUserResponse, LoginResponse, LoginRequest
from app.service import InvalidCredentialsError
from app.service.auth import AuthService, get_auth_service

router = APIRouter()


@router.post("/register", status_code=201, response_model=RegisterUserResponse)
async def register(
    request: RegisterUserRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        user_id = await auth_service.register_user(
            email=request.email,
            password=request.password.get_secret_value(),
            first_name=request.first_name,
            last_name=request.last_name,
            two_factor_enabled=request.two_factor_enabled,
        )
        return RegisterUserResponse(id=user_id)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    # don't need to catch ValidationError because FastAPI does it for us
    # don't need to catch generic Exception because FastAPI does it for us


@router.post("/login", status_code=200, response_model=LoginResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    try:
        access_token = await auth_service.authenticate_user(
            email=request.email,
            password=request.password.get_secret_value(),
        )
        return LoginResponse(access_token=access_token)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # don't need to catch ValidationError because FastAPI does it for us
    # don't need to catch generic Exception because FastAPI does it for us
