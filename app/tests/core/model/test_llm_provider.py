
from app.common.deps import open_session
from app.core.model.api import ModelPublic
from app.core.model.llm.base import get_llm_provider
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
            Model.type == ModelType.LLM,
            Model.deleted == False,
            )
        model_entity = session.exec(select_sql).first()
        if not model_entity:
            print("no LLM model found")
            return

    model = ModelPublic.create(model_entity)
    provider = get_llm_provider(model)
    v = provider.test_run("Hello World!")
    print(f"test_run:\n{v}")


def test_setup_llm(print_time):
    print("\ntest_setup_llm")
    workspace_id, tenant_id = 1, 1
    with open_session() as session:
        model = get_setup_model(
            session, ModelType.TextEmbedding,
            workspace_id, tenant_id)
        if not model:
            print("no LLM model found")
            return

    provider = get_llm_provider(model)
    v = provider.test_run("Hello World!")
    print(f"test_run:\n{v}")

