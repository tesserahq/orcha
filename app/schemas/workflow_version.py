from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class WorkflowVersionBase(BaseModel):
    """Base workflow version model containing common workflow version attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the workflow version. Defaults to None."""

    workflow_id: UUID
    """ID of the workflow this version belongs to. Required field."""

    version: int
    """Version number of the workflow. Required field."""

    is_active: bool = True
    """Whether this version is active. Defaults to True."""


class WorkflowVersionCreate(BaseModel):
    """Schema for creating a new workflow version. Version is auto-generated if not provided."""

    id: Optional[UUID] = None
    """Unique identifier for the workflow version. Defaults to None."""

    workflow_id: UUID
    """ID of the workflow this version belongs to. Required field."""

    version: Optional[int] = None
    """Version number of the workflow. Auto-incremented if not provided."""

    is_active: bool = True
    """Whether this version is active. Defaults to True."""


class WorkflowVersionUpdate(BaseModel):
    """Schema for updating an existing workflow version. All fields are optional."""

    workflow_id: Optional[UUID] = None
    """Updated workflow ID."""

    version: Optional[int] = None
    """Updated version number."""

    is_active: Optional[bool] = None
    """Updated active status."""


class WorkflowVersionInDB(WorkflowVersionBase):
    """Schema representing a workflow version as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the workflow version in the database."""

    created_at: datetime
    """Timestamp when the workflow version record was created."""

    updated_at: datetime
    """Timestamp when the workflow version record was last updated."""

    model_config = {"from_attributes": True}


class WorkflowVersion(WorkflowVersionInDB):
    """Schema for workflow version data returned in API responses. Inherits all fields from WorkflowVersionInDB."""

    pass


class WorkflowVersionDetails(BaseModel):
    """Schema for detailed workflow version information, typically used in workflow version views."""

    id: UUID
    """Unique identifier for the workflow version."""

    workflow_id: UUID
    """ID of the workflow this version belongs to."""

    version: int
    """Version number of the workflow."""

    is_active: bool
    """Whether this version is active."""

    created_at: datetime
    """Timestamp when the workflow version record was created."""

    updated_at: datetime
    """Timestamp when the workflow version record was last updated."""

    model_config = {"from_attributes": True}
