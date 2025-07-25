import os
import os.path
import shutil
from uuid import uuid4

from fastapi import UploadFile
from sqlmodel import Session

from app.common.db import engine
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.file.api import FilePublic
from app.core.file.service.file_type import detect_file_type
from app.entities.file import File
from app.util.datetime import format_date_compact
from app.util.codec import get_file_md5


def upload_file(file: UploadFile) -> FilePublic:
    file_dir = f"{settings.UPLOAD_DIRECTORY}/{format_date_compact()}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)

    file_path = f"{file_dir}/{uuid4()}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = detect_file_type(file_path)
    if not file_type:
        raise BizException.new(ErrorCode.file_type_not_supported)
    else:
        file_type, mime_type = file_type

    md5 = get_file_md5(file_path)
    with Session(engine) as session:
        existing_entity = session.get(File, md5)

    if existing_entity:
        return FilePublic(**existing_entity.model_dump())

    filename, size = file.filename, file.size
    entity = File(id=md5, type=file_type, name=filename,
                  size=size, mime_type=mime_type)

    save_dir = _get_file_dir(md5)
    os.makedirs(save_dir, exist_ok=True)
    save_path = f"{save_dir}/{md5}"
    shutil.move(file_path, save_path) # maybe very slow

    ex: Exception | None = None
    with Session(engine) as session:
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
