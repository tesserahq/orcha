from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Column, DateTime, String
from sqlalchemy import Boolean, ARRAY
import uuid

from app.db import Base


class Event(Base, TimestampMixin, SoftDeleteMixin):
    """Event model for the application.
    This model represents an event in the system.
    """

    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    spec_version: Mapped[str] = mapped_column(String, nullable=False, default="1.0")
    data_content_type = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    time = Column(DateTime, nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    source = Column(String, nullable=False)
    labels = Column(JSONB, default=dict, nullable=False)  # Dictionary of labels
    privy = Column(Boolean, nullable=False, default=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)

    # source_id: Mapped[UUID] = mapped_column(
    #     UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False
    # )

    # source = relationship("Source", back_populates="events")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
