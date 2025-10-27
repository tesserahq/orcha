from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class SourceBase(BaseModel):
    """Base source model containing common source attributes."""

    id: Optional[UUID] = None
    """Unique identifier for the source. Defaults to None."""

    name: str
    """Name of the source. Required field."""

    description: Optional[str] = None
    """Description of the source. Optional field."""

    identifier: str
    """Unique identifier for the source. Required field."""


class SourceCreate(SourceBase):
    """Schema for creating a new source. Inherits all fields from SourceBase."""

    pass


class SourceUpdate(BaseModel):
    """Schema for updating an existing source. All fields are optional."""

    name: Optional[str] = None
    """Updated source name."""

    description: Optional[str] = None
    """Updated source description."""

    identifier: Optional[str] = None
    """Updated source identifier."""


class SourceInDB(SourceBase):
    """Schema representing a source as stored in the database. Includes database-specific fields."""

    id: UUID
    """Unique identifier for the source in the database."""

    created_at: datetime
    """Timestamp when the source record was created."""

    updated_at: datetime
    """Timestamp when the source record was last updated."""

    model_config = {"from_attributes": True}


class Source(SourceInDB):
    """Schema for source data returned in API responses. Inherits all fields from SourceInDB."""

    pass


class SourceDetails(BaseModel):
    """Schema for detailed source information, typically used in source views."""

    id: UUID
    """Unique identifier for the source."""

    name: str
    """Name of the source."""

    description: Optional[str] = None
    """Description of the source."""

    identifier: str
    """Unique identifier for the source."""

    created_at: datetime
    """Timestamp when the source record was created."""

    updated_at: datetime
    """Timestamp when the source record was last updated."""

    model_config = {"from_attributes": True}
