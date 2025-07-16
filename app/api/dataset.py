from typing import Any

from fastapi import APIRouter, Query

from app.common.base import PageResult, wrap_api_result
from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.dataset.api import DatasetCreate, \
    DatasetImport, DatasetPublic, \
    PreviewChunk, PreviewChunkPublic, SimpleDatasetPublic
from app.core.dataset.preview_file_chunk import preview_file_chunk
from app.core.file.upload import get_file_path
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.dataset import page_and_count_datasets
from app.entities.dao.file import get_files
from app.entities.dataset import Dataset
from app.tasks.dataset_import_task import send_dataset_import_task

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


@router.post("/preview_chunk", response_model=PreviewChunkPublic)
def preview_chunk(params: PreviewChunk) -> Any:
    return preview_file_chunk(params)


@router.post("", response_model=DatasetPublic)
def create(session: SessionDep, params: DatasetCreate) -> Any:
    entity = Dataset(name=params.name, description=params.description)
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return DatasetPublic.new(entity)


@router.post("/import", response_model=AsyncTaskPublic)
def import_document(session: SessionDep, params: DatasetImport) -> Any:
    if not params.file and not params.website:
        raise BizException.new(
            ErrorCode.request_validation_error_detail,
            "neither file or website is unset"
        )

    dataset_id = params.id
    entity = session.get(Dataset, dataset_id)
    if not entity:
        raise BizException.new(ErrorCode.dataset_not_found, dataset_id)

    files = {}
    # check params
    if params.file:
        file_ids = params.file.file_ids
        files = get_files(session, file_ids)
        missing_file_ids = [file_id for file_id in file_ids
                            if file_id not in files]
        if missing_file_ids:
            raise BizException.new(
                ErrorCode.file_not_found, missing_file_ids
            )

    # import task
    dataset = DatasetPublic.new(entity)
    task = send_dataset_import_task(params, dataset, files)
    return wrap_api_result(task)
