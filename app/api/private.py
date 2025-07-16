import logging
from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["private"], prefix="/private")

logger = logging.getLogger(__name__)


@router.get("/logging")
def logging() -> Any:
    logger.info(f"test log is: router={router}")
