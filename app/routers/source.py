from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from app.db import get_db
from app.schemas.source import Source, SourceCreate, SourceUpdate
from app.services.source_service import SourceService

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=Source, status_code=status.HTTP_201_CREATED)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """Create a new source."""
    source_service = SourceService(db)

    # Check if identifier already exists
    if source.identifier and source_service.get_source_by_identifier(source.identifier):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source with this identifier already exists",
        )

    return source_service.create_source(source)


@router.get("", response_model=Page[Source])
def list_sources(db: Session = Depends(get_db)):
    """List all sources."""
    return paginate(db, SourceService(db).get_sources_query())


@router.get("/{source_id}", response_model=Source)
def get_source(source_id: UUID, db: Session = Depends(get_db)):
    """Get a source by ID."""
    source = SourceService(db).get_source(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source not found"
        )
    return source


@router.put("/{source_id}", response_model=Source)
def update_source(source_id: UUID, source: SourceUpdate, db: Session = Depends(get_db)):
    """Update a source."""
    source_service = SourceService(db)

    # Check if identifier is being updated and already exists
    if source.identifier:
        existing_source = source_service.get_source_by_identifier(source.identifier)
        if existing_source and existing_source.id != source_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source with this identifier already exists",
            )

    updated_source = source_service.update_source(source_id, source)
    if not updated_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source not found"
        )
    return updated_source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: UUID, db: Session = Depends(get_db)):
    """Delete a source (soft delete)."""
    if not SourceService(db).delete_source(source_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source not found"
        )
