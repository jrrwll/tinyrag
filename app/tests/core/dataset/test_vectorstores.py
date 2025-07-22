from app.config import settings
from app.core.dataset.process_rule import get_text_splitter
from app.core.dataset.vectorstores import get_vector_store
from app.core.file.enums import FileType
from app.core.file.service.load import load_document_file
from app.tests.test_base import _find_first_file


def test_add_documents():
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")

    docs = list(load_document_file(local_path, FileType.TXT))

    text_splitter = get_text_splitter(settings.dataset_default_process_rule)
    documents = text_splitter.split_documents(docs)

    vector_store = get_vector_store()
    doc_ids = vector_store.add_documents(documents)
    print(f"doc_ids={doc_ids}")


def test_search():
    vector_store = get_vector_store()
    matched_dcos = vector_store.similarity_search("流沙", k=10)
    for d in matched_dcos:
        print(f"{d}")
