"""Task for backfilling event types cache from the database."""

from app.core.celery_app import celery_app
from app.core.logging_config import get_logger
from app.models.event import Event
from app.utils.db.db_session_helper import db_session
from app.utils.event_type_cache import set_event_types

logger = get_logger("backfill_event_types_task")


@celery_app.task(name="app.tasks.backfill_event_types_task.backfill_event_types_task")
def backfill_event_types_task() -> None:
    """
    Backfill the event types cache with distinct event types from the database.

    This task queries all distinct event_type values from the events table
    and stores them in the cache.
    """
    logger.info("Starting event types cache backfill")

    with db_session() as db:
        # Query distinct event_type values from the events table
        # Results will be tuples like (event_type,), so we unpack them
        distinct_results = db.query(Event.event_type).distinct().all()

        # Extract event type strings from the result tuples and filter out empty values
        event_types = [event_type for (event_type,) in distinct_results if event_type]

        # Set all event types in cache
        set_event_types(event_types)

        logger.info(f"Backfilled {len(event_types)} event types to cache")
