"""Add created_by_id to workflows

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-03-17

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_USER_ID = "4bfb4792-0aab-45fa-9d48-45de47687bd6"


def upgrade() -> None:
    """Add created_by_id column to workflows table."""
    # Add as nullable first so we can backfill existing rows
    op.add_column(
        "workflows",
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )

    # Backfill existing workflows with the default user
    op.execute(
        f"UPDATE workflows SET created_by_id = '{DEFAULT_USER_ID}' WHERE created_by_id IS NULL"
    )

    # Now enforce NOT NULL
    op.alter_column("workflows", "created_by_id", nullable=False)

    op.create_index(
        "ix_workflows_created_by_id",
        "workflows",
        ["created_by_id"],
    )


def downgrade() -> None:
    """Remove created_by_id column from workflows table."""
    op.drop_index("ix_workflows_created_by_id", "workflows")
    op.drop_column("workflows", "created_by_id")
