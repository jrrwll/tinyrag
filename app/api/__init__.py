from fastapi import APIRouter

from app.api import private, workflow
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(workflow.router)


if settings.IS_TEST_ENV:
    api_router.include_router(private.router)
