from typing import Iterator

from langchain_core.documents import Document

from app.core.file.document_loader import load_docx, load_pdf, load_text
from app.core.file.upload import get_file_path
from app.entities.file import File


def load_document_file(file: File) -> Iterator[Document]:
    file_path = get_file_path(file.id)

    extension = file.extension
    if not extension:
        return iter([])

    extension = extension.lower()
    if extension == 'pdf':
        return load_pdf(file_path)
    elif extension == 'docx':
        return load_docx(file_path)
    else:
        return load_text(file_path)
