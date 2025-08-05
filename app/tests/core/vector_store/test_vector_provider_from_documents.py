from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient

from app.config import settings
from app.core.file.enums import FileType
from app.core.knowledge.text_process.base import get_text_processor
from app.core.model.embedding.base import get_embedding_provider
from app.core.vector_store.enums import VectorStoreType
from app.core.vector_store.provider.base import VectorProvideFactory
from app.tests.core.vector_store.test_vector_provider import \
    _get_vector_store_and_model
from app.tests.test_base import _find_first_file


def test_add_documents_chroma():
    run_add_documents(VectorStoreType.Chroma)


def run_add_documents(vector_store_type: VectorStoreType):
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")
    if not local_path:
        return
    text_processor = get_text_processor(settings.default_process_rule)
    documents = text_processor.load_documents(local_path, FileType.TXT)
    docs = list(text_processor.split_documents(documents))
    docs1 = [d.to_document() for d in docs[:2]]
    docs2 = [d.to_document() for d in docs[2:]]

    vector_store, model = _get_vector_store_and_model(vector_store_type)
    model_provider = get_embedding_provider(model)

    client = QdrantClient(path=vector_store.local_dir())
    vector = QdrantVectorStore.from_documents(
        docs1, model_provider.model,
        client=client,
        collection_name='tinyrag_test')

    docs_id = vector.add_documents(docs2)
    print(f"docs_id: {docs_id}")


def run_search(vector_store_type: VectorStoreType):
    print(f"\nvector_store_type={vector_store_type}")
    vector_store, model = _get_vector_store_and_model(vector_store_type)
    vector = VectorProvideFactory.create_vector(
        "tinyrag_test", vector_store, model)

    vec = vector.model_provider.embed_query("流沙")
    print(f"\nvec {len(vec)} {vec}\n")

    matched_dcos = vector.similarity_search("流沙", k=10)
    for d in matched_dcos:
        print(f"{d}")
