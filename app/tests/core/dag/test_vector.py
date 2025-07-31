from sqlmodel import select

from app.common.deps import open_session
from app.config import settings
from app.core.file.enums import FileType
from app.core.model.api import ModelPublic
from app.core.model.default_model import get_default_model
from app.core.model.enums import ModelType
from app.core.knowledge.text_process.base import get_text_processor
from app.core.vector_store.api import VectorStorePublic
from app.core.vector_store.enums import VectorStoreType
from app.core.vector_store.provider.base import VectorProvideFactory
from app.entities.vector_store import VectorStore
from app.tests.test_base import _find_first_file


def test_add_documents_chroma():
    run_add_documents(VectorStoreType.Chroma)


def test_search_chroma():
    run_search(VectorStoreType.Chroma)


def test_add_documents_qdrant():
    run_add_documents(VectorStoreType.Qdrant)


def test_search_qdrant():
    run_search(VectorStoreType.Qdrant)


def test_add_documents_pgvector():
    run_add_documents(VectorStoreType.PGVector)


def test_search_pgvector():
    run_search(VectorStoreType.PGVector)


def test_add_documents_milvus():
    run_add_documents(VectorStoreType.Milvus)


def test_search_milvus():
    run_search(VectorStoreType.Milvus)


def run_add_documents(vector_store_type: VectorStoreType):
    settings.VECTOR_STORE_TYPE = vector_store_type

    print(f"\nvector_store_type={vector_store_type}")
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")
    if not local_path:
        return

    text_processor = get_text_processor(settings.knowledge_default_process_rule)

    docs = list(text_processor.load_documents(local_path, FileType.TXT))
    print(f"\ndocs len {len(docs)}")

    documents = text_processor.split_documents(docs)

    model = ModelPublic.create(get_default_model(ModelType.LLM))
    vector_store = _get_vector_store(vector_store_type)
    vector = VectorProvideFactory.create_vector("tinyrag_test", vector_store, model)

    vector.add_documents(documents)
    doc_ids = [doc.id for doc in documents]
    print(f"doc_ids={doc_ids}")


def run_search(vector_store_type: VectorStoreType):
    settings.VECTOR_STORE_TYPE = vector_store_type

    print(f"\nvector_store_type={vector_store_type}")
    model = ModelPublic.create(get_default_model(ModelType.LLM))
    vector_store = _get_vector_store(vector_store_type)
    vector = VectorProvideFactory.create_vector("tinyrag_test", vector_store, model)


    vec = vector.model_provider.embed_query("流沙")
    print(f"\nvec {len(vec)} {vec}\n")

    matched_dcos = vector.similarity_search("流沙", k=10)
    for d in matched_dcos:
        print(f"{d}")


def _get_vector_store(vector_store_type: VectorStoreType) -> VectorStorePublic:
    with open_session() as session:
        stmt = select(VectorStore).where(
            VectorStore.tenant_id == 1
        )
        vector_stores = session.exec(stmt).all()
        for vector_store in vector_stores:
            if vector_store.type == vector_store_type:
                return VectorStorePublic.create(vector_store)
    raise Exception(f"vector store {vector_store_type} not found")
