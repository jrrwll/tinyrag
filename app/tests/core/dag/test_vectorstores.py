from app.config import settings
from app.core.rag.text_process.base import get_text_processor
from app.core.rag.vectorstores import create_vector_store
from app.core.file.enums import FileType
from app.core.file.service.load import load_document_file
from app.tests.test_base import _find_first_file


def test_add_documents():
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")
    if not local_path:
        return

    text_processor = get_text_processor(settings.dataset_default_process_rule)

    docs = list(text_processor.load_documents(local_path, FileType.TXT))
    print(f"\ndocs={len(docs)}")

    documents = text_processor.split_documents(docs)

    vector_store = create_vector_store("test")
    doc_ids = vector_store.add_documents(documents)
    print(f"doc_ids={doc_ids}")


def test_search():
    vector_store = create_vector_store("test")
    matched_dcos = vector_store.similarity_search("流沙", k=10)
    for d in matched_dcos:
        print(f"{d}")
