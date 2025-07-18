import logging
from typing import Any

from fastapi import APIRouter

from app.common.scheduler import RQManager

router = APIRouter(tags=["private"], prefix="/private")

logger = logging.getLogger(__name__)


@router.get("/test_log")
def test_log() -> Any:
    logger.info(f"test log is: {logger}")


@router.get("/queue_stat")
def queue_stat() -> Any:
    rq_manager = RQManager()
    return {
        "pending_jobs": rq_manager.queue.count,
        "scheduled_jobs": len(rq_manager.scheduler),
    }

