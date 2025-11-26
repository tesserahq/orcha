from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db import Base


class Workflow(Base, TimestampMixin, SoftDeleteMixin):
    """Workflow model for the application.
    This model represents a workflow in the system.
    """

    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active_version_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_versions.id"), nullable=True
    )
    last_execution_time: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    execution_status: Mapped[str | None] = mapped_column(String, nullable=True)
    execution_status_message: Mapped[str | None] = mapped_column(String, nullable=True)

    active_version = relationship("WorkflowVersion", foreign_keys=[active_version_id])
    versions = relationship(
        "WorkflowVersion",
        back_populates="workflow",
        foreign_keys="WorkflowVersion.workflow_id",
    )
