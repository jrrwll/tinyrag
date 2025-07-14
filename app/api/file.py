from typing import Any

from fastapi import APIRouter
from fastapi import File, UploadFile

from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.file.api import FilePublic
from app.core.file.upload import delete_file, upload_file
from app.entities.file import File as FileEntity

router = APIRouter(prefix="/file", tags=["file"])


@router.post("/upload", response_model=FilePublic)
def upload(file: UploadFile = File(...)) -> Any:
    return upload_file(file)


@router.get("", response_model=FilePublic)
def get(session: SessionDep, id: str) -> Any:
    entity = session.get(FileEntity, id)
    if not entity:
        raise BizException.new(ErrorCode.file_not_found, id)

    return FilePublic(**entity.model_dump())


@router.delete("")
def delete(session: SessionDep, id: str) -> Any:
    entity = session.get(FileEntity, id)
    if not entity:
        raise BizException.new(ErrorCode.file_not_found, id)

    delete_file(entity)
