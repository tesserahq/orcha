from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class NodeBase(BaseModel):
    """Base node model containing common node attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the node. Defaults to None."""

    name: str
    """Name of the node. Required field."""

    description: Optional[str] = None
    """Description of the node. Optional field."""

    kind: str
    """Type/kind of the node. Required field."""

    settings: dict
    """Settings for the node. Required field."""

    ui_settings: dict
    """UI settings for the node. Required field."""

    workflow_version_id: UUID
    """ID of the workflow version this node belongs to. Required field."""


class NodeCreate(NodeBase):
    """Schema for creating a new node. Inherits all fields from NodeBase."""

    pass


class NodeUpdate(BaseModel):
    """Schema for updating an existing node. All fields are optional."""

    name: Optional[str] = None
    """Updated node name."""

    description: Optional[str] = None
    """Updated node description."""

    kind: Optional[str] = None
    """Updated node kind."""

    settings: Optional[dict] = None
    """Updated node settings."""

    ui_settings: Optional[dict] = None
    """Updated node UI settings."""

    workflow_version_id: Optional[UUID] = None
    """Updated workflow version ID."""


class NodeInDB(NodeBase):
    """Schema representing a node as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the node in the database."""

    created_at: datetime
    """Timestamp when the node record was created."""

    updated_at: datetime
    """Timestamp when the node record was last updated."""

    model_config = {"from_attributes": True}


class Node(NodeInDB):
    """Schema for node data returned in API responses. Inherits all fields from NodeInDB."""

    pass


class NodeDetails(BaseModel):
    """Schema for detailed node information, typically used in node views."""

    id: UUID
    """Unique identifier for the node."""

    name: str
    """Name of the node."""

    description: Optional[str] = None
    """Description of the node."""

    kind: str
    """Type/kind of the node."""

    settings: dict
    """Settings for the node."""

    ui_settings: dict
    """UI settings for the node."""

    workflow_version_id: UUID
    """ID of the workflow version this node belongs to."""

    created_at: datetime
    """Timestamp when the node record was created."""

    updated_at: datetime
    """Timestamp when the node record was last updated."""

    model_config = {"from_attributes": True}
