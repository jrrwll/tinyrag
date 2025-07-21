from typing import Iterator

from langchain_core.documents import Document

from app.core.file.enums import FileType
from app.util.langchain.document_loader import load_docx, load_pdf, load_text


# File or file_path
def load_document_file(file_path: str, file_type: FileType) -> Iterator[Document]:
    if file_type == FileType.Pdf:
        return load_pdf(file_path)
    elif file_type == FileType.Doc:
        return load_docx(file_path)
    else:
        return load_text(file_path)
