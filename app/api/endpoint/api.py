from fastapi import APIRouter
from app.api.endpoint import health

router = APIRouter(prefix="/api/v1")
router.include_router(health.router, tags=["health"])
