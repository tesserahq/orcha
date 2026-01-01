from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from app.db import get_db
from app.schemas.event import Event as EventSchema, EventCreate, EventUpdate
from app.models.event import Event as EventModel
from app.services.event_service import EventService
from app.routers.utils.dependencies import get_event_by_id

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=Page[EventSchema])
def list_events(db: Session = Depends(get_db)):
    """List all events."""
    return paginate(db, EventService(db).get_events_query())


@router.get("/{event_id}", response_model=EventSchema)
def get_event(event: EventModel = Depends(get_event_by_id)):
    """Get an event by ID."""
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event: EventModel = Depends(get_event_by_id), db: Session = Depends(get_db)
):
    """Delete an event (soft delete)."""
    if not EventService(db).delete_event(event.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
