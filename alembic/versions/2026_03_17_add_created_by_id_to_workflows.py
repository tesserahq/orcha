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


def upgrade() -> None:
    """Add created_by_id column to workflows table."""
    op.add_column(
        "workflows",
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_workflows_created_by_id",
        "workflows",
        ["created_by_id"],
    )


def downgrade() -> None:
    """Remove created_by_id column from workflows table."""
    op.drop_index("ix_workflows_created_by_id", "workflows")
    op.drop_column("workflows", "created_by_id")
