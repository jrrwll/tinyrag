import json
from functools import cached_property
from typing import Literal, Self

from pydantic_settings import BaseSettings
from pydantic import model_validator

from app.common.constants import APP_NAME
from app.core.dataset.base import ProcessRule
from app.core.dataset.enums import VectorStoreType
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


class VectorStoreConfig(BaseSettings):

    VECTOR_STORE_TYPE: VectorStoreType = VectorStoreType.Chroma
    VECTOR_STORE_COLLECTION_NAME: str = APP_NAME

    CHROMA_PERSIST_DIRECTORY: str | None

    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None

    PGVECTOR_URL: str | None = None

    # pymilvus.milvus_client.milvus_client.MilvusClient.__init__
    MILVUS_URI: str = "http://localhost:19530"
    MILVUS_USER: str = ""
    MILVUS_PASSWORD: str = ""
    MILVUS_DB_NAME: str = ""
    MILVUS_TOKEN: str = ""
    MILVUS_TIMEOUT: float | None = None

    @property
    def vector_store__persist_directory(self) -> str:
        if self.CHROMA_PERSIST_DIRECTORY:
            return self.CHROMA_PERSIST_DIRECTORY
        return f"{_singleton_workdir}/vectorstore"
