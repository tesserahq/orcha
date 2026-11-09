"""Add indexes on events.created_at and events.event_type for filtering

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-11-09

Additive only: safe with the previous release, which never reads these columns
through an index. Built CONCURRENTLY so writes to the events table are not blocked.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create indexes used by the events list filters."""
    with op.get_context().autocommit_block():
        op.create_index(
            "ix_events_created_at",
            "events",
            ["created_at"],
            postgresql_concurrently=True,
            if_not_exists=True,
        )
        op.create_index(
            "ix_events_event_type",
            "events",
            ["event_type"],
            postgresql_concurrently=True,
            postgresql_ops={"event_type": "text_pattern_ops"},
            if_not_exists=True,
        )


def downgrade() -> None:
    """Drop the events list filter indexes."""
    with op.get_context().autocommit_block():
        op.drop_index(
            "ix_events_event_type",
            table_name="events",
            postgresql_concurrently=True,
            if_exists=True,
        )
        op.drop_index(
            "ix_events_created_at",
            table_name="events",
            postgresql_concurrently=True,
            if_exists=True,
        )
