from sqlmodel import select

from app.common.deps import SessionDep
from app.entities.file import File


def get_files(session: SessionDep, file_ids: list[str], tenant_id: int
) -> dict[str, File]:
    statement = select(File).where(
        File.id.in_(file_ids), # type: ignore[attr-defined]
        File.tenant_id == tenant_id,
    )

    files = session.exec(statement).all()
    return {file.id: file for file in files}
