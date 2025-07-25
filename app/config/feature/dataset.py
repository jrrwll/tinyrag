import json
from functools import cached_property
from typing import Self

from pydantic_settings import BaseSettings
from pydantic import model_validator, PositiveInt, NonNegativeInt

from app.common.constants import APP_NAME
from app.core.rag.base import ProcessRule
from app.core.rag.enums import VectorStoreType
from app.config.base import _singleton_workdir

_dataset_default_process_rule = {
    "text_splitter": {
        "chunk_overlap": 50,
        "chunk_size": 1024,
        "separators": ["\n\n", "\n", " ", ""]
    }
}

class DatasetConfig(BaseSettings):
    DATASET_DEFAULT_PROCESS_RULE: str = json.dumps(_dataset_default_process_rule)

    @cached_property
    def dataset_default_process_rule(self) -> ProcessRule:
        return ProcessRule.model_validate_json(
            self.DATASET_DEFAULT_PROCESS_RULE)

    @model_validator(mode="after")
    def _validate_process_rule(self) -> Self:
        process_rule = self.dataset_default_process_rule
        assert process_rule
        return self


class FileUploadConfig(BaseSettings):

    UPLOAD_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_IMAGE_FILE_SIZE_LIMIT: NonNegativeInt = 20
    UPLOAD_AUDIO_FILE_SIZE_LIMIT: NonNegativeInt = 50
    UPLOAD_VIDEO_FILE_SIZE_LIMIT: NonNegativeInt = 100


class VectorStoreConfig(BaseSettings):

    VECTOR_STORE_TYPE: VectorStoreType = VectorStoreType.Chroma

    CHROMA_PERSIST_DIRECTORY: str | None = None
    CHROMA_HOST: str | None = None
    CHROMA_PORT: PositiveInt | None = None
    CHROMA_TENANT: str | None = None
    CHROMA_DATABASE: str | None = None
    CHROMA_AUTH_PROVIDER: str | None = None
    CHROMA_AUTH_CREDENTIALS: str | None = None

    QDRANT_LOCAL_PATH: str | None = None
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    QDRANT_HTTPS: bool | None = None
    QDRANT_GRPC_PORT: PositiveInt | None = None
    QDRANT_GRPC_ENABLED: bool = False

    # postgresql+psycopg://user:password@host:port/database
    PGVECTOR_URL: str | None = None
    PGVECTOR_POOL_SIZE: PositiveInt | None = None
    PGVECTOR_POOL_TIMEOUT: PositiveInt | None = None

    # pymilvus.milvus_client.milvus_client.MilvusClient.__init__
    MILVUS_URI: str | None = None
    MILVUS_USER: str | None = None
    MILVUS_PASSWORD: str | None = None
    MILVUS_DB_NAME: str = APP_NAME
    MILVUS_TOKEN: str | None = None
    MILVUS_TIMEOUT: float | None = None

    @cached_property
    def vector_store_persist_directory(self) -> str:
        return f"{_singleton_workdir}/vectorstore/{self.VECTOR_STORE_TYPE.value}"
