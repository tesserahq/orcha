from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from app.db import get_db
from app.schemas.event import Event, EventCreate, EventUpdate
from app.services.event_service import EventService
from app.services.source_service import SourceService

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Create a new event."""
    event_service = EventService(db)
    source_service = SourceService(db)

    # Validate that the source exists
    source = source_service.get_source(event.source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source not found",
        )

    return event_service.create_event(event)


@router.get("", response_model=Page[Event])
def list_events(db: Session = Depends(get_db)):
    """List all events."""
    return paginate(db, EventService(db).get_events_query())


@router.get("/source/{source_id}", response_model=Page[Event])
def list_events_by_source(source_id: UUID, db: Session = Depends(get_db)):
    """List all events for a specific source."""
    event_service = EventService(db)
    source_service = SourceService(db)

    # Validate that the source exists
    source = source_service.get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found",
        )

    from app.models.event import Event
    from sqlalchemy import select

    return paginate(
        db,
        select(Event).filter(Event.source_id == source_id).order_by(Event.time.desc()),
    )


@router.get("/type/{event_type}", response_model=Page[Event])
def list_events_by_type(event_type: str, db: Session = Depends(get_db)):
    """List all events of a specific type."""
    from app.models.event import Event
    from sqlalchemy import select

    return paginate(
        db,
        select(Event)
        .filter(Event.event_type == event_type)
        .order_by(Event.time.desc()),
    )


@router.get("/{event_id}", response_model=Event)
def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get an event by ID."""
    event = EventService(db).get_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return event


@router.put("/{event_id}", response_model=Event)
def update_event(event_id: UUID, event: EventUpdate, db: Session = Depends(get_db)):
    """Update an event."""
    event_service = EventService(db)

    # If updating source_id, validate it exists
    if event.source_id:
        source_service = SourceService(db)
        source = source_service.get_source(event.source_id)
        if not source:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source not found",
            )

    updated_event = event_service.update_event(event_id, event)
    if not updated_event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return updated_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: UUID, db: Session = Depends(get_db)):
    """Delete an event (soft delete)."""
    if not EventService(db).delete_event(event_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
