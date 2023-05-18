from fastapi import APIRouter, Depends, HTTPException

from app.repository import UserAlreadyExistsError
from app.repository.postgres.user import UserRepository, get_user_repository
from app.schema.user import RegisterUserRequest, RegisterUserResponse

router = APIRouter()


@router.post("/register", status_code=201, response_model=RegisterUserResponse)
async def register(
    request: RegisterUserRequest,
    user_repository: UserRepository = Depends(get_user_repository),
):
    try:
        user_id = await user_repository.insert_user(
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
