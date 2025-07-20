from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.base import (
    api_router,
    exception_handler,
)
from app.common.log import add_request_id, config_logging
from app.config import settings

config_logging()

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_exception_handler(Exception, exception_handler)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_request_id)
