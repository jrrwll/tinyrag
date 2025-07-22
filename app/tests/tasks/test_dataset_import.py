from sqlmodel import select

from app.common.db import open_session
from app.config import settings
from app.core.dataset.process_rule import get_text_splitter
from app.core.file.service.file_type import detect_file_type
from app.core.file.service.load import load_document_file
from app.entities.dao.dataset import save_document_chucks
from app.entities.dataset import DocumentChunk
from app.tests.test_base import _find_first_file


def test_split_documents():
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")

    process_rule = settings.dataset_default_process_rule
    text_splitter = get_text_splitter(process_rule)

    file_type, _ = detect_file_type(local_path)
    docs = load_document_file(local_path, file_type)
    doc = next(docs)

    documents = text_splitter.split_documents([doc])
    for document in documents[0:3]:
        print(f"{document}")

    document = documents[0]
    chunk = DocumentChunk(
        dataset_id=0,
        document_id=0,
        position=0,
        content=document.page_content,
        word_count=0,
    )
    save_document_chucks([chunk])

    with open_session() as session:
        select_sql = select(DocumentChunk).where(DocumentChunk.document_id == 0)
        chunks = session.exec(select_sql).all()
        print("\nchunks")
        for c in chunks:
            print(f"chunk={c}")
