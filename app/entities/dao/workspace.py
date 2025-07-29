from sqlmodel import func, select

from app.common.deps import SessionDep, open_session
from app.core.model.api import ModelPublic
from app.core.model.enums import EmbeddingType, ModelType
from app.core.workspace.api import WorkspacePublic
from app.core.workspace.base import WorkspaceDetail
from app.entities.dao.model import get_model
from app.entities.workspace import Workspace


def page_and_count_workspaces(
        session: SessionDep, page_no: int, page_size: int
) -> tuple[list[dict], int]:  # type: ignore[type-arg]
    conditions = [Workspace.deleted == False]

    count_statement = (
        select(func.count()).select_from(Workspace)
        .where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(  # type: ignore[call-overload]
            Workspace.id,
            Workspace.created_at,
            Workspace.updated_at,
            Workspace.name,
            Workspace.description,
        )
        .select_from(Workspace)
        .where(*conditions)
        .offset(offset)
        .limit(limit)
    )
    models = session.exec(page_statement).mappings().all()
    return [dict(i) for i in models], count


def get_workspace_detail(workspace_id: int) -> WorkspaceDetail | None:
    with open_session() as session:
        workspace_entity = session.get(Workspace, workspace_id)
        if not workspace_entity:
            return None
        tenant_id = workspace_entity.tenant_id

        workspace = WorkspacePublic.create(workspace_entity)
        llm_model_config = workspace.llm_model_config
        embedding_model_config = workspace.embedding_model_config

        workspace_detail = WorkspaceDetail(
            id=workspace.id, name=workspace.name)

        if llm_model_config:
            model_id = llm_model_config.model_id
            workspace_detail.llm_model = get_model(session, model_id, tenant_id)
        if embedding_model_config:
            if embedding_model_config.embedding_type == EmbeddingType.Provider:
                model_id = embedding_model_config.model_id
                workspace_detail.embedding_model = get_model(
                    session, model_id, tenant_id)
            else:
                workspace_detail.embedding_model = ModelPublic.from_builtin(
                    ModelType.TextEmbedding, embedding_model_config.model_name)

        return workspace_detail
