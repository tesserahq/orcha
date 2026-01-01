from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from httpx import Request
from sqlalchemy.orm import Session
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page

from app.db import get_db
from app.schemas.source import Source as SourceSchema, SourceCreate, SourceUpdate
from app.services.source_service import SourceService
from app.models.source import Source as SourceModel
from app.routers.utils.dependencies import get_source_by_id
from app.auth.rbac import build_rbac_dependencies


async def infer_domain(request: Request) -> Optional[str]:
    return "*"


RESOURCE = "source"
rbac = build_rbac_dependencies(
    resource=RESOURCE,
    domain_resolver=infer_domain,
)

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=SourceSchema, status_code=status.HTTP_201_CREATED)
def create_source(
    source: SourceCreate,
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["create"]),
):
    """Create a new source."""
    source_service = SourceService(db)

    # Check if identifier already exists
    if source.identifier and source_service.get_source_by_identifier(source.identifier):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source with this identifier already exists",
        )

    return source_service.create_source(source)


@router.get("", response_model=Page[SourceSchema])
def list_sources(
    db: Session = Depends(get_db), _authorized: bool = Depends(rbac["read"])
):
    """List all sources."""
    return paginate(db, SourceService(db).get_sources_query())


@router.get("/{source_id}", response_model=SourceSchema)
def get_source(
    source: SourceModel = Depends(get_source_by_id),
    _authorized: bool = Depends(rbac["read"]),
):
    """Get a source by ID."""
    return source


@router.put("/{source_id}", response_model=SourceSchema)
def update_source(
    source: SourceModel = Depends(get_source_by_id),
    update: SourceUpdate = ...,
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["update"]),
):
    """Update a source."""
    source_service = SourceService(db)

    # Check if identifier is being updated and already exists
    if update.identifier:
        existing_source = source_service.get_source_by_identifier(update.identifier)
        if existing_source and existing_source.id != source.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source with this identifier already exists",
            )

    updated_source = source_service.update_source(source.id, update)
    if not updated_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source not found"
        )
    return updated_source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source: SourceModel = Depends(get_source_by_id),
    db: Session = Depends(get_db),
    _authorized: bool = Depends(rbac["delete"]),
):
    """Delete a source (soft delete)."""
    if not SourceService(db).delete_source(source.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source not found"
        )
