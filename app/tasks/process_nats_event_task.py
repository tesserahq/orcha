"""Task for processing NATS events asynchronously."""

from datetime import datetime, timezone
from typing import Dict, Optional

from app.core.celery_app import celery_app
from app.core.logging_config import get_logger
from app.db import SessionLocal
from app.schemas.event import EventCreate
from app.services.event_service import EventService
from app.utils.event_type_cache import add_event_type

logger = get_logger("nats_event_task")


@celery_app.task(name="app.tasks.process_nats_event_task.process_nats_event_task")
def process_nats_event_task(msg: Dict) -> Optional[str]:
    """
    Process a NATS event message and store it in the database.

    This task runs asynchronously via Celery, allowing the NATS handler
    to quickly acknowledge messages and continue processing.

    Args:
        msg: Dictionary containing the event message from NATS

    Returns:
        Optional[str]: The created event ID as a string, or None on error
    """
    logger.info(f"Processing NATS event: {msg}")

    db = SessionLocal()
    try:
        # Parse time if it's a string
        time_value = msg.get("time")
        if isinstance(time_value, str):
            time_value = datetime.fromisoformat(time_value.replace("Z", "+00:00"))
        elif time_value is None:
            time_value = datetime.now(timezone.utc)

        # Extract specific fields from the event for model columns
        event_data = msg.get("event_data")
        if event_data is None:
            event_data = {}
        elif not isinstance(event_data, dict):
            # If event_data is not a dict, wrap it
            event_data = {"data": event_data}

        event_create = EventCreate(
            source=msg.get("source", ""),
            spec_version=msg.get("spec_version", "1.0"),
            event_type=msg.get("event_type", ""),
            event_data=event_data,  # Store entire event here
            data_content_type=msg.get("data_content_type", "application/json"),
            subject=msg.get("subject", ""),
            time=time_value,
            tags=msg.get("tags"),
            labels=msg.get("labels"),
            privy=msg.get("privy", False),  # Default to False if not provided
            user_id=msg.get("user_id"),
        )

        # Create event using EventService
        event_service = EventService(db)
        created_event = event_service.create_event(event_create)

        # Add event type to cache (maintains unique list)
        event_type = msg.get("event_type")
        if event_type:
            add_event_type(event_type)

        logger.info(f"Event created successfully: {created_event.id}")
        return str(created_event.id)
    except Exception as e:
        logger.error(f"Error creating event: {e}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
