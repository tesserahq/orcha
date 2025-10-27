import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.mixins import TimestampMixin, SoftDeleteMixin
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSONB
import uuid

from app.db import Base


class Event(Base, TimestampMixin, SoftDeleteMixin):
    """Event model for the application.
    This model represents an event in the system.
    """

    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    spec_version: Mapped[str] = mapped_column(String, nullable=False, default="1.0")
    time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    source_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False
    )

    source = relationship("Source", back_populates="events")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
