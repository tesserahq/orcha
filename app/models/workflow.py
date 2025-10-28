from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
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
    trigger_event_type: Mapped[str] = mapped_column(String, nullable=False)
    trigger_event_filters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    versions = relationship("WorkflowVersion", back_populates="workflow")
