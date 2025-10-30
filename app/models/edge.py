from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

from app.db import Base


class Edge(Base, TimestampMixin, SoftDeleteMixin):
    """Edge model for the application.
    This model represents an edge in the system.
    """

    __tablename__ = "edges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=True)
    source_node_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False
    )
    target_node_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False
    )
    workflow_version_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_versions.id"), nullable=False
    )
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ui_settings: Mapped[dict] = mapped_column(JSONB, nullable=False)

    target_node = relationship(
        "Node", foreign_keys=[target_node_id], back_populates="target_edges"
    )
    source_node = relationship(
        "Node", foreign_keys=[source_node_id], back_populates="source_edges"
    )
    workflow_version = relationship("WorkflowVersion", back_populates="edges")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
