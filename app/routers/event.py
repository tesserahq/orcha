from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from httpx import Request
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from app.db import DbSession
from app.schemas.event import Event as EventSchema
from app.models.event import Event as EventModel
from app.repositories.event_repository import EventRepository
from app.auth.rbac import build_rbac_dependencies
from app.routers.utils.dependencies import get_event_by_id


async def infer_domain(request: Request) -> Optional[str]:
    return "*"


RESOURCE = "event"
rbac = build_rbac_dependencies(
    resource=RESOURCE,
    domain_resolver=infer_domain,
)

router = APIRouter(
    prefix="/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)


def _to_naive_utc(value: Optional[datetime]) -> Optional[datetime]:
    """created_at is stored as naive UTC; normalize incoming datetimes to match."""
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


@router.get("", response_model=Page[EventSchema])
def list_events(
    db: DbSession,
    event_type: Optional[str] = Query(
        None,
        description="Event type prefix, e.g. 'com.mylinden.', or a pattern with '*' wildcards",
    ),
    created_from: Optional[datetime] = Query(
        None, description="Only events created at or after this time (inclusive)"
    ),
    created_to: Optional[datetime] = Query(
        None, description="Only events created at or before this time (inclusive)"
    ),
    _authorized: bool = Depends(rbac["read"]),
):
    """List events, optionally filtered by type and created_at range."""
    created_from = _to_naive_utc(created_from)
    created_to = _to_naive_utc(created_to)
    if (
        created_from is not None
        and created_to is not None
        and created_from > created_to
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="created_from must be before or equal to created_to",
        )

    query = EventRepository(db).get_events_query(
        event_type=event_type,
        created_from=created_from,
        created_to=created_to,
    )
    return paginate(db, query)


@router.get("/{event_id}", response_model=EventSchema)
def get_event(
    event: EventModel = Depends(get_event_by_id),
    _authorized: bool = Depends(rbac["read"]),
):
    """Get an event by ID."""
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    db: DbSession,
    event: EventModel = Depends(get_event_by_id),
    _authorized: bool = Depends(rbac["delete"]),
):
    """Delete an event (soft delete)."""
    if not EventRepository(db).delete_event(event.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
