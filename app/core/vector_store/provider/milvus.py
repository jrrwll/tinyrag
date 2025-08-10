from langchain_milvus import Milvus
from pydantic import BaseModel, SecretStr
from pymilvus import MilvusClient

from app.core.vector_store.provider.base import VectorProvider


class MilvusVectorStoreConfig(BaseModel):
    uri: str
    user: str | None =  None
    password: SecretStr | None =  None
    db_name: str | None =  None
    token: SecretStr | None =  None
    timeout: float | None =  None


# TODO cache the client
class MilvusVectorProvider(VectorProvider[MilvusVectorStoreConfig, MilvusClient]):

    @staticmethod
    def get_config_type() -> type[MilvusVectorStoreConfig]:
        return MilvusVectorStoreConfig

    def _init(self) -> None:
        connection_args = self.config.model_dump(exclude_none=True)

        self.vector_store = Milvus(
            connection_args=connection_args,
            collection_name=self.collection_name,
            embedding_function=self.model_provider.model
        )
        self.client = self.vector_store._milvus_client

