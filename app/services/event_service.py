from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate
from app.services.soft_delete_service import SoftDeleteService
from app.utils.db.filtering import apply_filters


class EventService(SoftDeleteService[Event]):
    """Service class for managing event CRUD operations."""

    def __init__(self, db: Session):
        """
        Initialize the event service.

        Args:
            db: Database session
        """
        super().__init__(db, Event)

    def get_event(self, event_id: UUID) -> Optional[Event]:
        """
        Get a single event by ID.

        Args:
            event_id: The ID of the event to retrieve

        Returns:
            Optional[Event]: The event or None if not found
        """
        return self.db.query(Event).filter(Event.id == event_id).first()

    def get_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """
        Get a list of events with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Event]: List of events
        """
        return (
            self.db.query(Event)
            .order_by(Event.time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_events_query(self):
        """
        Get a query for all events.
        This is useful for pagination with fastapi-pagination.

        Returns:
            Select: SQLAlchemy select statement for events
        """
        return select(Event).order_by(Event.time.desc())

    def get_events_by_source(
        self, source_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Event]:
        """
        Get all events for a specific source.

        Args:
            source_id: The ID of the source
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Event]: List of events for the source
        """
        return (
            self.db.query(Event)
            .filter(Event.source_id == source_id)
            .order_by(Event.time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_events_by_type(
        self, event_type: str, skip: int = 0, limit: int = 100
    ) -> List[Event]:
        """
        Get all events of a specific type.

        Args:
            event_type: The type of events to retrieve
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List[Event]: List of events of the specified type
        """
        return (
            self.db.query(Event)
            .filter(Event.event_type == event_type)
            .order_by(Event.time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_event(self, event: EventCreate) -> Event:
        """
        Create a new event.

        Args:
            event: The event data to create

        Returns:
            Event: The created event
        """
        db_event = Event(**event.model_dump())
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event

    def update_event(self, event_id: UUID, event: EventUpdate) -> Optional[Event]:
        """
        Update an existing event.

        Args:
            event_id: The ID of the event to update
            event: The updated event data

        Returns:
            Optional[Event]: The updated event or None if not found
        """
        db_event = self.db.query(Event).filter(Event.id == event_id).first()
        if db_event:
            update_data = event.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_event, key, value)
            self.db.commit()
            self.db.refresh(db_event)
        return db_event

    def delete_event(self, event_id: UUID) -> bool:
        """
        Soft delete an event.

        Args:
            event_id: The ID of the event to delete

        Returns:
            bool: True if the event was deleted, False otherwise
        """
        return self.delete_record(event_id)

    def search(self, filters: dict) -> List[Event]:
        """
        Search events based on dynamic filter criteria.

        Args:
            filters: A dictionary where keys are field names and values are either:
                - A direct value (e.g. {"event_type": "user.created"})
                - A dictionary with 'operator' and 'value' keys (e.g. {"event_type": {"operator": "ilike", "value": "%user%"}})

        Returns:
            List[Event]: Filtered list of events matching the criteria.
        """
        query = self.db.query(Event)
        query = apply_filters(query, Event, filters)
        return query.all()

    def restore_event(self, event_id: UUID) -> bool:
        """Restore a soft-deleted event by setting deleted_at to None."""
        return self.restore_record(event_id)

    def hard_delete_event(self, event_id: UUID) -> bool:
        """Permanently delete an event from the database."""
        return self.hard_delete_record(event_id)

    def get_deleted_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """Get all soft-deleted events."""
        return self.get_deleted_records(skip, limit)

    def get_deleted_event(self, event_id: UUID) -> Optional[Event]:
        """Get a single soft-deleted event by ID."""
        return self.get_deleted_record(event_id)

    def get_events_deleted_after(self, date) -> List[Event]:
        """Get events deleted after a specific date."""
        return self.get_records_deleted_after(date)
