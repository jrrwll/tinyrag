from app.common.deps import open_session
from app.core.model.api import ModelPublic
from app.core.model.embedding.base import get_embedding_provider
from app.core.model.enums import ModelType
from app.entities.model import Model
from app.entities.repo.model import get_setup_model
from app.tests import print_time
from sqlmodel import select


def test_provider(print_time):
    print("\ntest_provider")
    workspace_id, tenant_id = 1, 1
    with open_session() as session:
        select_sql = select(Model).where(
            Model.tenant_id == tenant_id,
            Model.type == ModelType.TextEmbedding,
            Model.deleted == False,
        )
        model_entity = session.exec(select_sql).first()
        if not model_entity:
            print("no TextEmbedding model found")
            return

    model = ModelPublic.create(model_entity)
    provider = get_embedding_provider(model)
    v = provider.embed_query("Hello World!")
    print(f"embed_query {len(v)}:\n{v}")


def test_setup_embedding(print_time):
    print("\ntest_setup_embedding")
    workspace_id, tenant_id = 1, 1
    with open_session() as session:
        model = get_setup_model(
            session, ModelType.TextEmbedding,
            workspace_id, tenant_id)
        if not model:
            print("no TextEmbedding model found")
            return

    provider = get_embedding_provider(model)
    v = provider.embed_query("Hello World!")
    print(f"embed_query {len(v)}:\n{v}")


def test_builtin_embedding1(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "all-MiniLM-L6-v2")
    provider = get_embedding_provider(model)
    v = provider.embed_query("Hello World!")
    print(len(v)) # 384
    print(v)


def test_builtin_embedding2(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "all-MiniLM-L12-v2")
    provider = get_embedding_provider(model)
    v = provider.embed_query("Hello World!")
    print(len(v)) # 384
    print(v)


def test_builtin_embedding3(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "multilingual-e5-small")
    provider = get_embedding_provider(model)
    v = provider.embed_query("Hello World!")
    print(len(v)) #
    print(v)


def test_builtin_embedding4(print_time):
    print("\ntest_builtin_embedding")

    model = ModelPublic.from_builtin(
        ModelType.TextEmbedding, "nomic-embed-text-v1.5")
    provider = get_embedding_provider(model)
    v = provider.embed_query("Hello World!")
    print(len(v)) # 768
    print(v)
