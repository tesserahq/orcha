# Import celery app first
from app.core.celery_app import celery_app
from app.tasks.prune_events_tasks import prune_events_task
from app.tasks.process_nats_event_task import process_nats_event_task
from app.tasks.backfill_event_types_task import backfill_event_types_task

# Initialize logging configuration for Celery workers
from app.core.logging_config import LoggingConfig

LoggingConfig()  # Initialize logging

__all__ = [
    "celery_app",
    "prune_events_task",
    "process_nats_event_task",
    "backfill_event_types_task",
]
