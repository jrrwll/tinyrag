from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType
from app.tests import print_time


def test_embeddings(print_time):
    model_provider = get_default_model_provider(ModelType.TextEmbedding)
    print(f"\nmodel_provider={model_provider}")
    embeddings_model = model_provider.embeddings_model
    print(f"\nembeddings_model={embeddings_model}")

    vec = embeddings_model.embed_query("Hi")
    print(f"\nvec={vec}")
