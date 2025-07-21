from app.config import settings
from app.core.file.storage.opendal import OpendalStorageProvider
import os
import os.path

def test_opendal():
    storage_provider = OpendalStorageProvider()
    storage_provider.test_connect()


def test_upload_dir():
    local_dir = f"{settings.UPLOAD_DIRECTORY}/quantangshi"
    if not os.path.exists(local_dir):
        return
    print(f"\nprepare to upload {local_dir}")
    storage_provider = OpendalStorageProvider()
    c = storage_provider.upload_dir("chinese-poetry/quantangshi", local_dir)
    print(f"\nc={c}")


def test_list_files():
    storage_provider = OpendalStorageProvider()
    print("\nprepare to list_files /")
    files = storage_provider.list_files("/")
    for file in files:
        print(file)

    print("\nprepare to recursive list_files /")
    files = storage_provider.list_files("/", recursive=True)
    for file in files:
        print(file)