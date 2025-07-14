import mimetypes
import os
import os.path
import shutil
from uuid import uuid4

from fastapi import UploadFile
from sqlmodel import Session

from app.common.config import settings
from app.common.db import engine
from app.core.file.api import FilePublic
from app.entities.file import File
from app.util.datetme import format_date_compact
from app.util.file import get_file_md5


def upload_file(file: UploadFile) -> FilePublic:
    file_dir = f"{settings.UPLOAD_DIRECTORY}/{format_date_compact()}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)

    file_path = f"{file_dir}/{uuid4()}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    md5 = get_file_md5(file_path)

    with Session(engine) as session:
        existing_entity = session.get(File, md5)

    if existing_entity:
        return FilePublic(**existing_entity.model_dump())

    filename, size = file.filename, file.size
    _, extension = os.path.splitext(filename)
    mime_type, _ = mimetypes.guess_type(file_path)

    entity = File(id=md5, name=filename, size=size,
         extension=extension, mime_type=mime_type)

    tail1, tail2 = md5[-4:-2], md5[-2:]
    save_dir = f"{settings.FILES_DIRECTORY}/{tail1}/{tail2}"
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

    return FilePublic(**existing_entity.model_dump())


def delete_file(entity: File):
    md5 = entity.id
    tail = md5[-4:]
    save_path = f"{settings.FILES_DIRECTORY}/{tail}/{md5}"
    if os.path.exists(save_path):
        os.remove(save_path)
