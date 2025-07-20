import hashlib
import os


def is_binary_file(file_path: str) -> bool:
    with open(file_path, 'rb') as f:
        # read 1024 bytes in the head
        chunk = f.read(1024)
        # check unprintable chars
        if b'\0' in chunk:
            return True
        if all(c < 128 for c in chunk):
            return False

    return True


def get_file_md5(file_path: str) -> str:
    hash_md5 = hashlib.md5()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def mkdirs(dir_path: str) -> None:
    os.makedirs(dir_path, exist_ok=True)