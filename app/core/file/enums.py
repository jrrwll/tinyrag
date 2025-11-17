from enum import StrEnum


class FileType(StrEnum):
    TXT = "txt"
    Pdf = "pdf"
    Doc = "Doc"  # doc or docx
    Image = "image"
    Audio = "audio"
    Video = "video"

    def is_document(self) -> bool:
        return self in _documents


_documents = {FileType.TXT, FileType.Doc, FileType.Pdf}
