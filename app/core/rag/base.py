from pydantic import BaseModel


class TextSplitterRule(BaseModel):
    chunk_overlap: int | None = None
    chunk_size: int | None = None
    separators: list[str] | None = None


class ProcessRule(BaseModel):
    text_splitter: TextSplitterRule


class RerankingModelConfig(BaseModel):
    model_id: int


class EmbeddingModelConfig(BaseModel):
    model_id: int


class RetrievalModelConfig(BaseModel):
    top_k: int
    reranking_model: RerankingModelConfig | None = None
