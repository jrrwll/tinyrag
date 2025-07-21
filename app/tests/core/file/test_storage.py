import os
import os.path

from app.config import settings
from app.core.file.storage.base import get_storage_provider


def test_test_connect():
    storage_provider = get_storage_provider()
    storage_provider.test_connect()


def test_upload_dir():
    local_dir = f"{settings.UPLOAD_DIRECTORY}/quantangshi"
    if not os.path.exists(local_dir):
        return
    print(f"\nprepare to upload {local_dir}")
    storage_provider = get_storage_provider()
    c = storage_provider.upload_dir("chinese-poetry/quantangshi", local_dir)
    print(f"\nc={c}")


def test_list_files():
    storage_provider = get_storage_provider()
    print("\nprepare to list_files /")
    files = storage_provider.list_files("")
    for file in files:
        print(file)

    print("\nprepare to recursive list_files /")
    files = storage_provider.list_files("", recursive=True)
    first_key = None
    for file in files:
        print(file)
        if not first_key:
            first_key = file.key

    keys = [
        first_key, '/'.join(first_key.split('/')[:-1]) + "/",
        f"{first_key}_johndoe", f"{first_key}_johndoe/"
    ]
    print(f"\nprepare to exists {keys}")
    for k in keys:
        exists = storage_provider.exists(k)
        print(f"file {k} exists: {exists}")
