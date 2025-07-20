from typing import Any

from fastapi import APIRouter
from fastapi import File, UploadFile

from app.util.api import ApiResult
from app.common.db import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.file.api import FilePublic
from app.core.file.service.upload import delete_file, upload_file
from app.entities.file import File as FileEntity

router = APIRouter(prefix="/file", tags=["file"])


@router.post("/upload", response_model=ApiResult[FilePublic])
def upload(file: UploadFile = File(...)) -> Any:
    res = upload_file(file)
    return ApiResult.new(res)


@router.get("", response_model=ApiResult[FilePublic])
def get(session: SessionDep, id: str) -> Any:
    entity = session.get(FileEntity, id)
    if not entity:
        raise BizException.new(ErrorCode.file_not_found, id)

    return ApiResult.new(FilePublic(**entity.model_dump()))


@router.delete("", response_model=ApiResult[Any])
def delete(session: SessionDep, id: str) -> Any:
    entity = session.get(FileEntity, id)
    if not entity:
        raise BizException.new(ErrorCode.file_not_found, id)

    delete_file(entity)
    return ApiResult.new()
