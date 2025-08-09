from sqlmodel import select

from app.common.deps import open_session
from app.config import settings
from app.core.file.enums import FileType
from app.core.knowledge.text_process.base import get_text_processor
from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from app.core.vector_store.api import VectorStorePublic
from app.core.vector_store.enums import VectorStoreType
from app.core.vector_store.provider.base import VectorProviderFactory
from app.entities.repo.model import get_setup_model
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
    print(f"\nvector_store_type={vector_store_type}")
    local_path = _find_first_file()
    print(f"\nlocal_path={local_path}")
    if not local_path:
        return

    text_processor = get_text_processor(settings.default_process_rule)

    docs = list(text_processor.load_documents(local_path, FileType.TXT))
    print(f"\ndocs len {len(docs)}")

    documents = list(text_processor.split_documents(docs))

    vector_store, model = _get_vector_store_and_model(vector_store_type)
    vector = VectorProviderFactory.create_vector(
        "tinyrag_test", vector_store, model)

    vector.add_documents(documents)
    doc_ids = [doc.id for doc in documents]
    print(f"doc_ids={doc_ids}")


def run_search(vector_store_type: VectorStoreType):
    print(f"\nvector_store_type={vector_store_type}")
    vector_store, model = _get_vector_store_and_model(vector_store_type)
    vector = VectorProviderFactory.create_vector(
        "tinyrag_test", vector_store, model)

    vec = vector.model_provider.embed_query("流沙")
    print(f"\nvec {len(vec)} {vec}\n")

    matched_dcos = vector.similarity_search("流沙", k=10)
    for d in matched_dcos:
        print(f"{d}")

def _get_vector_store_and_model(
        vector_store_type: VectorStoreType
) -> tuple[VectorStorePublic, ModelPublic]:
    workspace_id, tenant_id = 1, 1
    with open_session() as session:
        model = get_setup_model(
            session, ModelType.TextEmbedding,
            workspace_id, tenant_id)
        if not model:
            raise RuntimeError("No embedding model")

        stmt = select(VectorStore).where(VectorStore.type == vector_store_type).limit(1)
        vector_store_entity = session.exec(stmt).first()
        if not vector_store_entity:
            raise ValueError(f"Vector store {vector_store_type} not found in db")
        vector_store = VectorStorePublic.create(vector_store_entity)

        print(f"\nvector_store={vector_store.model_dump_json(exclude_defaults=True)}")
        print(f"\nmodel={model.model_dump_json(exclude_defaults=True)}")
        return vector_store, model
