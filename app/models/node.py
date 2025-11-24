from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

from app.db import Base


class Node(Base, TimestampMixin, SoftDeleteMixin):
    """Node model for the application.
    This model represents a node in the system.
    """

    __tablename__ = "nodes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    properties: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    ui_settings: Mapped[dict] = mapped_column(JSONB, nullable=False)
    workflow_version_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("workflow_versions.id"), nullable=False
    )
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    workflow_version = relationship("WorkflowVersion", back_populates="nodes")
    source_edges = relationship(
        "Edge", foreign_keys="Edge.source_node_id", back_populates="source_node"
    )
    target_edges = relationship(
        "Edge", foreign_keys="Edge.target_node_id", back_populates="target_node"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
