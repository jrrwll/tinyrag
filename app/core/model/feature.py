from app.core.model.api import ModelPublic
from app.core.model.base import ModelFeatureConfig
from app.core.model.embedding.base import get_embedding_provider
from app.core.model.enums import ModelType
from app.entities.model import Model


def compute_model_feature(entity: Model) -> ModelFeatureConfig:
    config = ModelFeatureConfig()

    model_type = entity.type
    if model_type == ModelType.TextEmbedding:
        model = ModelPublic.create(entity)
        provider = get_embedding_provider(model)
        embedding_vector = provider.embed_query("dummy_text")
        config.vector_size = len(embedding_vector)

    return config
