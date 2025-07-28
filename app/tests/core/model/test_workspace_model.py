from app.core.model.embedding.base import get_embedding_provider
from app.core.model.llm.base import get_llm_provider
from app.entities.dao.workspace import get_workspace_detail
from app.tests import print_time


def test_llm_model(print_time):
    print("\ntest_llm_model")
    workspace = get_workspace_detail(1)
    if not workspace.llm_model:
        print("No LLM model found")
        return

    model_provider = get_llm_provider(workspace.llm_model)
    print(f"\nmodel_provider={model_provider}")

    res = model_provider.test_run("Who are you?")
    print(f"\nres:\n{res}")
    print(f"content:\n{res.get('content')}")


def test_embeddings_model(print_time):
    print("\ntest_embeddings_model")
    workspace = get_workspace_detail(1)
    if not workspace.embedding_model:
        print("No LLM model found")
        return

    model_provider = get_embedding_provider(workspace.embedding_model)
    print(f"\nmodel_provider={model_provider}")

    vec = model_provider.embed_query("Hi")
    print(f"\nvec={vec}")
