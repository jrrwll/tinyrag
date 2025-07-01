from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.api import (
    api_router,
    exception_handler,
)
from app.common.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_exception_handler(Exception, exception_handler)

if __name__ == "__main__":
    import uvicorn

    # uvicorn.run(app, host="0.0.0.0")
    uvicorn.run(app="app.main:app", host="0.0.0.0", reload=True, log_level="debug")
