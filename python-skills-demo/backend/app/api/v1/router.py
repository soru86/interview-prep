"""V1 router — aggregates all v1 endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import items, users

router = APIRouter(prefix="/api/v1")
router.include_router(users.router)
router.include_router(items.router)
