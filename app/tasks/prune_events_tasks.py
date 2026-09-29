import datetime

from app.core.celery_app import celery_app
from app.db import session_scope
from app.repositories.event_repository import EventRepository


@celery_app.task
def prune_events_task(
    days_to_keep: int = 30,
) -> None:
    """
    Background task to ingest raw text into a project's vector store.

    Args:
        days_to_keep: The number of days to keep events.
    """
    with session_scope() as db:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        EventRepository(db).delete_events_created_before(cutoff_date)
