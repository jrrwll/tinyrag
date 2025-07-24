from abc import ABC, abstractmethod

from langchain_core.vectorstores import VectorStore

from app.core.rag.text_process.base import DocumentModel
from app.core.rag.vector.base import Vector


class BaseVectorStore(Vector, ABC):

    @abstractmethod
    def get_vector_store(self) -> VectorStore:
        raise NotImplementedError()

    def add_documents(self, documents: list[DocumentModel]) -> None:
        docs = [d.to_document() for d in documents]
        self.get_vector_store().add_documents(docs)

    def add_texts(self, documents: list[DocumentModel],
            embeddings: list[list[float]], **kwargs):
        ids = [d.id for d in documents]
        texts = [d.content for d in documents]
        metadatas = [d.metadata for d in documents]

        self.get_vector_store().add_texts(ids=ids, texts=texts, metadatas=metadatas)
