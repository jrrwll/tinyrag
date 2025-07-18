import logging
from typing import Any

from fastapi import APIRouter

router = APIRouter(tags=["private"], prefix="/private")

logger = logging.getLogger(__name__)


@router.get("/test_log")
def test_log() -> Any:
    logger.info(f"test log is: {logger}")

