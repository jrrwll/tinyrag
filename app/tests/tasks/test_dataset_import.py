from sqlmodel import select

from app.common.db import open_session
from app.core.file.service.base import get_storage_files
from app.entities.file import File
from app.tasks.knowledge_import.file import list_files
from app.tasks.knowledge_import.storage import list_storage_files


def test_list_files():
    print("\ntest_list_files")
    with open_session() as session:
        select_stmt = select(File).where(File.deleted == False).limit(10)

        files = session.exec(select_stmt).all()
        file_dict = {file.id: file for file in files}

    for params in list_files(file_dict):
        print(params.model_dump_json())


def test_list_storage_files():
    print("\ntest_list_storage_files")
    storage_files = get_storage_files("chinese-poetry/quantangshi/")

    limit = 10
    for params in list_storage_files(storage_files):
        print(params.model_dump_json())
        limit -= 1
        if limit == 0:
            break
