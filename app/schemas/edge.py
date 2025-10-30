from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class EdgeBase(BaseModel):
    """Base edge model containing common edge attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the edge. Defaults to None."""

    name: Optional[str] = None
    """Name of the edge. Optional field."""

    source_node_id: UUID
    """ID of the source node. Required field."""

    target_node_id: UUID
    """ID of the target node. Required field."""

    workflow_version_id: UUID
    """ID of the workflow version this edge belongs to. Required field."""

    settings: dict
    """Settings for the edge. Required field."""

    ui_settings: dict
    """UI settings for the edge. Required field."""


class EdgeCreate(EdgeBase):
    """Schema for creating a new edge. Inherits all fields from EdgeBase."""

    pass


class EdgeUpdate(BaseModel):
    """Schema for updating an existing edge. All fields are optional."""

    name: Optional[str] = None
    """Updated edge name."""

    source_node_id: Optional[UUID] = None
    """Updated source node ID."""

    target_node_id: Optional[UUID] = None
    """Updated target node ID."""

    settings: Optional[dict] = None
    """Updated edge settings."""

    ui_settings: Optional[dict] = None
    """Updated edge UI settings."""

    workflow_version_id: Optional[UUID] = None
    """Updated workflow version ID."""


class EdgeInDB(EdgeBase):
    """Schema representing an edge as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the edge in the database."""

    created_at: datetime
    """Timestamp when the edge record was created."""

    updated_at: datetime
    """Timestamp when the edge record was last updated."""

    model_config = {"from_attributes": True}


class Edge(EdgeInDB):
    """Schema for edge data returned in API responses. Inherits all fields from EdgeInDB."""

    pass


class EdgeDetails(BaseModel):
    """Schema for detailed edge information, typically used in edge views."""

    id: UUID
    """Unique identifier for the edge."""

    name: Optional[str] = None
    """Name of the edge."""

    source_node_id: UUID
    """ID of the source node."""

    target_node_id: UUID
    """ID of the target node."""

    workflow_version_id: UUID
    """ID of the workflow version this edge belongs to."""

    settings: dict
    """Settings for the edge."""

    ui_settings: dict
    """UI settings for the edge."""

    created_at: datetime
    """Timestamp when the edge record was created."""

    updated_at: datetime
    """Timestamp when the edge record was last updated."""

    model_config = {"from_attributes": True}
