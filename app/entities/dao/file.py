from sqlmodel import select

from app.common.deps import SessionDep
from app.entities.file import File


def get_files(session: SessionDep, file_ids: list[str]) -> dict[str, File]:
    statement = select(File).where(
        File.id in file_ids,
    )

    files = session.exec(statement).all()
    return {file.id: file for file in files}
