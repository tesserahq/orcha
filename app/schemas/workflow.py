from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.node import NodeCreate
from app.schemas.edge import EdgeCreate
from app.schemas.node import NodeCreatePayload
from app.schemas.node import Node


class WorkflowBase(BaseModel):
    """Base workflow model containing common workflow attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the workflow. Defaults to None."""

    name: str
    """Name of the workflow. Required field."""

    description: Optional[str] = None
    """Description of the workflow. Optional field."""

    is_active: bool = True
    """Whether the workflow is active. Defaults to True."""

    active_version_id: Optional[UUID] = None
    """ID of the active version of the workflow. Optional field."""


class WorkflowCreate(WorkflowBase):
    """Schema for creating a new workflow. Inherits all fields from WorkflowBase."""

    pass


class WorkflowUpdate(BaseModel):
    """Schema for updating an existing workflow. All fields are optional."""

    name: Optional[str] = None
    """Updated workflow name."""

    description: Optional[str] = None
    """Updated workflow description."""

    is_active: Optional[bool] = None
    """Updated active status."""

    active_version_id: Optional[UUID] = None
    """Updated active version ID."""


class WorkflowUpdateRequest(BaseModel):
    """Schema for updating an existing workflow. All fields are optional."""

    name: Optional[str] = None
    """Updated workflow name."""

    description: Optional[str] = None
    """Updated workflow description."""

    is_active: Optional[bool] = None
    """Updated active status."""

    nodes: Optional[List[NodeCreatePayload]] = None
    """Ordered nodes to associate with the new workflow version. Optional."""


class WorkflowInDB(WorkflowBase):
    """Schema representing a workflow as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the workflow in the database."""

    created_at: datetime
    """Timestamp when the workflow record was created."""

    updated_at: datetime
    """Timestamp when the workflow record was last updated."""

    model_config = {"from_attributes": True}


class Workflow(WorkflowInDB):
    """Schema for workflow data returned in API responses. Inherits all fields from WorkflowInDB."""

    pass


class WorkflowWithNodes(Workflow):
    """Workflow response including ordered nodes for the active version."""

    nodes: List[Node]


class WorkflowDetails(BaseModel):
    """Schema for detailed workflow information, typically used in workflow views."""

    id: UUID
    """Unique identifier for the workflow."""

    name: str
    """Name of the workflow."""

    description: Optional[str] = None
    """Description of the workflow."""

    is_active: bool
    """Whether the workflow is active."""

    created_at: datetime
    """Timestamp when the workflow record was created."""

    updated_at: datetime
    """Timestamp when the workflow record was last updated."""

    model_config = {"from_attributes": True}
