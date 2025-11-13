from typing import Any

from fastapi import File, UploadFile

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.file.api import FilePublic, FileUploadPublic
from app.core.file.service import get_upload_rule
from app.core.file.upload import delete_file, upload_file
from app.entities.file import File as FileEntity
from corepy.api import ApiResult

router = CustomAPIRouter(prefix="/file", tags=["file"])


@router.get("/upload", response_model=ApiResult[FileUploadPublic])
def get_upload() -> Any:
    res = get_upload_rule()
    return ApiResult.create(res)


@router.post("/upload", response_model=ApiResult[FilePublic])
def upload(workspace_id: int, current_user: CurrentUser,
        file: UploadFile = File(...)) -> Any:
    res = upload_file(file, workspace_id, current_user)
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[FilePublic])
def get(session: SessionDep, id: str, current_user: CurrentUser) -> Any:
    entity = session.get(FileEntity, id)
    if not entity:
        raise BizException.create(ErrorCode.file_not_found)

    return ApiResult.create(FilePublic(**entity.model_dump()))


@router.delete("", response_model=ApiResult[Any])
def delete(session: SessionDep, id: str) -> Any:
    entity = session.get(FileEntity, id)
    if not entity:
        raise BizException.create(ErrorCode.file_not_found)

    delete_file(entity)
    return ApiResult.create()
