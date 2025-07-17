from typing import Iterator

from langchain_core.documents import Document

from app.core.file.enums import FileType
from app.core.file.service.upload import get_file_path
from app.entities.file import File
from app.util.langchain.document_loader import load_docx, load_pdf, load_text


def load_document_file(file: File) -> Iterator[Document]:
    file_path = get_file_path(file.id)

    file_type = file.type
    if file_type == FileType.Pdf:
        return load_pdf(file_path)
    elif file_type == FileType.Doc:
        return load_docx(file_path)
    else:
        return load_text(file_path)
