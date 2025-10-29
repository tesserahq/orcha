from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db import Base


class WorkflowVersion(Base, TimestampMixin, SoftDeleteMixin):
    """Workflow version model for the application.
    This model represents a version of a workflow in the system.
    """

    __tablename__ = "workflow_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflows.id"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    workflow = relationship("Workflow", back_populates="versions")
    nodes = relationship("Node", back_populates="workflow_version")
    edges = relationship("Edge", back_populates="workflow_version")
