import os
import os.path
import shutil
from uuid import uuid4

from fastapi import UploadFile

from app.common.deps import open_session
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.file.api import FilePublic
from app.core.file.file_type import detect_file_type
from app.entities.file import File
from app.entities.user import User
from corepy.codec import file_md5
from corepy.datetime import format_date_compact


def upload_file(file: UploadFile, workspace_id: int, current_user: User) -> FilePublic:
    file_dir = f"{settings.UPLOAD_DIRECTORY}/{format_date_compact()}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)

    file_path = f"{file_dir}/{uuid4()}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = detect_file_type(file_path)
    if not file_type:
        raise BizException.create(ErrorCode.file_type_not_supported)
    else:
        file_type, mime_type = file_type

    md5 = file_md5(file_path)
    with open_session() as session:
        existing_entity = session.get(File, md5)

    if existing_entity:
        return FilePublic(**existing_entity.model_dump())

    filename, size = file.filename, file.size
    entity = File(id=md5, type=file_type, name=filename,
                  size=size, mime_type=mime_type,
                  tenant_id=current_user.tenant_id,
                  workspace_id=workspace_id)

    save_dir = _get_file_dir(md5)
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{md5}"
    shutil.move(file_path, save_path) # maybe very slow

    ex: Exception | None = None
    with open_session() as session:
        try:
            session.add(entity)
            session.commit()
            session.refresh(entity)
        except Exception as e:
            session.rollback()
            ex = e

    if ex:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise ex

    return FilePublic(**entity.model_dump())


def delete_file(entity: File) -> None:
    save_path = get_file_path(entity.id)
    if os.path.exists(save_path):
        os.remove(save_path)


def get_file_path(file_id: str) -> str:
    return f"{_get_file_dir(file_id)}/{file_id}"


def _get_file_dir(file_id: str) -> str:
    tail1, tail2 = file_id[-4:-2], file_id[-2:]
    return f"{settings.FILES_DIRECTORY}/{tail1}/{tail2}"
