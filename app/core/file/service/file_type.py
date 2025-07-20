from typing import Tuple

import filetype
from filetype.types import AUDIO, IMAGE, Type, VIDEO, archive, document

from app.core.file.enums import FileType
from app.util.collection import any_match
from app.util.file import is_binary_file


def detect_file_type(file_path: str) -> Tuple[FileType, str] | None:
    buf = filetype.get_bytes(file_path)
    if archive.Pdf().match(buf):
        return FileType.Pdf, archive.Pdf.MIME
    elif document.Docx().match(buf):
        return FileType.Doc, document.Docx.MIME
    elif document.Doc().match(buf):
        return FileType.Doc, document.Doc.MIME

    if not is_binary_file(file_path):
        return FileType.TXT, "text/plain"

    def match(typ: Type) -> bool:
        return typ.match(buf)

    typ = any_match(VIDEO, match)
    if typ:
        return FileType.Video, typ.mime

    typ = any_match(AUDIO, match)
    if typ:
        return FileType.Audio, typ.mime

    typ = any_match(IMAGE, match)
    if typ:
        return FileType.Image, typ.mime

    return None

