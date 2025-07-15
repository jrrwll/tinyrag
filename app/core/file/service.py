from langchain_core.documents import Document

from app.core.file.document_loader import load_docx, load_pdf, load_text
from app.core.file.upload import get_file_path
from app.entities.file import File


def load_document_file(file: File, limit: int | None = None) -> list[Document]:
    file_path = get_file_path(file.id)

    extension = file.extension
    if not extension:
        return []

    extension = extension.lower()
    if extension == 'pdf':
        iter = load_pdf(file_path)
    elif extension == 'docx':
        iter = load_docx(file_path)
    else:
        iter = load_text(file_path)

    if not limit:
        return list(iter)
    else:
        docs = []
        for doc in iter:
            if limit == 0:
                break
            limit -= 1

            docs.append(doc)
        return docs
