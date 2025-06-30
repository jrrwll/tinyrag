from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError

from app.api import api_router, biz_exception_handler, exception_handler, validation_exception_handler
from app.common.config import settings
from app.common.error_code import BizException


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(BizException, biz_exception_handler)
app.add_exception_handler(Exception, exception_handler)

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0")
    uvicorn.run(app="app.main:app", host="0.0.0.0",
                reload=True, log_level="debug")
