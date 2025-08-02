from app.common.deps import open_session
from app.core.model.api import ModelPublic
from app.core.model.embedding.base import get_embedding_provider
from app.core.model.enums import ModelType
from app.entities.repo.model import get_required_setup_model
from app.tests import print_time


def test_embedding(print_time):
    print("\ntest_embedding")
    workspace_id, tenant_id = 1, 1
    with open_session() as session:
        model = get_required_setup_model(
            session, ModelType.TextEmbedding,
            workspace_id, tenant_id)

    embedding_provider = get_embedding_provider(model)
    v = embedding_provider.embed_query("Hello World!")
    print(v)


def test_builtin_embedding1(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "all-MiniLM-L6-v2")
    embedding_provider = get_embedding_provider(model)
    v = embedding_provider.embed_query("Hello World!")
    print(len(v)) # 384
    print(v)


def test_builtin_embedding2(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "all-MiniLM-L12-v2")
    embedding_provider = get_embedding_provider(model)
    v = embedding_provider.embed_query("Hello World!")
    print(len(v)) # 384
    print(v)


def test_builtin_embedding3(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "multilingual-e5-small")
    embedding_provider = get_embedding_provider(model)
    v = embedding_provider.embed_query("Hello World!")
    print(len(v)) #
    print(v)


def test_builtin_embedding4(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "nomic-embed-text-v1.5")
    embedding_provider = get_embedding_provider(model)
    v = embedding_provider.embed_query("Hello World!")
    print(len(v)) # 768
    print(v)
