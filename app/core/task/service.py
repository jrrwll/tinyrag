from app.common.db import open_session
from app.entities.task import AsyncTask


def update_task_progress(task_id: str, progress: int) -> None:
    with open_session() as session:
        entity = session.get(AsyncTask, task_id)
        if not entity:
            return

        entity.progress = progress
        session.add(entity)
        session.commit()
