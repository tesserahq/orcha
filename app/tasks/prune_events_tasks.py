import datetime
from app.models.event import Event
from typing import Dict, Optional
from uuid import UUID

from app.core.celery_app import celery_app
from app.db import SessionLocal
from app.utils.db.db_session_helper import db_session


@celery_app.task
def prune_events_task(
    days_to_keep: int = 30,
) -> None:
    """
    Background task to ingest raw text into a project's vector store.

    Args:
        days_to_keep: The number of days to keep events.
    """
    with db_session() as db:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        db.query(Event).filter(Event.created_at < cutoff_date).delete()
        db.commit()
