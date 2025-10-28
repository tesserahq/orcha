from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class EventBase(BaseModel):
    """Base event model containing common event attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the event. Defaults to None."""

    data: dict
    """Event data as JSONB. Required field."""

    event_type: str
    """Type of the event. Required field."""

    spec_version: str = "1.0"
    """CloudEvents specification version. Defaults to '1.0'."""

    time: datetime
    """Timestamp when the event occurred. Required field."""

    source_id: UUID
    """ID of the source that generated this event. Required field."""


class EventCreate(EventBase):
    """Schema for creating a new event. Inherits all fields from EventBase."""

    pass


class EventUpdate(BaseModel):
    """Schema for updating an existing event. All fields are optional."""

    data: Optional[dict] = None
    """Updated event data."""

    event_type: Optional[str] = None
    """Updated event type."""

    spec_version: Optional[str] = None
    """Updated specification version."""

    time: Optional[datetime] = None
    """Updated event timestamp."""

    source_id: Optional[UUID] = None
    """Updated source ID."""


class EventInDB(EventBase):
    """Schema representing an event as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the event in the database."""

    created_at: datetime
    """Timestamp when the event record was created."""

    updated_at: datetime
    """Timestamp when the event record was last updated."""

    model_config = {"from_attributes": True}


class Event(EventInDB):
    """Schema for event data returned in API responses. Inherits all fields from EventInDB."""

    pass


class EventDetails(BaseModel):
    """Schema for detailed event information, typically used in event views."""

    id: UUID
    """Unique identifier for the event."""

    data: dict
    """Event data."""

    event_type: str
    """Type of the event."""

    spec_version: str
    """CloudEvents specification version."""

    time: datetime
    """Timestamp when the event occurred."""

    source_id: UUID
    """ID of the source that generated this event."""

    created_at: datetime
    """Timestamp when the event record was created."""

    updated_at: datetime
    """Timestamp when the event record was last updated."""

    model_config = {"from_attributes": True}
