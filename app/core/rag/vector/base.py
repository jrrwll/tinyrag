from abc import ABC, abstractmethod
from typing import Type

from app.config import settings
from app.core.rag.enums import VectorStoreType
from app.core.rag.text_process.base import DocumentModel
from app.entities.model import Model


class Vector(ABC):

    collection_name: str

    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    def create_collection_if_absent(self):
        raise NotImplementedError()

    def delete_collection(self):
        raise NotImplementedError()

    @abstractmethod
    def add_documents(self, documents: list[DocumentModel]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def add_texts(self, documents: list[DocumentModel], embeddings: list[list[float]], **kwargs):
        raise NotImplementedError()


class VectorFactory:

    @staticmethod
    def create_vector(collection_name: str, model: Model) -> Vector:
        vector_class = VectorFactory._get_vector_class()

        return vector_class(collection_name, model)

    @staticmethod
    def _get_vector_class[T: Vector]() -> Type[T]:
        vector_store_type = settings.VECTOR_STORE_TYPE
        if vector_store_type == VectorStoreType.Qdrant:
            from app.core.rag.vector.qdrant import QdrantVector

            return QdrantVector
        elif vector_store_type == VectorStoreType.PGVector:
            from app.core.rag.vector.postgres import PostgresVector

            return PostgresVector
        elif vector_store_type == VectorStoreType.Milvus:
            from app.core.rag.vector.milvus import MilvusVector

            return MilvusVector
        else:
            from app.core.rag.vector.chroma import ChromaVector

            return ChromaVector
