from app.common.deps import open_session
from app.core.model.enums import ModelType
from app.entities.repo.model import get_required_setup_model, get_setup_models
from app.entities.repo.vector_store import get_setup_vector_store


def test_get_setup_model():
    print("\ntest_get_setup_vector_store")
    workspace_id, tenant_id = 1, 1

    with open_session() as session:
        models = get_setup_models(session, workspace_id, tenant_id)
        for model_type, model in models.items():
            print(f"\n{model_type}")
            print(model.model_dump_json(indent=4))

        model = get_required_setup_model(
            session, ModelType.LLM,
            workspace_id, tenant_id)
        print(f"\nLLM={model.model_dump_json()}")

        model = get_required_setup_model(
            session, ModelType.TextEmbedding,
            workspace_id, tenant_id)
        print(f"\nTextEmbedding={model.model_dump_json()}")


def test_get_setup_vector_store():
    print("\ntest_get_setup_vector_store")
    workspace_id, tenant_id = 1, 1

    with open_session() as session:
        vs = get_setup_vector_store(session, workspace_id, tenant_id)
        print(vs.model_dump_json(indent=4))
