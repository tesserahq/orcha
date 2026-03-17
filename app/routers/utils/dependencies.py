from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db import get_db
from app.models.workflow import Workflow
from app.models.event import Event
from app.models.source import Source
from app.models.user import User
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.event_repository import EventRepository
from app.repositories.source_repository import SourceRepository


def get_current_user(request: Request) -> User:
    if hasattr(request.state, "user") and request.state.user is not None:
        return request.state.user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )


def get_workflow_by_id(
    workflow_id: UUID,
    db: Session = Depends(get_db),
) -> Workflow:
    """FastAPI dependency to get a workflow by ID.

    Args:
        workflow_id: The UUID of the workflow to retrieve
        db: Database session dependency

    Returns:
        Workflow: The retrieved workflow

    Raises:
        HTTPException: If the workflow is not found
    """
    workflow = WorkflowRepository(db).get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


def get_event_by_id(
    event_id: UUID,
    db: Session = Depends(get_db),
) -> Event:
    """FastAPI dependency to get an event by ID.

    Args:
        event_id: The UUID of the event to retrieve
        db: Database session dependency

    Returns:
        Event: The retrieved event

    Raises:
        HTTPException: If the event is not found
    """
    event = EventRepository(db).get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


def get_source_by_id(
    source_id: UUID,
    db: Session = Depends(get_db),
) -> Source:
    """FastAPI dependency to get a source by ID.

    Args:
        source_id: The UUID of the source to retrieve
        db: Database session dependency

    Returns:
        Source: The retrieved source

    Raises:
        HTTPException: If the source is not found
    """
    source = SourceRepository(db).get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source
