import json
import logging
from typing import Iterable, Optional
from uuid import uuid4

from pydantic import BaseModel

from app.core.knowledge.api import KnowledgePublic
from app.core.knowledge.base import ProcessRule
from app.core.knowledge.text.base import DocumentModel
from app.core.knowledge.text.keywords import extract_keywords
from app.core.knowledge.text.process import TextProcessor
from app.core.knowledge.text.tokens import get_word_count
from app.core.model.api import ModelPublic
from app.core.vector_store.api import VectorStorePublic
from app.core.vector_store.provider.base import VectorProvider, \
    VectorProviderFactory
from app.entities.dao.knowledge import save_knowledge_document, \
    save_knowledge_document_chucks
from app.entities.dao.task import update_task_progress
from app.entities.knowledge import Knowledge, KnowledgeDocument, \
    KnowledgeDocumentChunk
from app.util.collection import partition_iterable

logger = logging.getLogger(__name__)
from app.core.file.enums import FileType
from app.core.knowledge.enums import DocumentSourceType


class _FileTaskParams(BaseModel):
    file_path: str
    file_type: FileType
    source_info: str
    source_type: DocumentSourceType


def import_from_files(
        file_params: Iterable[Optional[_FileTaskParams]], file_count: int,
        knowledge: KnowledgePublic, process_rule: ProcessRule,
        model: ModelPublic, vector_store: VectorStorePublic,
        task_id: str, tenant_id: int, workspace_id: int):
    text_processor = TextProcessor.get_processor(process_rule)
    process_rule_str = process_rule.model_dump_json()

    collection_name = Knowledge.get_collection_name(knowledge.id)

    vector = VectorProviderFactory.create_vector(
        collection_name, vector_store, model)

    task_raito, task_raito_step = 0.0, 1 / file_count
    for params in file_params:
        if not params:
            continue

        docs = TextProcessor.load_documents(params.file_path, params.file_type)

        position = 0
        for doc in docs:
            doc_entity = KnowledgeDocument(
                id=doc.id, tenant_id=tenant_id, workspace_id=workspace_id,
                knowledge_id=knowledge.id, position=position,
                process_rule=process_rule_str,
                source_type=params.source_type, source_info=params.source_info)
            doc_entity = save_knowledge_document(doc_entity)

            documents = text_processor.split_documents([doc])

            partition_documents = partition_iterable(documents, 100)
            offset = 0
            for documents in partition_documents:
                import_document_chucks(documents, doc_entity, offset, vector)
                offset += len(documents)

            # update stat fields
            doc_entity.indexing = True
            save_knowledge_document(doc_entity)
            position += 1

        task_raito += task_raito_step
        progress = int(task_raito * 100)
        if not update_task_progress(task_id, progress):
            logger.warning(f"async_task={task_id}, "
                           f"update task progress={progress} failed")


def import_document_chucks(
        documents: list[DocumentModel], doc_entity: KnowledgeDocument,
        offset: int, vector: VectorProvider):
    for i in range(len(documents)):
        if not documents[i].id:
            documents[i].id = uuid4()

    vector.add_documents(documents)

    chucks = [to_document_chuck(i + offset, d, doc_entity)
              for i, d in enumerate(documents)]
    save_knowledge_document_chucks(chucks)


def to_document_chuck(index: int, doc: DocumentModel,
        doc_entity: KnowledgeDocument) -> KnowledgeDocumentChunk:
    word_count = get_word_count(doc.content)
    keywords = extract_keywords(doc.content)

    doc_entity.word_count += word_count
    return KnowledgeDocumentChunk(
        id=doc.id,
        tenant_id=doc_entity.tenant_id,
        workspace_id=doc_entity.workspace_id,
        knowledge_id=doc_entity.knowledge_id,
        document_id=doc_entity.id,
        position=index,
        content=doc.content,
        word_count=word_count,
        keywords=json.dumps(keywords),
    )
