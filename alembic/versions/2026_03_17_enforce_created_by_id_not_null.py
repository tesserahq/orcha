"""Enforce created_by_id NOT NULL on workflows

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-17

"""

from typing import Sequence, Union

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_USER_ID = "4bfb4792-0aab-45fa-9d48-45de47687bd6"


def upgrade() -> None:
    """Backfill any remaining NULL created_by_id values and enforce NOT NULL."""
    op.execute(
        f"UPDATE workflows SET created_by_id = '{DEFAULT_USER_ID}' WHERE created_by_id IS NULL"
    )
    op.alter_column("workflows", "created_by_id", nullable=False)


def downgrade() -> None:
    """Revert created_by_id back to nullable."""
    op.alter_column("workflows", "created_by_id", nullable=True)
