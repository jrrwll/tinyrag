import hashlib
import os
import codecs

__boms = (codecs.BOM_UTF8, codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE,
          codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE)
__text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})


def is_binary_file(file_path: str) -> bool:
    with open(file_path, 'rb') as f:
        # read 1024 bytes in the head
        chunk = f.read(1024)

        # has utf bom
        header = chunk[0:4]
        if any(header.startswith(bom) for bom in __boms):
            return True

        # check unprintable chars
        if b'\0' in chunk:
            return True

        # unprintable chars threshold
        non_text = sum(byte not in __text_chars for byte in chunk)
        return (non_text / len(chunk)) > 0.3


def get_file_md5(file_path: str) -> str:
    hash_md5 = hashlib.md5()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def mkdirs(dir_path: str) -> None:
    os.makedirs(dir_path, exist_ok=True)