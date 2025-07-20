from pydantic_settings import BaseSettings

from app.common.constants import APP_NAME


class S3Config(BaseSettings):

    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_UPLOAD_BUCKET: str = APP_NAME
