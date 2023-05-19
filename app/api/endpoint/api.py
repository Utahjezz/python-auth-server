from fastapi import APIRouter
from app.api.endpoint import health, auth

router = APIRouter(prefix="/api/v1")
router.include_router(health.router, tags=["health"])
router.include_router(auth.router, tags=["auth"])
