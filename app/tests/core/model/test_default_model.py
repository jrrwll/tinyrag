from app.core.model.api import ModelPublic
from app.core.model.default_model import get_default_model
from app.core.model.enums import ModelType
from app.core.model.privoder.base import get_model_provider
from app.tests import print_time


def test_llm_model(print_time):
    model = get_default_model(ModelType.LLM)
    model_provider = get_model_provider(ModelPublic.create(model))
    print(f"\nmodel_provider={model_provider}")

    res = model_provider.test_run("Who are you?")
    print(f"\nres:\n{res}")
    print(f"content:\n{res.get('content')}")


def test_embeddings_model(print_time):
    model = get_default_model(ModelType.TextEmbedding)
    model_provider = get_model_provider(ModelPublic.create(model))
    print(f"\nmodel_provider={model_provider}")

    vec = model_provider.embed_query("Hi")
    print(f"\nvec={vec}")
