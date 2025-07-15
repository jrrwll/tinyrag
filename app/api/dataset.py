from typing import Any

from fastapi import APIRouter, Query

from app.common.base import PageResult
from app.common.config import settings
from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.dataset.api import DatasetImportCreate, DatasetPublic, \
    PreviewChunk, PreviewChunkPublic, SimpleDatasetPublic
from app.core.dataset.preview_file_chunk import preview_file_chunk
from app.entities.dao.dataset import page_and_count_datasets
from app.entities.dataset import Dataset

router = APIRouter(prefix="/dataset", tags=["dataset"])


@router.get("/list", response_model=PageResult[SimpleDatasetPublic])
def list(
        session: SessionDep,
        page_no: int = Query(default=1, ge=1, le=settings.DEFAULT_MAX_PAGE_NO),
        page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE,
                               ge=1, le=settings.DEFAULT_MAX_PAGE_SIZE),
        enable: bool | None = None,
) -> Any:
    entities, count = page_and_count_datasets(session, page_no, page_size, enable)
    return PageResult[SimpleDatasetPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleDatasetPublic(**entity) for entity in entities],
    )


@router.get("", response_model=DatasetPublic)
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Dataset, id)
    if not entity:
        raise BizException.new(ErrorCode.dataset_not_found, id)

    return DatasetPublic(**entity.model_dump())


@router.post("/import", response_model=DatasetPublic)
def create_import(session: SessionDep, params: DatasetImportCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return DatasetPublic(**entity.model_dump())


@router.post("/init", response_model=DatasetPublic)
def create_import(session: SessionDep, id: int) -> Any:


    return DatasetPublic(**entity.model_dump())


@router.post("/preview_chunk", response_model=PreviewChunkPublic)
def preview_chunk(params: PreviewChunk) -> Any:
    return preview_file_chunk(params)
